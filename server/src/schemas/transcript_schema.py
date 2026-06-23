from pydantic import BaseModel


class TranscriptUploadResponse(BaseModel):
    meeting_id: str
    chunk_count: int
    title: str
