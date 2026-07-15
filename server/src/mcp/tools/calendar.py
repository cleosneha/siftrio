from __future__ import annotations

import logging
from uuid import UUID

from mcp.server.fastmcp import Context, FastMCP
from sqlalchemy.ext.asyncio import AsyncSession

from src.mcp.context import MCPContext
from src.mcp.schemas.common import ToolResult
from src.mcp.tool_helpers import run_tool
from src.repositories.meeting_repository import MeetingRepository
from src.schemas.meeting_schema import MeetingResponse

logger = logging.getLogger(__name__)


async def _get_upcoming_meetings(
    db: AsyncSession,
    auth: MCPContext,
    client_id: str | None = None,
    project_id: str | None = None,
    limit: int = 10,
) -> ToolResult:
    repo = MeetingRepository(db)

    if project_id:
        meetings = await repo.list_by_project(UUID(project_id), limit=limit)
    elif client_id:
        meetings = await repo.list_by_client(UUID(client_id), limit=limit)
    else:
        meetings = []
        for ws_id in auth.workspace_ids:
            from src.repositories.client_repository import ClientRepository

            client_repo = ClientRepository(db)
            clients = await client_repo.list_with_project_counts(UUID(ws_id))
            for client, _ in clients:
                client_meetings = await repo.list_by_client(client.id, limit=limit)
                meetings.extend(client_meetings)
        meetings = sorted(meetings, key=lambda m: m.created_at or "", reverse=True)[
            :limit
        ]

    items = []
    for m in meetings:
        data = MeetingResponse.model_validate(m).model_dump()
        if m.google_meet_url:
            items.append(data)

    if not items:
        items = [
            MeetingResponse.model_validate(m).model_dump()
            for m in meetings[:limit]
        ]

    return ToolResult(data=items, message=f"Found {len(items)} meetings")


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def get_upcoming_meetings(
        ctx: Context,
        client_id: str | None = None,
        project_id: str | None = None,
        limit: int = 10,
    ) -> str:
        """Get upcoming meetings, prioritizing those with Google Meet links.

        Useful for finding meetings with video conference links.

        Args:
            client_id: Filter by client UUID.
            project_id: Filter by project UUID.
            limit: Maximum results (default 10).
        """
        result = await run_tool(
            ctx, "get_upcoming_meetings", _get_upcoming_meetings,
            client_id=client_id, project_id=project_id, limit=limit,
        )
        return result.model_dump_json()
