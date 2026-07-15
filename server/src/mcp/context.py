from dataclasses import dataclass, field
from uuid import UUID

from pydantic import BaseModel


class AuthContext(BaseModel):
    user_id: UUID
    workspace_ids: list[UUID]


@dataclass
class MCPContext:
    user_id: UUID
    workspace_ids: list[UUID] = field(default_factory=list)
