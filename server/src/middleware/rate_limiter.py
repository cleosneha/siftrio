import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from jwt import decode as jwt_decode
from limits import parse, strategies, storage
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded as SlowAPIRateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from src.core.config import settings
from src.mcp.server import mcp_app

logger = logging.getLogger(__name__)


def get_user_id_or_ip(request: Request) -> str:
    token = request.cookies.get("access_token")
    if not token:
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if token:
        try:
            payload = jwt_decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
            uid = payload.get("user_id")
            if uid:
                return str(uid)
        except Exception:
            logger.warning("Rate-limit JWT decode failed", exc_info=True)
    return get_remote_address(request)


_limiter = strategies.FixedWindowRateLimiter(storage.MemoryStorage())

RULES: list[tuple[str, str, str]] = [
    ("/api/assistant/", "19/minute", "user"),
    ("/api/transcripts/", "5/minute", "user"),
    ("/webhooks/fireflies", "30/minute", "ip"),
    ("/webhooks/", "30/minute", "ip"),
]

KEY_FUNCS = {
    "user": get_user_id_or_ip,
    "ip": get_remote_address,
}


async def rate_limit_exceeded_handler(request: Request, exc: SlowAPIRateLimitExceeded) -> JSONResponse:
    return JSONResponse(
        status_code=429,
        content={
            "error": "rate_limit_exceeded",
            "detail": "Too many requests. Try again shortly.",
        },
        headers={"Retry-After": str(int(exc.retry_after))},
    )


def configure_rate_limiting(app: FastAPI) -> None:
    @app.middleware("http")
    async def rate_limit_middleware(request: Request, call_next):
        path = request.url.path
        rule = _match_rule(path)
        if rule is not None:
            limit_str, key_type = rule
            key_func = KEY_FUNCS[key_type]
            limit_item = parse(limit_str)
            limit_key = key_func(request)
            if not _limiter.hit(limit_item, limit_key, path):
                retry_after = int(limit_item.get_expiry())
                headers: dict[str, str] = {"Retry-After": str(retry_after)}
                origin = request.headers.get("origin")
                if origin:
                    headers["Access-Control-Allow-Origin"] = origin
                    headers["Access-Control-Allow-Credentials"] = "true"
                    headers["Access-Control-Allow-Methods"] = "*"
                    headers["Access-Control-Allow-Headers"] = "*"
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "rate_limit_exceeded",
                        "detail": "Too many requests. Try again shortly.",
                    },
                    headers=headers,
                )
        return await call_next(request)

    ip_limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])
    mcp_app.state.limiter = ip_limiter
    mcp_app.add_exception_handler(SlowAPIRateLimitExceeded, rate_limit_exceeded_handler)
    mcp_app.add_middleware(SlowAPIMiddleware)


def _match_rule(path: str) -> tuple[str, str] | None:
    for prefix, limit_str, key_type in RULES:
        if path == prefix or path.startswith(prefix):
            return (limit_str, key_type)
    return None
