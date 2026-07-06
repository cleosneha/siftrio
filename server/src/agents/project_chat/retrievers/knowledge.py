from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.agents.project_chat.schemas import RetrievedKnowledge
from src.models.client import Client
from src.models.knowledge_base import (
    ActionItem,
    Decision,
    Question,
    Requirement,
    Risk,
)
from src.models.meeting import Meeting
from src.models.project import Project


ENTITY_MODELS = [
    (Requirement, "requirement"),
    (ActionItem, "action_item"),
    (Decision, "decision"),
    (Risk, "risk"),
    (Question, "question"),
]


class KnowledgeRetriever:
    async def search(
        self,
        db: AsyncSession,
        filters: dict | None = None,
    ) -> list[RetrievedKnowledge]:
        filters = filters or {}
        workspace_ids = filters.get("workspace_ids") or []
        client_ids = filters.get("client_ids") or []
        project_ids = filters.get("project_ids") or []
        meeting_ids = filters.get("meeting_ids") or []
        keywords = filters.get("keywords") or []
        date_range = filters.get("date_range")

        results: list[RetrievedKnowledge] = []
        for model, entity_type in ENTITY_MODELS:
            entities = await self._search_entity(
                db,
                model,
                entity_type,
                workspace_ids=workspace_ids,
                client_ids=client_ids,
                project_ids=project_ids,
                meeting_ids=meeting_ids,
                keywords=keywords,
                date_range=date_range,
            )
            results.extend(entities)

        results.sort(key=lambda x: x.entity_type)
        return results

    async def _search_entity(
        self,
        db: AsyncSession,
        model,
        entity_type: str,
        workspace_ids: list[str] | None = None,
        client_ids: list[str] | None = None,
        project_ids: list[str] | None = None,
        meeting_ids: list[str] | None = None,
        keywords: list[str] | None = None,
        date_range: dict | None = None,
    ) -> list[RetrievedKnowledge]:
        stmt = select(model).options(joinedload(model.meeting))

        workspace_ids = workspace_ids or []
        client_ids = client_ids or []
        project_ids = project_ids or []
        meeting_ids = meeting_ids or []
        keywords = keywords or []

        needs_project_join = bool(workspace_ids or client_ids or project_ids)
        if needs_project_join:
            stmt = stmt.join(model.project, isouter=False)
            if workspace_ids or client_ids:
                stmt = stmt.join(Project.client)
            if workspace_ids:
                stmt = stmt.where(Client.workspace_id.in_([UUID(wid) for wid in workspace_ids]))
            if client_ids:
                stmt = stmt.where(Client.id.in_([UUID(cid) for cid in client_ids]))

        if meeting_ids:
            stmt = stmt.where(model.meeting_id.in_([UUID(mid) for mid in meeting_ids]))
        if project_ids:
            stmt = stmt.where(model.project_id.in_([UUID(pid) for pid in project_ids]))

        if keywords:
            search_terms = " & ".join(keywords)
            ts_query = func.plainto_tsquery("english", search_terms)
            ts_vector = func.to_tsvector(
                "english",
                func.coalesce(model.title, "") + " " + func.coalesce(model.description, ""),
            )
            stmt = stmt.where(ts_vector.op("@@")(ts_query))

        if date_range:
            stmt = stmt.join(Meeting, model.meeting_id == Meeting.id, isouter=True)
            if date_range.get("start"):
                stmt = stmt.where(Meeting.meeting_date >= date_range["start"])
            if date_range.get("end"):
                stmt = stmt.where(Meeting.meeting_date <= date_range["end"])

        stmt = stmt.order_by(model.created_at.desc())
        result = await db.execute(stmt)
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
