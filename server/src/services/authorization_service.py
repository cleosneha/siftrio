from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions.base import BaseAPIException
from src.repositories.workspace_repository import WorkspaceRepository


class AuthorizationService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._workspace_repo = WorkspaceRepository(db)

    async def assert_workspace_access(self, workspace_id: UUID, user_id: UUID) -> None:
        workspace = await self._workspace_repo.get_by_id(workspace_id)
        if workspace is None:
            raise BaseAPIException(message="Workspace not found", status_code=404)
        if workspace.created_by != user_id:
            raise BaseAPIException(
                message="You don't have access to this workspace",
                status_code=403,
            )
