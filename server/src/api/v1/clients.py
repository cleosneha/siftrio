from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.controllers.client_controller import ClientController
from src.core.database import get_db
from src.middlewares.auth import require_authenticated_user
from src.schemas.base_response import BaseResponse
from src.schemas.client_schema import ClientCreate
from src.services.client_service import ClientService

router = APIRouter(
    prefix="/clients",
    tags=["clients"],
    dependencies=[Depends(require_authenticated_user)],
)


@router.post("", response_model=BaseResponse)
async def create_client(body: ClientCreate, db: AsyncSession = Depends(get_db)) -> BaseResponse:
    service = ClientService(db)
    data = await service.create(body.workspace_id, body.name, body.description)
    return BaseResponse(message="Client created successfully", data=data)


@router.get("", response_model=BaseResponse)
async def list_clients(
    workspace_id: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    service = ClientService(db)
    ws_id = UUID(workspace_id) if workspace_id else None
    data = await service.list(ws_id)
    return BaseResponse(data=data)


@router.get("/{client_id}", response_model=BaseResponse)
async def get_client(client_id: str, db: AsyncSession = Depends(get_db)) -> BaseResponse:
    controller = ClientController(db)
    return await controller.get_by_id(client_id)
