from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ProjectCreate(BaseModel):
    client_id: str
    name: str
    description: str | None = None


class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    id: UUID
    client_id: UUID
    name: str
    description: str | None = None
    status: str = "active"
    created_at: datetime | None = None
    updated_at: datetime | None = None
