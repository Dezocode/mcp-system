#!/usr/bin/env python3
"""
Test script to verify that MCP tools are properly organized and accessible
after the standardization to mcp_tools directory.
"""

import os
import sys
from pathlib import Path

def test_mcp_tools_organization():
    """Test that all MCP tools are properly organized in mcp_tools directory."""
    
    print("🔍 Testing MCP Tools Organization...")
    
    base_dir = Path(__file__).parent
    mcp_tools_dir = base_dir / "mcp_tools"
    
    # Test directory structure
    expected_dirs = [
        "core",
        "installation", 
        "integration",
        "development",
        "launchers",
        "examples"
    ]
    
    for dir_name in expected_dirs:
        dir_path = mcp_tools_dir / dir_name
        if dir_path.exists():
            print(f"✅ {dir_name}/ directory exists")
        else:
            print(f"❌ {dir_name}/ directory missing")
            return False
    
    # Test core Python modules
    core_modules = [
        "mcp_tools/core/types.py",
        "mcp_tools/core/server.py", 
        "mcp_tools/core/router.py",
        "mcp_tools/core/manager.py"
    ]
    
    for module_path in core_modules:
        full_path = base_dir / module_path
        if full_path.exists():
            print(f"✅ {module_path} exists")
        else:
            print(f"❌ {module_path} missing")
            return False
    
    # Test installation tools
    installation_tools = [
        "mcp_tools/installation/installer.py",
        "mcp_tools/installation/auto_discovery.py"
    ]
    
    for tool_path in installation_tools:
        full_path = base_dir / tool_path
        if full_path.exists():
            print(f"✅ {tool_path} exists")
        else:
            print(f"❌ {tool_path} missing")
            return False
    
    # Test launchers
    launchers = [
        "mcp_tools/launchers/universal",
        "mcp_tools/launchers/init-project",
        "mcp_tools/launchers/fix"
    ]
    
    for launcher_path in launchers:
        full_path = base_dir / launcher_path
        if full_path.exists():
            print(f"✅ {launcher_path} exists")
        else:
            print(f"❌ {launcher_path} missing")
            return False
    
    # Test Python imports
    sys.path.insert(0, str(base_dir))
    try:
        from mcp_tools.core import types
        print("✅ mcp_tools.core.types imports successfully")
    except ImportError as e:
        print(f"❌ mcp_tools.core.types import failed: {e}")
        return False
    
    try:
        import mcp_tools.installation.auto_discovery
        print("✅ mcp_tools.installation.auto_discovery imports successfully")
    except ImportError as e:
        print(f"❌ mcp_tools.installation.auto_discovery import failed: {e}")
        return False
        
    print("\n🎉 All MCP tools successfully organized in mcp_tools directory!")
    return True

if __name__ == "__main__":
    success = test_mcp_tools_organization()
    sys.exit(0 if success else 1)