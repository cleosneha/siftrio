from uuid import UUID

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.middlewares.auth import require_authenticated_user
from src.repositories.meeting_repository import MeetingRepository
from src.schemas.base_response import BaseResponse
from src.schemas.meeting_schema import MeetingCreate, MeetingResponse
from src.services.meeting_service import MeetingService

router = APIRouter(
    prefix="/meetings",
    tags=["meetings"],
    dependencies=[Depends(require_authenticated_user)],
)


@router.post("", response_model=BaseResponse)
async def create_meeting(
    body: MeetingCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    service = MeetingService(db)
    user_id = UUID(request.state.user.id) if request.state.user else None
    data = await service.create(
        client_id=body.client_id,
        project_id=body.project_id,
        title=body.title,
        meeting_type=body.meeting_type,
        tags=body.tags,
        meeting_date=body.meeting_date,
        meeting_provider=body.meeting_provider,
        meeting_url=body.meeting_url,
        start_time=body.start_time,
        end_time=body.end_time,
        user_id=user_id,
    )
    return BaseResponse(message="Meeting created successfully", data=data)


@router.get("/{meeting_id}", response_model=BaseResponse)
async def get_meeting(meeting_id: str, db: AsyncSession = Depends(get_db)) -> BaseResponse:
    meeting = await MeetingRepository(db).get_by_id(UUID(meeting_id))
    if meeting is None:
        return BaseResponse(success=False, message="Meeting not found", data=None)
    data = MeetingResponse(
        id=str(meeting.id),
        client_id=str(meeting.client_id),
        project_id=str(meeting.project_id) if meeting.project_id else None,
        title=meeting.title,
        meeting_type=meeting.meeting_type.value,
        tags=meeting.tags,
        transcript=meeting.transcript,
        meeting_date=meeting.meeting_date.isoformat() if meeting.meeting_date else None,
        start_time=meeting.start_time.isoformat().replace("+00:00", "Z") if meeting.start_time else None,
        end_time=meeting.end_time.isoformat().replace("+00:00", "Z") if meeting.end_time else None,
        meeting_provider=meeting.meeting_provider.value,
        meeting_url=meeting.meeting_url,
        created_at=meeting.created_at.isoformat().replace("+00:00", "Z") if meeting.created_at else None,
        updated_at=meeting.updated_at.isoformat().replace("+00:00", "Z") if meeting.updated_at else None,
    ).model_dump()
    return BaseResponse(data=data)


@router.get("", response_model=BaseResponse)
async def list_meetings(
    client_id: str | None = None,
    project_id: str | None = None,
    miscellaneous: bool = False,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    repo = MeetingRepository(db)

    if project_id:
        meetings = await repo.list_by_project(UUID(project_id))
    elif miscellaneous and client_id:
        meetings = await repo.list_miscellaneous_by_client(UUID(client_id))
    elif client_id:
        meetings = await repo.list_by_client(UUID(client_id))
    else:
        return BaseResponse(data=[])

    data = [
        MeetingResponse(
            id=str(m.id),
            client_id=str(m.client_id),
            project_id=str(m.project_id) if m.project_id else None,
            title=m.title,
            meeting_type=m.meeting_type.value,
            tags=m.tags,
            transcript=m.transcript,
            meeting_date=m.meeting_date.isoformat() if m.meeting_date else None,
            start_time=m.start_time.isoformat().replace("+00:00", "Z") if m.start_time else None,
            end_time=m.end_time.isoformat().replace("+00:00", "Z") if m.end_time else None,
            meeting_provider=m.meeting_provider.value,
            meeting_url=m.meeting_url,
            created_at=m.created_at.isoformat().replace("+00:00", "Z") if m.created_at else None,
            updated_at=m.updated_at.isoformat().replace("+00:00", "Z") if m.updated_at else None,
        ).model_dump()
        for m in meetings
    ]
    return BaseResponse(data=data)


@router.delete("/{meeting_id}", response_model=BaseResponse)
async def delete_meeting(meeting_id: str, db: AsyncSession = Depends(get_db)) -> BaseResponse:
    repo = MeetingRepository(db)
    await repo.delete(UUID(meeting_id))
    return BaseResponse(message="Meeting deleted successfully")
