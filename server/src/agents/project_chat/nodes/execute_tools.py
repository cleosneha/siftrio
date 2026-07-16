import asyncio
import logging
from uuid import UUID

from langgraph.types import RunnableConfig

from src.agents.project_chat.retrievers.hybrid import HybridRetriever
from src.agents.project_chat.schemas import RetrievedContext
from src.agents.project_chat.services.entity_hydrator import EntityHydrator
from src.agents.project_chat.state import ChatState
from src.mcp.dispatcher import MCPDispatcher
from src.mcp.schemas.common import ToolResult
from src.mcp.schemas.execution_context import ToolExecutionContext

logger = logging.getLogger(__name__)


async def execute_tools(
    state: ChatState,
    dispatcher: MCPDispatcher,
    retriever: HybridRetriever,
    hydrator: EntityHydrator,
    config: RunnableConfig | None = None,
) -> dict[str, object]:
    tool_plan = state.get("tool_plan")
    retrieval_scope = state.get("retrieval_scope")
    db = config["configurable"]["db"] if config else None

    if db is None:
        return {"tool_results": [], "retrieved_chunks": [], "meeting_analysis": [], "knowledge_entities": []}

    if tool_plan and tool_plan.out_of_scope:
        return {"tool_results": [], "retrieved_chunks": [], "meeting_analysis": [], "knowledge_entities": []}

    user_context = state["user_context"]
    context = ToolExecutionContext(
        user_id=UUID(user_context["id"]),
        workspace_ids=[UUID(wid) for wid in retrieval_scope.workspace_ids] if retrieval_scope else [],
    )

    tasks = []

    if tool_plan and tool_plan.tool_calls:
        for call in tool_plan.tool_calls:
            tasks.append(dispatcher.dispatch(call.tool, context, **call.args))

    rag_task = None
    if tool_plan and tool_plan.rag_needed and retrieval_scope:
        rag_task = retriever.retrieve(db, retrieval_scope)
    elif retrieval_scope and not tool_plan:
        rag_task = retriever.retrieve(db, retrieval_scope)

    if rag_task:
        tasks.append(rag_task)

    if not tasks:
        return {"tool_results": [], "retrieved_chunks": [], "meeting_analysis": [], "knowledge_entities": []}

    results = await asyncio.gather(*tasks, return_exceptions=True)

    tool_results: list[ToolResult] = []
    retrieved_chunks = []
    meeting_analysis = []
    knowledge_entities = []

    for r in results:
        if isinstance(r, RetrievedContext):
            retrieved_chunks = r.chunks
            meeting_analysis = r.meetings
            knowledge_entities = r.knowledge
        elif isinstance(r, ToolResult):
            tool_results.append(r)
        elif isinstance(r, Exception):
            logger.error("Tool execution failed: %s", r)
            tool_results.append(ToolResult(success=False, message=str(r)))

    if knowledge_entities:
        hydrated = await hydrator.hydrate(knowledge_entities, context)
        non_hydrated = []
        for h in hydrated:
            if h.source == "mcp" and h.data is not None:
                tool_results.append(ToolResult(success=True, data=h.data))
            else:
                non_hydrated.append(h.entity)
        knowledge_entities = non_hydrated

    return {
        "tool_results": tool_results,
        "retrieved_chunks": retrieved_chunks,
        "meeting_analysis": meeting_analysis,
        "knowledge_entities": knowledge_entities,
    }
