# MCP Server

Hosted Model Context Protocol (MCP) server for Siftrio.

Exposes Siftrio's business capabilities to AI assistants, Claude Desktop, VS Code, Cursor, and other MCP-compatible clients.

## Architecture

```
MCP Tool
      ↓
   Service Layer
      ↓
 Repository Layer
```

MCP tools never access repositories directly. All business logic lives in the existing service layer.

## Directory Structure

```
src/mcp/
├── server.py          # MCPServer instance, lifespan, FastAPI mount
├── registry.py        # Tool registration mechanism
├── auth.py            # TokenVerifier for workspace API keys
├── dependencies.py    # Resolvers for DB sessions, auth context
├── context.py         # Typed lifespan context (MCPContext)
├── tool_helpers.py    # Common patterns for tool functions
├── tools/             # Business tool modules
├── schemas/           # Pydantic schemas for tool I/O
├── utils/             # Logging and utilities
└── README.md
```

## Adding a Tool

1. Create a new file in `tools/` (e.g., `tools/meetings.py`)

2. Define a `register(mcp)` function:

```python
from mcp.server.fastmcp import FastMCP

def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def search_meetings(query: str) -> str:
        """Search meetings by title or content."""
        # Implementation here
        return "result"
```

3. Add the module path to `TOOL_MODULES` in `registry.py`:

```python
TOOL_MODULES = [
    ...
    "src.mcp.tools.meetings",
]
```

## Authentication

MCP tools authenticate via Workspace API Keys using the `Authorization: Bearer` header.

Each key is SHA-256 hashed before storage. The plaintext secret is shown only once at creation time.

## Context

Tools access the authenticated user and workspace via `MCPContext`:

```python
from mcp.server.fastmcp import Context
from src.mcp.context import MCPContext

@mcp.tool()
async def my_tool(ctx: Context) -> str:
    auth: MCPContext = ctx.request_context.lifespan_context
    workspace_id = auth.workspace_id
    user_id = auth.user_id
    ...
```

## Transport

Streamable HTTP at `/mcp`. The MCP server is mounted as a Starlette sub-application on the FastAPI app.

## Dependencies

- `mcp>=1.27,<2` (MCP Python SDK)
- Existing service layer
- PostgreSQL (workspace_api_keys table)
