from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.controllers.workspace_controller import WorkspaceController
from src.core.database import get_db
from src.schemas.base_response import BaseResponse
from src.schemas.workspace_schema import WorkspaceCreate

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


@router.post("", response_model=BaseResponse)
async def create_workspace(body: WorkspaceCreate, db: AsyncSession = Depends(get_db)) -> BaseResponse:
    controller = WorkspaceController(db)
    return await controller.create(body)


@router.get("", response_model=BaseResponse)
async def list_workspaces(db: AsyncSession = Depends(get_db)) -> BaseResponse:
    controller = WorkspaceController(db)
    return await controller.list()


@router.get("/{workspace_id}", response_model=BaseResponse)
async def get_workspace(workspace_id: str, db: AsyncSession = Depends(get_db)) -> BaseResponse:
    controller = WorkspaceController(db)
    return await controller.get_by_id(workspace_id)
