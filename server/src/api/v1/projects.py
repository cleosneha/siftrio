from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.controllers.project_controller import ProjectController
from src.core.database import get_db
from src.schemas.base_response import BaseResponse
from src.schemas.project_schema import ProjectCreate

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=BaseResponse)
async def create_project(body: ProjectCreate, db: AsyncSession = Depends(get_db)) -> BaseResponse:
    controller = ProjectController(db)
    return await controller.create(body)


@router.get("", response_model=BaseResponse)
async def list_projects(
    client_id: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    controller = ProjectController(db)
    return await controller.list(client_id)


@router.get("/{project_id}", response_model=BaseResponse)
async def get_project(project_id: str, db: AsyncSession = Depends(get_db)) -> BaseResponse:
    controller = ProjectController(db)
    return await controller.get_by_id(project_id)
