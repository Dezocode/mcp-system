# MCP System: Universal Server Management & Claude Code Integration

<div align="center">

![MCP System](https://img.shields.io/badge/MCP-System-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8+-green?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

**Complete Model Context Protocol (MCP) server management system with permissionless Claude Code CLI integration**

*Use this as a foundation to build and manage MCP servers, or give this as an example to an AI coding assistant for structure and best practices!*

</div>

## 🌟 Overview

This project provides a **complete MCP server management ecosystem** that enables seamless creation, testing, upgrading, and integration of MCP servers with Claude Code CLI. It includes intelligent auto-discovery, permissionless integration, and a modular upgrade system.

The implementation follows Anthropic's best practices and provides a comprehensive template for building production-ready MCP servers with advanced management capabilities.

## ✨ Features

### 🚀 **Universal Management**
- **`mcp-universal`**: Works in any project directory with auto-detection
- **`mcp-init-project`**: Automatically initializes MCP for current project
- **Template system**: Python FastMCP, TypeScript Node.js, Minimal Python
- **Testing framework**: Comprehensive server testing and validation

### 🧠 **Intelligent Auto-Discovery**
- Detects project types: Python, Node.js, Rust, Go, Docker, Claude projects
- Analyzes environment and suggests appropriate MCP servers
- Generates detailed discovery reports with recommendations

### 🔗 **Permissionless Claude Code Integration**
- Automatically detects Claude Code usage in any project
- Safe merging with existing Claude Desktop configurations
- No special permissions or complex setup required
- Works seamlessly across all project types

### ⚡ **Modular Upgrade System**
- **6 pre-built modules**: logging, authentication, caching, database, metrics, versioning
- **Custom module creation**: Build your own upgrade modules
- **Safety features**: Backups, dry-runs, rollbacks
- **Template compatibility**: Works across different server implementations

## 🛠️ Prerequisites

- **Python 3.8+** (Python 3.12+ recommended)
- **Git** (for repository management)
- **Node.js 18+** (for TypeScript templates)
- **Claude Code CLI** (for Claude integration)
- **Docker** (optional, for containerized servers)

## 🚀 Installation

### One-Click Installation (Recommended)

```bash
# Clone the repository
git clone https://github.com/dezocode/mcp-system.git
cd mcp-system

# Run one-click installer
chmod +x install.sh
./install.sh
```

### Manual Installation

```bash
# Clone and setup
git clone https://github.com/dezocode/mcp-system.git
cd mcp-system

# Install Python dependencies
pip install -r requirements.txt

# Run Python installer
python3 install-mcp-system.py

# Add to PATH (restart terminal after this)
export PATH="$HOME/bin:$PATH"
```

### Verification

```bash
# Verify installation
mcp-universal --help
mcp-init-project --help

# Check system status
mcp-universal bridge status
```

## 📋 Configuration

The system automatically configures itself, but you can customize:

### Environment Variables

Create `.env` file in your project directory:

```bash
# MCP System Configuration
MCP_SYSTEM_PATH="$HOME/.mcp-system"
MCP_AUTO_DISCOVERY=true
MCP_SAFE_MODE=true

# Default Server Settings
DEFAULT_HOST=localhost
DEFAULT_PORT_START=8050

# Claude Integration
CLAUDE_AUTO_INIT=true
CLAUDE_CONFIG_BACKUP=true
```

### Claude Configuration

The system automatically merges with your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "mcp-system": {
      "command": "mcp-universal",
      "args": ["router"],
      "env": {
        "MCP_SYSTEM_PATH": "/Users/you/.mcp-system",
        "MCP_AUTO_DISCOVERY": "true"
      }
    }
  }
}
```

## 🎯 Quick Start

### 1. Initialize Any Project

```bash
# Navigate to any project
cd /path/to/your/project

# Auto-detect and initialize
mcp-universal

# Or manually initialize
mcp-init-project
```

### 2. Create Your First Server

```bash
# For Python projects
mcp-universal create my-tools --template python-fastmcp --port 8055

# For Node.js projects  
mcp-universal create my-tools --template typescript-node --port 8056

# For minimal implementations
mcp-universal create my-tools --template minimal-python --port 8057
```

### 3. Test and Deploy

```bash
# Test the server
mcp-universal test my-tools --start

# Start for production
mcp-universal my-tools start

# Check status
mcp-universal status
```

### 4. Upgrade with New Features

```bash
# Interactive upgrade wizard
mcp-universal upgrade wizard my-tools

# Add specific capabilities
mcp-universal upgrade install my-tools authentication caching-redis

# Suggest upgrades from description
mcp-universal upgrade suggest "I need secure API with monitoring" my-tools
```

## 🏗️ Server Templates

### Python FastMCP Template

**Best for**: Full-featured Python servers with advanced capabilities

```python
from fastmcp import MCP

mcp = MCP()

@mcp.tool()
async def my_tool(param: str) -> str:
    """My custom MCP tool"""
    return f"Processed: {param}"

if __name__ == "__main__":
    mcp.run()
```

### TypeScript Node.js Template

**Best for**: Modern JavaScript/TypeScript implementations

```typescript
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';

const server = new McpServer({
  name: 'my-server',
  version: '1.0.0'
});

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [{
    name: 'my_tool',
    description: 'My custom tool',
    inputSchema: {
      type: 'object',
      properties: {
        param: { type: 'string' }
      }
    }
  }]
}));

const transport = new StdioServerTransport();
server.connect(transport);
```

### Minimal Python Template

**Best for**: Lightweight, simple implementations

```python
import json
import sys

def handle_request(request):
    if request['method'] == 'tools/list':
        return {
            'tools': [{
                'name': 'my_tool',
                'description': 'Simple tool',
                'inputSchema': {'type': 'object'}
            }]
        }
    return {'error': 'Unknown method'}

if __name__ == "__main__":
    for line in sys.stdin:
        request = json.loads(line)
        response = handle_request(request)
        print(json.dumps(response))
```

## 🔧 Available Commands

### Universal Commands (Work Anywhere)

```bash
# System management
mcp-universal status                           # Check all servers
mcp-universal list                            # List available servers
mcp-universal all start                       # Start all servers
mcp-universal all stop                        # Stop all servers

# Server creation
mcp-universal create <name> [options]         # Create new server
mcp-universal create <name> --template python-fastmcp --port 8055

# Testing
mcp-universal test <server>                   # Test specific server
mcp-universal test all                        # Test all servers
mcp-universal test <server> --start           # Start and test

# Upgrades
mcp-universal upgrade wizard <server>         # Interactive upgrade
mcp-universal upgrade suggest "<desc>" <srv>  # Suggest from description
mcp-universal upgrade install <srv> <modules> # Install modules
mcp-universal upgrade rollback <srv> <module> # Rollback upgrade

# Claude integration
mcp-universal bridge init                     # Initialize Claude bridge
mcp-universal bridge status                   # Check integration status
mcp-universal bridge auto-init                # Auto-initialize if detected
```

### Project-Specific Commands

```bash
# Available after running mcp-init-project
./mcp <server> start                          # Start project server
./mcp <server> stop                           # Stop project server
./mcp <server> restart                        # Restart project server
./mcp <server> logs                           # View server logs
./mcp <server> status                         # Check server status
./mcp-test                                    # Test project servers
./mcp-upgrade                                 # Upgrade project servers
```

### Discovery and Analysis

```bash
# Environment analysis
mcp-universal discover analyze               # Analyze current directory
mcp-universal discover report               # Generate discovery report
mcp-universal discover auto-init            # Auto-initialize based on analysis
```

## 📦 Upgrade Modules

### Available Modules

#### 1. **Enhanced Logging** (`logging-enhancement`)
- Structured JSON logging with correlation IDs
- Performance metrics and context-aware logging
- Compatible: Python FastMCP, Minimal Python

```python
from src.utils.logging import logger, set_correlation_id
set_correlation_id(new_correlation_id())
logger.info("Processing request", user_id="123", action="save_memory")
```

#### 2. **JWT Authentication** (`authentication`)
- Token generation and validation
- Permission-based access control with rate limiting
- Compatible: Python FastMCP, TypeScript Node.js

```python
from src.middleware.auth import require_auth

@require_auth(permissions=["admin"])
async def admin_tool(ctx, param: str):
    # Only users with admin permission can access
    pass
```

#### 3. **Redis Caching** (`caching-redis`)
- High-performance Redis caching with TTL
- Decorator-based caching and statistics
- Compatible: All templates

```python
from src.utils.cache import cached

@cached(ttl=600, key_prefix="weather")
async def expensive_api_call(city: str):
    # Results cached for 10 minutes
    pass
```

#### 4. **Database Migrations** (`database-migrations`)
- Alembic-based schema management
- Version control for schemas with rollback support
- Compatible: Python FastMCP

#### 5. **Prometheus Metrics** (`monitoring-metrics`)
- Request/response metrics and error tracking
- Performance monitoring with Grafana support
- Compatible: Python FastMCP, TypeScript Node.js

#### 6. **API Versioning** (`api-versioning`)
- Semantic versioning with compatibility resolution
- Deprecation warnings and migration helpers
- Compatible: Python FastMCP, TypeScript Node.js

### Installing Modules

```bash
# Interactive selection
mcp-universal upgrade wizard my-server

# Install specific modules
mcp-universal upgrade install my-server logging-enhancement authentication

# Suggest from natural language
mcp-universal upgrade suggest "I need secure API with caching and monitoring" my-server
```

## 🎯 Use Cases & Examples

### Example 1: Claude Code Project

```bash
# Navigate to Claude project (contains .claude/ directory)
cd my-claude-project

# Auto-initialization (detects Claude automatically)
mcp-universal
# ✅ Claude project detected - MCP integration active!

# Create project-specific tools
./mcp create project-assistant --template python-fastmcp
./mcp-test project-assistant --start

# Add capabilities
./mcp-upgrade install project-assistant authentication monitoring-metrics
```

### Example 2: Python API Development

```bash
# Navigate to Python project
cd my-python-api

# Initialize
mcp-init-project
# 🎯 Python project detected
# ✅ Created my-python-api-tools server

# Develop and test
cd ~/mcp-my-python-api-tools
# Edit src/main.py to add your tools
mcp-universal test my-python-api-tools --start

# Add production features
mcp-universal upgrade install my-python-api-tools \
  authentication \
  caching-redis \
  database-migrations \
  monitoring-metrics
```

### Example 3: Full-Stack Development

```bash
# Multi-language project (Python backend + React frontend)
cd full-stack-app

# Initialize (detects both environments)
mcp-universal
# 🎯 Detected: python, nodejs, web_frontend
# 💡 Suggested servers: python-tools, nodejs-tools, web-tools

# Create comprehensive tooling
mcp-universal create backend-tools --template python-fastmcp --port 8055
mcp-universal create frontend-tools --template typescript-node --port 8056

# Add full production stack
mcp-universal upgrade install backend-tools \
  authentication caching-redis database-migrations monitoring-metrics

mcp-universal upgrade install frontend-tools \
  authentication api-versioning monitoring-metrics
```

## 🔒 Security & Safety

### Built-in Safety Features

- ✅ **Configuration Backups**: Automatic backup before any changes
- ✅ **Dry Run Mode**: Test upgrades without applying changes
- ✅ **Rollback System**: Complete rollback of any module
- ✅ **Safe Mode**: Non-destructive operations by default
- ✅ **Permission Validation**: Verify write permissions before installation

### Security Best Practices

```bash
# Always test in dry-run first
mcp-universal upgrade install my-server authentication --dry-run

# Backup before major changes
cp ~/.claude/claude_desktop_config.json ~/.claude/claude_desktop_config.backup

# Use safe mode for production
export MCP_SAFE_MODE=true
```

## 🐳 Docker Support

### Running Servers in Docker

```bash
# Build server image
cd ~/mcp-my-server
docker build -t my-server:latest .

# Run with MCP system
mcp-universal my-server start --docker

# Docker Compose integration
mcp-universal generate docker-compose my-server
```

### Container Template

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src/
EXPOSE 8050

CMD ["python", "src/main.py"]
```

## 🔧 Advanced Configuration

### Custom Templates

Create your own server templates:

```bash
# Create template directory
mkdir ~/.mcp-system/templates/my-custom-template

# Add template files
# template.json - Template configuration
# {{name}}.py - Main server file (with variable substitution)
# requirements.txt - Dependencies
# README.md - Template documentation
```

### Environment-Specific Configs

```bash
# Development
export MCP_ENV=development
export MCP_DEBUG=true
export MCP_AUTO_RELOAD=true

# Production  
export MCP_ENV=production
export MCP_SAFE_MODE=true
export MCP_LOG_LEVEL=warning
```

## 📚 Documentation

Comprehensive documentation is available in the `docs/` directory:

- **[Complete Documentation](docs/MCP-Complete-Documentation.md)** - Full system guide
- **[Upgrade System Guide](docs/MCP-Upgrader-Documentation.md)** - Modular enhancement guide  
- **[Quick Start Guide](docs/MCP-Quick-Start-Guide.md)** - Get up and running fast
- **[API Reference](docs/API-Reference.md)** - Complete API documentation
- **[Troubleshooting](docs/Troubleshooting.md)** - Common issues and solutions

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone for development
git clone https://github.com/dezocode/mcp-system.git
cd mcp-system

# Install in development mode
pip install -e .

# Run tests
python -m pytest tests/

# Format code
black src/
isort src/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Anthropic** for the Model Context Protocol specification
- **FastMCP** for the Python MCP framework
- **Mem0** for inspiration on MCP server architecture
- **Claude Code CLI** for enabling seamless AI development workflows

---

<div align="center">

**🚀 Transform your development workflow with the MCP System!**

[Get Started](#-installation) • [View Docs](docs/) • [Report Issues](https://github.com/dezocode/mcp-system/issues) • [Join Discussions](https://github.com/dezocode/mcp-system/discussions)

</div>