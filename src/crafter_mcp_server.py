#!/usr/bin/env python3
"""
Crafter MCP Server
A specialized MCP server that orchestrates the Enhanced MCP Crafter
Provides continuous tweaking and management capabilities via MCP protocol
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

import mcp.server.stdio
import mcp.types as types
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions

# Import our crafter
from mcp_crafter import EnhancedMCPCrafter, ServerComplexity, ServerCapability, CrafterForm

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("crafter_mcp_server")

SERVER_NAME = "crafter"
SERVER_VERSION = "1.0.0"


class CrafterMCPServer:
    """
    MCP Server that provides access to the Enhanced MCP Crafter
    Allows Claude to create, manage, and monitor MCP servers
    """
    
    def __init__(self):
        self.server = Server(SERVER_NAME)
        self.crafter = EnhancedMCPCrafter()
        self.active_sessions = {}
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup MCP protocol handlers"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            """List available crafter tools"""
            return [
                types.Tool(
                    name="create_mcp_server",
                    description="Create a new MCP server from specifications",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "server_name": {
                                "type": "string",
                                "description": "Name of the MCP server to create"
                            },
                            "description": {
                                "type": "string",
                                "description": "Description of the server functionality"
                            },
                            "complexity": {
                                "type": "string",
                                "enum": ["simple", "standard", "advanced", "enterprise", "custom"],
                                "default": "standard",
                                "description": "Complexity level of the server"
                            },
                            "capabilities": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "enum": [
                                        "tools", "resources", "prompts", "monitoring", 
                                        "persistence", "authentication", "rate_limiting", 
                                        "caching", "webhooks", "streaming"
                                    ]
                                },
                                "description": "List of capabilities to include"
                            },
                            "template_base": {
                                "type": "string",
                                "default": "enterprise-python",
                                "description": "Base template to use"
                            },
                            "custom_tools": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "description": {"type": "string"},
                                        "parameters": {"type": "object"},
                                        "implementation": {"type": "string"}
                                    }
                                },
                                "description": "Custom tools to implement"
                            },
                            "dependencies": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Additional Python dependencies"
                            },
                            "environment_vars": {
                                "type": "object",
                                "description": "Environment variables configuration"
                            },
                            "deployment_config": {
                                "type": "object",
                                "properties": {
                                    "docker": {"type": "boolean", "default": True},
                                    "kubernetes": {"type": "boolean", "default": False},
                                    "compose": {"type": "boolean", "default": True},
                                    "git": {"type": "boolean", "default": True}
                                },
                                "description": "Deployment configuration options"
                            }
                        },
                        "required": ["server_name"]
                    }
                ),
                types.Tool(
                    name="get_build_status",
                    description="Get the status of a server build process",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "build_id": {
                                "type": "string",
                                "description": "Build ID to check status for"
                            }
                        },
                        "required": ["build_id"]
                    }
                ),
                types.Tool(
                    name="list_servers",
                    description="List all created MCP servers",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                types.Tool(
                    name="update_server",
                    description="Update an existing MCP server configuration",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "server_name": {
                                "type": "string",
                                "description": "Name of the server to update"
                            },
                            "updates": {
                                "type": "object",
                                "description": "Updates to apply (same format as create)"
                            }
                        },
                        "required": ["server_name", "updates"]
                    }
                ),
                types.Tool(
                    name="delete_server",
                    description="Delete an MCP server and its files",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "server_name": {
                                "type": "string",
                                "description": "Name of the server to delete"
                            },
                            "confirm": {
                                "type": "boolean",
                                "description": "Confirmation flag (must be true)"
                            }
                        },
                        "required": ["server_name", "confirm"]
                    }
                ),
                types.Tool(
                    name="get_server_info",
                    description="Get detailed information about a specific server",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "server_name": {
                                "type": "string",
                                "description": "Name of the server to get info for"
                            }
                        },
                        "required": ["server_name"]
                    }
                ),
                types.Tool(
                    name="start_continuous_mode",
                    description="Start continuous monitoring and tweaking mode",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "watch_patterns": {
                                "type": "array",
                                "items": {"type": "string"},
                                "default": ["*.py", "*.json", "*.yaml", "*.toml"],
                                "description": "File patterns to watch for changes"
                            }
                        },
                        "required": []
                    }
                ),
                types.Tool(
                    name="create_complex_workflow",
                    description="Create a complex MCP server with multiple interconnected components",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "workflow_name": {
                                "type": "string",
                                "description": "Name of the workflow"
                            },
                            "servers": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "role": {"type": "string"},
                                        "capabilities": {"type": "array"},
                                        "connections": {"type": "array"}
                                    }
                                },
                                "description": "Multiple servers in the workflow"
                            },
                            "orchestration": {
                                "type": "object",
                                "description": "Orchestration configuration"
                            }
                        },
                        "required": ["workflow_name", "servers"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(
            name: str, arguments: dict[str, Any] | None
        ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
            """Handle tool calls"""
            if arguments is None:
                arguments = {}
            
            try:
                if name == "create_mcp_server":
                    return await self.create_mcp_server(**arguments)
                elif name == "get_build_status":
                    return await self.get_build_status(**arguments)
                elif name == "list_servers":
                    return await self.list_servers(**arguments)
                elif name == "update_server":
                    return await self.update_server(**arguments)
                elif name == "delete_server":
                    return await self.delete_server(**arguments)
                elif name == "get_server_info":
                    return await self.get_server_info(**arguments)
                elif name == "start_continuous_mode":
                    return await self.start_continuous_mode(**arguments)
                elif name == "create_complex_workflow":
                    return await self.create_complex_workflow(**arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")
            except Exception as e:
                logger.error(f"Error in tool {name}: {e}")
                return [types.TextContent(
                    type="text", 
                    text=f"Error executing {name}: {str(e)}"
                )]
    
    async def create_mcp_server(
        self, 
        server_name: str,
        description: str = "",
        complexity: str = "standard",
        capabilities: List[str] = None,
        template_base: str = "enterprise-python",
        custom_tools: List[Dict[str, Any]] = None,
        dependencies: List[str] = None,
        environment_vars: Dict[str, str] = None,
        deployment_config: Dict[str, Any] = None,
        **kwargs
    ) -> List[types.TextContent]:
        """Create a new MCP server"""
        
        # Set defaults
        if capabilities is None:
            capabilities = ["tools", "monitoring"]
        if custom_tools is None:
            custom_tools = []
        if dependencies is None:
            dependencies = []
        if environment_vars is None:
            environment_vars = {}
        if deployment_config is None:
            deployment_config = {"docker": True, "compose": True}
        
        # Build form data
        form_data = {
            "server_name": server_name,
            "description": description or f"MCP server: {server_name}",
            "complexity": complexity,
            "capabilities": capabilities,
            "template_base": template_base,
            "custom_tools": custom_tools,
            "dependencies": dependencies,
            "environment_vars": environment_vars,
            "deployment_config": deployment_config,
            "metadata": {
                "created_via": "crafter_mcp_server",
                "created_at": datetime.now(timezone.utc).isoformat()
            }
        }
        
        try:
            # Start the crafter watchdog if not already running
            if not hasattr(self.crafter, '_watching_started'):
                await self.crafter.start_watching()
                self.crafter._watching_started = True
            
            # Process the form
            build_id = await self.crafter.process_claude_form(form_data)
            
            result = {
                "status": "success",
                "message": f"Server '{server_name}' creation started",
                "build_id": build_id,
                "server_name": server_name,
                "complexity": complexity,
                "capabilities": capabilities,
                "next_steps": [
                    f"Use 'get_build_status' with build_id '{build_id}' to monitor progress",
                    f"Server will be created at: {self.crafter.servers_dir / server_name}",
                    "Files will be automatically monitored for changes"
                ]
            }
            
            return [types.TextContent(
                type="text", 
                text=json.dumps(result, indent=2)
            )]
            
        except Exception as e:
            error_result = {
                "status": "error",
                "message": f"Failed to create server '{server_name}'",
                "error": str(e)
            }
            return [types.TextContent(
                type="text", 
                text=json.dumps(error_result, indent=2)
            )]
    
    async def get_build_status(self, build_id: str) -> List[types.TextContent]:
        """Get build status"""
        status = await self.crafter.get_build_status(build_id)
        
        if status.get("status") == "not_found":
            result = {
                "status": "not_found",
                "message": f"Build ID '{build_id}' not found"
            }
        else:
            result = {
                "status": "found",
                "build_info": status
            }
        
        return [types.TextContent(
            type="text", 
            text=json.dumps(result, indent=2, default=str)
        )]
    
    async def list_servers(self) -> List[types.TextContent]:
        """List all servers"""
        servers = self.crafter.list_servers()
        
        result = {
            "status": "success",
            "server_count": len(servers),
            "servers": servers
        }
        
        return [types.TextContent(
            type="text", 
            text=json.dumps(result, indent=2, default=str)
        )]
    
    async def update_server(
        self, 
        server_name: str, 
        updates: Dict[str, Any]
    ) -> List[types.TextContent]:
        """Update an existing server"""
        servers = self.crafter.list_servers()
        
        if server_name not in servers:
            result = {
                "status": "error",
                "message": f"Server '{server_name}' not found"
            }
        else:
            # For now, updating means recreating with new config
            # In a full implementation, this would be more sophisticated
            server_info = servers[server_name]
            original_form = server_info.get("form", {})
            
            # Merge updates
            updated_form = {**original_form, **updates}
            updated_form["server_name"] = server_name  # Ensure name stays the same
            
            try:
                build_id = await self.crafter.process_claude_form(updated_form)
                result = {
                    "status": "success",
                    "message": f"Server '{server_name}' update started",
                    "build_id": build_id,
                    "updates_applied": updates
                }
            except Exception as e:
                result = {
                    "status": "error",
                    "message": f"Failed to update server '{server_name}'",
                    "error": str(e)
                }
        
        return [types.TextContent(
            type="text", 
            text=json.dumps(result, indent=2)
        )]
    
    async def delete_server(
        self, 
        server_name: str, 
        confirm: bool = False
    ) -> List[types.TextContent]:
        """Delete a server"""
        if not confirm:
            result = {
                "status": "error",
                "message": "Deletion requires confirmation. Set 'confirm' to true."
            }
        else:
            success = await self.crafter.delete_server(server_name)
            
            if success:
                result = {
                    "status": "success",
                    "message": f"Server '{server_name}' deleted successfully"
                }
            else:
                result = {
                    "status": "error",
                    "message": f"Server '{server_name}' not found"
                }
        
        return [types.TextContent(
            type="text", 
            text=json.dumps(result, indent=2)
        )]
    
    async def get_server_info(self, server_name: str) -> List[types.TextContent]:
        """Get detailed server information"""
        servers = self.crafter.list_servers()
        
        if server_name not in servers:
            result = {
                "status": "error",
                "message": f"Server '{server_name}' not found"
            }
        else:
            server_info = servers[server_name]
            server_path = Path(server_info["path"])
            
            # Get file structure
            files = []
            if server_path.exists():
                for file_path in server_path.rglob("*"):
                    if file_path.is_file():
                        files.append(str(file_path.relative_to(server_path)))
            
            result = {
                "status": "success",
                "server_info": server_info,
                "file_structure": files,
                "path": str(server_path),
                "exists": server_path.exists()
            }
        
        return [types.TextContent(
            type="text", 
            text=json.dumps(result, indent=2, default=str)
        )]
    
    async def start_continuous_mode(
        self, 
        watch_patterns: List[str] = None
    ) -> List[types.TextContent]:
        """Start continuous monitoring mode"""
        if watch_patterns is None:
            watch_patterns = ["*.py", "*.json", "*.yaml", "*.toml"]
        
        try:
            # Start watching if not already started
            if not hasattr(self.crafter, '_watching_started'):
                await self.crafter.start_watching()
                self.crafter._watching_started = True
            
            session_id = str(uuid.uuid4())
            self.active_sessions[session_id] = {
                "type": "continuous_monitoring",
                "started_at": datetime.now(timezone.utc),
                "watch_patterns": watch_patterns,
                "status": "active"
            }
            
            result = {
                "status": "success",
                "message": "Continuous monitoring mode started",
                "session_id": session_id,
                "watch_patterns": watch_patterns,
                "monitoring": [
                    "File changes will trigger automatic rebuilds",
                    "Server modifications will be detected in real-time",
                    "Form submissions will be processed asynchronously"
                ]
            }
            
        except Exception as e:
            result = {
                "status": "error",
                "message": "Failed to start continuous mode",
                "error": str(e)
            }
        
        return [types.TextContent(
            type="text", 
            text=json.dumps(result, indent=2, default=str)
        )]
    
    async def create_complex_workflow(
        self, 
        workflow_name: str,
        servers: List[Dict[str, Any]],
        orchestration: Dict[str, Any] = None
    ) -> List[types.TextContent]:
        """Create a complex workflow with multiple interconnected servers"""
        if orchestration is None:
            orchestration = {"type": "sequential", "auto_deploy": True}
        
        try:
            # Start watching if needed
            if not hasattr(self.crafter, '_watching_started'):
                await self.crafter.start_watching()
                self.crafter._watching_started = True
            
            build_ids = []
            created_servers = []
            
            # Create each server in the workflow
            for i, server_spec in enumerate(servers):
                server_name = f"{workflow_name}_{server_spec.get('name', f'server_{i}')}"
                
                form_data = {
                    "server_name": server_name,
                    "description": f"Part of {workflow_name} workflow - {server_spec.get('role', 'component')}",
                    "complexity": "advanced",
                    "capabilities": server_spec.get("capabilities", ["tools", "monitoring"]),
                    "template_base": "enterprise-python",
                    "custom_tools": server_spec.get("custom_tools", []),
                    "dependencies": server_spec.get("dependencies", []),
                    "environment_vars": server_spec.get("environment_vars", {}),
                    "deployment_config": {
                        "docker": True,
                        "compose": True,
                        "kubernetes": orchestration.get("kubernetes", False)
                    },
                    "metadata": {
                        "workflow": workflow_name,
                        "role": server_spec.get("role"),
                        "connections": server_spec.get("connections", []),
                        "orchestration": orchestration
                    }
                }
                
                build_id = await self.crafter.process_claude_form(form_data)
                build_ids.append(build_id)
                created_servers.append(server_name)
            
            result = {
                "status": "success",
                "message": f"Complex workflow '{workflow_name}' creation started",
                "workflow_name": workflow_name,
                "servers_created": created_servers,
                "build_ids": build_ids,
                "orchestration": orchestration,
                "next_steps": [
                    "Monitor build progress using get_build_status for each build_id",
                    "Servers will be interconnected based on workflow configuration",
                    "Deployment orchestration will be set up automatically"
                ]
            }
            
        except Exception as e:
            result = {
                "status": "error",
                "message": f"Failed to create workflow '{workflow_name}'",
                "error": str(e)
            }
        
        return [types.TextContent(
            type="text", 
            text=json.dumps(result, indent=2)
        )]
    
    async def run(self):
        """Run the server using stdio transport"""
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name=SERVER_NAME,
                    server_version=SERVER_VERSION,
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={}
                    )
                )
            )


async def main():
    """Main entry point for the crafter MCP server"""
    logger.info(f"Starting {SERVER_NAME} v{SERVER_VERSION}")
    logger.info("This server provides access to the Enhanced MCP Crafter")
    
    server = CrafterMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())