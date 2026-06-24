from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.base_response import BaseResponse
from src.services.project_service import ProjectService


class ProjectController:
    def __init__(self, db: AsyncSession) -> None:
        self.service = ProjectService(db)

    async def get_by_id(self, project_id: str) -> BaseResponse:
        data = await self.service.get_by_id(UUID(project_id))
        if data is None:
            return BaseResponse(success=False, message="Project not found", data=None)
        return BaseResponse(data=data)
