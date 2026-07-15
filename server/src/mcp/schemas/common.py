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
