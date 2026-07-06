from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.project_jira import ProjectJira


class ProjectJiraRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_project(self, project_id: UUID) -> ProjectJira | None:
        result = await self._db.execute(
            select(ProjectJira).where(ProjectJira.project_id == project_id)
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        project_id: UUID,
        jira_project_id: str,
        jira_project_key: str,
        jira_project_name: str,
        jira_project_type: str | None = None,
    ) -> ProjectJira:
        mapping = ProjectJira(
            project_id=project_id,
            provider="jira",
            jira_project_id=jira_project_id,
            jira_project_key=jira_project_key,
            jira_project_name=jira_project_name,
            jira_project_type=jira_project_type,
        )
        self._db.add(mapping)
        await self._db.flush()
        await self._db.refresh(mapping)
        return mapping

    async def delete(self, mapping: ProjectJira) -> None:
        await self._db.delete(mapping)
        await self._db.flush()

    async def list_by_workspace(self, workspace_id: UUID) -> list[ProjectJira]:
        from src.models.client import Client
        from src.models.project import Project
        result = await self._db.execute(
            select(ProjectJira)
            .join(Project, ProjectJira.project_id == Project.id)
            .join(Client, Project.client_id == Client.id)
            .where(Client.workspace_id == workspace_id)
        )
        return list(result.scalars().all())
