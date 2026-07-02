from uuid import UUID

from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.embeddings import EmbeddingService
from src.repositories.meeting_chunk_repository import MeetingChunkRepository
from src.repositories.meeting_repository import MeetingRepository
from src.services.meeting_analysis_service import MeetingAnalysisService


class TranscriptService:
    def __init__(
        self,
        db: AsyncSession,
        meeting_repo: MeetingRepository,
        chunk_repo: MeetingChunkRepository,
        embeddings: EmbeddingService,
        analysis_service: MeetingAnalysisService,
    ) -> None:
        self.db = db
        self.meeting_repo = meeting_repo
        self.chunk_repo = chunk_repo
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            length_function=len,
        )
        self.embeddings = embeddings
        self.analysis_service = analysis_service

    async def process_upload(
        self,
        meeting_id: UUID,
        transcript_text: str,
    ) -> dict:
        meeting = await self.meeting_repo.get_by_id(meeting_id)
        if meeting is None:
            raise ValueError("Meeting not found")

        meeting.transcript = transcript_text
        await self.db.flush()

        await self.chunk_repo.delete_by_meeting(meeting_id)

        chunks = self.text_splitter.split_text(transcript_text)
        texts_to_embed = [c for c in chunks if c.strip()]
        embeddings_list = await self.embeddings.embed_documents(texts_to_embed)

        workspace_id = meeting.client.workspace_id if meeting.client else None
        client_id = meeting.client_id
        project_id = meeting.project_id

        for i, (chunk_text, embedding) in enumerate(zip(chunks, embeddings_list)):
            await self.chunk_repo.create(
                meeting_id=meeting_id,
                chunk_index=i,
                chunk_text=chunk_text,
                embedding=embedding,
                workspace_id=workspace_id,
                client_id=client_id,
                project_id=project_id,
                chunk_metadata={
                    "chunk_size": len(chunk_text),
                    "meeting_title": meeting.title,
                    "meeting_type": meeting.meeting_type.value,
                    "meeting_date": meeting.meeting_date.isoformat() if meeting.meeting_date else None,
                    "project_name": meeting.project.name if meeting.project else None,
                    "client_name": meeting.client.name if meeting.client else None,
                    "workspace_name": meeting.client.workspace.name if meeting.client and meeting.client.workspace else None,
                    "created_at": meeting.created_at.isoformat() if meeting.created_at else None,
                },
            )

        await self.analysis_service.generate_analysis(meeting_id)

        await self.db.commit()

        return {
            "meeting_id": str(meeting.id),
            "chunk_count": len(chunks),
            "title": meeting.title,
        }
