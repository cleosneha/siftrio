from langchain_mistralai import MistralAIEmbeddings

from src.core.config import settings


class EmbeddingService:
    def __init__(self) -> None:
        self._embeddings = MistralAIEmbeddings(model=settings.MISTRAL_EMBED_MODEL)

    async def embed_query(self, text: str) -> list[float]:
        return await self._embeddings.aembed_query(text)

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return await self._embeddings.aembed_documents(texts)


embedder = EmbeddingService()
