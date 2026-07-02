from pydantic import BaseModel, Field


class AssistantQueryRequest(BaseModel):
    question: str = Field(min_length=1)


class AssistantCitationResponse(BaseModel):
    meeting_id: str | None = None
    meeting_title: str = Field(default="")
    meeting_date: str | None = None
    chunk_index: int | None = None


class AssistantQueryResponse(BaseModel):
    answer: str
    citations: list[AssistantCitationResponse] = Field(default_factory=list)
    ambiguous_entities: dict | None = None
