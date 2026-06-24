from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.controllers.project_controller import ProjectController
from src.core.database import get_db
from src.middlewares.auth import require_authenticated_user
from src.schemas.base_response import BaseResponse
from src.schemas.project_schema import ProjectCreate
from src.services.project_service import ProjectService

router = APIRouter(
    prefix="/projects",
    tags=["projects"],
    dependencies=[Depends(require_authenticated_user)],
)


@router.post("", response_model=BaseResponse)
async def create_project(body: ProjectCreate, db: AsyncSession = Depends(get_db)) -> BaseResponse:
    service = ProjectService(db)
    data = await service.create(body.client_id, body.name, body.description)
    return BaseResponse(message="Project created successfully", data=data)


@router.get("", response_model=BaseResponse)
async def list_projects(
    client_id: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    service = ProjectService(db)
    cl_id = UUID(client_id) if client_id else None
    data = await service.list(cl_id)
    return BaseResponse(data=data)


@router.get("/{project_id}", response_model=BaseResponse)
async def get_project(project_id: str, db: AsyncSession = Depends(get_db)) -> BaseResponse:
    controller = ProjectController(db)
    return await controller.get_by_id(project_id)
