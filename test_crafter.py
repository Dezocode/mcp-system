#!/usr/bin/env python3
"""
Test the Enhanced MCP Crafter
"""

import asyncio
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mcp_crafter import EnhancedMCPCrafter, ServerComplexity, ServerCapability


async def test_basic_functionality():
    """Test basic crafter functionality"""
    print("🧪 Testing Enhanced MCP Crafter...")
    
    # Initialize crafter
    workspace = Path("/tmp/mcp-crafter-test")
    crafter = EnhancedMCPCrafter(workspace)
    
    print(f"✅ Crafter initialized at {workspace}")
    
    # Test form processing
    test_form = {
        "server_name": "test-weather-server",
        "description": "A test weather MCP server",
        "complexity": "standard",
        "capabilities": ["tools", "monitoring", "caching"],
        "template_base": "enterprise-python",
        "custom_tools": [
            {
                "name": "get_weather",
                "description": "Get current weather",
                "parameters": {"city": {"type": "string"}},
                "implementation": "return f'Weather for {kwargs.get(\"city\", \"Unknown\")}: 72°F'"
            }
        ],
        "dependencies": ["requests", "redis"],
        "environment_vars": {"API_KEY": "test-key"},
        "deployment_config": {"docker": True, "compose": True}
    }
    
    print("📝 Processing test form...")
    build_id = await crafter.process_claude_form(test_form)
    print(f"✅ Build started with ID: {build_id}")
    
    # Wait a moment for processing
    await asyncio.sleep(2)
    
    # Check build status
    status = await crafter.get_build_status(build_id)
    print(f"📊 Build status: {status.get('status', 'unknown')}")
    print(f"📈 Progress: {status.get('progress', 0)}%")
    
    # List servers
    servers = crafter.list_servers()
    print(f"📋 Servers created: {len(servers)}")
    
    if servers:
        server_name = list(servers.keys())[0]
        print(f"🔍 First server: {server_name}")
        
        # Check if files were created
        server_path = Path(servers[server_name]["path"])
        if server_path.exists():
            print(f"📁 Server directory exists: {server_path}")
            
            # List created files
            created_files = list(server_path.rglob("*"))
            print(f"📄 Files created: {len([f for f in created_files if f.is_file()])}")
            
            # Check key files
            key_files = ["src/main.py", "pyproject.toml", "README.md", ".env.example"]
            for key_file in key_files:
                file_path = server_path / key_file
                if file_path.exists():
                    print(f"  ✅ {key_file}")
                else:
                    print(f"  ❌ {key_file} missing")
        else:
            print(f"❌ Server directory not found: {server_path}")
    
    print("✅ Basic functionality test completed!")


async def test_crafter_mcp_server():
    """Test the Crafter MCP Server"""
    print("\n🧪 Testing Crafter MCP Server...")
    
    try:
        from crafter_mcp_server import CrafterMCPServer
        
        # Initialize server
        server = CrafterMCPServer()
        print("✅ Crafter MCP Server initialized")
        
        # Test tool listing
        tools = await server.server._tool_handlers["list_tools"]()
        print(f"🔧 Available tools: {len(tools)}")
        
        for tool in tools[:3]:  # Show first 3 tools
            print(f"  - {tool.name}: {tool.description}")
        
        print("✅ Crafter MCP Server test completed!")
        
    except ImportError as e:
        print(f"⚠️  Could not import Crafter MCP Server: {e}")


def test_cli():
    """Test CLI functionality"""
    print("\n🧪 Testing CLI...")
    
    # Test help
    import subprocess
    try:
        result = subprocess.run([
            "python", "/home/runner/work/mcp-system/mcp-system/bin/mcp-crafter", "help"
        ], capture_output=True, text=True)
        
        if result.returncode == 0 and "Enhanced MCP Crafter CLI" in result.stdout:
            print("✅ CLI help working")
        else:
            print("❌ CLI help failed")
            print(f"Return code: {result.returncode}")
            print(f"Stdout: {result.stdout}")
            print(f"Stderr: {result.stderr}")
    except Exception as e:
        print(f"❌ CLI test failed: {e}")


async def main():
    """Run all tests"""
    print("🚀 Enhanced MCP Crafter Test Suite")
    print("=" * 50)
    
    await test_basic_functionality()
    await test_crafter_mcp_server()
    test_cli()
    
    print("\n🎉 Test suite completed!")


if __name__ == "__main__":
    asyncio.run(main())