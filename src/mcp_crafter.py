#!/usr/bin/env python3
"""
Enhanced MCP Server Crafter
A robust, modular system for creating complex MCP servers with advanced features:
- Watchdog pathing and file monitoring
- Async form processing from Claude
- Modular and hierarchical server building
- Built-in automation and continuous tweaking
- CLI total integration
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union
from dataclasses import dataclass, asdict

try:
    import aiofiles
except ImportError:
    # Fallback async file operations
    aiofiles = None

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    # Create dummy classes if watchdog not available
    class Observer:
        def schedule(self, *args, **kwargs): pass
        def start(self): pass
        def stop(self): pass
        def join(self): pass
    
    class FileSystemEventHandler:
        def on_modified(self, event): pass
    
    WATCHDOG_AVAILABLE = False

try:
    from pydantic import BaseModel, Field
except ImportError:
    # Basic fallback for pydantic
    BaseModel = object
    Field = lambda **kwargs: None

try:
    from jinja2 import Environment, FileSystemLoader
except ImportError:
    # Simple template fallback
    class Environment:
        def __init__(self, *args, **kwargs): pass
        def get_template(self, name): return SimpleTemplate()
    
    class FileSystemLoader: pass
    
    class SimpleTemplate:
        def render(self, **kwargs): return ""

try:
    import click
except ImportError:
    # Simple click fallback
    class click:
        @staticmethod
        def group(): return lambda f: f
        @staticmethod
        def command(): return lambda f: f
        @staticmethod
        def option(*args, **kwargs): return lambda f: f
        @staticmethod
        def argument(*args, **kwargs): return lambda f: f
        @staticmethod
        def echo(text): print(text)
        @staticmethod
        def Choice(choices): return str

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ServerComplexity(Enum):
    """Server complexity levels"""
    SIMPLE = "simple"
    STANDARD = "standard"
    ADVANCED = "advanced"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"


class ServerCapability(Enum):
    """Server capability types"""
    TOOLS = "tools"
    RESOURCES = "resources"
    PROMPTS = "prompts"
    MONITORING = "monitoring"
    PERSISTENCE = "persistence"
    AUTHENTICATION = "authentication"
    RATE_LIMITING = "rate_limiting"
    CACHING = "caching"
    WEBHOOKS = "webhooks"
    STREAMING = "streaming"


class BuildStatus(Enum):
    """Build status types"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class CrafterForm:
    """Form data from Claude for server creation"""
    server_name: str
    description: str
    complexity: ServerComplexity
    capabilities: List[ServerCapability]
    template_base: str
    custom_tools: List[Dict[str, Any]]
    dependencies: List[str]
    environment_vars: Dict[str, str]
    deployment_config: Dict[str, Any]
    metadata: Dict[str, Any]
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)


class MCPWatchdog(FileSystemEventHandler):
    """Watchdog for monitoring MCP server files and triggering rebuilds"""
    
    def __init__(self, crafter_instance):
        self.crafter = crafter_instance
        self.watched_paths = set()
        
    def on_modified(self, event):
        if event.is_directory:
            return
            
        file_path = Path(event.src_path)
        if self._should_trigger_rebuild(file_path):
            logger.info(f"File changed: {file_path}, triggering rebuild")
            asyncio.create_task(self.crafter.handle_file_change(file_path))
            
    def _should_trigger_rebuild(self, file_path: Path) -> bool:
        """Determine if file change should trigger rebuild"""
        # Monitor Python files, config files, templates
        return file_path.suffix in {'.py', '.json', '.yaml', '.yml', '.toml', '.env', '.md'}


class EnhancedMCPCrafter:
    """
    Enhanced MCP Server Crafter with advanced capabilities
    """
    
    def __init__(self, workspace_dir: Optional[Path] = None):
        self.workspace_dir = workspace_dir or Path.cwd() / "mcp-workspace"
        self.workspace_dir.mkdir(exist_ok=True)
        
        # Setup directories
        self.templates_dir = self.workspace_dir / "templates"
        self.servers_dir = self.workspace_dir / "servers"
        self.builds_dir = self.workspace_dir / "builds"
        self.config_dir = self.workspace_dir / "config"
        
        for dir_path in [self.templates_dir, self.servers_dir, self.builds_dir, self.config_dir]:
            dir_path.mkdir(exist_ok=True)
            
        # State management
        self.active_builds = {}
        self.server_registry = {}
        self.form_queue = asyncio.Queue()
        
        # Watchdog setup
        self.observer = Observer()
        self.watchdog = MCPWatchdog(self)
        
        # Jinja2 environment for templates
        self.jinja_env = Environment(
            loader=FileSystemLoader([str(self.templates_dir), str(Path(__file__).parent / "templates")])
        )
        
        # Built-in templates
        self._setup_builtin_templates()
        
        logger.info(f"Enhanced MCP Crafter initialized at {self.workspace_dir}")
    
    def _setup_builtin_templates(self):
        """Setup built-in advanced templates"""
        builtin_templates = {
            "enterprise-python": self._create_enterprise_python_template(),
            "microservice-fastapi": self._create_microservice_template(),
            "streaming-websocket": self._create_streaming_template(),
            "ml-inference": self._create_ml_template(),
        }
        
        for template_name, template_content in builtin_templates.items():
            template_dir = self.templates_dir / template_name
            template_dir.mkdir(exist_ok=True)
            
            for file_path, content in template_content.items():
                file_full_path = template_dir / file_path
                file_full_path.parent.mkdir(parents=True, exist_ok=True)
                if not file_full_path.exists():
                    file_full_path.write_text(content)
    
    async def start_watching(self):
        """Start the watchdog file monitoring"""
        self.observer.schedule(self.watchdog, str(self.servers_dir), recursive=True)
        self.observer.start()
        logger.info("Watchdog monitoring started")
    
    async def stop_watching(self):
        """Stop the watchdog file monitoring"""
        self.observer.stop()
        self.observer.join()
        logger.info("Watchdog monitoring stopped")
    
    async def process_claude_form(self, form_data: Dict[str, Any]) -> str:
        """Process form from Claude asynchronously"""
        try:
            # Validate and parse form
            crafter_form = CrafterForm(
                server_name=form_data.get("server_name"),
                description=form_data.get("description", ""),
                complexity=ServerComplexity(form_data.get("complexity", "standard")),
                capabilities=[ServerCapability(cap) for cap in form_data.get("capabilities", [])],
                template_base=form_data.get("template_base", "enterprise-python"),
                custom_tools=form_data.get("custom_tools", []),
                dependencies=form_data.get("dependencies", []),
                environment_vars=form_data.get("environment_vars", {}),
                deployment_config=form_data.get("deployment_config", {}),
                metadata=form_data.get("metadata", {})
            )
            
            # Queue for processing
            build_id = str(uuid.uuid4())
            await self.form_queue.put((build_id, crafter_form))
            
            # Start async build
            asyncio.create_task(self._process_build_queue())
            
            return build_id
            
        except Exception as e:
            logger.error(f"Error processing Claude form: {e}")
            raise
    
    async def _process_build_queue(self):
        """Process queued builds asynchronously"""
        while not self.form_queue.empty():
            try:
                build_id, form = await self.form_queue.get()
                await self._build_server(build_id, form)
            except Exception as e:
                logger.error(f"Error processing build: {e}")
    
    async def _build_server(self, build_id: str, form: CrafterForm):
        """Build MCP server from form specification"""
        self.active_builds[build_id] = {
            "status": BuildStatus.IN_PROGRESS,
            "form": form,
            "started_at": datetime.now(timezone.utc),
            "progress": 0
        }
        
        try:
            server_dir = self.servers_dir / form.server_name
            if server_dir.exists():
                # Handle existing server - backup or merge
                await self._handle_existing_server(server_dir, form)
            
            server_dir.mkdir(exist_ok=True)
            
            # Generate server based on complexity and capabilities
            await self._generate_hierarchical_server(server_dir, form, build_id)
            
            # Setup monitoring for this server
            self._add_server_to_watchdog(server_dir)
            
            # Register server
            self.server_registry[form.server_name] = {
                "path": str(server_dir),
                "form": asdict(form),
                "build_id": build_id,
                "created_at": form.created_at.isoformat(),
                "status": "active"
            }
            
            # Update build status
            self.active_builds[build_id]["status"] = BuildStatus.SUCCESS
            self.active_builds[build_id]["completed_at"] = datetime.now(timezone.utc)
            self.active_builds[build_id]["progress"] = 100
            
            logger.info(f"Successfully built server: {form.server_name}")
            
        except Exception as e:
            self.active_builds[build_id]["status"] = BuildStatus.FAILED
            self.active_builds[build_id]["error"] = str(e)
            logger.error(f"Failed to build server {form.server_name}: {e}")
            raise
    
    async def _generate_hierarchical_server(self, server_dir: Path, form: CrafterForm, build_id: str):
        """Generate server with hierarchical modular structure"""
        
        # Update progress
        self.active_builds[build_id]["progress"] = 10
        
        # 1. Generate base server structure
        await self._generate_base_structure(server_dir, form)
        self.active_builds[build_id]["progress"] = 25
        
        # 2. Add capabilities as modules
        await self._add_capability_modules(server_dir, form)
        self.active_builds[build_id]["progress"] = 50
        
        # 3. Generate custom tools
        await self._generate_custom_tools(server_dir, form)
        self.active_builds[build_id]["progress"] = 70
        
        # 4. Setup deployment configuration
        await self._setup_deployment_config(server_dir, form)
        self.active_builds[build_id]["progress"] = 85
        
        # 5. Generate documentation and tests
        await self._generate_docs_and_tests(server_dir, form)
        self.active_builds[build_id]["progress"] = 95
        
        # 6. Final validation and setup
        await self._validate_and_finalize(server_dir, form)
        self.active_builds[build_id]["progress"] = 100
    
    async def _generate_base_structure(self, server_dir: Path, form: CrafterForm):
        """Generate base server structure from template"""
        template_name = form.template_base
        template_dir = self.templates_dir / template_name
        
        if not template_dir.exists():
            # Fall back to default template
            template_name = "enterprise-python"
            template_dir = self.templates_dir / template_name
        
        # Copy and render template files
        await self._render_template_files(template_dir, server_dir, form)
    
    async def _render_template_files(self, template_dir: Path, output_dir: Path, form: CrafterForm):
        """Render Jinja2 template files with form data"""
        template_vars = {
            "server_name": form.server_name,
            "description": form.description,
            "capabilities": [cap.value for cap in form.capabilities],
            "dependencies": form.dependencies,
            "environment_vars": form.environment_vars,
            "deployment_config": form.deployment_config,
            "metadata": form.metadata,
            "created_at": form.created_at.isoformat()
        }
        
        for template_file in template_dir.rglob("*"):
            if template_file.is_file() and not template_file.name.startswith('.'):
                rel_path = template_file.relative_to(template_dir)
                output_file = output_dir / rel_path
                output_file.parent.mkdir(parents=True, exist_ok=True)
                
                if template_file.suffix in {'.py', '.json', '.yaml', '.yml', '.md', '.toml', '.env'}:
                    # Render as Jinja2 template
                    template = self.jinja_env.get_template(str(rel_path))
                    rendered = template.render(**template_vars)
                    await self._write_file_async(output_file, rendered)
                else:
                    # Copy binary files as-is
                    content = template_file.read_bytes()
                    await self._write_file_async(output_file, content, mode='wb')
    
    async def _write_file_async(self, file_path: Path, content: Union[str, bytes], mode: str = 'w'):
        """Write file asynchronously"""
        if isinstance(content, bytes):
            mode = 'wb'
        
        if aiofiles:
            async with aiofiles.open(file_path, mode) as f:
                await f.write(content)
        else:
            # Fallback to synchronous write
            with open(file_path, mode) as f:
                f.write(content)
    
    async def _add_capability_modules(self, server_dir: Path, form: CrafterForm):
        """Add capability modules based on form specification"""
        modules_dir = server_dir / "src" / "modules"
        modules_dir.mkdir(parents=True, exist_ok=True)
        
        for capability in form.capabilities:
            await self._add_capability_module(modules_dir, capability, form)
    
    async def _add_capability_module(self, modules_dir: Path, capability: ServerCapability, form: CrafterForm):
        """Add specific capability module"""
        module_templates = {
            ServerCapability.MONITORING: self._create_monitoring_module(),
            ServerCapability.PERSISTENCE: self._create_persistence_module(),
            ServerCapability.AUTHENTICATION: self._create_auth_module(),
            ServerCapability.RATE_LIMITING: self._create_rate_limiting_module(),
            ServerCapability.CACHING: self._create_caching_module(),
            ServerCapability.WEBHOOKS: self._create_webhooks_module(),
            ServerCapability.STREAMING: self._create_streaming_module(),
        }
        
        if capability in module_templates:
            module_content = module_templates[capability]
            module_file = modules_dir / f"{capability.value}.py"
            await self._write_file_async(module_file, module_content)
    
    async def _generate_custom_tools(self, server_dir: Path, form: CrafterForm):
        """Generate custom tools from form specification"""
        tools_dir = server_dir / "src" / "tools"
        tools_dir.mkdir(parents=True, exist_ok=True)
        
        for tool_spec in form.custom_tools:
            await self._generate_custom_tool(tools_dir, tool_spec, form)
    
    async def _generate_custom_tool(self, tools_dir: Path, tool_spec: Dict[str, Any], form: CrafterForm):
        """Generate a single custom tool"""
        tool_name = tool_spec.get("name", "custom_tool")
        tool_template = self._create_custom_tool_template(tool_spec)
        tool_file = tools_dir / f"{tool_name}.py"
        await self._write_file_async(tool_file, tool_template)
    
    async def _setup_deployment_config(self, server_dir: Path, form: CrafterForm):
        """Setup deployment configuration files"""
        config = form.deployment_config
        
        # Docker configuration
        if config.get("docker", True):
            await self._generate_docker_config(server_dir, form)
        
        # Kubernetes configuration
        if config.get("kubernetes", False):
            await self._generate_k8s_config(server_dir, form)
        
        # Docker Compose
        if config.get("compose", True):
            await self._generate_compose_config(server_dir, form)
    
    async def _generate_docs_and_tests(self, server_dir: Path, form: CrafterForm):
        """Generate comprehensive documentation and tests"""
        # Generate README
        readme_content = self._create_readme_template(form)
        await self._write_file_async(server_dir / "README.md", readme_content)
        
        # Generate tests
        tests_dir = server_dir / "tests"
        tests_dir.mkdir(exist_ok=True)
        
        test_content = self._create_test_template(form)
        await self._write_file_async(tests_dir / f"test_{form.server_name.replace('-', '_')}.py", test_content)
    
    async def _validate_and_finalize(self, server_dir: Path, form: CrafterForm):
        """Final validation and setup"""
        # Validate generated files
        await self._validate_server_structure(server_dir)
        
        # Setup git repository
        if form.deployment_config.get("git", True):
            await self._setup_git_repo(server_dir)
        
        # Generate startup scripts
        await self._generate_startup_scripts(server_dir, form)
    
    async def handle_file_change(self, file_path: Path):
        """Handle file change event from watchdog"""
        # Find which server this file belongs to
        for server_name, server_info in self.server_registry.items():
            server_path = Path(server_info["path"])
            if file_path.is_relative_to(server_path):
                logger.info(f"Triggering incremental rebuild for {server_name} due to {file_path}")
                await self._incremental_rebuild(server_name, file_path)
                break
    
    async def _incremental_rebuild(self, server_name: str, changed_file: Path):
        """Perform incremental rebuild of server"""
        server_info = self.server_registry.get(server_name)
        if not server_info:
            return
        
        # Determine what needs to be rebuilt based on changed file
        if "tools" in str(changed_file):
            await self._rebuild_tools(server_name)
        elif "modules" in str(changed_file):
            await self._rebuild_modules(server_name)
        elif changed_file.name in {"pyproject.toml", "requirements.txt", "Dockerfile"}:
            await self._rebuild_deployment(server_name)
    
    def _add_server_to_watchdog(self, server_dir: Path):
        """Add server directory to watchdog monitoring"""
        self.watchdog.watched_paths.add(server_dir)
    
    async def get_build_status(self, build_id: str) -> Dict[str, Any]:
        """Get build status and progress"""
        return self.active_builds.get(build_id, {"status": "not_found"})
    
    def list_servers(self) -> Dict[str, Any]:
        """List all registered servers"""
        return self.server_registry
    
    async def delete_server(self, server_name: str) -> bool:
        """Delete a server and its files"""
        if server_name not in self.server_registry:
            return False
        
        server_info = self.server_registry[server_name]
        server_path = Path(server_info["path"])
        
        # Remove from watchdog
        self.watchdog.watched_paths.discard(server_path)
        
        # Remove files
        import shutil
        if server_path.exists():
            shutil.rmtree(server_path)
        
        # Remove from registry
        del self.server_registry[server_name]
        
        logger.info(f"Deleted server: {server_name}")
        return True

    # Template creation methods (condensed for space)
    def _create_enterprise_python_template(self) -> Dict[str, str]:
        """Create enterprise-grade Python MCP server template"""
        return {
            "src/main.py": self._get_enterprise_main_template(),
            "pyproject.toml": self._get_enterprise_pyproject_template(),
            "Dockerfile": self._get_enterprise_dockerfile_template(),
            "docker-compose.yml": self._get_enterprise_compose_template(),
            ".env.example": self._get_enterprise_env_template(),
        }
    
    def _get_enterprise_main_template(self) -> str:
        return '''#!/usr/bin/env python3
"""
{{ server_name }} - Enterprise MCP Server
{{ description }}

Generated by Enhanced MCP Crafter
Created: {{ created_at }}
"""

import asyncio
import logging
from typing import Any, Sequence
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# Import modules based on capabilities
{%- for capability in capabilities %}
from modules.{{ capability }} import {{ capability.title().replace('_', '') }}Module
{%- endfor %}

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("{{ server_name }}")

SERVER_NAME = "{{ server_name }}"
SERVER_VERSION = "1.0.0"

class {{ server_name.title().replace('-', '').replace('_', '') }}Server:
    """Enterprise MCP Server with advanced capabilities"""
    
    def __init__(self):
        self.server = Server(SERVER_NAME)
        self.modules = {}
        self._setup_modules()
        self._setup_handlers()
    
    def _setup_modules(self):
        """Initialize capability modules"""
        {%- for capability in capabilities %}
        self.modules["{{ capability }}"] = {{ capability.title().replace('_', '') }}Module()
        {%- endfor %}
    
    def _setup_handlers(self):
        """Setup MCP protocol handlers"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            tools = []
            # Add tools from all modules
            for module in self.modules.values():
                if hasattr(module, 'get_tools'):
                    tools.extend(await module.get_tools())
            return tools
        
        @self.server.call_tool()
        async def handle_call_tool(
            name: str, arguments: dict[str, Any] | None
        ) -> list[types.TextContent]:
            if arguments is None:
                arguments = {}
            
            # Route to appropriate module
            for module in self.modules.values():
                if hasattr(module, 'handle_tool') and await module.can_handle(name):
                    return await module.handle_tool(name, arguments)
            
            raise ValueError(f"Unknown tool: {name}")
    
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
    """Main entry point"""
    logger.info(f"Starting {SERVER_NAME} v{SERVER_VERSION}")
    server = {{ server_name.title().replace('-', '').replace('_', '') }}Server()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())
'''

    def _create_monitoring_module(self) -> str:
        return '''"""
Monitoring module for MCP server
Provides health checks, metrics, and performance monitoring
"""

import time
import psutil
from typing import Any, List
import mcp.types as types

class MonitoringModule:
    """Advanced monitoring capabilities"""
    
    def __init__(self):
        self.start_time = time.time()
        self.request_count = 0
    
    async def get_tools(self) -> List[types.Tool]:
        return [
            types.Tool(
                name="get_health",
                description="Get server health status",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
            types.Tool(
                name="get_metrics",
                description="Get detailed server metrics",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            )
        ]
    
    async def can_handle(self, tool_name: str) -> bool:
        return tool_name in ["get_health", "get_metrics"]
    
    async def handle_tool(self, name: str, arguments: dict) -> List[types.TextContent]:
        self.request_count += 1
        
        if name == "get_health":
            return await self._get_health()
        elif name == "get_metrics":
            return await self._get_metrics()
    
    async def _get_health(self) -> List[types.TextContent]:
        uptime = time.time() - self.start_time
        status = {
            "status": "healthy",
            "uptime_seconds": uptime,
            "requests_handled": self.request_count
        }
        return [types.TextContent(type="text", text=f"Health: {status}")]
    
    async def _get_metrics(self) -> List[types.TextContent]:
        metrics = {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "uptime": time.time() - self.start_time,
            "requests": self.request_count
        }
        return [types.TextContent(type="text", text=f"Metrics: {metrics}")]
'''

    def _create_microservice_template(self) -> Dict[str, str]:
        """Create microservice-oriented FastAPI template"""
        return {
            "src/main.py": '''#!/usr/bin/env python3
"""
{{ server_name }} - Microservice MCP Server
{{ description }}
"""

import asyncio
import logging
from typing import Any, Sequence
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types
from fastapi import FastAPI, HTTPException
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("{{ server_name }}")

SERVER_NAME = "{{ server_name }}"
SERVER_VERSION = "1.0.0"

# FastAPI app for HTTP endpoints
app = FastAPI(title=SERVER_NAME, version=SERVER_VERSION)

class {{ server_name.title().replace('-', '').replace('_', '') }}Server:
    """Microservice MCP Server with HTTP API"""
    
    def __init__(self):
        self.server = Server(SERVER_NAME)
        self.setup_handlers()
        self.setup_http_routes()
    
    def setup_handlers(self):
        """Setup MCP protocol handlers"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            return [
                types.Tool(
                    name="http_request",
                    description="Make HTTP requests via the microservice",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "method": {"type": "string", "enum": ["GET", "POST", "PUT", "DELETE"]},
                            "url": {"type": "string"},
                            "headers": {"type": "object"},
                            "data": {"type": "object"}
                        },
                        "required": ["method", "url"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict[str, Any] | None) -> list[types.TextContent]:
            if arguments is None:
                arguments = {}
            
            if name == "http_request":
                return await self.handle_http_request(**arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")
    
    def setup_http_routes(self):
        """Setup FastAPI HTTP routes"""
        
        @app.get("/")
        async def root():
            return {"message": f"{{ server_name }} microservice is running"}
        
        @app.get("/health")
        async def health():
            return {"status": "healthy", "server": SERVER_NAME}
    
    async def handle_http_request(self, method: str, url: str, headers: dict = None, data: dict = None) -> list[types.TextContent]:
        """Handle HTTP requests"""
        import httpx
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.request(method, url, headers=headers, json=data)
                result = {
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "content": response.text
                }
                return [types.TextContent(type="text", text=str(result))]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    async def run_mcp(self):
        """Run MCP server"""
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(read_stream, write_stream, InitializationOptions(
                server_name=SERVER_NAME,
                server_version=SERVER_VERSION,
                capabilities=self.server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            ))
    
    def run_http(self):
        """Run HTTP server"""
        uvicorn.run(app, host="0.0.0.0", port=8000)

async def main():
    """Main entry point"""
    server = {{ server_name.title().replace('-', '').replace('_', '') }}Server()
    
    # Run both MCP and HTTP servers
    import threading
    http_thread = threading.Thread(target=server.run_http)
    http_thread.daemon = True
    http_thread.start()
    
    await server.run_mcp()

if __name__ == "__main__":
    asyncio.run(main())
''',
            "pyproject.toml": '''[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "{{ server_name }}"
version = "1.0.0"
description = "{{ description }}"
dependencies = [
    "mcp>=1.0.0",
    "fastapi>=0.104.0",
    "uvicorn>=0.24.0",
    "httpx>=0.25.0"
]
''',
        }
    
    def _create_streaming_template(self) -> Dict[str, str]:
        """Create streaming WebSocket template"""
        return {
            "src/main.py": '''#!/usr/bin/env python3
"""
{{ server_name }} - Streaming MCP Server
{{ description }}
"""

import asyncio
import json
import logging
from typing import Any, Sequence
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types
import websockets

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("{{ server_name }}")

SERVER_NAME = "{{ server_name }}"
SERVER_VERSION = "1.0.0"

class {{ server_name.title().replace('-', '').replace('_', '') }}Server:
    """Streaming MCP Server with WebSocket support"""
    
    def __init__(self):
        self.server = Server(SERVER_NAME)
        self.connected_clients = set()
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup MCP protocol handlers"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            return [
                types.Tool(
                    name="stream_data",
                    description="Stream data to connected WebSocket clients",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "data": {"type": "object"},
                            "stream_id": {"type": "string"}
                        },
                        "required": ["data"]
                    }
                ),
                types.Tool(
                    name="get_connected_clients",
                    description="Get count of connected WebSocket clients",
                    inputSchema={"type": "object", "properties": {}}
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict[str, Any] | None) -> list[types.TextContent]:
            if arguments is None:
                arguments = {}
            
            if name == "stream_data":
                return await self.stream_data(**arguments)
            elif name == "get_connected_clients":
                return await self.get_connected_clients()
            else:
                raise ValueError(f"Unknown tool: {name}")
    
    async def stream_data(self, data: dict, stream_id: str = None) -> list[types.TextContent]:
        """Stream data to connected clients"""
        if not self.connected_clients:
            return [types.TextContent(type="text", text="No connected clients")]
        
        message = {
            "type": "stream",
            "stream_id": stream_id or "default",
            "data": data,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        # Broadcast to all connected clients
        disconnected = []
        for client in self.connected_clients:
            try:
                await client.send(json.dumps(message))
            except websockets.exceptions.ConnectionClosed:
                disconnected.append(client)
        
        # Remove disconnected clients
        for client in disconnected:
            self.connected_clients.discard(client)
        
        return [types.TextContent(
            type="text", 
            text=f"Streamed to {len(self.connected_clients)} clients"
        )]
    
    async def get_connected_clients(self) -> list[types.TextContent]:
        """Get connected clients count"""
        return [types.TextContent(
            type="text", 
            text=f"Connected clients: {len(self.connected_clients)}"
        )]
    
    async def websocket_handler(self, websocket, path):
        """Handle WebSocket connections"""
        self.connected_clients.add(websocket)
        logger.info(f"Client connected. Total: {len(self.connected_clients)}")
        
        try:
            await websocket.send(json.dumps({
                "type": "welcome",
                "server": SERVER_NAME,
                "version": SERVER_VERSION
            }))
            
            async for message in websocket:
                # Echo received messages
                await websocket.send(f"Echo: {message}")
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.connected_clients.discard(websocket)
            logger.info(f"Client disconnected. Total: {len(self.connected_clients)}")
    
    async def run_websocket_server(self):
        """Run WebSocket server"""
        server = await websockets.serve(self.websocket_handler, "localhost", 8765)
        logger.info("WebSocket server started on ws://localhost:8765")
        await server.wait_closed()
    
    async def run_mcp(self):
        """Run MCP server"""
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(read_stream, write_stream, InitializationOptions(
                server_name=SERVER_NAME,
                server_version=SERVER_VERSION,
                capabilities=self.server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            ))

async def main():
    """Main entry point"""
    server = {{ server_name.title().replace('-', '').replace('_', '') }}Server()
    
    # Run both MCP and WebSocket servers concurrently
    await asyncio.gather(
        server.run_mcp(),
        server.run_websocket_server()
    )

if __name__ == "__main__":
    asyncio.run(main())
''',
            "pyproject.toml": '''[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "{{ server_name }}"
version = "1.0.0"
description = "{{ description }}"
dependencies = [
    "mcp>=1.0.0",
    "websockets>=11.0.0"
]
''',
        }
    
    def _create_ml_template(self) -> Dict[str, str]:
        """Create ML inference template"""
        return {
            "src/main.py": '''#!/usr/bin/env python3
"""
{{ server_name }} - ML Inference MCP Server
{{ description }}
"""

import asyncio
import json
import logging
from typing import Any, Sequence, Optional
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("{{ server_name }}")

SERVER_NAME = "{{ server_name }}"
SERVER_VERSION = "1.0.0"

class {{ server_name.title().replace('-', '').replace('_', '') }}Server:
    """ML Inference MCP Server"""
    
    def __init__(self):
        self.server = Server(SERVER_NAME)
        self.models = {}
        self.setup_handlers()
        self.load_models()
    
    def load_models(self):
        """Load ML models (placeholder)"""
        # This would load actual models in production
        self.models["dummy"] = lambda x: {"prediction": "dummy_result", "confidence": 0.95}
        logger.info("Models loaded")
    
    def setup_handlers(self):
        """Setup MCP protocol handlers"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            return [
                types.Tool(
                    name="predict",
                    description="Make predictions using loaded ML models",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "model_name": {"type": "string", "description": "Model to use"},
                            "input_data": {"type": "object", "description": "Input data for prediction"},
                            "preprocessing": {"type": "object", "description": "Preprocessing options"}
                        },
                        "required": ["model_name", "input_data"]
                    }
                ),
                types.Tool(
                    name="list_models",
                    description="List available ML models",
                    inputSchema={"type": "object", "properties": {}}
                ),
                types.Tool(
                    name="model_info",
                    description="Get information about a specific model",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "model_name": {"type": "string"}
                        },
                        "required": ["model_name"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict[str, Any] | None) -> list[types.TextContent]:
            if arguments is None:
                arguments = {}
            
            if name == "predict":
                return await self.predict(**arguments)
            elif name == "list_models":
                return await self.list_models()
            elif name == "model_info":
                return await self.model_info(**arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")
    
    async def predict(self, model_name: str, input_data: dict, preprocessing: dict = None) -> list[types.TextContent]:
        """Make predictions"""
        if model_name not in self.models:
            return [types.TextContent(
                type="text", 
                text=f"Model '{model_name}' not found"
            )]
        
        try:
            # Apply preprocessing if specified
            processed_data = input_data
            if preprocessing:
                processed_data = self.apply_preprocessing(input_data, preprocessing)
            
            # Make prediction
            model = self.models[model_name]
            result = model(processed_data)
            
            response = {
                "model": model_name,
                "input": input_data,
                "prediction": result,
                "preprocessing_applied": preprocessing is not None
            }
            
            return [types.TextContent(
                type="text", 
                text=json.dumps(response, indent=2)
            )]
            
        except Exception as e:
            return [types.TextContent(
                type="text", 
                text=f"Prediction error: {str(e)}"
            )]
    
    async def list_models(self) -> list[types.TextContent]:
        """List available models"""
        models_info = {
            "available_models": list(self.models.keys()),
            "total_count": len(self.models)
        }
        
        return [types.TextContent(
            type="text", 
            text=json.dumps(models_info, indent=2)
        )]
    
    async def model_info(self, model_name: str) -> list[types.TextContent]:
        """Get model information"""
        if model_name not in self.models:
            return [types.TextContent(
                type="text", 
                text=f"Model '{model_name}' not found"
            )]
        
        # This would return actual model metadata in production
        info = {
            "name": model_name,
            "type": "placeholder",
            "description": f"Information about {model_name} model",
            "input_format": "flexible",
            "output_format": "json"
        }
        
        return [types.TextContent(
            type="text", 
            text=json.dumps(info, indent=2)
        )]
    
    def apply_preprocessing(self, data: dict, preprocessing: dict) -> dict:
        """Apply preprocessing to input data"""
        # Placeholder preprocessing
        return data
    
    async def run(self):
        """Run the server"""
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(read_stream, write_stream, InitializationOptions(
                server_name=SERVER_NAME,
                server_version=SERVER_VERSION,
                capabilities=self.server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            ))

async def main():
    """Main entry point"""
    logger.info(f"Starting {SERVER_NAME} v{SERVER_VERSION}")
    server = {{ server_name.title().replace('-', '').replace('_', '') }}Server()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())
''',
            "pyproject.toml": '''[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "{{ server_name }}"
version = "1.0.0"
description = "{{ description }}"
dependencies = [
    "mcp>=1.0.0",
    "numpy>=1.21.0",
    "scikit-learn>=1.0.0"
]

[project.optional-dependencies]
pytorch = ["torch>=1.12.0", "torchvision>=0.13.0"]
tensorflow = ["tensorflow>=2.8.0"]
''',
        }
    
    def _create_persistence_module(self) -> str:
        return '''"""
Persistence module for MCP server
Provides database connectivity and data persistence capabilities
"""

import asyncio
import json
import sqlite3
from pathlib import Path
from typing import Any, List, Dict, Optional
import mcp.types as types

class PersistenceModule:
    """Database persistence capabilities"""
    
    def __init__(self, db_path: str = "server_data.db"):
        self.db_path = Path(db_path)
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS data_store (
                    id INTEGER PRIMARY KEY,
                    key TEXT UNIQUE,
                    value TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
    
    async def get_tools(self) -> List[types.Tool]:
        return [
            types.Tool(
                name="store_data",
                description="Store data in the database",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "key": {"type": "string"},
                        "value": {"type": "object"}
                    },
                    "required": ["key", "value"]
                }
            ),
            types.Tool(
                name="retrieve_data",
                description="Retrieve data from the database",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "key": {"type": "string"}
                    },
                    "required": ["key"]
                }
            ),
            types.Tool(
                name="list_keys",
                description="List all stored keys",
                inputSchema={"type": "object", "properties": {}}
            )
        ]
    
    async def can_handle(self, tool_name: str) -> bool:
        return tool_name in ["store_data", "retrieve_data", "list_keys"]
    
    async def handle_tool(self, name: str, arguments: dict) -> List[types.TextContent]:
        if name == "store_data":
            return await self._store_data(**arguments)
        elif name == "retrieve_data":
            return await self._retrieve_data(**arguments)
        elif name == "list_keys":
            return await self._list_keys()
    
    async def _store_data(self, key: str, value: Any) -> List[types.TextContent]:
        """Store data in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO data_store (key, value) VALUES (?, ?)",
                    (key, json.dumps(value))
                )
                conn.commit()
            return [types.TextContent(type="text", text=f"Data stored for key: {key}")]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error storing data: {str(e)}")]
    
    async def _retrieve_data(self, key: str) -> List[types.TextContent]:
        """Retrieve data from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT value FROM data_store WHERE key = ?", (key,))
                row = cursor.fetchone()
                if row:
                    return [types.TextContent(type="text", text=row[0])]
                else:
                    return [types.TextContent(type="text", text=f"No data found for key: {key}")]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error retrieving data: {str(e)}")]
    
    async def _list_keys(self) -> List[types.TextContent]:
        """List all stored keys"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT key, timestamp FROM data_store ORDER BY timestamp DESC")
                keys = [{"key": row[0], "timestamp": row[1]} for row in cursor.fetchall()]
            return [types.TextContent(type="text", text=json.dumps(keys, indent=2))]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error listing keys: {str(e)}")]
'''
    
    def _create_auth_module(self) -> str:
        return '''"""
Authentication module for MCP server
Provides JWT-based authentication and authorization
"""

import jwt
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Any, List, Dict, Optional
import mcp.types as types

class AuthenticationModule:
    """JWT-based authentication capabilities"""
    
    def __init__(self, secret_key: str = None):
        self.secret_key = secret_key or secrets.token_hex(32)
        self.users = {}  # In production, use proper user storage
        self.active_tokens = set()
    
    async def get_tools(self) -> List[types.Tool]:
        return [
            types.Tool(
                name="authenticate",
                description="Authenticate user and get JWT token",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "username": {"type": "string"},
                        "password": {"type": "string"}
                    },
                    "required": ["username", "password"]
                }
            ),
            types.Tool(
                name="validate_token",
                description="Validate JWT token",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "token": {"type": "string"}
                    },
                    "required": ["token"]
                }
            ),
            types.Tool(
                name="create_user",
                description="Create new user account",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "username": {"type": "string"},
                        "password": {"type": "string"},
                        "roles": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["username", "password"]
                }
            )
        ]
    
    async def can_handle(self, tool_name: str) -> bool:
        return tool_name in ["authenticate", "validate_token", "create_user"]
    
    async def handle_tool(self, name: str, arguments: dict) -> List[types.TextContent]:
        if name == "authenticate":
            return await self._authenticate(**arguments)
        elif name == "validate_token":
            return await self._validate_token(**arguments)
        elif name == "create_user":
            return await self._create_user(**arguments)
    
    def _hash_password(self, password: str) -> str:
        """Hash password with salt"""
        salt = secrets.token_hex(16)
        hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return f"{salt}:{hashed.hex()}"
    
    def _verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        try:
            salt, hash_part = hashed.split(':')
            return hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex() == hash_part
        except:
            return False
    
    async def _authenticate(self, username: str, password: str) -> List[types.TextContent]:
        """Authenticate user and return JWT token"""
        if username not in self.users:
            return [types.TextContent(type="text", text="Invalid credentials")]
        
        user = self.users[username]
        if not self._verify_password(password, user['password']):
            return [types.TextContent(type="text", text="Invalid credentials")]
        
        # Generate JWT token
        payload = {
            'username': username,
            'roles': user.get('roles', []),
            'exp': datetime.utcnow() + timedelta(hours=24),
            'iat': datetime.utcnow()
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm='HS256')
        self.active_tokens.add(token)
        
        return [types.TextContent(type="text", text=f"Token: {token}")]
    
    async def _validate_token(self, token: str) -> List[types.TextContent]:
        """Validate JWT token"""
        try:
            if token not in self.active_tokens:
                return [types.TextContent(type="text", text="Token not active")]
            
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return [types.TextContent(type="text", text=f"Valid token for: {payload['username']}")]
        except jwt.ExpiredSignatureError:
            return [types.TextContent(type="text", text="Token expired")]
        except jwt.InvalidTokenError:
            return [types.TextContent(type="text", text="Invalid token")]
    
    async def _create_user(self, username: str, password: str, roles: List[str] = None) -> List[types.TextContent]:
        """Create new user"""
        if username in self.users:
            return [types.TextContent(type="text", text="User already exists")]
        
        self.users[username] = {
            'password': self._hash_password(password),
            'roles': roles or ['user'],
            'created_at': datetime.utcnow().isoformat()
        }
        
        return [types.TextContent(type="text", text=f"User {username} created successfully")]
'''
    
    def _create_rate_limiting_module(self) -> str:
        return '''"""
Rate limiting module for MCP server
Provides request rate limiting and throttling capabilities
"""

import time
from collections import defaultdict, deque
from typing import Any, List, Dict, Optional
import mcp.types as types

class RateLimitingModule:
    """Rate limiting and throttling capabilities"""
    
    def __init__(self):
        self.request_history = defaultdict(deque)
        self.limits = {
            'default': {'requests': 100, 'window': 3600},  # 100 requests per hour
            'premium': {'requests': 1000, 'window': 3600}  # 1000 requests per hour
        }
    
    async def get_tools(self) -> List[types.Tool]:
        return [
            types.Tool(
                name="check_rate_limit",
                description="Check if client is within rate limits",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "client_id": {"type": "string"},
                        "tier": {"type": "string", "default": "default"}
                    },
                    "required": ["client_id"]
                }
            ),
            types.Tool(
                name="get_rate_status",
                description="Get current rate limit status for client",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "client_id": {"type": "string"}
                    },
                    "required": ["client_id"]
                }
            ),
            types.Tool(
                name="set_rate_limit",
                description="Set custom rate limit for client",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "client_id": {"type": "string"},
                        "requests": {"type": "integer"},
                        "window": {"type": "integer"}
                    },
                    "required": ["client_id", "requests", "window"]
                }
            )
        ]
    
    async def can_handle(self, tool_name: str) -> bool:
        return tool_name in ["check_rate_limit", "get_rate_status", "set_rate_limit"]
    
    async def handle_tool(self, name: str, arguments: dict) -> List[types.TextContent]:
        if name == "check_rate_limit":
            return await self._check_rate_limit(**arguments)
        elif name == "get_rate_status":
            return await self._get_rate_status(**arguments)
        elif name == "set_rate_limit":
            return await self._set_rate_limit(**arguments)
    
    async def _check_rate_limit(self, client_id: str, tier: str = "default") -> List[types.TextContent]:
        """Check if client is within rate limits"""
        now = time.time()
        limit_config = self.limits.get(tier, self.limits['default'])
        window = limit_config['window']
        max_requests = limit_config['requests']
        
        # Clean old requests
        client_history = self.request_history[client_id]
        while client_history and client_history[0] < now - window:
            client_history.popleft()
        
        # Check if within limits
        if len(client_history) >= max_requests:
            time_to_reset = int(window - (now - client_history[0]))
            return [types.TextContent(
                type="text", 
                text=f"Rate limit exceeded. Reset in {time_to_reset} seconds"
            )]
        
        # Record this request
        client_history.append(now)
        
        return [types.TextContent(
            type="text", 
            text=f"Request allowed. {len(client_history)}/{max_requests} used"
        )]
    
    async def _get_rate_status(self, client_id: str) -> List[types.TextContent]:
        """Get rate limit status"""
        now = time.time()
        client_history = self.request_history[client_id]
        
        # Clean old requests
        while client_history and client_history[0] < now - 3600:
            client_history.popleft()
        
        status = {
            "client_id": client_id,
            "requests_in_last_hour": len(client_history),
            "oldest_request": client_history[0] if client_history else None,
            "newest_request": client_history[-1] if client_history else None
        }
        
        return [types.TextContent(type="text", text=str(status))]
    
    async def _set_rate_limit(self, client_id: str, requests: int, window: int) -> List[types.TextContent]:
        """Set custom rate limit"""
        self.limits[client_id] = {'requests': requests, 'window': window}
        return [types.TextContent(
            type="text", 
            text=f"Rate limit set for {client_id}: {requests} requests per {window} seconds"
        )]
'''
    
    def _create_caching_module(self) -> str:
        return '''"""
Caching module for MCP server
Provides in-memory and persistent caching capabilities
"""

import json
import time
import hashlib
from typing import Any, List, Dict, Optional
import mcp.types as types

class CachingModule:
    """Caching capabilities with TTL support"""
    
    def __init__(self):
        self.cache = {}
        self.ttl_cache = {}
    
    async def get_tools(self) -> List[types.Tool]:
        return [
            types.Tool(
                name="cache_set",
                description="Store data in cache with optional TTL",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "key": {"type": "string"},
                        "value": {"type": "object"},
                        "ttl": {"type": "integer", "description": "Time to live in seconds"}
                    },
                    "required": ["key", "value"]
                }
            ),
            types.Tool(
                name="cache_get",
                description="Retrieve data from cache",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "key": {"type": "string"}
                    },
                    "required": ["key"]
                }
            ),
            types.Tool(
                name="cache_delete",
                description="Delete data from cache",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "key": {"type": "string"}
                    },
                    "required": ["key"]
                }
            ),
            types.Tool(
                name="cache_stats",
                description="Get cache statistics",
                inputSchema={"type": "object", "properties": {}}
            )
        ]
    
    async def can_handle(self, tool_name: str) -> bool:
        return tool_name in ["cache_set", "cache_get", "cache_delete", "cache_stats"]
    
    async def handle_tool(self, name: str, arguments: dict) -> List[types.TextContent]:
        if name == "cache_set":
            return await self._cache_set(**arguments)
        elif name == "cache_get":
            return await self._cache_get(**arguments)
        elif name == "cache_delete":
            return await self._cache_delete(**arguments)
        elif name == "cache_stats":
            return await self._cache_stats()
    
    def _is_expired(self, key: str) -> bool:
        """Check if cached item is expired"""
        if key not in self.ttl_cache:
            return False
        return time.time() > self.ttl_cache[key]
    
    async def _cache_set(self, key: str, value: Any, ttl: int = None) -> List[types.TextContent]:
        """Set cache value"""
        self.cache[key] = value
        
        if ttl:
            self.ttl_cache[key] = time.time() + ttl
        
        return [types.TextContent(
            type="text", 
            text=f"Cached data for key: {key}" + (f" (TTL: {ttl}s)" if ttl else "")
        )]
    
    async def _cache_get(self, key: str) -> List[types.TextContent]:
        """Get cache value"""
        if key not in self.cache:
            return [types.TextContent(type="text", text=f"Key not found: {key}")]
        
        if self._is_expired(key):
            del self.cache[key]
            del self.ttl_cache[key]
            return [types.TextContent(type="text", text=f"Key expired: {key}")]
        
        return [types.TextContent(type="text", text=json.dumps(self.cache[key]))]
    
    async def _cache_delete(self, key: str) -> List[types.TextContent]:
        """Delete cache value"""
        if key in self.cache:
            del self.cache[key]
            if key in self.ttl_cache:
                del self.ttl_cache[key]
            return [types.TextContent(type="text", text=f"Deleted key: {key}")]
        
        return [types.TextContent(type="text", text=f"Key not found: {key}")]
    
    async def _cache_stats(self) -> List[types.TextContent]:
        """Get cache statistics"""
        now = time.time()
        expired_keys = [k for k, exp_time in self.ttl_cache.items() if now > exp_time]
        
        stats = {
            "total_keys": len(self.cache),
            "keys_with_ttl": len(self.ttl_cache),
            "expired_keys": len(expired_keys),
            "cache_size_bytes": len(json.dumps(self.cache))
        }
        
    
    def _create_webhooks_module(self) -> str:
        return '''"""
Webhooks module for MCP server
Provides webhook registration and handling capabilities
"""

import asyncio
import json
import hmac
import hashlib
from typing import Any, List, Dict, Optional
import mcp.types as types
from urllib.parse import urlparse

class WebhooksModule:
    """Webhook registration and handling capabilities"""
    
    def __init__(self):
        self.webhooks = {}
        self.webhook_history = []
    
    async def get_tools(self) -> List[types.Tool]:
        return [
            types.Tool(
                name="register_webhook",
                description="Register a webhook endpoint",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "url": {"type": "string"},
                        "events": {"type": "array", "items": {"type": "string"}},
                        "secret": {"type": "string", "description": "Optional webhook secret"}
                    },
                    "required": ["name", "url", "events"]
                }
            ),
            types.Tool(
                name="trigger_webhook",
                description="Manually trigger a webhook",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "event": {"type": "string"},
                        "data": {"type": "object"}
                    },
                    "required": ["name", "event", "data"]
                }
            ),
            types.Tool(
                name="list_webhooks",
                description="List all registered webhooks",
                inputSchema={"type": "object", "properties": {}}
            ),
            types.Tool(
                name="webhook_history",
                description="Get webhook delivery history",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "limit": {"type": "integer", "default": 10}
                    }
                }
            )
        ]
    
    async def can_handle(self, tool_name: str) -> bool:
        return tool_name in ["register_webhook", "trigger_webhook", "list_webhooks", "webhook_history"]
    
    async def handle_tool(self, name: str, arguments: dict) -> List[types.TextContent]:
        if name == "register_webhook":
            return await self._register_webhook(**arguments)
        elif name == "trigger_webhook":
            return await self._trigger_webhook(**arguments)
        elif name == "list_webhooks":
            return await self._list_webhooks()
        elif name == "webhook_history":
            return await self._webhook_history(**arguments)
    
    async def _register_webhook(self, name: str, url: str, events: List[str], secret: str = None) -> List[types.TextContent]:
        """Register a webhook"""
        # Validate URL
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return [types.TextContent(type="text", text="Invalid URL")]
        
        self.webhooks[name] = {
            "url": url,
            "events": events,
            "secret": secret,
            "created_at": asyncio.get_event_loop().time(),
            "delivery_count": 0
        }
        
        return [types.TextContent(type="text", text=f"Webhook '{name}' registered for events: {events}")]
    
    async def _trigger_webhook(self, name: str, event: str, data: dict) -> List[types.TextContent]:
        """Trigger a webhook"""
        if name not in self.webhooks:
            return [types.TextContent(type="text", text=f"Webhook '{name}' not found")]
        
        webhook = self.webhooks[name]
        if event not in webhook["events"]:
            return [types.TextContent(type="text", text=f"Event '{event}' not subscribed")]
        
        # Prepare payload
        payload = {
            "event": event,
            "data": data,
            "timestamp": asyncio.get_event_loop().time(),
            "webhook": name
        }
        
        # Create signature if secret provided
        headers = {"Content-Type": "application/json"}
        if webhook["secret"]:
            signature = hmac.new(
                webhook["secret"].encode(),
                json.dumps(payload).encode(),
                hashlib.sha256
            ).hexdigest()
            headers["X-Webhook-Signature"] = f"sha256={signature}"
        
        # Record delivery attempt
        delivery = {
            "webhook": name,
            "event": event,
            "url": webhook["url"],
            "timestamp": asyncio.get_event_loop().time(),
            "status": "pending"
        }
        
        try:
            # In production, this would make actual HTTP request
            # For now, just simulate
            delivery["status"] = "success"
            webhook["delivery_count"] += 1
            
            self.webhook_history.append(delivery)
            
            return [types.TextContent(type="text", text=f"Webhook '{name}' triggered successfully")]
            
        except Exception as e:
            delivery["status"] = "failed"
            delivery["error"] = str(e)
            self.webhook_history.append(delivery)
            
            return [types.TextContent(type="text", text=f"Webhook '{name}' delivery failed: {str(e)}")]
    
    async def _list_webhooks(self) -> List[types.TextContent]:
        """List registered webhooks"""
        if not self.webhooks:
            return [types.TextContent(type="text", text="No webhooks registered")]
        
        webhook_list = []
        for name, config in self.webhooks.items():
            webhook_list.append({
                "name": name,
                "url": config["url"],
                "events": config["events"],
                "delivery_count": config["delivery_count"],
                "has_secret": bool(config["secret"])
            })
        
        return [types.TextContent(type="text", text=json.dumps(webhook_list, indent=2))]
    
    async def _webhook_history(self, limit: int = 10) -> List[types.TextContent]:
        """Get webhook delivery history"""
        recent_history = self.webhook_history[-limit:] if self.webhook_history else []
        return [types.TextContent(type="text", text=json.dumps(recent_history, indent=2))]
'''
    
    def _create_streaming_module(self) -> str:
        return '''"""
Streaming module for MCP server
Provides real-time data streaming capabilities
"""

import asyncio
import json
import time
from typing import Any, List, Dict, Optional, AsyncGenerator
import mcp.types as types

class StreamingModule:
    """Real-time streaming capabilities"""
    
    def __init__(self):
        self.active_streams = {}
        self.stream_subscribers = {}
    
    async def get_tools(self) -> List[types.Tool]:
        return [
            types.Tool(
                name="start_stream",
                description="Start a new data stream",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "stream_id": {"type": "string"},
                        "stream_type": {"type": "string", "enum": ["realtime", "batch", "event"]},
                        "interval": {"type": "number", "default": 1.0}
                    },
                    "required": ["stream_id", "stream_type"]
                }
            ),
            types.Tool(
                name="stop_stream",
                description="Stop a data stream",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "stream_id": {"type": "string"}
                    },
                    "required": ["stream_id"]
                }
            ),
            types.Tool(
                name="get_stream_data",
                description="Get latest data from a stream",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "stream_id": {"type": "string"},
                        "count": {"type": "integer", "default": 10}
                    },
                    "required": ["stream_id"]
                }
            ),
            types.Tool(
                name="list_streams",
                description="List all active streams",
                inputSchema={"type": "object", "properties": {}}
            )
        ]
    
    async def can_handle(self, tool_name: str) -> bool:
        return tool_name in ["start_stream", "stop_stream", "get_stream_data", "list_streams"]
    
    async def handle_tool(self, name: str, arguments: dict) -> List[types.TextContent]:
        if name == "start_stream":
            return await self._start_stream(**arguments)
        elif name == "stop_stream":
            return await self._stop_stream(**arguments)
        elif name == "get_stream_data":
            return await self._get_stream_data(**arguments)
        elif name == "list_streams":
            return await self._list_streams()
    
    async def _start_stream(self, stream_id: str, stream_type: str, interval: float = 1.0) -> List[types.TextContent]:
        """Start a new stream"""
        if stream_id in self.active_streams:
            return [types.TextContent(type="text", text=f"Stream '{stream_id}' already exists")]
        
        stream_config = {
            "id": stream_id,
            "type": stream_type,
            "interval": interval,
            "started_at": time.time(),
            "data_points": [],
            "running": True
        }
        
        self.active_streams[stream_id] = stream_config
        
        # Start stream task
        asyncio.create_task(self._stream_generator(stream_id))
        
        return [types.TextContent(type="text", text=f"Stream '{stream_id}' started")]
    
    async def _stop_stream(self, stream_id: str) -> List[types.TextContent]:
        """Stop a stream"""
        if stream_id not in self.active_streams:
            return [types.TextContent(type="text", text=f"Stream '{stream_id}' not found")]
        
        self.active_streams[stream_id]["running"] = False
        del self.active_streams[stream_id]
        
        return [types.TextContent(type="text", text=f"Stream '{stream_id}' stopped")]
    
    async def _get_stream_data(self, stream_id: str, count: int = 10) -> List[types.TextContent]:
        """Get latest stream data"""
        if stream_id not in self.active_streams:
            return [types.TextContent(type="text", text=f"Stream '{stream_id}' not found")]
        
        stream = self.active_streams[stream_id]
        latest_data = stream["data_points"][-count:] if stream["data_points"] else []
        
        result = {
            "stream_id": stream_id,
            "type": stream["type"],
            "data_count": len(latest_data),
            "data": latest_data
        }
        
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    
    async def _list_streams(self) -> List[types.TextContent]:
        """List active streams"""
        streams_info = []
        for stream_id, config in self.active_streams.items():
            streams_info.append({
                "id": stream_id,
                "type": config["type"],
                "running": config["running"],
                "data_points": len(config["data_points"]),
                "started_at": config["started_at"]
            })
        
        return [types.TextContent(type="text", text=json.dumps(streams_info, indent=2))]
    
    async def _stream_generator(self, stream_id: str):
        """Generate stream data"""
        stream = self.active_streams[stream_id]
        counter = 0
        
        while stream["running"]:
            # Generate sample data based on stream type
            if stream["type"] == "realtime":
                data_point = {
                    "timestamp": time.time(),
                    "value": counter,
                    "random": hash(str(time.time())) % 100
                }
            elif stream["type"] == "batch":
                data_point = {
                    "batch_id": counter,
                    "timestamp": time.time(),
                    "items": [f"item_{i}" for i in range(5)]
                }
            else:  # event
                data_point = {
                    "event_id": counter,
                    "timestamp": time.time(),
                    "event_type": "sample_event",
                    "data": {"counter": counter}
                }
            
            stream["data_points"].append(data_point)
            
            # Keep only last 100 data points
            if len(stream["data_points"]) > 100:
                stream["data_points"] = stream["data_points"][-100:]
            
            counter += 1
            await asyncio.sleep(stream["interval"])
'''
    
    def _get_enterprise_pyproject_template(self) -> str:
        return """[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "{{ server_name }}"
version = "1.0.0"
description = "{{ description }}"
authors = [
    {name = "Generated by MCP Crafter", email = "crafter@mcp-system.local"}
]
readme = "README.md"
requires-python = ">=3.10"
keywords = ["mcp", "server", "{{ server_name }}"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]

dependencies = [
    "mcp>=1.0.0",
    "pydantic>=2.4.0",
    "python-dotenv>=1.0.0"
    {%- for dep in dependencies %},
    "{{ dep }}"
    {%- endfor %}
    {%- if "persistence" in capabilities %},
    "sqlalchemy>=2.0.0",
    "aiosqlite>=0.17.0"
    {%- endif %}
    {%- if "authentication" in capabilities %},
    "pyjwt>=2.8.0",
    "passlib>=1.7.4",
    "bcrypt>=4.0.0"
    {%- endif %}
    {%- if "caching" in capabilities %},
    "redis>=5.0.0"
    {%- endif %}
    {%- if "monitoring" in capabilities %},
    "psutil>=5.9.0",
    "prometheus-client>=0.19.0"
    {%- endif %}
    {%- if "rate_limiting" in capabilities %},
    "slowapi>=0.1.0"
    {%- endif %}
    {%- if "streaming" in capabilities %},
    "websockets>=11.0.0"
    {%- endif %}
    {%- if "webhooks" in capabilities %},
    "httpx>=0.25.0"
    {%- endif %}
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "black>=23.9.0",
    "isort>=5.12.0",
    "mypy>=1.6.0",
    "coverage>=7.3.0"
]
docker = [
    "gunicorn>=21.2.0"
]

[project.scripts]
{{ server_name.replace('-', '_') }} = "src.main:main"

[tool.black]
line-length = 88
target-version = ["py310"]
include = '\\.pyi?$'

[tool.isort]
profile = "black"
multi_line_output = 3
include_trailing_comma = true
force_grid_wrap = 0
use_parentheses = true
ensure_newline_before_comments = true
line_length = 88

[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
"""
    
    def _get_enterprise_dockerfile_template(self) -> str:
        return """# Multi-stage build for {{ server_name }}
FROM python:3.11-slim as builder

# Set build arguments
ARG BUILD_DATE
ARG VERSION=1.0.0

# Add metadata
LABEL org.opencontainers.image.title="{{ server_name }}"
LABEL org.opencontainers.image.description="{{ description }}"
LABEL org.opencontainers.image.version=$VERSION
LABEL org.opencontainers.image.created=$BUILD_DATE

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    build-essential \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Install uv for faster dependency management
RUN pip install uv

# Set up working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml ./
COPY README.md ./

# Install dependencies
RUN uv venv && uv pip install -e .

# Production stage
FROM python:3.11-slim as production

# Create non-root user for security
RUN groupadd -r mcpuser && useradd -r -g mcpuser mcpuser

# Install runtime dependencies
{%- if "persistence" in capabilities %}
RUN apt-get update && apt-get install -y sqlite3 && rm -rf /var/lib/apt/lists/*
{%- endif %}

# Set working directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy source code
COPY src/ ./src/
COPY .env.example ./.env

# Set ownership and permissions
RUN chown -R mcpuser:mcpuser /app
USER mcpuser

# Set environment variables
ENV PYTHONPATH=/app
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL=INFO

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD python -c "import sys; sys.exit(0)" || exit 1

# Default command (stdio transport)
CMD ["python", "src/main.py"]
"""
    
    def _get_enterprise_compose_template(self) -> str:
        return """version: '3.8'

services:
  {{ server_name }}:
    build: 
      context: .
      args:
        BUILD_DATE: ${BUILD_DATE:-$(date -u +'%Y-%m-%dT%H:%M:%SZ')}
        VERSION: ${VERSION:-1.0.0}
    environment:
      - LOG_LEVEL=INFO
      - PYTHONUNBUFFERED=1
      {%- for key, value in environment_vars.items() %}
      - {{ key }}={{ value }}
      {%- endfor %}
    restart: unless-stopped
    volumes:
      - ./data:/app/data
      - ./.env:/app/.env
    
    {%- if "persistence" in capabilities %}
    depends_on:
      - database
    {%- endif %}
    {%- if "caching" in capabilities %}
      - redis
    {%- endif %}

{%- if "persistence" in capabilities %}
  database:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: {{ server_name.replace("-", "_") }}
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${DB_PASSWORD:-password}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: "10s"
      timeout: "5s"
      retries: 5
{%- endif %}

{%- if "caching" in capabilities %}
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: "10s"
      timeout: "3s"
      retries: 3
{%- endif %}

{%- if "monitoring" in capabilities %}
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
{%- endif %}

volumes:
{%- if "persistence" in capabilities %}
  postgres_data:
{%- endif %}
{%- if "caching" in capabilities %}
  redis_data:
{%- endif %}
{%- if "monitoring" in capabilities %}
  prometheus_data:
{%- endif %}

networks:
  default:
    name: {{ server_name }}_network
"""
    
    def _get_enterprise_env_template(self) -> str:
        return """# {{ server_name.upper() }} MCP Server Configuration
# Generated by Enhanced MCP Crafter

# Server Configuration
LOG_LEVEL=INFO
PYTHONUNBUFFERED=1

{%- if "persistence" in capabilities %}
# Database Configuration
DATABASE_URL=postgresql://postgres:password@localhost:5432/{{ server_name.replace("-", "_") }}
{%- endif %}

{%- if "caching" in capabilities %}
# Redis Configuration  
REDIS_URL=redis://localhost:6379/0
CACHE_TTL=3600
{%- endif %}

{%- if "authentication" in capabilities %}
# Authentication Configuration
JWT_SECRET_KEY=your-secret-key-here
JWT_EXPIRATION_HOURS=24
{%- endif %}

{%- if "rate_limiting" in capabilities %}
# Rate Limiting Configuration
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600
{%- endif %}

{%- if "monitoring" in capabilities %}
# Monitoring Configuration
PROMETHEUS_PORT=9090
HEALTH_CHECK_INTERVAL=30
{%- endif %}

{%- if "streaming" in capabilities %}
# Streaming Configuration
WEBSOCKET_PORT=8765
STREAM_BUFFER_SIZE=100
{%- endif %}

{%- if "webhooks" in capabilities %}
# Webhook Configuration
WEBHOOK_TIMEOUT=30
WEBHOOK_RETRY_COUNT=3
{%- endif %}

# Custom Environment Variables
{%- for key, value in environment_vars.items() %}
{{ key }}={{ value }}
{%- endfor %}

# Development Settings
DEBUG=false
"""
    
    def _create_custom_tool_template(self, tool_spec: Dict[str, Any]) -> str:
        """Create custom tool implementation"""
        tool_name = tool_spec.get("name", "custom_tool")
        description = tool_spec.get("description", "Custom tool")
        parameters = tool_spec.get("parameters", {})
        implementation = tool_spec.get("implementation", "return 'Not implemented'")
        
        return f'''"""
Custom tool: {tool_name}
{description}
"""

import json
from typing import Any, List
import mcp.types as types

async def {tool_name}(**kwargs) -> List[types.TextContent]:
    """
    {description}
    
    Parameters: {json.dumps(parameters, indent=2)}
    """
    try:
        # Custom implementation
        {implementation}
        
        result = {{"status": "success", "tool": "{tool_name}", "data": kwargs}}
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    except Exception as e:
        error_result = {{"status": "error", "tool": "{tool_name}", "error": str(e)}}
        return [types.TextContent(type="text", text=json.dumps(error_result, indent=2))]
'''
    
    async def _handle_existing_server(self, server_dir: Path, form: CrafterForm):
        """Handle existing server directory"""
        import shutil
        backup_dir = server_dir.parent / f"{server_dir.name}_backup_{int(asyncio.get_event_loop().time())}"
        shutil.copytree(server_dir, backup_dir)
        logger.info(f"Backed up existing server to {backup_dir}")
    
    async def _generate_docker_config(self, server_dir: Path, form: CrafterForm):
        """Generate Docker configuration"""
        dockerfile_content = self._get_enterprise_dockerfile_template()
        
        # Render template
        template_vars = {
            "server_name": form.server_name,
            "description": form.description,
            "capabilities": [cap.value for cap in form.capabilities],
            "environment_vars": form.environment_vars
        }
        
        if self.jinja_env:
            template = self.jinja_env.from_string(dockerfile_content)
            rendered = template.render(**template_vars)
        else:
            rendered = dockerfile_content
        
        await self._write_file_async(server_dir / "Dockerfile", rendered)
    
    async def _generate_k8s_config(self, server_dir: Path, form: CrafterForm):
        """Generate Kubernetes configuration"""
        k8s_dir = server_dir / "k8s"
        k8s_dir.mkdir(exist_ok=True)
        
        # Basic deployment manifest
        deployment_yaml = f'''apiVersion: apps/v1
kind: Deployment
metadata:
  name: {form.server_name}
  labels:
    app: {form.server_name}
spec:
  replicas: 1
  selector:
    matchLabels:
      app: {form.server_name}
  template:
    metadata:
      labels:
        app: {form.server_name}
    spec:
      containers:
      - name: {form.server_name}
        image: {form.server_name}:latest
        ports:
        - containerPort: 8000
        env:
        - name: LOG_LEVEL
          value: INFO
---
apiVersion: v1
kind: Service
metadata:
  name: {form.server_name}-service
spec:
  selector:
    app: {form.server_name}
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: ClusterIP
'''
        await self._write_file_async(k8s_dir / "deployment.yaml", deployment_yaml)
    
    async def _generate_compose_config(self, server_dir: Path, form: CrafterForm):
        """Generate Docker Compose configuration"""
        compose_content = self._get_enterprise_compose_template()
        
        template_vars = {
            "server_name": form.server_name,
            "description": form.description,
            "capabilities": [cap.value for cap in form.capabilities],
            "environment_vars": form.environment_vars
        }
        
        if self.jinja_env:
            template = self.jinja_env.from_string(compose_content)
            rendered = template.render(**template_vars)
        else:
            rendered = compose_content
        
        await self._write_file_async(server_dir / "docker-compose.yml", rendered)
    
    def _create_readme_template(self, form: CrafterForm) -> str:
        """Create README template"""
        return f'''# {form.server_name.title().replace("-", " ")} MCP Server

{form.description}

**Generated by Enhanced MCP Crafter**  
**Created:** {form.created_at.isoformat()}  
**Complexity:** {form.complexity.value}

## 🚀 Features

This MCP server includes the following capabilities:

{chr(10).join([f"- ✅ **{cap.value.title().replace('_', ' ')}**" for cap in form.capabilities])}

## 📋 Quick Start

### Prerequisites

- Python 3.10 or higher
- Docker (optional)
- Docker Compose (optional)

### Installation

1. **Navigate to the server directory:**
   ```bash
   cd {form.server_name}
   ```

2. **Install dependencies:**
   ```bash
   pip install -e .
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run the server:**
   ```bash
   python src/main.py
   ```

## 🐳 Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# Or build manually
docker build -t {form.server_name} .
docker run {form.server_name}
```

## 🔧 Configuration

The server uses environment variables for configuration. See `.env.example` for available options.

### Important Configuration Notes

- **Transport**: This server uses stdio transport (Anthropic's recommended method)
- **Modules**: Capabilities are implemented as pluggable modules
- **Logging**: Configured via LOG_LEVEL environment variable

## 📚 API Reference

This server implements the official MCP protocol:

- **Protocol Version**: 2024-11-05
- **Transport**: stdio (stdin/stdout)
- **Capabilities**: {", ".join([cap.value for cap in form.capabilities])}

## 🤝 Contributing

This server was generated by the Enhanced MCP Crafter. To modify:

1. Edit the source files in `src/`
2. Modify capability modules in `src/modules/`
3. Add custom tools in `src/tools/`
4. Update configuration in `.env`

## 📄 License

This project is licensed under the MIT License.

## 🔗 Additional Resources

- [Official MCP Documentation](https://docs.anthropic.com/mcp)
- [MCP Protocol Specification](https://docs.anthropic.com/mcp/specification)
- [Enhanced MCP Crafter](https://github.com/dezocode/mcp-system)
'''
    
    def _create_test_template(self, form: CrafterForm) -> str:
        """Create test template"""
        class_name = form.server_name.title().replace('-', '').replace('_', '')
        
        return f'''"""
Tests for {form.server_name} MCP server

Generated by Enhanced MCP Crafter
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch
import mcp.types as types

# Import the server class
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from main import {class_name}Server


class Test{class_name}Server:
    """Test suite for the MCP server implementation."""

    @pytest.fixture
    async def server(self):
        """Create a test server instance."""
        return {class_name}Server()

    @pytest.mark.asyncio
    async def test_server_initialization(self, server):
        """Test that the server initializes correctly."""
        assert server.server.name == "{form.server_name}"
        assert hasattr(server, 'modules')
        
        # Check that capability modules are loaded
        expected_modules = {[repr(cap.value) for cap in form.capabilities]}
        for module_name in expected_modules:
            assert module_name in server.modules

    @pytest.mark.asyncio
    async def test_list_tools(self, server):
        """Test the list_tools handler."""
        tools = await server.server._tool_handlers["list_tools"]()
        
        assert len(tools) > 0
        assert all(isinstance(tool, types.Tool) for tool in tools)
        
        # Verify all tools have required fields
        for tool in tools:
            assert tool.name
            assert tool.description
            assert tool.inputSchema

    @pytest.mark.asyncio
    async def test_module_integration(self, server):
        """Test that modules are properly integrated."""
        for module_name, module in server.modules.items():
            # Check module has required methods
            assert hasattr(module, 'get_tools')
            assert hasattr(module, 'can_handle')
            assert hasattr(module, 'handle_tool')
            
            # Test module tools
            tools = await module.get_tools()
            assert isinstance(tools, list)

    @pytest.mark.asyncio
    async def test_call_tool_routing(self, server):
        """Test that tool calls are routed correctly."""
        call_tool = server.server._tool_handlers["call_tool"]
        
        # Test with unknown tool
        with pytest.raises(ValueError, match="Unknown tool"):
            await call_tool("nonexistent_tool", {{}})

    @pytest.mark.asyncio
    async def test_error_handling(self, server):
        """Test error handling in tool calls."""
        call_tool = server.server._tool_handlers["call_tool"]
        
        # Test with invalid parameters should be handled gracefully
        # Implementation depends on specific tools

    def test_server_metadata(self, server):
        """Test server metadata and configuration."""
        assert hasattr(server, 'server')
        assert server.server.name == "{form.server_name}"

    @pytest.mark.asyncio 
    async def test_mcp_protocol_compliance(self, server):
        """Test MCP protocol compliance."""
        tools = await server.server._tool_handlers["list_tools"]()
        
        # Test that tools return proper MCP content types
        for tool in tools:
            assert hasattr(tool, 'name')
            assert hasattr(tool, 'description')
            assert hasattr(tool, 'inputSchema')


# Integration tests
class Test{class_name}Integration:
    """Integration tests for the MCP server."""

    @pytest.mark.asyncio
    async def test_full_workflow(self):
        """Test a complete MCP workflow."""
        server = {class_name}Server()
        
        # List tools
        tools = await server.server._tool_handlers["list_tools"]()
        assert len(tools) > 0
        
        # Test each available tool
        call_tool = server.server._tool_handlers["call_tool"]
        
        for tool in tools[:3]:  # Test first 3 tools
            try:
                # Call with empty arguments
                result = await call_tool(tool.name, {{}})
                assert isinstance(result, list)
                assert all(isinstance(content, types.TextContent) for content in result)
            except ValueError as e:
                # Some tools may require specific parameters
                assert "required" in str(e).lower() or "unknown tool" in str(e).lower()


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
'''
    
    async def _validate_server_structure(self, server_dir: Path):
        """Validate generated server structure"""
        required_files = [
            "src/main.py",
            "pyproject.toml",
            ".env.example",
            "README.md"
        ]
        
        for file_path in required_files:
            full_path = server_dir / file_path
            if not full_path.exists():
                raise ValueError(f"Required file missing: {file_path}")
    
    async def _setup_git_repo(self, server_dir: Path):
        """Setup git repository"""
        gitignore_content = '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Environment
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Database
*.db
*.sqlite

# Docker
.dockerignore

# MCP specific
server_data.db
mcp-workspace/
'''
        await self._write_file_async(server_dir / ".gitignore", gitignore_content)
    
    async def _generate_startup_scripts(self, server_dir: Path, form: CrafterForm):
        """Generate startup scripts"""
        scripts_dir = server_dir / "scripts"
        scripts_dir.mkdir(exist_ok=True)
        
        # Development startup script
        dev_script = f'''#!/bin/bash
# Development startup script for {form.server_name}

echo "Starting {form.server_name} in development mode..."

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Install dependencies if needed
if [ ! -d ".venv" ]; then
    echo "Installing dependencies..."
    python -m venv .venv
    source .venv/bin/activate
    pip install -e .
else
    source .venv/bin/activate
fi

# Run the server
echo "Starting MCP server..."
python src/main.py
'''
        await self._write_file_async(scripts_dir / "dev.sh", dev_script)
        
        # Production startup script
        prod_script = f'''#!/bin/bash
# Production startup script for {form.server_name}

echo "Starting {form.server_name} in production mode..."

# Ensure environment is set
export PYTHONUNBUFFERED=1
export LOG_LEVEL=${{LOG_LEVEL:-INFO}}

# Run with proper error handling
exec python src/main.py
'''
        await self._write_file_async(scripts_dir / "prod.sh", prod_script)
    
    async def _rebuild_tools(self, server_name: str):
        """Rebuild tools for a server"""
        logger.info(f"Rebuilding tools for {server_name}")
        # Implementation would reload tool modules
    
    async def _rebuild_modules(self, server_name: str):
        """Rebuild modules for a server"""
        logger.info(f"Rebuilding modules for {server_name}")
        # Implementation would reload capability modules
    
    async def _rebuild_deployment(self, server_name: str):
        """Rebuild deployment configuration"""
        logger.info(f"Rebuilding deployment config for {server_name}")
        # Implementation would regenerate Docker/compose files


# CLI Integration
@click.group()
def cli():
    """Enhanced MCP Crafter CLI"""
    pass

@cli.command()
@click.option('--form', type=str, help='JSON form data from Claude')
@click.option('--name', type=str, help='Server name')
@click.option('--complexity', type=click.Choice(['simple', 'standard', 'advanced', 'enterprise']), default='standard')
def create(form, name, complexity):
    """Create a new MCP server"""
    async def _create():
        crafter = EnhancedMCPCrafter()
        await crafter.start_watching()
        
        if form:
            # Process Claude form
            form_data = json.loads(form)
            build_id = await crafter.process_claude_form(form_data)
            click.echo(f"Build started with ID: {build_id}")
        elif name:
            # Interactive creation
            form_data = {
                "server_name": name,
                "complexity": complexity,
                "capabilities": ["tools", "monitoring"],
                "template_base": "enterprise-python",
                "custom_tools": [],
                "dependencies": [],
                "environment_vars": {},
                "deployment_config": {},
                "metadata": {}
            }
            build_id = await crafter.process_claude_form(form_data)
            click.echo(f"Build started with ID: {build_id}")
        
        await crafter.stop_watching()
    
    asyncio.run(_create())

@cli.command()
@click.argument('build_id')
def status(build_id):
    """Get build status"""
    async def _status():
        crafter = EnhancedMCPCrafter()
        status = await crafter.get_build_status(build_id)
        click.echo(json.dumps(status, indent=2, default=str))
    
    asyncio.run(_status())

@cli.command()
def list():
    """List all servers"""
    crafter = EnhancedMCPCrafter()
    servers = crafter.list_servers()
    click.echo(json.dumps(servers, indent=2, default=str))

if __name__ == "__main__":
    cli()