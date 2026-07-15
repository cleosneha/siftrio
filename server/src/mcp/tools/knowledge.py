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


async def _list_requirements(
    db: AsyncSession, auth: MCPContext,
    project_id: str | None = None, meeting_id: str | None = None,
    status: str | None = None, limit: int = 50, offset: int = 0,
) -> ToolResult:
    svc = _service(db)
    items = await svc.list_requirements(
        project_id=UUID(project_id) if project_id else None,
        meeting_id=UUID(meeting_id) if meeting_id else None,
        status=status, limit=limit, offset=offset,
    )
    return ToolResult(data=items, message=f"Found {len(items)} requirements")


async def _list_action_items(
    db: AsyncSession, auth: MCPContext,
    project_id: str | None = None, meeting_id: str | None = None,
    status: str | None = None, limit: int = 50, offset: int = 0,
) -> ToolResult:
    svc = _service(db)
    items = await svc.list_action_items(
        project_id=UUID(project_id) if project_id else None,
        meeting_id=UUID(meeting_id) if meeting_id else None,
        status=status, limit=limit, offset=offset,
    )
    return ToolResult(data=items, message=f"Found {len(items)} action items")


async def _list_decisions(
    db: AsyncSession, auth: MCPContext,
    project_id: str | None = None, meeting_id: str | None = None,
    status: str | None = None, limit: int = 50, offset: int = 0,
) -> ToolResult:
    svc = _service(db)
    items = await svc.list_decisions(
        project_id=UUID(project_id) if project_id else None,
        meeting_id=UUID(meeting_id) if meeting_id else None,
        status=status, limit=limit, offset=offset,
    )
    return ToolResult(data=items, message=f"Found {len(items)} decisions")


async def _list_risks(
    db: AsyncSession, auth: MCPContext,
    project_id: str | None = None, meeting_id: str | None = None,
    status: str | None = None, limit: int = 50, offset: int = 0,
) -> ToolResult:
    svc = _service(db)
    items = await svc.list_risks(
        project_id=UUID(project_id) if project_id else None,
        meeting_id=UUID(meeting_id) if meeting_id else None,
        status=status, limit=limit, offset=offset,
    )
    return ToolResult(data=items, message=f"Found {len(items)} risks")


async def _list_questions(
    db: AsyncSession, auth: MCPContext,
    project_id: str | None = None, meeting_id: str | None = None,
    status: str | None = None, limit: int = 50, offset: int = 0,
) -> ToolResult:
    svc = _service(db)
    items = await svc.list_questions(
        project_id=UUID(project_id) if project_id else None,
        meeting_id=UUID(meeting_id) if meeting_id else None,
        status=status, limit=limit, offset=offset,
    )
    return ToolResult(data=items, message=f"Found {len(items)} questions")


async def _get_knowledge_item(
    db: AsyncSession, auth: MCPContext, item_type: str, item_id: str,
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


_KNOWLEDGE_TOOLS = {
    "list_requirements": _list_requirements,
    "list_action_items": _list_action_items,
    "list_decisions": _list_decisions,
    "list_risks": _list_risks,
    "list_questions": _list_questions,
    "get_knowledge_item": _get_knowledge_item,
}

_KNOWLEDGE_PARAMS = [
    ToolParameterSpec(name="workspace_id", type="string", description="Filter by workspace UUID. Auto-resolved if not provided.", required=False),
    ToolParameterSpec(name="project_id", type="string", description="Filter by project UUID.", required=False),
    ToolParameterSpec(name="meeting_id", type="string", description="Filter by meeting UUID.", required=False),
    ToolParameterSpec(name="status", type="string", description="Filter by status (e.g., 'pending', 'approved').", required=False),
    ToolParameterSpec(name="limit", type="integer", description="Maximum results (default 50).", required=False, default=50),
    ToolParameterSpec(name="offset", type="integer", description="Pagination offset.", required=False, default=0),
]

TOOL_SPECS = [
    ToolSpec(name="list_requirements", description="List project requirements, optionally filtered by project, meeting, or status.", parameters=_KNOWLEDGE_PARAMS),
    ToolSpec(name="list_action_items", description="List action items across meetings, optionally filtered by project, meeting, or status.", parameters=_KNOWLEDGE_PARAMS),
    ToolSpec(name="list_decisions", description="List decisions recorded in meetings, optionally filtered by project, meeting, or status.", parameters=_KNOWLEDGE_PARAMS),
    ToolSpec(name="list_risks", description="List risks identified in meetings, optionally filtered by project, meeting, or status.", parameters=_KNOWLEDGE_PARAMS),
    ToolSpec(name="list_questions", description="List open or answered questions from meetings, optionally filtered by project, meeting, or status.", parameters=_KNOWLEDGE_PARAMS),
    ToolSpec(
        name="get_knowledge_item",
        description="Get a specific knowledge item (requirement, action_item, decision, risk, or question) by ID.",
        parameters=[
            ToolParameterSpec(name="item_type", type="string", description="One of 'requirement', 'action_item', 'decision', 'risk', 'question'.", required=True),
            ToolParameterSpec(name="item_id", type="string", description="The UUID of the item to retrieve.", required=True),
            ToolParameterSpec(name="workspace_id", type="string", description="Scope to a specific workspace. Auto-resolved from item if not provided.", required=False),
        ],
    ),
]


def register(mcp: FastMCP, dispatcher: MCPDispatcher) -> None:
    for spec in TOOL_SPECS:
        dispatcher.register(spec.name, _KNOWLEDGE_TOOLS[spec.name])

    @mcp.tool()
    async def list_requirements(
        ctx: Context, workspace_id: str | None = None, project_id: str | None = None,
        meeting_id: str | None = None, status: str | None = None,
        limit: int = 50, offset: int = 0,
    ) -> str:
        """List project requirements, optionally filtered by project, meeting, or status."""
        from src.mcp.dependencies import get_auth_context
        from src.mcp.schemas.execution_context import ToolExecutionContext

        auth = get_auth_context(ctx)
        context = ToolExecutionContext(user_id=auth.user_id, workspace_ids=auth.workspace_ids)
        result = await dispatcher.dispatch(
            "list_requirements", context,
            workspace_id=workspace_id, project_id=project_id, meeting_id=meeting_id,
            status=status, limit=limit, offset=offset,
        )
        return result.model_dump_json()

    @mcp.tool()
    async def list_action_items(
        ctx: Context, workspace_id: str | None = None, project_id: str | None = None,
        meeting_id: str | None = None, status: str | None = None,
        limit: int = 50, offset: int = 0,
    ) -> str:
        """List action items across meetings, optionally filtered by project, meeting, or status."""
        from src.mcp.dependencies import get_auth_context
        from src.mcp.schemas.execution_context import ToolExecutionContext

        auth = get_auth_context(ctx)
        context = ToolExecutionContext(user_id=auth.user_id, workspace_ids=auth.workspace_ids)
        result = await dispatcher.dispatch(
            "list_action_items", context,
            workspace_id=workspace_id, project_id=project_id, meeting_id=meeting_id,
            status=status, limit=limit, offset=offset,
        )
        return result.model_dump_json()

    @mcp.tool()
    async def list_decisions(
        ctx: Context, workspace_id: str | None = None, project_id: str | None = None,
        meeting_id: str | None = None, status: str | None = None,
        limit: int = 50, offset: int = 0,
    ) -> str:
        """List decisions recorded in meetings, optionally filtered by project, meeting, or status."""
        from src.mcp.dependencies import get_auth_context
        from src.mcp.schemas.execution_context import ToolExecutionContext

        auth = get_auth_context(ctx)
        context = ToolExecutionContext(user_id=auth.user_id, workspace_ids=auth.workspace_ids)
        result = await dispatcher.dispatch(
            "list_decisions", context,
            workspace_id=workspace_id, project_id=project_id, meeting_id=meeting_id,
            status=status, limit=limit, offset=offset,
        )
        return result.model_dump_json()

    @mcp.tool()
    async def list_risks(
        ctx: Context, workspace_id: str | None = None, project_id: str | None = None,
        meeting_id: str | None = None, status: str | None = None,
        limit: int = 50, offset: int = 0,
    ) -> str:
        """List risks identified in meetings, optionally filtered by project, meeting, or status."""
        from src.mcp.dependencies import get_auth_context
        from src.mcp.schemas.execution_context import ToolExecutionContext

        auth = get_auth_context(ctx)
        context = ToolExecutionContext(user_id=auth.user_id, workspace_ids=auth.workspace_ids)
        result = await dispatcher.dispatch(
            "list_risks", context,
            workspace_id=workspace_id, project_id=project_id, meeting_id=meeting_id,
            status=status, limit=limit, offset=offset,
        )
        return result.model_dump_json()

    @mcp.tool()
    async def list_questions(
        ctx: Context, workspace_id: str | None = None, project_id: str | None = None,
        meeting_id: str | None = None, status: str | None = None,
        limit: int = 50, offset: int = 0,
    ) -> str:
        """List open or answered questions from meetings, optionally filtered by project, meeting, or status."""
        from src.mcp.dependencies import get_auth_context
        from src.mcp.schemas.execution_context import ToolExecutionContext

        auth = get_auth_context(ctx)
        context = ToolExecutionContext(user_id=auth.user_id, workspace_ids=auth.workspace_ids)
        result = await dispatcher.dispatch(
            "list_questions", context,
            workspace_id=workspace_id, project_id=project_id, meeting_id=meeting_id,
            status=status, limit=limit, offset=offset,
        )
        return result.model_dump_json()

    @mcp.tool()
    async def get_knowledge_item(
        ctx: Context, item_type: str, item_id: str, workspace_id: str | None = None,
    ) -> str:
        """Get a specific knowledge item (requirement, action_item, decision, risk, or question) by ID."""
        from src.mcp.dependencies import get_auth_context
        from src.mcp.schemas.execution_context import ToolExecutionContext

        auth = get_auth_context(ctx)
        context = ToolExecutionContext(user_id=auth.user_id, workspace_ids=auth.workspace_ids)
        result = await dispatcher.dispatch(
            "get_knowledge_item", context,
            item_type=item_type, item_id=item_id, workspace_id=workspace_id,
        )
        return result.model_dump_json()
