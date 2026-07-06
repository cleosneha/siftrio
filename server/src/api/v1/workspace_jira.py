import logging
from uuid import UUID

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

from src.core.config import settings
from src.core.database import get_db
from src.middleware.auth import require_authenticated_user
from src.repositories.project_jira_repository import ProjectJiraRepository
from src.schemas.base_response import BaseResponse
from src.services.membership_service import MembershipService
from src.services.workspace_jira_service import WorkspaceJiraService

router = APIRouter(
    tags=["workspace-jira"],
    dependencies=[Depends(require_authenticated_user)],
)


@router.get("/workspaces/{workspace_id}/jira", response_model=BaseResponse)
async def get_workspace_jira(
    workspace_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    user_id = UUID(request.state.user.id)
    await MembershipService(db).assert_workspace_access(workspace_id, user_id)
    service = WorkspaceJiraService(db)
    data = await service.get_integration(workspace_id)
    if data is None:
        return BaseResponse(success=False, message="No Jira integration", data=None)
    return BaseResponse(data=data)


@router.get("/workspaces/{workspace_id}/jira/connect")
async def connect_workspace_jira_redirect(
    workspace_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> RedirectResponse:
    user_id = UUID(request.state.user.id)
    await MembershipService(db).assert_workspace_access(workspace_id, user_id)
    service = WorkspaceJiraService(db)
    url = await service.get_or_create_oauth_url(workspace_id, user_id)
    return RedirectResponse(url=url)


@router.post("/workspaces/{workspace_id}/jira/connect")
async def connect_workspace_jira(
    workspace_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> dict:
    user_id = UUID(request.state.user.id)
    await MembershipService(db).assert_workspace_access(workspace_id, user_id)
    service = WorkspaceJiraService(db)
    url = await service.get_or_create_oauth_url(workspace_id, user_id)
    return {"url": url}


@router.get("/jira/callback")
async def jira_oauth_callback(
    code: str,
    state: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> RedirectResponse:
    workspace_id = UUID(state)
    request.state.user = getattr(request.state, "user", None)
    if request.state.user is None:
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/login?error=jira_auth")

    user_id = UUID(request.state.user.id)
    service = WorkspaceJiraService(db)
    try:
        await service.handle_callback(workspace_id, code, user_id)
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/workspaces/{workspace_id}?jira=connected"
        )
    except Exception as exc:
        logger.exception("Jira OAuth callback failed for workspace %s: %s", workspace_id, exc)
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/workspaces/{workspace_id}?jira=error"
        )


@router.post("/workspaces/{workspace_id}/jira/refresh", response_model=BaseResponse)
async def refresh_workspace_jira(
    workspace_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    user_id = UUID(request.state.user.id)
    await MembershipService(db).assert_workspace_access(workspace_id, user_id)
    service = WorkspaceJiraService(db)
    data = await service.refresh_token(workspace_id)
    return BaseResponse(message="Token refreshed", data=data)


@router.get("/workspaces/{workspace_id}/jira/sites", response_model=BaseResponse)
async def list_jira_sites(
    workspace_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    user_id = UUID(request.state.user.id)
    await MembershipService(db).assert_workspace_access(workspace_id, user_id)
    service = WorkspaceJiraService(db)
    data = await service.get_sites(workspace_id)
    return BaseResponse(data=data)


@router.delete("/workspaces/{workspace_id}/jira", response_model=BaseResponse)
async def disconnect_workspace_jira(
    workspace_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    user_id = UUID(request.state.user.id)
    await MembershipService(db).assert_workspace_access(workspace_id, user_id)

    service = WorkspaceJiraService(db)
    project_jira_repo = ProjectJiraRepository(db)

    project_mappings = await project_jira_repo.list_by_workspace(workspace_id)
    for mapping in project_mappings:
        await project_jira_repo.delete(mapping)

    await service.disconnect(workspace_id)
    await db.commit()
    return BaseResponse(message="Jira disconnected from workspace")
