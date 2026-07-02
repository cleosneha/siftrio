from src.agents.schemas import RetrievedContext
from src.agents.services.context_builder import ContextBuilderService
from src.agents.state import ChatState


async def build_context(
    state: ChatState,
    context_builder: ContextBuilderService,
) -> dict[str, str | None]:
    retrieved_context = RetrievedContext(
        chunks=state["retrieved_chunks"],
        meetings=state["meeting_analysis"],
        knowledge=state["knowledge_entities"],
    )
    context = context_builder.build(retrieved_context)
    return {"context": context}