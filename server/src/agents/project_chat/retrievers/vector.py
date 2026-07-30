from uuid import UUID

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from src.agents.project_chat.schemas import RetrievedChunk
from src.core.config import settings
from src.core.embeddings import EmbeddingService
from src.models.client import Client
from src.models.meeting import Meeting
from src.models.meeting_chunk import MeetingChunk


class VectorRetriever:
    def __init__(
        self,
        embeddings: EmbeddingService,
        top_k: int = 20,
    ) -> None:
        self.embeddings = embeddings
        self.top_k = top_k

    async def search(
        self,
        db: AsyncSession,
        query: str,
        filters: dict | None = None,
    ) -> list[RetrievedChunk]:
        query_embedding = await self.embeddings.embed_query(query)

        # ef_search controls the size of the dynamic candidate list during HNSW traversal.
        # Higher values improve recall at the cost of slightly higher latency.
        # Default pgvector value is 40, which may miss relevant results.
        # 100 is a reasonable production default for this use case.
        await db.execute(text(f"SET hnsw.ef_search = {settings.HNSW_EF_SEARCH}"))

        distance = MeetingChunk.embedding.cosine_distance(query_embedding)
        stmt = select(MeetingChunk, distance.label("distance"))

        if filters:
            stmt = self._apply_filters(stmt, filters)

        stmt = stmt.order_by(distance).limit(self.top_k)

        result = await db.execute(stmt)
        rows = result.all()

        return [
            RetrievedChunk(
                chunk_id=str(chunk.id),
                meeting_id=str(chunk.meeting_id),
                chunk_index=chunk.chunk_index,
                chunk_text=chunk.chunk_text,
                score=round(1.0 - (dist / 2.0), 4),
                vector_score=round(1.0 - (dist / 2.0), 4),
                metadata=chunk.chunk_metadata or {},
            )
            for chunk, dist in rows
        ]

    @staticmethod
    def _apply_filters(stmt, filters: dict):
        joined_meeting = False

        workspace_ids = filters.get("workspace_ids") or []
        if workspace_ids:
            stmt = stmt.join(Meeting, MeetingChunk.meeting_id == Meeting.id)
            stmt = stmt.join(Client, Meeting.client_id == Client.id)
            stmt = stmt.where(Client.workspace_id.in_([UUID(wid) for wid in workspace_ids]))
            joined_meeting = True

        if filters.get("client_ids"):
            if not joined_meeting:
                stmt = stmt.join(Meeting, MeetingChunk.meeting_id == Meeting.id)
                joined_meeting = True
            stmt = stmt.where(Meeting.client_id.in_([UUID(cid) for cid in filters["client_ids"]]))

        if filters.get("project_ids"):
            if not joined_meeting:
                stmt = stmt.join(Meeting, MeetingChunk.meeting_id == Meeting.id)
                joined_meeting = True
            stmt = stmt.where(Meeting.project_id.in_([UUID(pid) for pid in filters["project_ids"]]))

        if filters.get("meeting_ids"):
            stmt = stmt.where(MeetingChunk.meeting_id.in_([UUID(mid) for mid in filters["meeting_ids"]]))

        date_range = filters.get("date_range")
        if date_range and (date_range.get("start") or date_range.get("end")):
            if not joined_meeting:
                stmt = stmt.join(Meeting, MeetingChunk.meeting_id == Meeting.id)
            if date_range.get("start"):
                stmt = stmt.where(Meeting.meeting_date >= date_range["start"])
            if date_range.get("end"):
                stmt = stmt.where(Meeting.meeting_date <= date_range["end"])

        return stmt
