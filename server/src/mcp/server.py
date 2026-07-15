import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from mcp.server.auth.settings import AuthSettings
from mcp.server.fastmcp import FastMCP
from pydantic import AnyHttpUrl

from src.core.config import settings
from src.core.database import async_session_factory
from src.mcp.auth import WorkspaceApiKeyVerifier
from src.mcp.context import MCPContext
from src.mcp.registry import ToolRegistry

logger = logging.getLogger(__name__)


@asynccontextmanager
async def mcp_lifespan(server: FastMCP) -> AsyncIterator[MCPContext]:  # type: ignore[type-arg]
    logger.info("MCP server starting up")
    yield MCPContext(
        workspace_id=None,  # type: ignore[arg-type]
        user_id=None,  # type: ignore[arg-type]
    )
    logger.info("MCP server shutting down")


mcp_server = FastMCP(
    "Siftrio",
    instructions="Siftrio MCP Server - AI Project Memory + SDLC Copilot",
    lifespan=mcp_lifespan,
    token_verifier=WorkspaceApiKeyVerifier(async_session_factory),
    auth=AuthSettings(
        issuer_url=AnyHttpUrl(settings.BACKEND_URL),
        resource_server_url=AnyHttpUrl(f"{settings.BACKEND_URL}/mcp"),
        required_scopes=["mcp:read"],
    ),
)

mcp_app = mcp_server.streamable_http_app()


def mount_mcp(app: FastAPI) -> None:
    app.mount(
        "/mcp",
        app=mcp_app,
        name="mcp",
    )
    registry = ToolRegistry(mcp_server)
    registry.register_all()
    logger.info("MCP server mounted at /mcp")
