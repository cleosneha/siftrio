from uuid import UUID

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.middlewares.auth import require_authenticated_user
from src.schemas.base_response import BaseResponse
from src.services.membership_service import MembershipService

router = APIRouter(
    prefix="/members",
    tags=["members"],
    dependencies=[Depends(require_authenticated_user)],
)


@router.get("/workspace/{workspace_id}", response_model=BaseResponse)
async def list_workspace_members(
    workspace_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    user_id = UUID(request.state.user.id)
    service = MembershipService(db)
    await service.assert_workspace_access(workspace_id, user_id)
    data = await service.list_workspace_members(workspace_id)
    return BaseResponse(data=data)


@router.get("/client/{client_id}", response_model=BaseResponse)
async def list_client_members(
    client_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    user_id = UUID(request.state.user.id)
    service = MembershipService(db)
    await service.assert_client_access(client_id, user_id)
    data = await service.list_client_members(client_id)
    return BaseResponse(data=data)


@router.get("/project/{project_id}", response_model=BaseResponse)
async def list_project_members(
    project_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    user_id = UUID(request.state.user.id)
    service = MembershipService(db)
    await service.assert_project_access(project_id, user_id)
    data = await service.list_project_members(project_id)
    return BaseResponse(data=data)


@router.delete("/workspace/{workspace_id}/users/{user_id}", response_model=BaseResponse)
async def remove_workspace_member(
    workspace_id: UUID,
    user_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    current_user_id = UUID(request.state.user.id)
    service = MembershipService(db)
    await service.assert_workspace_access(workspace_id, current_user_id)
    await service.remove_workspace_member(workspace_id, user_id)
    await db.commit()
    return BaseResponse(message="Member removed successfully.")


@router.delete("/client/{client_id}/users/{user_id}", response_model=BaseResponse)
async def remove_client_member(
    client_id: UUID,
    user_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    current_user_id = UUID(request.state.user.id)
    service = MembershipService(db)
    await service.assert_client_access(client_id, current_user_id)
    await service.remove_client_member(client_id, user_id)
    await db.commit()
    return BaseResponse(message="Member removed successfully.")


@router.delete("/project/{project_id}/users/{user_id}", response_model=BaseResponse)
async def remove_project_member(
    project_id: UUID,
    user_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    current_user_id = UUID(request.state.user.id)
    service = MembershipService(db)
    await service.assert_project_access(project_id, current_user_id)
    await service.remove_project_member(project_id, user_id)
    await db.commit()
    return BaseResponse(message="Member removed successfully.")
