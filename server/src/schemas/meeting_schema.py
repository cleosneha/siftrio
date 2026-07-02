from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class MeetingCreate(BaseModel):
    client_id: str
    project_id: str | None = None
    title: str
    meeting_type: str = "project"
    tags: list[str] = []
    meeting_date: str | None = None
    meeting_provider: str = "manual"
    meeting_url: str | None = None
    start_time: str | None = None
    end_time: str | None = None
    guest_emails: list[str] = []


class MeetingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    id: UUID
    client_id: UUID
    project_id: UUID | None = None
    title: str
    meeting_type: str = "project"
    tags: list[str] = []
    transcript: str | None = None
    meeting_date: datetime | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    meeting_provider: str = "manual"
    meeting_url: str | None = None
    google_calendar_event_id: str | None = None
    google_meet_url: str | None = None
    google_meet_code: str | None = None
    fireflies_meeting_id: str | None = None
    transcript_status: str | None = None
    guest_emails: list[str] = []
    created_at: datetime | None = None
    updated_at: datetime | None = None


class TranscriptStatusResponse(BaseModel):
    transcript_status: str | None
    fireflies_meeting_id: str | None
