from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions.base import BaseAPIException
from src.repositories.client_repository import ClientRepository
from src.repositories.project_repository import ProjectRepository
from src.schemas.project_schema import ProjectResponse
from src.services.authorization_service import AuthorizationService


class ProjectService:
    def __init__(
        self,
        db: AsyncSession,
        repo: ProjectRepository,
        client_repo: ClientRepository,
        authorization_service: AuthorizationService | None = None,
    ) -> None:
        self.db = db
        self.repo = repo
        self.client_repo = client_repo
        self.authorization_service = authorization_service

    async def create(
        self, client_id: str, name: str, description: str | None = None, user_id: UUID | None = None
    ) -> dict:
        cl_id = UUID(client_id)
        client = await self.client_repo.get_by_id(cl_id)
        if client is None:
            raise BaseAPIException(
                message="Client not found",
                status_code=404,
            )

        if self.authorization_service and user_id:
            await self.authorization_service.assert_workspace_access(client.workspace_id, user_id)

        project = await self.repo.create(cl_id, name, description)
        await self.db.commit()
        return ProjectResponse.model_validate(project).model_dump()

    async def get_by_id(self, project_id: UUID) -> dict | None:
        project = await self.repo.get_by_id(project_id)
        if project is None:
            return None
        return ProjectResponse.model_validate(project).model_dump()

    async def list(self, client_id: UUID | None = None, limit: int = 50, offset: int = 0) -> list[dict]:
        projects = await self.repo.list(client_id, limit=limit, offset=offset)
        return [ProjectResponse.model_validate(p).model_dump() for p in projects]
