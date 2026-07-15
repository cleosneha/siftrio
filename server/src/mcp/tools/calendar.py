from __future__ import annotations

import logging
from uuid import UUID

from mcp.server.fastmcp import Context, FastMCP
from sqlalchemy.ext.asyncio import AsyncSession

from src.mcp.context import MCPContext
from src.mcp.schemas.common import AmbiguousMatch, AmbiguousResult, ToolResult
from src.mcp.tool_helpers import run_tool
from src.repositories.client_repository import ClientRepository
from src.repositories.meeting_repository import MeetingRepository
from src.schemas.meeting_schema import MeetingResponse

logger = logging.getLogger(__name__)


async def _get_upcoming_meetings(
    db: AsyncSession,
    auth: MCPContext,
    client_id: str | None = None,
    project_id: str | None = None,
    limit: int = 10,
) -> ToolResult | AmbiguousResult:
    repo = MeetingRepository(db)

    if auth.resolved_workspace is not None:
        ws_id = auth.resolved_workspace.workspace_id
        client_repo = ClientRepository(db)
        clients = await client_repo.list_with_project_counts(ws_id)
        meetings = []
        for client, _ in clients:
            if client_id and str(client.id) != client_id:
                continue
            client_meetings = await repo.list_by_client(client.id, limit=limit)
            meetings.extend(client_meetings)
    elif project_id:
        meetings = await repo.list_by_project(UUID(project_id), limit=limit)
    elif client_id:
        meetings = await repo.list_by_client(UUID(client_id), limit=limit)
    else:
        meetings_by_ws: dict[str, list] = {}
        for ws_id in auth.workspace_ids:
            client_repo = ClientRepository(db)
            clients = await client_repo.list_with_project_counts(UUID(ws_id))
            for client, _ in clients:
                client_meetings = await repo.list_by_client(client.id, limit=limit)
                if client_meetings:
                    meetings_by_ws.setdefault(ws_id, []).extend(client_meetings)

        if len(meetings_by_ws) > 1:
            matches = []
            for ws_id, ws_meetings in meetings_by_ws.items():
                for m in ws_meetings[:3]:
                    matches.append(AmbiguousMatch(
                        workspace_id=ws_id,
                        workspace_name="",
                        resource_type="meeting",
                        resource_name=m.title,
                    ))
            return AmbiguousResult(matches=matches)

        meetings = []
        for ws_meetings in meetings_by_ws.values():
            meetings.extend(ws_meetings)

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
        workspace_id: str | None = None,
        client_id: str | None = None,
        project_id: str | None = None,
        limit: int = 10,
    ) -> str:
        """Get upcoming meetings, prioritizing those with Google Meet links.

        Useful for finding meetings with video conference links.

        Args:
            workspace_id: Filter by workspace UUID. Auto-resolved if not provided.
            client_id: Filter by client UUID.
            project_id: Filter by project UUID.
            limit: Maximum results (default 10).
        """
        result = await run_tool(
            ctx, "get_upcoming_meetings", _get_upcoming_meetings,
            workspace_id=workspace_id,
            client_id=client_id, project_id=project_id, limit=limit,
        )
        return result.model_dump_json()
