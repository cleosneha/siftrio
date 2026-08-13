from uuid import UUID

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.controllers.meeting_analysis_controller import MeetingAnalysisController
from src.core.database import get_db
from src.middleware.auth import require_authenticated_user
from src.schemas.base_response import BaseResponse


router = APIRouter(
    prefix="/meetings",
    tags=["meeting-analysis"],
    dependencies=[Depends(require_authenticated_user)],
)


@router.get("/{meeting_id}/analysis", response_model=BaseResponse)
async def get_meeting_analysis(
    meeting_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    user_id = UUID(request.state.user.id)
    from src.services.membership_service import MembershipService
    await MembershipService(db).assert_workspace_boundary("meeting", meeting_id, user_id)
    controller = MeetingAnalysisController(db)
    return await controller.get_analysis(meeting_id)


@router.post("/{meeting_id}/analysis/regenerate", response_model=BaseResponse)
async def regenerate_meeting_analysis(
    meeting_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    user_id = UUID(request.state.user.id)
    from src.services.membership_service import MembershipService
    await MembershipService(db).assert_workspace_boundary("meeting", meeting_id, user_id)
    controller = MeetingAnalysisController(db)
    return await controller.regenerate(meeting_id)
