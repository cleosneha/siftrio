from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.workspace import Workspace


class WorkspaceRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create(
        self,
        name: str,
        description: str | None = None,
        created_by: UUID | None = None,
    ) -> Workspace:
        workspace = Workspace(name=name, description=description, created_by=created_by)
        self._db.add(workspace)
        await self._db.flush()
        await self._db.refresh(workspace)
        return workspace

    async def get_by_id(self, workspace_id: UUID) -> Workspace | None:
        result = await self._db.execute(
            select(Workspace).where(Workspace.id == workspace_id)
        )
        return result.scalar_one_or_none()

    async def list(self, limit: int = 50, offset: int = 0) -> list[Workspace]:
        result = await self._db.execute(
            select(Workspace).order_by(Workspace.created_at.desc()).limit(limit).offset(offset)
        )
        return list(result.scalars().all())
