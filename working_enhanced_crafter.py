#!/usr/bin/env python3
"""
Simplified MCP Crafter - Core Implementation
Focuses on essential MCP server creation functionality with proper error handling
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timezone

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp_crafter")


def validate_path(path: Path, base_dir: Path) -> Path:
    """Validate that path is within base directory to prevent path traversal"""
    try:
        resolved_path = path.resolve()
        resolved_base = base_dir.resolve()
        if not str(resolved_path).startswith(str(resolved_base)):
            raise ValueError(f"Path {path} is outside base directory {base_dir}")
        return resolved_path
    except Exception as e:
        raise ValueError(f"Invalid path: {e}")

def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent injection"""
    import re
    # Remove or replace dangerous characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    sanitized = re.sub(r'\.\.', '_', sanitized)  # Prevent directory traversal
    return sanitized[:255]  # Limit length

class MCPCrafter:
    """
    Simplified MCP Server Crafter
    Creates MCP servers with proper validation and error handling
    """
    
    def __init__(self, workspace_dir: Optional[Path] = None):
        # Validate and create workspace
        self.workspace_dir = workspace_dir or Path.cwd() / "mcp-workspace"
        try:
            self.workspace_dir.mkdir(parents=True, exist_ok=True)
            # Validate workspace is accessible
            validate_path(self.workspace_dir, Path.cwd())
        except Exception as e:
            raise ValueError(f"Failed to initialize workspace: {e}")
        
        # Build tracking
        self.build_history = []
        
        logger.info(f"MCP Crafter initialized at {self.workspace_dir}")
    
    def _create_safe_file(self, file_path: Path, content: str) -> bool:
        """Safely create file with content validation"""
        try:
            # Validate path is within workspace
            safe_path = validate_path(file_path, self.workspace_dir)
            
            # Sanitize content - basic validation
            if len(content) > 1_000_000:  # 1MB limit
                raise ValueError("Content too large")
            
            # Create parent directories safely
            safe_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file with proper encoding
            safe_path.write_text(content, encoding='utf-8')
            return True
            
        except Exception as e:
            logger.error(f"Failed to create file {file_path}: {e}")
            return False
    
    async def create_mcp_server(self, server_name: str, tools: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create a basic MCP server with specified tools
        Simplified implementation focused on core functionality
        """
        
        logger.info(f"Creating MCP server: {server_name}")
        
        # Sanitize server name
        safe_server_name = sanitize_filename(server_name)
        server_dir = self.workspace_dir / safe_server_name
        
        try:
            # Create server directory structure
            server_dir.mkdir(exist_ok=True)
            src_dir = server_dir / "src"
            src_dir.mkdir(exist_ok=True)
            
            # Generate main server file
            main_content = self._generate_main_file(safe_server_name, tools)
            if not self._create_safe_file(src_dir / "main.py", main_content):
                return {"success": False, "error": "Failed to create main file"}
            
            # Generate pyproject.toml
            pyproject_content = self._generate_pyproject(safe_server_name)
            if not self._create_safe_file(server_dir / "pyproject.toml", pyproject_content):
                return {"success": False, "error": "Failed to create pyproject.toml"}
            
            # Generate README
            readme_content = self._generate_readme(safe_server_name, tools)
            if not self._create_safe_file(server_dir / "README.md", readme_content):
                return {"success": False, "error": "Failed to create README"}
            
            # Record build
            build_record = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "server_name": safe_server_name,
                "server_dir": str(server_dir),
                "tools_count": len(tools),
                "success": True
            }
            self.build_history.append(build_record)
            
            logger.info(f"✅ Successfully created MCP server: {safe_server_name}")
            return build_record
            
        except Exception as e:
            logger.error(f"❌ Failed to create MCP server {server_name}: {e}")
            return {"success": False, "error": str(e)}
    
    def _generate_main_file(self, server_name: str, tools: List[Dict[str, Any]]) -> str:
        """Generate clean main.py file for MCP server"""
        tools_code = ""
        for tool in tools:
            name = tool.get("name", "unnamed_tool")
            description = tool.get("description", "Tool description")
            schema = tool.get("inputSchema", {"type": "object", "properties": {}})
            
            tools_code += f'''
# {name} Tool
@server.call_tool()
async def {name}(arguments: dict):
    """
    {description}
    """
    try:
        # TODO: Implement {name} logic here
        return {{
            "success": True,
            "message": "{name} executed successfully",
            "data": arguments
        }}
    except Exception as e:
        return {{
            "success": False,
            "error": str(e)
        }}
'''
        
        return f'''#!/usr/bin/env python3
"""
{server_name} - MCP Server
Auto-generated MCP server implementation
"""

import asyncio
import logging
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("{server_name}")

# Create server instance
server = Server("{server_name}")

{tools_code}

async def main():
    """Run the MCP server"""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="{server_name}",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={{}},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
'''
    
    def _generate_pyproject(self, server_name: str) -> str:
        """Generate pyproject.toml file"""
        return f'''[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "{server_name}"
version = "1.0.0"
description = "MCP Server for {server_name}"
authors = [{{name = "MCP Crafter", email = "admin@example.com"}}]
license = {{text = "MIT"}}
readme = "README.md"
requires-python = ">=3.8"
dependencies = [
    "mcp>=1.0.0",
]

[project.scripts]
{server_name} = "src.main:main"
'''
    
    def _generate_readme(self, server_name: str, tools: List[Dict[str, Any]]) -> str:
        """Generate README.md file"""
        tools_list = "\\n".join([f"- **{tool.get('name', 'tool')}**: {tool.get('description', 'Tool description')}" for tool in tools])
        
        return f'''# {server_name}

MCP Server implementation for {server_name}.

## Tools

{tools_list}

## Installation

```bash
pip install -e .
```

## Usage

```bash
python src/main.py
```

## Generated by MCP Crafter

This server was automatically generated using the MCP Crafter tool.
'''


# Demo function for testing
async def demo():
    """Demonstrate the simplified MCP crafter"""
    logger.info("🎯 MCP Crafter Demo - Simplified Implementation")
    
    # Create a basic MCP server
    crafter = MCPCrafter()
    
    resume_tools = [
        {
            "name": "parse_resume",
            "description": "Parse and extract information from resume data",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "resume_text": {"type": "string", "description": "Resume content to parse"},
                    "format": {"type": "string", "enum": ["text", "pdf", "json"], "default": "text"}
                },
                "required": ["resume_text"]
            }
        },
        {
            "name": "export_resume", 
            "description": "Export resume in various formats",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "resume_data": {"type": "object", "description": "Processed resume data"},
                    "format": {"type": "string", "enum": ["pdf", "html", "json"], "default": "pdf"}
                },
                "required": ["resume_data"]
            }
        }
    ]
    
    result = await crafter.create_mcp_server("resume_mcp_server", resume_tools)
    
    if result.get("success"):
        logger.info(f"✅ Created server: {result['server_name']}")
        logger.info(f"📁 Location: {result['server_dir']}")
        logger.info(f"🔧 Tools: {result['tools_count']}")
    else:
        logger.error(f"❌ Failed: {result.get('error', 'Unknown error')}")
    
    return result


if __name__ == "__main__":
    asyncio.run(demo())
