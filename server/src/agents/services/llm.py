from langchain_mistralai import ChatMistralAI
from langchain_core.messages import BaseMessage
from langchain_core.language_models import BaseChatModel
from pydantic import BaseModel


class LLMService:
    def __init__(
        self,
        model: str = "mistral-small-latest",
        temperature: float = 0.1,
    ) -> None:
        self._model = ChatMistralAI(model=model, temperature=temperature)

    @property
    def model(self) -> ChatMistralAI:
        return self._model

    def with_structured_output(self, schema: type[BaseModel]) -> BaseChatModel:
        return self._model.with_structured_output(schema)

    async def invoke(self, messages: list[BaseMessage]) -> BaseMessage:
        return await self._model.ainvoke(messages)
