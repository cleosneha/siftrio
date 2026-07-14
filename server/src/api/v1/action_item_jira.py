from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.middleware.auth import require_authenticated_user
from src.schemas.base_response import BaseResponse
from src.schemas.jira_schema import ActionItemJiraCreateRequest
from src.services.action_item_jira_service import ActionItemJiraService
from src.services.membership_service import MembershipService

router = APIRouter(
    tags=["action-item-jira"],
    dependencies=[Depends(require_authenticated_user)],
)


@router.get("/projects/{project_id}/action-items/{action_item_id}/jira/preview", response_model=BaseResponse)
async def preview_action_item_jira(
    project_id: UUID,
    action_item_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    user_id = UUID(request.state.user.id)
    await MembershipService(db).assert_project_access(project_id, user_id)
    service = ActionItemJiraService(db)
    data = await service.get_preview(action_item_id)
    return BaseResponse(data=data)


@router.get("/projects/{project_id}/action-items/{action_item_id}/jira/issue-types", response_model=BaseResponse)
async def list_jira_issue_types(
    project_id: UUID,
    action_item_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    user_id = UUID(request.state.user.id)
    await MembershipService(db).assert_project_access(project_id, user_id)
    service = ActionItemJiraService(db)
    data = await service.get_issue_types(project_id)
    return BaseResponse(data=data)


@router.get("/projects/{project_id}/action-items/{action_item_id}/jira/users", response_model=BaseResponse)
async def search_jira_assignees(
    project_id: UUID,
    action_item_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    query: str = Query(""),
) -> BaseResponse:
    user_id = UUID(request.state.user.id)
    await MembershipService(db).assert_project_access(project_id, user_id)
    service = ActionItemJiraService(db)
    data = await service.search_users(project_id, query)
    return BaseResponse(data=data)


@router.post("/projects/{project_id}/action-items/{action_item_id}/jira/issues", response_model=BaseResponse)
async def create_jira_issue_from_action_item(
    project_id: UUID,
    action_item_id: UUID,
    body: ActionItemJiraCreateRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    user_id = UUID(request.state.user.id)
    await MembershipService(db).assert_project_access(project_id, user_id)
    service = ActionItemJiraService(db)

    from src.repositories.workspace_jira_repository import WorkspaceJiraRepository
    from src.models.client import Client
    from src.repositories.project_repository import ProjectRepository
    project = await ProjectRepository(db).get_by_id(project_id)
    if project is None:
        return BaseResponse(success=False, message="Project not found", data=None)
    client = await db.get(Client, project.client_id)
    site_url = None
    if client:
        integration = await WorkspaceJiraRepository(db).get_by_workspace(client.workspace_id)
        if integration:
            site_url = integration.site_url

    data = await service.create_issue(action_item_id, body, site_url=site_url)
    return BaseResponse(message="Jira issue created", data=data)


@router.get("/projects/{project_id}/action-items/{action_item_id}/jira/issue", response_model=BaseResponse)
async def get_jira_issue_details(
    project_id: UUID,
    action_item_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    user_id = UUID(request.state.user.id)
    await MembershipService(db).assert_project_access(project_id, user_id)
    service = ActionItemJiraService(db)
    data = await service.get_issue_details(project_id, action_item_id)
    return BaseResponse(data=data)
