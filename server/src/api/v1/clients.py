from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.controllers.client_controller import ClientController
from src.core.database import get_db
from src.middlewares.auth import require_authenticated_user
from src.repositories.client_repository import ClientRepository
from src.repositories.workspace_repository import WorkspaceRepository
from src.schemas.base_response import BaseResponse
from src.schemas.client_schema import ClientCreate
from src.services.authorization_service import AuthorizationService
from src.services.client_service import ClientService
from src.utils.uuid_validator import parse_optional_uuid

router = APIRouter(
    prefix="/clients",
    tags=["clients"],
    dependencies=[Depends(require_authenticated_user)],
)


@router.post("", response_model=BaseResponse)
async def create_client(
    body: ClientCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    user_id = UUID(request.state.user.id) if request.state.user else None
    authz = AuthorizationService(db)
    service = ClientService(db, ClientRepository(db), WorkspaceRepository(db), authorization_service=authz)
    data = await service.create(body.workspace_id, body.name, body.description, user_id=user_id)
    return BaseResponse(message="Client created successfully", data=data)


@router.get("", response_model=BaseResponse)
async def list_clients(
    workspace_id: str | None = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    service = ClientService(db, ClientRepository(db), WorkspaceRepository(db))
    ws_id = parse_optional_uuid(workspace_id, "workspace_id") if workspace_id else None
    data = await service.list(ws_id, limit=limit, offset=offset)
    return BaseResponse(data=data)


@router.get("/{client_id}", response_model=BaseResponse)
async def get_client(client_id: UUID, db: AsyncSession = Depends(get_db)) -> BaseResponse:
    controller = ClientController(db)
    return await controller.get_by_id(client_id)
