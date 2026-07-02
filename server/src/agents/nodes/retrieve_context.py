from src.agents.retrievers.hybrid import HybridRetriever
from src.agents.state import ChatState


async def retrieve_context(
    state: ChatState,
    retriever: HybridRetriever,
) -> dict[str, object]:
    parsed_query = state["parsed_query"]
    if parsed_query is None:
        raise ValueError("parsed_query must be set before retrieving context")

    retrieved_context = await retriever.retrieve(parsed_query)
    return {
        "retrieved_chunks": retrieved_context.chunks,
        "meeting_analysis": retrieved_context.meetings,
        "knowledge_entities": retrieved_context.knowledge,
    }