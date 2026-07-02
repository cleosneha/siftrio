from functools import partial

from langgraph.graph import END, START, StateGraph

from src.agents.nodes.build_context import build_context
from src.agents.nodes.generate_response import generate_response
from src.agents.nodes.parse_query import parse_query
from src.agents.nodes.retrieve_context import retrieve_context
from src.agents.retrievers.hybrid import HybridRetriever
from src.agents.services.context_builder import ContextBuilderService
from src.agents.services.llm import LLMService
from src.agents.services.query_parser import QueryParserService
from src.agents.services.scope_builder import ScopeBuilderService
from src.agents.state import ChatState


def _build_graph():
    llm = LLMService()
    query_parser = QueryParserService(llm)
    retriever = HybridRetriever()
    context_builder = ContextBuilderService()
    scope_builder = ScopeBuilderService()

    workflow = StateGraph(ChatState)

    workflow.add_node(
        "parse_query",
        partial(parse_query, query_parser=query_parser, scope_builder=scope_builder),
    )
    workflow.add_node("retrieve_context", partial(retrieve_context, retriever=retriever))
    workflow.add_node("build_context", partial(build_context, context_builder=context_builder))
    workflow.add_node("generate_response", partial(generate_response, llm=llm))

    workflow.add_edge(START, "parse_query")
    workflow.add_edge("parse_query", "retrieve_context")
    workflow.add_edge("retrieve_context", "build_context")
    workflow.add_edge("build_context", "generate_response")
    workflow.add_edge("generate_response", END)

    return workflow.compile()


compiled_graph = _build_graph()
