import logging
import time
from collections.abc import Callable
from functools import wraps
from typing import Any

logger = logging.getLogger("mcp.tools")


def log_tool_execution(
    tool_name: str,
    args: dict[str, Any],
    duration_ms: float,
    success: bool,
    error: str | None = None,
) -> None:
    log_data = {
        "tool": tool_name,
        "duration_ms": round(duration_ms, 2),
        "success": success,
    }
    if error:
        log_data["error"] = error
    logger.info("mcp.tool_exec %s", log_data)


def tool_timer(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        start = time.monotonic()
        tool_name = func.__name__
        success = True
        error_msg = None
        try:
            result = await func(*args, **kwargs)
            return result
        except Exception as e:
            success = False
            error_msg = str(e)
            raise
        finally:
            duration_ms = (time.monotonic() - start) * 1000
            log_tool_execution(tool_name, {}, duration_ms, success, error_msg)

    return wrapper
