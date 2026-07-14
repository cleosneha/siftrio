from __future__ import annotations

from asyncio.log import logger
from uuid import UUID

from sqlalchemy import and_, exists, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.client import Client
from src.models.project import Project


class ClientRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create(
        self, workspace_id: UUID, name: str, description: str | None = None
    ) -> Client:
        logger.debug(f"Creating client in workspace {workspace_id} with name '{name}'")
        client = Client(workspace_id=workspace_id, name=name, description=description)
        self._db.add(client)
        await self._db.flush()
        await self._db.refresh(client)
        return client

    async def get_by_id(self, client_id: UUID) -> Client | None:
        result = await self._db.execute(
            select(Client).where(Client.id == client_id)
        )
        return result.scalar_one_or_none()

    async def list_with_project_counts(
        self, workspace_id: UUID | None = None, limit: int = 50, offset: int = 0
    ) -> list[tuple[Client, int]]:
        subq = (
            select(func.count(Project.id))
            .where(Project.client_id == Client.id)
            .correlate(Client)
            .scalar_subquery()
        )
        query = select(Client, subq.label("project_count"))
        if workspace_id is not None:
            query = query.where(Client.workspace_id == workspace_id)
        query = query.order_by(Client.created_at.desc()).limit(limit).offset(offset)
        result = await self._db.execute(query)
        return [(client, count) for client, count in result.all()]

    async def list_with_project_counts_by_user_id(
        self, user_id: UUID, workspace_id: UUID | None = None, limit: int = 50, offset: int = 0
    ) -> list[tuple[Client, int]]:
        from src.models.client_member import ClientMember
        from src.models.project_member import ProjectMember
        subq = (
            select(func.count(Project.id))
            .where(Project.client_id == Client.id)
            .correlate(Client)
            .scalar_subquery()
        )
        client_member_exists = exists().where(
            and_(
                ClientMember.client_id == Client.id,
                ClientMember.user_id == user_id,
            )
        )
        project_member_exists = exists().where(
            and_(
                ProjectMember.user_id == user_id,
                Project.id == ProjectMember.project_id,
                Project.client_id == Client.id,
            )
        )
        query = select(Client, subq.label("project_count")).where(
            client_member_exists | project_member_exists
        )
        if workspace_id is not None:
            query = query.where(Client.workspace_id == workspace_id)
        query = query.order_by(Client.created_at.desc()).limit(limit).offset(offset)
        result = await self._db.execute(query)
        return [(client, count) for client, count in result.all()]

    async def get_project_count(self, client_id: UUID) -> int:
        result = await self._db.execute(
            select(func.count(Project.id)).where(Project.client_id == client_id)
        )
        return result.scalar() or 0
