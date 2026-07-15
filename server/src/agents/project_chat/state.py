from typing import Any, NotRequired, TypedDict

from src.agents.project_chat.schemas import (
    Citation,
    ParsedQuery,
    RetrievedChunk,
    RetrievedKnowledge,
    RetrievedMeeting,
    RetrievalScope,
    ToolPlan,
)
from src.mcp.schemas.common import ToolResult


class ChatState(TypedDict):
    question: str
    user_context: dict[str, Any]
    parsed_query: ParsedQuery | None
    retrieval_scope: RetrievalScope | None
    tool_plan: ToolPlan | None
    retrieved_chunks: list[RetrievedChunk]
    meeting_analysis: list[RetrievedMeeting]
    knowledge_entities: list[RetrievedKnowledge]
    tool_results: list[ToolResult]
    context: str | None
    answer: str | None
    citations: list[Citation]
    messages: NotRequired[list[dict[str, str]]]
    conversation_summary: NotRequired[str]
