from src.agents.project_chat.schemas import RetrievedContext
from src.agents.project_chat.services.context_builder import ContextBuilderService
from src.agents.project_chat.state import ChatState


def _format_messages(messages: list[dict[str, str]], max_pairs: int = 4) -> str:
    if not messages:
        return "(no previous conversation)"
    recent = messages[-(max_pairs * 2):]
    lines = []
    for msg in recent:
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
    messages = state.get("messages", [])
    summary = state.get("conversation_summary", "")

    recent = _format_messages(messages)

    parts = []
    if summary:
        parts.append(f"Conversation Summary:\n{summary}")
    if recent and recent != "(no previous conversation)":
        parts.append(f"Recent Conversation:\n{recent}")

    parts.append(f"Retrieved Knowledge:\n{context_builder.build(retrieved_context)}")

    context = "\n\n".join(parts)
    return {"context": context}
