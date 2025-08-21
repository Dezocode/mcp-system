#!/usr/bin/env python3
"""
Claude Code MCP Bridge
Bridge between Claude Code and MCP servers
"""

import os
import json
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional

class ClaudeCodeMCPBridge:
    """Bridge for Claude Code integration with MCP"""
    
    def __init__(self, config_path: str = None):
        self.home = Path.home()
        self.claude_config_path = Path(config_path) if config_path else self.home / ".claude" / "claude_desktop_config.json"
        self.mcp_system_path = Path(os.getenv("MCP_SYSTEM_PATH", self.home / ".mcp-system"))
        
    def load_claude_config(self) -> Dict[str, Any]:
        """Load Claude configuration"""
        try:
            if self.claude_config_path.exists():
                with open(self.claude_config_path, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Warning: Could not load Claude config: {e}")
            return {}
    
    def save_claude_config(self, config: Dict[str, Any]) -> bool:
        """Save Claude configuration"""
        try:
            self.claude_config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.claude_config_path, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving Claude config: {e}")
            return False
    
    def merge_claude_config(self, new_config: Dict[str, Any]) -> bool:
        """Merge new configuration with existing Claude config"""
        try:
            existing_config = self.load_claude_config()
            
            # Merge mcpServers
            if "mcpServers" not in existing_config:
                existing_config["mcpServers"] = {}
                
            if "mcpServers" in new_config:
                existing_config["mcpServers"].update(new_config["mcpServers"])
            
            # Merge other sections
            for key, value in new_config.items():
                if key != "mcpServers":
                    existing_config[key] = value
            
            return self.save_claude_config(existing_config)
        except Exception as e:
            print(f"Error merging Claude config: {e}")
            return False
    
    def register_mcp_server(self, server_name: str, command: str, args: list = None, env: dict = None) -> bool:
        """Register an MCP server with Claude"""
        config = self.load_claude_config()
        
        if "mcpServers" not in config:
            config["mcpServers"] = {}
            
        config["mcpServers"][server_name] = {
            "command": command,
            "args": args or [],
            "env": env or {}
        }
        
        return self.save_claude_config(config)
    
    def unregister_mcp_server(self, server_name: str) -> bool:
        """Unregister an MCP server from Claude"""
        config = self.load_claude_config()
        
        if "mcpServers" in config and server_name in config["mcpServers"]:
            del config["mcpServers"][server_name]
            return self.save_claude_config(config)
            
        return True
    
    def list_mcp_servers(self) -> Dict[str, Dict[str, Any]]:
        """List registered MCP servers"""
        config = self.load_claude_config()
        return config.get("mcpServers", {})
    
    def auto_discover_and_register(self) -> int:
        """Auto-discover and register MCP servers in the current project"""
        registered = 0
        
        # Check for common MCP server patterns
        current_dir = Path.cwd()
        
        # Look for Python MCP servers
        for pattern in ["*mcp*.py", "*server*.py"]:
            for py_file in current_dir.glob(pattern):
                if self._is_mcp_server_file(py_file):
                    server_name = py_file.stem
                    if self.register_mcp_server(
                        server_name,
                        "python",
                        [str(py_file)],
                        {"PYTHONPATH": str(current_dir)}
                    ):
                        print(f"✅ Registered MCP server: {server_name}")
                        registered += 1
        
        return registered
    
    def create_safe_mcp_integration(self) -> Dict[str, Any]:
        """Create safe MCP integration configuration"""
        return {
            "mcpServers": {
                "mcp-universal": {  # Changed to match test expectation
                    "command": "python",
                    "args": ["-m", "src.pipeline_mcp_server"],
                    "env": {
                        "MCP_SYSTEM_PATH": str(self.mcp_system_path),
                        "MCP_AUTO_DISCOVERY": "true",
                        "MCP_SAFE_MODE": "true"
                    }
                }
            },
            "security": {
                "safe_mode": True,
                "auto_discovery": True,
                "rate_limiting": True
            }
        }
    
    def _is_mcp_server_file(self, file_path: Path) -> bool:
        """Check if a Python file is an MCP server"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                # Simple heuristic - look for MCP-related imports
                return any(pattern in content for pattern in [
                    "from mcp",
                    "import mcp",
                    "fastmcp",
                    "@mcp.tool"
                ])
        except Exception:
            return False


def main():
    """CLI entry point"""
    import sys
    
    bridge = ClaudeCodeMCPBridge()
    
    if len(sys.argv) < 2:
        print("Usage: claude_code_mcp_bridge.py <command>")
        print("Commands: register, unregister, list, auto-discover")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "register":
        if len(sys.argv) < 4:
            print("Usage: register <server_name> <command> [args...]")
            sys.exit(1)
        server_name = sys.argv[2]
        command_path = sys.argv[3]
        args = sys.argv[4:] if len(sys.argv) > 4 else []
        
        if bridge.register_mcp_server(server_name, command_path, args):
            print(f"✅ Registered MCP server: {server_name}")
        else:
            print(f"❌ Failed to register MCP server: {server_name}")
            
    elif command == "unregister":
        if len(sys.argv) < 3:
            print("Usage: unregister <server_name>")
            sys.exit(1)
        server_name = sys.argv[2]
        
        if bridge.unregister_mcp_server(server_name):
            print(f"✅ Unregistered MCP server: {server_name}")
        else:
            print(f"❌ Failed to unregister MCP server: {server_name}")
            
    elif command == "list":
        servers = bridge.list_mcp_servers()
        if servers:
            print("Registered MCP servers:")
            for name, config in servers.items():
                print(f"  {name}: {config['command']} {' '.join(config.get('args', []))}")
        else:
            print("No MCP servers registered")
            
    elif command == "auto-discover" or command == "init":
        count = bridge.auto_discover_and_register()
        print(f"✅ Auto-discovered and registered {count} MCP servers")
        
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()