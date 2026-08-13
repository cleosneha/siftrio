from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import delete, exists, and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.client import Client
from src.models.client_member import ClientMember
from src.models.project import Project
from src.models.project_member import ProjectMember
from src.models.workspace import Workspace
from src.models.base import MemberRole, rank
from src.models.workspace_member import WorkspaceMember
from src.repositories.client_member_repository import ClientMemberRepository
from src.repositories.client_repository import ClientRepository
from src.repositories.project_member_repository import ProjectMemberRepository
from src.repositories.project_repository import ProjectRepository
from src.repositories.resource_repository import ResourceRepository
from src.repositories.workspace_member_repository import WorkspaceMemberRepository
from src.schemas.membership_schema import MemberResponse
from src.services.audit_service import AuditService


class MembershipService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.ws_member_repo = WorkspaceMemberRepository(db)
        self.client_member_repo = ClientMemberRepository(db)
        self.project_member_repo = ProjectMemberRepository(db)
        self.client_repo = ClientRepository(db)
        self.project_repo = ProjectRepository(db)
        self.resource_repo = ResourceRepository(db)

    async def assert_workspace_boundary(
        self, resource_type: str, resource_id: UUID, user_id: UUID
    ) -> None:
        workspace_id = await self.resource_repo.get_workspace_id(resource_type, resource_id)
        if workspace_id is None:
            raise HTTPException(status_code=404, detail="Resource not found")
        member = await self.ws_member_repo.get_by_user_and_workspace(workspace_id, user_id)
        if member is None:
            raise HTTPException(status_code=404, detail="Access denied to this resource")

    async def get_accessible_project_ids(self, user_id: UUID) -> list[UUID]:
        rows = await self.db.execute(
            select(Project.id)
            .join(Client, Client.id == Project.client_id)
            .where(
                Client.workspace_id.in_(
                    select(WorkspaceMember.workspace_id).where(
                        WorkspaceMember.user_id == user_id
                    )
                )
            )
            .distinct()
        )
        return list(rows.scalars().all())

    async def get_visible_project_ids(
        self, user_id: UUID, workspace_id: UUID
    ) -> list[UUID]:
        """Projects whose content a user may retrieve in this workspace (§8.8)."""
        ws_role = await self.ws_member_repo.get_by_user_and_workspace(
            workspace_id, user_id
        )
        if ws_role is not None:
            all_projects = await self.project_repo.list_by_workspace(workspace_id)
            return [p.id for p in all_projects]

        visible: set[UUID] = set()
        for cm in await self.client_member_repo.list_by_user(workspace_id, user_id):
            for p in await self.project_repo.list(client_id=cm.client_id):
                visible.add(p.id)
        for pm in await self.project_member_repo.list_by_workspace(
            workspace_id, user_id
        ):
            visible.add(pm.project_id)
        return list(visible)

    async def get_visible_client_ids(
        self, user_id: UUID, workspace_id: UUID
    ) -> list[UUID]:
        """Clients whose content (incl. client-level meetings) a user may retrieve."""
        ws_role = await self.ws_member_repo.get_by_user_and_workspace(
            workspace_id, user_id
        )
        if ws_role is not None:
            return await self.client_repo.list_ids_by_workspace(workspace_id)

        visible: set[UUID] = set()
        for cm in await self.client_member_repo.list_by_user(workspace_id, user_id):
            visible.add(cm.client_id)
        for pm in await self.project_member_repo.list_by_workspace(
            workspace_id, user_id
        ):
            project = await self.project_repo.get_by_id(pm.project_id)
            if project:
                visible.add(project.client_id)
        return list(visible)

    async def get_effective_role(
        self, level: str, resource_id: UUID, user_id: UUID
    ) -> MemberRole | None:
        """Highest role the user holds on the resource chain up to the workspace root."""
        roles: list[MemberRole | None] = []
        if level == "workspace":
            m = await self.ws_member_repo.get_by_user_and_workspace(resource_id, user_id)
            roles.append(m.role if m else None)
        elif level == "client":
            m = await self.client_member_repo.get_by_user_and_client(resource_id, user_id)
            roles.append(m.role if m else None)
            client = await self.client_repo.get_by_id(resource_id)
            if client:
                wm = await self.ws_member_repo.get_by_user_and_workspace(client.workspace_id, user_id)
                roles.append(wm.role if wm else None)
        elif level == "project":
            m = await self.project_member_repo.get_by_user_and_project(resource_id, user_id)
            roles.append(m.role if m else None)
            project = await self.project_repo.get_by_id(resource_id)
            if project:
                roles.append(await self.get_effective_role("client", project.client_id, user_id))
        return max(roles, key=rank, default=None)

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

    async def remove_workspace_member(
        self, workspace_id: UUID, user_id: UUID, actor_user_id: UUID
    ) -> None:
        member = await self.ws_member_repo.get_by_user_and_workspace(workspace_id, user_id)
        if member is None:
            return
        if member.role == MemberRole.OWNER:
            await self._assert_owner_removal(
                "workspace", workspace_id, user_id, actor_user_id
            )

        member_count = await self.ws_member_repo.count_by_workspace(workspace_id)
        await self.ws_member_repo.delete(workspace_id, user_id)

        if member_count <= 1:
            await self._delete_workspace_cascade(workspace_id)
        else:
            AuditService(self.db).record(
                workspace_id=workspace_id,
                action="member.removed",
                resource_type="workspace",
                resource_id=workspace_id,
                actor_user_id=actor_user_id,
                new_value={"role": member.role.value, "user_id": str(user_id)},
            )
            await self.db.flush()

    async def remove_client_member(
        self, client_id: UUID, user_id: UUID, actor_user_id: UUID
    ) -> None:
        member = await self.client_member_repo.get_by_user_and_client(client_id, user_id)
        if member is None:
            return
        if member.role == MemberRole.OWNER:
            await self._assert_owner_removal(
                "client", client_id, user_id, actor_user_id
            )

        member_count = await self.client_member_repo.count_by_client(client_id)
        ws_id = await self.resource_repo.get_workspace_id("client", client_id)
        await self.client_member_repo.delete(client_id, user_id)

        if member_count <= 1:
            await self._delete_client_cascade(client_id)
        else:
            await self.db.flush()

        if ws_id is not None:
            AuditService(self.db).record(
                workspace_id=ws_id,
                action="member.removed",
                resource_type="client",
                resource_id=client_id,
                actor_user_id=actor_user_id,
                new_value={"role": member.role.value, "user_id": str(user_id)},
            )
            await self.db.flush()

    async def remove_project_member(
        self, project_id: UUID, user_id: UUID, actor_user_id: UUID
    ) -> None:
        member = await self.project_member_repo.get_by_user_and_project(project_id, user_id)
        if member is None:
            return
        if member.role == MemberRole.OWNER:
            await self._assert_owner_removal(
                "project", project_id, user_id, actor_user_id
            )

        member_count = await self.project_member_repo.count_by_project(project_id)
        ws_id = await self.resource_repo.get_workspace_id("project", project_id)
        await self.project_member_repo.delete(project_id, user_id)

        if member_count <= 1:
            await self._delete_project_cascade(project_id)
        else:
            await self.db.flush()

        if ws_id is not None:
            AuditService(self.db).record(
                workspace_id=ws_id,
                action="member.removed",
                resource_type="project",
                resource_id=project_id,
                actor_user_id=actor_user_id,
                new_value={"role": member.role.value, "user_id": str(user_id)},
            )
            await self.db.flush()

    async def change_workspace_role(
        self, workspace_id: UUID, user_id: UUID, new_role: MemberRole, actor_user_id: UUID
    ) -> MemberResponse | None:
        member = await self.ws_member_repo.get_by_user_and_workspace(workspace_id, user_id)
        if member is None:
            return None
        await self._assert_role_change(
            "workspace", workspace_id, member, new_role, actor_user_id
        )
        old_role = member.role
        member.role = new_role
        AuditService(self.db).record(
            workspace_id=workspace_id,
            action="member.role_changed",
            resource_type="workspace",
            resource_id=workspace_id,
            actor_user_id=actor_user_id,
            old_value={"role": old_role.value},
            new_value={"role": new_role.value},
        )
        await self.db.flush()
        await self.db.refresh(member)
        return MemberResponse.model_validate(member)

    async def change_client_role(
        self, client_id: UUID, user_id: UUID, new_role: MemberRole, actor_user_id: UUID
    ) -> MemberResponse | None:
        member = await self.client_member_repo.get_by_user_and_client(client_id, user_id)
        if member is None:
            return None
        await self._assert_role_change(
            "client", client_id, member, new_role, actor_user_id
        )
        old_role = member.role
        member.role = new_role
        ws_id = await self.resource_repo.get_workspace_id("client", client_id)
        if ws_id is not None:
            AuditService(self.db).record(
                workspace_id=ws_id,
                action="member.role_changed",
                resource_type="client",
                resource_id=client_id,
                actor_user_id=actor_user_id,
                old_value={"role": old_role.value},
                new_value={"role": new_role.value},
            )
        await self.db.flush()
        await self.db.refresh(member)
        return MemberResponse.model_validate(member)

    async def change_project_role(
        self, project_id: UUID, user_id: UUID, new_role: MemberRole, actor_user_id: UUID
    ) -> MemberResponse | None:
        member = await self.project_member_repo.get_by_user_and_project(project_id, user_id)
        if member is None:
            return None
        await self._assert_role_change(
            "project", project_id, member, new_role, actor_user_id
        )
        old_role = member.role
        member.role = new_role
        ws_id = await self.resource_repo.get_workspace_id("project", project_id)
        if ws_id is not None:
            AuditService(self.db).record(
                workspace_id=ws_id,
                action="member.role_changed",
                resource_type="project",
                resource_id=project_id,
                actor_user_id=actor_user_id,
                old_value={"role": old_role.value},
                new_value={"role": new_role.value},
            )
        await self.db.flush()
        await self.db.refresh(member)
        return MemberResponse.model_validate(member)

    async def _assert_owner_removal(
        self, level: str, resource_id: UUID, user_id: UUID, actor_user_id: UUID
    ) -> None:
        owner_count = await self._count_owners(level, resource_id)
        if owner_count <= 1:
            raise HTTPException(status_code=403, detail="Cannot remove the last owner")
        actor_role = await self.get_effective_role(level, resource_id, actor_user_id)
        if actor_role != MemberRole.OWNER:
            raise HTTPException(
                status_code=403, detail="Only an owner can remove an owner"
            )

    async def _assert_role_change(
        self,
        level: str,
        resource_id: UUID,
        member,
        new_role: MemberRole,
        actor_user_id: UUID,
    ) -> None:
        actor_role = await self.get_effective_role(level, resource_id, actor_user_id)
        if rank(new_role) > rank(actor_role):
            raise HTTPException(
                status_code=403, detail="Cannot assign a role higher than your own"
            )
        if member.role == MemberRole.OWNER and new_role != MemberRole.OWNER:
            owner_count = await self._count_owners(level, resource_id)
            if owner_count <= 1:
                raise HTTPException(
                    status_code=403, detail="Cannot demote the last owner"
                )
            if actor_role != MemberRole.OWNER:
                raise HTTPException(
                    status_code=403, detail="Only an owner can demote an owner"
                )

    async def _count_owners(self, level: str, resource_id: UUID) -> int:
        if level == "workspace":
            return await self.ws_member_repo.count_owners_by_workspace(resource_id)
        if level == "client":
            return await self.client_member_repo.count_owners_by_client(resource_id)
        return await self.project_member_repo.count_owners_by_project(resource_id)

    async def _delete_workspace_cascade(self, workspace_id: UUID) -> None:
        from src.models.external_user import ExternalUser
        from src.models.workspace_integration import WorkspaceIntegration

        await self.db.execute(
            delete(WorkspaceIntegration).where(
                WorkspaceIntegration.workspace_id == workspace_id
            )
        )
        await self.db.execute(
            delete(ExternalUser).where(
                ExternalUser.workspace_id == workspace_id
            )
        )
        await self.db.execute(
            delete(Workspace).where(Workspace.id == workspace_id)
        )
        await self.db.flush()

    async def _delete_client_cascade(self, client_id: UUID) -> None:
        from src.models.meeting import Meeting
        from src.models.project_integration import ProjectIntegration
        from src.models.project_member import ProjectMember

        project_ids_result = await self.db.execute(
            select(Project.id).where(Project.client_id == client_id)
        )
        project_ids = [row[0] for row in project_ids_result.all()]

        if project_ids:
            await self.db.execute(
                delete(ProjectMember).where(
                    ProjectMember.project_id.in_(project_ids)
                )
            )
            await self.db.execute(
                delete(ProjectIntegration).where(
                    ProjectIntegration.project_id.in_(project_ids)
                )
            )
            await self.db.execute(
                delete(Project).where(Project.id.in_(project_ids))
            )

        await self.db.execute(
            delete(Meeting).where(Meeting.client_id == client_id)
        )
        await self.db.execute(delete(Client).where(Client.id == client_id))
        await self.db.flush()

    async def _delete_project_cascade(self, project_id: UUID) -> None:
        from src.models.meeting import Meeting
        from src.models.project_integration import ProjectIntegration
        from src.models.project_member import ProjectMember

        await self.db.execute(
            delete(ProjectIntegration).where(
                ProjectIntegration.project_id == project_id
            )
        )
        await self.db.execute(
            delete(ProjectMember).where(
                ProjectMember.project_id == project_id
            )
        )
        await self.db.execute(
            delete(Meeting).where(Meeting.project_id == project_id)
        )
        await self.db.execute(
            delete(Project).where(Project.id == project_id)
        )
        await self.db.flush()

    def _to_response(self, member) -> dict:
        data = MemberResponse.model_validate(member).model_dump()
        user = getattr(member, "user", None)
        if user:
            data["email"] = user.email
            data["full_name"] = user.full_name
            data["profile_picture"] = user.profile_picture
        return data


class EffectiveRoleCache:
    """Stored on request.state; one instance per HTTP request."""

    def __init__(self, membership_service) -> None:
        self._membership = membership_service
        self._cache: dict[tuple[str, UUID], MemberRole] = {}

    async def resolve(
        self, level: str, resource_id: UUID, user_id: UUID
    ) -> MemberRole:
        key = (level, resource_id)
        if key not in self._cache:
            self._cache[key] = await self._membership.get_effective_role(
                level, resource_id, user_id
            )
        return self._cache[key]
