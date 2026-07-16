from __future__ import annotations

import importlib
import logging
from typing import TYPE_CHECKING, Any

from src.mcp.schemas.common import ToolSpec

if TYPE_CHECKING:
    from mcp.server.fastmcp import FastMCP

    from src.mcp.dispatcher import MCPDispatcher

logger = logging.getLogger(__name__)

TOOL_MODULES = [
    "src.mcp.tools.meetings",
    "src.mcp.tools.projects",
    "src.mcp.tools.workspaces",
    "src.mcp.tools.action_items",
    "src.mcp.tools.knowledge",
    "src.mcp.tools.jira",
    "src.mcp.tools.calendar",
]


class ToolRegistry:
    def __init__(
        self,
        mcp_server: FastMCP,
        dispatcher: MCPDispatcher,
    ) -> None:
        self.mcp = mcp_server
        self.dispatcher = dispatcher
        self._specs: list[ToolSpec] = []
        self._registered: list[str] = []

    def register_all(self) -> None:
        for module_path in TOOL_MODULES:
            try:
                module = importlib.import_module(module_path)
                if hasattr(module, "register"):
                    module.register(self.mcp, self.dispatcher)
                    self._registered.append(module_path)
                    logger.info("Registered MCP tool module: %s", module_path)
                if hasattr(module, "TOOL_SPECS"):
                    self._specs.extend(module.TOOL_SPECS)
            except ImportError:
                logger.debug(
                    "MCP tool module %s not found, skipping", module_path
                )
            except Exception:
                logger.exception(
                    "Failed to register MCP tool module: %s", module_path
                )

        logger.info(
            "MCP tool registry complete: %d modules registered, %d tool specs",
            len(self._registered),
            len(self._specs),
        )

    def add_spec(self, spec: ToolSpec) -> None:
        self._specs.append(spec)

    def all_specs(self) -> list[ToolSpec]:
        return list(self._specs)

    def hydration_tools(self) -> dict[str, str]:
        """Returns {entity_type: tool_name} for all hydration-capable tools."""
        return {
            spec.entity_type: spec.name
            for spec in self._specs
            if spec.entity_type is not None
        }

    @property
    def registered_modules(self) -> list[str]:
        return list(self._registered)
