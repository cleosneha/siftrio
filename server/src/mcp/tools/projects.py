from __future__ import annotations

import logging
from uuid import UUID

from mcp.server.fastmcp import Context, FastMCP
from sqlalchemy.ext.asyncio import AsyncSession

from src.mcp.context import MCPContext
from src.mcp.schemas.common import AmbiguousMatch, AmbiguousResult, ToolResult
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
) -> ToolResult | AmbiguousResult:
    repo = ProjectRepository(db)

    if auth.resolved_workspace is not None:
        ws_id = auth.resolved_workspace.workspace_id
        client_repo = ClientRepository(db)
        clients = await client_repo.list_with_project_counts(ws_id)
        projects = []
        for client, _ in clients:
            if client_id and str(client.id) != client_id:
                continue
            client_projects = await repo.list(client_id=client.id, limit=limit, offset=offset)
            projects.extend(client_projects)
        projects = projects[:limit]
    elif client_id:
        projects = await repo.list(client_id=UUID(client_id), limit=limit, offset=offset)
    else:
        projects_by_ws: dict[str, list] = {}
        for ws_id in auth.workspace_ids:
            client_repo = ClientRepository(db)
            clients = await client_repo.list_with_project_counts(UUID(ws_id))
            for client, _ in clients:
                client_projects = await repo.list(client_id=client.id, limit=limit, offset=offset)
                if client_projects:
                    projects_by_ws.setdefault(ws_id, []).extend(client_projects)

        if len(projects_by_ws) > 1:
            matches = []
            for ws_id, ws_projects in projects_by_ws.items():
                for p in ws_projects[:3]:
                    matches.append(AmbiguousMatch(
                        workspace_id=ws_id,
                        workspace_name="",
                        resource_type="project",
                        resource_name=p.name,
                    ))
            return AmbiguousResult(matches=matches)

        projects = []
        for ws_projects in projects_by_ws.values():
            projects.extend(ws_projects)
        projects = projects[:limit]

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
        workspace_id: str | None = None,
        client_id: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> str:
        """List projects you have access to, optionally filtered by client.

        Args:
            workspace_id: Filter by workspace UUID. Auto-resolved if not provided.
            client_id: Filter by client UUID.
            limit: Maximum number of results (default 50).
            offset: Pagination offset.
        """
        result = await run_tool(
            ctx, "list_projects", _list_projects,
            workspace_id=workspace_id,
            client_id=client_id,
            limit=limit, offset=offset,
        )
        return result.model_dump_json()

    @mcp.tool()
    async def get_project(
        ctx: Context,
        project_id: str,
        workspace_id: str | None = None,
    ) -> str:
        """Get details of a specific project by ID.

        Args:
            project_id: The UUID of the project to retrieve.
            workspace_id: Scope to a specific workspace. Auto-resolved from project if not provided.
        """
        result = await run_tool(
            ctx, "get_project", _get_project,
            workspace_id=workspace_id,
            project_id=project_id,
        )
        return result.model_dump_json()
