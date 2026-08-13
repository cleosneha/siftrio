from uuid import UUID

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.middleware.auth import require_authenticated_user
from src.middleware.rbac import require_client_role, require_project_role, require_workspace_role
from src.models.base import MemberRole
from src.schemas.base_response import BaseResponse
from src.schemas.ownership_schema import OwnershipTransferRequest
from src.services.membership_service import MembershipService

router = APIRouter(
    prefix="/ownership",
    tags=["ownership"],
    dependencies=[Depends(require_authenticated_user)],
)


@router.post("/workspaces/{workspace_id}/transfer", response_model=BaseResponse)
async def transfer_workspace_ownership(
    workspace_id: UUID,
    body: OwnershipTransferRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    user_id = UUID(request.state.user.id)
    service = MembershipService(db)
    await service.assert_workspace_boundary("workspace", workspace_id, user_id)
    await require_workspace_role(MemberRole.OWNER)(workspace_id, request, db)
    await service.transfer_ownership("workspace", workspace_id, body.user_id, user_id)
    await db.commit()
    return BaseResponse(message="Workspace ownership transferred successfully")


@router.post("/clients/{client_id}/transfer", response_model=BaseResponse)
async def transfer_client_ownership(
    client_id: UUID,
    body: OwnershipTransferRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    user_id = UUID(request.state.user.id)
    service = MembershipService(db)
    await service.assert_workspace_boundary("client", client_id, user_id)
    await require_client_role(MemberRole.OWNER)(client_id, request, db)
    await service.transfer_ownership("client", client_id, body.user_id, user_id)
    await db.commit()
    return BaseResponse(message="Client ownership transferred successfully")


@router.post("/projects/{project_id}/transfer", response_model=BaseResponse)
async def transfer_project_ownership(
    project_id: UUID,
    body: OwnershipTransferRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    user_id = UUID(request.state.user.id)
    service = MembershipService(db)
    await service.assert_workspace_boundary("project", project_id, user_id)
    await require_project_role(MemberRole.OWNER)(project_id, request, db)
    await service.transfer_ownership("project", project_id, body.user_id, user_id)
    await db.commit()
    return BaseResponse(message="Project ownership transferred successfully")
