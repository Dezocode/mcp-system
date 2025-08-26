#!/usr/bin/env python3
"""
Enhanced MCP Crafter - Robust MCP Server Generation System
Builds upon existing mcp-create-server.py with advanced capabilities

This enhanced version adds:
1. Watchdog file system monitoring integration
2. CLI framework generation
3. Asynchronous form processing from Claude
4. Modular component architecture
5. Runtime configuration and tweaking
6. Orchestration capabilities

Author: Enhanced MCP Crafter Team
Version: 1.0.0
"""

import asyncio
import json
import logging
import os
import shutil
import sys
import tempfile
import time
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import yaml
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

# Import the existing MCP server generator
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import manually since the file uses hyphens
import importlib.util
spec = importlib.util.spec_from_file_location("mcp_create_server", Path(__file__).parent.parent / "core" / "mcp-create-server.py")
mcp_create_server = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mcp_create_server)
MCPServerGenerator = mcp_create_server.MCPServerGenerator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class EnhancedServerRequest:
    """Enhanced server generation request with advanced features"""
    name: str
    template: str
    description: str
    port: int
    features: List[str] = None  # ["watchdog", "cli", "automation", "monitoring"]
    dependencies: List[str] = None
    environment: Dict[str, str] = None
    custom_modules: List[Dict] = None
    path: Optional[str] = None
    
    def __post_init__(self):
        if self.features is None:
            self.features = []
        if self.dependencies is None:
            self.dependencies = []
        if self.environment is None:
            self.environment = {}
        if self.custom_modules is None:
            self.custom_modules = []

@dataclass
class CrafterFormData:
    """Structured form data from Claude or other clients"""
    form_type: str  # "server_generation", "enhancement", "orchestration"
    requirements: Dict[str, Any]
    options: Dict[str, Any] = None
    metadata: Dict[str, Any] = None
    created_at: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()
        if self.options is None:
            self.options = {}
        if self.metadata is None:
            self.metadata = {}

class EnhancedMCPCrafter(MCPServerGenerator):
    """Enhanced MCP Server Generator with robust capabilities"""
    
    def __init__(self):
        super().__init__()
        self.enhanced_templates_dir = Path.home() / ".mcp-enhanced-templates"
        self.enhanced_templates_dir.mkdir(exist_ok=True)
        self.active_forms = {}
        self.orchestration_tasks = {}
        
        # Enhanced templates with feature modules
        self.feature_modules = {
            "watchdog": self._generate_watchdog_module,
            "cli": self._generate_cli_module,
            "automation": self._generate_automation_module,
            "monitoring": self._generate_monitoring_module
        }
        
        logger.info("Enhanced MCP Crafter initialized")
    
    def generate_enhanced_server(self, request: EnhancedServerRequest) -> Dict[str, str]:
        """Generate an enhanced MCP server with advanced features"""
        logger.info(f"Generating enhanced server: {request.name} with features: {request.features}")
        
        # Start with base template from parent class
        if request.template == "python-fastmcp":
            base_files = self.create_python_fastmcp_template(
                request.name, request.port, request.description
            )
        elif request.template == "typescript-node":
            base_files = self.create_typescript_template(
                request.name, request.port, request.description
            )
        elif request.template == "minimal-python":
            base_files = self.create_minimal_python_template(
                request.name, request.port, request.description
            )
        else:
            raise ValueError(f"Unknown template: {request.template}")
        
        # Enhance with requested features
        enhanced_files = self._enhance_base_template(base_files, request)
        
        return enhanced_files
    
    def _enhance_base_template(self, base_files: Dict[str, str], request: EnhancedServerRequest) -> Dict[str, str]:
        """Enhance base template with requested features"""
        enhanced_files = base_files.copy()
        
        # Enhance main server file
        if "src/main.py" in enhanced_files:
            enhanced_files["src/main.py"] = self._enhance_main_file(
                enhanced_files["src/main.py"], request
            )
        
        # Add feature modules
        for feature in request.features:
            if feature in self.feature_modules:
                module_files = self.feature_modules[feature](request)
                enhanced_files.update(module_files)
        
        # Enhance configuration files
        enhanced_files["pyproject.toml"] = self._enhance_pyproject(
            enhanced_files.get("pyproject.toml", ""), request
        )
        enhanced_files["README.md"] = self._enhance_readme(
            enhanced_files.get("README.md", ""), request
        )
        enhanced_files[".env.example"] = self._enhance_env(
            enhanced_files.get(".env.example", ""), request
        )
        
        # Add Docker enhancements
        enhanced_files["docker-compose.enhanced.yml"] = self._generate_enhanced_docker_compose(request)
        
        # Add component directory structure
        enhanced_files["src/components/__init__.py"] = ""
        
        return enhanced_files
    
    def _enhance_main_file(self, main_content: str, request: EnhancedServerRequest) -> str:
        """Enhance the main server file with feature integrations"""
        
        # Add imports for enabled features
        feature_imports = []
        feature_setup = []
        
        if "watchdog" in request.features:
            feature_imports.append("from components.watchdog_component import setup_watchdog")
            feature_setup.append("        self.watchdog = setup_watchdog(self)")
        
        if "cli" in request.features:
            feature_imports.append("from components.cli_component import setup_cli")
            feature_setup.append("        self.cli = setup_cli(self)")
        
        if "automation" in request.features:
            feature_imports.append("from components.automation_component import setup_automation")
            feature_setup.append("        self.automation = setup_automation(self)")
        
        if "monitoring" in request.features:
            feature_imports.append("from components.monitoring_component import setup_monitoring")
            feature_setup.append("        self.monitoring = setup_monitoring(self)")
        
        # Insert imports after existing imports
        imports_section = "\n".join(feature_imports)
        setup_section = "\n".join(feature_setup)
        
        # Find insertion points and enhance the file
        lines = main_content.split('\n')
        
        # Add imports after existing imports
        import_end_idx = 0
        for i, line in enumerate(lines):
            if line.startswith('import ') or line.startswith('from '):
                import_end_idx = i
        
        if imports_section:
            lines.insert(import_end_idx + 1, imports_section)
        
        # Add feature setup in the context initialization
        for i, line in enumerate(lines):
            if "def __post_init__(self):" in line or "context = " in line and "Context(" in line:
                # Insert setup calls after context creation
                lines.insert(i + 2, setup_section)
                break
        
        # Add enhanced tools
        enhanced_tools = self._generate_enhanced_tools(request)
        lines.extend(enhanced_tools.split('\n'))
        
        return '\n'.join(lines)
    
    def _generate_enhanced_tools(self, request: EnhancedServerRequest) -> str:
        """Generate enhanced MCP tools for the server"""
        tools = []
        
        # Always add enhanced status tool
        tools.append(f"""
@mcp.tool()
async def get_enhanced_status(ctx: Context) -> str:
    \"\"\"Get comprehensive server status with all features.
    
    Args:
        ctx: The MCP server provided context
    
    Returns:
        Detailed server status including all features
    \"\"\"
    context = ctx.request_context.lifespan_context
    status = {{
        "server": SERVER_NAME,
        "status": "running",
        "port": SERVER_PORT,
        "features": {request.features},
        "uptime": time.time() - getattr(context, 'start_time', time.time())
    }}
    
    # Add feature-specific status
    if hasattr(context, 'monitoring'):
        status["monitoring"] = context.monitoring.get_summary()
    
    if hasattr(context, 'automation'):
        status["automation"] = {{
            "running": context.automation.running,
            "tasks": list(context.automation.scheduled_tasks.keys())
        }}
    
    if hasattr(context, 'watchdog'):
        status["watchdog"] = {{
            "active": hasattr(context, 'watchdog_observer'),
            "watching": getattr(context, 'watch_paths', [])
        }}
    
    return json.dumps(status, indent=2)
""")
        
        # Add file change handler if watchdog is enabled
        if "watchdog" in request.features:
            tools.append(f"""
@mcp.tool()
async def handle_file_change(ctx: Context, event_type: str, file_path: str) -> str:
    \"\"\"Handle file system changes detected by watchdog.
    
    Args:
        ctx: The MCP server provided context
        event_type: Type of file event (created, modified, deleted)
        file_path: Path to the changed file
        
    Returns:
        Result of handling the file change
    \"\"\"
    logger.info(f"File {{event_type}}: {{file_path}}")
    
    # Add custom file change handling logic here
    context = ctx.request_context.lifespan_context
    
    # Example: reload configuration on config file changes
    if file_path.endswith('.env') or file_path.endswith('config.json'):
        logger.info("Configuration file changed, triggering reload...")
        # Add reload logic here
    
    return f"Handled {{event_type}} event for {{file_path}} at {{datetime.now()}}"
""")
        
        # Add configuration tool if needed
        tools.append(f"""
@mcp.tool()
async def configure_feature(ctx: Context, feature: str, config: str) -> str:
    \"\"\"Configure server features dynamically.
    
    Args:
        ctx: The MCP server provided context
        feature: Feature name to configure
        config: Configuration JSON string
        
    Returns:
        Configuration result
    \"\"\"
    try:
        config_data = json.loads(config)
        context = ctx.request_context.lifespan_context
        
        if feature == "monitoring" and hasattr(context, 'monitoring'):
            # Configure monitoring
            context.monitoring.update_config(config_data)
            return f"Configured monitoring: {{config_data}}"
        elif feature == "automation" and hasattr(context, 'automation'):
            # Configure automation
            context.automation.update_config(config_data)
            return f"Configured automation: {{config_data}}"
        else:
            return f"Feature {{feature}} not available or not configurable"
            
    except json.JSONDecodeError:
        return f"Invalid JSON configuration: {{config}}"
    except Exception as e:
        return f"Error configuring {{feature}}: {{str(e)}}"
""")
        
        return '\n'.join(tools)
    
    def _generate_watchdog_module(self, request: EnhancedServerRequest) -> Dict[str, str]:
        """Generate watchdog monitoring module"""
        
        watchdog_component = f'''"""
Watchdog monitoring component for {request.name}
Provides real-time file system monitoring capabilities
"""
import logging
import asyncio
from pathlib import Path
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

logger = logging.getLogger(__name__)

class {request.name.title().replace("-", "")}WatchdogHandler(FileSystemEventHandler):
    """File system monitoring handler for {request.name}"""
    
    def __init__(self, server_context=None):
        self.server_context = server_context
        self.logger = logging.getLogger(f"{request.name}.watchdog")
        
    def on_modified(self, event):
        if not event.is_directory:
            self.logger.info(f"File modified: {{event.src_path}}")
            if self.server_context and hasattr(self.server_context, 'handle_file_change'):
                try:
                    asyncio.create_task(
                        self.server_context.handle_file_change("modified", event.src_path)
                    )
                except Exception as e:
                    self.logger.error(f"Error handling file change: {{e}}")
    
    def on_created(self, event):
        if not event.is_directory:
            self.logger.info(f"File created: {{event.src_path}}")
            if self.server_context and hasattr(self.server_context, 'handle_file_change'):
                try:
                    asyncio.create_task(
                        self.server_context.handle_file_change("created", event.src_path)
                    )
                except Exception as e:
                    self.logger.error(f"Error handling file change: {{e}}")
    
    def on_deleted(self, event):
        if not event.is_directory:
            self.logger.info(f"File deleted: {{event.src_path}}")
            if self.server_context and hasattr(self.server_context, 'handle_file_change'):
                try:
                    asyncio.create_task(
                        self.server_context.handle_file_change("deleted", event.src_path)
                    )
                except Exception as e:
                    self.logger.error(f"Error handling file change: {{e}}")

def setup_watchdog(server_context, watch_paths=None):
    """Setup file system monitoring for the server"""
    if watch_paths is None:
        watch_paths = ["."]
    
    observer = Observer()
    handler = {request.name.title().replace("-", "")}WatchdogHandler(server_context)
    
    for path in watch_paths:
        if Path(path).exists():
            observer.schedule(handler, path, recursive=True)
            logger.info(f"Watching path: {{path}}")
        else:
            logger.warning(f"Watch path does not exist: {{path}}")
    
    observer.start()
    server_context.watchdog_observer = observer
    server_context.watch_paths = watch_paths
    
    logger.info("Watchdog monitoring started")
    return observer

def stop_watchdog(server_context):
    """Stop file system monitoring"""
    if hasattr(server_context, 'watchdog_observer'):
        server_context.watchdog_observer.stop()
        server_context.watchdog_observer.join()
        logger.info("Watchdog monitoring stopped")
'''
        
        return {"src/components/watchdog_component.py": watchdog_component}
    
    def _generate_cli_module(self, request: EnhancedServerRequest) -> Dict[str, str]:
        """Generate CLI integration module"""
        
        cli_component = f'''"""
CLI integration component for {request.name}
Provides command-line interface for server management
"""
import click
import asyncio
import json
import requests
from typing import Any, Dict

@click.group()
@click.pass_context
def cli(ctx):
    """CLI interface for {request.name} MCP server"""
    ctx.ensure_object(dict)
    ctx.obj['server_url'] = f"http://localhost:{request.port}"

@cli.command()
@click.option('--config', help='Configuration file path')
@click.option('--port', default={request.port}, help='Server port')
@click.option('--host', default='localhost', help='Server host')
@click.option('--watch-paths', multiple=True, help='Paths to monitor with watchdog')
def start(config, port, host, watch_paths):
    """Start the {request.name} server"""
    click.echo(f"Starting {request.name} on {{host}}:{{port}}")
    
    # Set environment variables if provided
    if config:
        click.echo(f"Using config file: {{config}}")
    
    if watch_paths:
        import os
        os.environ['WATCH_PATHS'] = ','.join(watch_paths)
        click.echo(f"Monitoring paths: {{', '.join(watch_paths)}}")
    
    # Import and start the server
    try:
        from src.main import mcp
        mcp.run(host=host, port=port)
    except ImportError:
        click.echo("Error: Could not import server. Make sure you're in the server directory.")
        return 1

@cli.command()
@click.pass_context
def status(ctx):
    """Get server status"""
    server_url = ctx.obj['server_url']
    try:
        # Try to get status via HTTP health endpoint
        response = requests.get(f"{{server_url}}/health", timeout=5)
        if response.status_code == 200:
            status_data = response.json()
            click.echo(f"✅ {request.name} server is running")
            click.echo(f"Status: {{status_data.get('status', 'unknown')}}")
            click.echo(f"Uptime: {{status_data.get('uptime', 'unknown')}}")
        else:
            click.echo(f"❌ Server returned status code: {{response.status_code}}")
    except requests.exceptions.RequestException:
        click.echo(f"❌ {request.name} server is not responding")

@cli.command()
@click.option('--key', required=True, help='Configuration key')
@click.option('--value', required=True, help='Configuration value')
@click.pass_context
def config_set(ctx, key, value):
    """Set configuration value"""
    click.echo(f"Setting {{key}} = {{value}}")
    
    # Try to update configuration via API
    server_url = ctx.obj['server_url']
    try:
        payload = {{"key": key, "value": value}}
        response = requests.post(f"{{server_url}}/config", json=payload, timeout=5)
        if response.status_code == 200:
            click.echo("✅ Configuration updated successfully")
        else:
            click.echo(f"❌ Failed to update configuration: {{response.text}}")
    except requests.exceptions.RequestException as e:
        click.echo(f"❌ Error connecting to server: {{e}}")

@cli.command()
@click.option('--key', help='Configuration key to get')
@click.pass_context
def config_get(ctx, key):
    """Get configuration value"""
    server_url = ctx.obj['server_url']
    try:
        url = f"{{server_url}}/config"
        if key:
            url += f"?key={{key}}"
        
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            config_data = response.json()
            if key:
                click.echo(f"{{key}}: {{config_data.get(key, 'Not found')}}")
            else:
                click.echo("Configuration:")
                for k, v in config_data.items():
                    click.echo(f"  {{k}}: {{v}}")
        else:
            click.echo(f"❌ Failed to get configuration: {{response.text}}")
    except requests.exceptions.RequestException as e:
        click.echo(f"❌ Error connecting to server: {{e}}")

@cli.command()
@click.argument('tool_name')
@click.argument('args', nargs=-1)
@click.pass_context
def call_tool(ctx, tool_name, args):
    """Call a server tool directly"""
    click.echo(f"Calling tool {{tool_name}} with args {{args}}")
    
    server_url = ctx.obj['server_url']
    try:
        payload = {{
            "tool": tool_name,
            "arguments": list(args)
        }}
        response = requests.post(f"{{server_url}}/call_tool", json=payload, timeout=10)
        if response.status_code == 200:
            result = response.json()
            click.echo("Tool result:")
            click.echo(json.dumps(result, indent=2))
        else:
            click.echo(f"❌ Tool call failed: {{response.text}}")
    except requests.exceptions.RequestException as e:
        click.echo(f"❌ Error connecting to server: {{e}}")

@cli.command()
@click.pass_context
def logs(ctx):
    """View server logs"""
    # Try to read local log files
    log_paths = ["logs/server.log", "server.log", f"{request.name}.log"]
    
    for log_path in log_paths:
        if Path(log_path).exists():
            click.echo(f"Reading logs from {{log_path}}:")
            with open(log_path, 'r') as f:
                lines = f.readlines()
                # Show last 50 lines
                for line in lines[-50:]:
                    click.echo(line.strip())
            return
    
    click.echo("No log files found")

def setup_cli(server_context):
    """Setup CLI integration for the server context"""
    # This would be called during server initialization
    # to prepare CLI-related functionality
    server_context.cli_enabled = True
    return cli

if __name__ == '__main__':
    cli()
'''
        
        return {"src/cli.py": cli_component}
    
    def _generate_automation_module(self, request: EnhancedServerRequest) -> Dict[str, str]:
        """Generate automation module"""
        
        automation_component = f'''"""
Automation component for {request.name}
Provides scheduled tasks and automated operations
"""
import asyncio
import schedule
import time
import logging
from datetime import datetime, timedelta
from typing import Callable, Dict, Any

logger = logging.getLogger(__name__)

class AutomationManager:
    """Manages automated tasks for {request.name}"""
    
    def __init__(self, server_context=None):
        self.server_context = server_context
        self.scheduled_tasks = {{}}
        self.running = False
        self.config = {{
            "health_check_interval": "5m",
            "log_cleanup_interval": "24h",
            "metrics_collection_interval": "30s"
        }}
        
    async def start_automation(self):
        """Start the automation loop"""
        self.running = True
        logger.info("Starting automation manager")
        
        # Schedule default tasks
        self._schedule_default_tasks()
        
        while self.running:
            schedule.run_pending()
            await asyncio.sleep(1)
    
    def stop_automation(self):
        """Stop the automation loop"""
        self.running = False
        schedule.clear()
        logger.info("Automation manager stopped")
    
    def _schedule_default_tasks(self):
        """Schedule default automated tasks"""
        
        # Health check task
        self.schedule_task(
            "health_check", 
            self.run_health_check, 
            self.config["health_check_interval"]
        )
        
        # Log cleanup task
        self.schedule_task(
            "log_cleanup", 
            self.cleanup_logs, 
            self.config["log_cleanup_interval"]
        )
        
        # Metrics collection (if monitoring is enabled)
        if hasattr(self.server_context, 'monitoring'):
            self.schedule_task(
                "metrics_collection",
                self.collect_metrics,
                self.config["metrics_collection_interval"]
            )
    
    def schedule_task(self, task_name: str, func: Callable, 
                     interval: str = "1m", **kwargs):
        """Schedule a recurring task
        
        Args:
            task_name: Unique name for the task
            func: Function to execute
            interval: Interval string (e.g., '30s', '5m', '1h', '1d')
            **kwargs: Additional arguments for the function
        """
        try:
            if interval.endswith('s'):
                schedule.every(int(interval[:-1])).seconds.do(func, **kwargs)
            elif interval.endswith('m'):
                schedule.every(int(interval[:-1])).minutes.do(func, **kwargs)
            elif interval.endswith('h'):
                schedule.every(int(interval[:-1])).hours.do(func, **kwargs)
            elif interval.endswith('d'):
                schedule.every(int(interval[:-1])).days.do(func, **kwargs)
            else:
                logger.error(f"Invalid interval format: {{interval}}")
                return
            
            self.scheduled_tasks[task_name] = {{
                "function": func,
                "interval": interval,
                "kwargs": kwargs
            }}
            logger.info(f"Scheduled task '{{task_name}}' with interval {{interval}}")
            
        except ValueError as e:
            logger.error(f"Error scheduling task '{{task_name}}': {{e}}")
    
    def unschedule_task(self, task_name: str):
        """Remove a scheduled task"""
        if task_name in self.scheduled_tasks:
            # Note: schedule library doesn't provide easy task removal by name
            # In a production system, you'd want a more sophisticated scheduler
            del self.scheduled_tasks[task_name]
            logger.info(f"Unscheduled task: {{task_name}}")
    
    async def run_health_check(self):
        """Automated health check"""
        try:
            if self.server_context:
                # Check server health
                start_time = time.time()
                
                # Basic health checks
                health_status = {{
                    "timestamp": datetime.now().isoformat(),
                    "server_running": True,
                    "response_time": time.time() - start_time,
                    "memory_usage": self._get_memory_usage(),
                    "disk_usage": self._get_disk_usage()
                }}
                
                # Add feature-specific health checks
                if hasattr(self.server_context, 'monitoring'):
                    health_status["monitoring"] = "active"
                
                if hasattr(self.server_context, 'watchdog_observer'):
                    health_status["watchdog"] = "active"
                
                logger.info(f"Health check completed: {{health_status}}")
                
        except Exception as e:
            logger.error(f"Health check failed: {{e}}")
    
    async def cleanup_logs(self):
        """Automated log cleanup"""
        try:
            log_dir = Path("logs")
            if log_dir.exists():
                # Remove log files older than 7 days
                cutoff_date = datetime.now() - timedelta(days=7)
                
                for log_file in log_dir.glob("*.log"):
                    if log_file.stat().st_mtime < cutoff_date.timestamp():
                        log_file.unlink()
                        logger.info(f"Cleaned up old log file: {{log_file}}")
                        
            logger.info("Log cleanup completed")
            
        except Exception as e:
            logger.error(f"Log cleanup failed: {{e}}")
    
    async def collect_metrics(self):
        """Collect system metrics"""
        try:
            if hasattr(self.server_context, 'monitoring'):
                await self.server_context.monitoring.collect_metrics()
                
        except Exception as e:
            logger.error(f"Metrics collection failed: {{e}}")
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage percentage"""
        try:
            import psutil
            return psutil.virtual_memory().percent
        except ImportError:
            return 0.0
    
    def _get_disk_usage(self) -> float:
        """Get current disk usage percentage"""
        try:
            import psutil
            return psutil.disk_usage('/').percent
        except ImportError:
            return 0.0
    
    def update_config(self, new_config: Dict[str, Any]):
        """Update automation configuration"""
        self.config.update(new_config)
        logger.info(f"Automation configuration updated: {{new_config}}")
        
        # Reschedule tasks if intervals changed
        self.stop_automation()
        asyncio.create_task(self.start_automation())

def setup_automation(server_context):
    """Setup automated tasks for the server"""
    automation = AutomationManager(server_context)
    server_context.automation = automation
    
    # Start automation in background
    asyncio.create_task(automation.start_automation())
    
    logger.info("Automation system initialized")
    return automation
'''
        
        return {"src/components/automation_component.py": automation_component}
    
    def _generate_monitoring_module(self, request: EnhancedServerRequest) -> Dict[str, str]:
        """Generate monitoring module"""
        
        monitoring_component = f'''"""
Monitoring component for {request.name}
Provides comprehensive system and application monitoring
"""
import time
import logging
import asyncio
from dataclasses import dataclass, asdict
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class MetricData:
    """Metric data point"""
    name: str
    value: float
    timestamp: float
    labels: Dict[str, str] = None
    
    def __post_init__(self):
        if self.labels is None:
            self.labels = {{}}

class MonitoringManager:
    """Manages monitoring and metrics for {request.name}"""
    
    def __init__(self, server_context=None):
        self.server_context = server_context
        self.metrics: List[MetricData] = []
        self.running = False
        self.config = {{
            "collection_interval": 30,  # seconds
            "retention_count": 1000,    # number of metrics to keep
            "export_enabled": False,
            "export_format": "json"
        }}
        
    async def start_monitoring(self):
        """Start monitoring loop"""
        self.running = True
        logger.info("Starting monitoring system")
        
        while self.running:
            await self.collect_metrics()
            await asyncio.sleep(self.config["collection_interval"])
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.running = False
        logger.info("Monitoring system stopped")
    
    async def collect_metrics(self):
        """Collect system and application metrics"""
        timestamp = time.time()
        
        try:
            # System metrics
            system_metrics = self._collect_system_metrics(timestamp)
            self.metrics.extend(system_metrics)
            
            # Application metrics
            app_metrics = await self._collect_application_metrics(timestamp)
            self.metrics.extend(app_metrics)
            
            # Feature-specific metrics
            feature_metrics = self._collect_feature_metrics(timestamp)
            self.metrics.extend(feature_metrics)
            
            # Cleanup old metrics
            if len(self.metrics) > self.config["retention_count"]:
                self.metrics = self.metrics[-self.config["retention_count"]:]
            
            # Export metrics if enabled
            if self.config["export_enabled"]:
                await self._export_metrics()
                
        except Exception as e:
            logger.error(f"Error collecting metrics: {{e}}")
    
    def _collect_system_metrics(self, timestamp: float) -> List[MetricData]:
        """Collect system-level metrics"""
        metrics = []
        
        try:
            import psutil
            
            # CPU metrics
            cpu_percent = psutil.cpu_percent()
            metrics.append(MetricData("cpu_usage_percent", cpu_percent, timestamp))
            
            # Memory metrics
            memory = psutil.virtual_memory()
            metrics.append(MetricData("memory_usage_percent", memory.percent, timestamp))
            metrics.append(MetricData("memory_used_bytes", memory.used, timestamp))
            metrics.append(MetricData("memory_available_bytes", memory.available, timestamp))
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            metrics.append(MetricData("disk_usage_percent", disk.percent, timestamp))
            metrics.append(MetricData("disk_used_bytes", disk.used, timestamp))
            metrics.append(MetricData("disk_free_bytes", disk.free, timestamp))
            
            # Network metrics
            network = psutil.net_io_counters()
            metrics.append(MetricData("network_bytes_sent", network.bytes_sent, timestamp))
            metrics.append(MetricData("network_bytes_recv", network.bytes_recv, timestamp))
            
        except ImportError:
            logger.warning("psutil not available, skipping system metrics")
        except Exception as e:
            logger.error(f"Error collecting system metrics: {{e}}")
        
        return metrics
    
    async def _collect_application_metrics(self, timestamp: float) -> List[MetricData]:
        """Collect application-specific metrics"""
        metrics = []
        
        try:
            if self.server_context:
                # Server uptime
                if hasattr(self.server_context, 'start_time'):
                    uptime = timestamp - self.server_context.start_time
                    metrics.append(MetricData("server_uptime_seconds", uptime, timestamp))
                
                # Request counts (would be implemented with actual request tracking)
                metrics.append(MetricData("requests_total", 1, timestamp, {{"method": "GET"}}))
                
                # Response times (would be implemented with actual timing)
                metrics.append(MetricData("response_time_seconds", 0.1, timestamp))
                
        except Exception as e:
            logger.error(f"Error collecting application metrics: {{e}}")
        
        return metrics
    
    def _collect_feature_metrics(self, timestamp: float) -> List[MetricData]:
        """Collect feature-specific metrics"""
        metrics = []
        
        try:
            if self.server_context:
                # Watchdog metrics
                if hasattr(self.server_context, 'watchdog_observer'):
                    metrics.append(MetricData("watchdog_active", 1, timestamp))
                    metrics.append(MetricData(
                        "watchdog_watched_paths", 
                        len(getattr(self.server_context, 'watch_paths', [])), 
                        timestamp
                    ))
                
                # Automation metrics
                if hasattr(self.server_context, 'automation'):
                    automation = self.server_context.automation
                    metrics.append(MetricData("automation_active", 1 if automation.running else 0, timestamp))
                    metrics.append(MetricData("automation_tasks_count", len(automation.scheduled_tasks), timestamp))
                
        except Exception as e:
            logger.error(f"Error collecting feature metrics: {{e}}")
        
        return metrics
    
    async def _export_metrics(self):
        """Export metrics to external systems"""
        try:
            if self.config["export_format"] == "json":
                await self._export_json()
            elif self.config["export_format"] == "prometheus":
                await self._export_prometheus()
                
        except Exception as e:
            logger.error(f"Error exporting metrics: {{e}}")
    
    async def _export_json(self):
        """Export metrics in JSON format"""
        export_dir = Path("metrics")
        export_dir.mkdir(exist_ok=True)
        
        # Export recent metrics
        recent_metrics = self.get_recent_metrics(100)
        export_data = {{
            "timestamp": datetime.now().isoformat(),
            "server": "{request.name}",
            "metrics": [asdict(metric) for metric in recent_metrics]
        }}
        
        export_file = export_dir / f"metrics_{{int(time.time())}}.json"
        with open(export_file, 'w') as f:
            import json
            json.dump(export_data, f, indent=2)
    
    async def _export_prometheus(self):
        """Export metrics in Prometheus format"""
        # This would implement Prometheus metrics export
        # For now, just log that it would be exported
        logger.info("Would export metrics to Prometheus")
    
    def get_recent_metrics(self, count=100) -> List[MetricData]:
        """Get recent metrics"""
        return self.metrics[-count:] if self.metrics else []
    
    def get_summary(self) -> Dict[str, Any]:
        """Get metric summary"""
        if not self.metrics:
            return {{"status": "no_data"}}
        
        recent = self.get_recent_metrics(10)
        latest_timestamp = recent[-1].timestamp if recent else time.time()
        
        # Calculate averages for key metrics
        cpu_metrics = [m.value for m in recent if m.name == "cpu_usage_percent"]
        memory_metrics = [m.value for m in recent if m.name == "memory_usage_percent"]
        
        return {{
            "status": "active",
            "last_collection": datetime.fromtimestamp(latest_timestamp).isoformat(),
            "total_metrics": len(self.metrics),
            "recent_cpu_avg": sum(cpu_metrics) / len(cpu_metrics) if cpu_metrics else 0,
            "recent_memory_avg": sum(memory_metrics) / len(memory_metrics) if memory_metrics else 0,
            "collection_interval": self.config["collection_interval"]
        }}
    
    def update_config(self, new_config: Dict[str, Any]):
        """Update monitoring configuration"""
        self.config.update(new_config)
        logger.info(f"Monitoring configuration updated: {{new_config}}")

def setup_monitoring(server_context):
    """Setup monitoring for the server"""
    monitoring = MonitoringManager(server_context)
    server_context.monitoring = monitoring
    
    # Start monitoring in background
    asyncio.create_task(monitoring.start_monitoring())
    
    logger.info("Monitoring system initialized")
    return monitoring
'''
        
        return {"src/components/monitoring_component.py": monitoring_component}
    
    def _enhance_pyproject(self, base_pyproject: str, request: EnhancedServerRequest) -> str:
        """Enhance pyproject.toml with feature dependencies"""
        
        # Parse existing dependencies or create new ones
        base_deps = [
            "mcp>=1.0.0",
            "python-dotenv",
            "fastapi", 
            "uvicorn[standard]",
            "pydantic"
        ]
        
        # Add feature-specific dependencies
        if "watchdog" in request.features:
            base_deps.append("watchdog")
        if "automation" in request.features:
            base_deps.append("schedule")
        if "monitoring" in request.features:
            base_deps.append("psutil")
        if "cli" in request.features:
            base_deps.extend(["click", "requests"])
        
        # Add custom dependencies
        base_deps.extend(request.dependencies)
        
        # Generate enhanced pyproject.toml
        deps_str = '",\n    "'.join(base_deps)
        
        enhanced_pyproject = f'''[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "{request.name}"
version = "0.1.0"
description = "{request.description}"
authors = [
    {{name = "Enhanced MCP Crafter", email = "crafter@mcp-system.com"}}
]
readme = "README.md"
requires-python = ">=3.9"
dependencies = [
    "{deps_str}"
]

[project.optional-dependencies]
dev = [
    "pytest",
    "pytest-asyncio", 
    "black",
    "isort",
    "mypy",
    "pre-commit"
]

[project.scripts]
{request.name} = "src.main:main"
{request.name}-cli = "src.cli:cli"

[tool.black]
line-length = 88
target-version = ["py39"]

[tool.isort]
profile = "black"
multi_line_output = 3

[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = false
ignore_missing_imports = true

# Enhanced MCP Server Configuration
[tool.mcp_crafter]
features = {request.features}
generated_at = "{datetime.now(timezone.utc).isoformat()}"
template = "{request.template}"
'''
        
        return enhanced_pyproject
    
    def _enhance_readme(self, base_readme: str, request: EnhancedServerRequest) -> str:
        """Enhance README with feature documentation"""
        
        feature_docs = self._generate_feature_documentation(request.features)
        
        enhanced_readme = f'''# {request.name.title().replace("-", " ")} - Enhanced MCP Server

{request.description}

## ✨ Enhanced Features

This MCP server was generated with the Enhanced MCP Crafter and includes:

{chr(10).join(f"- ✅ **{feature.title()}**: Advanced {feature} capabilities" for feature in request.features)}

## 🚀 Quick Start

1. **Install dependencies:**
```bash
cd {request.name}
pip install -e .
```

2. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your settings
```

3. **Start the server:**
```bash
# Using the main script
{request.name}

# Or using CLI
{request.name}-cli start --port {request.port}

# Or directly
python src/main.py
```

## 📋 CLI Interface

The enhanced server includes a full CLI interface:

```bash
# Start server with options
{request.name}-cli start --port {request.port} --host localhost

# Check server status  
{request.name}-cli status

# Configure features
{request.name}-cli config-set monitoring.enabled true

# View logs
{request.name}-cli logs

# Call tools directly
{request.name}-cli call-tool get_enhanced_status
```

{feature_docs}

## 🔧 API Endpoints

### Core Tools
- `hello_world(name)` - Greet someone
- `get_enhanced_status()` - Get comprehensive server status with all features
- `configure_feature(feature, config)` - Dynamic feature configuration

### Enhanced Tools
{"- `handle_file_change(event_type, file_path)` - Handle file system changes" if "watchdog" in request.features else ""}

## ⚙️ Configuration

Environment variables (see `.env.example`):
```bash
HOST=localhost
PORT={request.port}
{chr(10).join(f"{k}={v}" for k, v in request.environment.items())}
```

## 🐳 Docker Support

```bash
# Build and run with Docker Compose (enhanced version)
docker-compose -f docker-compose.enhanced.yml up -d

# Or standard version
docker-compose up -d
```

## 🔗 Integration

Add to your MCP configuration (`~/.mcp-servers.json`):
```json
{{
  "{request.name}": {{
    "name": "{request.name.title().replace('-', ' ')} Enhanced MCP Server",
    "command": "uv run python src/main.py",
    "port": {request.port},
    "features": {request.features},
    "env_file": ".env"
  }}
}}
```

## 🛠️ Development

This server was generated by the Enhanced MCP Crafter with:
- **Template**: {request.template}
- **Features**: {', '.join(request.features)}
- **Dependencies**: {', '.join(request.dependencies)}
- **Generated**: {datetime.now(timezone.utc).isoformat()}

### Adding Custom Tools

1. Add new functions to `src/main.py` decorated with `@mcp.tool()`
2. Restart the server to load new tools
3. Test with: `{request.name}-cli call-tool your_new_tool`

### Feature Configuration

Each feature can be configured dynamically:
```bash
{request.name}-cli config-set feature_name.setting value
```

## 📄 License

This project is licensed under the MIT License.
'''
        
        return enhanced_readme
    
    def _generate_feature_documentation(self, features: List[str]) -> str:
        """Generate documentation for enabled features"""
        docs = []
        
        if "watchdog" in features:
            docs.append("""## 🔍 Watchdog Monitoring

Automatic file system monitoring with real-time change detection:

- **Real-time monitoring**: Detects file changes as they happen
- **Configurable paths**: Monitor specific directories or files
- **Event handling**: Custom responses to file changes
- **Integration ready**: Connects with automation and monitoring systems

### Configuration:
```bash
# Set watch paths
export WATCH_PATHS=".,config/,src/"

# Enable/disable via CLI
{server_name}-cli config-set watchdog.enabled true
```""")
        
        if "cli" in features:
            docs.append("""## 💻 CLI Integration

Full command-line interface for server management:

- **Server control**: Start, stop, status monitoring
- **Configuration management**: Dynamic config updates
- **Tool calling**: Direct tool execution from command line
- **Log access**: Real-time log viewing

### Usage:
```bash
# Full CLI help
{server_name}-cli --help

# Start with custom settings
{server_name}-cli start --port 8080 --host 0.0.0.0
```""")
        
        if "automation" in features:
            docs.append("""## 🤖 Automation

Scheduled tasks and automated operations:

- **Health monitoring**: Automated health checks
- **Log management**: Automatic log rotation and cleanup
- **Metrics collection**: Scheduled metric gathering
- **Custom tasks**: Add your own scheduled operations

### Configuration:
```bash
# Configure intervals
{server_name}-cli config-set automation.health_check_interval 10m
{server_name}-cli config-set automation.log_cleanup_interval 7d
```""")
        
        if "monitoring" in features:
            docs.append("""## 📊 Monitoring

Comprehensive system and application monitoring:

- **System metrics**: CPU, memory, disk, network monitoring
- **Application metrics**: Request counts, response times, uptime
- **Feature metrics**: Monitor all enabled features
- **Export support**: JSON and Prometheus format export

### Configuration:
```bash
# Configure collection
{server_name}-cli config-set monitoring.collection_interval 30
{server_name}-cli config-set monitoring.export_enabled true
```""")
        
        return "\n\n".join(docs)
    
    def _enhance_env(self, base_env: str, request: EnhancedServerRequest) -> str:
        """Enhance .env.example with feature-specific variables"""
        
        env_vars = [
            f"# {request.name.upper()} Enhanced MCP Server Configuration",
            "",
            "# Core server settings",
            "HOST=localhost",
            f"PORT={request.port}",
            ""
        ]
        
        if "watchdog" in request.features:
            env_vars.extend([
                "# Watchdog monitoring settings",
                "WATCHDOG_ENABLED=true",
                "WATCH_PATHS=.,config/,src/",
                "WATCHDOG_RECURSIVE=true",
                ""
            ])
        
        if "automation" in request.features:
            env_vars.extend([
                "# Automation settings",
                "AUTOMATION_ENABLED=true", 
                "HEALTH_CHECK_INTERVAL=5m",
                "LOG_CLEANUP_INTERVAL=24h",
                "METRICS_COLLECTION_INTERVAL=30s",
                ""
            ])
        
        if "monitoring" in request.features:
            env_vars.extend([
                "# Monitoring settings",
                "MONITORING_ENABLED=true",
                "METRICS_COLLECTION_INTERVAL=30",
                "METRICS_RETENTION_COUNT=1000",
                "METRICS_EXPORT_ENABLED=false",
                "METRICS_EXPORT_FORMAT=json",
                ""
            ])
        
        if "cli" in request.features:
            env_vars.extend([
                "# CLI settings",
                "CLI_ENABLED=true",
                ""
            ])
        
        # Add custom environment variables
        if request.environment:
            env_vars.extend([
                "# Custom environment variables",
                *[f"{k}={v}" for k, v in request.environment.items()],
                ""
            ])
        
        return "\n".join(env_vars)
    
    def _generate_enhanced_docker_compose(self, request: EnhancedServerRequest) -> str:
        """Generate enhanced docker-compose.yml with all features"""
        
        services = f'''version: '3.8'

services:
  {request.name}:
    build: .
    ports:
      - "{request.port}:{request.port}"
    environment:
      - HOST=0.0.0.0
      - PORT={request.port}
      - WATCHDOG_ENABLED=true
      - AUTOMATION_ENABLED=true
      - MONITORING_ENABLED=true
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./config:/app/config
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:{request.port}/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - {request.name}-network'''
        
        # Add monitoring stack if monitoring is enabled
        if "monitoring" in request.features:
            services += f'''

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
    networks:
      - {request.name}-network

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    volumes:
      - grafana_data:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    networks:
      - {request.name}-network'''
        
        services += f'''

networks:
  {request.name}-network:
    driver: bridge

volumes:
  data:
  logs:'''
        
        if "monitoring" in request.features:
            services += '''
  prometheus_data:
  grafana_data:'''
        
        return services
    
    def process_claude_form(self, form_data: CrafterFormData) -> Dict[str, Any]:
        """Process a form submission from Claude"""
        logger.info(f"Processing Claude form: {form_data.form_type}")
        
        if form_data.form_type == "server_generation":
            return self._process_server_generation_form(form_data)
        elif form_data.form_type == "enhancement":
            return self._process_enhancement_form(form_data)
        elif form_data.form_type == "orchestration":
            return self._process_orchestration_form(form_data)
        else:
            return {
                "status": "error",
                "message": f"Unknown form type: {form_data.form_type}"
            }
    
    def _process_server_generation_form(self, form_data: CrafterFormData) -> Dict[str, Any]:
        """Process server generation form from Claude"""
        try:
            req_data = form_data.requirements
            
            # Convert form data to enhanced request
            request = EnhancedServerRequest(
                name=req_data.get("name", "claude-generated-server"),
                template=req_data.get("template", "python-fastmcp"),
                description=req_data.get("description", "Server generated from Claude form"),
                port=req_data.get("port", 8055),
                features=req_data.get("features", ["cli", "monitoring"]),
                dependencies=req_data.get("dependencies", []),
                environment=req_data.get("environment", {}),
                path=req_data.get("path")
            )
            
            # Generate the server
            files = self.generate_enhanced_server(request)
            
            # Create the server directory and files
            server_path = Path.home() / f"mcp-{request.name}"
            if server_path.exists():
                return {
                    "status": "error",
                    "message": f"Server directory already exists: {server_path}"
                }
            
            server_path.mkdir(parents=True)
            created_files = []
            
            for file_path, content in files.items():
                full_path = server_path / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(content)
                created_files.append(str(full_path))
            
            # Add to MCP configuration
            self._add_to_config(request.name, str(server_path), request.port, request.template)
            
            return {
                "status": "success",
                "server_name": request.name,
                "path": str(server_path),
                "features": request.features,
                "files_created": len(created_files),
                "next_steps": [
                    f"cd {server_path}",
                    "pip install -e .",
                    "cp .env.example .env",
                    f"{request.name}-cli start"
                ]
            }
            
        except Exception as e:
            logger.error(f"Error processing server generation form: {e}")
            return {
                "status": "error", 
                "message": str(e)
            }
    
    def _process_enhancement_form(self, form_data: CrafterFormData) -> Dict[str, Any]:
        """Process server enhancement form"""
        # This would implement enhancement of existing servers
        return {
            "status": "success",
            "message": "Enhancement form processed (implementation pending)"
        }
    
    def _process_orchestration_form(self, form_data: CrafterFormData) -> Dict[str, Any]:
        """Process orchestration form for multiple server tasks"""
        # This would implement orchestration of multiple operations
        return {
            "status": "success", 
            "message": "Orchestration form processed (implementation pending)"
        }

def main():
    """CLI interface for the Enhanced MCP Crafter"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Enhanced MCP Server Generator with advanced features",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Enhanced Features Available:
  watchdog    - File system monitoring
  cli        - Command-line interface
  automation - Scheduled tasks and automation
  monitoring - System and application monitoring

Examples:
  python enhanced_mcp_crafter.py weather-server --template python-fastmcp \\
    --port 8055 --features watchdog cli monitoring
  
  python enhanced_mcp_crafter.py file-manager --template typescript-node \\
    --port 8056 --features watchdog automation
        """
    )
    
    parser.add_argument("name", help="Server name (e.g., 'weather-server')")
    parser.add_argument(
        "--template",
        "-t",
        choices=["python-fastmcp", "typescript-node", "minimal-python"],
        default="python-fastmcp",
        help="Base template to use (default: python-fastmcp)"
    )
    parser.add_argument(
        "--port",
        "-p",
        type=int,
        default=8055,
        help="Port number (default: 8055)"
    )
    parser.add_argument("--description", "-d", help="Server description")
    parser.add_argument("--path", help="Custom installation path")
    parser.add_argument(
        "--features",
        nargs="+",
        choices=["watchdog", "cli", "automation", "monitoring"],
        default=["cli"],
        help="Features to include (default: cli)"
    )
    parser.add_argument(
        "--dependencies",
        nargs="+",
        default=[],
        help="Additional dependencies to include"
    )
    parser.add_argument(
        "--env",
        action="append",
        help="Environment variables (format: KEY=VALUE)"
    )
    
    args = parser.parse_args()
    
    # Parse environment variables
    environment = {}
    if args.env:
        for env_var in args.env:
            if "=" in env_var:
                key, value = env_var.split("=", 1)
                environment[key] = value
    
    # Create enhanced request
    request = EnhancedServerRequest(
        name=args.name,
        template=args.template,
        description=args.description or f"Enhanced MCP server for {args.name}",
        port=args.port,
        features=args.features,
        dependencies=args.dependencies,
        environment=environment,
        path=args.path
    )
    
    # Generate the enhanced server
    crafter = EnhancedMCPCrafter()
    
    try:
        files = crafter.generate_enhanced_server(request)
        
        # Create server directory
        if request.path:
            server_path = Path(request.path).expanduser()
        else:
            server_path = Path.home() / f"mcp-{request.name}"
        
        if server_path.exists():
            print(f"❌ Directory {server_path} already exists")
            return 1
        
        # Create files
        server_path.mkdir(parents=True)
        created_files = []
        
        for file_path, content in files.items():
            full_path = server_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)
            created_files.append(str(full_path))
        
        # Add to MCP configuration
        crafter._add_to_config(request.name, str(server_path), request.port, request.template)
        
        print(f"✅ Enhanced MCP server '{request.name}' created successfully!")
        print(f"📁 Location: {server_path}")
        print(f"🎯 Features: {', '.join(request.features)}")
        print(f"📦 Files created: {len(created_files)}")
        print()
        print("🚀 Next steps:")
        print(f"  1. cd {server_path}")
        print("  2. pip install -e .")
        print("  3. cp .env.example .env")
        print("  4. Edit .env with your configuration")
        print(f"  5. {request.name}-cli start")
        print()
        print("📖 For help:")
        print(f"  {request.name}-cli --help")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error creating enhanced server: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())