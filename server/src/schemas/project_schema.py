from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ProjectCreate(BaseModel):
    client_id: str
    name: str
    description: str | None = None


class ProjectResponse(BaseModel):
    id: UUID
    client_id: UUID
    name: str
    description: str | None = None
    status: str = "active"
    created_at: datetime | None = None
    updated_at: datetime | None = None
