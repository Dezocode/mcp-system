"""
Tests for final-demo MCP server
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock
from mcp.server.fastmcp import Context

# Import your server modules here
# from src.main import hello_world, get_status, example_tool

@pytest.mark.asyncio
async def test_hello_world():
    """Test the hello_world tool"""
    # Mock context
    ctx = Mock(spec=Context)

    # Test with default name
    result = await hello_world(ctx)
    assert "Hello, World!" in result
    assert "final-demo" in result

    # Test with custom name
    result = await hello_world(ctx, name="Alice")
    assert "Hello, Alice!" in result

@pytest.mark.asyncio
async def test_get_status():
    """Test the get_status tool"""
    # Mock context
    ctx = Mock(spec=Context)
    ctx.request_context = Mock()
    ctx.request_context.lifespan_context = Mock()
    ctx.request_context.lifespan_context.initialized = True

    result = await get_status(ctx)
    status_data = json.loads(result)

    assert status_data["server"] == "final-demo"
    assert status_data["status"] == "running"
    assert status_data["initialized"] is True
    assert status_data["port"] == 8055

@pytest.mark.asyncio
async def test_example_tool():
    """Test the example_tool"""
    ctx = Mock(spec=Context)

    # Test with required parameter
    result = await example_tool(ctx, param1="test")
    assert "Processed test with value 10" == result

    # Test with both parameters
    result = await example_tool(ctx, param1="test", param2=20)
    assert "Processed test with value 20" == result

# Add more tests for your custom tools here
