from __future__ import annotations

import logging
from uuid import UUID

from mcp.server.fastmcp import Context, FastMCP
from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions.base import BaseAPIException
from src.mcp.context import MCPContext
from src.mcp.schemas.common import ToolResult
from src.mcp.tool_helpers import run_tool
from src.repositories.project_jira_repository import ProjectJiraRepository
from src.repositories.workspace_jira_repository import WorkspaceJiraRepository

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


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def get_jira_integration_status(
        ctx: Context,
        workspace_id: str | None = None,
    ) -> str:
        """Check if Jira is connected for a workspace and get connection details.

        Args:
            workspace_id: The UUID of the workspace to check. Auto-resolved if not provided.
        """
        result = await run_tool(
            ctx, "get_jira_integration_status", _get_jira_integration_status,
            workspace_id=workspace_id,
        )
        return result.model_dump_json()

    @mcp.tool()
    async def list_jira_projects(
        ctx: Context,
        project_id: str,
        workspace_id: str | None = None,
    ) -> str:
        """List available Jira projects that can be linked to a Siftrio project.

        Args:
            project_id: The UUID of the Siftrio project.
            workspace_id: Scope to a specific workspace. Auto-resolved from project if not provided.
        """
        result = await run_tool(
            ctx, "list_jira_projects", _list_jira_projects,
            workspace_id=workspace_id,
            project_id=project_id,
        )
        return result.model_dump_json()

    @mcp.tool()
    async def get_project_jira_mapping(
        ctx: Context,
        project_id: str,
        workspace_id: str | None = None,
    ) -> str:
        """Get the Jira project mapping for a Siftrio project, if one exists.

        Args:
            project_id: The UUID of the Siftrio project.
            workspace_id: Scope to a specific workspace. Auto-resolved from project if not provided.
        """
        result = await run_tool(
            ctx, "get_project_jira_mapping", _get_project_jira_mapping,
            workspace_id=workspace_id,
            project_id=project_id,
        )
        return result.model_dump_json()

    @mcp.tool()
    async def get_jira_issue(
        ctx: Context,
        project_id: str,
        action_item_id: str,
        workspace_id: str | None = None,
    ) -> str:
        """Get details of a Jira issue linked to an action item.

        Args:
            project_id: The UUID of the Siftrio project.
            action_item_id: The UUID of the action item with a linked Jira issue.
            workspace_id: Scope to a specific workspace. Auto-resolved from project if not provided.
        """
        result = await run_tool(
            ctx, "get_jira_issue", _get_jira_issue,
            workspace_id=workspace_id,
            project_id=project_id, action_item_id=action_item_id,
        )
        return result.model_dump_json()
