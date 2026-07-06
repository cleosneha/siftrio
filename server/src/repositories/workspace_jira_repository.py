from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.workspace_jira import WorkspaceJira


class WorkspaceJiraRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_workspace(self, workspace_id: UUID) -> WorkspaceJira | None:
        result = await self._db.execute(
            select(WorkspaceJira).where(WorkspaceJira.workspace_id == workspace_id)
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        workspace_id: UUID,
        access_token: str,
        refresh_token: str | None = None,
        token_expires_at: object = None,
        cloud_id: str | None = None,
        cloud_name: str | None = None,
        site_url: str | None = None,
        connected_by: UUID | None = None,
    ) -> WorkspaceJira:
        integration = WorkspaceJira(
            workspace_id=workspace_id,
            provider="jira",
            access_token=access_token,
            refresh_token=refresh_token,
            token_expires_at=token_expires_at,
            cloud_id=cloud_id,
            cloud_name=cloud_name,
            site_url=site_url,
            connected_by=connected_by,
        )
        self._db.add(integration)
        await self._db.flush()
        await self._db.refresh(integration)
        return integration

    async def update(
        self,
        integration: WorkspaceJira,
        **kwargs: object,
    ) -> WorkspaceJira:
        for key, value in kwargs.items():
            setattr(integration, key, value)
        await self._db.flush()
        await self._db.refresh(integration)
        return integration

    async def delete(self, integration: WorkspaceJira) -> None:
        await self._db.delete(integration)
        await self._db.flush()

    async def list_by_workspace_ids(self, workspace_ids: list[UUID]) -> list[WorkspaceJira]:
        result = await self._db.execute(
            select(WorkspaceJira).where(WorkspaceJira.workspace_id.in_(workspace_ids))
        )
        return list(result.scalars().all())
