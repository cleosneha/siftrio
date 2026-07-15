from __future__ import annotations

import logging
from uuid import UUID

from mcp.server.fastmcp import Context, FastMCP
from sqlalchemy.ext.asyncio import AsyncSession

from src.mcp.context import MCPContext
from src.mcp.schemas.common import ToolResult
from src.mcp.tool_helpers import run_tool
from src.repositories.client_repository import ClientRepository
from src.repositories.project_repository import ProjectRepository
from src.schemas.project_schema import ProjectResponse

logger = logging.getLogger(__name__)


async def _list_projects(
    db: AsyncSession,
    auth: MCPContext,
    client_id: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> ToolResult:
    repo = ProjectRepository(db)
    if client_id:
        projects = await repo.list(client_id=UUID(client_id), limit=limit, offset=offset)
    else:
        projects = await repo.list_by_user_id(auth.user_id, limit=limit, offset=offset)

    items = [ProjectResponse.model_validate(p).model_dump() for p in projects]
    return ToolResult(data=items, message=f"Found {len(items)} projects")


async def _get_project(
    db: AsyncSession, auth: MCPContext, project_id: str
) -> ToolResult:
    repo = ProjectRepository(db)
    project = await repo.get_by_id(UUID(project_id))
    if project is None:
        return ToolResult(success=False, message="Project not found")
    return ToolResult(data=ProjectResponse.model_validate(project).model_dump())


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def list_projects(
        ctx: Context,
        client_id: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> str:
        """List projects you have access to, optionally filtered by client.

        Args:
            client_id: Filter by client UUID.
            limit: Maximum number of results (default 50).
            offset: Pagination offset.
        """
        result = await run_tool(
            ctx,
            "list_projects",
            _list_projects,
            client_id=client_id,
            limit=limit,
            offset=offset,
        )
        return result.model_dump_json()

    @mcp.tool()
    async def get_project(ctx: Context, project_id: str) -> str:
        """Get details of a specific project by ID.

        Args:
            project_id: The UUID of the project to retrieve.
        """
        result = await run_tool(
            ctx, "get_project", _get_project, project_id=project_id
        )
        return result.model_dump_json()
