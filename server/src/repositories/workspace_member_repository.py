from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.workspace_member import MemberRole, WorkspaceMember


class WorkspaceMemberRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create(
        self, workspace_id: UUID, user_id: UUID, role: MemberRole = MemberRole.MEMBER
    ) -> WorkspaceMember:
        member = WorkspaceMember(workspace_id=workspace_id, user_id=user_id, role=role)
        self._db.add(member)
        await self._db.flush()
        await self._db.refresh(member)
        return member

    async def get_by_workspace(self, workspace_id: UUID) -> list[WorkspaceMember]:
        result = await self._db.execute(
            select(WorkspaceMember)
            .options(selectinload(WorkspaceMember.user))
            .where(WorkspaceMember.workspace_id == workspace_id)
        )
        return list(result.scalars().all())

    async def get_by_user_and_workspace(
        self, workspace_id: UUID, user_id: UUID
    ) -> WorkspaceMember | None:
        result = await self._db.execute(
            select(WorkspaceMember).where(
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def delete(self, workspace_id: UUID, user_id: UUID) -> None:
        await self._db.execute(
            delete(WorkspaceMember).where(
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.user_id == user_id,
            )
        )
