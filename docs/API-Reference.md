# MCP System API Reference

This document provides comprehensive API reference for all MCP System components.

## 🚀 Command Line Interface

### Universal Commands

#### `mcp-universal`

**Description**: Universal MCP launcher that works in any project directory

**Usage**: `mcp-universal [command] [options]`

**Commands**:

##### `mcp-universal status`
Check status of all MCP servers
```bash
mcp-universal status
# Output: Server status table with health information
```

##### `mcp-universal list`
List all available MCP servers
```bash
mcp-universal list
mcp-universal list --format json
mcp-universal list --template python-fastmcp
```

##### `mcp-universal create <name> [options]`
Create new MCP server from template
```bash
mcp-universal create my-server --template python-fastmcp --port 8055
mcp-universal create my-server --template typescript-node --port 8056
mcp-universal create my-server --template minimal-python --port 8057
```

**Options**:
- `--template <template>`: Server template (python-fastmcp, typescript-node, minimal-python)
- `--port <port>`: Server port (default: auto-assigned)
- `--host <host>`: Server host (default: localhost)
- `--directory <dir>`: Target directory (default: ~/mcp-{name})

##### `mcp-universal test <server> [options]`
Test MCP servers
```bash
mcp-universal test my-server
mcp-universal test all
mcp-universal test my-server --start --verbose
```

**Options**:
- `--start`: Start server before testing
- `--verbose`: Detailed output
- `--report <file>`: Save report to file

##### `mcp-universal upgrade <command> [options]`
Manage server upgrades
```bash
mcp-universal upgrade wizard my-server
mcp-universal upgrade suggest "I need auth and caching" my-server
mcp-universal upgrade install my-server authentication caching-redis
mcp-universal upgrade rollback my-server authentication
mcp-universal upgrade list-modules
```

##### `mcp-universal bridge <command>`
Manage Claude Code integration
```bash
mcp-universal bridge init
mcp-universal bridge status
mcp-universal bridge auto-init
```

##### `mcp-universal discover <command>`
Environment discovery and analysis
```bash
mcp-universal discover analyze
mcp-universal discover report
mcp-universal discover auto-init
```

---

### Project Commands

#### `mcp-init-project`

**Description**: Initialize MCP integration for current project

**Usage**: `mcp-init-project [options]`

**Options**:
- `--force`: Force initialization even if already configured
- `--template <template>`: Override auto-detected template
- `--verbose`: Detailed output

**Examples**:
```bash
# Auto-detect and initialize
mcp-init-project

# Force specific template
mcp-init-project --template python-fastmcp --force
```

---

## 🐍 Python API

### Core Classes

#### `MCPSystemInstaller`

**Module**: `src.install_mcp_system`

**Description**: Main installer class for MCP System

```python
from src.install_mcp_system import MCPSystemInstaller

installer = MCPSystemInstaller()
success = installer.run_installation()
```

**Methods**:

##### `check_prerequisites() -> bool`
Check if system prerequisites are met
```python
if installer.check_prerequisites():
    print("Prerequisites OK")
```

##### `create_directories()`
Create necessary system directories
```python
installer.create_directories()
```

##### `package_components()`
Package all MCP components
```python
installer.package_components()
```

##### `create_universal_launcher()`
Create universal MCP launcher
```python
installer.create_universal_launcher()
```

##### `run_installation() -> bool`
Run complete installation process
```python
success = installer.run_installation()
```

---

#### `ClaudeCodeMCPBridge`

**Module**: `src.claude_code_mcp_bridge`

**Description**: Bridge for seamless Claude Code CLI integration

```python
from src.claude_code_mcp_bridge import ClaudeCodeMCPBridge

bridge = ClaudeCodeMCPBridge()
success = bridge.setup_permissionless_integration()
```

**Methods**:

##### `detect_claude_code_usage() -> bool`
Detect if Claude Code is being used
```python
if bridge.detect_claude_code_usage():
    print("Claude Code detected")
```

##### `detect_project_type() -> List[str]`
Detect current project type(s)
```python
project_types = bridge.detect_project_type()
# Returns: ['python', 'git', 'claude']
```

##### `create_safe_mcp_integration() -> Dict[str, Any]`
Create safe MCP integration configuration
```python
config = bridge.create_safe_mcp_integration()
```

##### `merge_claude_config(new_config: Dict[str, Any]) -> bool`
Safely merge MCP config with existing Claude configuration
```python
success = bridge.merge_claude_config(new_config)
```

##### `setup_permissionless_integration() -> bool`
Setup complete permissionless integration
```python
success = bridge.setup_permissionless_integration()
```

##### `check_integration_status() -> Dict[str, Any]`
Check current integration status
```python
status = bridge.check_integration_status()
print(f"Claude detected: {status['claude_detected']}")
print(f"MCP installed: {status['mcp_system_installed']}")
```

---

#### `MCPAutoDiscovery`

**Module**: `src.auto_discovery_system`

**Description**: Intelligent environment detection and analysis

```python
from src.auto_discovery_system import MCPAutoDiscovery

discovery = MCPAutoDiscovery()
analysis = discovery.analyze_environment()
```

**Methods**:

##### `scan_directory(path: Path, max_depth: int = 3) -> Dict[str, Any]`
Recursively scan directory for environment indicators
```python
results = discovery.scan_directory(Path("/path/to/project"))
```

##### `detect_project_type() -> List[str]`
Detect current project type(s)
```python
types = discovery.detect_project_type()
# Returns: ['python', 'nodejs', 'docker']
```

##### `analyze_environment(path: Path = None) -> Dict[str, Any]`
Perform comprehensive environment analysis
```python
analysis = discovery.analyze_environment()
print(f"Detected: {analysis['detected_environments']}")
print(f"Suggested: {analysis['suggested_servers']}")
```

##### `auto_initialize_project(analysis: Dict[str, Any] = None) -> bool`
Automatically initialize MCP for current project
```python
success = discovery.auto_initialize_project()
```

##### `create_environment_report(analysis: Dict[str, Any]) -> str`
Create detailed environment analysis report
```python
report = discovery.create_environment_report(analysis)
print(report)
```

---

### Configuration Classes

#### `ServerConfig`

**Description**: Server configuration management

```python
from src.config import ServerConfig

config = ServerConfig("my-server")
config.host = "localhost"
config.port = 8055
config.template = "python-fastmcp"
config.save()
```

**Attributes**:
- `name: str` - Server name
- `host: str` - Server host
- `port: int` - Server port
- `template: str` - Server template
- `enabled: bool` - Server enabled status
- `auto_start: bool` - Auto-start on system boot

**Methods**:
- `load()` - Load configuration from file
- `save()` - Save configuration to file
- `validate()` - Validate configuration
- `to_dict()` - Convert to dictionary

---

#### `SystemConfig`

**Description**: System-wide configuration management

```python
from src.config import SystemConfig

config = SystemConfig()
config.auto_discovery = True
config.safe_mode = True
config.save()
```

**Attributes**:
- `auto_discovery: bool` - Enable auto-discovery
- `safe_mode: bool` - Enable safe mode
- `default_template: str` - Default server template
- `default_port_start: int` - Starting port for auto-assignment

---

## 🔧 Upgrade System API

### `MCPUpgrader`

**Module**: `src.mcp_upgrader`

**Description**: Modular server upgrade system

```python
from src.mcp_upgrader import MCPUpgrader

upgrader = MCPUpgrader()
analysis = upgrader.analyze_server("my-server")
```

**Methods**:

##### `analyze_server(server_name: str) -> Dict[str, Any]`
Analyze server for upgrade opportunities
```python
analysis = upgrader.analyze_server("my-server")
print(f"Installed modules: {analysis['installed_modules']}")
print(f"Recommended: {analysis['recommended_upgrades']}")
```

##### `suggest_upgrades_for_prompt(prompt: str, server_name: str = None) -> List[str]`
Suggest upgrades based on natural language prompt
```python
suggestions = upgrader.suggest_upgrades_for_prompt(
    "I need authentication and caching", 
    "my-server"
)
```

##### `apply_upgrade_module(server_name: str, module_id: str, dry_run: bool = False) -> bool`
Apply upgrade module to server
```python
# Dry run first
success = upgrader.apply_upgrade_module("my-server", "authentication", dry_run=True)

# Apply for real
if success:
    upgrader.apply_upgrade_module("my-server", "authentication")
```

##### `rollback_module(server_name: str, module_id: str) -> bool`
Rollback upgrade module
```python
success = upgrader.rollback_module("my-server", "authentication")
```

##### `list_available_modules(template_filter: str = None) -> List[Dict[str, Any]]`
List available upgrade modules
```python
modules = upgrader.list_available_modules("python-fastmcp")
for module in modules:
    print(f"{module['id']}: {module['description']}")
```

---

### Upgrade Modules

#### `UpgradeModule`

**Description**: Base class for upgrade modules

```python
from src.upgrade_modules import UpgradeModule

class CustomModule(UpgradeModule):
    def __init__(self):
        super().__init__(
            module_id="custom-feature",
            name="Custom Feature",
            description="Adds custom functionality",
            version="1.0.0",
            compatibility=["python-fastmcp"]
        )
    
    def install(self, server_info: ServerInfo) -> bool:
        # Installation logic
        return True
    
    def rollback(self, server_info: ServerInfo) -> bool:
        # Rollback logic
        return True
```

**Methods**:
- `install(server_info: ServerInfo) -> bool` - Install module
- `rollback(server_info: ServerInfo) -> bool` - Rollback module
- `validate_compatibility(server_info: ServerInfo) -> bool` - Check compatibility
- `get_dependencies() -> List[str]` - Get required dependencies

---

## 🔍 Discovery System API

### Environment Detection

#### `detect_project_environment(path: Path) -> Dict[str, Any]`

**Description**: Detect project environment and suggest configuration

```python
from src.discovery import detect_project_environment

env = detect_project_environment(Path("/path/to/project"))
print(f"Type: {env['type']}")
print(f"Confidence: {env['confidence']}")
print(f"Suggested servers: {env['suggested_servers']}")
```

**Returns**:
```python
{
    "type": "python",
    "confidence": 0.95,
    "indicators": ["pyproject.toml", "requirements.txt"],
    "suggested_servers": ["python-tools", "testing-tools"],
    "recommended_actions": [
        {
            "action": "create_server",
            "description": "Create Python tools server",
            "command": "mcp-universal create python-tools --template python-fastmcp"
        }
    ]
}
```

---

### Analysis Functions

#### `analyze_file_patterns(path: Path) -> Dict[str, int]`

**Description**: Analyze file patterns in directory

```python
from src.discovery import analyze_file_patterns

patterns = analyze_file_patterns(Path("/path/to/project"))
print(f"Python files: {patterns.get('python', 0)}")
print(f"JavaScript files: {patterns.get('javascript', 0)}")
```

#### `analyze_dependencies(path: Path) -> Dict[str, List[str]]`

**Description**: Analyze project dependencies

```python
from src.discovery import analyze_dependencies

deps = analyze_dependencies(Path("/path/to/project"))
print(f"Python deps: {deps.get('python', [])}")
print(f"Node.js deps: {deps.get('nodejs', [])}")
```

---

## 🧪 Testing API

### `MCPTestFramework`

**Module**: `src.mcp_test_framework`

**Description**: Comprehensive testing framework for MCP servers

```python
from src.mcp_test_framework import MCPTestFramework

tester = MCPTestFramework()
results = tester.test_server("my-server")
```

**Methods**:

##### `test_server(server_name: str, start_server: bool = False) -> Dict[str, Any]`
Test specific MCP server
```python
results = tester.test_server("my-server", start_server=True)
print(f"Passed: {results['passed']}")
print(f"Failed: {results['failed']}")
```

##### `test_all_servers() -> Dict[str, Any]`
Test all available servers
```python
results = tester.test_all_servers()
for server, result in results.items():
    print(f"{server}: {'✅' if result['success'] else '❌'}")
```

##### `health_check(server_name: str) -> bool`
Perform health check on server
```python
healthy = tester.health_check("my-server")
```

##### `generate_report(results: Dict[str, Any], output_file: str = None) -> str`
Generate test report
```python
report = tester.generate_report(results, "test_report.json")
```

---

## 🔒 Security API

### Permission Management

#### `check_permissions(path: Path) -> Dict[str, bool]`

**Description**: Check file system permissions

```python
from src.security import check_permissions

perms = check_permissions(Path("/target/directory"))
print(f"Read: {perms['read']}")
print(f"Write: {perms['write']}")
print(f"Execute: {perms['execute']}")
```

#### `safe_file_operation(operation: str, source: Path, target: Path) -> bool`

**Description**: Perform safe file operations with backup

```python
from src.security import safe_file_operation

success = safe_file_operation("copy", source_file, target_file)
```

---

## 📊 Monitoring API

### Metrics Collection

#### `collect_system_metrics() -> Dict[str, Any]`

**Description**: Collect system performance metrics

```python
from src.monitoring import collect_system_metrics

metrics = collect_system_metrics()
print(f"CPU usage: {metrics['cpu_percent']}%")
print(f"Memory usage: {metrics['memory_percent']}%")
print(f"Active servers: {metrics['active_servers']}")
```

#### `collect_server_metrics(server_name: str) -> Dict[str, Any]`

**Description**: Collect metrics for specific server

```python
from src.monitoring import collect_server_metrics

metrics = collect_server_metrics("my-server")
print(f"Requests: {metrics['request_count']}")
print(f"Response time: {metrics['avg_response_time']}ms")
print(f"Error rate: {metrics['error_rate']}%")
```

---

## 🔧 Utilities API

### Path Management

#### `get_system_paths() -> Dict[str, Path]`

**Description**: Get standard system paths

```python
from src.utils import get_system_paths

paths = get_system_paths()
print(f"System dir: {paths['system']}")
print(f"Components: {paths['components']}")
print(f"Docs: {paths['docs']}")
```

### Configuration Helpers

#### `load_config(config_type: str) -> Dict[str, Any]`

**Description**: Load configuration file

```python
from src.utils import load_config

config = load_config("system")
print(f"Auto discovery: {config['auto_discovery']}")
```

#### `save_config(config_type: str, data: Dict[str, Any]) -> bool`

**Description**: Save configuration file

```python
from src.utils import save_config

config = {"auto_discovery": True, "safe_mode": True}
success = save_config("system", config)
```

---

## 🌐 HTTP API (Future)

### REST Endpoints

**Note**: HTTP API is planned for future releases

#### `GET /api/v1/servers`
List all servers
```json
{
  "servers": [
    {
      "name": "my-server",
      "status": "running",
      "port": 8055,
      "template": "python-fastmcp"
    }
  ]
}
```

#### `POST /api/v1/servers`
Create new server
```json
{
  "name": "new-server",
  "template": "python-fastmcp",
  "port": 8056
}
```

#### `GET /api/v1/servers/{name}/status`
Get server status
```json
{
  "name": "my-server",
  "status": "running",
  "health": "healthy",
  "uptime": 3600,
  "requests": 1250
}
```

---

## 📚 Type Definitions

### Common Types

```python
from typing import Dict, List, Optional, Any, Union
from pathlib import Path

# Server information
ServerInfo = Dict[str, Any]

# Environment analysis result
EnvironmentAnalysis = Dict[str, Any]

# Test results
TestResults = Dict[str, Any]

# Configuration data
ConfigData = Dict[str, Any]

# Module metadata
ModuleMetadata = Dict[str, Any]
```

### Enums

```python
from enum import Enum

class ServerStatus(Enum):
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"

class ServerTemplate(Enum):
    PYTHON_FASTMCP = "python-fastmcp"
    TYPESCRIPT_NODE = "typescript-node"
    MINIMAL_PYTHON = "minimal-python"

class UpgradeModuleStatus(Enum):
    AVAILABLE = "available"
    INSTALLED = "installed"
    INCOMPATIBLE = "incompatible"
    CONFLICTED = "conflicted"
```

---

## 🚨 Error Handling

### Exception Classes

```python
class MCPSystemError(Exception):
    """Base exception for MCP System"""
    pass

class InstallationError(MCPSystemError):
    """Installation-related errors"""
    pass

class ConfigurationError(MCPSystemError):
    """Configuration-related errors"""
    pass

class ServerError(MCPSystemError):
    """Server-related errors"""
    pass

class UpgradeError(MCPSystemError):
    """Upgrade-related errors"""
    pass

class DiscoveryError(MCPSystemError):
    """Discovery-related errors"""
    pass
```

### Error Codes

```python
from enum import IntEnum

class ErrorCode(IntEnum):
    SUCCESS = 0
    GENERAL_ERROR = 1
    INSTALLATION_FAILED = 10
    CONFIG_ERROR = 20
    SERVER_ERROR = 30
    UPGRADE_ERROR = 40
    DISCOVERY_ERROR = 50
    PERMISSION_ERROR = 60
```

---

## 📝 Examples

### Complete Server Creation Workflow

```python
#!/usr/bin/env python3
"""
Complete example of creating and managing an MCP server
"""

from src.mcp_create_server import MCPServerCreator
from src.mcp_test_framework import MCPTestFramework
from src.mcp_upgrader import MCPUpgrader

def create_and_setup_server():
    # Create server
    creator = MCPServerCreator()
    success = creator.create_server(
        name="weather-api",
        template="python-fastmcp",
        port=8055,
        description="Weather API tools"
    )
    
    if not success:
        print("❌ Server creation failed")
        return False
    
    # Test server
    tester = MCPTestFramework()
    results = tester.test_server("weather-api", start_server=True)
    
    if not results['success']:
        print("❌ Server tests failed")
        return False
    
    # Add upgrades
    upgrader = MCPUpgrader()
    
    # Add authentication
    upgrader.apply_upgrade_module("weather-api", "authentication")
    
    # Add caching
    upgrader.apply_upgrade_module("weather-api", "caching-redis")
    
    # Add monitoring
    upgrader.apply_upgrade_module("weather-api", "monitoring-metrics")
    
    print("✅ Server created and configured successfully")
    return True

if __name__ == "__main__":
    create_and_setup_server()
```

### Environment Discovery Workflow

```python
#!/usr/bin/env python3
"""
Complete example of environment discovery and auto-initialization
"""

from src.auto_discovery_system import MCPAutoDiscovery
from src.claude_code_mcp_bridge import ClaudeCodeMCPBridge
from pathlib import Path

def discover_and_initialize(project_path: str):
    project = Path(project_path)
    
    # Analyze environment
    discovery = MCPAutoDiscovery()
    discovery.current_dir = project
    
    analysis = discovery.analyze_environment(project)
    
    print(f"🔍 Analysis Results:")
    print(f"  Detected environments: {analysis['detected_environments']}")
    print(f"  Suggested servers: {analysis['suggested_servers']}")
    print(f"  Confidence scores: {analysis['confidence_scores']}")
    
    # Auto-initialize if Claude project detected
    if "claude_code" in analysis["detected_environments"]:
        bridge = ClaudeCodeMCPBridge()
        bridge.current_project = project
        
        success = bridge.setup_permissionless_integration()
        if success:
            print("✅ Claude Code integration configured")
        else:
            print("❌ Claude Code integration failed")
    
    # Auto-initialize MCP based on analysis
    success = discovery.auto_initialize_project(analysis)
    if success:
        print("✅ MCP system initialized for project")
    else:
        print("❌ MCP initialization failed")
    
    # Generate report
    report = discovery.create_environment_report(analysis)
    report_file = project / ".mcp" / "discovery-report.md"
    report_file.write_text(report)
    print(f"📊 Report saved to {report_file}")

if __name__ == "__main__":
    discover_and_initialize("/path/to/your/project")
```

---

This API reference provides comprehensive documentation for all MCP System components. For more examples and tutorials, see the [Complete Documentation](MCP-Complete-Documentation.md).