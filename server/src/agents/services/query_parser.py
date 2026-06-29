from langchain_core.messages import HumanMessage

from src.agents.schemas import ParsedQuery
from src.agents.prompts import QUERY_PARSER_PROMPT
from src.agents.services.llm import LLMService


class QueryParserService:
    def __init__(self, llm: LLMService) -> None:
        self._llm = llm

    async def parse(self, question: str) -> ParsedQuery:
        prompt = QUERY_PARSER_PROMPT.format(question=question)
        structured = self._llm.with_structured_output(ParsedQuery)
        response = await structured.ainvoke([HumanMessage(content=prompt)])
        response.original_question = question
        return response
