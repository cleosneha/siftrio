from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.project_member import ProjectMember
from src.models.base import MemberRole


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

    async def count_by_project(self, project_id: UUID) -> int:
        result = await self._db.execute(
            select(func.count(ProjectMember.id)).where(
                ProjectMember.project_id == project_id
            )
        )
        return result.scalar() or 0

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

    async def list_project_ids_by_user(self, user_id: UUID) -> list[UUID]:
        result = await self._db.execute(
            select(ProjectMember.project_id).where(
                ProjectMember.user_id == user_id
            )
        )
        return [row[0] for row in result.all()]

    async def delete(self, project_id: UUID, user_id: UUID) -> None:
        await self._db.execute(
            delete(ProjectMember).where(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == user_id,
            )
        )
