import logging

from langgraph.types import RunnableConfig

from src.agents.project_chat.schemas import ToolPlan
from src.agents.project_chat.services.tool_planner import ToolPlannerService
from src.agents.project_chat.state import ChatState

logger = logging.getLogger(__name__)


async def plan_tools(
    state: ChatState,
    planner: ToolPlannerService,
    config: RunnableConfig | None = None,
) -> dict[str, object]:
    parsed_query = state.get("parsed_query")
    retrieval_scope = state.get("retrieval_scope")

    if parsed_query is None or retrieval_scope is None:
        return {"tool_plan": ToolPlan(tool_calls=[], rag_needed=True, rag_query=state["question"])}

    if retrieval_scope.ambiguous_entities:
        return {"tool_plan": ToolPlan(tool_calls=[], rag_needed=True, rag_query=state["question"])}

    tool_plan = await planner.plan(parsed_query, retrieval_scope)
    return {"tool_plan": tool_plan}
