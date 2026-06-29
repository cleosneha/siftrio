from typing import TypedDict

from src.agents.schemas import (
    Citation,
    ParsedQuery,
    RetrievedChunk,
    RetrievedContext,
    RetrievedKnowledge,
    RetrievedMeeting,
)


class ChatState(TypedDict):
    question: str
    parsed_query: ParsedQuery | None
    filters: dict | None
    retrieved_chunks: list[RetrievedChunk]
    meeting_analysis: list[RetrievedMeeting]
    knowledge_entities: list[RetrievedKnowledge]
    context: str | None
    answer: str | None
    citations: list[Citation]
