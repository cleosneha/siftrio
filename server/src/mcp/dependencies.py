import logging

from mcp.server.auth.middleware.auth_context import get_access_token
from mcp.server.fastmcp import Context

from src.mcp.context import MCPContext

logger = logging.getLogger(__name__)


def get_auth_context(ctx: Context) -> MCPContext:  # type: ignore[type-arg]
    token = get_access_token()
    if token and token.claims:
        user_id = token.claims.get("user_id")
        workspace_ids = token.claims.get("workspace_ids", [])
        return MCPContext(
            user_id=user_id,
            workspace_ids=workspace_ids,
        )

    lifespan_ctx: MCPContext = ctx.request_context.lifespan_context
    return MCPContext(
        user_id=lifespan_ctx.user_id,
        workspace_ids=lifespan_ctx.workspace_ids,
    )
