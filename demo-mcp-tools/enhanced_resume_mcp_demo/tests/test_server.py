#!/usr/bin/env python3
"""
Tests for enhanced_resume_mcp_demo MCP Server
"""

import pytest
import asyncio
from src.main import mcp


class TestEnhanced_Resume_Mcp_DemoServer:
    """Test cases for enhanced_resume_mcp_demo server"""
    
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
        assert info["name"] == "enhanced_resume_mcp_demo"
        assert "version" in info
