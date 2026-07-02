from uuid import UUID

from fastapi import Depends, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.embeddings import embedder
from src.repositories.knowledge_repository import KnowledgeRepository
from src.repositories.meeting_analysis_repository import MeetingAnalysisRepository
from src.repositories.meeting_chunk_repository import MeetingChunkRepository
from src.repositories.meeting_repository import MeetingRepository
from src.schemas.base_response import BaseResponse
from src.services.knowledge_service import KnowledgeService
from src.services.meeting_analysis_service import MeetingAnalysisService
from src.services.transcript_service import TranscriptService


class TranscriptController:
    def __init__(self, db: AsyncSession) -> None:
        meeting_repo = MeetingRepository(db)
        chunk_repo = MeetingChunkRepository(db)
        knowledge_service = KnowledgeService(
            db=db,
            repo=KnowledgeRepository(db),
            meeting_repo=meeting_repo,
            chunk_repo=chunk_repo,
        )
        analysis_service = MeetingAnalysisService(
            db=db,
            repo=MeetingAnalysisRepository(db),
            meeting_repo=meeting_repo,
            knowledge_service=knowledge_service,
        )
        self.service = TranscriptService(
            db=db,
            meeting_repo=meeting_repo,
            chunk_repo=chunk_repo,
            embeddings=embedder,
            analysis_service=analysis_service,
        )

    async def upload(self, meeting_id: str, file: UploadFile) -> BaseResponse:
        if not file.filename or not file.filename.endswith(".txt"):
            return BaseResponse(
                success=False,
                message="Only .txt files are supported",
                data=None,
            )
        content = await file.read()
        transcript_text = content.decode("utf-8")
        data = await self.service.process_upload(UUID(meeting_id), transcript_text)
        return BaseResponse(message="Transcript processed successfully", data=data)
