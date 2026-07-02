from sqlalchemy.ext.asyncio import AsyncSession

from src.agents.services.response import ChatService
from src.exceptions.base import BaseAPIException
from src.schemas.assistant_schema import AssistantQueryRequest, AssistantQueryResponse


class AssistantController:
    def __init__(self, db: AsyncSession, user_context: dict | None = None) -> None:
        self.service = ChatService(db, user_context=user_context)

    async def query(self, body: AssistantQueryRequest) -> AssistantQueryResponse:
        question = body.question.strip()
        if not question:
            raise BaseAPIException(message="Question cannot be empty", status_code=400)

        result = await self.service.chat(question)
        return AssistantQueryResponse(**result)