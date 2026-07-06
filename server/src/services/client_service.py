from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions.base import BaseAPIException
from src.repositories.client_repository import ClientRepository
from src.models.workspace_member import MemberRole
from src.repositories.client_member_repository import ClientMemberRepository
from src.repositories.workspace_repository import WorkspaceRepository
from src.schemas.client_schema import ClientResponse


class ClientService:
    def __init__(
        self,
        db: AsyncSession,
        repo: ClientRepository,
        workspace_repo: WorkspaceRepository,
    ) -> None:
        self.db = db
        self.repo = repo
        self.workspace_repo = workspace_repo
        self.client_member_repo = ClientMemberRepository(db)

    async def create(
        self, workspace_id: str, name: str, description: str | None = None, user_id: UUID | None = None
    ) -> dict:
        from src.services.membership_service import MembershipService
        ws_id = UUID(workspace_id)

        if user_id:
            await MembershipService(self.db).assert_workspace_access(ws_id, user_id)

        workspace = await self.workspace_repo.get_by_id(ws_id)
        if workspace is None:
            raise BaseAPIException(
                message="Workspace not found",
                status_code=404,
            )

        client = await self.repo.create(ws_id, name, description)
        if user_id:
            await self.client_member_repo.create(client.id, user_id, role=MemberRole.OWNER)
        await self.db.commit()
        return ClientResponse.model_validate(client).model_dump()

    async def get_by_id(self, client_id: UUID) -> dict | None:
        client = await self.repo.get_by_id(client_id)
        if client is None:
            return None
        project_count = await self.repo.get_project_count(client_id)
        data = ClientResponse.model_validate(client).model_dump()
        data["project_count"] = project_count
        return data

    async def list(self, workspace_id: UUID | None = None, user_id: UUID | None = None, limit: int = 50, offset: int = 0) -> list[dict]:
        if user_id:
            rows = await self.repo.list_with_project_counts_by_user_id(user_id, workspace_id, limit=limit, offset=offset)
        else:
            rows = await self.repo.list_with_project_counts(workspace_id, limit=limit, offset=offset)
        result = []
        for client, project_count in rows:
            data = ClientResponse.model_validate(client).model_dump()
            data["project_count"] = project_count
            result.append(data)
        return result
