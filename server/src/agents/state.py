from typing import Any, TypedDict

from sqlalchemy.ext.asyncio import AsyncSession

from src.agents.schemas import (
    Citation,
    ParsedQuery,
    RetrievedChunk,
    RetrievedKnowledge,
    RetrievedMeeting,
    RetrievalScope,
)


class ChatState(TypedDict):
    question: str
    db: AsyncSession
    user_context: dict[str, Any]
    parsed_query: ParsedQuery | None
    retrieval_scope: RetrievalScope | None
    retrieved_chunks: list[RetrievedChunk]
    meeting_analysis: list[RetrievedMeeting]
    knowledge_entities: list[RetrievedKnowledge]
    context: str | None
    answer: str | None
    citations: list[Citation]
    conversation_history: list[dict[str, str]]
