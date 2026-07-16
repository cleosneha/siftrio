from __future__ import annotations

import inspect
import logging
import time
from typing import Any
from uuid import UUID

from src.core.database import async_session_factory
from src.mcp.context import MCPContext
from src.mcp.schemas.common import ToolResult
from src.mcp.schemas.execution_context import ToolExecutionContext
from src.mcp.workspace_resolver import resolve_workspace

logger = logging.getLogger(__name__)

_ENTITY_KEYS = ("workspace_id", "client_id", "project_id", "meeting_id")


def _extract_entity_ids(kwargs: dict[str, Any]) -> dict[str, str | None]:
    return {k: kwargs.pop(k, None) for k in _ENTITY_KEYS if k in kwargs}


def _requires_workspace(tool_name: str, kwargs: dict[str, Any]) -> bool:
    return any(kwargs.get(k) for k in ("workspace_id", "client_id", "project_id", "meeting_id"))


def _filter_kwargs(func: Any, kwargs: dict[str, Any]) -> dict[str, Any]:
    sig = inspect.signature(func)
    accepted = set(sig.parameters.keys())
    return {k: v for k, v in kwargs.items() if k in accepted or "kwargs" in sig.parameters}


class MCPDispatcher:
    def __init__(self) -> None:
        self._tools: dict[str, Any] = {}

    def register(self, name: str, func: Any) -> None:
        self._tools[name] = func
        logger.debug("MCPDispatcher registered tool: %s", name)

    async def dispatch(
        self,
        tool_name: str,
        context: ToolExecutionContext,
        **kwargs: Any,
    ) -> ToolResult:
        func = self._tools.get(tool_name)
        if func is None:
            logger.warning("MCPDispatcher unknown tool: %s", tool_name)
            return ToolResult(success=False, message=f"Unknown tool: {tool_name}")

        entity_kwargs = _extract_entity_ids(kwargs)

        logger.info(
            "mcp.dispatch tool=%s user=%s workspaces=%d",
            tool_name,
            context.user_id,
            len(context.workspace_ids),
        )

        async with async_session_factory() as db:
            t0 = time.perf_counter()
            try:
                auth = MCPContext(
                    user_id=context.user_id,
                    workspace_ids=list(context.workspace_ids),
                )

                resolved = await resolve_workspace(
                    db=db,
                    user_workspace_ids=list(context.workspace_ids),
                    **entity_kwargs,
                )

                if resolved is None and _requires_workspace(tool_name, entity_kwargs):
                    return ToolResult(
                        success=False,
                        message="Workspace not found or access denied",
                    )

                auth.resolved_workspace = resolved

                filtered_kwargs = _filter_kwargs(func, {**entity_kwargs, **kwargs})
                result = await func(db=db, auth=auth, **filtered_kwargs)
                elapsed = (time.perf_counter() - t0) * 1000
                logger.info(
                    "mcp.dispatch.complete tool=%s elapsed=%.1fms",
                    tool_name,
                    elapsed,
                )
                return result
            except Exception as e:
                elapsed = (time.perf_counter() - t0) * 1000
                logger.error(
                    "mcp.dispatch.error tool=%s elapsed=%.1fms error=%s",
                    tool_name,
                    elapsed,
                    str(e),
                )
                raise
