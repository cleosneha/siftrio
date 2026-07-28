import logging
from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.client import Client
from src.models.project import Project
from src.models.workspace import Workspace
from src.repositories.auth_repository import AuthRepository

logger = logging.getLogger(__name__)


class UserDeletionService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.auth_repo = AuthRepository(db)

    async def delete_user(self, user_id: UUID) -> None:
        user = await self.auth_repo.get_user_by_id(user_id)
        if not user:
            return

        sole_workspace_ids = await self._find_sole_member_workspaces(user_id)
        sole_client_ids = await self._find_sole_member_clients(
            user_id, sole_workspace_ids
        )
        sole_project_ids = await self._find_sole_member_projects(
            user_id, sole_client_ids
        )

        for workspace_id in sole_workspace_ids:
            await self._delete_workspace_cascade(workspace_id)

        for client_id in sole_client_ids:
            await self._delete_client_cascade(client_id)

        for project_id in sole_project_ids:
            await self._delete_project_cascade(project_id)

        await self.db.delete(user)
        await self.db.flush()

        logger.info(
            "User %s deleted. Orphaned workspaces: %d, clients: %d, projects: %d",
            user_id,
            len(sole_workspace_ids),
            len(sole_client_ids),
            len(sole_project_ids),
        )

    async def _find_sole_member_workspaces(self, user_id: UUID) -> list[UUID]:
        from src.models.workspace_member import WorkspaceMember

        member_count_subq = (
            select(
                WorkspaceMember.workspace_id,
                func.count(WorkspaceMember.id).label("member_count"),
            )
            .group_by(WorkspaceMember.workspace_id)
            .having(func.count(WorkspaceMember.id) == 1)
            .subquery()
        )

        result = await self.db.execute(
            select(member_count_subq.c.workspace_id)
            .join(
                WorkspaceMember,
                (WorkspaceMember.workspace_id == member_count_subq.c.workspace_id)
                & (WorkspaceMember.user_id == user_id),
            )
        )
        return [row[0] for row in result.all()]

    async def _find_sole_member_clients(
        self, user_id: UUID, exclude_workspace_ids: list[UUID]
    ) -> list[UUID]:
        from src.models.client_member import ClientMember

        member_count_subq = (
            select(
                ClientMember.client_id,
                func.count(ClientMember.id).label("member_count"),
            )
            .group_by(ClientMember.client_id)
            .having(func.count(ClientMember.id) == 1)
            .subquery()
        )

        query = (
            select(member_count_subq.c.client_id)
            .join(
                ClientMember,
                (ClientMember.client_id == member_count_subq.c.client_id)
                & (ClientMember.user_id == user_id),
            )
            .join(Client, Client.id == member_count_subq.c.client_id)
        )

        if exclude_workspace_ids:
            query = query.where(
                Client.workspace_id.notin_(exclude_workspace_ids)
            )

        result = await self.db.execute(query)
        return [row[0] for row in result.all()]

    async def _find_sole_member_projects(
        self, user_id: UUID, exclude_client_ids: list[UUID]
    ) -> list[UUID]:
        from src.models.project_member import ProjectMember

        member_count_subq = (
            select(
                ProjectMember.project_id,
                func.count(ProjectMember.id).label("member_count"),
            )
            .group_by(ProjectMember.project_id)
            .having(func.count(ProjectMember.id) == 1)
            .subquery()
        )

        query = (
            select(member_count_subq.c.project_id)
            .join(
                ProjectMember,
                (ProjectMember.project_id == member_count_subq.c.project_id)
                & (ProjectMember.user_id == user_id),
            )
            .join(Project, Project.id == member_count_subq.c.project_id)
        )

        if exclude_client_ids:
            query = query.where(
                Project.client_id.notin_(exclude_client_ids)
            )

        result = await self.db.execute(query)
        return [row[0] for row in result.all()]

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

    async def _delete_client_cascade(self, client_id: UUID) -> None:
        from src.models.meeting import Meeting
        from src.models.project_integration import ProjectIntegration
        from src.models.project_member import ProjectMember

        project_ids = await self._get_client_project_ids(client_id)
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

    async def _get_client_project_ids(self, client_id: UUID) -> list[UUID]:
        result = await self.db.execute(
            select(Project.id).where(Project.client_id == client_id)
        )
        return [row[0] for row in result.all()]
