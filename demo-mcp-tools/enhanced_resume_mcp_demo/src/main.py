#!/usr/bin/env python3
"""
enhanced_resume_mcp_demo - MCP Server
Generated using MCP Tools standardized template
"""

import asyncio
import json
import logging
from typing import Any, Dict, List

from mcp.server.fastmcp import FastMCP
from mcp.server.models import InitializationOptions


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the MCP server
mcp = FastMCP("enhanced_resume_mcp_demo")


@mcp.tool()
def hello_world(name: str = "World") -> str:
    """
    Say hello to someone
    
    Args:
        name: The name to greet
        
    Returns:
        A greeting message
    """
    return f"Hello, {name}! This is enhanced_resume_mcp_demo MCP Server."


@mcp.resource("config://info")
def get_server_info() -> Dict[str, Any]:
    """Get server information"""
    return {
        "name": "enhanced_resume_mcp_demo",
        "version": "1.0.0",
        "description": "MCP Server created with standardized template"
    }


async def main():
    """Main entry point"""
    try:
        # Run the server
        async with mcp.run_server() as server:
            await server.serve()
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
