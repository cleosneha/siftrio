from __future__ import annotations

import logging
from typing import TYPE_CHECKING
from uuid import UUID

from mcp.server.fastmcp import Context, FastMCP
from sqlalchemy.ext.asyncio import AsyncSession

from src.mcp.context import MCPContext
from src.mcp.schemas.common import ToolParameterSpec, ToolResult, ToolSpec
from src.repositories.workspace_repository import WorkspaceRepository
from src.schemas.workspace_schema import WorkspaceResponse

if TYPE_CHECKING:
    from src.mcp.dispatcher import MCPDispatcher

logger = logging.getLogger(__name__)

TOOL_SPECS = [
    ToolSpec(
        name="list_workspaces",
        description="List all workspaces you have access to.",
        parameters=[],
    ),
    ToolSpec(
        name="get_workspace",
        description="Get details of a specific workspace by ID.",
        entity_type="workspace",
        parameters=[
            ToolParameterSpec(name="workspace_id", type="string", description="The UUID of the workspace to retrieve", required=True),
        ],
    ),
]


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
    if str(workspace.id) not in [str(wid) for wid in auth.workspace_ids]:
        return ToolResult(success=False, message="Access denied to this workspace")
    return ToolResult(data=WorkspaceResponse.model_validate(workspace).model_dump())


def register(mcp: FastMCP, dispatcher: MCPDispatcher) -> None:
    for spec in TOOL_SPECS:
        dispatcher.register(spec.name, {"list_workspaces": _list_workspaces, "get_workspace": _get_workspace}[spec.name])

    @mcp.tool()
    async def list_workspaces(ctx: Context) -> str:
        """List all workspaces you have access to."""
        from src.mcp.dependencies import get_auth_context
        from src.mcp.schemas.execution_context import ToolExecutionContext

        auth = get_auth_context(ctx)
        context = ToolExecutionContext(user_id=auth.user_id, workspace_ids=auth.workspace_ids)
        result = await dispatcher.dispatch("list_workspaces", context)
        return result.model_dump_json()

    @mcp.tool()
    async def get_workspace(ctx: Context, workspace_id: str) -> str:
        """Get details of a specific workspace by ID.

        Args:
            workspace_id: The UUID of the workspace to retrieve.
        """
        from src.mcp.dependencies import get_auth_context
        from src.mcp.schemas.execution_context import ToolExecutionContext

        auth = get_auth_context(ctx)
        context = ToolExecutionContext(user_id=auth.user_id, workspace_ids=auth.workspace_ids)
        result = await dispatcher.dispatch("get_workspace", context, workspace_id=workspace_id)
        return result.model_dump_json()
