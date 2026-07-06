from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.repositories.meeting_suggestion_repository import MeetingSuggestionRepository
from src.schemas.base_response import BaseResponse
from src.schemas.meeting_suggestion_schema import MeetingSuggestionScheduleRequest
from src.services.meeting_suggestion_service import MeetingSuggestionService


class MeetingSuggestionController:
    def __init__(self, db: AsyncSession) -> None:
        self.service = MeetingSuggestionService(
            db=db,
            repo=MeetingSuggestionRepository(db),
        )

    async def list_suggestions(self, meeting_id: UUID) -> BaseResponse:
        data = await self.service.list_suggestions(meeting_id)
        return BaseResponse(data=data)

    async def schedule(
        self,
        suggestion_id: UUID,
        body: MeetingSuggestionScheduleRequest,
    ) -> BaseResponse:
        try:
            data = await self.service.schedule(
                suggestion_id,
                title=body.title,
                description=body.description,
                meeting_date=body.meeting_date,
                start_time=body.start_time,
                end_time=body.end_time,
            )
            return BaseResponse(message="Suggestion scheduled", data=data)
        except ValueError as e:
            return BaseResponse(success=False, message=str(e), data=None)

    async def dismiss(self, suggestion_id: UUID) -> BaseResponse:
        try:
            data = await self.service.dismiss(suggestion_id)
            return BaseResponse(message="Suggestion dismissed", data=data)
        except ValueError as e:
            return BaseResponse(success=False, message=str(e), data=None)
