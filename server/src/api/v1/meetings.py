from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.controllers.meeting_controller import MeetingController
from src.core.database import get_db
from src.schemas.base_response import BaseResponse
from src.schemas.meeting_schema import MeetingCreate

router = APIRouter(prefix="/meetings", tags=["meetings"])


@router.post("", response_model=BaseResponse)
async def create_meeting(body: MeetingCreate, db: AsyncSession = Depends(get_db)) -> BaseResponse:
    controller = MeetingController(db)
    return await controller.create(body)


@router.get("/{meeting_id}", response_model=BaseResponse)
async def get_meeting(meeting_id: str, db: AsyncSession = Depends(get_db)) -> BaseResponse:
    controller = MeetingController(db)
    return await controller.get_by_id(meeting_id)


@router.get("", response_model=BaseResponse)
async def list_meetings(
    client_id: str | None = None,
    project_id: str | None = None,
    miscellaneous: bool = False,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    controller = MeetingController(db)
    if project_id:
        return await controller.list_by_project(project_id)
    if miscellaneous and client_id:
        return await controller.list_miscellaneous(client_id)
    if client_id:
        return await controller.list_by_client(client_id)
    return BaseResponse(data=[])


@router.delete("/{meeting_id}", response_model=BaseResponse)
async def delete_meeting(meeting_id: str, db: AsyncSession = Depends(get_db)) -> BaseResponse:
    controller = MeetingController(db)
    return await controller.delete(meeting_id)
