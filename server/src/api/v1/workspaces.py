from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

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
async def create_workspace(body: WorkspaceCreate, db: AsyncSession = Depends(get_db)) -> BaseResponse:
    repo = WorkspaceRepository(db)
    workspace = await repo.create(body.name, body.description)
    data = WorkspaceResponse(
        id=str(workspace.id),
        name=workspace.name,
        description=workspace.description,
        created_at=workspace.created_at.isoformat() if workspace.created_at else None,
        updated_at=workspace.updated_at.isoformat() if workspace.updated_at else None,
    ).model_dump()
    return BaseResponse(message="Workspace created successfully", data=data)


@router.get("", response_model=BaseResponse)
async def list_workspaces(db: AsyncSession = Depends(get_db)) -> BaseResponse:
    repo = WorkspaceRepository(db)
    workspaces = await repo.list()
    data = [
        WorkspaceResponse(
            id=str(w.id),
            name=w.name,
            description=w.description,
            created_at=w.created_at.isoformat() if w.created_at else None,
            updated_at=w.updated_at.isoformat() if w.updated_at else None,
        ).model_dump()
        for w in workspaces
    ]
    return BaseResponse(data=data)


@router.get("/{workspace_id}", response_model=BaseResponse)
async def get_workspace(workspace_id: str, db: AsyncSession = Depends(get_db)) -> BaseResponse:
    repo = WorkspaceRepository(db)
    workspace = await repo.get_by_id(UUID(workspace_id))
    if workspace is None:
        return BaseResponse(success=False, message="Workspace not found", data=None)
    data = WorkspaceResponse(
        id=str(workspace.id),
        name=workspace.name,
        description=workspace.description,
        created_at=workspace.created_at.isoformat() if workspace.created_at else None,
        updated_at=workspace.updated_at.isoformat() if workspace.updated_at else None,
    ).model_dump()
    return BaseResponse(data=data)
