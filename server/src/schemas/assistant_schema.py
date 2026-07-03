from pydantic import BaseModel, Field


class AssistantQueryRequest(BaseModel):
    question: str = Field(min_length=1)
    thread_id: str = Field(default="", description="Conversation thread ID for checkpointing. Empty string starts a new conversation.")


class AssistantCitationResponse(BaseModel):
    meeting_id: str | None = None
    meeting_title: str = Field(default="")
    meeting_date: str | None = None
    chunk_index: int | None = None


class AssistantQueryResponse(BaseModel):
    answer: str
    citations: list[AssistantCitationResponse] = Field(default_factory=list)
    ambiguous_entities: dict | None = None
