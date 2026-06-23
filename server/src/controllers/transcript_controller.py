from uuid import UUID

from fastapi import Depends, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.schemas.base_response import BaseResponse
from src.services.transcript_service import TranscriptService


class TranscriptController:
    def __init__(self, db: AsyncSession) -> None:
        self.service = TranscriptService(db)

    async def upload(self, meeting_id: str, file: UploadFile) -> BaseResponse:
        if not file.filename or not file.filename.endswith(".txt"):
            return BaseResponse(
                success=False,
                message="Only .txt files are supported",
                data=None,
            )
        content = await file.read()
        transcript_text = content.decode("utf-8")
        data = await self.service.process_upload(UUID(meeting_id), transcript_text)
        return BaseResponse(message="Transcript processed successfully", data=data)
