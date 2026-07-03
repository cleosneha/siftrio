import re

from langchain_core.messages import HumanMessage

from src.agents.prompts import ANSWER_PROMPT
from src.agents.schemas import Citation
from src.agents.services.llm import LLMService
from src.agents.state import ChatState


_CITATION_PATTERN = re.compile(r"\[(chunk|meeting|knowledge):([^\]]+)\]")


def _message_content_to_text(content: object) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and "text" in item:
                parts.append(str(item["text"]))
            else:
                parts.append(str(item))
        return "".join(parts)
    return str(content)


def _extract_citations(text: str, chunks, meetings, knowledge) -> list[Citation]:
    chunk_lookup = {c.chunk_id: c for c in chunks}
    meeting_lookup = {m.meeting_id: m for m in meetings}
    knowledge_lookup = {k.entity_id: k for k in knowledge}

    citations: list[Citation] = []
    seen: set[tuple[str, str]] = set()

    for source_type, source_id in _CITATION_PATTERN.findall(text):
        key = (source_type, source_id)
        if key in seen:
            continue
        seen.add(key)

        if source_type == "chunk":
            source = chunk_lookup.get(source_id)
            if source is None:
                continue
            citations.append(Citation(
                source_type="chunk",
                source_id=source_id,
                title=source.metadata.get("meeting_title") or f"Chunk {source.chunk_index}",
                excerpt=source.chunk_text,
                relevance_score=source.score,
            ))
        elif source_type == "meeting":
            source = meeting_lookup.get(source_id)
            if source is None:
                continue
            citations.append(Citation(
                source_type="meeting",
                source_id=source_id,
                title=source.title,
                excerpt=source.summary or source.title,
            ))
        else:
            source = knowledge_lookup.get(source_id)
            if source is None:
                continue
            citations.append(Citation(
                source_type="knowledge",
                source_id=source_id,
                title=source.title,
                excerpt=source.description or source.title,
            ))

    return citations


async def generate_response(
    state: ChatState,
    llm: LLMService,
) -> dict[str, object]:
    question = state["question"]
    context = state["context"] or ""
    history = state.get("conversation_history", [])

    if state.get("retrieval_scope") and state["retrieval_scope"].ambiguous_entities:
        parts = []
        for entity_type, candidates in state["retrieval_scope"].ambiguous_entities.items():
            names = ", ".join(c.name for c in candidates)
            parts.append(f"multiple {entity_type}s ({names})")
        note = f"[Note: The query matched {' and '.join(parts)}. The same name may appear as both a client and a project.]\n\n"
        context = note + context

    conversation_text = ""
    if history:
        lines = []
        for msg in history[-5:]:
            role = "User" if msg.get("role") == "user" else "Assistant"
            lines.append(f"{role}: {msg.get('content', '')}")
        conversation_text = "\n".join(lines)

    prompt = ANSWER_PROMPT.format(
        conversation_history=conversation_text or "(no previous conversation)",
        context=context,
        question=question,
    )

    response = await llm.invoke([HumanMessage(content=prompt)])
    answer = _message_content_to_text(response.content)
    citations = _extract_citations(
        answer,
        state["retrieved_chunks"],
        state["meeting_analysis"],
        state["knowledge_entities"],
    )

    return {
        "answer": answer,
        "citations": citations,
    }
