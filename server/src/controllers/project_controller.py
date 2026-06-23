from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.schemas.base_response import BaseResponse
from src.schemas.project_schema import ProjectCreate
from src.services.project_service import ProjectService


class ProjectController:
    def __init__(self, db: AsyncSession) -> None:
        self.service = ProjectService(db)

    async def create(self, body: ProjectCreate) -> BaseResponse:
        data = await self.service.create(body.client_id, body.name, body.description)
        return BaseResponse(message="Project created successfully", data=data)

    async def get_by_id(self, project_id: str) -> BaseResponse:
        data = await self.service.get_by_id(UUID(project_id))
        if data is None:
            return BaseResponse(success=False, message="Project not found", data=None)
        return BaseResponse(data=data)

    async def list(self, client_id: str | None = None) -> BaseResponse:
        cl_id = UUID(client_id) if client_id else None
        data = await self.service.list(cl_id)
        return BaseResponse(data=data)
