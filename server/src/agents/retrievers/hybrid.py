from sqlalchemy.ext.asyncio import AsyncSession

from src.agents.schemas import RetrievedContext, RetrievalScope
from src.agents.retrievers.knowledge import KnowledgeRetriever
from src.agents.retrievers.meetings import MeetingRetriever
from src.agents.retrievers.vector import VectorRetriever
from src.core.embeddings import EmbeddingService, embedder


class HybridRetriever:
    def __init__(
        self,
        embeddings: EmbeddingService = embedder,
    ) -> None:
        self._vector = VectorRetriever(embeddings=embeddings)
        self._meetings = MeetingRetriever()
        self._knowledge = KnowledgeRetriever()

    async def retrieve(
        self,
        db: AsyncSession,
        scope: RetrievalScope,
    ) -> RetrievedContext:
        filters = self._build_filters(scope)

        chunks = await self._vector.search(db, scope.query_text, filters)
        meeting_ids = list(set(c.meeting_id for c in chunks))
        meetings = await self._meetings.get_by_ids(db, meeting_ids)
        knowledge = await self._knowledge.search(db, filters)

        return RetrievedContext(
            chunks=chunks,
            meetings=meetings,
            knowledge=knowledge,
        )

    @staticmethod
    def _build_filters(scope: RetrievalScope) -> dict:
        filters: dict = {}
        if scope.workspace_ids:
            filters["workspace_ids"] = scope.workspace_ids
        if scope.client_ids:
            filters["client_ids"] = scope.client_ids
        if scope.project_ids:
            filters["project_ids"] = scope.project_ids
        if scope.meeting_ids:
            filters["meeting_ids"] = scope.meeting_ids
        return filters
