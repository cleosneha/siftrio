import logging
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

from src.core.database import get_db
from src.middlewares.auth import require_authenticated_user
from src.repositories.workspace_repository import WorkspaceRepository
from src.schemas.base_response import BaseResponse
from src.schemas.workspace_schema import WorkspaceCreate, WorkspaceResponse
from src.utils.uuid_validator import validate_uuid_path

router = APIRouter(
    prefix="/workspaces",
    tags=["workspaces"],
    dependencies=[Depends(require_authenticated_user)],
)


@router.post("", response_model=BaseResponse)
async def create_workspace(
    body: WorkspaceCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    repo = WorkspaceRepository(db)
    user_id = UUID(request.state.user.id)
    workspace = await repo.create(body.name, body.description, created_by=user_id)
    await db.commit()
    data = WorkspaceResponse.model_validate(workspace).model_dump()
    return BaseResponse(message="Workspace created successfully", data=data)


@router.get("", response_model=BaseResponse)
async def list_workspaces(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    repo = WorkspaceRepository(db)
    workspaces = await repo.list(limit=limit, offset=offset)
    data = [WorkspaceResponse.model_validate(w).model_dump() for w in workspaces]
    return BaseResponse(data=data)


@router.get("/{workspace_id}", response_model=BaseResponse)
async def get_workspace(
    workspace_id: UUID = Depends(validate_uuid_path),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    repo = WorkspaceRepository(db)
    workspace = await repo.get_by_id(workspace_id)
    if workspace is None:
        return BaseResponse(success=False, message="Workspace not found", data=None)
    data = WorkspaceResponse.model_validate(workspace).model_dump()
    return BaseResponse(data=data)
