from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.meeting import Meeting, MeetingProvider, MeetingType, TranscriptStatus


class MeetingRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(
        self,
        client_id: UUID,
        project_id: UUID | None,
        title: str,
        meeting_type: MeetingType,
        tags: list[str],
        meeting_date: datetime | None = None,
        meeting_provider: MeetingProvider = MeetingProvider.MANUAL,
        meeting_url: str | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        guest_emails: list[str] | None = None,
        google_calendar_event_id: str | None = None,
        google_meet_url: str | None = None,
        google_meet_code: str | None = None,
        transcript_status: str | None = None,
    ) -> Meeting:
        meeting = Meeting(
            client_id=client_id,
            project_id=project_id,
            title=title,
            meeting_type=meeting_type,
            tags=tags,
            meeting_date=meeting_date,
            meeting_provider=meeting_provider,
            meeting_url=meeting_url,
            start_time=start_time,
            end_time=end_time,
            guest_emails=guest_emails,
            google_calendar_event_id=google_calendar_event_id,
            google_meet_url=google_meet_url,
            google_meet_code=google_meet_code,
            transcript_status=transcript_status,
        )
        self.db.add(meeting)
        await self.db.commit()
        await self.db.refresh(meeting)
        return meeting

    async def update(self, meeting_id: UUID, **kwargs) -> Meeting | None:
        meeting = await self.get_by_id(meeting_id)
        if meeting is None:
            return None
        for key, value in kwargs.items():
            setattr(meeting, key, value)
        await self.db.commit()
        await self.db.refresh(meeting)
        return meeting

    async def get_by_id(self, meeting_id: UUID) -> Meeting | None:
        result = await self.db.execute(
            select(Meeting).where(Meeting.id == meeting_id)
        )
        return result.scalar_one_or_none()

    async def find_by_google_event_id(self, event_id: str) -> Meeting | None:
        result = await self.db.execute(
            select(Meeting).where(Meeting.google_calendar_event_id == event_id)
        )
        return result.scalar_one_or_none()

    async def find_by_google_meet_url(self, meet_url: str) -> Meeting | None:
        result = await self.db.execute(
            select(Meeting).where(Meeting.google_meet_url == meet_url)
        )
        return result.scalar_one_or_none()

    async def find_by_google_meet_code(self, meet_code: str) -> Meeting | None:
        result = await self.db.execute(
            select(Meeting).where(Meeting.google_meet_code == meet_code)
        )
        return result.scalar_one_or_none()

    async def list_by_client(self, client_id: UUID) -> list[Meeting]:
        result = await self.db.execute(
            select(Meeting)
            .where(Meeting.client_id == client_id)
            .order_by(Meeting.created_at.desc())
        )
        return list(result.scalars().all())

    async def list_by_project(self, project_id: UUID) -> list[Meeting]:
        result = await self.db.execute(
            select(Meeting)
            .where(Meeting.project_id == project_id)
            .order_by(Meeting.created_at.desc())
        )
        return list(result.scalars().all())

    async def list_miscellaneous_by_client(self, client_id: UUID) -> list[Meeting]:
        result = await self.db.execute(
            select(Meeting)
            .where(
                Meeting.client_id == client_id,
                Meeting.meeting_type == MeetingType.MISCELLANEOUS,
            )
            .order_by(Meeting.created_at.desc())
        )
        return list(result.scalars().all())

    async def delete(self, meeting_id: UUID) -> None:
        meeting = await self.get_by_id(meeting_id)
        if meeting:
            await self.db.delete(meeting)
            await self.db.commit()
