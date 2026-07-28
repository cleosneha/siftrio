from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.project_integration import ProjectIntegration
from src.models.project import Project


class ProjectIntegrationRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_project(self, project_id: UUID) -> ProjectIntegration | None:
        result = await self._db.execute(
            select(ProjectIntegration).where(
                ProjectIntegration.project_id == project_id
            )
        )
        return result.scalar_one_or_none()

    async def get_by_project_and_provider(
        self, project_id: UUID, provider: str,
    ) -> ProjectIntegration | None:
        result = await self._db.execute(
            select(ProjectIntegration).where(
                ProjectIntegration.project_id == project_id,
                ProjectIntegration.provider == provider,
            )
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        project_id: UUID,
        provider: str,
        external_project_id: str,
        external_project_key: str | None = None,
        external_project_name: str | None = None,
        config: dict | None = None,
    ) -> ProjectIntegration:
        integration = ProjectIntegration(
            project_id=project_id,
            provider=provider,
            external_project_id=external_project_id,
            external_project_key=external_project_key,
            external_project_name=external_project_name,
            config=config,
        )
        self._db.add(integration)
        await self._db.flush()
        await self._db.refresh(integration)
        return integration

    async def update(
        self,
        integration: ProjectIntegration,
        **kwargs,
    ) -> ProjectIntegration:
        for key, value in kwargs.items():
            if hasattr(integration, key):
                setattr(integration, key, value)
        await self._db.flush()
        await self._db.refresh(integration)
        return integration

    async def delete(self, integration: ProjectIntegration) -> None:
        await self._db.delete(integration)
        await self._db.flush()

    async def list_by_workspace(self, workspace_id: UUID) -> list[ProjectIntegration]:
        result = await self._db.execute(
            select(ProjectIntegration)
            .join(Project, ProjectIntegration.project_id == Project.id)
            .join(Project.client)
            .where(Project.client.has(workspace_id=workspace_id))
        )
        return list(result.scalars().all())
