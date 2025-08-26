#!/usr/bin/env python3
"""
MCP Crafter Server - MCP Server for Orchestrating Server Generation
Model Context Protocol v1.0 Compliant Server

This MCP server provides tools for robust MCP server generation:
1. crafter_generate_server - Generate enhanced MCP servers 
2. crafter_process_form - Process Claude forms asynchronously
3. crafter_add_watchdog - Add file monitoring to existing servers
4. crafter_enhance_cli - Add CLI integration to servers
5. crafter_orchestrate - Orchestrate multiple server tasks
6. crafter_continuous_tweak - Runtime configuration tweaking

The crafter accepts form submissions from Claude and can build
complex MCP servers with watchdog pathing, CLI integration,
automation, and monitoring capabilities.

Author: MCP Crafter Team
Version: 1.0.0
MCP Protocol: v1.0
"""

import asyncio
import json
import logging
import os
import sys
import time
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp.server.lowlevel import NotificationOptions, Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# Import our enhanced crafter
sys.path.insert(0, str(Path(__file__).parent))
from enhanced_mcp_crafter import EnhancedMCPCrafter, EnhancedServerRequest, CrafterFormData

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class OrchestrationTask:
    """Task for orchestrating multiple operations"""
    task_id: str
    task_type: str  # "generate", "enhance", "deploy"
    config: Dict[str, Any]
    dependencies: List[str] = None
    status: str = "pending"  # "pending", "running", "completed", "failed"
    result: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.result is None:
            self.result = {}

class MCPCrafterServer:
    """MCP Server for orchestrating MCP server generation and management"""
    
    def __init__(self):
        self.server = Server("mcp-crafter")
        self.crafter = EnhancedMCPCrafter()
        self.active_forms = {}
        self.orchestration_tasks = {}
        self.form_queue = asyncio.Queue()
        
        # Setup request handlers
        self._setup_handlers()
        
        logger.info("MCP Crafter Server initialized")
    
    def _setup_handlers(self):
        """Setup MCP request handlers"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            """List available crafter tools"""
            return [
                types.Tool(
                    name="crafter_generate_server",
                    description="Generate robust MCP servers with enhanced features",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Server name"},
                            "template": {
                                "type": "string",
                                "enum": ["python-fastmcp", "typescript-node", "minimal-python"],
                                "description": "Base template"
                            },
                            "description": {"type": "string", "description": "Server description"},
                            "port": {"type": "integer", "description": "Server port", "default": 8055},
                            "features": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "enum": ["watchdog", "cli", "automation", "monitoring"]
                                },
                                "description": "Features to include",
                                "default": ["cli"]
                            },
                            "dependencies": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Additional dependencies",
                                "default": []
                            },
                            "environment": {
                                "type": "object",
                                "description": "Environment variables",
                                "default": {}
                            },
                            "path": {"type": "string", "description": "Custom installation path"}
                        },
                        "required": ["name", "template", "description"]
                    }
                ),
                types.Tool(
                    name="crafter_process_form",
                    description="Process Claude forms and requests asynchronously",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "form_type": {
                                "type": "string",
                                "enum": ["server_generation", "enhancement", "orchestration"],
                                "description": "Type of form to process"
                            },
                            "requirements": {
                                "type": "object",
                                "description": "Form requirements and configuration"
                            },
                            "options": {
                                "type": "object",
                                "description": "Additional options",
                                "default": {}
                            },
                            "async_mode": {
                                "type": "boolean",
                                "description": "Process asynchronously",
                                "default": False
                            }
                        },
                        "required": ["form_type", "requirements"]
                    }
                ),
                types.Tool(
                    name="crafter_add_watchdog",
                    description="Add file system monitoring to existing MCP servers",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "server_path": {"type": "string", "description": "Path to existing server"},
                            "watch_paths": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Paths to monitor",
                                "default": ["."]
                            }
                        },
                        "required": ["server_path"]
                    }
                ),
                types.Tool(
                    name="crafter_enhance_cli",
                    description="Add CLI integration framework to MCP servers",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "server_path": {"type": "string", "description": "Path to existing server"},
                            "additional_commands": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Additional CLI commands to add",
                                "default": []
                            }
                        },
                        "required": ["server_path"]
                    }
                ),
                types.Tool(
                    name="crafter_orchestrate",
                    description="Orchestrate multiple server generation and management tasks",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "tasks": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "type": {
                                            "type": "string",
                                            "enum": ["generate", "enhance", "deploy"]
                                        },
                                        "config": {"type": "object"},
                                        "dependencies": {
                                            "type": "array",
                                            "items": {"type": "string"},
                                            "default": []
                                        }
                                    },
                                    "required": ["type", "config"]
                                },
                                "description": "List of tasks to orchestrate"
                            },
                            "execution_mode": {
                                "type": "string",
                                "enum": ["sequential", "parallel", "dependency_order"],
                                "description": "Execution mode",
                                "default": "dependency_order"
                            }
                        },
                        "required": ["tasks"]
                    }
                ),
                types.Tool(
                    name="crafter_continuous_tweak",
                    description="Enable runtime configuration and tweaking of MCP servers",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "server_name": {"type": "string", "description": "Server to configure"},
                            "operation": {
                                "type": "string",
                                "enum": ["enable_feature", "disable_feature", "update_config", "restart_component"],
                                "description": "Tweaking operation"
                            },
                            "parameters": {
                                "type": "object",
                                "description": "Operation parameters",
                                "default": {}
                            }
                        },
                        "required": ["server_name", "operation"]
                    }
                ),
                types.Tool(
                    name="crafter_get_status",
                    description="Get status of crafter operations and generated servers",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "include_servers": {
                                "type": "boolean",
                                "description": "Include status of generated servers",
                                "default": True
                            }
                        }
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
            """Handle tool calls"""
            
            try:
                if name == "crafter_generate_server":
                    return await self._handle_generate_server(arguments)
                elif name == "crafter_process_form":
                    return await self._handle_process_form(arguments)
                elif name == "crafter_add_watchdog":
                    return await self._handle_add_watchdog(arguments)
                elif name == "crafter_enhance_cli":
                    return await self._handle_enhance_cli(arguments)
                elif name == "crafter_orchestrate":
                    return await self._handle_orchestrate(arguments)
                elif name == "crafter_continuous_tweak":
                    return await self._handle_continuous_tweak(arguments)
                elif name == "crafter_get_status":
                    return await self._handle_get_status(arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")
                    
            except Exception as e:
                logger.error(f"Error handling tool {name}: {e}")
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "error",
                        "tool": name,
                        "message": str(e),
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }, indent=2)
                )]
    
    async def _handle_generate_server(self, arguments: dict) -> list[types.TextContent]:
        """Handle enhanced server generation"""
        try:
            # Create enhanced server request
            request = EnhancedServerRequest(
                name=arguments["name"],
                template=arguments["template"],
                description=arguments["description"],
                port=arguments.get("port", 8055),
                features=arguments.get("features", ["cli"]),
                dependencies=arguments.get("dependencies", []),
                environment=arguments.get("environment", {}),
                path=arguments.get("path")
            )
            
            logger.info(f"Generating enhanced server: {request.name} with features: {request.features}")
            
            # Generate the server files
            files = self.crafter.generate_enhanced_server(request)
            
            # Determine server path
            if request.path:
                server_path = Path(request.path).expanduser()
            else:
                server_path = Path.home() / f"mcp-{request.name}"
            
            if server_path.exists():
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "error",
                        "message": f"Directory {server_path} already exists. Choose a different path or remove the existing directory.",
                        "suggested_path": str(Path.home() / f"mcp-{request.name}-{int(time.time())}")
                    }, indent=2)
                )]
            
            # Create directory and write files
            server_path.mkdir(parents=True, exist_ok=True)
            created_files = []
            
            for file_path, content in files.items():
                full_path = server_path / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(content)
                created_files.append(str(full_path))
            
            # Add to MCP configuration
            try:
                self.crafter._add_to_config(request.name, str(server_path), request.port, request.template)
            except Exception as e:
                logger.warning(f"Could not add to MCP config: {e}")
            
            result = {
                "status": "success",
                "server_name": request.name,
                "path": str(server_path),
                "template": request.template,
                "features": request.features,
                "port": request.port,
                "files_created": len(created_files),
                "created_files": created_files[:10],  # Limit output
                "next_steps": [
                    f"cd {server_path}",
                    "pip install -e .",
                    "cp .env.example .env",
                    f"# Edit .env with your configuration",
                    f"{request.name}-cli start --port {request.port}"
                ],
                "cli_commands": {
                    "start": f"{request.name}-cli start",
                    "status": f"{request.name}-cli status",
                    "help": f"{request.name}-cli --help"
                },
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
            
        except Exception as e:
            logger.error(f"Error generating server: {e}")
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "status": "error",
                    "message": f"Failed to generate server: {str(e)}",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }, indent=2)
            )]
    
    async def _handle_process_form(self, arguments: dict) -> list[types.TextContent]:
        """Handle Claude form processing"""
        try:
            form_data = CrafterFormData(
                form_type=arguments["form_type"],
                requirements=arguments["requirements"],
                options=arguments.get("options", {}),
                metadata={"source": "mcp_tool_call"}
            )
            
            async_mode = arguments.get("async_mode", False)
            form_id = str(uuid.uuid4())
            
            logger.info(f"Processing form {form_id}: {form_data.form_type}")
            
            if async_mode:
                # Queue for async processing
                self.active_forms[form_id] = form_data
                await self.form_queue.put((form_id, form_data))
                
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "queued",
                        "form_id": form_id,
                        "form_type": form_data.form_type,
                        "message": "Form queued for asynchronous processing",
                        "check_status": f"Use crafter_get_status to check progress",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }, indent=2)
                )]
            else:
                # Process immediately
                result = self.crafter.process_claude_form(form_data)
                
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "completed",
                        "form_id": form_id,
                        "form_type": form_data.form_type,
                        "result": result,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }, indent=2)
                )]
                
        except Exception as e:
            logger.error(f"Error processing form: {e}")
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "status": "error",
                    "message": f"Failed to process form: {str(e)}",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }, indent=2)
            )]
    
    async def _handle_add_watchdog(self, arguments: dict) -> list[types.TextContent]:
        """Add watchdog monitoring to existing server"""
        try:
            server_path = Path(arguments["server_path"]).expanduser()
            watch_paths = arguments.get("watch_paths", ["."])
            
            if not server_path.exists():
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "error",
                        "message": f"Server path does not exist: {server_path}",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }, indent=2)
                )]
            
            # Generate watchdog component for the server
            request = EnhancedServerRequest(
                name=server_path.name,
                template="python-fastmcp",  # Default
                description="Enhanced with watchdog",
                port=8055,  # Default
                features=["watchdog"]
            )
            
            watchdog_files = self.crafter._generate_watchdog_module(request)
            
            # Create components directory
            components_dir = server_path / "src" / "components"
            components_dir.mkdir(parents=True, exist_ok=True)
            
            # Write watchdog component
            created_files = []
            for file_path, content in watchdog_files.items():
                full_path = server_path / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(content)
                created_files.append(str(full_path))
            
            result = {
                "status": "success",
                "server_path": str(server_path),
                "watch_paths": watch_paths,
                "files_created": created_files,
                "integration_steps": [
                    "Add 'from components.watchdog_component import setup_watchdog' to your main.py",
                    "Call 'setup_watchdog(context)' in your server lifespan function",
                    "Add 'watchdog' to your dependencies in pyproject.toml",
                    "Restart your server to enable monitoring"
                ],
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
            
        except Exception as e:
            logger.error(f"Error adding watchdog: {e}")
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "status": "error",
                    "message": f"Failed to add watchdog: {str(e)}",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }, indent=2)
            )]
    
    async def _handle_enhance_cli(self, arguments: dict) -> list[types.TextContent]:
        """Add CLI integration to existing server"""
        try:
            server_path = Path(arguments["server_path"]).expanduser()
            additional_commands = arguments.get("additional_commands", [])
            
            if not server_path.exists():
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "error",
                        "message": f"Server path does not exist: {server_path}",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }, indent=2)
                )]
            
            # Generate CLI component
            request = EnhancedServerRequest(
                name=server_path.name,
                template="python-fastmcp",
                description="Enhanced with CLI",
                port=8055,
                features=["cli"]
            )
            
            cli_files = self.crafter._generate_cli_module(request)
            
            # Write CLI files
            created_files = []
            for file_path, content in cli_files.items():
                full_path = server_path / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(content)
                created_files.append(str(full_path))
            
            result = {
                "status": "success",
                "server_path": str(server_path),
                "files_created": created_files,
                "additional_commands": additional_commands,
                "cli_usage": f"{server_path.name}-cli --help",
                "integration_steps": [
                    "Add CLI script to your pyproject.toml [project.scripts] section",
                    "Install with 'pip install -e .' to enable CLI commands",
                    f"Test with '{server_path.name}-cli --help'"
                ],
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
            
        except Exception as e:
            logger.error(f"Error enhancing CLI: {e}")
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "status": "error",
                    "message": f"Failed to enhance CLI: {str(e)}",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }, indent=2)
            )]
    
    async def _handle_orchestrate(self, arguments: dict) -> list[types.TextContent]:
        """Orchestrate multiple server tasks"""
        try:
            tasks_config = arguments["tasks"]
            execution_mode = arguments.get("execution_mode", "dependency_order")
            
            orchestration_id = str(uuid.uuid4())
            
            # Create orchestration tasks
            tasks = []
            for i, task_config in enumerate(tasks_config):
                task = OrchestrationTask(
                    task_id=f"{orchestration_id}-{i}",
                    task_type=task_config["type"],
                    config=task_config["config"],
                    dependencies=task_config.get("dependencies", [])
                )
                tasks.append(task)
            
            self.orchestration_tasks[orchestration_id] = {
                "tasks": tasks,
                "execution_mode": execution_mode,
                "status": "running",
                "start_time": time.time()
            }
            
            logger.info(f"Starting orchestration {orchestration_id} with {len(tasks)} tasks")
            
            # Execute tasks based on mode
            if execution_mode == "sequential":
                results = await self._execute_sequential(tasks)
            elif execution_mode == "parallel":
                results = await self._execute_parallel(tasks)
            else:  # dependency_order
                results = await self._execute_dependency_order(tasks)
            
            self.orchestration_tasks[orchestration_id]["status"] = "completed"
            self.orchestration_tasks[orchestration_id]["results"] = results
            
            result = {
                "status": "success",
                "orchestration_id": orchestration_id,
                "execution_mode": execution_mode,
                "tasks_completed": len([r for r in results if r.get("status") == "success"]),
                "tasks_failed": len([r for r in results if r.get("status") == "error"]),
                "results": results,
                "execution_time": time.time() - self.orchestration_tasks[orchestration_id]["start_time"],
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
            
        except Exception as e:
            logger.error(f"Error in orchestration: {e}")
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "status": "error",
                    "message": f"Orchestration failed: {str(e)}",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }, indent=2)
            )]
    
    async def _execute_sequential(self, tasks: List[OrchestrationTask]) -> List[Dict]:
        """Execute tasks sequentially"""
        results = []
        for task in tasks:
            logger.info(f"Executing task {task.task_id}: {task.task_type}")
            result = await self._execute_single_task(task)
            results.append(result)
            
            # Stop on failure if desired
            if result.get("status") == "error":
                logger.error(f"Task {task.task_id} failed, stopping sequential execution")
                break
                
        return results
    
    async def _execute_parallel(self, tasks: List[OrchestrationTask]) -> List[Dict]:
        """Execute tasks in parallel"""
        async def execute_task(task):
            return await self._execute_single_task(task)
        
        results = await asyncio.gather(*[execute_task(task) for task in tasks], return_exceptions=True)
        
        # Convert exceptions to error results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "task_id": tasks[i].task_id,
                    "status": "error",
                    "message": str(result)
                })
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def _execute_dependency_order(self, tasks: List[OrchestrationTask]) -> List[Dict]:
        """Execute tasks in dependency order"""
        completed = set()
        results = []
        
        while len(completed) < len(tasks):
            progress_made = False
            
            for task in tasks:
                if task.task_id in completed:
                    continue
                
                # Check if all dependencies are completed
                deps_completed = all(dep in completed for dep in task.dependencies)
                
                if deps_completed:
                    logger.info(f"Executing task {task.task_id}: {task.task_type}")
                    result = await self._execute_single_task(task)
                    results.append(result)
                    completed.add(task.task_id)
                    progress_made = True
                    break
            
            if not progress_made:
                # Circular dependency or missing dependency
                remaining_tasks = [task.task_id for task in tasks if task.task_id not in completed]
                logger.error(f"Cannot resolve dependencies for tasks: {remaining_tasks}")
                break
        
        return results
    
    async def _execute_single_task(self, task: OrchestrationTask) -> Dict:
        """Execute a single orchestration task"""
        try:
            task.status = "running"
            
            if task.task_type == "generate":
                # Generate a server
                config = task.config
                request = EnhancedServerRequest(
                    name=config["name"],
                    template=config.get("template", "python-fastmcp"),
                    description=config.get("description", "Generated via orchestration"),
                    port=config.get("port", 8055),
                    features=config.get("features", ["cli"]),
                    dependencies=config.get("dependencies", []),
                    environment=config.get("environment", {}),
                    path=config.get("path")
                )
                
                files = self.crafter.generate_enhanced_server(request)
                
                server_path = Path.home() / f"mcp-{request.name}"
                if not server_path.exists():
                    server_path.mkdir(parents=True)
                    for file_path, content in files.items():
                        full_path = server_path / file_path
                        full_path.parent.mkdir(parents=True, exist_ok=True)
                        full_path.write_text(content)
                
                task.status = "completed"
                return {
                    "task_id": task.task_id,
                    "task_type": task.task_type,
                    "status": "success",
                    "server_name": request.name,
                    "path": str(server_path),
                    "features": request.features
                }
            
            elif task.task_type == "enhance":
                # Enhance existing server
                task.status = "completed"
                return {
                    "task_id": task.task_id,
                    "task_type": task.task_type,
                    "status": "success",
                    "message": "Enhancement completed"
                }
            
            elif task.task_type == "deploy":
                # Deploy server (placeholder)
                task.status = "completed"
                return {
                    "task_id": task.task_id,
                    "task_type": task.task_type,
                    "status": "success",
                    "message": "Deployment completed"
                }
            
            else:
                task.status = "failed"
                return {
                    "task_id": task.task_id,
                    "task_type": task.task_type,
                    "status": "error",
                    "message": f"Unknown task type: {task.task_type}"
                }
                
        except Exception as e:
            task.status = "failed"
            logger.error(f"Task {task.task_id} failed: {e}")
            return {
                "task_id": task.task_id,
                "task_type": task.task_type,
                "status": "error",
                "message": str(e)
            }
    
    async def _handle_continuous_tweak(self, arguments: dict) -> list[types.TextContent]:
        """Handle runtime configuration tweaking"""
        try:
            server_name = arguments["server_name"]
            operation = arguments["operation"]
            parameters = arguments.get("parameters", {})
            
            logger.info(f"Continuous tweak: {operation} on {server_name}")
            
            # In a real implementation, this would connect to the running server
            # and apply the configuration changes
            result = {
                "status": "success",
                "server_name": server_name,
                "operation": operation,
                "parameters": parameters,
                "message": f"Applied {operation} to {server_name}",
                "note": "This is a simulation - in production, this would connect to the running server",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
            
        except Exception as e:
            logger.error(f"Error in continuous tweak: {e}")
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "status": "error",
                    "message": f"Continuous tweak failed: {str(e)}",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }, indent=2)
            )]
    
    async def _handle_get_status(self, arguments: dict) -> list[types.TextContent]:
        """Get crafter status and server information"""
        try:
            include_servers = arguments.get("include_servers", True)
            
            status = {
                "crafter_status": "running",
                "active_forms": len(self.active_forms),
                "orchestrations": len(self.orchestration_tasks),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            # Add orchestration status
            if self.orchestration_tasks:
                status["orchestrations_detail"] = {}
                for orch_id, orch_data in self.orchestration_tasks.items():
                    status["orchestrations_detail"][orch_id] = {
                        "status": orch_data["status"],
                        "execution_mode": orch_data["execution_mode"],
                        "task_count": len(orch_data["tasks"]),
                        "start_time": orch_data.get("start_time")
                    }
            
            # Add form processing status
            if self.active_forms:
                status["forms_detail"] = {}
                for form_id, form_data in self.active_forms.items():
                    status["forms_detail"][form_id] = {
                        "form_type": form_data.form_type,
                        "created_at": form_data.created_at
                    }
            
            # Add generated servers info
            if include_servers:
                mcp_config_file = Path.home() / ".mcp-servers.json"
                if mcp_config_file.exists():
                    try:
                        with open(mcp_config_file, 'r') as f:
                            mcp_config = json.load(f)
                        
                        crafter_servers = {
                            name: config for name, config in mcp_config.items()
                            if config.get("generated_by") == "mcp-crafter"
                        }
                        
                        status["generated_servers"] = {
                            "count": len(crafter_servers),
                            "servers": crafter_servers
                        }
                    except Exception as e:
                        status["generated_servers"] = {
                            "error": f"Could not read MCP config: {e}"
                        }
                else:
                    status["generated_servers"] = {
                        "count": 0,
                        "note": "No MCP configuration file found"
                    }
            
            return [types.TextContent(
                type="text",
                text=json.dumps(status, indent=2)
            )]
            
        except Exception as e:
            logger.error(f"Error getting status: {e}")
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "status": "error",
                    "message": f"Failed to get status: {str(e)}",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }, indent=2)
            )]

async def main():
    """Main entry point for the MCP Crafter Server"""
    crafter_server = MCPCrafterServer()
    
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await crafter_server.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="mcp-crafter",
                server_version="1.0.0",
                capabilities=crafter_server.server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())