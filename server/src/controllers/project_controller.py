from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.client_repository import ClientRepository
from src.repositories.project_repository import ProjectRepository
from src.schemas.base_response import BaseResponse
from src.services.project_service import ProjectService


class ProjectController:
    def __init__(self, db: AsyncSession) -> None:
        self.service = ProjectService(
            db=db,
            repo=ProjectRepository(db),
            client_repo=ClientRepository(db),
        )

    async def get_by_id(self, project_id: UUID) -> BaseResponse:
        data = await self.service.get_by_id(project_id)
        if data is None:
            return BaseResponse(success=False, message="Project not found", data=None)
        return BaseResponse(data=data)
