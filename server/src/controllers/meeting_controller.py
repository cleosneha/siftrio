from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.meeting_repository import MeetingRepository
from src.schemas.base_response import BaseResponse
from src.schemas.meeting_schema import MeetingResponse


class MeetingController:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = MeetingRepository(db)

    async def get_by_id(self, meeting_id: str) -> BaseResponse:
        meeting = await self.repo.get_by_id(UUID(meeting_id))
        if meeting is None:
            return BaseResponse(success=False, message="Meeting not found", data=None)
        data = MeetingResponse(
            id=str(meeting.id),
            client_id=str(meeting.client_id),
            project_id=str(meeting.project_id) if meeting.project_id else None,
            title=meeting.title,
            meeting_type=meeting.meeting_type.value,
            tags=meeting.tags,
            transcript=meeting.transcript,
            meeting_date=meeting.meeting_date.isoformat() if meeting.meeting_date else None,
            created_at=meeting.created_at.isoformat() if meeting.created_at else None,
            updated_at=meeting.updated_at.isoformat() if meeting.updated_at else None,
        ).model_dump()
        return BaseResponse(data=data)
