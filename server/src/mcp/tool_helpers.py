import logging
from typing import Any

from mcp.server.fastmcp import Context
from sqlalchemy.ext.asyncio import AsyncSession

from src.mcp.context import MCPContext
from src.mcp.dependencies import get_auth_context
from src.mcp.schemas.common import ToolResult

logger = logging.getLogger(__name__)


async def run_tool(
    ctx: Context,  # type: ignore[type-arg]
    tool_name: str,
    func: Any,
    **kwargs: Any,
) -> ToolResult:
    from src.core.database import async_session_factory

    auth = get_auth_context(ctx)

    logger.info(
        "mcp.tool.start tool=%s user=%s workspaces=%d",
        tool_name,
        auth.user_id,
        len(auth.workspace_ids),
    )

    async with async_session_factory() as db:
        try:
            result = await func(db=db, auth=auth, **kwargs)
            logger.info("mcp.tool.complete tool=%s", tool_name)
            return result
        except Exception as e:
            logger.error("mcp.tool.error tool=%s error=%s", tool_name, str(e))
            raise
