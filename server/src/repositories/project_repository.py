from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.project import Project
from src.utils.tenant_scope import visible_project_exists


class ProjectRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create(
        self,
        client_id: UUID,
        name: str,
        description: str | None = None,
    ) -> Project:
        project = Project(client_id=client_id, name=name, description=description)
        self._db.add(project)
        await self._db.flush()
        await self._db.refresh(project)
        return project

    async def get_by_id(self, project_id: UUID) -> Project | None:
        result = await self._db.execute(
            select(Project).where(Project.id == project_id)
        )
        return result.scalar_one_or_none()

    async def update(self, project_id: UUID, **kwargs) -> Project | None:
        project = await self.get_by_id(project_id)
        if project is None:
            return None
        for key, value in kwargs.items():
            setattr(project, key, value)
        await self._db.flush()
        await self._db.refresh(project)
        return project

    async def list(self, client_id: UUID | None = None, limit: int = 50, offset: int = 0) -> list[Project]:
        query = select(Project)
        if client_id is not None:
            query = query.where(Project.client_id == client_id)
        query = query.order_by(Project.created_at.desc()).limit(limit).offset(offset)
        result = await self._db.execute(query)
        return list(result.scalars().all())

    async def list_by_workspace(self, workspace_id: UUID) -> list[Project]:
        from src.models.client import Client
        query = (
            select(Project)
            .join(Client, Client.id == Project.client_id)
            .where(Client.workspace_id == workspace_id)
        )
        result = await self._db.execute(query)
        return list(result.scalars().all())

    async def list_by_user_id(self, user_id: UUID, client_id: UUID | None = None, limit: int = 50, offset: int = 0) -> list[Project]:
        query = select(Project).where(visible_project_exists(user_id))
        if client_id is not None:
            query = query.where(Project.client_id == client_id)
        query = query.order_by(Project.created_at.desc()).limit(limit).offset(offset)
        result = await self._db.execute(query)
        return list(result.scalars().all())
