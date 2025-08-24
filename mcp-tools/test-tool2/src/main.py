"""
test-tool2 - MCP Server
MCP server for test-tool2
"""

from mcp.server.fastmcp import FastMCP, Context
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass
from dotenv import load_dotenv
import asyncio
import json
import os

load_dotenv()

# Server configuration
SERVER_NAME = "test-tool2"
SERVER_PORT = 8055
SERVER_HOST = os.getenv("HOST", "localhost")

@dataclass
class TestTool2Context:
    """Context for the test-tool2 MCP server."""
    # Add your context variables here
    initialized: bool = False

@asynccontextmanager
async def server_lifespan(
    server: FastMCP
) -> AsyncIterator[TestTool2Context]:
    """
    Manages the server lifecycle.

    Args:
        server: The FastMCP server instance

    Yields:
        Context: The server context
    """
    # Initialize your server resources here
    print(f"Starting {SERVER_NAME} server...")

    context = TestTool2Context(initialized=True)

    try:
        yield context
    finally:
        # Cleanup resources here
        print(f"Shutting down {SERVER_NAME} server...")

# Initialize FastMCP server
mcp = FastMCP(
    SERVER_NAME,
    description="MCP server for test-tool2",
    lifespan=server_lifespan,
    host=SERVER_HOST,
    port=SERVER_PORT
)

@mcp.tool()
async def hello_world(ctx: Context, name: str = "World") -> str:
    """Say hello to someone.

    Args:
        ctx: The MCP server provided context
        name: The name to greet

    Returns:
        A greeting message
    """
    return f"Hello, {name}! This is {SERVER_NAME} server."

@mcp.tool()
async def get_status(ctx: Context) -> str:
    """Get server status.

    Args:
        ctx: The MCP server provided context

    Returns:
        Server status information
    """
    context = ctx.request_context.lifespan_context
    return json.dumps({
        "server": SERVER_NAME,
        "status": "running",
        "initialized": context.initialized,
        "port": SERVER_PORT
    }, indent=2)

# Add your custom tools here
@mcp.tool()
async def example_tool(ctx: Context, param1: str, param2: int = 10) -> str:
    """Example tool demonstrating parameter handling.

    Args:
        ctx: The MCP server provided context
        param1: A required string parameter
        param2: An optional integer parameter (default: 10)

    Returns:
        Result of the operation
    """
    return f"Processed {param1} with value {param2}"

if __name__ == "__main__":
    print(f"Starting {SERVER_NAME} MCP server on {SERVER_HOST}:{SERVER_PORT}")
    mcp.run()
