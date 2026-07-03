from pydantic import BaseModel, Field


class ConversationTurn(BaseModel):
    role: str = Field(description="user or assistant")
    content: str = Field(description="Message text")


class AssistantQueryRequest(BaseModel):
    question: str = Field(min_length=1)
    conversation_history: list[ConversationTurn] = Field(
        default_factory=list,
        description="Last 3-5 conversation turns for follow-up context",
    )


class AssistantCitationResponse(BaseModel):
    meeting_id: str | None = None
    meeting_title: str = Field(default="")
    meeting_date: str | None = None
    chunk_index: int | None = None


class AssistantQueryResponse(BaseModel):
    answer: str
    citations: list[AssistantCitationResponse] = Field(default_factory=list)
    ambiguous_entities: dict | None = None
