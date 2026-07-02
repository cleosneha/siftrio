from src.agents.retrievers.hybrid import HybridRetriever
from src.agents.state import ChatState


async def retrieve_context(
    state: ChatState,
    retriever: HybridRetriever,
) -> dict[str, object]:
    db = state["db"]
    retrieval_scope = state.get("retrieval_scope")
    if retrieval_scope is None:
        raise ValueError("retrieval_scope must be set before retrieving context")

    retrieved_context = await retriever.retrieve(db, retrieval_scope)
    return {
        "retrieved_chunks": retrieved_context.chunks,
        "meeting_analysis": retrieved_context.meetings,
        "knowledge_entities": retrieved_context.knowledge,
    }
