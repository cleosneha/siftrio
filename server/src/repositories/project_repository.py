from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.project import Project


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

    async def list(self, client_id: UUID | None = None, limit: int = 50, offset: int = 0) -> list[Project]:
        query = select(Project)
        if client_id is not None:
            query = query.where(Project.client_id == client_id)
        query = query.order_by(Project.created_at.desc()).limit(limit).offset(offset)
        result = await self._db.execute(query)
        return list(result.scalars().all())
