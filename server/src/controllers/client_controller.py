from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.client_repository import ClientRepository
from src.repositories.workspace_repository import WorkspaceRepository
from src.schemas.base_response import BaseResponse
from src.services.client_service import ClientService


class ClientController:
    def __init__(self, db: AsyncSession) -> None:
        self.service = ClientService(
            db=db,
            repo=ClientRepository(db),
            workspace_repo=WorkspaceRepository(db),
        )

    async def get_by_id(self, client_id: UUID) -> BaseResponse:
        data = await self.service.get_by_id(client_id)
        if data is None:
            return BaseResponse(success=False, message="Client not found", data=None)
        return BaseResponse(data=data)
