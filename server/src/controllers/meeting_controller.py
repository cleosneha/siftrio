from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.schemas.base_response import BaseResponse
from src.schemas.meeting_schema import MeetingCreate
from src.services.meeting_service import MeetingService


class MeetingController:
    def __init__(self, db: AsyncSession) -> None:
        self.service = MeetingService(db)

    async def create(self, body: MeetingCreate) -> BaseResponse:
        data = await self.service.create(
            client_id=body.client_id,
            project_id=body.project_id,
            title=body.title,
            meeting_type=body.meeting_type,
            tags=body.tags,
            meeting_date=body.meeting_date,
        )
        return BaseResponse(message="Meeting created successfully", data=data)

    async def get_by_id(self, meeting_id: str) -> BaseResponse:
        data = await self.service.get_by_id(UUID(meeting_id))
        if data is None:
            return BaseResponse(success=False, message="Meeting not found", data=None)
        return BaseResponse(data=data)

    async def list_by_client(self, client_id: str) -> BaseResponse:
        data = await self.service.list_by_client(UUID(client_id))
        return BaseResponse(data=data)

    async def list_by_project(self, project_id: str) -> BaseResponse:
        data = await self.service.list_by_project(UUID(project_id))
        return BaseResponse(data=data)

    async def list_miscellaneous(self, client_id: str) -> BaseResponse:
        data = await self.service.list_miscellaneous_by_client(UUID(client_id))
        return BaseResponse(data=data)

    async def delete(self, meeting_id: str) -> BaseResponse:
        await self.service.delete(UUID(meeting_id))
        return BaseResponse(message="Meeting deleted successfully")
