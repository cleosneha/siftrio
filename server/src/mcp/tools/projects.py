from __future__ import annotations

import logging
from typing import TYPE_CHECKING
from uuid import UUID

from mcp.server.fastmcp import Context, FastMCP
from sqlalchemy.ext.asyncio import AsyncSession

from src.mcp.context import MCPContext
from src.mcp.schemas.common import (
    AmbiguousMatch,
    AmbiguousResult,
    ToolParameterSpec,
    ToolResult,
    ToolSpec,
)
from src.repositories.client_repository import ClientRepository
from src.repositories.project_repository import ProjectRepository
from src.schemas.project_schema import ProjectResponse

if TYPE_CHECKING:
    from src.mcp.dispatcher import MCPDispatcher

logger = logging.getLogger(__name__)

TOOL_SPECS = [
    ToolSpec(
        name="list_projects",
        description="List projects you have access to, optionally filtered by client.",
        parameters=[
            ToolParameterSpec(name="workspace_id", type="string", description="Filter by workspace UUID. Auto-resolved if not provided.", required=False),
            ToolParameterSpec(name="client_id", type="string", description="Filter by client UUID.", required=False),
            ToolParameterSpec(name="limit", type="integer", description="Maximum number of results (default 50).", required=False, default=50),
            ToolParameterSpec(name="offset", type="integer", description="Pagination offset.", required=False, default=0),
        ],
    ),
    ToolSpec(
        name="get_project",
        description="Get details of a specific project by ID.",
        entity_type="project",
        parameters=[
            ToolParameterSpec(name="project_id", type="string", description="The UUID of the project to retrieve.", required=True),
            ToolParameterSpec(name="workspace_id", type="string", description="Scope to a specific workspace. Auto-resolved from project if not provided.", required=False),
        ],
    ),
]


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


def register(mcp: FastMCP, dispatcher: MCPDispatcher) -> None:
    for spec in TOOL_SPECS:
        dispatcher.register(spec.name, {"list_projects": _list_projects, "get_project": _get_project}[spec.name])

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
        from src.mcp.dependencies import get_auth_context
        from src.mcp.schemas.execution_context import ToolExecutionContext

        auth = get_auth_context(ctx)
        context = ToolExecutionContext(user_id=auth.user_id, workspace_ids=auth.workspace_ids)
        result = await dispatcher.dispatch(
            "list_projects", context,
            workspace_id=workspace_id, client_id=client_id,
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
        from src.mcp.dependencies import get_auth_context
        from src.mcp.schemas.execution_context import ToolExecutionContext

        auth = get_auth_context(ctx)
        context = ToolExecutionContext(user_id=auth.user_id, workspace_ids=auth.workspace_ids)
        result = await dispatcher.dispatch(
            "get_project", context,
            project_id=project_id, workspace_id=workspace_id,
        )
        return result.model_dump_json()
