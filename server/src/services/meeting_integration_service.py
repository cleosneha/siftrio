import logging
import re
import uuid
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.exceptions.base import BaseAPIException
from src.services.auth_service import AuthService
from src.integrations.google_oauth import create_oauth_client

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
    def __init__(self, db: AsyncSession, auth_service: AuthService) -> None:
        self.db = db
        self.auth_service = auth_service

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
        access_token = await self.auth_service.get_valid_google_access_token(user_id)

        if not access_token:
            raise BaseAPIException(
                message="Google integration not found or expired. Please log in with Google.",
                status_code=400,
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
        client = create_oauth_client()
        client.token = {"access_token": access_token, "token_type": "Bearer"}

        event_start_dt = start_time or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        event_end_dt = end_time or (datetime.now(timezone.utc) + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")

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

        url = settings.GOOGLE_CALENDAR_API_URL

        try:
            resp = await client.post(url, json=body)
        except Exception as e:
            raise BaseAPIException(
                message=f"Failed to connect to Google Calendar API: {e}",
                status_code=500,
            )

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
