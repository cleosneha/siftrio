import logging
from typing import Annotated

from mcp.server.fastmcp import Context
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.mcp.context import MCPContext
from src.services.membership_service import MembershipService

logger = logging.getLogger(__name__)


def get_session_factory(ctx: Context) -> async_sessionmaker:  # type: ignore[type-arg]
    lifespan_ctx: MCPContext = ctx.request_context.lifespan_context
    return lifespan_ctx.session_factory  # type: ignore[attr-defined]


def get_auth_context(ctx: Context) -> MCPContext:  # type: ignore[type-arg]
    lifespan_ctx: MCPContext = ctx.request_context.lifespan_context
    return MCPContext(
        workspace_id=lifespan_ctx.workspace_id,
        user_id=lifespan_ctx.user_id,
    )
