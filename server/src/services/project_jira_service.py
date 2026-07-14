from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions.base import BaseAPIException
from src.integrations.atlassian.client import JiraClient
from src.repositories.project_jira_repository import ProjectJiraRepository
from src.repositories.project_repository import ProjectRepository
from src.schemas.jira_schema import (
    ConnectJiraProjectRequest,
    CreateJiraProjectRequest,
    JiraProjectItem,
    ProjectJiraResponse,
)
from src.services.workspace_jira_service import WorkspaceJiraService


class ProjectJiraService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = ProjectJiraRepository(db)
        self.project_repo = ProjectRepository(db)
        self.workspace_jira_service = WorkspaceJiraService(db)

    async def get_mapping(self, project_id: UUID) -> dict | None:
        mapping = await self.repo.get_by_project(project_id)
        if mapping is None:
            return None
        return ProjectJiraResponse.model_validate(mapping).model_dump()

    async def get_available_projects(self, project_id: UUID) -> list[dict]:
        project = await self.project_repo.get_by_id(project_id)
        if project is None:
            raise BaseAPIException(message="Project not found", status_code=404)

        from src.models.client import Client
        client = await self.db.get(Client, project.client_id)
        if client is None:
            raise BaseAPIException(message="Client not found", status_code=404)

        access_token = await self.workspace_jira_service.get_valid_access_token(client.workspace_id)
        integration = await self.workspace_jira_service.repo.get_by_workspace(client.workspace_id)
        if integration is None or not integration.cloud_id:
            raise BaseAPIException(
                message="Workspace not connected to Jira",
                status_code=400,
            )

        client = JiraClient(integration.cloud_id, access_token)
        projects = await client.get_projects()
        return [
            JiraProjectItem(
                id=p["id"],
                key=p["key"],
                name=p.get("name", ""),
                projectTypeKey=p.get("projectTypeKey"),
                style=p.get("style"),
            ).model_dump()
            for p in projects
        ]

    async def connect_existing(
        self,
        project_id: UUID,
        body: ConnectJiraProjectRequest,
    ) -> dict:
        project = await self.project_repo.get_by_id(project_id)
        if project is None:
            raise BaseAPIException(message="Project not found", status_code=404)

        existing = await self.repo.get_by_project(project_id)
        if existing is not None:
            raise BaseAPIException(
                message="Project already has a Jira integration. Disconnect first.",
                status_code=400,
            )

        mapping = await self.repo.create(
            project_id=project_id,
            jira_project_id=body.jira_project_id,
            jira_project_key=body.jira_project_key,
            jira_project_name=body.jira_project_name,
            jira_project_type=body.jira_project_type,
        )
        await self.db.commit()
        return ProjectJiraResponse.model_validate(mapping).model_dump()

    async def create_and_connect(
        self,
        project_id: UUID,
        body: CreateJiraProjectRequest,
    ) -> dict:
        project = await self.project_repo.get_by_id(project_id)
        if project is None:
            raise BaseAPIException(message="Project not found", status_code=404)

        existing = await self.repo.get_by_project(project_id)
        if existing is not None:
            raise BaseAPIException(
                message="Project already has a Jira integration. Disconnect first.",
                status_code=400,
            )

        from src.models.client import Client
        client = await self.db.get(Client, project.client_id)
        if client is None:
            raise BaseAPIException(message="Client not found", status_code=404)

        access_token = await self.workspace_jira_service.get_valid_access_token(client.workspace_id)
        integration = await self.workspace_jira_service.repo.get_by_workspace(client.workspace_id)
        if integration is None:
            raise BaseAPIException(
                message="Workspace not connected to Jira",
                status_code=400,
            )

        client = JiraClient(integration.cloud_id or "", access_token)

        user = await client.get_current_user()
        lead_account_id = user.get("accountId") if user else None

        created = await client.create_project(
            key=body.key,
            name=body.name,
            project_type_key=body.project_type_key,
            template_key=body.template_key,
            lead_account_id=lead_account_id,
        )
        if created is None:
            raise BaseAPIException(
                message="Failed to create Jira project. Check permissions and try again.",
                status_code=400,
            )

        try:
            mapping = await self.repo.create(
                project_id=project_id,
                jira_project_id=created["id"],
                jira_project_key=created["key"],
                jira_project_name=created.get("name", body.name),
                jira_project_type=created.get("projectTypeKey", body.project_type_key),
            )
        except Exception:
            await self.db.rollback()
            raise BaseAPIException(
                message="Failed to store project mapping. Jira project was created but could not be linked.",
                status_code=500,
            )

        await self.db.commit()
        return ProjectJiraResponse.model_validate(mapping).model_dump()

    async def disconnect(self, project_id: UUID) -> None:
        mapping = await self.repo.get_by_project(project_id)
        if mapping is None:
            raise BaseAPIException(
                message="Project has no Jira integration",
                status_code=400,
            )

        await self.repo.delete(mapping)
        await self.db.commit()
