from __future__ import annotations

import logging
from uuid import UUID

from mcp.server.fastmcp import Context, FastMCP
from sqlalchemy.ext.asyncio import AsyncSession

from src.mcp.context import MCPContext
from src.mcp.schemas.common import ToolResult
from src.mcp.tool_helpers import run_tool
from src.repositories.knowledge_repository import KnowledgeRepository
from src.repositories.meeting_chunk_repository import MeetingChunkRepository
from src.repositories.meeting_repository import MeetingRepository
from src.services.knowledge_service import KnowledgeService

logger = logging.getLogger(__name__)


def _service(db: AsyncSession) -> KnowledgeService:
    return KnowledgeService(
        db=db,
        repo=KnowledgeRepository(db),
        meeting_repo=MeetingRepository(db),
        chunk_repo=MeetingChunkRepository(db),
    )


async def _update_action_item_status(
    db: AsyncSession,
    auth: MCPContext,
    action_item_id: str,
    status: str,
) -> ToolResult:
    svc = _service(db)
    item = await svc.update_action_item(
        UUID(action_item_id), {"status": status}
    )
    return ToolResult(data=item, message=f"Action item status updated to '{status}'")


async def _get_action_item(
    db: AsyncSession, auth: MCPContext, action_item_id: str
) -> ToolResult:
    svc = _service(db)
    item = await svc.get_action_item(UUID(action_item_id))
    if item is None:
        return ToolResult(success=False, message="Action item not found")
    return ToolResult(data=item)


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def get_action_item(ctx: Context, action_item_id: str) -> str:
        """Get a specific action item by ID, including assignee, due date, and Jira sync status.

        Args:
            action_item_id: The UUID of the action item.
        """
        result = await run_tool(
            ctx, "get_action_item", _get_action_item,
            action_item_id=action_item_id,
        )
        return result.model_dump_json()

    @mcp.tool()
    async def update_action_item_status(
        ctx: Context, action_item_id: str, status: str
    ) -> str:
        """Update the status of an action item.

        Args:
            action_item_id: The UUID of the action item.
            status: New status value (e.g., 'completed', 'in_progress', 'pending').
        """
        result = await run_tool(
            ctx, "update_action_item_status", _update_action_item_status,
            action_item_id=action_item_id, status=status,
        )
        return result.model_dump_json()
