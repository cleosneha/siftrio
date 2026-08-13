from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.models.base import APIKeyScope


class ApiKeyCreate(BaseModel):
    name: str
    scope: APIKeyScope = APIKeyScope.READ
    workspace_id: UUID | None = None


class ApiKeyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    key_prefix: str
    scope: APIKeyScope
    workspace_id: UUID | None = None
    last_used_at: datetime | None = None
    revoked_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class ApiKeyCreatedResponse(BaseModel):
    id: UUID
    name: str
    secret: str
    key_prefix: str
    scope: APIKeyScope
    workspace_id: UUID | None = None
    created_at: datetime | None = None
