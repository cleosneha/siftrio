import logging

from mcp.server.fastmcp import Context

from src.mcp.context import MCPContext

logger = logging.getLogger(__name__)


def get_auth_context(ctx: Context) -> MCPContext:  # type: ignore[type-arg]
    lifespan_ctx: MCPContext = ctx.request_context.lifespan_context
    return MCPContext(
        user_id=lifespan_ctx.user_id,
        workspace_ids=lifespan_ctx.workspace_ids,
    )
