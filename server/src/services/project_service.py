from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions.base import BaseAPIException
from src.repositories.client_repository import ClientRepository
from src.models.workspace_member import MemberRole
from src.repositories.client_member_repository import ClientMemberRepository
from src.repositories.project_member_repository import ProjectMemberRepository
from src.repositories.project_repository import ProjectRepository
from src.schemas.project_schema import ProjectResponse


class ProjectService:
    def __init__(
        self,
        db: AsyncSession,
        repo: ProjectRepository,
        client_repo: ClientRepository,
    ) -> None:
        self.db = db
        self.repo = repo
        self.client_repo = client_repo
        self.project_member_repo = ProjectMemberRepository(db)
        self.client_member_repo = ClientMemberRepository(db)

    async def create(
        self, client_id: str, name: str, description: str | None = None, user_id: UUID | None = None
    ) -> dict:
        from src.services.membership_service import MembershipService
        cl_id = UUID(client_id)
        client = await self.client_repo.get_by_id(cl_id)
        if client is None:
            raise BaseAPIException(
                message="Client not found",
                status_code=404,
            )

        if user_id:
            await MembershipService(self.db).assert_workspace_access(client.workspace_id, user_id)

        project = await self.repo.create(cl_id, name, description)
        if user_id:
            await self.project_member_repo.create(project.id, user_id, role=MemberRole.OWNER)
            await self.client_member_repo.create(cl_id, user_id)
        await self.db.commit()
        return ProjectResponse.model_validate(project).model_dump()

    async def get_by_id(self, project_id: UUID) -> dict | None:
        project = await self.repo.get_by_id(project_id)
        if project is None:
            return None
        return ProjectResponse.model_validate(project).model_dump()

    async def list(self, client_id: UUID | None = None, user_id: UUID | None = None, limit: int = 50, offset: int = 0) -> list[dict]:
        if user_id:
            projects = await self.repo.list_by_user_id(user_id, client_id, limit=limit, offset=offset)
        else:
            projects = await self.repo.list(client_id, limit=limit, offset=offset)
        return [ProjectResponse.model_validate(p).model_dump() for p in projects]
