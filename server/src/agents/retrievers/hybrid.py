from sqlalchemy.ext.asyncio import AsyncSession

from src.agents.schemas import ParsedQuery, RetrievedContext
from src.agents.retrievers.knowledge import KnowledgeRetriever
from src.agents.retrievers.meetings import MeetingRetriever
from src.agents.retrievers.vector import VectorRetriever
from src.core.embeddings import EmbeddingService, embedder


class HybridRetriever:
    def __init__(
        self,
        db: AsyncSession,
        embeddings: EmbeddingService = embedder,
    ) -> None:
        self._vector = VectorRetriever(db, embeddings=embeddings)
        self._meetings = MeetingRetriever(db)
        self._knowledge = KnowledgeRetriever(db)

    async def retrieve(self, query: ParsedQuery) -> RetrievedContext:
        filters = {
            k: v
            for k, v in {
                "workspace_id": query.workspace_id,
                "client_id": query.client_id,
                "project_id": query.project_id,
                "meeting_id": query.meeting_id,
            }.items()
            if v is not None
        }

        chunks = await self._vector.search(query.original_question, filters)
        meeting_ids = list(set(c.meeting_id for c in chunks))
        meetings = await self._meetings.get_by_ids(meeting_ids)
        knowledge = await self._knowledge.search(filters)

        return RetrievedContext(
            chunks=chunks,
            meetings=meetings,
            knowledge=knowledge,
        )
