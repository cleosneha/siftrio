from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.workspace_repository import WorkspaceRepository


class WorkspaceService:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = WorkspaceRepository(db)

    async def create(self, name: str, description: str | None = None) -> dict:
        workspace = await self.repo.create(name, description)
        return {
            "id": str(workspace.id),
            "name": workspace.name,
            "description": workspace.description,
            "created_at": workspace.created_at.isoformat() if workspace.created_at else None,
            "updated_at": workspace.updated_at.isoformat() if workspace.updated_at else None,
        }

    async def get_by_id(self, workspace_id: UUID) -> dict | None:
        workspace = await self.repo.get_by_id(workspace_id)
        if workspace is None:
            return None
        return {
            "id": str(workspace.id),
            "name": workspace.name,
            "description": workspace.description,
            "created_at": workspace.created_at.isoformat() if workspace.created_at else None,
            "updated_at": workspace.updated_at.isoformat() if workspace.updated_at else None,
        }

    async def list(self) -> list[dict]:
        workspaces = await self.repo.list()
        return [
            {
                "id": str(w.id),
                "name": w.name,
                "description": w.description,
                "created_at": w.created_at.isoformat() if w.created_at else None,
                "updated_at": w.updated_at.isoformat() if w.updated_at else None,
            }
            for w in workspaces
        ]
