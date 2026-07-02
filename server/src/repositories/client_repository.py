from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.client import Client
from src.models.project import Project


class ClientRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(
        self, workspace_id: UUID, name: str, description: str | None = None
    ) -> Client:
        client = Client(workspace_id=workspace_id, name=name, description=description)
        self.db.add(client)
        await self.db.flush()
        await self.db.refresh(client)
        return client

    async def get_by_id(self, client_id: UUID) -> Client | None:
        result = await self.db.execute(
            select(Client).where(Client.id == client_id)
        )
        return result.scalar_one_or_none()

    async def list(self, workspace_id: UUID | None = None) -> list[Client]:
        query = select(Client)
        if workspace_id is not None:
            query = query.where(Client.workspace_id == workspace_id)
        query = query.order_by(Client.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_project_count(self, client_id: UUID) -> int:
        result = await self.db.execute(
            select(func.count(Project.id)).where(Project.client_id == client_id)
        )
        return result.scalar() or 0
