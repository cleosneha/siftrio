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

    async def _call_llm(self, parsed_query: ParsedQuery, scope: RetrievalScope) -> ToolPlan:
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
        return await structured.ainvoke([HumanMessage(content=prompt)])

    async def plan(
        self,
        parsed_query: ParsedQuery,
        scope: RetrievalScope,
    ) -> ToolPlan:
        query_text = scope.query_text
        query_lower = query_text.lower()

        STRUCTURED_KEYWORDS = [
            "action item", "action items", "due date", "requirement", "requirements",
            "decision", "decisions", "risk", "risks", "assignee", "jira",
            "blocker", "blockers", "status",
        ]
        has_structured_keyword = any(kw in query_lower for kw in STRUCTURED_KEYWORDS)
        has_scope_entities = bool(scope.project_ids or scope.meeting_ids)

        if not has_scope_entities and not has_structured_keyword:
            tool_plan = ToolPlan(
                tool_calls=[],
                rag_needed=True,
                rag_query=query_text,
                out_of_scope=False,
                routing_source="deterministic_entity_gap",
            )
            logger.info(
                "plan_tools | routing=%s | rag=%s | tools=%d | query=%.80s",
                tool_plan.routing_source,
                tool_plan.rag_needed,
                len(tool_plan.tool_calls),
                query_text,
            )
            return tool_plan

        tool_plan = await self._call_llm(parsed_query, scope)

        if has_scope_entities and has_structured_keyword:
            tool_plan.routing_source = "deterministic_keyword"
            tool_plan.rag_needed = False
        else:
            tool_plan.routing_source = "llm_ambiguous"

        logger.info(
            "plan_tools | routing=%s | rag=%s | tools=%d | query=%.80s",
            tool_plan.routing_source,
            tool_plan.rag_needed,
            len(tool_plan.tool_calls),
            query_text,
        )
        return tool_plan
