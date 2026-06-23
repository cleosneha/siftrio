from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions.base import BaseAPIException
from src.repositories.client_repository import ClientRepository
from src.repositories.workspace_repository import WorkspaceRepository


class ClientService:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = ClientRepository(db)
        self.workspace_repo = WorkspaceRepository(db)

    async def create(
        self, workspace_id: str, name: str, description: str | None = None
    ) -> dict:
        ws_id = UUID(workspace_id)
        workspace = await self.workspace_repo.get_by_id(ws_id)
        if workspace is None:
            raise BaseAPIException(
                message="Workspace not found",
                status_code=404,
            )

        client = await self.repo.create(ws_id, name, description)
        return {
            "id": str(client.id),
            "workspace_id": str(client.workspace_id),
            "name": client.name,
            "description": client.description,
            "project_count": 0,
            "created_at": client.created_at.isoformat() if client.created_at else None,
            "updated_at": client.updated_at.isoformat() if client.updated_at else None,
        }

    async def get_by_id(self, client_id: UUID) -> dict | None:
        client = await self.repo.get_by_id(client_id)
        if client is None:
            return None
        project_count = await self.repo.get_project_count(client_id)
        return {
            "id": str(client.id),
            "workspace_id": str(client.workspace_id),
            "name": client.name,
            "description": client.description,
            "project_count": project_count,
            "created_at": client.created_at.isoformat() if client.created_at else None,
            "updated_at": client.updated_at.isoformat() if client.updated_at else None,
        }

    async def list(self, workspace_id: UUID | None = None) -> list[dict]:
        clients = await self.repo.list(workspace_id)
        result = []
        for c in clients:
            project_count = await self.repo.get_project_count(c.id)
            result.append(
                {
                    "id": str(c.id),
                    "workspace_id": str(c.workspace_id),
                    "name": c.name,
                    "description": c.description,
                    "project_count": project_count,
                    "created_at": c.created_at.isoformat() if c.created_at else None,
                    "updated_at": c.updated_at.isoformat() if c.updated_at else None,
                }
            )
        return result
