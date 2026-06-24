import json
import logging
import uuid
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions.base import BaseAPIException
from src.repositories.auth_repository import AuthRepository
from src.tools.google_oauth import create_oauth_client, refresh_google_token

logger = logging.getLogger(__name__)


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
    ) -> str:
        integration = await self.repo.get_integration(user_id, "google")
        if not integration or not integration.access_token:
            raise BaseAPIException(
                message="Google integration not found. Please log in with Google.",
                status_code=400,
            )

        access_token = integration.access_token
        logger.info("Google granted scopes: %s", integration.scopes)

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

        meet_url = await self._create_calendar_event(
            access_token=access_token,
            title=title,
            description=description,
            start_time=start_time,
            end_time=end_time,
        )

        return meet_url

    async def _create_calendar_event(
        self,
        access_token: str,
        title: str,
        description: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
    ) -> str:
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

        body = {
            "summary": title,
            "description": description or "",
            "start": event_start,
            "end": event_end,
            "conferenceData": {
                "createRequest": {
                    "requestId": str(uuid.uuid4()),
                }
            },
        }

        url = "https://www.googleapis.com/calendar/v3/calendars/primary/events?conferenceDataVersion=1"

        logger.info("Google Calendar API request URL: %s", url)
        logger.info("Google Calendar API request payload: %s", json.dumps(body, indent=2, default=str))

        try:
            resp = await client.post(url, json=body)
        except Exception as e:
            raise BaseAPIException(
                message=f"Failed to connect to Google Calendar API: {e}",
                status_code=500,
            )

        logger.info("Google Calendar API response status: %s", resp.status_code)
        logger.info("Google Calendar API response body: %s", resp.text)

        if resp.status_code != 200:
            raise BaseAPIException(
                message=f"Google Calendar API error ({resp.status_code}): {resp.text}",
                status_code=500,
            )

        event_data = resp.json()
        meet_url = event_data.get("hangoutLink") or (
            event_data.get("conferenceData", {}).get("entryPoints", [{}])[0].get("uri")
        )

        if not meet_url:
            raise BaseAPIException(
                message="Google Meet link could not be generated from the event response",
                status_code=500,
            )

        return meet_url
