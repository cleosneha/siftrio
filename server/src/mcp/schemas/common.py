from typing import Any

from pydantic import BaseModel, Field


class ToolResult(BaseModel):
    success: bool = True
    message: str = "Success"
    data: Any = None


class PaginatedResult(BaseModel):
    items: list[Any] = Field(default_factory=list)
    total: int = 0
    limit: int = 50
    offset: int = 0


class AmbiguousMatch(BaseModel):
    workspace_id: str
    workspace_name: str
    resource_type: str
    resource_name: str


class AmbiguousResult(BaseModel):
    status: str = "ambiguous"
    message: str = "Multiple matching resources found."
    matches: list[AmbiguousMatch] = Field(default_factory=list)


class ToolParameterSpec(BaseModel):
    name: str
    type: str
    description: str
    required: bool = True
    default: Any = None


class ToolSpec(BaseModel):
    name: str
    description: str
    parameters: list[ToolParameterSpec] = Field(default_factory=list)
    entity_type: str | None = Field(
        default=None,
        description="Entity type this tool hydrates (e.g. 'action_item', 'meeting'). "
        "Used by the entity hydrator to resolve which tool fetches structured data.",
    )
