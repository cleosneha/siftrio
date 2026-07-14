from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.project_member import ProjectMember
from src.models.workspace_member import MemberRole


class ProjectMemberRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create(
        self, project_id: UUID, user_id: UUID, role: MemberRole = MemberRole.MEMBER
    ) -> ProjectMember:
        existing = await self.get_by_user_and_project(project_id, user_id)
        if existing:
            return existing
        member = ProjectMember(project_id=project_id, user_id=user_id, role=role)
        self._db.add(member)
        await self._db.flush()
        await self._db.refresh(member)
        return member

    async def get_by_project(self, project_id: UUID) -> list[ProjectMember]:
        result = await self._db.execute(
            select(ProjectMember)
            .options(selectinload(ProjectMember.user))
            .where(ProjectMember.project_id == project_id)
        )
        return list(result.scalars().all())

    async def get_by_user_and_project(
        self, project_id: UUID, user_id: UUID
    ) -> ProjectMember | None:
        result = await self._db.execute(
            select(ProjectMember).where(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def delete(self, project_id: UUID, user_id: UUID) -> None:
        await self._db.execute(
            delete(ProjectMember).where(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == user_id,
            )
        )
