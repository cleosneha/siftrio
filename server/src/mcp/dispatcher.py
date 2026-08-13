from __future__ import annotations

import inspect
import logging
import time
from typing import Any
from uuid import UUID

from fastapi import HTTPException

from src.core.database import async_session_factory
from src.mcp.context import MCPContext
from src.mcp.schemas.common import ToolResult
from src.mcp.schemas.execution_context import ToolExecutionContext
from src.mcp.workspace_resolver import resolve_workspace
from src.repositories.meeting_repository import MeetingRepository
from src.repositories.resource_repository import ResourceRepository
from src.services.permission_service import (
    require_permission,
    user_has_permission_in_workspaces,
)

logger = logging.getLogger(__name__)

_ENTITY_KEYS = ("workspace_id", "client_id", "project_id", "meeting_id")


def _extract_entity_ids(kwargs: dict[str, Any]) -> dict[str, str | None]:
    return {k: kwargs.pop(k, None) for k in _ENTITY_KEYS if k in kwargs}


def _requires_workspace(kwargs: dict[str, Any]) -> bool:
    return any(kwargs.get(k) for k in _ENTITY_KEYS)


def _filter_kwargs(func: Any, kwargs: dict[str, Any]) -> dict[str, Any]:
    sig = inspect.signature(func)
    accepted = set(sig.parameters.keys())
    return {k: v for k, v in kwargs.items() if k in accepted or "kwargs" in sig.parameters}


def _to_uuid(value: Any) -> UUID:
    return value if isinstance(value, UUID) else UUID(str(value))


async def _resolve_project_from_item(
    db, kwargs: dict[str, Any]
) -> UUID | None:
    """Resolve the project for action_item_id / item_id based tools."""
    if kwargs.get("action_item_id"):
        return await ResourceRepository(db).get_project_id(
            "action_item", _to_uuid(kwargs["action_item_id"])
        )
    if kwargs.get("item_id"):
        item_type = kwargs.get("item_type", "action_item")
        return await ResourceRepository(db).get_project_id(
            item_type, _to_uuid(kwargs["item_id"])
        )
    return None


async def _resolve_target(
    db, boundary_kwargs: dict[str, Any]
) -> tuple[str, UUID] | None:
    """Resolve (level, resource_id) for the permission gate (§3.3 step 3)."""
    if boundary_kwargs.get("project_id"):
        return "project", _to_uuid(boundary_kwargs["project_id"])
    if boundary_kwargs.get("client_id"):
        return "client", _to_uuid(boundary_kwargs["client_id"])
    if boundary_kwargs.get("workspace_id"):
        return "workspace", _to_uuid(boundary_kwargs["workspace_id"])
    if boundary_kwargs.get("meeting_id"):
        meeting = await MeetingRepository(db).get_by_id(
            _to_uuid(boundary_kwargs["meeting_id"])
        )
        if meeting is None:
            return None
        if meeting.project_id:
            return "project", meeting.project_id
        if meeting.client_id:
            return "client", meeting.client_id
        return None
    return None


class MCPDispatcher:
    def __init__(self) -> None:
        self._tools: dict[str, Any] = {}
        self._permissions: dict[str, str] = {}

    def register(self, name: str, func: Any) -> None:
        self._tools[name] = func
        logger.debug("MCPDispatcher registered tool: %s", name)

    def set_permissions(self, permissions: dict[str, str]) -> None:
        self._permissions.update(permissions)

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
        if context.user_id is None:
            return ToolResult(success=False, message="Unauthenticated MCP call")

        user_id = _to_uuid(context.user_id)
        user_workspace_ids = [_to_uuid(w) for w in context.workspace_ids]
        permission = self._permissions.get(tool_name)

        kwargs = dict(kwargs)
        entity_kwargs = _extract_entity_ids(kwargs)

        logger.info(
            "mcp.dispatch tool=%s user=%s workspaces=%d permission=%s",
            tool_name,
            user_id,
            len(user_workspace_ids),
            permission,
        )

        async with async_session_factory() as db:
            t0 = time.perf_counter()
            try:
                boundary_kwargs = dict(entity_kwargs)
                if not _requires_workspace(boundary_kwargs):
                    project_id = await _resolve_project_from_item(db, kwargs)
                    if project_id:
                        boundary_kwargs["project_id"] = str(project_id)

                auth = MCPContext(
                    user_id=user_id,
                    workspace_ids=[str(w) for w in user_workspace_ids],
                )

                resolved = await resolve_workspace(
                    db=db,
                    user_workspace_ids=user_workspace_ids,
                    **boundary_kwargs,
                )

                if resolved is None and _requires_workspace(boundary_kwargs):
                    return ToolResult(
                        success=False,
                        message="Workspace not found or access denied",
                    )

                auth.resolved_workspace = resolved

                target = await _resolve_target(db, boundary_kwargs)
                if permission:
                    if target is not None:
                        level, resource_id = target
                        try:
                            await require_permission(
                                user_id, permission, level, resource_id, db
                            )
                        except HTTPException as e:
                            return ToolResult(
                                success=False,
                                message=f"Access denied: {e.detail}",
                            )
                    else:
                        allowed = await user_has_permission_in_workspaces(
                            user_id, permission, user_workspace_ids, db
                        )
                        if not allowed:
                            return ToolResult(
                                success=False,
                                message="Access denied: insufficient permissions",
                            )

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
