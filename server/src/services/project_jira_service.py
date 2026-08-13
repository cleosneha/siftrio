from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions.base import BaseAPIException
from src.integrations.atlassian.client import JiraClient
from src.repositories.project_integration_repository import ProjectIntegrationRepository
from src.repositories.project_repository import ProjectRepository
from src.repositories.resource_repository import ResourceRepository
from src.schemas.jira_schema import (
    ConnectJiraProjectRequest,
    CreateJiraProjectRequest,
    JiraProjectItem,
    ProjectJiraResponse,
)
from src.services.audit_service import AuditService
from src.services.workspace_jira_service import WorkspaceJiraService


class ProjectJiraService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = ProjectIntegrationRepository(db)
        self.project_repo = ProjectRepository(db)
        self.workspace_jira_service = WorkspaceJiraService(db)

    async def get_mapping(self, project_id: UUID) -> dict | None:
        mapping = await self.repo.get_by_project_and_provider(project_id, "jira")
        if mapping is None:
            return None
        return self._to_response(mapping)

    async def get_available_projects(self, project_id: UUID) -> list[dict]:
        project = await self.project_repo.get_by_id(project_id)
        if project is None:
            raise BaseAPIException(message="Project not found", status_code=404)

        from src.models.client import Client
        client = await self.db.get(Client, project.client_id)
        if client is None:
            raise BaseAPIException(message="Client not found", status_code=404)

        access_token = await self.workspace_jira_service.get_valid_access_token(client.workspace_id)
        cloud_id = await self.workspace_jira_service.get_cloud_id(client.workspace_id)

        jira_client = JiraClient(cloud_id, access_token)
        projects = await jira_client.get_projects()
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
        actor_user_id: UUID,
    ) -> dict:
        project = await self.project_repo.get_by_id(project_id)
        if project is None:
            raise BaseAPIException(message="Project not found", status_code=404)

        existing = await self.repo.get_by_project_and_provider(project_id, "jira")
        if existing is not None:
            raise BaseAPIException(
                message="Project already has a Jira integration. Disconnect first.",
                status_code=400,
            )

        config = {}
        if body.jira_project_type:
            config["jira_project_type"] = body.jira_project_type

        mapping = await self.repo.create(
            project_id=project_id,
            provider="jira",
            external_project_id=body.jira_project_id,
            external_project_key=body.jira_project_key,
            external_project_name=body.jira_project_name,
            config=config if config else None,
        )
        ws_id = await ResourceRepository(self.db).get_workspace_id("project", project_id)
        if ws_id is not None:
            AuditService(self.db).record(
                workspace_id=ws_id,
                action="integration.connected",
                resource_type="project",
                resource_id=project_id,
                actor_user_id=actor_user_id,
                new_value={
                    "provider": "jira",
                    "jira_project_id": body.jira_project_id,
                    "jira_project_key": body.jira_project_key,
                    "jira_project_name": body.jira_project_name,
                },
            )
        await self.db.commit()
        return self._to_response(mapping)

    async def create_and_connect(
        self,
        project_id: UUID,
        body: CreateJiraProjectRequest,
        actor_user_id: UUID,
    ) -> dict:
        project = await self.project_repo.get_by_id(project_id)
        if project is None:
            raise BaseAPIException(message="Project not found", status_code=404)

        existing = await self.repo.get_by_project_and_provider(project_id, "jira")
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
        cloud_id = await self.workspace_jira_service.get_cloud_id(client.workspace_id)

        jira_client = JiraClient(cloud_id, access_token)

        user = await jira_client.get_current_user()
        lead_account_id = user.get("accountId") if user else None

        created = await jira_client.create_project(
            key=body.key,
            name=body.name,
            project_type_key=body.project_type_key,
            template_key=body.template_key,
            lead_account_id=lead_account_id,
        )

        config = {}
        if created.get("projectTypeKey"):
            config["jira_project_type"] = created.get("projectTypeKey")

        try:
            mapping = await self.repo.create(
                project_id=project_id,
                provider="jira",
                external_project_id=created["id"],
                external_project_key=created["key"],
                external_project_name=created.get("name", body.name),
                config=config if config else None,
            )
        except Exception:
            await self.db.rollback()
            raise BaseAPIException(
                message="Failed to store project mapping. Jira project was created but could not be linked.",
                status_code=500,
            )

        ws_id = await ResourceRepository(self.db).get_workspace_id("project", project_id)
        if ws_id is not None:
            AuditService(self.db).record(
                workspace_id=ws_id,
                action="integration.connected",
                resource_type="project",
                resource_id=project_id,
                actor_user_id=actor_user_id,
                new_value={
                    "provider": "jira",
                    "jira_project_id": created["id"],
                    "jira_project_key": created["key"],
                    "jira_project_name": created.get("name", body.name),
                },
            )
        await self.db.commit()
        return self._to_response(mapping)

    async def disconnect(self, project_id: UUID, actor_user_id: UUID) -> None:
        mapping = await self.repo.get_by_project_and_provider(project_id, "jira")
        if mapping is None:
            raise BaseAPIException(
                message="Project has no Jira integration",
                status_code=400,
            )

        await self.repo.delete(mapping)
        ws_id = await ResourceRepository(self.db).get_workspace_id("project", project_id)
        if ws_id is not None:
            AuditService(self.db).record(
                workspace_id=ws_id,
                action="integration.disconnected",
                resource_type="project",
                resource_id=project_id,
                actor_user_id=actor_user_id,
                new_value={"provider": "jira"},
            )
        await self.db.commit()

    def _to_response(self, integration) -> dict:
        config = integration.config or {}
        return ProjectJiraResponse(
            id=integration.id,
            project_id=integration.project_id,
            provider=integration.provider,
            jira_project_id=integration.external_project_id,
            jira_project_key=integration.external_project_key or "",
            jira_project_name=integration.external_project_name or "",
            jira_project_type=config.get("jira_project_type"),
            created_at=integration.created_at,
            updated_at=integration.updated_at,
        ).model_dump()
