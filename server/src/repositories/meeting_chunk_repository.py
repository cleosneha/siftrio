from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.meeting_chunk import MeetingChunk


class MeetingChunkRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create(
        self,
        meeting_id: UUID,
        chunk_index: int,
        chunk_text: str,
        embedding: list[float],
        chunk_metadata: dict | None = None,
        workspace_id: UUID | None = None,
        client_id: UUID | None = None,
        project_id: UUID | None = None,
    ) -> MeetingChunk:
        chunk = MeetingChunk(
            meeting_id=meeting_id,
            chunk_index=chunk_index,
            chunk_text=chunk_text,
            embedding=embedding,
            chunk_metadata=chunk_metadata,
            workspace_id=workspace_id,
            client_id=client_id,
            project_id=project_id,
        )
        self._db.add(chunk)
        await self._db.flush()
        await self._db.refresh(chunk)
        return chunk

    async def delete_by_meeting(self, meeting_id: UUID) -> None:
        await self._db.execute(
            delete(MeetingChunk).where(MeetingChunk.meeting_id == meeting_id)
        )
