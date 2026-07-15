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
from src.schemas.knowledge_schema import (
    ActionItemResponse,
    DecisionResponse,
    QuestionResponse,
    RequirementResponse,
    RiskResponse,
)
from src.services.knowledge_service import KnowledgeService

logger = logging.getLogger(__name__)


def _service(db: AsyncSession) -> KnowledgeService:
    return KnowledgeService(
        db=db,
        repo=KnowledgeRepository(db),
        meeting_repo=MeetingRepository(db),
        chunk_repo=MeetingChunkRepository(db),
    )


async def _list_requirements(
    db: AsyncSession,
    auth: MCPContext,
    project_id: str | None = None,
    meeting_id: str | None = None,
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> ToolResult:
    svc = _service(db)
    items = await svc.list_requirements(
        project_id=UUID(project_id) if project_id else None,
        meeting_id=UUID(meeting_id) if meeting_id else None,
        status=status,
        limit=limit,
        offset=offset,
    )
    return ToolResult(data=items, message=f"Found {len(items)} requirements")


async def _list_action_items(
    db: AsyncSession,
    auth: MCPContext,
    project_id: str | None = None,
    meeting_id: str | None = None,
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> ToolResult:
    svc = _service(db)
    items = await svc.list_action_items(
        project_id=UUID(project_id) if project_id else None,
        meeting_id=UUID(meeting_id) if meeting_id else None,
        status=status,
        limit=limit,
        offset=offset,
    )
    return ToolResult(data=items, message=f"Found {len(items)} action items")


async def _list_decisions(
    db: AsyncSession,
    auth: MCPContext,
    project_id: str | None = None,
    meeting_id: str | None = None,
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> ToolResult:
    svc = _service(db)
    items = await svc.list_decisions(
        project_id=UUID(project_id) if project_id else None,
        meeting_id=UUID(meeting_id) if meeting_id else None,
        status=status,
        limit=limit,
        offset=offset,
    )
    return ToolResult(data=items, message=f"Found {len(items)} decisions")


async def _list_risks(
    db: AsyncSession,
    auth: MCPContext,
    project_id: str | None = None,
    meeting_id: str | None = None,
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> ToolResult:
    svc = _service(db)
    items = await svc.list_risks(
        project_id=UUID(project_id) if project_id else None,
        meeting_id=UUID(meeting_id) if meeting_id else None,
        status=status,
        limit=limit,
        offset=offset,
    )
    return ToolResult(data=items, message=f"Found {len(items)} risks")


async def _list_questions(
    db: AsyncSession,
    auth: MCPContext,
    project_id: str | None = None,
    meeting_id: str | None = None,
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> ToolResult:
    svc = _service(db)
    items = await svc.list_questions(
        project_id=UUID(project_id) if project_id else None,
        meeting_id=UUID(meeting_id) if meeting_id else None,
        status=status,
        limit=limit,
        offset=offset,
    )
    return ToolResult(data=items, message=f"Found {len(items)} questions")


async def _get_knowledge_item(
    db: AsyncSession,
    auth: MCPContext,
    item_type: str,
    item_id: str,
) -> ToolResult:
    svc = _service(db)
    getter = {
        "requirement": svc.get_requirement,
        "action_item": svc.get_action_item,
        "decision": svc.get_decision,
        "risk": svc.get_risk,
        "question": svc.get_question,
    }.get(item_type)
    if getter is None:
        return ToolResult(success=False, message=f"Unknown item type: {item_type}")
    item = await getter(UUID(item_id))
    if item is None:
        return ToolResult(success=False, message=f"{item_type.capitalize()} not found")
    return ToolResult(data=item)


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def list_requirements(
        ctx: Context,
        workspace_id: str | None = None,
        project_id: str | None = None,
        meeting_id: str | None = None,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> str:
        """List project requirements, optionally filtered by project, meeting, or status.

        Args:
            workspace_id: Filter by workspace UUID. Auto-resolved if not provided.
            project_id: Filter by project UUID.
            meeting_id: Filter by meeting UUID.
            status: Filter by status (e.g., 'pending', 'approved').
            limit: Maximum results (default 50).
            offset: Pagination offset.
        """
        result = await run_tool(
            ctx, "list_requirements", _list_requirements,
            workspace_id=workspace_id,
            project_id=project_id, meeting_id=meeting_id,
            status=status, limit=limit, offset=offset,
        )
        return result.model_dump_json()

    @mcp.tool()
    async def list_action_items(
        ctx: Context,
        workspace_id: str | None = None,
        project_id: str | None = None,
        meeting_id: str | None = None,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> str:
        """List action items across meetings, optionally filtered by project, meeting, or status.

        Args:
            workspace_id: Filter by workspace UUID. Auto-resolved if not provided.
            project_id: Filter by project UUID.
            meeting_id: Filter by meeting UUID.
            status: Filter by status (e.g., 'pending', 'completed').
            limit: Maximum results (default 50).
            offset: Pagination offset.
        """
        result = await run_tool(
            ctx, "list_action_items", _list_action_items,
            workspace_id=workspace_id,
            project_id=project_id, meeting_id=meeting_id,
            status=status, limit=limit, offset=offset,
        )
        return result.model_dump_json()

    @mcp.tool()
    async def list_decisions(
        ctx: Context,
        workspace_id: str | None = None,
        project_id: str | None = None,
        meeting_id: str | None = None,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> str:
        """List decisions recorded in meetings, optionally filtered by project, meeting, or status.

        Args:
            workspace_id: Filter by workspace UUID. Auto-resolved if not provided.
            project_id: Filter by project UUID.
            meeting_id: Filter by meeting UUID.
            status: Filter by status.
            limit: Maximum results (default 50).
            offset: Pagination offset.
        """
        result = await run_tool(
            ctx, "list_decisions", _list_decisions,
            workspace_id=workspace_id,
            project_id=project_id, meeting_id=meeting_id,
            status=status, limit=limit, offset=offset,
        )
        return result.model_dump_json()

    @mcp.tool()
    async def list_risks(
        ctx: Context,
        workspace_id: str | None = None,
        project_id: str | None = None,
        meeting_id: str | None = None,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> str:
        """List risks identified in meetings, optionally filtered by project, meeting, or status.

        Args:
            workspace_id: Filter by workspace UUID. Auto-resolved if not provided.
            project_id: Filter by project UUID.
            meeting_id: Filter by meeting UUID.
            status: Filter by status (e.g., 'open', 'mitigated').
            limit: Maximum results (default 50).
            offset: Pagination offset.
        """
        result = await run_tool(
            ctx, "list_risks", _list_risks,
            workspace_id=workspace_id,
            project_id=project_id, meeting_id=meeting_id,
            status=status, limit=limit, offset=offset,
        )
        return result.model_dump_json()

    @mcp.tool()
    async def list_questions(
        ctx: Context,
        workspace_id: str | None = None,
        project_id: str | None = None,
        meeting_id: str | None = None,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> str:
        """List open or answered questions from meetings, optionally filtered by project, meeting, or status.

        Args:
            workspace_id: Filter by workspace UUID. Auto-resolved if not provided.
            project_id: Filter by project UUID.
            meeting_id: Filter by meeting UUID.
            status: Filter by status (e.g., 'pending', 'answered').
            limit: Maximum results (default 50).
            offset: Pagination offset.
        """
        result = await run_tool(
            ctx, "list_questions", _list_questions,
            workspace_id=workspace_id,
            project_id=project_id, meeting_id=meeting_id,
            status=status, limit=limit, offset=offset,
        )
        return result.model_dump_json()

    @mcp.tool()
    async def get_knowledge_item(
        ctx: Context,
        item_type: str,
        item_id: str,
        workspace_id: str | None = None,
    ) -> str:
        """Get a specific knowledge item (requirement, action_item, decision, risk, or question) by ID.

        Args:
            item_type: One of 'requirement', 'action_item', 'decision', 'risk', 'question'.
            item_id: The UUID of the item to retrieve.
            workspace_id: Scope to a specific workspace. Auto-resolved from item if not provided.
        """
        result = await run_tool(
            ctx, "get_knowledge_item", _get_knowledge_item,
            workspace_id=workspace_id,
            item_type=item_type, item_id=item_id,
        )
        return result.model_dump_json()
