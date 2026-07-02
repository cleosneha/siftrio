from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.models.knowledge_base import (
    ActionItem,
    Decision,
    Question,
    Requirement,
    Risk,
)


class KnowledgeRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_requirement(
        self,
        project_id: UUID,
        meeting_id: UUID,
        title: str,
        source_chunk_id: UUID | None = None,
        description: str | None = None,
        priority: str | None = None,
    ) -> Requirement:
        entity = Requirement(
            project_id=project_id,
            meeting_id=meeting_id,
            source_chunk_id=source_chunk_id,
            title=title,
            description=description,
            priority=priority,
            status="pending",
        )
        self.db.add(entity)
        await self.db.flush()
        await self.db.refresh(entity)
        return entity

    async def create_action_item(
        self,
        project_id: UUID,
        meeting_id: UUID,
        title: str,
        source_chunk_id: UUID | None = None,
        description: str | None = None,
        assignee: str | None = None,
        due_date: str | None = None,
    ) -> ActionItem:
        parsed_due = datetime.fromisoformat(due_date) if due_date else None
        entity = ActionItem(
            project_id=project_id,
            meeting_id=meeting_id,
            source_chunk_id=source_chunk_id,
            title=title,
            description=description,
            assignee=assignee,
            due_date=parsed_due,
            status="pending",
        )
        self.db.add(entity)
        await self.db.flush()
        await self.db.refresh(entity)
        return entity

    async def create_decision(
        self,
        project_id: UUID,
        meeting_id: UUID,
        title: str,
        source_chunk_id: UUID | None = None,
        description: str | None = None,
        decision_date: str | None = None,
    ) -> Decision:
        parsed_date = datetime.fromisoformat(decision_date) if decision_date else None
        entity = Decision(
            project_id=project_id,
            meeting_id=meeting_id,
            source_chunk_id=source_chunk_id,
            title=title,
            description=description,
            decision_date=parsed_date,
            status="active",
        )
        self.db.add(entity)
        await self.db.flush()
        await self.db.refresh(entity)
        return entity

    async def create_risk(
        self,
        project_id: UUID,
        meeting_id: UUID,
        title: str,
        source_chunk_id: UUID | None = None,
        description: str | None = None,
        severity: str | None = None,
        mitigation: str | None = None,
    ) -> Risk:
        entity = Risk(
            project_id=project_id,
            meeting_id=meeting_id,
            source_chunk_id=source_chunk_id,
            title=title,
            description=description,
            severity=severity,
            mitigation=mitigation,
            status="open",
        )
        self.db.add(entity)
        await self.db.flush()
        await self.db.refresh(entity)
        return entity

    async def create_question(
        self,
        project_id: UUID,
        meeting_id: UUID,
        title: str,
        source_chunk_id: UUID | None = None,
        description: str | None = None,
        answer: str | None = None,
    ) -> Question:
        status = "answered" if answer else "pending"
        entity = Question(
            project_id=project_id,
            meeting_id=meeting_id,
            source_chunk_id=source_chunk_id,
            title=title,
            description=description,
            answer=answer,
            status=status,
        )
        self.db.add(entity)
        await self.db.flush()
        await self.db.refresh(entity)
        return entity

    async def list_requirements(
        self,
        project_id: UUID | None = None,
        meeting_id: UUID | None = None,
        status: str | None = None,
    ) -> list[Requirement]:
        return await self._list(Requirement, project_id, meeting_id, status)

    async def list_action_items(
        self,
        project_id: UUID | None = None,
        meeting_id: UUID | None = None,
        status: str | None = None,
    ) -> list[ActionItem]:
        return await self._list(ActionItem, project_id, meeting_id, status)

    async def list_decisions(
        self,
        project_id: UUID | None = None,
        meeting_id: UUID | None = None,
        status: str | None = None,
    ) -> list[Decision]:
        return await self._list(Decision, project_id, meeting_id, status)

    async def list_risks(
        self,
        project_id: UUID | None = None,
        meeting_id: UUID | None = None,
        status: str | None = None,
    ) -> list[Risk]:
        return await self._list(Risk, project_id, meeting_id, status)

    async def list_questions(
        self,
        project_id: UUID | None = None,
        meeting_id: UUID | None = None,
        status: str | None = None,
    ) -> list[Question]:
        return await self._list(Question, project_id, meeting_id, status)

    async def _list(
        self,
        model,
        project_id: UUID | None = None,
        meeting_id: UUID | None = None,
        status: str | None = None,
    ):
        query = select(model).options(
            joinedload(model.meeting),
            joinedload(model.project),
        )
        if project_id is not None:
            query = query.where(model.project_id == project_id)
        if meeting_id is not None:
            query = query.where(model.meeting_id == meeting_id)
        if status is not None:
            query = query.where(model.status == status)
        query = query.order_by(model.created_at.desc())
        result = await self.db.execute(query)
        return list(result.unique().scalars().all())

    async def get_requirement(self, entity_id: UUID) -> Requirement | None:
        return await self._get(Requirement, entity_id)

    async def get_action_item(self, entity_id: UUID) -> ActionItem | None:
        return await self._get(ActionItem, entity_id)

    async def get_decision(self, entity_id: UUID) -> Decision | None:
        return await self._get(Decision, entity_id)

    async def get_risk(self, entity_id: UUID) -> Risk | None:
        return await self._get(Risk, entity_id)

    async def get_question(self, entity_id: UUID) -> Question | None:
        return await self._get(Question, entity_id)

    async def _get(self, model, entity_id: UUID):
        result = await self.db.execute(
            select(model)
            .options(joinedload(model.meeting), joinedload(model.project))
            .where(model.id == entity_id)
        )
        return result.unique().scalar_one_or_none()

    async def update_requirement(
        self, entity_id: UUID, **kwargs
    ) -> Requirement | None:
        return await self._update(Requirement, entity_id, kwargs)

    async def update_action_item(
        self, entity_id: UUID, **kwargs
    ) -> ActionItem | None:
        return await self._update(ActionItem, entity_id, kwargs)

    async def update_decision(
        self, entity_id: UUID, **kwargs
    ) -> Decision | None:
        return await self._update(Decision, entity_id, kwargs)

    async def update_risk(self, entity_id: UUID, **kwargs) -> Risk | None:
        return await self._update(Risk, entity_id, kwargs)

    async def update_question(
        self, entity_id: UUID, **kwargs
    ) -> Question | None:
        return await self._update(Question, entity_id, kwargs)

    async def _update(self, model, entity_id: UUID, kwargs: dict):
        entity = await self.db.get(model, entity_id)
        if entity is None:
            return None
        for key, value in kwargs.items():
            if value is not None:
                setattr(entity, key, value)
        await self.db.flush()
        await self.db.refresh(entity)
        return entity

    async def delete_requirements_by_meeting(self, meeting_id: UUID) -> None:
        await self._delete_by_meeting(Requirement, meeting_id)

    async def delete_action_items_by_meeting(self, meeting_id: UUID) -> None:
        await self._delete_by_meeting(ActionItem, meeting_id)

    async def delete_decisions_by_meeting(self, meeting_id: UUID) -> None:
        await self._delete_by_meeting(Decision, meeting_id)

    async def delete_risks_by_meeting(self, meeting_id: UUID) -> None:
        await self._delete_by_meeting(Risk, meeting_id)

    async def delete_questions_by_meeting(self, meeting_id: UUID) -> None:
        await self._delete_by_meeting(Question, meeting_id)

    async def _delete_by_meeting(self, model, meeting_id: UUID) -> None:
        result = await self.db.execute(
            select(model).where(model.meeting_id == meeting_id)
        )
        entities = result.scalars().all()
        for entity in entities:
            await self.db.delete(entity)
