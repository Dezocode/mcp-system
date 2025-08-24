#!/usr/bin/env python3
"""
Tests for demo-watchdog-server MCP Server
"""

import pytest
import asyncio
from src.main import mcp


class TestDemowatchdogserverServer:
    """Test cases for demo-watchdog-server server"""
    
    def test_hello_world(self):
        """Test hello_world tool"""
        result = mcp.call_tool("hello_world", {"name": "Test"})
        assert "Hello, Test!" in result
        
    def test_hello_world_default(self):
        """Test hello_world tool with default name"""
        result = mcp.call_tool("hello_world", {})
        assert "Hello, World!" in result
        
    @pytest.mark.asyncio
    async def test_server_info_resource(self):
        """Test server info resource"""
        info = mcp.get_resource("config://info")
        assert info["name"] == "demo-watchdog-server"
        assert "version" in info
