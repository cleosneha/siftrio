from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.controllers.meeting_suggestion_controller import MeetingSuggestionController
from src.core.database import get_db
from src.middlewares.auth import require_authenticated_user
from src.schemas.base_response import BaseResponse
from src.schemas.meeting_suggestion_schema import MeetingSuggestionScheduleRequest


router = APIRouter(
    prefix="/meetings/{meeting_id}/suggestions",
    tags=["meeting-suggestions"],
    dependencies=[Depends(require_authenticated_user)],
)


@router.get("", response_model=BaseResponse)
async def list_suggestions(
    meeting_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    controller = MeetingSuggestionController(db)
    return await controller.list_suggestions(meeting_id)


@router.post("/{suggestion_id}/schedule", response_model=BaseResponse)
async def schedule_suggestion(
    meeting_id: UUID,
    suggestion_id: UUID,
    body: MeetingSuggestionScheduleRequest = MeetingSuggestionScheduleRequest(),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    controller = MeetingSuggestionController(db)
    return await controller.schedule(suggestion_id, body)


@router.post("/{suggestion_id}/dismiss", response_model=BaseResponse)
async def dismiss_suggestion(
    meeting_id: UUID,
    suggestion_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    controller = MeetingSuggestionController(db)
    return await controller.dismiss(suggestion_id)
