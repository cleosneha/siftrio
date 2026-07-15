from __future__ import annotations

import logging
from typing import TYPE_CHECKING
from uuid import UUID

from mcp.server.fastmcp import Context, FastMCP
from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions.base import BaseAPIException
from src.mcp.context import MCPContext
from src.mcp.schemas.common import ToolParameterSpec, ToolResult, ToolSpec
from src.repositories.project_jira_repository import ProjectJiraRepository
from src.repositories.workspace_jira_repository import WorkspaceJiraRepository

if TYPE_CHECKING:
    from src.mcp.dispatcher import MCPDispatcher

logger = logging.getLogger(__name__)


async def _get_jira_integration_status(
    db: AsyncSession, auth: MCPContext
) -> ToolResult:
    if auth.resolved_workspace is None:
        return ToolResult(
            success=False,
            message="Could not determine workspace. Please provide workspace_id.",
        )

    ws_id = auth.resolved_workspace.workspace_id
    repo = WorkspaceJiraRepository(db)
    integration = await repo.get_by_workspace(ws_id)
    if integration is None:
        return ToolResult(
            data={"connected": False, "workspace_name": auth.resolved_workspace.workspace_name},
            message="Jira is not connected for this workspace",
        )
    return ToolResult(
        data={
            "connected": True,
            "workspace_name": auth.resolved_workspace.workspace_name,
            "cloud_name": integration.cloud_name,
            "site_url": integration.site_url,
            "connected_at": (
                integration.connected_at.isoformat()
                if integration.connected_at
                else None
            ),
        },
        message="Jira is connected",
    )


async def _list_jira_projects(
    db: AsyncSession, auth: MCPContext, project_id: str
) -> ToolResult:
    from src.services.project_jira_service import ProjectJiraService

    proj_id = UUID(project_id)
    svc = ProjectJiraService(db)
    try:
        projects = await svc.get_available_projects(proj_id)
        return ToolResult(data=projects, message=f"Found {len(projects)} Jira projects")
    except BaseAPIException as e:
        return ToolResult(success=False, message=e.message)


async def _get_project_jira_mapping(
    db: AsyncSession, auth: MCPContext, project_id: str
) -> ToolResult:
    proj_id = UUID(project_id)
    repo = ProjectJiraRepository(db)
    mapping = await repo.get_by_project(proj_id)
    if mapping is None:
        return ToolResult(
            data={"mapped": False},
            message="No Jira project mapped to this Siftrio project",
        )
    return ToolResult(
        data={
            "mapped": True,
            "jira_project_id": mapping.jira_project_id,
            "jira_project_key": mapping.jira_project_key,
            "jira_project_name": mapping.jira_project_name,
            "jira_project_type": mapping.jira_project_type,
        },
        message="Jira project mapping found",
    )


async def _get_jira_issue(
    db: AsyncSession, auth: MCPContext, project_id: str, action_item_id: str
) -> ToolResult:
    from src.services.action_item_jira_service import ActionItemJiraService

    proj_id = UUID(project_id)
    svc = ActionItemJiraService(db)
    try:
        issue = await svc.get_issue_details(proj_id, UUID(action_item_id))
        return ToolResult(data=issue.model_dump(), message="Jira issue retrieved")
    except BaseAPIException as e:
        return ToolResult(success=False, message=e.message)


JIRA_TOOLS = {
    "get_jira_integration_status": _get_jira_integration_status,
    "list_jira_projects": _list_jira_projects,
    "get_project_jira_mapping": _get_project_jira_mapping,
    "get_jira_issue": _get_jira_issue,
}

TOOL_SPECS = [
    ToolSpec(
        name="get_jira_integration_status",
        description="Check if Jira is connected for a workspace and get connection details.",
        parameters=[
            ToolParameterSpec(name="workspace_id", type="string", description="The UUID of the workspace to check. Auto-resolved if not provided.", required=False),
        ],
    ),
    ToolSpec(
        name="list_jira_projects",
        description="List available Jira projects that can be linked to a Siftrio project.",
        parameters=[
            ToolParameterSpec(name="project_id", type="string", description="The UUID of the Siftrio project.", required=True),
            ToolParameterSpec(name="workspace_id", type="string", description="Scope to a specific workspace. Auto-resolved from project if not provided.", required=False),
        ],
    ),
    ToolSpec(
        name="get_project_jira_mapping",
        description="Get the Jira project mapping for a Siftrio project, if one exists.",
        parameters=[
            ToolParameterSpec(name="project_id", type="string", description="The UUID of the Siftrio project.", required=True),
            ToolParameterSpec(name="workspace_id", type="string", description="Scope to a specific workspace. Auto-resolved from project if not provided.", required=False),
        ],
    ),
    ToolSpec(
        name="get_jira_issue",
        description="Get details of a Jira issue linked to an action item.",
        parameters=[
            ToolParameterSpec(name="project_id", type="string", description="The UUID of the Siftrio project.", required=True),
            ToolParameterSpec(name="action_item_id", type="string", description="The UUID of the action item with a linked Jira issue.", required=True),
            ToolParameterSpec(name="workspace_id", type="string", description="Scope to a specific workspace. Auto-resolved from project if not provided.", required=False),
        ],
    ),
]


def register(mcp: FastMCP, dispatcher: MCPDispatcher) -> None:
    for spec in TOOL_SPECS:
        dispatcher.register(spec.name, JIRA_TOOLS[spec.name])

    @mcp.tool()
    async def get_jira_integration_status(
        ctx: Context, workspace_id: str | None = None,
    ) -> str:
        """Check if Jira is connected for a workspace and get connection details."""
        from src.mcp.dependencies import get_auth_context
        from src.mcp.schemas.execution_context import ToolExecutionContext

        auth = get_auth_context(ctx)
        context = ToolExecutionContext(user_id=auth.user_id, workspace_ids=auth.workspace_ids)
        result = await dispatcher.dispatch("get_jira_integration_status", context, workspace_id=workspace_id)
        return result.model_dump_json()

    @mcp.tool()
    async def list_jira_projects(
        ctx: Context, project_id: str, workspace_id: str | None = None,
    ) -> str:
        """List available Jira projects that can be linked to a Siftrio project."""
        from src.mcp.dependencies import get_auth_context
        from src.mcp.schemas.execution_context import ToolExecutionContext

        auth = get_auth_context(ctx)
        context = ToolExecutionContext(user_id=auth.user_id, workspace_ids=auth.workspace_ids)
        result = await dispatcher.dispatch(
            "list_jira_projects", context,
            project_id=project_id, workspace_id=workspace_id,
        )
        return result.model_dump_json()

    @mcp.tool()
    async def get_project_jira_mapping(
        ctx: Context, project_id: str, workspace_id: str | None = None,
    ) -> str:
        """Get the Jira project mapping for a Siftrio project, if one exists."""
        from src.mcp.dependencies import get_auth_context
        from src.mcp.schemas.execution_context import ToolExecutionContext

        auth = get_auth_context(ctx)
        context = ToolExecutionContext(user_id=auth.user_id, workspace_ids=auth.workspace_ids)
        result = await dispatcher.dispatch(
            "get_project_jira_mapping", context,
            project_id=project_id, workspace_id=workspace_id,
        )
        return result.model_dump_json()

    @mcp.tool()
    async def get_jira_issue(
        ctx: Context, project_id: str, action_item_id: str, workspace_id: str | None = None,
    ) -> str:
        """Get details of a Jira issue linked to an action item."""
        from src.mcp.dependencies import get_auth_context
        from src.mcp.schemas.execution_context import ToolExecutionContext

        auth = get_auth_context(ctx)
        context = ToolExecutionContext(user_id=auth.user_id, workspace_ids=auth.workspace_ids)
        result = await dispatcher.dispatch(
            "get_jira_issue", context,
            project_id=project_id, action_item_id=action_item_id, workspace_id=workspace_id,
        )
        return result.model_dump_json()
