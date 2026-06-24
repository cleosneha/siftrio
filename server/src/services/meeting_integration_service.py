import json
import logging
import re
import uuid
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions.base import BaseAPIException
from src.repositories.auth_repository import AuthRepository
from src.tools.google_oauth import create_oauth_client, refresh_google_token

logger = logging.getLogger(__name__)


def _validate_rfc3339(ts: str) -> dict:
    """Validate RFC3339 compliance and return diagnostics."""
    issues = []
    if not ts.endswith("Z") and "+" not in ts[10:]:
        issues.append("Missing timezone offset (no Z or +HH:MM suffix)")
    if not ts.endswith("Z") and "+" in ts[10:]:
        has_tz = True
    else:
        has_tz = bool(ts.endswith("Z")) or ("+" in ts[10:])
    if not has_tz:
        issues.append("Not RFC3339 compliant - missing timezone designator")
    try:
        datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError as e:
        issues.append(f"Unparseable datetime: {e}")
    return {
        "raw": ts,
        "valid": len(issues) == 0,
        "issues": issues,
    }


class MeetingIntegrationService:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = AuthRepository(db)

    async def create_google_meet(
        self,
        user_id: UUID,
        title: str,
        description: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
        guest_emails: list[str] | None = None,
        user_email: str | None = None,
    ) -> dict:
        integration = await self.repo.get_integration(user_id, "google")
        if not integration or not integration.access_token:
            raise BaseAPIException(
                message="Google integration not found. Please log in with Google.",
                status_code=400,
            )

        access_token = integration.access_token

        logger.info("=== TOKEN DIAGNOSTICS ===")
        logger.info("Access token (first 20 chars): %s...", access_token[:20])
        logger.info("Granted scopes: %s", integration.scopes)
        logger.info("Token expires at: %s", integration.token_expires_at)
        logger.info("Has refresh token: %s", bool(integration.refresh_token))
        logger.info("Token expiry UTC: %s, now UTC: %s", integration.token_expires_at, datetime.now(timezone.utc))
        if integration.token_expires_at:
            logger.info("Token expired: %s", integration.token_expires_at < datetime.now(timezone.utc))

        now = datetime.now(timezone.utc)
        if integration.token_expires_at and integration.token_expires_at < now:
            if not integration.refresh_token:
                raise BaseAPIException(
                    message="Google session expired. Please log in again.",
                    status_code=400,
                )
            token_data = await refresh_google_token(integration.refresh_token)
            if not token_data:
                raise BaseAPIException(
                    message="Failed to refresh Google token. Please log in again.",
                    status_code=400,
                )
            access_token = token_data["access_token"]
            await self.repo.upsert_integration(
                user_id=user_id,
                provider="google",
                access_token=token_data["access_token"],
                refresh_token=token_data.get("refresh_token") or integration.refresh_token,
                token_expires_at=(
                    datetime.fromtimestamp(token_data["expires_at"], tz=timezone.utc)
                    if token_data.get("expires_at")
                    else None
                ),
                scopes=token_data.get("scope") or integration.scopes,
            )

        result = await self._create_calendar_event(
            access_token=access_token,
            title=title,
            description=description,
            start_time=start_time,
            end_time=end_time,
            guest_emails=guest_emails,
            user_email=user_email,
        )

        return result

    async def _create_calendar_event(
        self,
        access_token: str,
        title: str,
        description: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
        guest_emails: list[str] | None = None,
        user_email: str | None = None,
    ) -> dict:
        logger.info("=== RFC3339 VALIDATION ===")
        if start_time:
            st_diag = _validate_rfc3339(start_time)
            logger.info("start_time diagnostics: %s", json.dumps(st_diag, indent=2))
        if end_time:
            et_diag = _validate_rfc3339(end_time)
            logger.info("end_time diagnostics: %s", json.dumps(et_diag, indent=2))

        client = create_oauth_client()
        client.token = {"access_token": access_token, "token_type": "Bearer"}

        if start_time:
            event_start_dt = start_time
            logger.info("Using start_time: %s", event_start_dt)
        else:
            event_start_dt = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            logger.info("No start_time provided, defaulting to now UTC: %s", event_start_dt)

        if end_time:
            event_end_dt = end_time
            logger.info("Using end_time: %s", event_end_dt)
        else:
            event_end_dt = (datetime.now(timezone.utc) + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
            logger.info("No end_time provided, defaulting to: %s", event_end_dt)

        event_start = {"dateTime": event_start_dt}
        event_end = {"dateTime": event_end_dt}

        attendees = []
        if user_email:
            attendees.append({"email": user_email})
        if guest_emails:
            for email in guest_emails:
                email = email.strip()
                if email:
                    attendees.append({"email": email})

        body = {
            "summary": title,
            "description": description or "",
            "start": event_start,
            "end": event_end,
            "attendees": attendees,
            "conferenceData": {
                "createRequest": {
                    "requestId": str(uuid.uuid4()),
                }
            },
        }

        url = "https://www.googleapis.com/calendar/v3/calendars/primary/events?conferenceDataVersion=1"

        logger.info("=== ACTUAL REQUEST ===")
        logger.info("URL: %s", url)
        logger.info("Headers (sensitive redacted): Authorization: Bearer %s...", access_token[:20])
        logger.info("Payload: %s", json.dumps(body, indent=2, default=str))

        try:
            resp = await client.post(url, json=body)
        except Exception as e:
            raise BaseAPIException(
                message=f"Failed to connect to Google Calendar API: {e}",
                status_code=500,
            )

        logger.info("=== ACTUAL RESPONSE ===")
        logger.info("Status code: %s", resp.status_code)
        logger.info("Response headers: %s", dict(resp.headers))
        logger.info("Response body: %s", resp.text)

        if resp.status_code != 200:
            raise BaseAPIException(
                message=f"Google Calendar API error ({resp.status_code}): {resp.text}",
                status_code=500,
            )

        event_data = resp.json()
        event_id = event_data.get("id", "")
        meet_url = event_data.get("hangoutLink") or (
            event_data.get("conferenceData", {}).get("entryPoints", [{}])[0].get("uri")
        )

        if not meet_url:
            raise BaseAPIException(
                message="Google Meet link could not be generated from the event response",
                status_code=500,
            )

        meet_code = None
        match = re.search(r"meet\.google\.com/([a-z0-9-]+)", meet_url)
        if match:
            meet_code = match.group(1)

        return {
            "meet_url": meet_url,
            "event_id": event_id,
            "meet_code": meet_code,
        }
