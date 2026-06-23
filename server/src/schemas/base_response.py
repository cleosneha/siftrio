from typing import Any, Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class BaseResponse(BaseModel, Generic[T]):
    success: bool = True
    message: str = "Success"
    data: T | None = None


class ErrorResponse(BaseModel):
    success: bool = False
    message: str = "Error"
    errors: list[dict[str, Any]] = []
