from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class InviteMemberRequest(BaseModel):
    email: str


class InvitationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    resource_type: str
    resource_id: UUID
    status: str
    token: str
    expires_at: datetime
    accepted_at: datetime | None = None
    created_at: datetime | None = None


class PendingInvitationItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    resource_type: str
    resource_id: UUID
    status: str
    expires_at: datetime
    created_at: datetime | None = None
