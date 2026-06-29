from uuid import UUID

from fastapi import Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.base_response import BaseResponse
from src.services.knowledge_service import KnowledgeService


class KnowledgeController:
    def __init__(self, db: AsyncSession) -> None:
        self.service = KnowledgeService(db)

    async def list_requirements(
        self,
        project_id: str | None = None,
        meeting_id: str | None = None,
        status: str | None = None,
    ) -> BaseResponse:
        pid = UUID(project_id) if project_id else None
        mid = UUID(meeting_id) if meeting_id else None
        data = await self.service.list_requirements(pid, mid, status)
        return BaseResponse(data=data)

    async def list_action_items(
        self,
        project_id: str | None = None,
        meeting_id: str | None = None,
        status: str | None = None,
    ) -> BaseResponse:
        pid = UUID(project_id) if project_id else None
        mid = UUID(meeting_id) if meeting_id else None
        data = await self.service.list_action_items(pid, mid, status)
        return BaseResponse(data=data)

    async def list_decisions(
        self,
        project_id: str | None = None,
        meeting_id: str | None = None,
        status: str | None = None,
    ) -> BaseResponse:
        pid = UUID(project_id) if project_id else None
        mid = UUID(meeting_id) if meeting_id else None
        data = await self.service.list_decisions(pid, mid, status)
        return BaseResponse(data=data)

    async def list_risks(
        self,
        project_id: str | None = None,
        meeting_id: str | None = None,
        status: str | None = None,
    ) -> BaseResponse:
        pid = UUID(project_id) if project_id else None
        mid = UUID(meeting_id) if meeting_id else None
        data = await self.service.list_risks(pid, mid, status)
        return BaseResponse(data=data)

    async def list_questions(
        self,
        project_id: str | None = None,
        meeting_id: str | None = None,
        status: str | None = None,
    ) -> BaseResponse:
        pid = UUID(project_id) if project_id else None
        mid = UUID(meeting_id) if meeting_id else None
        data = await self.service.list_questions(pid, mid, status)
        return BaseResponse(data=data)

    async def get_requirement(self, entity_id: str) -> BaseResponse:
        data = await self.service.get_requirement(UUID(entity_id))
        return self._response(data, "Requirement")

    async def get_action_item(self, entity_id: str) -> BaseResponse:
        data = await self.service.get_action_item(UUID(entity_id))
        return self._response(data, "Action item")

    async def get_decision(self, entity_id: str) -> BaseResponse:
        data = await self.service.get_decision(UUID(entity_id))
        return self._response(data, "Decision")

    async def get_risk(self, entity_id: str) -> BaseResponse:
        data = await self.service.get_risk(UUID(entity_id))
        return self._response(data, "Risk")

    async def get_question(self, entity_id: str) -> BaseResponse:
        data = await self.service.get_question(UUID(entity_id))
        return self._response(data, "Question")

    async def update_requirement(self, entity_id: str, body: dict) -> BaseResponse:
        data = await self.service.update_requirement(UUID(entity_id), body)
        return BaseResponse(message="Requirement updated", data=data)

    async def update_action_item(self, entity_id: str, body: dict) -> BaseResponse:
        data = await self.service.update_action_item(UUID(entity_id), body)
        return BaseResponse(message="Action item updated", data=data)

    async def update_decision(self, entity_id: str, body: dict) -> BaseResponse:
        data = await self.service.update_decision(UUID(entity_id), body)
        return BaseResponse(message="Decision updated", data=data)

    async def update_risk(self, entity_id: str, body: dict) -> BaseResponse:
        data = await self.service.update_risk(UUID(entity_id), body)
        return BaseResponse(message="Risk updated", data=data)

    async def update_question(self, entity_id: str, body: dict) -> BaseResponse:
        data = await self.service.update_question(UUID(entity_id), body)
        return BaseResponse(message="Question updated", data=data)

    def _response(self, data, label: str) -> BaseResponse:
        if data is None:
            return BaseResponse(success=False, message=f"{label} not found", data=None)
        return BaseResponse(data=data)
