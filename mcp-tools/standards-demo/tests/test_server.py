"""
Tests for standards-demo MCP server

Tests the official MCP protocol implementation.
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch
import mcp.types as types

# Import the server class
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from main import StandardsDemoServer


class TestMCPServer:
    """Test suite for the MCP server implementation."""

    @pytest.fixture
    async def server(self):
        """Create a test server instance."""
        return StandardsDemoServer()

    @pytest.mark.asyncio
    async def test_server_initialization(self, server):
        """Test that the server initializes correctly."""
        assert server.server.name == "standards-demo"
        assert hasattr(server, 'hello_world')
        assert hasattr(server, 'get_status')
        assert hasattr(server, 'example_tool')

    @pytest.mark.asyncio
    async def test_list_tools(self, server):
        """Test the list_tools handler."""
        # Mock the server's list_tools handler
        tools = await server.server._tool_handlers["list_tools"]()
        
        assert len(tools) == 3
        
        # Check hello_world tool
        hello_tool = next(tool for tool in tools if tool.name == "hello_world")
        assert hello_tool.description == "Say hello to someone"
        assert "name" in hello_tool.inputSchema["properties"]
        
        # Check get_status tool
        status_tool = next(tool for tool in tools if tool.name == "get_status")
        assert status_tool.description == "Get server status information"
        
        # Check example_tool
        example_tool = next(tool for tool in tools if tool.name == "example_tool")
        assert example_tool.description == "Example tool demonstrating parameter handling"
        assert "param1" in example_tool.inputSchema["properties"]
        assert "param2" in example_tool.inputSchema["properties"]

    @pytest.mark.asyncio
    async def test_hello_world_tool(self, server):
        """Test the hello_world tool."""
        # Test with default name
        result = await server.hello_world()
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Hello, World!" in result[0].text
        assert "standards-demo" in result[0].text

        # Test with custom name
        result = await server.hello_world(name="Alice")
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Hello, Alice!" in result[0].text

    @pytest.mark.asyncio
    async def test_get_status_tool(self, server):
        """Test the get_status tool."""
        result = await server.get_status()
        assert len(result) == 1
        assert result[0].type == "text"
        
        # Parse the JSON response
        status_data = json.loads(result[0].text)
        assert status_data["server"] == "standards-demo"
        assert status_data["version"] == "0.1.0"
        assert status_data["status"] == "running"
        assert "capabilities" in status_data

    @pytest.mark.asyncio
    async def test_example_tool(self, server):
        """Test the example_tool."""
        # Test with required parameter only
        result = await server.example_tool(param1="test")
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Processed 'test' with value 10" in result[0].text

        # Test with both parameters
        result = await server.example_tool(param1="test", param2=20)
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Processed 'test' with value 20" in result[0].text

    @pytest.mark.asyncio
    async def test_call_tool_handler(self, server):
        """Test the call_tool handler with various scenarios."""
        call_tool_handler = server.server._tool_handlers["call_tool"]
        
        # Test hello_world
        result = await call_tool_handler("hello_world", {"name": "Test"})
        assert len(result) == 1
        assert "Hello, Test!" in result[0].text
        
        # Test with empty arguments
        result = await call_tool_handler("hello_world", {})
        assert len(result) == 1
        assert "Hello, World!" in result[0].text
        
        # Test with None arguments
        result = await call_tool_handler("hello_world", None)
        assert len(result) == 1
        assert "Hello, World!" in result[0].text
        
        # Test unknown tool
        with pytest.raises(ValueError, match="Unknown tool"):
            await call_tool_handler("unknown_tool", {})

    @pytest.mark.asyncio
    async def test_tool_error_handling(self, server):
        """Test error handling in tool calls."""
        call_tool_handler = server.server._tool_handlers["call_tool"]
        
        # Test with invalid parameters (should raise appropriate error)
        with pytest.raises(TypeError):
            await call_tool_handler("example_tool", {"param2": "not_an_int"})

    def test_server_metadata(self, server):
        """Test server metadata and configuration."""
        assert hasattr(server, 'server')
        assert server.server.name == "standards-demo"

    @pytest.mark.asyncio 
    async def test_mcp_protocol_compliance(self, server):
        """Test MCP protocol compliance."""
        # Test that tools return proper MCP content types
        result = await server.hello_world()
        assert all(isinstance(content, types.TextContent) for content in result)
        assert all(content.type == "text" for content in result)
        
        result = await server.get_status()
        assert all(isinstance(content, types.TextContent) for content in result)
        
        result = await server.example_tool("test")
        assert all(isinstance(content, types.TextContent) for content in result)


# Integration tests
class TestMCPIntegration:
    """Integration tests for MCP server."""

    @pytest.mark.asyncio
    async def test_full_workflow(self):
        """Test a complete MCP workflow."""
        server = StandardsDemoServer()
        
        # List tools
        tools = await server.server._tool_handlers["list_tools"]()
        assert len(tools) > 0
        
        # Call each tool
        call_tool = server.server._tool_handlers["call_tool"]
        
        # Test hello_world
        result = await call_tool("hello_world", {"name": "Integration Test"})
        assert "Integration Test" in result[0].text
        
        # Test get_status
        result = await call_tool("get_status", {})
        status = json.loads(result[0].text)
        assert status["server"] == "standards-demo"
        
        # Test example_tool
        result = await call_tool("example_tool", {"param1": "integration", "param2": 42})
        assert "integration" in result[0].text
        assert "42" in result[0].text


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
