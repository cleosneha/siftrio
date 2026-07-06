import logging

from langchain_core.messages import HumanMessage

from src.agents.common.llm import LLMService

logger = logging.getLogger(__name__)

_SUMMARIZE_PROMPT = """You are a conversation summarizer. Condense the following conversation into a concise summary that preserves key facts, questions, and answers. The summary will be used as context for follow-up questions in a meeting analysis assistant.

Existing summary (if any):
{existing_summary}

New messages to incorporate:
{new_messages}

Write a concise summary (2-4 sentences) that combines the existing summary with any new information from the latest messages. Do NOT include greetings, pleasantries, or meta-commentary."""


class ConversationSummarizer:
    def __init__(self, llm: LLMService | None = None) -> None:
        self._llm = llm or LLMService()

    async def summarize(
        self,
        existing_summary: str,
        messages_to_summarize: list[dict[str, str]],
    ) -> str:
        if not messages_to_summarize:
            return existing_summary

        new_lines = []
        for msg in messages_to_summarize:
            role = "User" if msg.get("role") == "user" else "Assistant"
            new_lines.append(f"{role}: {msg.get('content', '')}")

        prompt = _SUMMARIZE_PROMPT.format(
            existing_summary=existing_summary or "(no existing summary)",
            new_messages="\n".join(new_lines) or "(no messages)",
        )

        try:
            response = await self._llm.invoke([HumanMessage(content=prompt)])
            summary = response.content.strip() if response.content else ""
            return summary or existing_summary
        except Exception as exc:
            logger.warning("Summarization failed: %s", exc)
            return existing_summary
