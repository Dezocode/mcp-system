#!/usr/bin/env python3
"""
final-demo - Official MCP Server
MCP server for final-demo

This server follows the official Anthropic MCP protocol specification.
"""

import asyncio
import json
import logging
from typing import Any, Sequence

import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from pydantic import AnyUrl

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("final-demo")

# Server metadata
SERVER_NAME = "final-demo"
SERVER_VERSION = "0.1.0"


class FinalDemoServer:
    """
    Official MCP Server implementation for final-demo.

    Follows Anthropic MCP protocol specification:
    - Uses stdio transport (recommended by Anthropic)
    - Implements standard MCP capabilities
    - Provides proper error handling
    """

    def __init__(self):
        self.server = Server(SERVER_NAME)
        self.setup_handlers()

    def setup_handlers(self):
        """Set up MCP protocol handlers following official patterns."""

        @self.server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            """
            List available tools.

            Returns the tools offered by this server.
            """
            return [
                types.Tool(
                    name="hello_world",
                    description="Say hello to someone",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "The name to greet",
                            }
                        },
                        "required": [],
                    },
                ),
                types.Tool(
                    name="get_status",
                    description="Get server status information",
                    inputSchema={"type": "object", "properties": {}, "required": []},
                ),
                types.Tool(
                    name="example_tool",
                    description="Example tool demonstrating parameter handling",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "param1": {
                                "type": "string",
                                "description": "A required string parameter",
                            },
                            "param2": {
                                "type": "integer",
                                "description": "An optional integer parameter",
                                "default": 10,
                            },
                        },
                        "required": ["param1"],
                    },
                ),
            ]

        @self.server.call_tool()
        async def handle_call_tool(
            name: str, arguments: dict[str, Any] | None
        ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
            """
            Handle tool calls.

            Args:
                name: The name of the tool to call
                arguments: The arguments for the tool

            Returns:
                The result of the tool call
            """
            if arguments is None:
                arguments = {}

            try:
                if name == "hello_world":
                    return await self.hello_world(**arguments)
                elif name == "get_status":
                    return await self.get_status(**arguments)
                elif name == "example_tool":
                    return await self.example_tool(**arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")
            except Exception as e:
                logger.error(f"Error in tool {name}: {e}")
                raise

    async def hello_world(self, name: str = "World") -> list[types.TextContent]:
        """
        Say hello to someone.

        Args:
            name: The name to greet

        Returns:
            A greeting message
        """
        message = f"Hello, {name}! This is {SERVER_NAME} server."
        return [types.TextContent(type="text", text=message)]

    async def get_status(self) -> list[types.TextContent]:
        """
        Get server status information.

        Returns:
            Server status information in JSON format
        """
        status = {
            "server": SERVER_NAME,
            "version": SERVER_VERSION,
            "status": "running",
            "description": "MCP server for final-demo",
            "capabilities": ["tools"],
        }
        return [types.TextContent(type="text", text=json.dumps(status, indent=2))]

    async def example_tool(
        self, param1: str, param2: int = 10
    ) -> list[types.TextContent]:
        """
        Example tool demonstrating parameter handling.

        Args:
            param1: A required string parameter
            param2: An optional integer parameter (default: 10)

        Returns:
            Result of the operation
        """
        result = f"Processed '{param1}' with value {param2}"
        return [types.TextContent(type="text", text=result)]

    async def run(self):
        """Run the server using stdio transport (Anthropic recommended)."""
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name=SERVER_NAME,
                    server_version=SERVER_VERSION,
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )


async def main():
    """Main entry point for the MCP server."""
    logger.info(f"Starting {SERVER_NAME} v{SERVER_VERSION}")
    logger.info("Using stdio transport (Anthropic MCP standard)")

    server = FinalDemoServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
