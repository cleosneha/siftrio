import logging
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions.base import BaseAPIException
from src.integrations.atlassian.client import JiraClient
from src.models.knowledge_base import ActionItemSyncStatus
from src.repositories.knowledge_repository import KnowledgeRepository
from src.repositories.project_jira_repository import ProjectJiraRepository
from src.repositories.project_repository import ProjectRepository
from src.schemas.jira_schema import (
    ActionItemJiraCreateRequest,
    ActionItemJiraCreateResponse,
    ActionItemJiraPreview,
    JiraIssueType,
    JiraUser,
)
from src.services.workspace_jira_service import WorkspaceJiraService

logger = logging.getLogger(__name__)


class ActionItemJiraService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.project_repo = ProjectRepository(db)
        self.project_jira_repo = ProjectJiraRepository(db)
        self.knowledge_repo = KnowledgeRepository(db)
        self.workspace_jira_service = WorkspaceJiraService(db)

    async def _resolve_jira_integration(self, project_id: UUID) -> tuple[str, str, str, str]:
        project = await self.project_repo.get_by_id(project_id)
        if project is None:
            raise BaseAPIException(message="Project not found", status_code=404)

        from src.models.client import Client
        client = await self.db.get(Client, project.client_id)
        if client is None:
            raise BaseAPIException(message="Client not found", status_code=404)

        workspace_id = client.workspace_id
        integration = await self.workspace_jira_service.repo.get_by_workspace(workspace_id)
        if integration is None or not integration.cloud_id:
            raise BaseAPIException(
                message="Workspace is not connected to Jira. Connect Jira first.",
                status_code=400,
            )

        if not integration.access_token:
            raise BaseAPIException(
                message="Jira access token is missing. Reconnect Jira.",
                status_code=400,
            )

        access_token = await self.workspace_jira_service.get_valid_access_token(workspace_id)

        project_jira = await self.project_jira_repo.get_by_project(project_id)
        if project_jira is None:
            raise BaseAPIException(
                message="Project is not connected to a Jira project. Connect a Jira project first.",
                status_code=400,
            )

        return (
            integration.cloud_id,
            access_token,
            project_jira.jira_project_id,
            project_jira.jira_project_key,
        )

    async def get_preview(self, action_item_id: UUID) -> ActionItemJiraPreview:
        entity = await self.knowledge_repo.get_action_item(action_item_id)
        if entity is None:
            raise BaseAPIException(message="Action item not found", status_code=404)

        meeting_title = entity.meeting.title if entity.meeting else "No meeting title"

        due = ""
        if entity.due_date:
            due = entity.due_date.strftime("%Y-%m-%d")

        desc_lines = [f"Meeting: {meeting_title}"]
        if entity.description:
            desc_lines.append("")
            desc_lines.append(entity.description)
        if due:
            desc_lines.append("")
            desc_lines.append(f"Due Date: {due}")
        if entity.assignee:
            desc_lines.append(f"Assignee: {entity.assignee}")

        return ActionItemJiraPreview(
            summary=entity.title,
            description="\n".join(desc_lines).strip(),
            issue_type="Task",
            priority="Medium",
            labels=["action-item"],
            assignee=entity.assignee,
        )

    async def get_issue_types(
        self, project_id: UUID,
    ) -> list[JiraIssueType]:
        cloud_id, access_token, jira_project_id, _jira_project_key = await self._resolve_jira_integration(project_id)
        client = JiraClient(cloud_id, access_token)
        raw = await client.get_issue_types(jira_project_id)
        return [
            JiraIssueType(
                id=str(t["id"]),
                name=t["name"],
                description=t.get("description"),
                subtask=t.get("subtask", False),
            )
            for t in raw
        ]

    async def search_users(
        self, project_id: UUID, query: str,
    ) -> list[JiraUser]:
        cloud_id, access_token, _jira_project_id, jira_project_key = await self._resolve_jira_integration(project_id)
        client = JiraClient(cloud_id, access_token)
        raw = await client.search_users(query, project=jira_project_key)
        return [
            JiraUser(
                account_id=u["accountId"],
                display_name=u.get("displayName", ""),
                email_address=u.get("emailAddress"),
            )
            for u in raw
        ]

    async def create_issue(
        self,
        action_item_id: UUID,
        request: ActionItemJiraCreateRequest,
        site_url: str | None = None,
    ) -> ActionItemJiraCreateResponse:
        entity = await self.knowledge_repo.get_action_item(action_item_id)
        if entity is None:
            raise BaseAPIException(message="Action item not found", status_code=404)

        if entity.jira_issue_id is not None:
            raise BaseAPIException(
                message="Action item already has a linked Jira issue",
                status_code=409,
            )

        cloud_id, access_token, _jira_project_id, jira_project_key = await self._resolve_jira_integration(
            entity.project_id,
        )

        fields: dict[str, object] = {
            "project": {"key": jira_project_key},
            "summary": request.summary,
            "description": {
                "version": 1,
                "type": "doc",
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {"type": "text", "text": request.description},
                        ],
                    },
                ],
            },
            "issuetype": {"id": request.issue_type_id},
            "labels": request.labels,
        }

        if request.assignee_account_id:
            fields["assignee"] = {"id": request.assignee_account_id}

        client = JiraClient(cloud_id, access_token)
        result = await client.create_issue(fields)
        if result is None:
            raise BaseAPIException(
                message="Failed to create Jira issue. Check logs for details.",
                status_code=502,
            )

        issue_id = str(result.get("id", ""))
        issue_key = str(result.get("key", ""))
        issue_url = f"https://{site_url or 'your-domain.atlassian.net'}/browse/{issue_key}" if site_url else ""

        from datetime import datetime, timezone
        updated = await self.knowledge_repo.update_action_item(
            action_item_id,
            jira_issue_id=issue_id,
            jira_issue_key=issue_key,
            jira_issue_url=issue_url,
            jira_issue_type=request.issue_type_id,
            jira_synced_at=datetime.now(timezone.utc),
            sync_status=ActionItemSyncStatus.SYNCED.value,
        )
        if updated is None:
            raise BaseAPIException(
                message="Action item not found during update",
                status_code=404,
            )

        await self.db.commit()

        return ActionItemJiraCreateResponse(
            issue_id=issue_id,
            issue_key=issue_key,
            issue_url=issue_url,
        )
