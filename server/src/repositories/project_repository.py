from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.project import Project


class ProjectRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(
        self,
        client_id: UUID,
        name: str,
        description: str | None = None,
    ) -> Project:
        project = Project(client_id=client_id, name=name, description=description)
        self.db.add(project)
        await self.db.flush()
        await self.db.refresh(project)
        return project

    async def get_by_id(self, project_id: UUID) -> Project | None:
        result = await self.db.execute(
            select(Project).where(Project.id == project_id)
        )
        return result.scalar_one_or_none()

    async def list(self, client_id: UUID | None = None) -> list[Project]:
        query = select(Project)
        if client_id is not None:
            query = query.where(Project.client_id == client_id)
        query = query.order_by(Project.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())
