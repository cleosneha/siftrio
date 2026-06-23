from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.schemas.base_response import BaseResponse
from src.schemas.workspace_schema import WorkspaceCreate
from src.services.workspace_service import WorkspaceService


class WorkspaceController:
    def __init__(self, db: AsyncSession) -> None:
        self.service = WorkspaceService(db)

    async def create(self, body: WorkspaceCreate) -> BaseResponse:
        data = await self.service.create(body.name, body.description)
        return BaseResponse(message="Workspace created successfully", data=data)

    async def get_by_id(self, workspace_id: str) -> BaseResponse:
        data = await self.service.get_by_id(UUID(workspace_id))
        if data is None:
            return BaseResponse(success=False, message="Workspace not found", data=None)
        return BaseResponse(data=data)

    async def list(self) -> BaseResponse:
        data = await self.service.list()
        return BaseResponse(data=data)
