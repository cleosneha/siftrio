from __future__ import annotations

import logging
from typing import TYPE_CHECKING
from uuid import UUID

from mcp.server.fastmcp import Context, FastMCP
from sqlalchemy.ext.asyncio import AsyncSession

from src.mcp.context import MCPContext
from src.mcp.schemas.common import ToolParameterSpec, ToolResult, ToolSpec
from src.repositories.knowledge_repository import KnowledgeRepository
from src.repositories.meeting_chunk_repository import MeetingChunkRepository
from src.repositories.meeting_repository import MeetingRepository
from src.services.knowledge_service import KnowledgeService

if TYPE_CHECKING:
    from src.mcp.dispatcher import MCPDispatcher

logger = logging.getLogger(__name__)


def _service(db: AsyncSession) -> KnowledgeService:
    return KnowledgeService(
        db=db,
        repo=KnowledgeRepository(db),
        meeting_repo=MeetingRepository(db),
        chunk_repo=MeetingChunkRepository(db),
    )


async def _get_action_item(
    db: AsyncSession, auth: MCPContext, action_item_id: str
) -> ToolResult:
    svc = _service(db)
    item = await svc.get_action_item(UUID(action_item_id))
    if item is None:
        return ToolResult(success=False, message="Action item not found")
    return ToolResult(data=item)


async def _update_action_item_status(
    db: AsyncSession, auth: MCPContext, action_item_id: str, status: str,
) -> ToolResult:
    svc = _service(db)
    item = await svc.update_action_item(UUID(action_item_id), {"status": status})
    return ToolResult(data=item, message=f"Action item status updated to '{status}'")


TOOL_SPECS = [
    ToolSpec(
        name="get_action_item",
        description="Get a specific action item by ID, including assignee, due date, and Jira sync status.",
        entity_type="action_item",
        parameters=[
            ToolParameterSpec(name="action_item_id", type="string", description="The UUID of the action item.", required=True),
            ToolParameterSpec(name="workspace_id", type="string", description="Scope to a specific workspace. Auto-resolved from action item if not provided.", required=False),
        ],
    ),
    ToolSpec(
        name="update_action_item_status",
        description="Update the status of an action item.",
        parameters=[
            ToolParameterSpec(name="action_item_id", type="string", description="The UUID of the action item.", required=True),
            ToolParameterSpec(name="status", type="string", description="New status value (e.g., 'completed', 'in_progress', 'pending').", required=True),
            ToolParameterSpec(name="workspace_id", type="string", description="Scope to a specific workspace. Auto-resolved from action item if not provided.", required=False),
        ],
    ),
]


def register(mcp: FastMCP, dispatcher: MCPDispatcher) -> None:
    dispatcher.register("get_action_item", _get_action_item)
    dispatcher.register("update_action_item_status", _update_action_item_status)

    @mcp.tool()
    async def get_action_item(
        ctx: Context, action_item_id: str, workspace_id: str | None = None,
    ) -> str:
        """Get a specific action item by ID, including assignee, due date, and Jira sync status."""
        from src.mcp.dependencies import get_auth_context
        from src.mcp.schemas.execution_context import ToolExecutionContext

        auth = get_auth_context(ctx)
        context = ToolExecutionContext(user_id=auth.user_id, workspace_ids=auth.workspace_ids)
        result = await dispatcher.dispatch(
            "get_action_item", context,
            action_item_id=action_item_id, workspace_id=workspace_id,
        )
        return result.model_dump_json()

    @mcp.tool()
    async def update_action_item_status(
        ctx: Context, action_item_id: str, status: str, workspace_id: str | None = None,
    ) -> str:
        """Update the status of an action item."""
        from src.mcp.dependencies import get_auth_context
        from src.mcp.schemas.execution_context import ToolExecutionContext

        auth = get_auth_context(ctx)
        context = ToolExecutionContext(user_id=auth.user_id, workspace_ids=auth.workspace_ids)
        result = await dispatcher.dispatch(
            "update_action_item_status", context,
            action_item_id=action_item_id, status=status, workspace_id=workspace_id,
        )
        return result.model_dump_json()
