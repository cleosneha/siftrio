from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions.base import BaseAPIException
from src.repositories.knowledge_repository import KnowledgeRepository
from src.repositories.meeting_chunk_repository import MeetingChunkRepository
from src.repositories.meeting_repository import MeetingRepository


class KnowledgeService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = KnowledgeRepository(db)
        self.meeting_repo = MeetingRepository(db)
        self.chunk_repo = MeetingChunkRepository(db)

    async def extract_from_analysis(
        self,
        meeting_id: UUID,
        requirements: list[dict] | None = None,
        action_items: list[dict] | None = None,
        decisions: list[dict] | None = None,
        risks: list[dict] | None = None,
        questions: list[dict] | None = None,
    ) -> None:
        meeting = await self.meeting_repo.get_by_id(meeting_id)
        if meeting is None or meeting.project_id is None:
            return

        project_id = meeting.project_id

        await self.repo.delete_requirements_by_meeting(meeting_id)
        await self.repo.delete_action_items_by_meeting(meeting_id)
        await self.repo.delete_decisions_by_meeting(meeting_id)
        await self.repo.delete_risks_by_meeting(meeting_id)
        await self.repo.delete_questions_by_meeting(meeting_id)

        if requirements:
            for item in requirements:
                await self.repo.create_requirement(
                    project_id=project_id,
                    meeting_id=meeting_id,
                    title=item.get("title", ""),
                    description=item.get("description"),
                    priority=item.get("priority"),
                )

        if action_items:
            for item in action_items:
                await self.repo.create_action_item(
                    project_id=project_id,
                    meeting_id=meeting_id,
                    title=item.get("title", ""),
                    description=item.get("description"),
                    assignee=item.get("assignee"),
                    due_date=item.get("due_date"),
                )

        if decisions:
            for item in decisions:
                await self.repo.create_decision(
                    project_id=project_id,
                    meeting_id=meeting_id,
                    title=item.get("title", ""),
                    description=item.get("description"),
                    decision_date=item.get("decision_date"),
                )

        if risks:
            for item in risks:
                await self.repo.create_risk(
                    project_id=project_id,
                    meeting_id=meeting_id,
                    title=item.get("title", ""),
                    description=item.get("description"),
                    severity=item.get("severity"),
                    mitigation=item.get("mitigation"),
                )

        if questions:
            for item in questions:
                await self.repo.create_question(
                    project_id=project_id,
                    meeting_id=meeting_id,
                    title=item.get("title", ""),
                    description=item.get("description"),
                    answer=item.get("answer"),
                )

        await self.db.commit()

    async def list_requirements(
        self,
        project_id: UUID | None = None,
        meeting_id: UUID | None = None,
        status: str | None = None,
    ) -> list[dict]:
        entities = await self.repo.list_requirements(project_id, meeting_id, status)
        return [self._to_dict(r, "priority") for r in entities]

    async def list_action_items(
        self,
        project_id: UUID | None = None,
        meeting_id: UUID | None = None,
        status: str | None = None,
    ) -> list[dict]:
        entities = await self.repo.list_action_items(project_id, meeting_id, status)
        return [self._to_dict(r, "assignee", "due_date") for r in entities]

    async def list_decisions(
        self,
        project_id: UUID | None = None,
        meeting_id: UUID | None = None,
        status: str | None = None,
    ) -> list[dict]:
        entities = await self.repo.list_decisions(project_id, meeting_id, status)
        return [self._to_dict(r, "decision_date") for r in entities]

    async def list_risks(
        self,
        project_id: UUID | None = None,
        meeting_id: UUID | None = None,
        status: str | None = None,
    ) -> list[dict]:
        entities = await self.repo.list_risks(project_id, meeting_id, status)
        return [self._to_dict(r, "severity", "mitigation") for r in entities]

    async def list_questions(
        self,
        project_id: UUID | None = None,
        meeting_id: UUID | None = None,
        status: str | None = None,
    ) -> list[dict]:
        entities = await self.repo.list_questions(project_id, meeting_id, status)
        return [self._to_dict(r, "answer") for r in entities]

    async def get_requirement(self, entity_id: UUID) -> dict | None:
        entity = await self.repo.get_requirement(entity_id)
        return self._to_dict(entity, "priority") if entity else None

    async def get_action_item(self, entity_id: UUID) -> dict | None:
        entity = await self.repo.get_action_item(entity_id)
        return self._to_dict(entity, "assignee", "due_date") if entity else None

    async def get_decision(self, entity_id: UUID) -> dict | None:
        entity = await self.repo.get_decision(entity_id)
        return self._to_dict(entity, "decision_date") if entity else None

    async def get_risk(self, entity_id: UUID) -> dict | None:
        entity = await self.repo.get_risk(entity_id)
        return self._to_dict(entity, "severity", "mitigation") if entity else None

    async def get_question(self, entity_id: UUID) -> dict | None:
        entity = await self.repo.get_question(entity_id)
        return self._to_dict(entity, "answer") if entity else None

    async def update_requirement(
        self, entity_id: UUID, data: dict
    ) -> dict | None:
        entity = await self.repo.update_requirement(entity_id, **data)
        if entity is None:
            raise BaseAPIException(message="Requirement not found", status_code=404)
        return self._to_dict(entity, "priority")

    async def update_action_item(
        self, entity_id: UUID, data: dict
    ) -> dict | None:
        entity = await self.repo.update_action_item(entity_id, **data)
        if entity is None:
            raise BaseAPIException(message="Action item not found", status_code=404)
        return self._to_dict(entity, "assignee", "due_date")

    async def update_decision(
        self, entity_id: UUID, data: dict
    ) -> dict | None:
        entity = await self.repo.update_decision(entity_id, **data)
        if entity is None:
            raise BaseAPIException(message="Decision not found", status_code=404)
        return self._to_dict(entity, "decision_date")

    async def update_risk(self, entity_id: UUID, data: dict) -> dict | None:
        entity = await self.repo.update_risk(entity_id, **data)
        if entity is None:
            raise BaseAPIException(message="Risk not found", status_code=404)
        return self._to_dict(entity, "severity", "mitigation")

    async def update_question(
        self, entity_id: UUID, data: dict
    ) -> dict | None:
        entity = await self.repo.update_question(entity_id, **data)
        if entity is None:
            raise BaseAPIException(message="Question not found", status_code=404)
        return self._to_dict(entity, "answer")

    def _to_dict(self, entity, *extra_fields) -> dict:
        result = {
            "id": str(entity.id),
            "project_id": str(entity.project_id),
            "meeting_id": str(entity.meeting_id),
            "source_chunk_id": str(entity.source_chunk_id) if entity.source_chunk_id else None,
            "title": entity.title,
            "description": entity.description,
            "status": entity.status,
            "created_at": entity.created_at.isoformat().replace("+00:00", "Z") if entity.created_at else None,
            "updated_at": entity.updated_at.isoformat().replace("+00:00", "Z") if entity.updated_at else None,
            "meeting_title": entity.meeting.title if entity.meeting else None,
        }
        for field in extra_fields:
            val = getattr(entity, field, None)
            if isinstance(val, str):
                result[field] = val
            elif val is not None:
                result[field] = str(val)
            else:
                result[field] = None
        return result
