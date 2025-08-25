# MCP Orchestrator Server

A comprehensive MCP server that provides enhanced Docker integration with launch capabilities, AI steering via React/JSON framework communication, and cross-platform resolution for Windows/Linux/WSL/Mac.

## Features

### 🚀 Enhanced Docker Integration
- **Docker Launch Capabilities**: Start Docker Desktop on Windows, Docker.app on macOS, or Docker daemon on Linux
- **Cross-Platform Support**: Automatic platform detection and Docker management for Windows/Linux/WSL/Mac
- **WSL2 Environment Detection**: Advanced WSL integration and management
- **Container Lifecycle Management**: Complete Docker container orchestration
- **Docker CLI Enhancement**: Execute Docker commands with enhanced capabilities

### 🤖 AI Steering & React/JSON Framework Communication
- **FastAPI Web Interface**: RESTful API for AI systems to control orchestrator
- **WebSocket Real-time Updates**: Live status monitoring and configuration changes
- **Dynamic Configuration**: Update orchestrator settings via API calls
- **CORS Support**: Ready for React frontend integration
- **JSON Protocol**: Complete JSON-based communication framework

### 🔧 Enhanced CLI Command Resolution
- **MCP System Setup CLI Integration**: Full integration with existing mcp-system tools
- **Platform-Aware Routing**: Commands routed based on detected environment
- **Docker Command Orchestration**: Specialized handling for Docker operations
- **Security Validation**: Prevents execution of dangerous commands in safe mode

### 👁️ Advanced Watchdog Monitoring
- **Real-time File System Monitoring**: Professional-grade Watchdog library integration
- **Container Health Monitoring**: Track Docker containers and system services
- **Performance Metrics**: Monitor CPU, memory, and disk usage
- **Automated Recovery**: Detect and respond to system issues

### 🌐 Cross-Platform Resolution
- **Windows Support**: Docker Desktop launch, WSL2 integration, PowerShell commands
- **macOS Support**: Docker.app launch, Homebrew detection, native command execution
- **Linux Support**: Docker daemon management, systemctl integration, service control
- **WSL Environment**: Enhanced WSL detection and Docker integration

## Tools Available

1. **docker_operation** - Execute Docker CLI commands with enhanced capabilities
2. **docker_launch** - Launch Docker Desktop or Docker daemon on any platform
3. **environment_setup** - Setup and configure MCP system environment
4. **container_management** - Manage Docker containers lifecycle
5. **watchdog_monitoring** - Monitor file systems and services
6. **cli_resolution** - Resolve and execute CLI commands
7. **windows_integration** - Windows-specific Docker operations
8. **health_monitoring** - Comprehensive system health checks
9. **deployment_orchestration** - Automate deployment workflows

## Installation

```bash
cd mcp-tools/orchestrator
pip install -e .
```

## Usage

### As MCP Server (Traditional Mode)
Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "orchestrator": {
      "command": "orchestrator",
      "args": []
    }
  }
}
```

### With Web API for AI Steering
Start with FastAPI web interface enabled:

```bash
# Start orchestrator with web API for AI steering
orchestrator --enable-web-api --web-port 8000

# Or with custom host/port
orchestrator --enable-web-api --web-host 0.0.0.0 --web-port 9000
```

### Docker Launch Examples

```bash
# Launch Docker via MCP tool
{
  "tool": "docker_launch",
  "platform": "auto",
  "wait_for_ready": true,
  "timeout": 60
}

# Platform-specific launch
{
  "tool": "docker_launch", 
  "platform": "windows",
  "wait_for_ready": true
}
```

### AI Steering via Web API

```bash
# Check status
curl http://localhost:8000/api/status

# Launch Docker via API
curl -X POST http://localhost:8000/api/docker/launch \
  -H "Content-Type: application/json" \
  -d '{"platform": "auto", "wait_for_ready": true}'

# Get platform capabilities
curl http://localhost:8000/api/platforms/detect

# Update configuration dynamically
curl -X POST http://localhost:8000/api/config/update \
  -H "Content-Type: application/json" \
  -d '{"environment": {"DOCKER_TIMEOUT": "60"}, "orchestrator": {"workspace_root": "/new/path"}}'
```

### WebSocket Real-time Updates

```javascript
// Connect to WebSocket for real-time updates
const ws = new WebSocket('ws://localhost:8000/ws/updates');

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Status update:', data);
};
```

### Direct CLI Usage
```bash
# Start the orchestrator server (MCP mode)
orchestrator

# Start with web API enabled
orchestrator --enable-web-api

# Show platform detection information
orchestrator --platform-info

# Show help with new features
orchestrator --help-info
```

## Configuration

Create a `.env` file:

```env
# Docker Configuration
DOCKER_HOST=unix:///var/run/docker.sock
DOCKER_TIMEOUT=30

# Windows WSL Configuration  
WSL_DISTRO=Ubuntu
WSL_USER=runner

# Web API Configuration
WEB_SERVER_ENABLED=false
WEB_SERVER_HOST=0.0.0.0
WEB_SERVER_PORT=8000

# Monitoring Configuration
WATCHDOG_ENABLED=true
HEALTH_CHECK_INTERVAL=30

# MCP System Configuration
MCP_WORKSPACE_ROOT=/home/runner/work/mcp-system/mcp-system
MCP_SESSION_DIR=./pipeline-sessions
```

## Architecture

The orchestrator integrates several key systems:

- **Environment Detection**: Automatically detects Windows/WSL/Docker environments
- **Docker Integration**: Provides full Docker Desktop and CLI integration
- **Watchdog System**: Real-time monitoring using the enhanced watchdog from claude_quality_patcher.py
- **CLI Resolution**: Command routing and execution with environment awareness
- **Health Monitoring**: Comprehensive system and container health checks

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Code formatting
black src/
isort src/

# Type checking
mypy src/
```

## Contributing

This server follows the MCP Tools standards established in the mcp-system repository. Please ensure all changes maintain compatibility with the existing infrastructure.