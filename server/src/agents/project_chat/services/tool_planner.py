import json
import logging

from langchain_core.messages import HumanMessage

from src.agents.common.llm import LLMService
from src.agents.project_chat.prompts import TOOL_PLANNER_PROMPT
from src.agents.project_chat.schemas import ParsedQuery, RetrievalScope, ToolPlan
from src.mcp.schemas.common import ToolSpec

logger = logging.getLogger(__name__)


class ToolPlannerService:
    def __init__(self, llm: LLMService, tool_specs: list[ToolSpec]) -> None:
        self._llm = llm
        self._tool_specs = tool_specs

    def _format_specs(self) -> str:
        lines = []
        for spec in self._tool_specs:
            lines.append(f"- {spec.name}: {spec.description}")
            if spec.parameters:
                for param in spec.parameters:
                    req = "required" if param.required else "optional"
                    default = f" (default: {param.default})" if param.default is not None else ""
                    lines.append(f"    - {param.name} ({param.type}, {req}{default}): {param.description}")
        return "\n".join(lines)

    async def plan(
        self,
        parsed_query: ParsedQuery,
        scope: RetrievalScope,
    ) -> ToolPlan:
        prompt = TOOL_PLANNER_PROMPT.format(
            tool_specs=self._format_specs(),
            question=parsed_query.original_question,
            intent=parsed_query.intent,
            workspace_name=parsed_query.workspace_name or "none",
            client_name=parsed_query.client_name or "none",
            project_name=parsed_query.project_name or "none",
            meeting_name=parsed_query.meeting_name or "none",
            keywords=", ".join(parsed_query.keywords) if parsed_query.keywords else "none",
            workspace_ids=", ".join(scope.workspace_ids) if scope.workspace_ids else "none",
            client_ids=", ".join(scope.client_ids) if scope.client_ids else "none",
            project_ids=", ".join(scope.project_ids) if scope.project_ids else "none",
            meeting_ids=", ".join(scope.meeting_ids) if scope.meeting_ids else "none",
        )

        structured = self._llm.with_structured_output(ToolPlan)
        response = await structured.ainvoke([HumanMessage(content=prompt)])

        logger.info(
            "Tool plan: %d MCP calls, rag_needed=%s",
            len(response.tool_calls),
            response.rag_needed,
        )
        for call in response.tool_calls:
            logger.info("  -> %s(%s)", call.tool, call.args)

        return response
