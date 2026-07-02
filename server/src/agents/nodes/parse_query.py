from src.agents.services.query_parser import QueryParserService
from src.agents.state import ChatState


async def parse_query(
    state: ChatState,
    query_parser: QueryParserService,
) -> dict[str, object]:
    parsed_query = await query_parser.parse(state["question"])
    return {"parsed_query": parsed_query}