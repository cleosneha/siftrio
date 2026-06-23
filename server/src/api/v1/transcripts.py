from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from src.controllers.transcript_controller import TranscriptController
from src.core.database import get_db
from src.schemas.base_response import BaseResponse

router = APIRouter(prefix="/transcripts", tags=["transcripts"])


@router.post("/{meeting_id}", response_model=BaseResponse)
async def upload_transcript(
    meeting_id: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    controller = TranscriptController(db)
    return await controller.upload(meeting_id, file)
