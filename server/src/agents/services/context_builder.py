from src.agents.schemas import RetrievedContext


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
                    lines.append(f"  Summary: {m.summary[:300]}")
                lines.append(f"  Meeting ID: {m.meeting_id}")
            sections.append("\n".join(lines))

        if context.knowledge:
            lines = ["KNOWLEDGE ENTITIES"]
            for k in context.knowledge:
                source = f" (from: {k.meeting_title})" if k.meeting_title else ""
                lines.append(f"- [{k.entity_type}] {k.title} ({k.status}){source}")
                if k.description:
                    lines.append(f"  {k.description[:300]}")
            sections.append("\n".join(lines))

        if context.chunks:
            lines = ["SUPPORTING TRANSCRIPT CHUNKS"]
            for c in context.chunks:
                lines.append(
                    f"[Meeting: {c.meeting_id} | Chunk {c.chunk_index} | Score: {c.score}]"
                )
                lines.append(c.chunk_text)
                lines.append("")
            sections.append("\n".join(lines))

        return "\n\n".join(sections)
