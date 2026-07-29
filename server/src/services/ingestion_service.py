import logging
from uuid import UUID

from sqlalchemy import text

from src.core.database import async_session_factory
from src.core.embeddings import embedder
from src.repositories.knowledge_repository import KnowledgeRepository
from src.repositories.meeting_analysis_repository import MeetingAnalysisRepository
from src.repositories.meeting_chunk_repository import MeetingChunkRepository
from src.repositories.meeting_repository import MeetingRepository
from src.services.knowledge_service import KnowledgeService
from src.services.meeting_analysis_service import MeetingAnalysisService
from src.services.transcript_service import TranscriptService

logger = logging.getLogger(__name__)


async def run_ingestion_pipeline(meeting_id: UUID, transcript_text: str) -> None:
    async with async_session_factory() as db:
        try:
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
            transcript_service = TranscriptService(
                db=db,
                meeting_repo=meeting_repo,
                chunk_repo=chunk_repo,
                embeddings=embedder,
                analysis_service=analysis_service,
            )

            await transcript_service.process_upload(meeting_id, transcript_text)

            await db.execute(
                text("UPDATE meetings SET transcript_status = 'completed' WHERE id = :mid"),
                {"mid": meeting_id},
            )
            await db.commit()
            logger.info("Ingestion completed for meeting %s", meeting_id)

        except Exception as e:
            logger.error("Ingestion failed for meeting %s: %s", meeting_id, e)
            try:
                await db.execute(
                    text("""
                        UPDATE meetings
                        SET transcript_status = 'failed', ingestion_error = :err
                        WHERE id = :mid
                    """),
                    {"mid": meeting_id, "err": str(e)},
                )
                await db.commit()
            except Exception as inner_e:
                logger.error("Failed to update error status for meeting %s: %s", meeting_id, inner_e)
