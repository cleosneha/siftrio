from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.workspace import Workspace


class WorkspaceRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, name: str, description: str | None = None) -> Workspace:
        workspace = Workspace(name=name, description=description)
        self.db.add(workspace)
        await self.db.commit()
        await self.db.refresh(workspace)
        return workspace

    async def get_by_id(self, workspace_id: UUID) -> Workspace | None:
        result = await self.db.execute(
            select(Workspace).where(Workspace.id == workspace_id)
        )
        return result.scalar_one_or_none()

    async def list(self) -> list[Workspace]:
        result = await self.db.execute(
            select(Workspace).order_by(Workspace.created_at.desc())
        )
        return list(result.scalars().all())
