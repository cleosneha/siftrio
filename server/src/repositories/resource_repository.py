from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.client import Client
from src.models.knowledge_base import ActionItem, Decision, Question, Requirement, Risk
from src.models.meeting import Meeting
from src.models.project import Project
from src.models.workspace import Workspace

_KNOWLEDGE_MODELS = {
    "requirement": Requirement,
    "action_item": ActionItem,
    "decision": Decision,
    "risk": Risk,
    "question": Question,
}


class ResourceRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_workspace_id(self, resource_type: str, resource_id: UUID) -> UUID | None:
        if resource_type == "workspace":
            stmt = select(Workspace.id).where(Workspace.id == resource_id)
        elif resource_type == "client":
            stmt = select(Client.workspace_id).where(Client.id == resource_id)
        elif resource_type == "project":
            stmt = (
                select(Client.workspace_id)
                .join(Project, Project.client_id == Client.id)
                .where(Project.id == resource_id)
            )
        elif resource_type == "meeting":
            stmt = (
                select(Client.workspace_id)
                .join(Meeting, Meeting.client_id == Client.id)
                .where(Meeting.id == resource_id)
            )
        elif resource_type in _KNOWLEDGE_MODELS:
            model = _KNOWLEDGE_MODELS[resource_type]
            stmt = (
                select(Client.workspace_id)
                .select_from(model)
                .join(Project, Project.id == model.project_id)
                .join(Client, Client.id == Project.client_id)
                .where(model.id == resource_id)
            )
        else:
            return None
        result = await self._db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_project_id(self, resource_type: str, resource_id: UUID) -> UUID | None:
        model = _KNOWLEDGE_MODELS.get(resource_type)
        if model is None:
            return None
        stmt = select(model.project_id).select_from(model).where(model.id == resource_id)
        result = await self._db.execute(stmt)
        return result.scalar_one_or_none()

    async def belongs_to_workspace(
        self, resource_type: str, resource_id: UUID, workspace_id: UUID
    ) -> bool:
        owner = await self.get_workspace_id(resource_type, resource_id)
        return owner is not None and owner == workspace_id
