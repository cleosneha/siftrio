import json
import logging
from time import perf_counter
from typing import Any, AsyncGenerator

from langchain_core.messages import AIMessageChunk

from src.agents.graph import compiled_graph
from src.agents.schemas import Citation
from src.agents.state import ChatState
from src.exceptions.base import AuthorizationError, BaseAPIException
from src.schemas.assistant_schema import AssistantCitationResponse

logger = logging.getLogger(__name__)


class ChatService:
    def __init__(
        self,
        db,
        user_context: dict[str, Any] | None = None,
    ) -> None:
        self._db = db
        self._user_context = user_context or {}
        self._graph = compiled_graph

    async def chat(
        self,
        question: str,
        conversation_history: list[dict[str, str]] | None = None,
    ) -> dict[str, object]:
        question = question.strip()
        if not question:
            raise BaseAPIException(message="Question cannot be empty", status_code=400)

        initial_state: ChatState = {
            "question": question,
            "db": self._db,
            "user_context": self._user_context,
            "parsed_query": None,
            "retrieval_scope": None,
            "retrieved_chunks": [],
            "meeting_analysis": [],
            "knowledge_entities": [],
            "context": None,
            "answer": None,
            "citations": [],
            "conversation_history": conversation_history or [],
        }

        start = perf_counter()

        try:
            result = await self._graph.ainvoke(initial_state)
        except AuthorizationError as exc:
            raise BaseAPIException(message=str(exc), status_code=403)
        except Exception as exc:
            logger.error("Assistant query failed: %s", exc, exc_info=True)
            raise BaseAPIException(
                message="Unable to process assistant request",
                status_code=500,
            ) from exc

        elapsed = perf_counter() - start

        parsed_query = result.get("parsed_query")
        retrieval_scope = result.get("retrieval_scope")
        retrieved_chunks = result.get("retrieved_chunks", [])
        meeting_analysis = result.get("meeting_analysis", [])
        knowledge_entities = result.get("knowledge_entities", [])
        context = result.get("context") or ""

        logger.info("Assistant incoming question: %s", question)
        logger.info(
            "Assistant parsed query: %s",
            parsed_query.model_dump() if parsed_query else None,
        )
        logger.info(
            "Assistant retrieval scope: %s",
            retrieval_scope.model_dump() if retrieval_scope else None,
        )
        logger.info("Assistant retrieved transcript chunks: %s", len(retrieved_chunks))
        logger.info("Assistant retrieved meetings: %s", len(meeting_analysis))
        logger.info("Assistant retrieved knowledge entities: %s", len(knowledge_entities))
        logger.info("Assistant context length: %s chars", len(context))
        logger.info("Assistant query completed in: %.2fs", elapsed)

        answer = result.get("answer", "")

        if not context.strip() or (not retrieved_chunks and not meeting_analysis and not knowledge_entities):
            answer = "I couldn't find relevant context for that question."

        serialized_citations = self._format_citations(
            result.get("citations", []),
            result,
        )

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
        conversation_history: list[dict[str, str]] | None = None,
    ) -> AsyncGenerator[str, None]:
        question = question.strip()
        if not question:
            yield json.dumps({"error": "Question cannot be empty"}) + "\n"
            return

        initial_state: ChatState = {
            "question": question,
            "db": self._db,
            "user_context": self._user_context,
            "parsed_query": None,
            "retrieval_scope": None,
            "retrieved_chunks": [],
            "meeting_analysis": [],
            "knowledge_entities": [],
            "context": None,
            "answer": None,
            "citations": [],
            "conversation_history": conversation_history or [],
        }

        try:
            async for event in self._graph.astream_events(initial_state, version="v2"):
                kind = event.get("event")
                if kind == "on_chat_model_stream":
                    chunk = event.get("data", {}).get("chunk")
                    if isinstance(chunk, AIMessageChunk):
                        token = chunk.content or ""
                        if token:
                            yield f"data: {json.dumps({'token': token})}\n\n"
                elif kind == "on_chain_end":
                    name = event.get("name", "")
                    if name == "generate_response":
                        output = event.get("data", {}).get("output", {})
                        yield f"data: {json.dumps({'done': True, 'citations': self._format_citations(
                            output.get('citations', []),
                            output,
                        )})}\n\n"
        except AuthorizationError as exc:
            yield f"data: {json.dumps({'error': str(exc)})}\n\n"
        except Exception as exc:
            logger.error("Assistant stream failed: %s", exc, exc_info=True)
            yield f"data: {json.dumps({'error': 'Unable to process assistant request'})}\n\n"

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
