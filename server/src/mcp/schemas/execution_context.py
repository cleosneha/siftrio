from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class ToolExecutionContext:
    user_id: UUID
    workspace_ids: list[UUID]
