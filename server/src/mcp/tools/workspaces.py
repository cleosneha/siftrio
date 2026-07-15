from __future__ import annotations

import logging
from uuid import UUID

from mcp.server.fastmcp import Context, FastMCP
from sqlalchemy.ext.asyncio import AsyncSession

from src.mcp.context import MCPContext
from src.mcp.schemas.common import ToolResult
from src.mcp.tool_helpers import run_tool
from src.repositories.workspace_repository import WorkspaceRepository
from src.schemas.workspace_schema import WorkspaceResponse

logger = logging.getLogger(__name__)


async def _list_workspaces(
    db: AsyncSession, auth: MCPContext
) -> ToolResult:
    repo = WorkspaceRepository(db)
    workspaces = await repo.list_by_user_id(auth.user_id)
    items = [WorkspaceResponse.model_validate(w).model_dump() for w in workspaces]
    return ToolResult(data=items, message=f"Found {len(items)} workspaces")


async def _get_workspace(
    db: AsyncSession, auth: MCPContext, workspace_id: str
) -> ToolResult:
    repo = WorkspaceRepository(db)
    workspace = await repo.get_by_id(UUID(workspace_id))
    if workspace is None:
        return ToolResult(success=False, message="Workspace not found")
    if str(workspace.id) not in auth.workspace_ids:
        return ToolResult(success=False, message="Access denied to this workspace")
    return ToolResult(data=WorkspaceResponse.model_validate(workspace).model_dump())


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def list_workspaces(ctx: Context) -> str:
        """List all workspaces you have access to."""
        result = await run_tool(ctx, "list_workspaces", _list_workspaces)
        return result.model_dump_json()

    @mcp.tool()
    async def get_workspace(ctx: Context, workspace_id: str) -> str:
        """Get details of a specific workspace by ID.

        Args:
            workspace_id: The UUID of the workspace to retrieve.
        """
        result = await run_tool(
            ctx, "get_workspace", _get_workspace, workspace_id=workspace_id
        )
        return result.model_dump_json()
