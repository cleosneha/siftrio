import logging
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

from src.core.database import get_db
from src.middlewares.auth import require_authenticated_user
from src.models.workspace_member import MemberRole
from src.repositories.membership_repository import WorkspaceMemberRepository
from src.repositories.workspace_repository import WorkspaceRepository
from src.schemas.base_response import BaseResponse
from src.schemas.workspace_schema import WorkspaceCreate, WorkspaceResponse


router = APIRouter(
    prefix="/workspaces",
    tags=["workspaces"],
    dependencies=[Depends(require_authenticated_user)],
)


@router.post("", response_model=BaseResponse)
async def create_workspace(
    body: WorkspaceCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    repo = WorkspaceRepository(db)
    member_repo = WorkspaceMemberRepository(db)
    user_id = UUID(request.state.user.id)
    workspace = await repo.create(body.name, body.description, created_by=user_id)
    await member_repo.create(workspace.id, user_id, MemberRole.OWNER)
    await db.commit()
    data = WorkspaceResponse.model_validate(workspace).model_dump()
    return BaseResponse(message="Workspace created successfully", data=data)


@router.get("", response_model=BaseResponse)
async def list_workspaces(
    request: Request,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    repo = WorkspaceRepository(db)
    user_id = UUID(request.state.user.id)
    workspaces = await repo.list_by_user_id(user_id, limit=limit, offset=offset)
    data = [WorkspaceResponse.model_validate(w).model_dump() for w in workspaces]
    return BaseResponse(data=data)


@router.get("/{workspace_id}", response_model=BaseResponse)
async def get_workspace(
    workspace_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    repo = WorkspaceRepository(db)
    workspace = await repo.get_by_id(workspace_id)
    if workspace is None:
        return BaseResponse(success=False, message="Workspace not found", data=None)
    user_id = UUID(request.state.user.id)
    from src.services.membership_service import MembershipService
    await MembershipService(db).assert_workspace_access(workspace_id, user_id)
    data = WorkspaceResponse.model_validate(workspace).model_dump()
    return BaseResponse(data=data)
