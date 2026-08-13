from uuid import UUID

from sqlalchemy import exists, select

from src.models.client import Client
from src.models.client_member import ClientMember
from src.models.project import Project
from src.models.project_member import ProjectMember
from src.models.workspace_member import WorkspaceMember


def tenant_scope_subquery(user_id: UUID):
    return (
        select(WorkspaceMember.workspace_id)
        .where(WorkspaceMember.user_id == user_id)
        .union(
            select(Client.workspace_id)
            .join(ClientMember, ClientMember.client_id == Client.id)
            .where(ClientMember.user_id == user_id),
            select(Client.workspace_id)
            .join(Project, Project.client_id == Client.id)
            .join(ProjectMember, ProjectMember.project_id == Project.id)
            .where(ProjectMember.user_id == user_id),
        )
    )


def visible_client_exists(user_id: UUID):
    return (
        exists().where(
            WorkspaceMember.workspace_id == Client.workspace_id,
            WorkspaceMember.user_id == user_id,
        )
        | exists().where(
            ClientMember.client_id == Client.id,
            ClientMember.user_id == user_id,
        )
        | exists().where(
            Project.client_id == Client.id,
            ProjectMember.project_id == Project.id,
            ProjectMember.user_id == user_id,
        )
    )


def visible_project_exists(user_id: UUID):
    return (
        exists().where(
            ProjectMember.project_id == Project.id,
            ProjectMember.user_id == user_id,
        )
        | exists().where(
            ClientMember.client_id == Project.client_id,
            ClientMember.user_id == user_id,
        )
        | exists().where(
            Client.id == Project.client_id,
            WorkspaceMember.workspace_id == Client.workspace_id,
            WorkspaceMember.user_id == user_id,
        )
    )
