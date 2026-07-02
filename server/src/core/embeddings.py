from langchain_mistralai import MistralAIEmbeddings


class EmbeddingService:
    def __init__(self) -> None:
        self._embeddings = MistralAIEmbeddings(model="mistral-embed")

    async def embed_query(self, text: str) -> list[float]:
        return await self._embeddings.aembed_query(text)

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return await self._embeddings.aembed_documents(texts)


embedder = EmbeddingService()
