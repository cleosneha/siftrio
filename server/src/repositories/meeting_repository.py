from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.meeting import Meeting, MeetingType


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
        meeting_date: str | None = None,
    ) -> Meeting:
        meeting = Meeting(
            client_id=client_id,
            project_id=project_id,
            title=title,
            meeting_type=meeting_type,
            tags=tags,
            meeting_date=meeting_date,
        )
        self.db.add(meeting)
        await self.db.commit()
        await self.db.refresh(meeting)
        return meeting

    async def get_by_id(self, meeting_id: UUID) -> Meeting | None:
        result = await self.db.execute(
            select(Meeting).where(Meeting.id == meeting_id)
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
