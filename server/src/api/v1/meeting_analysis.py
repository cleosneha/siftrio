from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.controllers.meeting_analysis_controller import MeetingAnalysisController
from src.core.database import get_db
from src.middlewares.auth import require_authenticated_user
from src.schemas.base_response import BaseResponse


router = APIRouter(
    prefix="/meetings",
    tags=["meeting-analysis"],
    dependencies=[Depends(require_authenticated_user)],
)


@router.get("/{meeting_id}/analysis", response_model=BaseResponse)
async def get_meeting_analysis(
    meeting_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    controller = MeetingAnalysisController(db)
    return await controller.get_analysis(meeting_id)


@router.post("/{meeting_id}/analysis/regenerate", response_model=BaseResponse)
async def regenerate_meeting_analysis(
    meeting_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    controller = MeetingAnalysisController(db)
    return await controller.regenerate(meeting_id)
