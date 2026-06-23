from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.meeting_chunk import MeetingChunk


class MeetingChunkRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(
        self,
        meeting_id: UUID,
        chunk_index: int,
        chunk_text: str,
        embedding: list[float],
        chunk_metadata: dict | None = None,
    ) -> MeetingChunk:
        chunk = MeetingChunk(
            meeting_id=meeting_id,
            chunk_index=chunk_index,
            chunk_text=chunk_text,
            embedding=embedding,
            chunk_metadata=chunk_metadata,
        )
        self.db.add(chunk)
        await self.db.commit()
        await self.db.refresh(chunk)
        return chunk

    async def list_by_meeting(self, meeting_id: UUID) -> list[MeetingChunk]:
        result = await self.db.execute(
            select(MeetingChunk)
            .where(MeetingChunk.meeting_id == meeting_id)
            .order_by(MeetingChunk.chunk_index)
        )
        return list(result.scalars().all())

    async def delete_by_meeting(self, meeting_id: UUID) -> None:
        result = await self.db.execute(
            select(MeetingChunk).where(MeetingChunk.meeting_id == meeting_id)
        )
        chunks = list(result.scalars().all())
        for chunk in chunks:
            await self.db.delete(chunk)
        await self.db.commit()
