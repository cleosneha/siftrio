from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class WorkspaceCreate(BaseModel):
    name: str
    description: str | None = None


class WorkspaceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str | None = None
    created_by: UUID | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
