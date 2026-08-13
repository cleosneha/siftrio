from uuid import UUID

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.middleware.auth import require_authenticated_user
from src.middleware.rbac import require_client_role, require_project_role, require_workspace_role
from src.models.base import MemberRole
from src.schemas.base_response import BaseResponse
from src.schemas.membership_schema import RoleChangeRequest
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
    await service.assert_workspace_boundary("workspace", workspace_id, user_id)
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
    await service.assert_workspace_boundary("client", client_id, user_id)
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
    await service.assert_workspace_boundary("project", project_id, user_id)
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
    await service.assert_workspace_boundary("workspace", workspace_id, current_user_id)
    await require_workspace_role(MemberRole.ADMIN)(workspace_id, request, db)
    await service.remove_workspace_member(workspace_id, user_id, current_user_id)
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
    await service.assert_workspace_boundary("client", client_id, current_user_id)
    await require_client_role(MemberRole.ADMIN)(client_id, request, db)
    await service.remove_client_member(client_id, user_id, current_user_id)
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
    await service.assert_workspace_boundary("project", project_id, current_user_id)
    await require_project_role(MemberRole.ADMIN)(project_id, request, db)
    await service.remove_project_member(project_id, user_id, current_user_id)
    await db.commit()
    return BaseResponse(message="Member removed successfully.")


@router.patch("/workspace/{workspace_id}/users/{user_id}/role", response_model=BaseResponse)
async def change_workspace_member_role(
    workspace_id: UUID,
    user_id: UUID,
    body: RoleChangeRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    current_user_id = UUID(request.state.user.id)
    service = MembershipService(db)
    await service.assert_workspace_boundary("workspace", workspace_id, current_user_id)
    await require_workspace_role(MemberRole.ADMIN)(workspace_id, request, db)
    member = await service.change_workspace_role(
        workspace_id, user_id, body.role, current_user_id
    )
    if member is None:
        await db.rollback()
        return BaseResponse(success=False, message="Member not found.")
    await db.commit()
    return BaseResponse(message="Member role updated successfully.", data=member)


@router.patch("/client/{client_id}/users/{user_id}/role", response_model=BaseResponse)
async def change_client_member_role(
    client_id: UUID,
    user_id: UUID,
    body: RoleChangeRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    current_user_id = UUID(request.state.user.id)
    service = MembershipService(db)
    await service.assert_workspace_boundary("client", client_id, current_user_id)
    await require_client_role(MemberRole.ADMIN)(client_id, request, db)
    member = await service.change_client_role(
        client_id, user_id, body.role, current_user_id
    )
    if member is None:
        await db.rollback()
        return BaseResponse(success=False, message="Member not found.")
    await db.commit()
    return BaseResponse(message="Member role updated successfully.", data=member)


@router.patch("/project/{project_id}/users/{user_id}/role", response_model=BaseResponse)
async def change_project_member_role(
    project_id: UUID,
    user_id: UUID,
    body: RoleChangeRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    current_user_id = UUID(request.state.user.id)
    service = MembershipService(db)
    await service.assert_workspace_boundary("project", project_id, current_user_id)
    await require_project_role(MemberRole.ADMIN)(project_id, request, db)
    member = await service.change_project_role(
        project_id, user_id, body.role, current_user_id
    )
    if member is None:
        await db.rollback()
        return BaseResponse(success=False, message="Member not found.")
    await db.commit()
    return BaseResponse(message="Member role updated successfully.", data=member)
