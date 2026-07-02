from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.agents.schemas import RetrievedChunk
from src.core.embeddings import EmbeddingService
from src.models.meeting_chunk import MeetingChunk


class VectorRetriever:
    def __init__(
        self,
        db: AsyncSession,
        embeddings: EmbeddingService,
        top_k: int = 10,
    ) -> None:
        self.db = db
        self.embeddings = embeddings
        self.top_k = top_k

    async def search(
        self,
        query: str,
        filters: dict | None = None,
    ) -> list[RetrievedChunk]:
        query_embedding = await self.embeddings.embed_query(query)

        distance = MeetingChunk.embedding.cosine_distance(query_embedding)
        stmt = select(MeetingChunk, distance.label("distance"))

        if filters:
            stmt = self._apply_filters(stmt, filters)

        stmt = stmt.order_by(distance).limit(self.top_k)

        result = await self.db.execute(stmt)
        rows = result.all()

        return [
            RetrievedChunk(
                chunk_id=str(chunk.id),
                meeting_id=str(chunk.meeting_id),
                chunk_index=chunk.chunk_index,
                chunk_text=chunk.chunk_text,
                score=round(1.0 - (dist / 2.0), 4),
                metadata=chunk.chunk_metadata or {},
            )
            for chunk, dist in rows
        ]

    @staticmethod
    def _apply_filters(stmt, filters: dict):
        if filters.get("workspace_id"):
            stmt = stmt.where(MeetingChunk.workspace_id == UUID(filters["workspace_id"]))
        if filters.get("client_id"):
            stmt = stmt.where(MeetingChunk.client_id == UUID(filters["client_id"]))
        if filters.get("project_id"):
            stmt = stmt.where(MeetingChunk.project_id == UUID(filters["project_id"]))
        if filters.get("meeting_id"):
            stmt = stmt.where(MeetingChunk.meeting_id == UUID(filters["meeting_id"]))

        return stmt
