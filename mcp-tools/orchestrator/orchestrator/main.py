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

# Web API imports
try:
    from fastapi import FastAPI, WebSocket, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

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
    
    async def launch_docker(self) -> Tuple[bool, str]:
        """Launch Docker Desktop or Docker daemon based on platform."""
        try:
            if self.is_windows:
                # Windows: Start Docker Desktop
                return await self._launch_docker_windows()
            elif platform.system().lower() == "darwin":
                # macOS: Start Docker.app
                return await self._launch_docker_macos()
            else:
                # Linux: Start dockerd
                return await self._launch_docker_linux()
        except Exception as e:
            logger.error(f"Docker launch failed: {e}")
            return False, str(e)
    
    async def _launch_docker_windows(self) -> Tuple[bool, str]:
        """Launch Docker Desktop on Windows."""
        try:
            # Try to start Docker Desktop
            process = await asyncio.create_subprocess_exec(
                "powershell", "-Command", 
                "Start-Process 'C:\\Program Files\\Docker\\Docker\\Docker Desktop.exe'",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                # Wait a bit for Docker to start
                await asyncio.sleep(5)
                # Verify Docker is running
                if await self._check_docker_running():
                    return True, "Docker Desktop started successfully"
                else:
                    return True, "Docker Desktop launched, starting up..."
            else:
                return False, f"Failed to start Docker Desktop: {stderr.decode()}"
                
        except Exception as e:
            # Fallback: try alternative paths
            try:
                process = await asyncio.create_subprocess_exec(
                    "cmd", "/c", "start", "", "Docker Desktop",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                await process.communicate()
                return True, "Docker Desktop launch attempted via cmd"
            except Exception as e2:
                return False, f"Docker Desktop launch failed: {e}, {e2}"
    
    async def _launch_docker_macos(self) -> Tuple[bool, str]:
        """Launch Docker.app on macOS."""
        try:
            process = await asyncio.create_subprocess_exec(
                "open", "-a", "Docker",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                await asyncio.sleep(5)
                if await self._check_docker_running():
                    return True, "Docker.app started successfully"
                else:
                    return True, "Docker.app launched, starting up..."
            else:
                return False, f"Failed to start Docker.app: {stderr.decode()}"
                
        except Exception as e:
            return False, f"Docker.app launch failed: {e}"
    
    async def _launch_docker_linux(self) -> Tuple[bool, str]:
        """Launch Docker daemon on Linux."""
        try:
            # Try systemctl first
            process = await asyncio.create_subprocess_exec(
                "sudo", "systemctl", "start", "docker",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                await asyncio.sleep(3)
                if await self._check_docker_running():
                    return True, "Docker daemon started via systemctl"
                else:
                    return True, "Docker daemon start initiated"
            else:
                # Fallback: try service command
                process = await asyncio.create_subprocess_exec(
                    "sudo", "service", "docker", "start",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await process.communicate()
                
                if process.returncode == 0:
                    return True, "Docker daemon started via service"
                else:
                    return False, f"Failed to start Docker daemon: {stderr.decode()}"
                
        except Exception as e:
            return False, f"Docker daemon launch failed: {e}"
    
    async def _check_docker_running(self) -> bool:
        """Check if Docker is running."""
        try:
            if self.docker_client:
                self.docker_client.ping()
                return True
            return False
        except Exception:
            return False

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


class WebAPIOrchestrator:
    """FastAPI web interface for AI steering via React/JSON framework communication."""
    
    def __init__(self, orchestrator_server):
        self.orchestrator_server = orchestrator_server
        self.app = None
        self.active_connections = []
        
        if FASTAPI_AVAILABLE:
            self.app = FastAPI(
                title="MCP Orchestrator API",
                description="AI-steerable Docker orchestration API with React/JSON framework support",
                version="1.0.0"
            )
            self._setup_routes()
            self._setup_middleware()
        else:
            logger.warning("FastAPI not available - Web API disabled")
    
    def _setup_middleware(self):
        """Setup CORS and other middleware for React compatibility."""
        if not self.app:
            return
            
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure appropriately for production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def _setup_routes(self):
        """Setup API routes for AI steering."""
        if not self.app:
            return
        
        @self.app.get("/api/status")
        async def get_status():
            """Get overall orchestrator status."""
            return {
                "status": "running",
                "platform": platform.system(),
                "docker_available": DOCKER_AVAILABLE,
                "fastapi_available": FASTAPI_AVAILABLE,
                "watchdog_available": WATCHDOG_AVAILABLE,
                "timestamp": time.time()
            }
        
        @self.app.post("/api/docker/launch")
        async def launch_docker(payload: dict = None):
            """Launch Docker via API."""
            if payload is None:
                payload = {}
            
            result = await handle_docker_launch(payload)
            return json.loads(result[0].text)
        
        @self.app.post("/api/docker/operation")
        async def docker_operation(payload: dict):
            """Execute Docker operation via API."""
            result = await handle_docker_operation(payload)
            return json.loads(result[0].text)
        
        @self.app.post("/api/container/management")
        async def container_management(payload: dict):
            """Container management via API."""
            result = await handle_container_management(payload)
            return json.loads(result[0].text)
        
        @self.app.post("/api/environment/setup")
        async def environment_setup(payload: dict):
            """Environment setup via API."""
            result = await handle_environment_setup(payload)
            return json.loads(result[0].text)
        
        @self.app.post("/api/health/monitoring")
        async def health_monitoring(payload: dict):
            """Health monitoring via API."""
            result = await handle_health_monitoring(payload)
            return json.loads(result[0].text)
        
        @self.app.get("/api/platforms/detect")
        async def detect_platforms():
            """Detect available platforms and capabilities."""
            detection = {
                "current_platform": platform.system(),
                "architecture": platform.machine(),
                "python_version": platform.python_version(),
                "docker_available": DOCKER_AVAILABLE,
                "watchdog_available": WATCHDOG_AVAILABLE,
                "fastapi_available": FASTAPI_AVAILABLE
            }
            
            # Windows-specific detection
            if self.orchestrator_server.windows_docker.is_windows:
                detection["wsl"] = self.orchestrator_server.windows_docker.detect_wsl_environment()
                detection["docker_desktop"] = self.orchestrator_server.windows_docker.get_docker_desktop_status()
            
            return detection
        
        @self.app.websocket("/ws/updates")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket for real-time updates."""
            await websocket.accept()
            self.active_connections.append(websocket)
            
            try:
                while True:
                    # Send periodic status updates
                    status = {
                        "type": "status_update",
                        "timestamp": time.time(),
                        "docker_status": self.orchestrator_server.windows_docker.get_docker_desktop_status(),
                        "system_health": {
                            "cpu_percent": psutil.cpu_percent(),
                            "memory_percent": psutil.virtual_memory().percent
                        }
                    }
                    await websocket.send_json(status)
                    await asyncio.sleep(5)
                    
            except Exception as e:
                logger.debug(f"WebSocket connection closed: {e}")
            finally:
                if websocket in self.active_connections:
                    self.active_connections.remove(websocket)
        
        @self.app.post("/api/config/update")
        async def update_config(config: dict):
            """Update orchestrator configuration dynamically."""
            try:
                # Update environment variables
                for key, value in config.get("environment", {}).items():
                    os.environ[key] = str(value)
                
                # Update orchestrator settings
                settings = config.get("orchestrator", {})
                if "workspace_root" in settings:
                    new_root = Path(settings["workspace_root"])
                    if new_root.exists():
                        self.orchestrator_server.workspace_root = new_root
                
                return {
                    "success": True,
                    "message": "Configuration updated successfully",
                    "timestamp": time.time()
                }
                
            except Exception as e:
                return {
                    "success": False,
                    "message": f"Configuration update failed: {str(e)}",
                    "timestamp": time.time()
                }
    
    async def broadcast_update(self, message: dict):
        """Broadcast update to all connected WebSocket clients."""
        if not self.active_connections:
            return
            
        message["timestamp"] = time.time()
        disconnected = []
        
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(connection)
        
        # Remove disconnected connections
        for connection in disconnected:
            self.active_connections.remove(connection)
    
    async def start_server(self, host: str = "0.0.0.0", port: int = 8000):
        """Start the FastAPI web server."""
        if not FASTAPI_AVAILABLE or not self.app:
            logger.error("FastAPI not available - cannot start web server")
            return
        
        config = uvicorn.Config(
            app=self.app,
            host=host,
            port=port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()


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
            except Exception as e:
                logger.warning(f"Infrastructure initialization failed: {e}")
        
        # Initialize Web API for AI steering
        self.web_api = WebAPIOrchestrator(self)
        self.web_server_enabled = os.getenv("WEB_SERVER_ENABLED", "false").lower() == "true"
        self.web_server_host = os.getenv("WEB_SERVER_HOST", "0.0.0.0")
        self.web_server_port = int(os.getenv("WEB_SERVER_PORT", "8000"))
        
        # Enhanced platform resolution
        self.platform_info = self._detect_platform_capabilities()
        
        # Setup MCP tools
        self._setup_tools()
        
        # Ensure directories exist
        self.session_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Orchestrator initialized at {self.workspace_root}")
        logger.info(f"Session directory: {self.session_dir}")
    
    def _detect_platform_capabilities(self) -> Dict[str, Any]:
        """Enhanced cross-platform detection for Windows/Linux/WSL/Mac."""
        platform_info = {
            "system": platform.system(),
            "architecture": platform.machine(),
            "python_version": platform.python_version(),
            "hostname": platform.node(),
            "platform_release": platform.release(),
            "docker_available": DOCKER_AVAILABLE,
            "watchdog_available": WATCHDOG_AVAILABLE,
            "fastapi_available": FASTAPI_AVAILABLE,
            "capabilities": []
        }
        
        # Windows-specific detection
        if platform_info["system"] == "Windows":
            platform_info["capabilities"].extend(["windows_docker_desktop", "wsl_integration"])
            try:
                platform_info["wsl"] = self.windows_docker.detect_wsl_environment()
                platform_info["docker_desktop"] = self.windows_docker.get_docker_desktop_status()
            except Exception as e:
                logger.debug(f"Windows detection failed: {e}")
        
        # macOS-specific detection
        elif platform_info["system"] == "Darwin":
            platform_info["capabilities"].extend(["macos_docker_app", "homebrew_support"])
            try:
                # Check for Docker.app
                docker_app_path = Path("/Applications/Docker.app")
                platform_info["docker_app_available"] = docker_app_path.exists()
                
                # Check for Homebrew
                homebrew_path = Path("/opt/homebrew/bin/brew") or Path("/usr/local/bin/brew")
                platform_info["homebrew_available"] = homebrew_path.exists()
            except Exception as e:
                logger.debug(f"macOS detection failed: {e}")
        
        # Linux-specific detection
        else:
            platform_info["capabilities"].extend(["linux_docker_daemon", "systemctl_support"])
            try:
                # Check for systemctl
                result = subprocess.run(["which", "systemctl"], capture_output=True, timeout=5)
                platform_info["systemctl_available"] = result.returncode == 0
                
                # Check for Docker daemon
                result = subprocess.run(["which", "dockerd"], capture_output=True, timeout=5)
                platform_info["dockerd_available"] = result.returncode == 0
                
                # Check if running in WSL
                if Path("/proc/version").exists():
                    with open("/proc/version", "r") as f:
                        version_info = f.read().lower()
                        if "microsoft" in version_info or "wsl" in version_info:
                            platform_info["is_wsl"] = True
                            platform_info["capabilities"].append("wsl_environment")
            except Exception as e:
                logger.debug(f"Linux detection failed: {e}")
        
        return platform_info
    
    def _setup_tools(self):
        """Setup MCP tools with enhanced capabilities."""
        logger.info("Setting up MCP tools with enhanced Docker launch and platform resolution")
        logger.info(f"Platform capabilities: {self.platform_info.get('capabilities', [])}")


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
            name="docker_launch",
            description="Launch Docker Desktop or Docker daemon on Windows/Linux/WSL/Mac platforms",
            inputSchema={
                "type": "object",
                "properties": {
                    "platform": {
                        "type": "string",
                        "enum": ["auto", "windows", "linux", "macos", "wsl"],
                        "description": "Target platform (auto-detect if not specified)",
                        "default": "auto"
                    },
                    "wait_for_ready": {
                        "type": "boolean",
                        "description": "Wait for Docker to be fully ready before returning",
                        "default": True
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Timeout in seconds to wait for Docker to be ready",
                        "default": 60
                    }
                }
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
        elif name == "docker_launch":
            return await handle_docker_launch(arguments)
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


async def handle_docker_launch(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle Docker launch requests with cross-platform support."""
    platform_target = arguments.get("platform", "auto")
    wait_for_ready = arguments.get("wait_for_ready", True)
    timeout = arguments.get("timeout", 60)
    
    result = {
        "tool": "docker_launch",
        "platform_target": platform_target,
        "wait_for_ready": wait_for_ready,
        "timeout": timeout,
        "success": False,
        "message": "",
        "platform_detected": platform.system(),
        "docker_status": {}
    }
    
    try:
        # Determine target platform
        if platform_target == "auto":
            current_platform = platform.system().lower()
            if current_platform == "windows":
                platform_target = "windows"
            elif current_platform == "darwin":
                platform_target = "macos"
            else:
                platform_target = "linux"
        
        result["platform_resolved"] = platform_target
        
        # Check if Docker is already running
        initial_status = orchestrator_server.windows_docker.get_docker_desktop_status()
        result["initial_docker_status"] = initial_status
        
        if initial_status.get("running", False):
            result["success"] = True
            result["message"] = "Docker is already running"
            result["docker_status"] = initial_status
        else:
            # Launch Docker
            success, message = await orchestrator_server.windows_docker.launch_docker()
            result["success"] = success
            result["message"] = message
            
            # Wait for Docker to be ready if requested
            if success and wait_for_ready:
                start_time = time.time()
                ready = False
                
                while (time.time() - start_time) < timeout and not ready:
                    await asyncio.sleep(2)
                    try:
                        status = orchestrator_server.windows_docker.get_docker_desktop_status()
                        if status.get("running", False):
                            ready = True
                            result["docker_status"] = status
                            result["message"] = f"{message} - Docker is now ready"
                            break
                    except Exception as e:
                        logger.debug(f"Docker readiness check failed: {e}")
                
                if not ready:
                    result["message"] = f"{message} - Docker may still be starting up"
                    result["timeout_reached"] = True
    
    except Exception as e:
        result["success"] = False
        result["message"] = f"Docker launch failed: {str(e)}"
        result["error"] = str(e)
    
    result["timestamp"] = time.time()
    
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
    """Main server entry point with support for MCP and Web API modes."""
    logger.info("Starting MCP Orchestrator Server...")
    logger.info("Tools available: 9 (including docker_launch)")
    logger.info("MCP Protocol: v1.0")
    logger.info(f"Workspace: {orchestrator_server.workspace_root}")
    logger.info(f"Platform: {orchestrator_server.platform_info['system']}")
    logger.info(f"Capabilities: {orchestrator_server.platform_info.get('capabilities', [])}")
    
    # Check if web server should run alongside MCP
    if orchestrator_server.web_server_enabled:
        logger.info(f"Web API enabled at http://{orchestrator_server.web_server_host}:{orchestrator_server.web_server_port}")
        
        # Run both MCP server and Web API server concurrently
        async def run_mcp_server():
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
        
        async def run_web_server():
            await orchestrator_server.web_api.start_server(
                host=orchestrator_server.web_server_host,
                port=orchestrator_server.web_server_port
            )
        
        # Run both servers concurrently
        await asyncio.gather(
            run_mcp_server(),
            run_web_server()
        )
    else:
        # Run only MCP server with stdio transport
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
@click.option("--enable-web-api", is_flag=True, help="Enable FastAPI web interface for AI steering")
@click.option("--web-host", default="0.0.0.0", help="Web API host (default: 0.0.0.0)")
@click.option("--web-port", default=8000, type=int, help="Web API port (default: 8000)")
@click.option("--platform-info", is_flag=True, help="Show platform detection information")
def cli(help_info, enable_web_api, web_host, web_port, platform_info):
    """MCP Orchestrator Server CLI with enhanced Docker launch and AI steering capabilities."""
    if help_info:
        click.echo("MCP Orchestrator Server - Enhanced Docker Integration with AI Steering")
        click.echo("Usage: orchestrator [OPTIONS]")
        click.echo("\nFeatures:")
        click.echo("  • Docker Desktop/daemon launch capabilities")
        click.echo("  • AI steering via React/JSON framework communication")
        click.echo("  • Enhanced Windows/Linux/WSL/Mac platform resolution")
        click.echo("  • Real-time monitoring and configuration")
        click.echo("\nOptions:")
        click.echo("  --enable-web-api    Enable FastAPI web interface")
        click.echo("  --web-host HOST     Web API host (default: 0.0.0.0)")
        click.echo("  --web-port PORT     Web API port (default: 8000)")
        click.echo("  --platform-info     Show platform detection information")
        return
    
    if platform_info:
        click.echo("Platform Detection Information:")
        click.echo(json.dumps(orchestrator_server.platform_info, indent=2))
        return
    
    # Set web server options if specified
    if enable_web_api:
        os.environ["WEB_SERVER_ENABLED"] = "true"
        os.environ["WEB_SERVER_HOST"] = web_host
        os.environ["WEB_SERVER_PORT"] = str(web_port)
        orchestrator_server.web_server_enabled = True
        orchestrator_server.web_server_host = web_host
        orchestrator_server.web_server_port = web_port
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server shutdown by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    cli()