from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

from pydantic import BaseModel

from src.mcp.workspace_resolver import ResolvedWorkspace


class AuthContext(BaseModel):
    user_id: UUID
    workspace_ids: list[UUID]


@dataclass
class MCPContext:
    user_id: UUID
    workspace_ids: list[UUID] = field(default_factory=list)
    resolved_workspace: ResolvedWorkspace | None = None
