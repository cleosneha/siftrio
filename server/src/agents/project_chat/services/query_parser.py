from langchain_core.messages import HumanMessage

from src.agents.common.llm import LLMService
from src.agents.project_chat.schemas import ParsedQuery
from src.agents.project_chat.prompts import QUERY_PARSER_PROMPT


class QueryParserService:
    def __init__(self, llm: LLMService) -> None:
        self._llm = llm

    async def parse(self, question: str) -> ParsedQuery:
        prompt = QUERY_PARSER_PROMPT.format(question=question)
        structured = self._llm.with_structured_output(ParsedQuery)
        response = await structured.ainvoke([HumanMessage(content=prompt)])
        response.original_question = question
        return response
