from uuid import UUID

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.controllers.meeting_suggestion_controller import MeetingSuggestionController
from src.core.database import get_db
from src.middleware.auth import require_authenticated_user
from src.middleware.rbac import require_client_role, require_project_role
from src.models.base import MemberRole
from src.repositories.meeting_repository import MeetingRepository
from src.schemas.base_response import BaseResponse
from src.schemas.meeting_suggestion_schema import MeetingSuggestionScheduleRequest
from src.services.membership_service import MembershipService


router = APIRouter(
    prefix="/meetings/{meeting_id}/suggestions",
    tags=["meeting-suggestions"],
    dependencies=[Depends(require_authenticated_user)],
)


async def _assert_meeting_access(meeting_id: UUID, request: Request, db: AsyncSession):
    user_id = UUID(request.state.user.id)
    await MembershipService(db).assert_workspace_boundary("meeting", meeting_id, user_id)
    meeting = await MeetingRepository(db).get_by_id(meeting_id)
    if meeting is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Meeting not found")
    await MembershipService(db).assert_meeting_access(meeting, user_id)
    return meeting


async def _require_meeting_role(meeting, request: Request, db: AsyncSession, min_role: MemberRole) -> None:
    if meeting.project_id:
        await require_project_role(min_role)(meeting.project_id, request, db)
    else:
        await require_client_role(min_role)(meeting.client_id, request, db)


@router.get("", response_model=BaseResponse)
async def list_suggestions(
    meeting_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    await _assert_meeting_access(meeting_id, request, db)
    controller = MeetingSuggestionController(db)
    return await controller.list_suggestions(meeting_id)


@router.post("/{suggestion_id}/schedule", response_model=BaseResponse)
async def schedule_suggestion(
    meeting_id: UUID,
    suggestion_id: UUID,
    request: Request,
    body: MeetingSuggestionScheduleRequest = MeetingSuggestionScheduleRequest(),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    meeting = await _assert_meeting_access(meeting_id, request, db)
    await _require_meeting_role(meeting, request, db, MemberRole.MEMBER)
    controller = MeetingSuggestionController(db)
    return await controller.schedule(suggestion_id, body)


@router.post("/{suggestion_id}/dismiss", response_model=BaseResponse)
async def dismiss_suggestion(
    meeting_id: UUID,
    suggestion_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    meeting = await _assert_meeting_access(meeting_id, request, db)
    await _require_meeting_role(meeting, request, db, MemberRole.MEMBER)
    controller = MeetingSuggestionController(db)
    return await controller.dismiss(suggestion_id)
