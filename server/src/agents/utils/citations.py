import re

from src.agents.schemas import Citation, RetrievedChunk, RetrievedKnowledge, RetrievedMeeting


_CITATION_PATTERN = re.compile(r"\[(chunk|meeting|knowledge):([^\]]+)\]")


def extract_citations(
    text: str,
    chunks: list[RetrievedChunk],
    meetings: list[RetrievedMeeting],
    knowledge: list[RetrievedKnowledge],
) -> list[Citation]:
    chunk_lookup = {chunk.chunk_id: chunk for chunk in chunks}
    meeting_lookup = {meeting.meeting_id: meeting for meeting in meetings}
    knowledge_lookup = {item.entity_id: item for item in knowledge}

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
            title = source.metadata.get("meeting_title") or f"Chunk {source.chunk_index}"
            excerpt = source.chunk_text
            relevance_score = source.score
        elif source_type == "meeting":
            source = meeting_lookup.get(source_id)
            if source is None:
                continue
            title = source.title
            excerpt = source.summary or source.title
            relevance_score = None
        else:
            source = knowledge_lookup.get(source_id)
            if source is None:
                continue
            title = source.title
            excerpt = source.description or source.title
            relevance_score = None

        citations.append(
            Citation(
                source_type=source_type,
                source_id=source_id,
                title=title,
                excerpt=excerpt,
                relevance_score=relevance_score,
            )
        )

    return citations
