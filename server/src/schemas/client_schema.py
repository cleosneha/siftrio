from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ClientCreate(BaseModel):
    workspace_id: str
    name: str
    description: str | None = None


class ClientResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workspace_id: UUID
    name: str
    description: str | None = None
    project_count: int = 0
    created_at: datetime | None = None
    updated_at: datetime | None = None
