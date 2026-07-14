from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import exists, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.client_member import ClientMember
from src.models.project import Project
from src.models.project_member import ProjectMember
from src.models.workspace_member import MemberRole, WorkspaceMember
from src.repositories.client_member_repository import ClientMemberRepository
from src.repositories.project_member_repository import ProjectMemberRepository
from src.repositories.workspace_member_repository import WorkspaceMemberRepository
from src.schemas.membership_schema import MemberResponse


class MembershipService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.ws_member_repo = WorkspaceMemberRepository(db)
        self.client_member_repo = ClientMemberRepository(db)
        self.project_member_repo = ProjectMemberRepository(db)

    async def assert_workspace_access(self, workspace_id: UUID, user_id: UUID) -> None:
        result = await self.db.execute(
            exists(WorkspaceMember).where(
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.user_id == user_id,
            ).select()
        )
        if not result.scalar():
            raise HTTPException(status_code=403, detail="Access denied to this workspace")

    async def assert_client_access(self, client_id: UUID, user_id: UUID) -> None:
        result = await self.db.execute(
            exists().where(
                and_(
                    ClientMember.client_id == client_id,
                    ClientMember.user_id == user_id,
                )
            ).select()
        )
        if result.scalar():
            return
        result = await self.db.execute(
            exists().where(
                and_(
                    ProjectMember.user_id == user_id,
                    Project.id == ProjectMember.project_id,
                    Project.client_id == client_id,
                )
            ).select()
        )
        if not result.scalar():
            raise HTTPException(status_code=403, detail="Access denied to this client")

    async def assert_project_access(self, project_id: UUID, user_id: UUID) -> None:
        result = await self.db.execute(
            exists(ProjectMember).where(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == user_id,
            ).select()
        )
        if not result.scalar():
            raise HTTPException(status_code=403, detail="Access denied to this project")

    async def assert_meeting_access(self, meeting, user_id: UUID) -> None:
        if meeting.project_id:
            await self.assert_project_access(meeting.project_id, user_id)
        else:
            await self.assert_client_access(meeting.client_id, user_id)

    async def list_workspace_members(self, workspace_id: UUID) -> list[dict]:
        members = await self.ws_member_repo.get_by_workspace(workspace_id)
        return [self._to_response(m) for m in members]

    async def list_client_members(self, client_id: UUID) -> list[dict]:
        members = await self.client_member_repo.get_by_client(client_id)
        return [self._to_response(m) for m in members]

    async def list_project_members(self, project_id: UUID) -> list[dict]:
        members = await self.project_member_repo.get_by_project(project_id)
        return [self._to_response(m) for m in members]

    async def remove_workspace_member(self, workspace_id: UUID, user_id: UUID) -> None:
        member = await self.ws_member_repo.get_by_user_and_workspace(workspace_id, user_id)
        if member and member.role == MemberRole.OWNER:
            raise HTTPException(status_code=403, detail="Cannot remove an owner")
        await self.ws_member_repo.delete(workspace_id, user_id)
        await self.db.flush()

    async def remove_client_member(self, client_id: UUID, user_id: UUID) -> None:
        member = await self.client_member_repo.get_by_user_and_client(client_id, user_id)
        if member and member.role == MemberRole.OWNER:
            raise HTTPException(status_code=403, detail="Cannot remove an owner")
        await self.client_member_repo.delete(client_id, user_id)
        await self.db.flush()

    async def remove_project_member(self, project_id: UUID, user_id: UUID) -> None:
        member = await self.project_member_repo.get_by_user_and_project(project_id, user_id)
        if member and member.role == MemberRole.OWNER:
            raise HTTPException(status_code=403, detail="Cannot remove an owner")
        await self.project_member_repo.delete(project_id, user_id)
        await self.db.flush()

    def _to_response(self, member) -> dict:
        data = MemberResponse.model_validate(member).model_dump()
        user = getattr(member, "user", None)
        if user:
            data["email"] = user.email
            data["full_name"] = user.full_name
            data["profile_picture"] = user.profile_picture
        return data
