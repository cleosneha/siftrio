from src.agents.schemas import RetrievedContext
from src.agents.services.context_builder import ContextBuilderService
from src.agents.state import ChatState


def _format_history(history: list[dict[str, str]]) -> str:
    if not history:
        return "(no previous conversation)"
    lines = []
    for msg in history:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        label = "User" if role == "user" else "Assistant"
        lines.append(f"{label}: {content}")
    return "\n".join(lines)


async def build_context(
    state: ChatState,
    context_builder: ContextBuilderService,
) -> dict[str, str | None]:
    retrieved_context = RetrievedContext(
        chunks=state["retrieved_chunks"],
        meetings=state["meeting_analysis"],
        knowledge=state["knowledge_entities"],
    )
    history = _format_history(state.get("conversation_history", []))
    context = context_builder.build(retrieved_context)
    context = f"Conversation History:\n{history}\n\nRetrieved Knowledge:\n{context}"
    return {"context": context}