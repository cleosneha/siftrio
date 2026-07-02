from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.repositories.knowledge_repository import KnowledgeRepository
from src.repositories.meeting_analysis_repository import MeetingAnalysisRepository
from src.repositories.meeting_chunk_repository import MeetingChunkRepository
from src.repositories.meeting_repository import MeetingRepository
from src.schemas.base_response import BaseResponse
from src.services.knowledge_service import KnowledgeService
from src.services.meeting_analysis_service import MeetingAnalysisService


class MeetingAnalysisController:
    def __init__(self, db: AsyncSession) -> None:
        meeting_repo = MeetingRepository(db)
        knowledge_service = KnowledgeService(
            db=db,
            repo=KnowledgeRepository(db),
            meeting_repo=meeting_repo,
            chunk_repo=MeetingChunkRepository(db),
        )
        self.service = MeetingAnalysisService(
            db=db,
            repo=MeetingAnalysisRepository(db),
            meeting_repo=meeting_repo,
            knowledge_service=knowledge_service,
        )

    async def get_analysis(self, meeting_id: UUID) -> BaseResponse:
        data = await self.service.get_analysis(meeting_id)
        if data is None:
            return BaseResponse(
                success=False,
                message="Analysis not found. Upload a transcript and regenerate.",
                data=None,
            )
        return BaseResponse(data=data)

    async def regenerate(self, meeting_id: UUID) -> BaseResponse:
        try:
            data = await self.service.generate_analysis(meeting_id)
            return BaseResponse(message="Analysis regenerated successfully", data=data)
        except ValueError as e:
            return BaseResponse(success=False, message=str(e), data=None)
