from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.agents.schemas import RetrievedKnowledge
from src.models.client import Client
from src.models.knowledge_base import (
    ActionItem,
    Decision,
    Question,
    Requirement,
    Risk,
)
from src.models.project import Project


ENTITY_MODELS = [
    (Requirement, "requirement"),
    (ActionItem, "action_item"),
    (Decision, "decision"),
    (Risk, "risk"),
    (Question, "question"),
]


class KnowledgeRetriever:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def search(
        self,
        filters: dict | None = None,
    ) -> list[RetrievedKnowledge]:
        filters = filters or {}
        meeting_id = filters.get("meeting_id")
        project_id = filters.get("project_id")
        client_id = filters.get("client_id")
        workspace_id = filters.get("workspace_id")

        results: list[RetrievedKnowledge] = []
        for model, entity_type in ENTITY_MODELS:
            entities = await self._search_entity(
                model,
                entity_type,
                meeting_id=meeting_id,
                project_id=project_id,
                client_id=client_id,
                workspace_id=workspace_id,
            )
            results.extend(entities)

        results.sort(key=lambda x: x.entity_type)
        return results

    async def _search_entity(
        self,
        model,
        entity_type: str,
        meeting_id: str | None,
        project_id: str | None,
        client_id: str | None,
        workspace_id: str | None,
    ) -> list[RetrievedKnowledge]:
        stmt = select(model).options(joinedload(model.meeting))

        needs_project_join = bool(client_id or workspace_id)

        if needs_project_join:
            stmt = stmt.join(model.project, isouter=False)
            if client_id:
                stmt = stmt.where(Project.client_id == UUID(client_id))
            if workspace_id:
                stmt = stmt.join(Project.client).where(
                    Client.workspace_id == UUID(workspace_id)
                )
        elif project_id:
            stmt = stmt.where(model.project_id == UUID(project_id))

        if meeting_id:
            stmt = stmt.where(model.meeting_id == UUID(meeting_id))

        stmt = stmt.order_by(model.created_at.desc())
        result = await self.db.execute(stmt)
        entities = list(result.unique().scalars().all())

        return [
            RetrievedKnowledge(
                entity_id=str(e.id),
                entity_type=entity_type,
                title=e.title,
                description=e.description,
                status=e.status,
                meeting_id=str(e.meeting.id) if e.meeting else None,
                meeting_title=e.meeting.title if e.meeting else None,
            )
            for e in entities
        ]
