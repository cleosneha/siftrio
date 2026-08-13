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
from src.models.base import MemberRole, rank
from src.repositories.meeting_repository import MeetingRepository
from src.repositories.resource_repository import ResourceRepository
from src.services.membership_service import MembershipService

logger = logging.getLogger(__name__)

WRITE_TOOLS = {"update_action_item_status"}


async def _effective_role_for_call(
    db, user_id: UUID, tool_name: str, args: dict
) -> MemberRole | None:
    """Effective role on the resource a write tool targets (§8.8)."""
    level: str | None = None
    resource_id: UUID | None = None

    if args.get("project_id"):
        level, resource_id = "project", UUID(args["project_id"])
    elif args.get("client_id"):
        level, resource_id = "client", UUID(args["client_id"])
    elif args.get("workspace_id"):
        level, resource_id = "workspace", UUID(args["workspace_id"])
    elif args.get("meeting_id"):
        meeting = await MeetingRepository(db).get_by_id(UUID(args["meeting_id"]))
        if meeting and meeting.project_id:
            level, resource_id = "project", meeting.project_id
        elif meeting:
            level, resource_id = "client", meeting.client_id
    elif args.get("action_item_id"):
        project_id = await ResourceRepository(db).get_project_id(
            "action_item", UUID(args["action_item_id"])
        )
        if project_id:
            level, resource_id = "project", project_id

    if level is None or resource_id is None:
        return None
    return await MembershipService(db).get_effective_role(level, resource_id, user_id)


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
    user_id = UUID(user_context["id"])
    context = ToolExecutionContext(
        user_id=user_id,
        workspace_ids=[UUID(wid) for wid in retrieval_scope.workspace_ids] if retrieval_scope else [],
    )

    tasks = []
    tool_results: list[ToolResult] = []

    if tool_plan and tool_plan.tool_calls:
        for call in tool_plan.tool_calls:
            if call.tool in WRITE_TOOLS:
                role = await _effective_role_for_call(db, user_id, call.tool, call.args or {})
                if rank(role) < rank(MemberRole.MEMBER):
                    logger.warning(
                        "Assistant write tool '%s' denied for user %s (role=%s)",
                        call.tool,
                        user_id,
                        role,
                    )
                    tool_results.append(
                        ToolResult(
                            success=False,
                            message=f"Tool '{call.tool}' requires member or higher",
                        )
                    )
                    continue
            tasks.append(dispatcher.dispatch(call.tool, context, **call.args))

    rag_task = None
    if tool_plan and tool_plan.rag_needed and retrieval_scope:
        rag_task = retriever.retrieve(db, retrieval_scope)
    elif retrieval_scope and not tool_plan:
        rag_task = retriever.retrieve(db, retrieval_scope)

    if rag_task:
        tasks.append(rag_task)

    if not tasks:
        return {"tool_results": tool_results, "retrieved_chunks": [], "meeting_analysis": [], "knowledge_entities": []}

    results = await asyncio.gather(*tasks, return_exceptions=True)

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
