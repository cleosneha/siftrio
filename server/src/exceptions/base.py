from pydantic import BaseModel, Field


class _ErrorData(BaseModel):
    message: str = "Internal server error"
    errors: list[dict] = Field(default_factory=list)
    status_code: int = 500


class BaseAPIException(Exception):
    def __init__(
        self,
        message: str | None = None,
        errors: list[dict] | None = None,
        status_code: int | None = None,
    ) -> None:
        kwargs = {}
        if message is not None:
            kwargs["message"] = message
        if errors is not None:
            kwargs["errors"] = errors
        if status_code is not None:
            kwargs["status_code"] = status_code
        self._data = _ErrorData(**kwargs)
        super().__init__(self._data.message)

    @property
    def message(self) -> str:
        return self._data.message

    @property
    def errors(self) -> list[dict]:
        return self._data.errors

    @property
    def status_code(self) -> int:
        return self._data.status_code
