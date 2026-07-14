from datetime import date, time
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SuggestedMeetingItem(BaseModel):
    title: str = Field(description="Suggested meeting title")
    description: str | None = Field(default=None, description="Meeting description or agenda")
    meeting_date: str | None = Field(default=None, description="Resolved meeting date ISO format YYYY-MM-DD")
    start_time: str | None = Field(default=None, description="Resolved start time HH:MM")
    end_time: str | None = Field(default=None, description="Resolved end time HH:MM")
    confidence: float = Field(default=0.0, description="Confidence score 0-1")
    reason: str = Field(description="Why this meeting was suggested, including the original transcript quote")


class MeetingSuggestionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    id: UUID
    meeting_id: UUID
    title: str
    description: str | None = None
    suggested_date: date | None = None
    start_time: time | None = None
    end_time: time | None = None
    confidence: float
    reason: str
    status: str


class MeetingSuggestionScheduleRequest(BaseModel):
    title: str | None = Field(default=None, description="Override title")
    description: str | None = Field(default=None, description="Override description")
    meeting_date: str | None = Field(default=None, description="Override meeting date YYYY-MM-DD")
    start_time: str | None = Field(default=None, description="Override start time HH:MM")
    end_time: str | None = Field(default=None, description="Override end time HH:MM")
