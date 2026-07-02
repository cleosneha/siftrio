from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions.base import BaseAPIException
from src.repositories.client_repository import ClientRepository
from src.repositories.workspace_repository import WorkspaceRepository
from src.schemas.client_schema import ClientResponse
from src.services.authorization_service import AuthorizationService


class ClientService:
    def __init__(
        self,
        db: AsyncSession,
        repo: ClientRepository,
        workspace_repo: WorkspaceRepository,
        authorization_service: AuthorizationService | None = None,
    ) -> None:
        self.db = db
        self.repo = repo
        self.workspace_repo = workspace_repo
        self.authorization_service = authorization_service

    async def create(
        self, workspace_id: str, name: str, description: str | None = None, user_id: UUID | None = None
    ) -> dict:
        ws_id = UUID(workspace_id)

        if self.authorization_service and user_id:
            await self.authorization_service.assert_workspace_access(ws_id, user_id)

        workspace = await self.workspace_repo.get_by_id(ws_id)
        if workspace is None:
            raise BaseAPIException(
                message="Workspace not found",
                status_code=404,
            )

        client = await self.repo.create(ws_id, name, description)
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

    async def list(self, workspace_id: UUID | None = None, limit: int = 50, offset: int = 0) -> list[dict]:
        rows = await self.repo.list_with_project_counts(workspace_id, limit=limit, offset=offset)
        result = []
        for client, project_count in rows:
            data = ClientResponse.model_validate(client).model_dump()
            data["project_count"] = project_count
            result.append(data)
        return result
