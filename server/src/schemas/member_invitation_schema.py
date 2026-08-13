from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.models.base import MemberRole


class InviteMemberRequest(BaseModel):
    email: str
    role: MemberRole = MemberRole.MEMBER


class InvitationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    resource_type: str
    resource_id: UUID
    role: MemberRole
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
    role: MemberRole
    status: str
    expires_at: datetime
    created_at: datetime | None = None
