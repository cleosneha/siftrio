from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.controllers.client_controller import ClientController
from src.core.database import get_db
from src.schemas.base_response import BaseResponse
from src.schemas.client_schema import ClientCreate

router = APIRouter(prefix="/clients", tags=["clients"])


@router.post("", response_model=BaseResponse)
async def create_client(body: ClientCreate, db: AsyncSession = Depends(get_db)) -> BaseResponse:
    controller = ClientController(db)
    return await controller.create(body)


@router.get("", response_model=BaseResponse)
async def list_clients(
    workspace_id: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    controller = ClientController(db)
    return await controller.list(workspace_id)


@router.get("/{client_id}", response_model=BaseResponse)
async def get_client(client_id: str, db: AsyncSession = Depends(get_db)) -> BaseResponse:
    controller = ClientController(db)
    return await controller.get_by_id(client_id)
