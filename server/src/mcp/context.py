from dataclasses import dataclass
from uuid import UUID

from pydantic import BaseModel


class AuthContext(BaseModel):
    workspace_id: UUID
    user_id: UUID


@dataclass
class MCPContext:
    workspace_id: UUID
    user_id: UUID
