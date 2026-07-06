from langgraph.types import RunnableConfig

from src.agents.services.query_parser import QueryParserService
from src.agents.services.scope_builder import ScopeBuilderService
from src.agents.state import ChatState


async def parse_query(
    state: ChatState,
    query_parser: QueryParserService,
    scope_builder: ScopeBuilderService,
    config: RunnableConfig | None = None,
) -> dict[str, object]:
    question = state["question"]
    db = config["configurable"]["db"] if config else None
    user_context = state["user_context"]

    parsed_query = await query_parser.parse(question)
    retrieval_scope = await scope_builder.build(db, question, parsed_query, user_context)

    return {
        "parsed_query": parsed_query,
        "retrieval_scope": retrieval_scope,
    }
