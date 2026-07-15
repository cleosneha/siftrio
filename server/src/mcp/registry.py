import importlib
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mcp.server.fastmcp import FastMCP

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
    def __init__(self, mcp_server: "FastMCP") -> None:
        self.mcp = mcp_server
        self._registered: list[str] = []

    def register_all(self) -> None:
        for module_path in TOOL_MODULES:
            try:
                module = importlib.import_module(module_path)
                if hasattr(module, "register"):
                    module.register(self.mcp)
                    self._registered.append(module_path)
                    logger.info("Registered MCP tool module: %s", module_path)
                else:
                    logger.debug(
                        "MCP tool module %s has no register() function, skipping",
                        module_path,
                    )
            except ImportError:
                logger.debug(
                    "MCP tool module %s not found, skipping", module_path
                )
            except Exception:
                logger.exception(
                    "Failed to register MCP tool module: %s", module_path
                )

        logger.info(
            "MCP tool registry complete: %d modules registered",
            len(self._registered),
        )

    @property
    def registered_modules(self) -> list[str]:
        return list(self._registered)
