from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, File, Request, UploadFile
from starlette.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.middleware.auth import require_authenticated_user
from src.middleware.rbac import require_client_role, require_project_role
from src.models.base import MemberRole
from src.repositories.meeting_repository import MeetingRepository
from src.schemas.base_response import BaseResponse
from src.services.ingestion_service import run_ingestion_pipeline

router = APIRouter(
    prefix="/transcripts",
    tags=["transcripts"],
    dependencies=[Depends(require_authenticated_user)],
)


@router.post("/{meeting_id}", response_model=BaseResponse)
async def upload_transcript(
    meeting_id: UUID,
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    if not file.filename or not file.filename.endswith(".txt"):
        return BaseResponse(
            success=False,
            message="Only .txt files are supported",
            data=None,
        )

    content = await file.read()
    transcript_text = content.decode("utf-8")

    user_id = UUID(request.state.user.id)
    from src.services.membership_service import MembershipService
    await MembershipService(db).assert_workspace_boundary("meeting", meeting_id, user_id)

    meeting = await MeetingRepository(db).get_by_id(meeting_id)
    if meeting is None:
        return BaseResponse(
            success=False,
            message="Meeting not found",
            data=None,
        )

    if meeting.project_id:
        await require_project_role(MemberRole.MEMBER)(meeting.project_id, request, db)
    else:
        await require_client_role(MemberRole.MEMBER)(meeting.client_id, request, db)

    result = await db.execute(
        text("""
            UPDATE meetings
            SET transcript_status = 'processing'
            WHERE id = :mid
              AND (transcript_status IS NULL OR transcript_status IN ('pending', 'failed'))
            RETURNING id
        """),
        {"mid": meeting_id},
    )
    if not result.fetchone():
        return BaseResponse(
            success=False,
            message="Meeting is already processing or has a completed transcript",
            data=None,
        )

    await db.commit()

    background_tasks.add_task(run_ingestion_pipeline, meeting_id, transcript_text)

    return JSONResponse(
        content=BaseResponse(
            message="Transcript processing started",
            data={"meeting_id": str(meeting_id), "status": "processing"},
        ).model_dump(),
        status_code=202,
    )
