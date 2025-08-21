#!/usr/bin/env python3
"""
MCP Auto Discovery System
Automatically discover and manage MCP servers
"""

import os
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any

class MCPAutoDiscovery:
    """Auto-discovery system for MCP servers"""
    
    def __init__(self, system_path: str = None):
        self.home = Path.home()
        self.system_path = Path(system_path) if system_path else self.home / ".mcp-system"
        self.discovery_cache = self.system_path / "discovery_cache.json"
        
    def discover_project_type(self, path: Path = None) -> List[str]:
        """Discover project type based on files present"""
        if path is None:
            path = Path.cwd()
            
        project_types = []
        
        # Python project indicators
        if any(path.glob(pattern) for pattern in ["*.py", "pyproject.toml", "setup.py", "requirements.txt"]):
            project_types.append("python")
            
        # Node.js project indicators
        if any(path.glob(pattern) for pattern in ["package.json", "node_modules"]):
            project_types.append("nodejs")
            
        # TypeScript indicators
        if any(path.glob(pattern) for pattern in ["tsconfig.json", "*.ts"]):
            project_types.append("typescript")
            
        # Claude project indicators
        if any(path.glob(pattern) for pattern in [".claude", "CLAUDE.md", "claude.json"]):
            project_types.append("claude")
            
        # MCP server indicators
        if self._has_mcp_indicators(path):
            project_types.append("mcp")
            
        return project_types if project_types else ["generic"]
    
    def _has_mcp_indicators(self, path: Path) -> bool:
        """Check if path contains MCP server indicators"""
        # Look for MCP-related files
        mcp_files = list(path.glob("*mcp*.py")) + list(path.glob("*server*.py"))
        
        for file in mcp_files:
            try:
                with open(file, 'r') as f:
                    content = f.read()
                    if any(indicator in content for indicator in [
                        "from mcp", "import mcp", "fastmcp", "@mcp.tool"
                    ]):
                        return True
            except Exception:
                continue
                
        return False
    
    def discover_mcp_servers(self, path: Path = None) -> List[Dict[str, Any]]:
        """Discover MCP servers in the given path"""
        if path is None:
            path = Path.cwd()
            
        servers = []
        
        # Look for Python MCP servers
        for py_file in path.glob("**/*.py"):
            if self._is_mcp_server(py_file):
                servers.append({
                    "name": py_file.stem,
                    "path": str(py_file),
                    "type": "python",
                    "auto_discovered": True
                })
        
        # Look for Node.js MCP servers
        for js_file in path.glob("**/*.js"):
            if self._is_mcp_server_js(js_file):
                servers.append({
                    "name": js_file.stem,
                    "path": str(js_file),
                    "type": "nodejs",
                    "auto_discovered": True
                })
                
        return servers
    
    def _is_mcp_server(self, file_path: Path) -> bool:
        """Check if a Python file is an MCP server"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                return any(pattern in content for pattern in [
                    "from mcp",
                    "import mcp", 
                    "fastmcp",
                    "@mcp.tool",
                    "mcp.server",
                    "MCPServer"
                ])
        except Exception:
            return False
    
    def _is_mcp_server_js(self, file_path: Path) -> bool:
        """Check if a JavaScript file is an MCP server"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                return any(pattern in content for pattern in [
                    "@modelcontextprotocol/sdk",
                    "McpServer",
                    "createMcpServer",
                    "tool:",
                    "resource:"
                ])
        except Exception:
            return False
    
    def save_discovery_cache(self, data: Dict[str, Any]) -> bool:
        """Save discovery results to cache"""
        try:
            self.system_path.mkdir(parents=True, exist_ok=True)
            with open(self.discovery_cache, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Failed to save discovery cache: {e}")
            return False
    
    def load_discovery_cache(self) -> Dict[str, Any]:
        """Load discovery results from cache"""
        try:
            if self.discovery_cache.exists():
                with open(self.discovery_cache, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Failed to load discovery cache: {e}")
        return {}
    
    def run_discovery(self, path: Path = None) -> Dict[str, Any]:
        """Run full discovery process"""
        if path is None:
            path = Path.cwd()
            
        results = {
            "timestamp": str(asyncio.get_event_loop().time()),
            "path": str(path),
            "project_types": self.discover_project_type(path),
            "mcp_servers": self.discover_mcp_servers(path),
            "recommendations": self._generate_recommendations(path)
        }
        
        self.save_discovery_cache(results)
        return results
    
    def analyze_environment(self, path: Path = None) -> Dict[str, Any]:
        """Analyze the current environment for MCP opportunities"""
        if path is None:
            path = Path.cwd()
            
        analysis = {
            "path": str(path),
            "project_types": self.discover_project_type(path),
            "existing_servers": self.discover_mcp_servers(path),
            "opportunities": [],
            "complexity": "simple"
        }
        
        # Analyze complexity
        py_files = list(path.glob("**/*.py"))
        if len(py_files) > 50:
            analysis["complexity"] = "complex"
        elif len(py_files) > 10:
            analysis["complexity"] = "medium"
            
        # Identify opportunities
        if "python" in analysis["project_types"] and not analysis["existing_servers"]:
            analysis["opportunities"].append("Create Python MCP server with fastmcp")
            
        if "nodejs" in analysis["project_types"] and not analysis["existing_servers"]:
            analysis["opportunities"].append("Create Node.js MCP server")
            
        return analysis
    
    def _generate_recommendations(self, path: Path) -> List[str]:
        """Generate recommendations based on discovery"""
        recommendations = []
        project_types = self.discover_project_type(path)
        
        if "python" in project_types and "mcp" not in project_types:
            recommendations.append("Consider creating a Python MCP server using fastmcp")
            
        if "nodejs" in project_types and "mcp" not in project_types:
            recommendations.append("Consider creating a Node.js MCP server using @modelcontextprotocol/sdk")
            
        if "claude" in project_types:
            recommendations.append("Configure Claude integration for discovered MCP servers")
            
        return recommendations


def main():
    """CLI entry point"""
    import sys
    
    discovery = MCPAutoDiscovery()
    
    if len(sys.argv) > 1:
        path = Path(sys.argv[1])
    else:
        path = Path.cwd()
    
    print(f"🔍 Running MCP discovery in: {path}")
    print("=" * 50)
    
    results = discovery.run_discovery(path)
    
    print(f"Project types: {', '.join(results['project_types'])}")
    print(f"MCP servers found: {len(results['mcp_servers'])}")
    
    if results['mcp_servers']:
        print("\nDiscovered MCP servers:")
        for server in results['mcp_servers']:
            print(f"  • {server['name']} ({server['type']}) - {server['path']}")
    
    if results['recommendations']:
        print("\nRecommendations:")
        for rec in results['recommendations']:
            print(f"  💡 {rec}")
    
    print(f"\n✅ Discovery complete! Results cached in {discovery.discovery_cache}")


if __name__ == "__main__":
    main()