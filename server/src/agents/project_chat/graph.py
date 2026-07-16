from __future__ import annotations

import logging
from functools import partial
from typing import TYPE_CHECKING

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from src.agents.common.llm import LLMService
from src.agents.project_chat.nodes.build_context import build_context
from src.agents.project_chat.nodes.execute_tools import execute_tools
from src.agents.project_chat.nodes.generate_response import generate_response
from src.agents.project_chat.nodes.parse_query import parse_query
from src.agents.project_chat.nodes.plan_tools import plan_tools
from src.agents.project_chat.retrievers.hybrid import HybridRetriever
from src.agents.project_chat.services.context_builder import ContextBuilderService
from src.agents.project_chat.services.entity_hydrator import EntityHydrator
from src.agents.project_chat.services.query_parser import QueryParserService
from src.agents.project_chat.services.scope_builder import ScopeBuilderService
from src.agents.project_chat.services.tool_planner import ToolPlannerService
from src.agents.project_chat.state import ChatState

if TYPE_CHECKING:
    from src.mcp.dispatcher import MCPDispatcher
    from src.mcp.schemas.common import ToolSpec

logger = logging.getLogger(__name__)

_compiled_graph = None


def build_graph(
    dispatcher: MCPDispatcher,
    tool_specs: list[ToolSpec],
    hydration_tools: dict[str, str] | None = None,
):
    global _compiled_graph

    llm = LLMService()
    query_parser = QueryParserService(llm)
    planner = ToolPlannerService(llm, tool_specs)
    retriever = HybridRetriever()
    context_builder = ContextBuilderService()
    scope_builder = ScopeBuilderService()
    hydrator = EntityHydrator(dispatcher, hydration_tools or {})

    workflow = StateGraph(ChatState)

    workflow.add_node(
        "parse_query",
        partial(parse_query, query_parser=query_parser, scope_builder=scope_builder),
    )
    workflow.add_node("plan_tools", partial(plan_tools, planner=planner))
    workflow.add_node(
        "execute_tools",
        partial(execute_tools, dispatcher=dispatcher, retriever=retriever, hydrator=hydrator),
    )
    workflow.add_node("build_context", partial(build_context, context_builder=context_builder))
    workflow.add_node("generate_response", partial(generate_response, llm=llm))

    workflow.add_edge(START, "parse_query")
    workflow.add_edge("parse_query", "plan_tools")
    workflow.add_edge("plan_tools", "execute_tools")
    workflow.add_edge("execute_tools", "build_context")
    workflow.add_edge("build_context", "generate_response")
    workflow.add_edge("generate_response", END)

    _compiled_graph = workflow.compile(checkpointer=MemorySaver())
    logger.info("Assistant graph built successfully")
    return _compiled_graph


def get_compiled_graph():
    if _compiled_graph is None:
        raise RuntimeError("Graph not built yet. Call build_graph() first.")
    return _compiled_graph
