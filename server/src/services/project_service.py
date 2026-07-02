from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions.base import BaseAPIException
from src.repositories.client_repository import ClientRepository
from src.repositories.project_repository import ProjectRepository


class ProjectService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = ProjectRepository(db)
        self.client_repo = ClientRepository(db)

    async def create(
        self, client_id: str, name: str, description: str | None = None
    ) -> dict:
        cl_id = UUID(client_id)
        client = await self.client_repo.get_by_id(cl_id)
        if client is None:
            raise BaseAPIException(
                message="Client not found",
                status_code=404,
            )

        project = await self.repo.create(cl_id, name, description)
        await self.db.commit()
        return {
            "id": str(project.id),
            "client_id": str(project.client_id),
            "name": project.name,
            "description": project.description,
            "status": project.status.value if project.status else "active",
            "created_at": project.created_at.isoformat() if project.created_at else None,
            "updated_at": project.updated_at.isoformat() if project.updated_at else None,
        }

    async def get_by_id(self, project_id: UUID) -> dict | None:
        project = await self.repo.get_by_id(project_id)
        if project is None:
            return None
        return {
            "id": str(project.id),
            "client_id": str(project.client_id),
            "name": project.name,
            "description": project.description,
            "status": project.status.value if project.status else "active",
            "created_at": project.created_at.isoformat() if project.created_at else None,
            "updated_at": project.updated_at.isoformat() if project.updated_at else None,
        }

    async def list(self, client_id: UUID | None = None) -> list[dict]:
        projects = await self.repo.list(client_id)
        return [
            {
                "id": str(p.id),
                "client_id": str(p.client_id),
                "name": p.name,
                "description": p.description,
                "status": p.status.value if p.status else "active",
                "created_at": p.created_at.isoformat() if p.created_at else None,
                "updated_at": p.updated_at.isoformat() if p.updated_at else None,
            }
            for p in projects
        ]
