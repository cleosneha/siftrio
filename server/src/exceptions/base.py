from typing import Any


class BaseAPIException(Exception):
    status_code: int = 500
    message: str = "Internal server error"
    errors: list[dict[str, Any]] = []

    def __init__(
        self,
        message: str | None = None,
        errors: list[dict[str, Any]] | None = None,
        status_code: int | None = None,
    ) -> None:
        if message is not None:
            self.message = message
        if errors is not None:
            self.errors = errors
        if status_code is not None:
            self.status_code = status_code
        super().__init__(self.message)
