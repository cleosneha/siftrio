from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class MemberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    role: str
    created_at: datetime | None = None

    email: str = ""
    full_name: str | None = None
    profile_picture: str | None = None
