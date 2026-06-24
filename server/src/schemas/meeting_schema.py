from pydantic import BaseModel


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


class MeetingResponse(BaseModel):
    id: str
    client_id: str
    project_id: str | None = None
    title: str
    meeting_type: str = "project"
    tags: list[str] = []
    transcript: str | None = None
    meeting_date: str | None = None
    start_time: str | None = None
    end_time: str | None = None
    meeting_provider: str = "manual"
    meeting_url: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
