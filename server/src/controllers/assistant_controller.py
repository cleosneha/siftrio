from typing import AsyncGenerator

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

        history = [m.model_dump() for m in body.conversation_history]
        result = await self.service.chat(question, conversation_history=history)
        return AssistantQueryResponse(**result)

    async def query_stream(
        self,
        body: AssistantQueryRequest,
    ) -> AsyncGenerator[str, None]:
        question = body.question.strip()
        if not question:
            yield "data: {\"error\": \"Question cannot be empty\"}\n\n"
            return

        history = [m.model_dump() for m in body.conversation_history]
        async for chunk in self.service.chat_stream(question, conversation_history=history):
            yield chunk