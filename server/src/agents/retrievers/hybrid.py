from sqlalchemy.ext.asyncio import AsyncSession

from src.agents.schemas import RetrievedContext, RetrievalScope
from src.agents.retrievers.keyword import KeywordRetriever
from src.agents.retrievers.knowledge import KnowledgeRetriever
from src.agents.retrievers.meetings import MeetingRetriever
from src.agents.retrievers.reranker import rrf_merge
from src.agents.retrievers.vector import VectorRetriever
from src.core.embeddings import EmbeddingService, embedder


class HybridRetriever:
    def __init__(
        self,
        embeddings: EmbeddingService = embedder,
    ) -> None:
        self._vector = VectorRetriever(embeddings=embeddings)
        self._keyword = KeywordRetriever()
        self._meetings = MeetingRetriever()
        self._knowledge = KnowledgeRetriever()

    async def retrieve(
        self,
        db: AsyncSession,
        scope: RetrievalScope,
    ) -> RetrievedContext:
        filters = self._build_filters(scope)

        vector_chunks = await self._vector.search(db, scope.query_text, filters)
        keyword_chunks = await self._keyword.search(db, scope.query_text, filters)

        chunks = rrf_merge(vector_chunks, keyword_chunks, top_k=10)

        meeting_ids = list(set(c.meeting_id for c in chunks))
        meetings = await self._meetings.get_by_ids(db, meeting_ids, date_range=scope.date_range)
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
        if scope.keywords:
            filters["keywords"] = scope.keywords
        if scope.date_range:
            filters["date_range"] = scope.date_range
        return filters
