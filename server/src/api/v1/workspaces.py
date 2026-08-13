import logging
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

from src.core.database import get_db
from src.middleware.auth import require_authenticated_user
from src.middleware.rbac import require_workspace_role
from src.models.base import MemberRole
from src.repositories.workspace_member_repository import WorkspaceMemberRepository
from src.repositories.workspace_repository import WorkspaceRepository
from src.schemas.base_response import BaseResponse
from src.schemas.workspace_schema import WorkspaceCreate, WorkspaceResponse, WorkspaceUpdate
from src.services.membership_service import MembershipService


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
    user_id = UUID(request.state.user.id)
    await MembershipService(db).assert_workspace_boundary("workspace", workspace_id, user_id)
    repo = WorkspaceRepository(db)
    workspace = await repo.get_by_id(workspace_id)
    data = WorkspaceResponse.model_validate(workspace).model_dump()
    return BaseResponse(data=data)


@router.patch("/{workspace_id}", response_model=BaseResponse)
async def update_workspace(
    workspace_id: UUID,
    body: WorkspaceUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    user_id = UUID(request.state.user.id)
    await MembershipService(db).assert_workspace_boundary("workspace", workspace_id, user_id)
    await require_workspace_role(MemberRole.ADMIN)(workspace_id, request, db)
    repo = WorkspaceRepository(db)
    workspace = await repo.update(workspace_id, **body.model_dump(exclude_none=True))
    if workspace is None:
        return BaseResponse(success=False, message="Workspace not found", data=None)
    await db.commit()
    return BaseResponse(data=WorkspaceResponse.model_validate(workspace).model_dump())


@router.delete("/{workspace_id}", response_model=BaseResponse)
async def delete_workspace(
    workspace_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    user_id = UUID(request.state.user.id)
    service = MembershipService(db)
    await service.assert_workspace_boundary("workspace", workspace_id, user_id)
    await require_workspace_role(MemberRole.OWNER)(workspace_id, request, db)
    await service.delete_workspace(workspace_id)
    await db.commit()
    return BaseResponse(message="Workspace deleted successfully")
