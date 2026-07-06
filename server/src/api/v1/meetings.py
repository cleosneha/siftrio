from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import async_session_factory, get_db
from src.utils.uuid_validator import parse_optional_uuid
from src.middlewares.auth import require_authenticated_user
from src.repositories.auth_repository import AuthRepository
from src.repositories.client_repository import ClientRepository
from src.repositories.meeting_repository import MeetingRepository
from src.repositories.project_repository import ProjectRepository
from src.schemas.base_response import BaseResponse
from src.schemas.meeting_schema import (
    MeetingCreate,
    MeetingResponse,
    TranscriptStatusResponse,
)
from src.core.embeddings import embedder
from src.services.auth_service import AuthService
from src.services.fireflies_service import FirefliesService
from src.services.meeting_integration_service import MeetingIntegrationService
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
    from src.services.membership_service import MembershipService
    user_id = UUID(request.state.user.id) if request.state.user else None
    membership = MembershipService(db)
    if body.project_id:
        await membership.assert_project_access(UUID(body.project_id), user_id)
    elif body.client_id:
        await membership.assert_client_access(UUID(body.client_id), user_id)

    auth_service = AuthService(AuthRepository(db))
    integration_service = MeetingIntegrationService(db, auth_service=auth_service)
    service = MeetingService(
        db=db,
        repo=MeetingRepository(db),
        client_repo=ClientRepository(db),
        project_repo=ProjectRepository(db),
        integration_service=integration_service,
    )
    user_email = request.state.user.email if request.state.user else None
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
        user_email=user_email,
        guest_emails=body.guest_emails,
    )
    return BaseResponse(message="Meeting created successfully", data=data)


@router.get("/{meeting_id}", response_model=BaseResponse)
async def get_meeting(
    meeting_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    meeting = await MeetingRepository(db).get_by_id(meeting_id)
    if meeting is None:
        return BaseResponse(success=False, message="Meeting not found", data=None)
    user_id = UUID(request.state.user.id)
    from src.services.membership_service import MembershipService
    await MembershipService(db).assert_meeting_access(meeting, user_id)
    data = MeetingResponse.model_validate(meeting).model_dump()
    return BaseResponse(data=data)


@router.get("", response_model=BaseResponse)
async def list_meetings(
    request: Request,
    client_id: str | None = Query(None),
    project_id: str | None = Query(None),
    miscellaneous: bool = False,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    repo = MeetingRepository(db)
    user_id = UUID(request.state.user.id)
    from src.services.membership_service import MembershipService
    membership = MembershipService(db)

    cl_id = parse_optional_uuid(client_id, "client_id") if client_id else None
    pr_id = parse_optional_uuid(project_id, "project_id") if project_id else None

    if pr_id:
        await membership.assert_project_access(pr_id, user_id)
        meetings = await repo.list_by_project(pr_id, limit=limit, offset=offset)
    elif miscellaneous and cl_id:
        await membership.assert_client_access(cl_id, user_id)
        meetings = await repo.list_miscellaneous_by_client(cl_id, limit=limit, offset=offset)
    elif cl_id:
        await membership.assert_client_access(cl_id, user_id)
        meetings = await repo.list_by_client(cl_id, limit=limit, offset=offset)
    else:
        return BaseResponse(data=[])

    data = [MeetingResponse.model_validate(m).model_dump() for m in meetings]
    return BaseResponse(data=data)


@router.get("/{meeting_id}/transcript-status", response_model=BaseResponse)
async def get_transcript_status(
    meeting_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    meeting = await MeetingRepository(db).get_by_id(meeting_id)
    if meeting is None:
        return BaseResponse(success=False, message="Meeting not found", data=None)
    user_id = UUID(request.state.user.id)
    from src.services.membership_service import MembershipService
    await MembershipService(db).assert_meeting_access(meeting, user_id)
    return BaseResponse(
        data=TranscriptStatusResponse(
            transcript_status=meeting.transcript_status if meeting.transcript_status else None,
            fireflies_meeting_id=meeting.fireflies_meeting_id,
        ).model_dump()
    )


@router.post("/{meeting_id}/retry-transcript", response_model=BaseResponse)
async def retry_transcript(
    meeting_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    meeting = await MeetingRepository(db).get_by_id(meeting_id)
    if meeting is None:
        return BaseResponse(success=False, message="Meeting not found", data=None)
    user_id = UUID(request.state.user.id)
    from src.services.membership_service import MembershipService
    await MembershipService(db).assert_meeting_access(meeting, user_id)

    if not meeting.fireflies_meeting_id:
        return BaseResponse(
            success=False,
            message="No Fireflies meeting ID associated with this meeting",
            data=None,
        )

    try:
        async with async_session_factory() as session:
            fireflies_service = FirefliesService(session, MeetingRepository(session), embedder)
            result = await fireflies_service.process_transcript(meeting.fireflies_meeting_id)
        return BaseResponse(
            message="Transcript retrieved and processed successfully",
            data=result,
        )
    except Exception as e:
        return BaseResponse(
            success=False,
            message=f"Failed to retrieve transcript: {e}",
            data=None,
        )


@router.delete("/{meeting_id}", response_model=BaseResponse)
async def delete_meeting(
    meeting_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    meeting = await MeetingRepository(db).get_by_id(meeting_id)
    if meeting is None:
        return BaseResponse(success=False, message="Meeting not found", data=None)
    user_id = UUID(request.state.user.id)
    from src.services.membership_service import MembershipService
    await MembershipService(db).assert_meeting_access(meeting, user_id)
    repo = MeetingRepository(db)
    await repo.delete(meeting_id)
    await db.commit()
    return BaseResponse(message="Meeting deleted successfully")
