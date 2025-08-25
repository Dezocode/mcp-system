#!/usr/bin/env python3
"""
MCP Orchestrator Server - Windows Docker Integration with Watchdog and CLI Resolution
Model Context Protocol v1.0 Compliant Server

This server provides comprehensive orchestration capabilities:
1. docker_operation - Execute Docker CLI commands with enhanced capabilities
2. environment_setup - Setup and configure MCP system environment
3. container_management - Manage Docker containers lifecycle
4. watchdog_monitoring - Monitor file systems and services
5. cli_resolution - Resolve and execute CLI commands
6. windows_integration - Windows-specific Docker operations
7. health_monitoring - Comprehensive system health checks
8. deployment_orchestration - Automate deployment workflows

Author: DezoCode
Version: 1.0.0
MCP Protocol: v1.0
"""

import asyncio
import json
import os
import platform
import shutil
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import click
import psutil
from dotenv import load_dotenv

# Add the repository root to path for imports
repo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(repo_root))

try:
    import docker
    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False

# Import existing infrastructure
try:
    from src.config.environment_detector import EnvironmentDetector
    from src.docker.health_check import DockerHealthCheck
    INFRASTRUCTURE_AVAILABLE = True
except ImportError:
    INFRASTRUCTURE_AVAILABLE = False

# MCP Protocol Imports
from mcp.server.models import InitializationOptions
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    INVALID_PARAMS,
    METHOD_NOT_FOUND,
    INTERNAL_ERROR,
)

# Load environment configuration
load_dotenv()

# Configure logging
import logging
logging.basicConfig(
    level=getattr(logging, os.getenv("MCP_LOG_LEVEL", "INFO")),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# MCP Error compatibility layer
class McpError(Exception):
    """MCP Error compatibility wrapper"""
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(message)

# Error codes for compatibility
class ErrorCode:
    INVALID_PARAMS = -32602
    METHOD_NOT_FOUND = -32601  
    INTERNAL_ERROR = -32603


class WindowsDockerIntegration:
    """Windows Docker Desktop and WSL integration handler."""
    
    def __init__(self):
        self.is_windows = platform.system().lower() == "windows"
        self.wsl_distro = os.getenv("WSL_DISTRO", "Ubuntu")
        self.wsl_user = os.getenv("WSL_USER", "runner")
        self.docker_desktop_enabled = os.getenv("DOCKER_DESKTOP_ENABLED", "true").lower() == "true"
        
        # Initialize Docker client if available
        self.docker_client = None
        if DOCKER_AVAILABLE:
            try:
                self.docker_client = docker.from_env(
                    timeout=int(os.getenv("DOCKER_TIMEOUT", "30"))
                )
                # Test connection
                self.docker_client.ping()
                logger.info("Docker client initialized successfully")
            except Exception as e:
                logger.warning(f"Docker client initialization failed: {e}")
                self.docker_client = None
    
    def detect_wsl_environment(self) -> Dict[str, Any]:
        """Detect WSL environment and configuration."""
        wsl_info = {
            "is_wsl": False,
            "distro": None,
            "version": None,
            "docker_integration": False,
            "available_distros": []
        }
        
        if self.is_windows:
            try:
                # Check if WSL is available
                result = subprocess.run(
                    ["wsl", "--list", "--verbose"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    wsl_info["is_wsl"] = True
                    wsl_info["available_distros"] = self._parse_wsl_distros(result.stdout)
            except Exception as e:
                logger.debug(f"WSL detection failed: {e}")
        else:
            # Check if running inside WSL
            try:
                with open("/proc/version", "r") as f:
                    version_info = f.read().lower()
                    if "microsoft" in version_info or "wsl" in version_info:
                        wsl_info["is_wsl"] = True
                        wsl_info["distro"] = os.getenv("WSL_DISTRO_NAME", "Unknown")
            except Exception as e:
                logger.debug(f"WSL environment check failed: {e}")
        
        return wsl_info
    
    def _parse_wsl_distros(self, wsl_output: str) -> List[Dict[str, str]]:
        """Parse WSL list output to extract distro information."""
        distros = []
        lines = wsl_output.strip().split('\n')
        
        for line in lines[1:]:  # Skip header
            if line.strip():
                parts = line.split()
                if len(parts) >= 3:
                    name = parts[0].strip('*')
                    state = parts[1]
                    version = parts[2]
                    distros.append({
                        "name": name,
                        "state": state,
                        "version": version,
                        "default": "*" in line
                    })
        
        return distros
    
    async def execute_docker_command(self, command: List[str], use_wsl: bool = False) -> Tuple[int, str, str]:
        """Execute Docker command with WSL integration support."""
        if use_wsl and self.is_windows:
            # Execute via WSL
            wsl_command = ["wsl", "-d", self.wsl_distro, "-u", self.wsl_user] + command
            logger.info(f"Executing via WSL: {' '.join(wsl_command)}")
        else:
            wsl_command = command
            logger.info(f"Executing directly: {' '.join(command)}")
        
        try:
            process = await asyncio.create_subprocess_exec(
                *wsl_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            return process.returncode, stdout.decode(), stderr.decode()
            
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            return -1, "", str(e)
    
    def get_docker_desktop_status(self) -> Dict[str, Any]:
        """Get Docker Desktop status and configuration."""
        status = {
            "available": False,
            "running": False,
            "version": None,
            "wsl_integration": False,
            "containers": 0,
            "images": 0
        }
        
        if self.docker_client:
            try:
                # Get Docker version
                version_info = self.docker_client.version()
                status["available"] = True
                status["version"] = version_info.get("Version", "Unknown")
                
                # Check if Docker is running
                self.docker_client.ping()
                status["running"] = True
                
                # Get container and image counts
                containers = self.docker_client.containers.list(all=True)
                images = self.docker_client.images.list()
                status["containers"] = len(containers)
                status["images"] = len(images)
                
                # Check WSL integration (Windows specific)
                if self.is_windows:
                    status["wsl_integration"] = self._check_wsl_docker_integration()
                
            except Exception as e:
                logger.debug(f"Docker status check failed: {e}")
                status["error"] = str(e)
        
        return status
    
    def _check_wsl_docker_integration(self) -> bool:
        """Check if Docker Desktop has WSL2 integration enabled."""
        try:
            # Check if Docker can be accessed from WSL
            if self.docker_client:
                # Try to run a simple Docker command to test integration
                version_info = self.docker_client.version()
                return "WSL" in version_info.get("Os", "") or "linux" in version_info.get("Os", "").lower()
            return False
        except Exception:
            return False


class WatchdogMonitor:
    """Enhanced watchdog monitoring using existing infrastructure."""
    
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.observers = {}
        self.enabled = os.getenv("WATCHDOG_ENABLED", "true").lower() == "true"
        self.monitored_paths = []
        
        if WATCHDOG_AVAILABLE and self.enabled:
            logger.info("Watchdog monitoring initialized")
        else:
            logger.warning("Watchdog monitoring disabled or unavailable")
    
    def start_monitoring(self, path: str, recursive: bool = True) -> str:
        """Start monitoring a specific path."""
        if not WATCHDOG_AVAILABLE or not self.enabled:
            return "Watchdog not available"
        
        monitor_id = f"monitor_{uuid.uuid4().hex[:8]}"
        
        try:
            class ChangeHandler(FileSystemEventHandler):
                def __init__(self, monitor_id: str):
                    self.monitor_id = monitor_id
                    self.changes = []
                
                def on_any_event(self, event):
                    if not event.is_directory:
                        self.changes.append({
                            "timestamp": time.time(),
                            "event_type": event.event_type,
                            "src_path": event.src_path,
                            "is_directory": event.is_directory
                        })
            
            handler = ChangeHandler(monitor_id)
            observer = Observer()
            observer.schedule(handler, path, recursive=recursive)
            observer.start()
            
            self.observers[monitor_id] = {
                "observer": observer,
                "handler": handler,
                "path": path,
                "started": time.time()
            }
            
            self.monitored_paths.append(path)
            logger.info(f"Started monitoring {path} with ID {monitor_id}")
            return monitor_id
            
        except Exception as e:
            logger.error(f"Failed to start monitoring {path}: {e}")
            return f"Error: {e}"
    
    def stop_monitoring(self, monitor_id: str) -> bool:
        """Stop monitoring for a specific monitor ID."""
        if monitor_id in self.observers:
            try:
                self.observers[monitor_id]["observer"].stop()
                self.observers[monitor_id]["observer"].join()
                del self.observers[monitor_id]
                logger.info(f"Stopped monitoring {monitor_id}")
                return True
            except Exception as e:
                logger.error(f"Failed to stop monitoring {monitor_id}: {e}")
                return False
        return False
    
    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get current monitoring status and statistics."""
        status = {
            "enabled": self.enabled,
            "available": WATCHDOG_AVAILABLE,
            "active_monitors": len(self.observers),
            "monitored_paths": self.monitored_paths,
            "monitors": {}
        }
        
        for monitor_id, info in self.observers.items():
            status["monitors"][monitor_id] = {
                "path": info["path"],
                "started": info["started"],
                "uptime": time.time() - info["started"],
                "changes_detected": len(info["handler"].changes),
                "recent_changes": info["handler"].changes[-5:]  # Last 5 changes
            }
        
        return status


class CLIResolver:
    """Enhanced CLI command resolution and execution."""
    
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.timeout = int(os.getenv("CLI_TIMEOUT", "300"))
        self.shell = os.getenv("CLI_SHELL", "/bin/bash")
        self.safe_mode = os.getenv("SAFE_MODE", "true").lower() == "true"
        self.allowed_operations = os.getenv("ALLOWED_DOCKER_OPERATIONS", "start,stop,restart,status,logs,inspect").split(",")
        self.restricted_paths = os.getenv("RESTRICTED_PATHS", "/etc,/sys,/proc").split(",")
    
    def validate_command(self, command: List[str]) -> Tuple[bool, str]:
        """Validate command for security and safety."""
        if not command:
            return False, "Empty command"
        
        cmd_str = " ".join(command).lower()
        
        # Check for restricted operations in safe mode
        if self.safe_mode:
            dangerous_commands = ["rm -rf", "format", "del /s", ":(){ :|:& };:", "chmod 777"]
            for dangerous in dangerous_commands:
                if dangerous in cmd_str:
                    return False, f"Dangerous command detected: {dangerous}"
        
        # Check Docker operations
        if command[0] == "docker" and len(command) > 1:
            operation = command[1]
            if operation not in self.allowed_operations:
                return False, f"Docker operation '{operation}' not allowed"
        
        # Check path restrictions
        for path in self.restricted_paths:
            if path in cmd_str:
                return False, f"Access to restricted path '{path}' not allowed"
        
        return True, "Command validated"
    
    async def execute_command(self, command: List[str], cwd: Optional[str] = None) -> Dict[str, Any]:
        """Execute command with comprehensive error handling."""
        start_time = time.time()
        
        # Validate command
        is_valid, validation_msg = self.validate_command(command)
        if not is_valid:
            return {
                "success": False,
                "error": validation_msg,
                "returncode": -1,
                "stdout": "",
                "stderr": validation_msg,
                "execution_time": 0
            }
        
        try:
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd or str(self.workspace_root)
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=self.timeout
                )
                
                execution_time = time.time() - start_time
                
                return {
                    "success": process.returncode == 0,
                    "returncode": process.returncode,
                    "stdout": stdout.decode(),
                    "stderr": stderr.decode(),
                    "execution_time": execution_time,
                    "command": " ".join(command)
                }
                
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                return {
                    "success": False,
                    "error": f"Command timed out after {self.timeout} seconds",
                    "returncode": -1,
                    "stdout": "",
                    "stderr": "Timeout",
                    "execution_time": time.time() - start_time
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "returncode": -1,
                "stdout": "",
                "stderr": str(e),
                "execution_time": time.time() - start_time
            }


class OrchestratorServer:
    """Main MCP Orchestrator Server class."""
    
    def __init__(self):
        self.server = Server("orchestrator")
        self.workspace_root = Path(os.getenv("MCP_WORKSPACE_ROOT", Path.cwd()))
        self.session_dir = Path(os.getenv("MCP_SESSION_DIR", "./pipeline-sessions"))
        
        # Initialize subsystems
        self.windows_docker = WindowsDockerIntegration()
        self.watchdog = WatchdogMonitor(self.workspace_root)
        self.cli_resolver = CLIResolver(self.workspace_root)
        
        # Initialize infrastructure if available
        self.environment_detector = None
        self.docker_health_check = None
        
        if INFRASTRUCTURE_AVAILABLE:
            try:
                self.environment_detector = EnvironmentDetector()
                self.docker_health_check = DockerHealthCheck()
                logger.info("Infrastructure components initialized")
            except Exception as e:
                logger.warning(f"Infrastructure initialization failed: {e}")
        
        # Ensure directories exist
        self.session_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Orchestrator initialized at {self.workspace_root}")
        logger.info(f"Session directory: {self.session_dir}")


# Initialize server instance
orchestrator_server = OrchestratorServer()


@orchestrator_server.server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List all available orchestrator tools."""
    return [
        Tool(
            name="docker_operation",
            description="Execute Docker CLI commands with enhanced Windows and WSL integration",
            inputSchema={
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["status", "start", "stop", "restart", "logs", "inspect", "ps", "images", "deploy"],
                        "description": "Docker operation to perform"
                    },
                    "target": {
                        "type": "string",
                        "description": "Container name, image name, or service target"
                    },
                    "use_wsl": {
                        "type": "boolean",
                        "description": "Execute command via WSL (Windows only)",
                        "default": False
                    },
                    "options": {
                        "type": "object",
                        "description": "Additional command options",
                        "properties": {
                            "follow": {"type": "boolean", "description": "Follow logs (for logs operation)"},
                            "all": {"type": "boolean", "description": "Show all containers/images"},
                            "stack": {"type": "string", "description": "Docker stack name (for deploy operation)"}
                        }
                    }
                },
                "required": ["operation"]
            }
        ),
        Tool(
            name="environment_setup",
            description="Setup and configure MCP system environment with Windows Docker integration",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["detect", "setup", "validate", "configure", "install_dependencies"],
                        "description": "Setup action to perform"
                    },
                    "components": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Components to setup (docker, wsl, mcp, watchdog)"
                    },
                    "force": {
                        "type": "boolean",
                        "description": "Force setup even if already configured",
                        "default": False
                    }
                },
                "required": ["action"]
            }
        ),
        Tool(
            name="container_management",
            description="Advanced Docker container lifecycle management",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["list", "create", "start", "stop", "remove", "inspect", "logs", "exec"],
                        "description": "Container management action"
                    },
                    "container_id": {
                        "type": "string",
                        "description": "Container ID or name"
                    },
                    "image": {
                        "type": "string",
                        "description": "Docker image name (for create action)"
                    },
                    "command": {
                        "type": "string",
                        "description": "Command to execute (for exec action)"
                    },
                    "options": {
                        "type": "object",
                        "description": "Additional options for the action"
                    }
                },
                "required": ["action"]
            }
        ),
        Tool(
            name="watchdog_monitoring",
            description="Real-time file system and service monitoring with enhanced watchdog",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["start", "stop", "status", "list", "changes"],
                        "description": "Monitoring action to perform"
                    },
                    "path": {
                        "type": "string",
                        "description": "Path to monitor (for start action)"
                    },
                    "monitor_id": {
                        "type": "string",
                        "description": "Monitor ID (for stop, status actions)"
                    },
                    "recursive": {
                        "type": "boolean",
                        "description": "Monitor subdirectories recursively",
                        "default": True
                    }
                },
                "required": ["action"]
            }
        ),
        Tool(
            name="cli_resolution",
            description="Resolve and execute CLI commands with environment awareness",
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Command and arguments to execute"
                    },
                    "working_directory": {
                        "type": "string",
                        "description": "Working directory for command execution"
                    },
                    "environment": {
                        "type": "object",
                        "description": "Environment variables for command"
                    },
                    "validate_only": {
                        "type": "boolean",
                        "description": "Only validate command without executing",
                        "default": False
                    }
                },
                "required": ["command"]
            }
        ),
        Tool(
            name="windows_integration",
            description="Windows-specific Docker and WSL integration operations",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["wsl_status", "docker_desktop_status", "distro_list", "integration_check"],
                        "description": "Windows integration action"
                    },
                    "distro": {
                        "type": "string",
                        "description": "WSL distro name (for distro-specific actions)"
                    }
                },
                "required": ["action"]
            }
        ),
        Tool(
            name="health_monitoring",
            description="Comprehensive system and Docker health monitoring",
            inputSchema={
                "type": "object",
                "properties": {
                    "scope": {
                        "type": "string",
                        "enum": ["system", "docker", "containers", "services", "all"],
                        "description": "Health monitoring scope"
                    },
                    "detailed": {
                        "type": "boolean",
                        "description": "Include detailed health information",
                        "default": True
                    }
                },
                "required": ["scope"]
            }
        ),
        Tool(
            name="deployment_orchestration",
            description="Automate deployment workflows with Docker and environment integration",
            inputSchema={
                "type": "object",
                "properties": {
                    "workflow": {
                        "type": "string",
                        "enum": ["development", "production", "testing", "custom"],
                        "description": "Deployment workflow type"
                    },
                    "config_file": {
                        "type": "string",
                        "description": "Path to deployment configuration file"
                    },
                    "dry_run": {
                        "type": "boolean",
                        "description": "Perform dry run without actual deployment",
                        "default": False
                    },
                    "steps": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Specific deployment steps to execute"
                    }
                },
                "required": ["workflow"]
            }
        )
    ]


@orchestrator_server.server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls with comprehensive error handling."""
    
    try:
        if name == "docker_operation":
            return await handle_docker_operation(arguments)
        elif name == "environment_setup":
            return await handle_environment_setup(arguments)
        elif name == "container_management":
            return await handle_container_management(arguments)
        elif name == "watchdog_monitoring":
            return await handle_watchdog_monitoring(arguments)
        elif name == "cli_resolution":
            return await handle_cli_resolution(arguments)
        elif name == "windows_integration":
            return await handle_windows_integration(arguments)
        elif name == "health_monitoring":
            return await handle_health_monitoring(arguments)
        elif name == "deployment_orchestration":
            return await handle_deployment_orchestration(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
            
    except Exception as e:
        logger.error(f"Tool {name} failed: {str(e)}")
        return [TextContent(
            type="text",
            text=json.dumps({
                "tool": name,
                "status": "error",
                "error": str(e),
                "timestamp": time.time()
            }, indent=2)
        )]


async def handle_docker_operation(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle Docker operation requests."""
    operation = arguments.get("operation")
    target = arguments.get("target")
    use_wsl = arguments.get("use_wsl", False)
    options = arguments.get("options", {})
    
    # Build Docker command
    if operation == "status":
        command = ["docker", "info"]
    elif operation == "ps":
        command = ["docker", "ps"]
        if options.get("all"):
            command.append("-a")
    elif operation == "images":
        command = ["docker", "images"]
    elif operation in ["start", "stop", "restart"]:
        if not target:
            raise ValueError(f"{operation} operation requires a target")
        command = ["docker", operation, target]
    elif operation == "logs":
        if not target:
            raise ValueError("logs operation requires a target")
        command = ["docker", "logs", target]
        if options.get("follow"):
            command.append("-f")
    elif operation == "inspect":
        if not target:
            raise ValueError("inspect operation requires a target")
        command = ["docker", "inspect", target]
    elif operation == "deploy":
        stack = options.get("stack", "default")
        command = ["docker", "stack", "deploy", "-c", "docker-compose.yml", stack]
    else:
        raise ValueError(f"Unknown Docker operation: {operation}")
    
    # Execute command
    returncode, stdout, stderr = await orchestrator_server.windows_docker.execute_docker_command(
        command, use_wsl=use_wsl
    )
    
    # Get Docker Desktop status for additional context
    docker_status = orchestrator_server.windows_docker.get_docker_desktop_status()
    
    result = {
        "tool": "docker_operation",
        "operation": operation,
        "target": target,
        "use_wsl": use_wsl,
        "command": " ".join(command),
        "success": returncode == 0,
        "returncode": returncode,
        "stdout": stdout,
        "stderr": stderr,
        "docker_status": docker_status,
        "timestamp": time.time()
    }
    
    return [TextContent(
        type="text",
        text=json.dumps(result, indent=2)
    )]


async def handle_environment_setup(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle environment setup requests."""
    action = arguments.get("action")
    components = arguments.get("components", [])
    force = arguments.get("force", False)
    
    result = {
        "tool": "environment_setup",
        "action": action,
        "components": components,
        "results": {}
    }
    
    if action == "detect":
        # Environment detection
        detection_results = {
            "platform": platform.system(),
            "architecture": platform.machine(),
            "python_version": platform.python_version(),
            "workspace_root": str(orchestrator_server.workspace_root),
            "docker_available": DOCKER_AVAILABLE,
            "watchdog_available": WATCHDOG_AVAILABLE,
            "infrastructure_available": INFRASTRUCTURE_AVAILABLE
        }
        
        # Windows-specific detection
        if orchestrator_server.windows_docker.is_windows:
            detection_results["wsl"] = orchestrator_server.windows_docker.detect_wsl_environment()
            detection_results["docker_desktop"] = orchestrator_server.windows_docker.get_docker_desktop_status()
        
        # Infrastructure detection if available
        if orchestrator_server.environment_detector:
            env_info = orchestrator_server.environment_detector.detect_environment()
            detection_results["detailed_environment"] = {
                "is_docker": env_info.is_docker,
                "container_type": env_info.container_type,
                "working_directory": env_info.working_directory,
                "hostname": env_info.hostname
            }
        
        result["results"]["detection"] = detection_results
        
    elif action == "setup":
        # Setup components
        setup_results = {}
        
        for component in components:
            if component == "directories":
                # Create necessary directories
                directories = [
                    orchestrator_server.session_dir,
                    orchestrator_server.workspace_root / "logs",
                    orchestrator_server.workspace_root / "tmp"
                ]
                for directory in directories:
                    directory.mkdir(parents=True, exist_ok=True)
                setup_results[component] = "Directories created successfully"
                
            elif component == "docker":
                # Docker setup validation
                docker_status = orchestrator_server.windows_docker.get_docker_desktop_status()
                setup_results[component] = docker_status
                
            elif component == "watchdog":
                # Watchdog setup
                if WATCHDOG_AVAILABLE:
                    monitor_id = orchestrator_server.watchdog.start_monitoring(
                        str(orchestrator_server.workspace_root)
                    )
                    setup_results[component] = f"Watchdog monitoring started: {monitor_id}"
                else:
                    setup_results[component] = "Watchdog not available"
                    
        result["results"]["setup"] = setup_results
        
    elif action == "validate":
        # Validate current setup
        validation_results = {
            "workspace_exists": orchestrator_server.workspace_root.exists(),
            "session_dir_exists": orchestrator_server.session_dir.exists(),
            "docker_functional": False,
            "watchdog_functional": WATCHDOG_AVAILABLE,
            "cli_resolver_ready": True
        }
        
        # Test Docker functionality
        if orchestrator_server.windows_docker.docker_client:
            try:
                orchestrator_server.windows_docker.docker_client.ping()
                validation_results["docker_functional"] = True
            except Exception:
                pass
        
        result["results"]["validation"] = validation_results
        
    result["timestamp"] = time.time()
    
    return [TextContent(
        type="text",
        text=json.dumps(result, indent=2)
    )]


async def handle_container_management(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle container management requests."""
    action = arguments.get("action")
    container_id = arguments.get("container_id")
    image = arguments.get("image")
    command = arguments.get("command")
    options = arguments.get("options", {})
    
    result = {
        "tool": "container_management",
        "action": action,
        "container_id": container_id
    }
    
    if not orchestrator_server.windows_docker.docker_client:
        result["error"] = "Docker client not available"
        result["success"] = False
    else:
        try:
            client = orchestrator_server.windows_docker.docker_client
            
            if action == "list":
                containers = client.containers.list(all=options.get("all", True))
                result["containers"] = [
                    {
                        "id": container.short_id,
                        "name": container.name,
                        "status": container.status,
                        "image": container.image.tags[0] if container.image.tags else "unknown"
                    }
                    for container in containers
                ]
                result["success"] = True
                
            elif action == "inspect" and container_id:
                container = client.containers.get(container_id)
                result["container_info"] = {
                    "id": container.id,
                    "name": container.name,
                    "status": container.status,
                    "image": container.image.tags[0] if container.image.tags else "unknown",
                    "created": container.attrs["Created"],
                    "ports": container.ports,
                    "labels": container.labels
                }
                result["success"] = True
                
            elif action in ["start", "stop", "remove"] and container_id:
                container = client.containers.get(container_id)
                if action == "start":
                    container.start()
                elif action == "stop":
                    container.stop()
                elif action == "remove":
                    container.remove()
                result["success"] = True
                result["message"] = f"Container {action} successful"
                
            elif action == "create" and image:
                container = client.containers.create(image, **options)
                result["container_id"] = container.id
                result["success"] = True
                result["message"] = "Container created successfully"
                
            elif action == "exec" and container_id and command:
                container = client.containers.get(container_id)
                exec_result = container.exec_run(command)
                result["exit_code"] = exec_result.exit_code
                result["output"] = exec_result.output.decode()
                result["success"] = True
                
            else:
                result["error"] = f"Invalid action '{action}' or missing required parameters"
                result["success"] = False
                
        except Exception as e:
            result["error"] = str(e)
            result["success"] = False
    
    result["timestamp"] = time.time()
    
    return [TextContent(
        type="text",
        text=json.dumps(result, indent=2)
    )]


async def handle_watchdog_monitoring(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle watchdog monitoring requests."""
    action = arguments.get("action")
    path = arguments.get("path")
    monitor_id = arguments.get("monitor_id")
    recursive = arguments.get("recursive", True)
    
    result = {
        "tool": "watchdog_monitoring",
        "action": action
    }
    
    if action == "start" and path:
        monitor_id = orchestrator_server.watchdog.start_monitoring(path, recursive)
        result["monitor_id"] = monitor_id
        result["path"] = path
        result["recursive"] = recursive
        result["success"] = "Error:" not in monitor_id
        
    elif action == "stop" and monitor_id:
        success = orchestrator_server.watchdog.stop_monitoring(monitor_id)
        result["monitor_id"] = monitor_id
        result["success"] = success
        
    elif action == "status":
        if monitor_id:
            # Get specific monitor status
            status = orchestrator_server.watchdog.get_monitoring_status()
            if monitor_id in status["monitors"]:
                result["monitor_status"] = status["monitors"][monitor_id]
                result["success"] = True
            else:
                result["error"] = f"Monitor {monitor_id} not found"
                result["success"] = False
        else:
            # Get all monitoring status
            result["monitoring_status"] = orchestrator_server.watchdog.get_monitoring_status()
            result["success"] = True
            
    elif action == "list":
        status = orchestrator_server.watchdog.get_monitoring_status()
        result["active_monitors"] = list(status["monitors"].keys())
        result["monitored_paths"] = status["monitored_paths"]
        result["success"] = True
        
    else:
        result["error"] = f"Invalid action '{action}' or missing required parameters"
        result["success"] = False
    
    result["timestamp"] = time.time()
    
    return [TextContent(
        type="text",
        text=json.dumps(result, indent=2)
    )]


async def handle_cli_resolution(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle CLI command resolution requests."""
    command = arguments.get("command", [])
    working_directory = arguments.get("working_directory")
    environment = arguments.get("environment", {})
    validate_only = arguments.get("validate_only", False)
    
    result = {
        "tool": "cli_resolution",
        "command": command,
        "validate_only": validate_only
    }
    
    if validate_only:
        # Only validate the command
        is_valid, validation_msg = orchestrator_server.cli_resolver.validate_command(command)
        result["valid"] = is_valid
        result["validation_message"] = validation_msg
        result["success"] = True
    else:
        # Execute the command
        execution_result = await orchestrator_server.cli_resolver.execute_command(
            command, cwd=working_directory
        )
        result.update(execution_result)
    
    result["timestamp"] = time.time()
    
    return [TextContent(
        type="text",
        text=json.dumps(result, indent=2)
    )]


async def handle_windows_integration(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle Windows integration requests."""
    action = arguments.get("action")
    distro = arguments.get("distro")
    
    result = {
        "tool": "windows_integration",
        "action": action
    }
    
    if action == "wsl_status":
        wsl_info = orchestrator_server.windows_docker.detect_wsl_environment()
        result["wsl_environment"] = wsl_info
        result["success"] = True
        
    elif action == "docker_desktop_status":
        docker_status = orchestrator_server.windows_docker.get_docker_desktop_status()
        result["docker_desktop"] = docker_status
        result["success"] = True
        
    elif action == "distro_list":
        wsl_info = orchestrator_server.windows_docker.detect_wsl_environment()
        result["available_distros"] = wsl_info.get("available_distros", [])
        result["success"] = True
        
    elif action == "integration_check":
        # Comprehensive integration check
        integration_status = {
            "platform": platform.system(),
            "wsl": orchestrator_server.windows_docker.detect_wsl_environment(),
            "docker": orchestrator_server.windows_docker.get_docker_desktop_status(),
            "docker_available": DOCKER_AVAILABLE,
            "watchdog_available": WATCHDOG_AVAILABLE
        }
        result["integration_status"] = integration_status
        result["success"] = True
        
    else:
        result["error"] = f"Unknown action: {action}"
        result["success"] = False
    
    result["timestamp"] = time.time()
    
    return [TextContent(
        type="text",
        text=json.dumps(result, indent=2)
    )]


async def handle_health_monitoring(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle health monitoring requests."""
    scope = arguments.get("scope")
    detailed = arguments.get("detailed", True)
    
    result = {
        "tool": "health_monitoring",
        "scope": scope,
        "detailed": detailed
    }
    
    health_data = {}
    
    if scope in ["system", "all"]:
        # System health
        health_data["system"] = {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory": dict(psutil.virtual_memory()._asdict()),
            "disk": dict(psutil.disk_usage("/")._asdict()),
            "boot_time": psutil.boot_time(),
            "process_count": len(psutil.pids())
        }
        
    if scope in ["docker", "all"] and orchestrator_server.windows_docker.docker_client:
        # Docker health
        try:
            docker_info = orchestrator_server.windows_docker.docker_client.info()
            health_data["docker"] = {
                "containers_running": docker_info.get("ContainersRunning", 0),
                "containers_paused": docker_info.get("ContainersPaused", 0),
                "containers_stopped": docker_info.get("ContainersStopped", 0),
                "images": docker_info.get("Images", 0),
                "server_version": docker_info.get("ServerVersion", "unknown"),
                "kernel_version": docker_info.get("KernelVersion", "unknown")
            }
        except Exception as e:
            health_data["docker"] = {"error": str(e)}
    
    if scope in ["containers", "all"] and orchestrator_server.windows_docker.docker_client:
        # Container health
        try:
            containers = orchestrator_server.windows_docker.docker_client.containers.list(all=True)
            health_data["containers"] = [
                {
                    "id": container.short_id,
                    "name": container.name,
                    "status": container.status,
                    "health": getattr(container.attrs.get("State", {}), "Health", {}).get("Status", "unknown")
                }
                for container in containers
            ]
        except Exception as e:
            health_data["containers"] = {"error": str(e)}
    
    if scope in ["services", "all"]:
        # Services health (watchdog, CLI resolver, etc.)
        health_data["services"] = {
            "watchdog": {
                "enabled": orchestrator_server.watchdog.enabled,
                "available": WATCHDOG_AVAILABLE,
                "active_monitors": len(orchestrator_server.watchdog.observers)
            },
            "cli_resolver": {
                "safe_mode": orchestrator_server.cli_resolver.safe_mode,
                "timeout": orchestrator_server.cli_resolver.timeout
            },
            "windows_docker": {
                "docker_client_available": orchestrator_server.windows_docker.docker_client is not None,
                "is_windows": orchestrator_server.windows_docker.is_windows
            }
        }
    
    # Use infrastructure health check if available
    if orchestrator_server.docker_health_check and detailed:
        try:
            infrastructure_health = orchestrator_server.docker_health_check.get_health_check_endpoint_response()
            health_data["infrastructure"] = infrastructure_health
        except Exception as e:
            health_data["infrastructure"] = {"error": str(e)}
    
    result["health_data"] = health_data
    result["success"] = True
    result["timestamp"] = time.time()
    
    return [TextContent(
        type="text",
        text=json.dumps(result, indent=2)
    )]


async def handle_deployment_orchestration(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle deployment orchestration requests."""
    workflow = arguments.get("workflow")
    config_file = arguments.get("config_file")
    dry_run = arguments.get("dry_run", False)
    steps = arguments.get("steps", [])
    
    result = {
        "tool": "deployment_orchestration",
        "workflow": workflow,
        "dry_run": dry_run
    }
    
    # Define workflow steps
    workflow_steps = {
        "development": [
            "environment_check",
            "dependency_check",
            "build_containers",
            "start_services",
            "health_check"
        ],
        "production": [
            "environment_check",
            "security_check",
            "backup_current",
            "build_production_containers",
            "deploy_services",
            "health_check",
            "smoke_test"
        ],
        "testing": [
            "environment_check",
            "build_test_containers",
            "run_tests",
            "cleanup"
        ]
    }
    
    if workflow not in workflow_steps and workflow != "custom":
        result["error"] = f"Unknown workflow: {workflow}"
        result["success"] = False
    else:
        deployment_steps = steps if workflow == "custom" else workflow_steps[workflow]
        execution_results = []
        
        for step in deployment_steps:
            step_result = {"step": step, "status": "pending"}
            
            if dry_run:
                step_result["status"] = "skipped (dry run)"
                step_result["description"] = f"Would execute: {step}"
            else:
                try:
                    # Execute deployment step
                    if step == "environment_check":
                        # Check environment readiness
                        env_check = await handle_environment_setup({"action": "validate"})
                        step_result["status"] = "completed"
                        step_result["details"] = json.loads(env_check[0].text)
                        
                    elif step == "dependency_check":
                        # Check dependencies
                        deps = {
                            "docker": DOCKER_AVAILABLE,
                            "watchdog": WATCHDOG_AVAILABLE,
                            "infrastructure": INFRASTRUCTURE_AVAILABLE
                        }
                        step_result["status"] = "completed"
                        step_result["dependencies"] = deps
                        
                    elif step == "build_containers":
                        # Build containers
                        build_result = await orchestrator_server.cli_resolver.execute_command(
                            ["docker", "build", "-t", "orchestrator:latest", "."]
                        )
                        step_result["status"] = "completed" if build_result["success"] else "failed"
                        step_result["build_output"] = build_result
                        
                    elif step == "health_check":
                        # Health check
                        health_result = await handle_health_monitoring({"scope": "all", "detailed": False})
                        step_result["status"] = "completed"
                        step_result["health"] = json.loads(health_result[0].text)
                        
                    else:
                        step_result["status"] = "skipped"
                        step_result["reason"] = f"Step '{step}' not implemented"
                        
                except Exception as e:
                    step_result["status"] = "failed"
                    step_result["error"] = str(e)
            
            execution_results.append(step_result)
        
        result["execution_results"] = execution_results
        result["success"] = all(r["status"] in ["completed", "skipped", "skipped (dry run)"] for r in execution_results)
    
    result["timestamp"] = time.time()
    
    return [TextContent(
        type="text",
        text=json.dumps(result, indent=2)
    )]


async def main():
    """Main server entry point."""
    logger.info("Starting MCP Orchestrator Server...")
    logger.info("Tools available: 8")
    logger.info("MCP Protocol: v1.0")
    logger.info(f"Workspace: {orchestrator_server.workspace_root}")
    
    # Run server with stdio transport
    async with stdio_server() as (read_stream, write_stream):
        await orchestrator_server.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="orchestrator",
                server_version="1.0.0",
                capabilities={}
            )
        )


@click.command()
@click.option("--help-info", is_flag=True, help="Show this help message")
def cli(help_info):
    """MCP Orchestrator Server CLI."""
    if help_info:
        click.echo("MCP Orchestrator Server - Windows Docker Integration with Watchdog")
        click.echo("Usage: orchestrator")
        click.echo("Starts the MCP server for Docker orchestration and monitoring")
        return
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server shutdown by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server shutdown by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)