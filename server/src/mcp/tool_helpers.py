from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

from mcp.server.fastmcp import Context
from sqlalchemy.ext.asyncio import AsyncSession

from src.mcp.context import MCPContext
from src.mcp.dependencies import get_auth_context
from src.mcp.schemas.common import AmbiguousResult, ToolResult

logger = logging.getLogger(__name__)


async def run_tool(
    ctx: Context,  # type: ignore[type-arg]
    tool_name: str,
    func: Any,
    workspace_id: str | None = None,
    client_id: str | None = None,
    project_id: str | None = None,
    meeting_id: str | None = None,
    **kwargs: Any,
) -> ToolResult | AmbiguousResult:
    from src.core.database import async_session_factory
    from src.mcp.workspace_resolver import resolve_workspace

    auth = get_auth_context(ctx)

    logger.info(
        "mcp.tool.start tool=%s user=%s workspaces=%d",
        tool_name,
        auth.user_id,
        len(auth.workspace_ids),
    )

    async with async_session_factory() as db:
        try:
            resolved = await resolve_workspace(
                db=db,
                user_workspace_ids=[UUID(wid) for wid in auth.workspace_ids],
                workspace_id=workspace_id,
                client_id=client_id,
                project_id=project_id,
                meeting_id=meeting_id,
            )

            if resolved is None and (workspace_id or client_id or project_id or meeting_id):
                return ToolResult(
                    success=False,
                    message="Workspace not found or access denied",
                )

            auth.resolved_workspace = resolved

            result = await func(db=db, auth=auth, **kwargs)
            logger.info("mcp.tool.complete tool=%s", tool_name)
            return result
        except Exception as e:
            logger.error("mcp.tool.error tool=%s error=%s", tool_name, str(e))
            raise
