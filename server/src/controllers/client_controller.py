from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.base_response import BaseResponse
from src.services.client_service import ClientService


class ClientController:
    def __init__(self, db: AsyncSession) -> None:
        self.service = ClientService(db)

    async def get_by_id(self, client_id: str) -> BaseResponse:
        data = await self.service.get_by_id(UUID(client_id))
        if data is None:
            return BaseResponse(success=False, message="Client not found", data=None)
        return BaseResponse(data=data)
