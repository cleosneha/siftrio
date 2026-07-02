from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.knowledge_repository import KnowledgeRepository
from src.repositories.meeting_chunk_repository import MeetingChunkRepository
from src.repositories.meeting_repository import MeetingRepository
from src.schemas.base_response import BaseResponse
from src.services.knowledge_service import KnowledgeService


class KnowledgeController:
    def __init__(self, db: AsyncSession) -> None:
        self.service = KnowledgeService(
            db=db,
            repo=KnowledgeRepository(db),
            meeting_repo=MeetingRepository(db),
            chunk_repo=MeetingChunkRepository(db),
        )

    async def list_requirements(
        self,
        project_id: UUID | None = None,
        meeting_id: UUID | None = None,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> BaseResponse:
        data = await self.service.list_requirements(project_id, meeting_id, status, limit=limit, offset=offset)
        return BaseResponse(data=data)

    async def list_action_items(
        self,
        project_id: UUID | None = None,
        meeting_id: UUID | None = None,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> BaseResponse:
        data = await self.service.list_action_items(project_id, meeting_id, status, limit=limit, offset=offset)
        return BaseResponse(data=data)

    async def list_decisions(
        self,
        project_id: UUID | None = None,
        meeting_id: UUID | None = None,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> BaseResponse:
        data = await self.service.list_decisions(project_id, meeting_id, status, limit=limit, offset=offset)
        return BaseResponse(data=data)

    async def list_risks(
        self,
        project_id: UUID | None = None,
        meeting_id: UUID | None = None,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> BaseResponse:
        data = await self.service.list_risks(project_id, meeting_id, status, limit=limit, offset=offset)
        return BaseResponse(data=data)

    async def list_questions(
        self,
        project_id: UUID | None = None,
        meeting_id: UUID | None = None,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> BaseResponse:
        data = await self.service.list_questions(project_id, meeting_id, status, limit=limit, offset=offset)
        return BaseResponse(data=data)

    async def get_requirement(self, entity_id: UUID) -> BaseResponse:
        data = await self.service.get_requirement(entity_id)
        return self._response(data, "Requirement")

    async def get_action_item(self, entity_id: UUID) -> BaseResponse:
        data = await self.service.get_action_item(entity_id)
        return self._response(data, "Action item")

    async def get_decision(self, entity_id: UUID) -> BaseResponse:
        data = await self.service.get_decision(entity_id)
        return self._response(data, "Decision")

    async def get_risk(self, entity_id: UUID) -> BaseResponse:
        data = await self.service.get_risk(entity_id)
        return self._response(data, "Risk")

    async def get_question(self, entity_id: UUID) -> BaseResponse:
        data = await self.service.get_question(entity_id)
        return self._response(data, "Question")

    async def update_requirement(self, entity_id: UUID, body: dict) -> BaseResponse:
        data = await self.service.update_requirement(entity_id, body)
        return BaseResponse(message="Requirement updated", data=data)

    async def update_action_item(self, entity_id: UUID, body: dict) -> BaseResponse:
        data = await self.service.update_action_item(entity_id, body)
        return BaseResponse(message="Action item updated", data=data)

    async def update_decision(self, entity_id: UUID, body: dict) -> BaseResponse:
        data = await self.service.update_decision(entity_id, body)
        return BaseResponse(message="Decision updated", data=data)

    async def update_risk(self, entity_id: UUID, body: dict) -> BaseResponse:
        data = await self.service.update_risk(entity_id, body)
        return BaseResponse(message="Risk updated", data=data)

    async def update_question(self, entity_id: UUID, body: dict) -> BaseResponse:
        data = await self.service.update_question(entity_id, body)
        return BaseResponse(message="Question updated", data=data)

    def _response(self, data, label: str) -> BaseResponse:
        if data is None:
            return BaseResponse(success=False, message=f"{label} not found", data=None)
        return BaseResponse(data=data)
