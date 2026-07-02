from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions.base import BaseAPIException
from src.models.meeting import MeetingProvider, MeetingType
from src.repositories.client_repository import ClientRepository
from src.repositories.meeting_repository import MeetingRepository
from src.repositories.project_repository import ProjectRepository
from src.services.meeting_integration_service import MeetingIntegrationService


class MeetingService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = MeetingRepository(db)
        self.client_repo = ClientRepository(db)
        self.project_repo = ProjectRepository(db)
        self.integration_service = MeetingIntegrationService(db)

    async def create(
        self,
        client_id: str,
        project_id: str | None,
        title: str,
        meeting_type: str,
        tags: list[str],
        meeting_date: str | None = None,
        meeting_provider: str = "manual",
        meeting_url: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
        user_id: UUID | None = None,
        user_email: str | None = None,
        guest_emails: list[str] | None = None,
    ) -> dict:
        cl_id = UUID(client_id)
        client = await self.client_repo.get_by_id(cl_id)
        if client is None:
            raise BaseAPIException(
                message="Client not found",
                status_code=404,
            )

        if meeting_type == "project":
            if not project_id:
                raise BaseAPIException(
                    message="Project ID is required for project meetings",
                    status_code=400,
                )
            pr_id = UUID(project_id)
            project = await self.project_repo.get_by_id(pr_id)
            if project is None:
                raise BaseAPIException(
                    message="Project not found",
                    status_code=404,
                )

        mt = MeetingType(meeting_type) if meeting_type == "miscellaneous" else MeetingType.PROJECT
        pr_id = UUID(project_id) if project_id else None
        parsed_date = datetime.fromisoformat(meeting_date) if meeting_date else None

        utc_start = datetime.fromisoformat(start_time.replace("Z", "+00:00")) if start_time else None
        utc_end = datetime.fromisoformat(end_time.replace("Z", "+00:00")) if end_time else None

        mp = MeetingProvider.GOOGLE_MEET if meeting_provider == "google_meet" else MeetingProvider.MANUAL
        resolved_url = meeting_url

        google_calendar_event_id = None
        google_meet_url = None
        google_meet_code = None
        transcript_status = None

        if mp == MeetingProvider.GOOGLE_MEET:
            if not user_id:
                raise BaseAPIException(
                    message="User authentication required to create Google Meet",
                    status_code=401,
                )
            result = await self.integration_service.create_google_meet(
                user_id=user_id,
                title=title,
                description=f"Meeting: {title}",
                start_time=start_time,
                end_time=end_time,
                guest_emails=guest_emails,
                user_email=user_email,
            )
            resolved_url = result["meet_url"]
            google_calendar_event_id = result["event_id"]
            google_meet_url = result["meet_url"]
            google_meet_code = result["meet_code"]
            transcript_status = "pending"

        meeting = await self.repo.create(
            client_id=cl_id,
            project_id=pr_id,
            title=title,
            meeting_type=mt,
            tags=tags,
            meeting_date=parsed_date,
            meeting_provider=mp,
            meeting_url=resolved_url,
            start_time=utc_start,
            end_time=utc_end,
            guest_emails=guest_emails,
            google_calendar_event_id=google_calendar_event_id,
            google_meet_url=google_meet_url,
            google_meet_code=google_meet_code,
            transcript_status=transcript_status,
        )

        await self.db.commit()

        return {
            "id": str(meeting.id),
            "client_id": str(meeting.client_id),
            "project_id": str(meeting.project_id) if meeting.project_id else None,
            "title": meeting.title,
            "meeting_type": meeting.meeting_type.value,
            "tags": meeting.tags,
            "transcript": meeting.transcript,
            "meeting_date": meeting.meeting_date.isoformat() if meeting.meeting_date else None,
            "start_time": meeting.start_time.isoformat().replace("+00:00", "Z") if meeting.start_time else None,
            "end_time": meeting.end_time.isoformat().replace("+00:00", "Z") if meeting.end_time else None,
            "meeting_provider": meeting.meeting_provider.value,
            "meeting_url": meeting.meeting_url,
            "google_calendar_event_id": meeting.google_calendar_event_id,
            "google_meet_url": meeting.google_meet_url,
            "google_meet_code": meeting.google_meet_code,
            "fireflies_meeting_id": meeting.fireflies_meeting_id,
            "transcript_status": meeting.transcript_status if meeting.transcript_status else None,
            "guest_emails": meeting.guest_emails or [],
            "created_at": meeting.created_at.isoformat().replace("+00:00", "Z") if meeting.created_at else None,
            "updated_at": meeting.updated_at.isoformat().replace("+00:00", "Z") if meeting.updated_at else None,
        }
