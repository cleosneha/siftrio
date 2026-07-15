import logging
from typing import Any

from mcp.server.fastmcp import Context
from sqlalchemy.ext.asyncio import AsyncSession

from src.mcp.context import MCPContext
from src.mcp.dependencies import get_auth_context, get_session_factory
from src.mcp.schemas.common import ToolResult

logger = logging.getLogger(__name__)


async def run_tool(
    ctx: Context,  # type: ignore[type-arg]
    tool_name: str,
    func: Any,
    **kwargs: Any,
) -> ToolResult:
    auth = get_auth_context(ctx)
    session_factory = get_session_factory(ctx)

    logger.info(
        "mcp.tool.start tool=%s workspace=%s user=%s",
        tool_name,
        auth.workspace_id,
        auth.user_id,
    )

    async with session_factory() as db:
        try:
            result = await func(db=db, auth=auth, **kwargs)
            logger.info("mcp.tool.complete tool=%s", tool_name)
            return result
        except Exception as e:
            logger.error("mcp.tool.error tool=%s error=%s", tool_name, str(e))
            raise
