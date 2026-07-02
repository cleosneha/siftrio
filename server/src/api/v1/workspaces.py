import logging
from uuid import UUID

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

from src.core.database import get_db
from src.middlewares.auth import require_authenticated_user
from src.repositories.workspace_repository import WorkspaceRepository
from src.schemas.base_response import BaseResponse
from src.schemas.workspace_schema import WorkspaceCreate, WorkspaceResponse

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
    data = WorkspaceResponse(
        id=workspace.id,
        name=workspace.name,
        description=workspace.description,
        created_by=workspace.created_by,
        created_at=workspace.created_at,
        updated_at=workspace.updated_at,
    ).model_dump()
    return BaseResponse(message="Workspace created successfully", data=data)


@router.get("", response_model=BaseResponse)
async def list_workspaces(db: AsyncSession = Depends(get_db)) -> BaseResponse:
    repo = WorkspaceRepository(db)
    workspaces = await repo.list()
    data = [
        WorkspaceResponse(
            id=w.id,
            name=w.name,
            description=w.description,
            created_by=w.created_by,
            created_at=w.created_at,
            updated_at=w.updated_at,
        ).model_dump()
        for w in workspaces
    ]
    return BaseResponse(data=data)


@router.get("/{workspace_id}", response_model=BaseResponse)
async def get_workspace(
    workspace_id: str,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    repo = WorkspaceRepository(db)
    workspace = await repo.get_by_id(UUID(workspace_id))
    if workspace is None:
        return BaseResponse(success=False, message="Workspace not found", data=None)
    data = WorkspaceResponse(
        id=workspace.id,
        name=workspace.name,
        description=workspace.description,
        created_by=workspace.created_by,
        created_at=workspace.created_at,
        updated_at=workspace.updated_at,
    ).model_dump()
    return BaseResponse(data=data)
