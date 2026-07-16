from __future__ import annotations

import logging
from dataclasses import dataclass, field

from src.agents.project_chat.schemas import RetrievedKnowledge
from src.mcp.dispatcher import MCPDispatcher
from src.mcp.schemas.common import ToolResult
from src.mcp.schemas.execution_context import ToolExecutionContext

logger = logging.getLogger(__name__)


@dataclass
class HydratedEntity:
    """A RAG entity enriched with structured MCP data."""

    entity: RetrievedKnowledge
    source: str  # "mcp" or "rag"
    data: dict | list | None = None


class EntityHydrator:
    """Enriches RAG entities by dispatching to the appropriate MCP tool.

    The hydrator resolves which tool to call from the hydration_tools mapping
    built by the ToolRegistry. No entity-specific logic is hardcoded.
    """

    def __init__(
        self,
        dispatcher: MCPDispatcher,
        hydration_tools: dict[str, str],
    ) -> None:
        self._dispatcher = dispatcher
        self._hydration_tools = hydration_tools

    async def hydrate(
        self,
        entities: list[RetrievedKnowledge],
        context: ToolExecutionContext,
    ) -> list[HydratedEntity]:
        """Hydrate RAG entities via MCP tools in parallel.

        For each entity, if a hydration tool exists for its entity_type,
        dispatch to it. On failure, fall back to the original RAG entity.
        """
        import asyncio

        tasks = []
        for entity in entities:
            tool_name = self._hydration_tools.get(entity.entity_type)
            if tool_name is None:
                tasks.append(self._fallback(entity))
                continue
            tasks.append(self._dispatch(tool_name, entity, context))

        return await asyncio.gather(*tasks)

    async def _dispatch(
        self,
        tool_name: str,
        entity: RetrievedKnowledge,
        context: ToolExecutionContext,
    ) -> HydratedEntity:
        """Dispatch to a hydration tool and wrap the result."""
        id_param = f"{entity.entity_type}_id"
        try:
            result = await self._dispatcher.dispatch(
                tool_name,
                context,
                **{id_param: entity.entity_id},
            )
            if result.success and result.data is not None:
                logger.debug(
                    "Hydrated %s %s via %s",
                    entity.entity_type,
                    entity.entity_id,
                    tool_name,
                )
                return HydratedEntity(
                    entity=entity,
                    source="mcp",
                    data=result.data if isinstance(result.data, (dict, list)) else {"value": result.data},
                )
            logger.debug(
                "Hydration returned no data for %s %s: %s",
                entity.entity_type,
                entity.entity_id,
                result.message,
            )
            return self._fallback(entity)
        except Exception:
            logger.warning(
                "Hydration failed for %s %s via %s",
                entity.entity_type,
                entity.entity_id,
                tool_name,
                exc_info=True,
            )
            return self._fallback(entity)

    @staticmethod
    def _fallback(entity: RetrievedKnowledge) -> HydratedEntity:
        return HydratedEntity(entity=entity, source="rag")
