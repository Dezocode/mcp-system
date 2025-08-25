# MCP Orchestrator Server

A comprehensive MCP server that provides Windows Docker integration, CLI command resolution, and watchdog monitoring capabilities.

## Features

### 🐳 Windows Docker Integration
- WSL2 environment detection and management
- Docker Desktop integration and control
- Container lifecycle management
- Docker CLI command execution with enhanced capabilities
- Windows-specific Docker deployment automation

### 🔧 CLI Command Resolution
- MCP system setup CLI integration
- Docker command orchestration
- Cross-platform command execution
- Environment-aware command routing
- Comprehensive command validation and execution

### 👁️ Watchdog Monitoring
- Real-time file system monitoring
- Container health monitoring
- Service status tracking
- Automated recovery mechanisms
- Performance metrics collection

### 🌐 Cross-Platform Support
- Windows 10/11 with WSL2
- Docker Desktop integration
- Linux container management
- Environment-specific optimizations

## Tools Available

1. **docker_operation** - Execute Docker CLI commands with enhanced capabilities
2. **environment_setup** - Setup and configure MCP system environment
3. **container_management** - Manage Docker containers lifecycle
4. **watchdog_monitoring** - Monitor file systems and services
5. **cli_resolution** - Resolve and execute CLI commands
6. **windows_integration** - Windows-specific Docker operations
7. **health_monitoring** - Comprehensive system health checks
8. **deployment_orchestration** - Automate deployment workflows

## Installation

```bash
cd mcp-tools/orchestrator
pip install -e .
```

## Usage

### As MCP Server
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

### Direct CLI Usage
```bash
# Start the orchestrator server
orchestrator

# Environment setup
orchestrator setup

# Docker operations
orchestrator docker --operation status
orchestrator docker --operation deploy --stack production
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