import json
import logging
from time import perf_counter
from typing import Any, AsyncGenerator

from langchain_core.messages import AIMessageChunk

from src.agents.project_chat.graph import get_compiled_graph
from src.agents.project_chat.schemas import Citation
from src.agents.project_chat.services.summarizer import ConversationSummarizer
from src.agents.project_chat.state import ChatState
from src.exceptions.base import AuthorizationError, BaseAPIException
from src.schemas.assistant_schema import AssistantCitationResponse

logger = logging.getLogger(__name__)

_MAX_EXCHANGES = 4
_MAX_MESSAGES = _MAX_EXCHANGES * 2


class ChatService:
    def __init__(
        self,
        db,
        user_context: dict[str, Any] | None = None,
    ) -> None:
        self._db = db
        self._user_context = user_context or {}
        self._graph = get_compiled_graph()
        self._summarizer = ConversationSummarizer()

    async def chat(
        self,
        question: str,
        thread_id: str = "",
    ) -> dict[str, object]:
        question = question.strip()
        if not question:
            raise BaseAPIException(message="Question cannot be empty", status_code=400)

        configurable = {"thread_id": thread_id} if thread_id else {}
        configurable["db"] = self._db
        config = {"configurable": configurable}

        existing_messages, existing_summary = await self._load_memory(config)

        initial_state: ChatState = {
            "question": question,
            "user_context": self._user_context,
            "parsed_query": None,
            "retrieval_scope": None,
            "tool_plan": None,
            "retrieved_chunks": [],
            "meeting_analysis": [],
            "knowledge_entities": [],
            "tool_results": [],
            "context": None,
            "answer": None,
            "citations": [],
            "messages": existing_messages,
            "conversation_summary": existing_summary,
        }

        start = perf_counter()

        try:
            result = await self._graph.ainvoke(initial_state, config=config)
        except AuthorizationError as exc:
            raise BaseAPIException(message=str(exc), status_code=403)
        except Exception as exc:
            logger.error("Assistant query failed: %s", exc, exc_info=True)
            raise BaseAPIException(
                message="Unable to process assistant request",
                status_code=500,
            ) from exc

        elapsed = perf_counter() - start

        logger.info("Assistant query completed in: %.2fs", elapsed)

        answer = result.get("answer", "")

        tool_plan = result.get("tool_plan")
        if tool_plan and getattr(tool_plan, "out_of_scope", False):
            answer = "This question is outside the scope of this assistant. I can only help with project-related queries such as meetings, action items, requirements, and Jira issues."
        elif not context.strip() or (not retrieved_chunks and not meeting_analysis and not knowledge_entities):
            answer = "I couldn't find relevant context for that question."

        serialized_citations = self._format_citations(
            result.get("citations", []),
            result,
        )

        if thread_id:
            await self._update_memory(config, question, answer, existing_messages, existing_summary)

        response: dict[str, object] = {
            "answer": answer,
            "citations": serialized_citations,
        }
        if retrieval_scope and retrieval_scope.ambiguous_entities:
            response["ambiguous_entities"] = {
                k: [c.model_dump() for c in v]
                for k, v in retrieval_scope.ambiguous_entities.items()
            }

        return response

    async def chat_stream(
        self,
        question: str,
        thread_id: str = "",
    ) -> AsyncGenerator[str, None]:
        question = question.strip()
        if not question:
            yield json.dumps({"error": "Question cannot be empty"}) + "\n"
            return

        configurable = {"thread_id": thread_id} if thread_id else {}
        configurable["db"] = self._db
        config = {"configurable": configurable}

        existing_messages, existing_summary = await self._load_memory(config)

        initial_state: ChatState = {
            "question": question,
            "user_context": self._user_context,
            "parsed_query": None,
            "retrieval_scope": None,
            "tool_plan": None,
            "retrieved_chunks": [],
            "meeting_analysis": [],
            "knowledge_entities": [],
            "tool_results": [],
            "context": None,
            "answer": None,
            "citations": [],
            "messages": existing_messages,
            "conversation_summary": existing_summary,
        }

        answer = ""
        citations: list[dict[str, object | None]] = []

        try:
            async for event in self._graph.astream_events(initial_state, config=config, version="v2"):
                kind = event.get("event")
                if kind == "on_chat_model_stream":
                    chunk = event.get("data", {}).get("chunk")
                    if isinstance(chunk, AIMessageChunk):
                        token = chunk.content or ""
                        if token:
                            answer += token
                            yield f"data: {json.dumps({'token': token})}\n\n"
                elif kind == "on_chain_end":
                    name = event.get("name", "")
                    if name == "generate_response":
                        output = event.get("data", {}).get("output", {})
                        citations = self._format_citations(
                            output.get("citations", []),
                            output,
                        )
                        yield f"data: {json.dumps({'done': True, 'citations': citations})}\n\n"
        except AuthorizationError as exc:
            yield f"data: {json.dumps({'error': str(exc)})}\n\n"
            return
        except Exception as exc:
            logger.error("Assistant stream failed: %s", exc, exc_info=True)
            yield f"data: {json.dumps({'error': 'Unable to process assistant request'})}\n\n"
            return

        if thread_id and answer:
            await self._update_memory(config, question, answer, existing_messages, existing_summary)

    async def _load_memory(
        self,
        config: dict[str, Any],
    ) -> tuple[list[dict[str, str]], str]:
        if not config:
            return [], ""
        try:
            snapshot = await self._graph.aget_state(config)
            if snapshot is not None and snapshot.values:
                values = snapshot.values
                return (
                    values.get("messages", []),
                    values.get("conversation_summary", ""),
                )
        except Exception as exc:
            logger.debug("No existing checkpoint for config %s: %s", config, exc)
        return [], ""

    async def _update_memory(
        self,
        config: dict[str, Any],
        question: str,
        answer: str,
        existing_messages: list[dict[str, str]],
        existing_summary: str,
    ) -> None:
        updated_messages = existing_messages + [
            {"role": "user", "content": question},
            {"role": "assistant", "content": answer},
        ]

        summary = existing_summary
        if len(updated_messages) > _MAX_MESSAGES:
            to_summarize = updated_messages[: -_MAX_MESSAGES]
            summary = await self._summarizer.summarize(existing_summary, to_summarize)
            updated_messages = updated_messages[-_MAX_MESSAGES:]

        await self._graph.aupdate_state(
            config,
            {
                "messages": updated_messages,
                "conversation_summary": summary,
                "parsed_query": None,
                "retrieval_scope": None,
                "tool_plan": None,
                "retrieved_chunks": [],
                "meeting_analysis": [],
                "knowledge_entities": [],
                "tool_results": [],
                "context": None,
                "answer": None,
                "citations": [],
            },
        )

    @staticmethod
    def _format_citations(
        citations: list[Citation | dict[str, Any]],
        result: dict[str, Any],
    ) -> list[dict[str, object | None]]:
        chunks = result.get("retrieved_chunks", [])
        meetings = {meeting.meeting_id: meeting for meeting in result.get("meeting_analysis", [])}
        knowledge = {item.entity_id: item for item in result.get("knowledge_entities", [])}

        formatted: list[dict[str, object | None]] = []
        for citation in citations:
            if isinstance(citation, Citation):
                source_type = citation.source_type
                source_id = citation.source_id
            else:
                source_type = citation.get("source_type")
                source_id = citation.get("source_id")

            if source_type == "chunk":
                source = next((chunk for chunk in chunks if chunk.chunk_id == source_id), None)
                if source is None:
                    continue
                meeting = meetings.get(source.meeting_id)
                formatted.append(
                    AssistantCitationResponse(
                        meeting_id=source.meeting_id,
                        meeting_title=(
                            meeting.title if meeting else source.metadata.get("meeting_title") or ""
                        ),
                        meeting_date=meeting.meeting_date if meeting else None,
                        chunk_index=source.chunk_index,
                    ).model_dump()
                )
            elif source_type == "meeting":
                meeting = meetings.get(source_id)
                if meeting is None:
                    continue
                formatted.append(
                    AssistantCitationResponse(
                        meeting_id=meeting.meeting_id,
                        meeting_title=meeting.title,
                        meeting_date=meeting.meeting_date,
                        chunk_index=None,
                    ).model_dump()
                )
            elif source_type == "knowledge":
                item = knowledge.get(source_id)
                if item is None:
                    continue
                meeting = meetings.get(item.meeting_id)
                formatted.append(
                    AssistantCitationResponse(
                        meeting_id=item.meeting_id,
                        meeting_title=item.meeting_title or (meeting.title if meeting else ""),
                        meeting_date=meeting.meeting_date if meeting else None,
                        chunk_index=None,
                    ).model_dump()
                )

        return formatted
