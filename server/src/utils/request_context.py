from __future__ import annotations

from contextvars import ContextVar
from dataclasses import dataclass


@dataclass(frozen=True)
class RequestMeta:
    ip_address: str | None = None
    user_agent: str | None = None


_request_meta: ContextVar[RequestMeta | None] = ContextVar(
    "request_meta", default=None
)


def set_request_meta(meta: RequestMeta | None) -> None:
    _request_meta.set(meta)


def get_request_meta() -> RequestMeta | None:
    return _request_meta.get()
