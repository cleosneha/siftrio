from sqlalchemy.ext.asyncio import AsyncSession

from src.agents.graph import build_chat_graph
from src.agents.retrievers.hybrid import HybridRetriever
from src.agents.schemas import Citation
from src.agents.services.context_builder import ContextBuilderService
from src.agents.services.llm import LLMService
from src.agents.services.query_parser import QueryParserService
from src.agents.state import ChatState
from src.core.embeddings import embedder


class ChatService:
    def __init__(
        self,
        db: AsyncSession,
        llm: LLMService | None = None,
    ) -> None:
        self._llm = llm or LLMService()
        self._query_parser = QueryParserService(self._llm)
        self._retriever = HybridRetriever(db, embeddings=embedder)
        self._context_builder = ContextBuilderService()
        self._graph = build_chat_graph(
            self._query_parser,
            self._retriever,
            self._context_builder,
            self._llm,
        )

    async def chat(self, question: str) -> dict[str, object]:
        initial_state: ChatState = {
            "question": question,
            "parsed_query": None,
            "filters": None,
            "retrieved_chunks": [],
            "meeting_analysis": [],
            "knowledge_entities": [],
            "context": None,
            "answer": None,
            "citations": [],
        }

        result = await self._graph.ainvoke(initial_state)
        citations = result.get("citations", [])
        serialized_citations = [
            citation.model_dump() if isinstance(citation, Citation) else citation
            for citation in citations
        ]

        return {
            "answer": result.get("answer") or "",
            "citations": serialized_citations,
        }
