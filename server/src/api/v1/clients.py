from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import get_db
from src.middleware.auth import require_authenticated_user
from src.middleware.rbac import require_client_role, require_workspace_role
from src.models.base import MemberRole
from src.repositories.client_repository import ClientRepository
from src.repositories.workspace_repository import WorkspaceRepository
from src.schemas.base_response import BaseResponse
from src.schemas.client_schema import ClientCreate, ClientResponse, ClientUpdate
from src.services.client_service import ClientService
from src.services.membership_service import MembershipService
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
    await MembershipService(db).assert_workspace_boundary("workspace", body.workspace_id, user_id)
    await require_workspace_role(MemberRole.ADMIN)(body.workspace_id, request, db)
    service = ClientService(db, ClientRepository(db), WorkspaceRepository(db))
    data = await service.create(body.workspace_id, body.name, body.description, user_id=user_id)
    return BaseResponse(message="Client created successfully", data=data)


@router.get("", response_model=BaseResponse)
async def list_clients(
    request: Request,
    workspace_id: str | None = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    service = ClientService(db, ClientRepository(db), WorkspaceRepository(db))
    user_id = UUID(request.state.user.id)
    ws_id = parse_optional_uuid(workspace_id, "workspace_id") if workspace_id else None
    data = await service.list(ws_id, user_id=user_id, limit=limit, offset=offset)
    return BaseResponse(data=data)


@router.get("/{client_id}", response_model=BaseResponse)
async def get_client(
    client_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    user_id = UUID(request.state.user.id)
    await MembershipService(db).assert_workspace_boundary("client", client_id, user_id)
    service = ClientService(db, ClientRepository(db), WorkspaceRepository(db))
    data = await service.get_by_id(client_id)
    if data is None:
        return BaseResponse(success=False, message="Client not found", data=None)
    return BaseResponse(data=data)


@router.patch("/{client_id}", response_model=BaseResponse)
async def update_client(
    client_id: UUID,
    body: ClientUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    user_id = UUID(request.state.user.id)
    await MembershipService(db).assert_workspace_boundary("client", client_id, user_id)
    await require_client_role(MemberRole.ADMIN)(client_id, request, db)
    repo = ClientRepository(db)
    client = await repo.update(client_id, **body.model_dump(exclude_none=True))
    if client is None:
        return BaseResponse(success=False, message="Client not found", data=None)
    await db.commit()
    return BaseResponse(data=ClientResponse.model_validate(client).model_dump())


@router.delete("/{client_id}", response_model=BaseResponse)
async def delete_client(
    client_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    user_id = UUID(request.state.user.id)
    service = MembershipService(db)
    await service.assert_workspace_boundary("client", client_id, user_id)
    await require_client_role(MemberRole.OWNER)(client_id, request, db)
    await service.delete_client(client_id)
    await db.commit()
    return BaseResponse(message="Client deleted successfully")
