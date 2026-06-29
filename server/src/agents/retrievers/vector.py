from langchain_mistralai import MistralAIEmbeddings
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.agents.schemas import RetrievedChunk
from src.models.meeting_chunk import MeetingChunk


class VectorRetriever:
    def __init__(
        self,
        db: AsyncSession,
        top_k: int = 10,
    ) -> None:
        self.db = db
        self.top_k = top_k
        self.embeddings = MistralAIEmbeddings(model="mistral-embed")

    async def search(
        self,
        query: str,
        filters: dict | None = None,
    ) -> list[RetrievedChunk]:
        query_embedding = await self.embeddings.aembed_query(query)

        distance = MeetingChunk.embedding.cosine_distance(query_embedding)
        stmt = (
            select(MeetingChunk, distance.label("distance"))
            .order_by(distance)
            .limit(self.top_k)
        )

        if filters:
            stmt = self._apply_filters(stmt, filters)

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

    def _apply_filters(self, stmt, filters: dict):
        meta = MeetingChunk.chunk_metadata

        if filters.get("workspace_id"):
            stmt = stmt.where(meta["workspace_id"].astext == str(filters["workspace_id"]))
        if filters.get("client_id"):
            stmt = stmt.where(meta["client_id"].astext == str(filters["client_id"]))
        if filters.get("project_id"):
            stmt = stmt.where(meta["project_id"].astext == str(filters["project_id"]))
        if filters.get("meeting_id"):
            stmt = stmt.where(meta["meeting_id"].astext == str(filters["meeting_id"]))

        return stmt
