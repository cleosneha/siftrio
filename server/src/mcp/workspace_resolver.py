from __future__ import annotations

import logging
from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.client import Client
from src.models.project import Project
from src.models.meeting import Meeting
from src.repositories.workspace_repository import WorkspaceRepository

logger = logging.getLogger(__name__)


@dataclass
class ResolvedWorkspace:
    workspace_id: UUID
    workspace_name: str


async def _ws_for_client(
    db: AsyncSession, client_id: UUID
) -> UUID | None:
    result = await db.execute(
        select(Client.workspace_id).where(Client.id == client_id)
    )
    row = result.first()
    return row[0] if row else None


async def _ws_for_project(
    db: AsyncSession, project_id: UUID
) -> UUID | None:
    result = await db.execute(
        select(Client.workspace_id)
        .join(Project, Project.client_id == Client.id)
        .where(Project.id == project_id)
    )
    row = result.first()
    return row[0] if row else None


async def _ws_for_meeting(
    db: AsyncSession, meeting_id: UUID
) -> UUID | None:
    result = await db.execute(
        select(Client.workspace_id)
        .join(Meeting, Meeting.client_id == Client.id)
        .where(Meeting.id == meeting_id)
    )
    row = result.first()
    return row[0] if row else None


async def resolve_workspace(
    db: AsyncSession,
    user_workspace_ids: list[UUID],
    workspace_id: str | None = None,
    client_id: str | None = None,
    project_id: str | None = None,
    meeting_id: str | None = None,
) -> ResolvedWorkspace | None:
    if workspace_id is not None:
        ws_uuid = UUID(workspace_id)
        if ws_uuid not in user_workspace_ids:
            logger.warning(
                "Workspace access denied: user workspaces=%s requested=%s",
                user_workspace_ids,
                ws_uuid,
            )
            return None
        ws_repo = WorkspaceRepository(db)
        workspace = await ws_repo.get_by_id(ws_uuid)
        if workspace is None:
            return None
        return ResolvedWorkspace(
            workspace_id=ws_uuid,
            workspace_name=workspace.name,
        )

    entity_ws: UUID | None = None
    if client_id is not None:
        entity_ws = await _ws_for_client(db, UUID(client_id))
    elif project_id is not None:
        entity_ws = await _ws_for_project(db, UUID(project_id))
    elif meeting_id is not None:
        entity_ws = await _ws_for_meeting(db, UUID(meeting_id))

    if entity_ws is None:
        return None

    if entity_ws not in user_workspace_ids:
        logger.warning(
            "Entity workspace not in user workspaces: entity_ws=%s user_workspaces=%s",
            entity_ws,
            user_workspace_ids,
        )
        return None

    ws_repo = WorkspaceRepository(db)
    workspace = await ws_repo.get_by_id(entity_ws)
    return ResolvedWorkspace(
        workspace_id=entity_ws,
        workspace_name=workspace.name if workspace else "Unknown",
    )
