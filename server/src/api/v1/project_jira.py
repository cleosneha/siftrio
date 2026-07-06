from uuid import UUID

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.middleware.auth import require_authenticated_user
from src.schemas.base_response import BaseResponse
from src.schemas.jira_schema import (
    ConnectJiraProjectRequest,
    CreateJiraProjectRequest,
)
from src.services.membership_service import MembershipService
from src.services.project_jira_service import ProjectJiraService

router = APIRouter(
    tags=["project-jira"],
    dependencies=[Depends(require_authenticated_user)],
)


@router.get("/projects/{project_id}/jira", response_model=BaseResponse)
async def get_project_jira(
    project_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    user_id = UUID(request.state.user.id)
    await MembershipService(db).assert_project_access(project_id, user_id)
    service = ProjectJiraService(db)
    data = await service.get_mapping(project_id)
    if data is None:
        return BaseResponse(success=False, message="No Jira integration", data=None)
    return BaseResponse(data=data)


@router.get("/projects/{project_id}/jira/projects", response_model=BaseResponse)
async def list_jira_projects(
    project_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    user_id = UUID(request.state.user.id)
    await MembershipService(db).assert_project_access(project_id, user_id)
    service = ProjectJiraService(db)
    data = await service.get_available_projects(project_id)
    return BaseResponse(data=data)


@router.post("/projects/{project_id}/jira/connect", response_model=BaseResponse)
async def connect_project_jira(
    project_id: UUID,
    body: ConnectJiraProjectRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    user_id = UUID(request.state.user.id)
    await MembershipService(db).assert_project_access(project_id, user_id)
    service = ProjectJiraService(db)
    data = await service.connect_existing(project_id, body)
    return BaseResponse(message="Jira project connected", data=data)


@router.post("/projects/{project_id}/jira/create", response_model=BaseResponse)
async def create_and_connect_jira_project(
    project_id: UUID,
    body: CreateJiraProjectRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    user_id = UUID(request.state.user.id)
    await MembershipService(db).assert_project_access(project_id, user_id)
    service = ProjectJiraService(db)
    data = await service.create_and_connect(project_id, body)
    return BaseResponse(message="Jira project created and connected", data=data)


@router.delete("/projects/{project_id}/jira", response_model=BaseResponse)
async def disconnect_project_jira(
    project_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    user_id = UUID(request.state.user.id)
    await MembershipService(db).assert_project_access(project_id, user_id)
    service = ProjectJiraService(db)
    await service.disconnect(project_id)
    return BaseResponse(message="Jira project disconnected")
