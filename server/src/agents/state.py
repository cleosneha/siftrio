from typing import Any, NotRequired, TypedDict

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
    user_context: dict[str, Any]
    parsed_query: ParsedQuery | None
    retrieval_scope: RetrievalScope | None
    retrieved_chunks: list[RetrievedChunk]
    meeting_analysis: list[RetrievedMeeting]
    knowledge_entities: list[RetrievedKnowledge]
    context: str | None
    answer: str | None
    citations: list[Citation]
    messages: NotRequired[list[dict[str, str]]]
    conversation_summary: NotRequired[str]
