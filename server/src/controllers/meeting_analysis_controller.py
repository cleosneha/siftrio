from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.schemas.base_response import BaseResponse
from src.services.meeting_analysis_service import MeetingAnalysisService


class MeetingAnalysisController:
    def __init__(self, db: AsyncSession) -> None:
        self.service = MeetingAnalysisService(db)

    async def get_analysis(self, meeting_id: str) -> BaseResponse:
        data = await self.service.get_analysis(UUID(meeting_id))
        if data is None:
            return BaseResponse(
                success=False,
                message="Analysis not found. Upload a transcript and regenerate.",
                data=None,
            )
        return BaseResponse(data=data)

    async def regenerate(self, meeting_id: str) -> BaseResponse:
        try:
            data = await self.service.generate_analysis(UUID(meeting_id))
            return BaseResponse(message="Analysis regenerated successfully", data=data)
        except ValueError as e:
            return BaseResponse(success=False, message=str(e), data=None)
