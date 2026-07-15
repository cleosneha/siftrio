from __future__ import annotations

import logging
from uuid import UUID

from mcp.server.fastmcp import Context, FastMCP
from sqlalchemy.ext.asyncio import AsyncSession

from src.mcp.context import MCPContext
from src.mcp.schemas.common import ToolResult
from src.mcp.tool_helpers import run_tool
from src.repositories.client_repository import ClientRepository
from src.repositories.meeting_repository import MeetingRepository
from src.repositories.project_repository import ProjectRepository
from src.schemas.meeting_schema import MeetingResponse
from src.services.meeting_integration_service import MeetingIntegrationService
from src.services.meeting_service import MeetingService

logger = logging.getLogger(__name__)


async def _list_meetings(
    db: AsyncSession,
    auth: MCPContext,
    client_id: str | None = None,
    project_id: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> ToolResult:
    repo = MeetingRepository(db)
    if project_id:
        meetings = await repo.list_by_project(UUID(project_id), limit=limit, offset=offset)
    elif client_id:
        meetings = await repo.list_by_client(UUID(client_id), limit=limit, offset=offset)
    else:
        meetings = []
        for ws_id in auth.workspace_ids:
            client_repo = ClientRepository(db)
            clients = await client_repo.list_with_project_counts(UUID(ws_id))
            for client, _ in clients:
                client_meetings = await repo.list_by_client(client.id, limit=limit, offset=offset)
                meetings.extend(client_meetings)
        meetings = sorted(meetings, key=lambda m: m.created_at or "", reverse=True)[:limit]

    items = [MeetingResponse.model_validate(m).model_dump() for m in meetings]
    return ToolResult(data=items, message=f"Found {len(items)} meetings")


async def _get_meeting(
    db: AsyncSession, auth: MCPContext, meeting_id: str
) -> ToolResult:
    repo = MeetingRepository(db)
    meeting = await repo.get_by_id(UUID(meeting_id))
    if meeting is None:
        return ToolResult(success=False, message="Meeting not found")
    return ToolResult(data=MeetingResponse.model_validate(meeting).model_dump())


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def list_meetings(
        ctx: Context,
        client_id: str | None = None,
        project_id: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> str:
        """List meetings, optionally filtered by client or project.

        Args:
            client_id: Filter by client UUID.
            project_id: Filter by project UUID.
            limit: Maximum number of results (default 50).
            offset: Pagination offset.
        """
        result = await run_tool(
            ctx,
            "list_meetings",
            _list_meetings,
            client_id=client_id,
            project_id=project_id,
            limit=limit,
            offset=offset,
        )
        return result.model_dump_json()

    @mcp.tool()
    async def get_meeting(ctx: Context, meeting_id: str) -> str:
        """Get details of a specific meeting by ID, including transcript if available.

        Args:
            meeting_id: The UUID of the meeting to retrieve.
        """
        result = await run_tool(
            ctx, "get_meeting", _get_meeting, meeting_id=meeting_id
        )
        return result.model_dump_json()
