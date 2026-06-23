from uuid import UUID

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_mistralai import MistralAIEmbeddings
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.meeting_repository import MeetingRepository
from src.repositories.meeting_chunk_repository import MeetingChunkRepository


class TranscriptService:
    def __init__(self, db: AsyncSession) -> None:
        self.meeting_repo = MeetingRepository(db)
        self.chunk_repo = MeetingChunkRepository(db)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        self.embeddings = MistralAIEmbeddings(model="mistral-embed")

    async def process_upload(
        self,
        meeting_id: UUID,
        transcript_text: str,
    ) -> dict:
        meeting = await self.meeting_repo.get_by_id(meeting_id)
        if meeting is None:
            raise ValueError("Meeting not found")

        meeting.transcript = transcript_text
        await self.meeting_repo.db.commit()

        await self.chunk_repo.delete_by_meeting(meeting_id)

        chunks = self.text_splitter.split_text(transcript_text)
        texts_to_embed = [c for c in chunks if c.strip()]
        embeddings_list = await self.embeddings.aembed_documents(texts_to_embed)

        for i, (chunk_text, embedding) in enumerate(zip(chunks, embeddings_list)):
            await self.chunk_repo.create(
                meeting_id=meeting_id,
                chunk_index=i,
                chunk_text=chunk_text,
                embedding=embedding,
                chunk_metadata={
                    "chunk_size": len(chunk_text),
                    "meeting_title": meeting.title,
                },
            )

        return {
            "meeting_id": str(meeting.id),
            "chunk_count": len(chunks),
            "title": meeting.title,
        }
