from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import get_db
from src.middleware.auth import require_authenticated_user
from src.repositories.client_repository import ClientRepository
from src.repositories.project_repository import ProjectRepository
from src.schemas.base_response import BaseResponse
from src.schemas.project_schema import ProjectCreate
from src.services.membership_service import MembershipService
from src.services.project_service import ProjectService
from src.utils.uuid_validator import parse_optional_uuid


router = APIRouter(
    prefix="/projects",
    tags=["projects"],
    dependencies=[Depends(require_authenticated_user)],
)


@router.post("", response_model=BaseResponse)
async def create_project(
    body: ProjectCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    user_id = UUID(request.state.user.id) if request.state.user else None
    service = ProjectService(db, ProjectRepository(db), ClientRepository(db))
    data = await service.create(body.client_id, body.name, body.description, user_id=user_id)
    return BaseResponse(message="Project created successfully", data=data)


@router.get("", response_model=BaseResponse)
async def list_projects(
    request: Request,
    client_id: str | None = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    service = ProjectService(db, ProjectRepository(db), ClientRepository(db))
    user_id = UUID(request.state.user.id)
    cl_id = parse_optional_uuid(client_id, "client_id") if client_id else None
    data = await service.list(cl_id, user_id=user_id, limit=limit, offset=offset)
    return BaseResponse(data=data)


@router.get("/{project_id}", response_model=BaseResponse)
async def get_project(
    project_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    user_id = UUID(request.state.user.id)
    await MembershipService(db).assert_project_access(project_id, user_id)
    service = ProjectService(db, ProjectRepository(db), ClientRepository(db))
    data = await service.get_by_id(project_id)
    if data is None:
        return BaseResponse(success=False, message="Project not found", data=None)
    return BaseResponse(data=data)
