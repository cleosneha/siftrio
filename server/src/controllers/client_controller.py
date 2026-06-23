from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.schemas.base_response import BaseResponse
from src.schemas.client_schema import ClientCreate
from src.services.client_service import ClientService


class ClientController:
    def __init__(self, db: AsyncSession) -> None:
        self.service = ClientService(db)

    async def create(self, body: ClientCreate) -> BaseResponse:
        data = await self.service.create(body.workspace_id, body.name, body.description)
        return BaseResponse(message="Client created successfully", data=data)

    async def get_by_id(self, client_id: str) -> BaseResponse:
        data = await self.service.get_by_id(UUID(client_id))
        if data is None:
            return BaseResponse(success=False, message="Client not found", data=None)
        return BaseResponse(data=data)

    async def list(self, workspace_id: str | None = None) -> BaseResponse:
        ws_id = UUID(workspace_id) if workspace_id else None
        data = await self.service.list(ws_id)
        return BaseResponse(data=data)
