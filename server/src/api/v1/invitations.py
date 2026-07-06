from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.middlewares.auth import require_authenticated_user
from src.models.member_invitation import ResourceType
from src.schemas.base_response import BaseResponse
from src.schemas.member_invitation_schema import InviteMemberRequest
from src.services.invitation_service import InvitationService

router = APIRouter(
    prefix="/invitations",
    tags=["invitations"],
    dependencies=[Depends(require_authenticated_user)],
)


@router.post("", response_model=BaseResponse)
async def create_invitation(
    body: InviteMemberRequest,
    request: Request,
    resource_type: str = Query(...),
    resource_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    user_id = UUID(request.state.user.id)
    service = InvitationService(db)
    rtype = ResourceType(resource_type)
    data = await service.invite(body.email, rtype, resource_id, user_id)
    return BaseResponse(message="Invitation sent successfully.", data=data)


@router.get("", response_model=BaseResponse)
async def list_pending_invitations(
    resource_type: str = Query(...),
    resource_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    service = InvitationService(db)
    rtype = ResourceType(resource_type)
    data = await service.list_pending(rtype, resource_id)
    return BaseResponse(data=data)


@router.post("/accept/{token}", response_model=BaseResponse)
async def accept_invitation(
    token: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    user_id = UUID(request.state.user.id)
    service = InvitationService(db)
    data = await service.accept(token, user_id)
    return BaseResponse(message="You have successfully joined.", data=data)
