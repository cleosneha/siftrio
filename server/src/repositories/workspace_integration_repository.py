from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.workspace_integration import WorkspaceIntegration


class WorkspaceIntegrationRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_workspace(self, workspace_id: UUID) -> WorkspaceIntegration | None:
        result = await self._db.execute(
            select(WorkspaceIntegration).where(
                WorkspaceIntegration.workspace_id == workspace_id
            )
        )
        return result.scalar_one_or_none()

    async def get_by_workspace_and_provider(
        self, workspace_id: UUID, provider: str,
    ) -> WorkspaceIntegration | None:
        result = await self._db.execute(
            select(WorkspaceIntegration).where(
                WorkspaceIntegration.workspace_id == workspace_id,
                WorkspaceIntegration.provider == provider,
            )
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        workspace_id: UUID,
        provider: str,
        access_token: str,
        refresh_token: str | None = None,
        token_expires_at=None,
        config: dict | None = None,
        connected_by: UUID | None = None,
    ) -> WorkspaceIntegration:
        integration = WorkspaceIntegration(
            workspace_id=workspace_id,
            provider=provider,
            access_token=access_token,
            refresh_token=refresh_token,
            token_expires_at=token_expires_at,
            config=config,
            connected_by=connected_by,
        )
        self._db.add(integration)
        await self._db.flush()
        await self._db.refresh(integration)
        return integration

    async def update(
        self,
        integration: WorkspaceIntegration,
        **kwargs,
    ) -> WorkspaceIntegration:
        for key, value in kwargs.items():
            if hasattr(integration, key):
                setattr(integration, key, value)
        await self._db.flush()
        await self._db.refresh(integration)
        return integration

    async def delete(self, integration: WorkspaceIntegration) -> None:
        await self._db.delete(integration)
        await self._db.flush()
