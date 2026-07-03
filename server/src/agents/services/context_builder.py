from src.agents.schemas import RetrievedContext

_MAX_TOKENS = 6000
_CHARS_PER_TOKEN = 4


def _estimate_tokens(text: str) -> int:
    return len(text) // _CHARS_PER_TOKEN


class ContextBuilderService:
    @staticmethod
    def build(context: RetrievedContext) -> str:
        sections = []

        if context.meetings:
            lines = ["RELEVANT MEETINGS"]
            for m in context.meetings:
                date_str = m.meeting_date or "no date"
                lines.append(f"- {m.title} ({date_str})")
                if m.summary:
                    lines.append(f"  Summary: {m.summary}")
            sections.append("\n".join(lines))

        if context.chunks:
            lines = ["SUPPORTING TRANSCRIPT CHUNKS"]
            for c in context.chunks:
                title = c.metadata.get("meeting_title", "")
                lines.append(f"[{title} | Chunk {c.chunk_index} | Score: {c.score}]")
                lines.append(c.chunk_text)
                lines.append("")
            sections.append("\n".join(lines))

        if context.knowledge:
            lines = ["KNOWLEDGE ENTITIES"]
            for k in context.knowledge:
                source = f" (from: {k.meeting_title})" if k.meeting_title else ""
                lines.append(f"- [{k.entity_type}] {k.title} ({k.status}){source}")
                if k.description:
                    lines.append(f"  {k.description}")
            sections.append("\n".join(lines))

        combined = "\n\n".join(sections)
        return ContextBuilderService._truncate_if_needed(combined, context)

    @staticmethod
    def _truncate_if_needed(text: str, context: RetrievedContext) -> str:
        if _estimate_tokens(text) <= _MAX_TOKENS:
            return text

        sections = text.split("\n\n")
        kept_sections: list[str] = []
        meeting_count = 0
        chunk_lines: list[str] = []

        for section in sections:
            if section.startswith("RELEVANT MEETINGS"):
                kept_sections.append(section)
                meeting_count = section.count("\n- ")
            elif section.startswith("SUPPORTING TRANSCRIPT CHUNKS"):
                chunk_lines = section.split("\n")
            elif section.startswith("KNOWLEDGE ENTITIES"):
                kept_sections.append(section)

        truncated = "\n\n".join(kept_sections)
        if _estimate_tokens(truncated) + meeting_count * 50 + 500 > _MAX_TOKENS:
            return truncated

        sorted_chunks = sorted(context.chunks, key=lambda c: c.score, reverse=True)
        chunk_header = "SUPPORTING TRANSCRIPT CHUNKS"
        kept_chunks: list[str] = [chunk_header]

        for c in sorted_chunks:
            title = c.metadata.get("meeting_title", "")
            entry = f"[{title} | Chunk {c.chunk_index} | Score: {c.score}]\n{c.chunk_text}"
            if _estimate_tokens("\n".join(kept_chunks) + entry) + _estimate_tokens(truncated) <= _MAX_TOKENS:
                kept_chunks.append(entry)
            else:
                break

        if len(kept_chunks) > 1:
            truncated += "\n\n" + "\n\n".join(kept_chunks)

        return truncated
