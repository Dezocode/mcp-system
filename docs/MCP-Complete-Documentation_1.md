# Complete MCP Server Management System

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Installation](#installation)
4. [Core Components](#core-components)
5. [Workflow Guide](#workflow-guide)
6. [Creating New MCP Servers](#creating-new-mcp-servers)
7. [Testing Framework](#testing-framework)
8. [Configuration Management](#configuration-management)
9. [Deployment Strategies](#deployment-strategies)
10. [Troubleshooting](#troubleshooting)
11. [Best Practices](#best-practices)

---

## Overview

This system provides a complete solution for managing multiple MCP (Model Context Protocol) servers with intelligent routing, automatic server selection, and seamless integration with Claude Code.

### Key Features

- 🎯 **Intelligent Server Selection**: Automatically chooses appropriate servers based on user prompts
- 🚀 **One-Command Management**: Start, stop, and manage servers with single commands
- 🔄 **Dependency Handling**: Automatic management of databases, services, and dependencies
- 📊 **Health Monitoring**: Real-time status tracking and health checks
- 🔧 **Development Tools**: Templates and testing frameworks for new server creation
- 🐳 **Container Support**: Docker and Docker Compose deployment options
- 📝 **Comprehensive Logging**: Detailed logs and debugging capabilities

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Interface Layer                     │
├─────────────────────────────────────────────────────────────────┤
│  Claude Code CLI  │  Terminal Commands  │  Web Interface       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Integration Layer                            │
├─────────────────────────────────────────────────────────────────┤
│  claude-mcp.sh   │  mcp-router.py     │  Makefile Commands    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Management Layer                             │
├─────────────────────────────────────────────────────────────────┤
│  mcp (Universal Launcher)  │  mcp-manager.py  │  Docker Compose │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      MCP Servers                                │
├─────────────────────────────────────────────────────────────────┤
│  mem0:8050  │  github:8052  │  filesystem:8051  │  custom:805X  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Infrastructure Layer                         │
├─────────────────────────────────────────────────────────────────┤
│  PostgreSQL  │  Ollama  │  Redis  │  External APIs  │  Storage  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Installation

### Prerequisites

```bash
# Required software
- Python 3.8+
- Node.js 16+ (for some servers)
- Docker & Docker Compose
- uv (Python package manager)
- jq (JSON processor)

# Optional but recommended
- make
- curl
- git
```

### Quick Installation

```bash
# 1. Clone or download the MCP system files
curl -O https://raw.githubusercontent.com/your-repo/mcp-system/main/install.sh
chmod +x install.sh
./install.sh

# 2. Or manual installation
mkdir -p ~/bin ~/.mcp-runtime
cp mcp ~/bin/
cp mcp-router.py ~/bin/
cp claude-mcp.sh ~/bin/claude-mcp
chmod +x ~/bin/{mcp,mcp-router.py,claude-mcp}

# 3. Add to PATH
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# 4. Initialize configuration
mcp list  # This creates ~/.mcp-servers.json
```

### Verification

```bash
# Check installation
which mcp
which claude-mcp
mcp list
claude-mcp help
```

---

## Core Components

### 1. Universal Launcher (`mcp`)

The main command for managing all MCP servers.

```bash
# Basic usage
mcp [server-name] [action] [options]

# Examples
mcp list                    # List all servers
mcp mem0 start             # Start memory server
mcp github stop            # Stop GitHub server
mcp all restart            # Restart all servers
mcp mem0 logs              # View server logs
mcp status                 # Check all server status
```

#### Supported Actions

| Action | Description | Example |
|--------|-------------|---------|
| `start` | Start server and dependencies | `mcp mem0 start` |
| `stop` | Stop server | `mcp mem0 stop` |
| `restart` | Stop and start server | `mcp mem0 restart` |
| `status` | Check server status | `mcp mem0 status` |
| `logs` | View server logs | `mcp mem0 logs` |
| `list` | List all available servers | `mcp list` |

### 2. Intelligent Router (`mcp-router.py`)

Analyzes user prompts and automatically selects appropriate MCP servers.

```bash
# Analyze a prompt
mcp-router.py --analyze "Remember my coding preferences"

# Route a request
mcp-router.py --route "Save this memory" --tool save_memory --data '{"text":"Hello"}'

# Interactive mode
mcp-router.py --interactive
```

#### Server Selection Logic

The router uses multiple strategies to determine server relevance:

1. **Keyword Matching**: Direct keyword presence in prompts
2. **Pattern Recognition**: Regex patterns for complex tasks
3. **Context Analysis**: Understanding task intent
4. **Score-based Ranking**: Multiple servers ranked by relevance

```python
# Example keyword mappings
server_keywords = {
    "mem0": ["memory", "remember", "recall", "store", "retrieve"],
    "filesystem": ["file", "directory", "read", "write", "create"],
    "github": ["github", "repository", "commit", "pull request"],
    "weather": ["weather", "forecast", "temperature", "climate"]
}
```

### 3. Claude Integration Helper (`claude-mcp.sh`)

Bridge between Claude Code and MCP servers with simplified commands.

```bash
# Memory operations
claude-mcp memory save "I prefer Python for AI"
claude-mcp memory search "programming language"
claude-mcp memory list

# Server management
claude-mcp analyze "Create a new GitHub repository"
claude-mcp status
claude-mcp list

# Direct server communication
claude-mcp send mem0 save_memory '{"text":"Test"}'
```

### 4. Configuration System

Central configuration in `~/.mcp-servers.json`:

```json
{
  "server-name": {
    "name": "Human-readable name",
    "path": "~/path/to/server",
    "command": "command to start server",
    "port": 8050,
    "env_file": ".env",
    "env": {
      "CUSTOM_VAR": "value"
    },
    "dependencies": {
      "postgres": {
        "type": "docker",
        "image": "postgres:latest",
        "name": "container-name",
        "env": {...},
        "ports": {"5432": "5432"}
      }
    },
    "install": "npm install && npm run build",
    "health_check": "curl http://localhost:8050/health"
  }
}
```

---

## Workflow Guide

### Daily Usage Workflow

#### 1. Starting Your Session

```bash
# Quick start - let the system decide
claude-mcp analyze "I want to work with GitHub repositories and save notes"
# → Automatically starts github and mem0 servers

# Or start specific servers
mcp mem0 start
mcp github start

# Or start everything
mcp all start
```

#### 2. Working with Memory

```bash
# Save information
claude-mcp memory save "Working on a React TypeScript project with Tailwind CSS"

# Search for information
claude-mcp memory search "React project"

# List all memories
claude-mcp memory list
```

#### 3. Check Status

```bash
# Quick status check
mcp status

# Detailed server information
mcp mem0 status
mcp github status
```

#### 4. Viewing Logs

```bash
# Follow logs in real-time
mcp mem0 logs

# View specific log file
tail -f ~/.mcp-runtime/mem0.log
```

### Development Workflow

#### 1. Creating a New Server

```bash
# Use the server generator (we'll create this)
mcp-create-server my-new-server --type python --port 8055

# Or manually create
mkdir ~/mcp-my-server
cd ~/mcp-my-server
# ... setup server code
```

#### 2. Testing Server

```bash
# Add to configuration
# Edit ~/.mcp-servers.json

# Start in development mode
mcp my-server start --fg  # foreground mode for debugging

# Test functionality
claude-mcp send my-server test_tool '{"param":"value"}'
```

#### 3. Production Deployment

```bash
# Docker deployment
docker-compose up -d

# Or system service
sudo systemctl enable mcp-my-server
sudo systemctl start mcp-my-server
```

---

## Creating New MCP Servers

### Server Template Generator

Use the `mcp-create-server` command to generate new MCP servers:

```bash
# Quick server creation
mcp-create-server my-weather --template python-fastmcp --port 8055

# With custom description and path
mcp-create-server file-manager \
  --template typescript-node \
  --port 8056 \
  --description "Advanced file management server" \
  --path ~/my-servers/file-manager
```

#### Available Templates

| Template | Language | Framework | Use Case |
|----------|----------|-----------|----------|
| `python-fastmcp` | Python | FastMCP | Full-featured MCP servers |
| `typescript-node` | TypeScript | Node.js + Express | Web-enabled MCP servers |
| `minimal-python` | Python | Basic | Simple, lightweight servers |

#### Template Features

Each template includes:
- ✅ **Complete server structure**
- ✅ **Example tools and handlers**
- ✅ **Configuration management (.env)**
- ✅ **Docker support**
- ✅ **Test framework integration**
- ✅ **Documentation (README.md)**
- ✅ **Auto-registration with MCP system**

### Step-by-Step Server Creation

#### 1. Generate Server

```bash
# Create a weather server
mcp-create-server weather-api --template python-fastmcp --port 8055

# Output:
# Created: /Users/your-name/mcp-weather-api/src/main.py
# Created: /Users/your-name/mcp-weather-api/pyproject.toml
# Created: /Users/your-name/mcp-weather-api/.env.example
# ... (other files)
# Added weather-api to MCP configuration
```

#### 2. Navigate and Setup

```bash
cd ~/mcp-weather-api

# Install dependencies
uv pip install -e .

# Configure environment
cp .env.example .env
# Edit .env with your API keys and settings
```

#### 3. Customize Your Server

Edit `src/main.py` to add your tools:

```python
@mcp.tool()
async def get_weather(ctx: Context, city: str, units: str = "metric") -> str:
    """Get current weather for a city.
    
    Args:
        ctx: The MCP server provided context
        city: The city name
        units: Temperature units (metric, imperial, kelvin)
        
    Returns:
        Weather information in JSON format
    """
    # Your weather API implementation here
    api_key = os.getenv("OPENWEATHER_API_KEY")
    # ... implementation
    return json.dumps(weather_data, indent=2)

@mcp.tool()
async def get_forecast(ctx: Context, city: str, days: int = 5) -> str:
    """Get weather forecast for a city.
    
    Args:
        ctx: The MCP server provided context
        city: The city name  
        days: Number of days for forecast
        
    Returns:
        Forecast data in JSON format
    """
    # Your forecast implementation here
    return json.dumps(forecast_data, indent=2)
```

#### 4. Test Your Server

```bash
# Test locally in foreground
mcp weather-api start --fg

# Or run tests
mcp-test weather-api --start

# Test specific tools
claude-mcp send weather-api get_weather '{"city":"San Francisco"}'
```

#### 5. Deploy to Production

```bash
# Docker deployment
docker-compose up -d

# Or system service (see Deployment section)
```

### Advanced Server Development

#### Custom Dependencies

Add database or service dependencies in the MCP configuration:

```json
{
  "weather-api": {
    "name": "Weather API Server",
    "path": "~/mcp-weather-api", 
    "command": "uv run python src/main.py",
    "port": 8055,
    "dependencies": {
      "redis": {
        "type": "docker",
        "image": "redis:latest",
        "name": "weather-redis",
        "ports": {"6379": "6379"}
      },
      "external_api": {
        "type": "service",
        "check_url": "https://api.openweathermap.org/data/2.5/weather"
      }
    }
  }
}
```

#### Environment Management

Use `.env` files for configuration:

```bash
# .env
OPENWEATHER_API_KEY=your-api-key-here
REDIS_URL=redis://localhost:6379
DEBUG=true
CACHE_TTL=300
```

#### Tool Documentation

Follow the documentation pattern:

```python
@mcp.tool()
async def complex_tool(ctx: Context, param1: str, param2: int = 10, 
                      param3: bool = False) -> str:
    """Brief description of what this tool does.
    
    Longer description explaining the tool's purpose, behavior,
    and any important notes about usage.
    
    Args:
        ctx: The MCP server provided context
        param1: Description of required parameter
        param2: Description of optional parameter (default: 10)
        param3: Description of boolean parameter (default: False)
        
    Returns:
        Description of what is returned
        
    Raises:
        ValueError: When param1 is invalid
        ConnectionError: When external service is unavailable
    """
```

---

## Testing Framework

The MCP testing framework provides comprehensive testing capabilities for your servers.

### Basic Testing

```bash
# Test a single server
mcp-test mem0

# Test all servers
mcp-test all

# Start server before testing
mcp-test weather-api --start

# Save detailed report
mcp-test all --report test-results.json
```

### Test Types

#### 1. Health Checks
- Server responsiveness
- Port accessibility
- Basic connectivity

#### 2. Protocol Compliance
- MCP specification adherence
- JSON-RPC format
- Tool discovery

#### 3. Tool Execution
- Individual tool testing
- Parameter validation
- Response format verification

#### 4. Custom Tests
- Defined in test suites
- Business logic validation
- Integration testing

### Creating Custom Test Suites

Create test configurations for your servers:

```python
# In your server directory: tests/test_suite.py
from mcp_test_framework import ServerTestSuite

weather_test_suite = ServerTestSuite(
    server_name="weather-api",
    base_url="http://localhost:8055",
    tests=[
        {
            "name": "get_weather_valid_city",
            "type": "tool",
            "tool": "get_weather",
            "args": {"city": "San Francisco"},
            "expected": "temperature"
        },
        {
            "name": "get_weather_invalid_city",
            "type": "tool", 
            "tool": "get_weather",
            "args": {"city": "InvalidCityName"},
            "expected": "error"
        },
        {
            "name": "forecast_endpoint",
            "type": "http",
            "endpoint": "/forecast",
            "method": "GET",
            "expected_status": 200
        }
    ]
)
```

### Automated Testing

#### CI/CD Integration

```yaml
# .github/workflows/test.yml
name: MCP Server Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install MCP tools
      run: |
        pip install -r requirements.txt
        chmod +x mcp-test
    
    - name: Start dependencies
      run: docker-compose up -d postgres redis
    
    - name: Run tests
      run: |
        mcp-test all --start --report test-results.json
    
    - name: Upload test results
      uses: actions/upload-artifact@v4
      with:
        name: test-results
        path: test-results.json
```

#### Pre-commit Testing

```bash
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: mcp-test
        name: MCP Server Tests
        entry: mcp-test
        args: [all]
        language: system
        pass_filenames: false
```

---

## Configuration Management

### Server Configuration (`~/.mcp-servers.json`)

The central configuration file defines all your MCP servers:

```json
{
  "server-name": {
    "name": "Human-readable server name",
    "path": "~/path/to/server/directory",
    "command": "command to start the server",
    "port": 8050,
    "env_file": ".env",
    "env": {
      "CUSTOM_ENV_VAR": "value"
    },
    "dependencies": {
      "database": {
        "type": "docker",
        "image": "postgres:15",
        "name": "server-postgres",
        "env": {
          "POSTGRES_DB": "serverdb",
          "POSTGRES_USER": "user",
          "POSTGRES_PASSWORD": "password"
        },
        "ports": {"5432": "5432"}
      },
      "redis": {
        "type": "docker", 
        "image": "redis:latest",
        "name": "server-redis",
        "ports": {"6379": "6379"}
      },
      "external_service": {
        "type": "service",
        "command": "some-service --port 9090",
        "check_url": "http://localhost:9090/health"
      }
    },
    "install": "pip install -r requirements.txt",
    "health_check": "curl -f http://localhost:8050/health"
  }
}
```

#### Configuration Fields

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `name` | string | Human-readable server name | Yes |
| `path` | string | Path to server directory | Yes |
| `command` | string | Command to start server | Yes |
| `port` | number | Server port number | Yes |
| `env_file` | string | Environment file (.env) | No |
| `env` | object | Environment variables | No |
| `dependencies` | object | Server dependencies | No |
| `install` | string | Installation command | No |
| `health_check` | string | Health check command | No |

### Environment Management

#### Server-specific .env files

Each server can have its own `.env` file:

```bash
# ~/mcp-weather/.env
OPENWEATHER_API_KEY=your-api-key
CACHE_ENABLED=true
CACHE_TTL=300
LOG_LEVEL=info
DATABASE_URL=postgresql://user:pass@localhost:5432/weather
```

#### Global environment variables

Set in your shell profile:

```bash
# ~/.zshrc or ~/.bashrc
export MCP_LOG_LEVEL=debug
export MCP_DATA_DIR=~/mcp-data
export MCP_RUNTIME_DIR=~/.mcp-runtime
```

### Router Configuration

Customize the intelligent router in `~/.mcp-router-config.json`:

```json
{
  "server_keywords": {
    "weather-api": ["weather", "forecast", "temperature", "climate"],
    "file-manager": ["file", "directory", "folder", "document"],
    "email-server": ["email", "mail", "send", "inbox"]
  },
  "task_patterns": {
    "weather-api": [
      "what.+weather",
      "temperature.+in",
      "forecast.+for"
    ]
  },
  "default_limits": {
    "response_timeout": 10,
    "max_retries": 3,
    "startup_wait": 5
  }
}
```

---

## Deployment Strategies

### Development Deployment

#### Local Development

```bash
# Quick start for development
mcp weather-api start --fg  # Foreground mode

# Or background with logs
mcp weather-api start
mcp weather-api logs
```

#### Development Tools

```bash
# File watching for auto-restart
pip install watchdog
watchmedo auto-restart --patterns="*.py" --recursive mcp weather-api start

# Debug mode
DEBUG=true mcp weather-api start
```

### Production Deployment

#### 1. Docker Deployment

**Single Server:**
```bash
cd ~/mcp-weather-api
docker build -t weather-api .
docker run -d --name weather-api -p 8055:8055 weather-api
```

**Multi-Server with Docker Compose:**
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  weather-api:
    build: ./mcp-weather-api
    ports:
      - "8055:8055"
    environment:
      - OPENWEATHER_API_KEY=${OPENWEATHER_API_KEY}
    depends_on:
      - redis
    restart: unless-stopped

  file-manager:
    build: ./mcp-file-manager  
    ports:
      - "8056:8056"
    volumes:
      - ./data:/app/data
    restart: unless-stopped

  redis:
    image: redis:latest
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  redis_data:
```

```bash
# Deploy all servers
docker-compose -f docker-compose.prod.yml up -d

# Scale specific services
docker-compose -f docker-compose.prod.yml up -d --scale weather-api=3
```

#### 2. System Service Deployment

**Create systemd service:**
```bash
# /etc/systemd/system/mcp-weather-api.service
[Unit]
Description=Weather API MCP Server
After=network.target
Requires=network.target

[Service]
Type=simple
User=mcp-user
Group=mcp-group
WorkingDirectory=/opt/mcp-servers/weather-api
ExecStart=/opt/mcp-servers/weather-api/.venv/bin/python src/main.py
EnvironmentFile=/opt/mcp-servers/weather-api/.env
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable mcp-weather-api
sudo systemctl start mcp-weather-api
sudo systemctl status mcp-weather-api
```

#### 3. Container Orchestration

**Kubernetes Deployment:**
```yaml
# weather-api-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: weather-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: weather-api
  template:
    metadata:
      labels:
        app: weather-api
    spec:
      containers:
      - name: weather-api
        image: weather-api:latest
        ports:
        - containerPort: 8055
        env:
        - name: OPENWEATHER_API_KEY
          valueFrom:
            secretKeyRef:
              name: weather-secrets
              key: api-key
---
apiVersion: v1
kind: Service
metadata:
  name: weather-api-service
spec:
  selector:
    app: weather-api
  ports:
  - port: 80
    targetPort: 8055
  type: LoadBalancer
```

### High Availability Setup

#### Load Balancing

```nginx
# /etc/nginx/sites-available/mcp-servers
upstream weather_api {
    server 127.0.0.1:8055;
    server 127.0.0.1:8056;
    server 127.0.0.1:8057;
}

server {
    listen 80;
    server_name weather-api.example.com;

    location / {
        proxy_pass http://weather_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        
        # SSE support
        proxy_buffering off;
        proxy_cache off;
    }
}
```

#### Health Monitoring

```bash
# Health check script
#!/bin/bash
# health-check.sh

check_server() {
    local server=$1
    local port=$2
    
    if curl -f "http://localhost:$port/health" >/dev/null 2>&1; then
        echo "✅ $server is healthy"
        return 0
    else
        echo "❌ $server is down"
        # Restart server
        mcp $server restart
        return 1
    fi
}

# Check all servers
check_server "weather-api" 8055
check_server "file-manager" 8056

# Run every 5 minutes
# */5 * * * * /path/to/health-check.sh
```

---

## Troubleshooting

### Common Issues

#### 1. Server Won't Start

**Problem:** Server fails to start or exits immediately

**Diagnosis:**
```bash
# Check logs
mcp server-name logs

# Check configuration
mcp server-name status

# Test manually
cd ~/mcp-server-name
python src/main.py  # Or appropriate command
```

**Common Causes:**
- Port already in use
- Missing dependencies
- Invalid configuration
- Permission issues
- Missing environment variables

**Solutions:**
```bash
# Check port usage
lsof -i :8050

# Kill process on port
kill -9 $(lsof -t -i:8050)

# Check dependencies
mcp server-name status
docker ps  # For Docker dependencies

# Fix permissions
chmod +x ~/bin/mcp
chown -R $USER:$USER ~/.mcp-runtime
```

#### 2. Connection Refused

**Problem:** Cannot connect to server

**Diagnosis:**
```bash
# Test direct connection
curl http://localhost:8050/health

# Check if server is listening
netstat -tlnp | grep 8050

# Check firewall
sudo ufw status
```

**Solutions:**
```bash
# Restart server
mcp server-name restart

# Check host binding
# In .env: HOST=0.0.0.0 instead of localhost

# Check firewall rules
sudo ufw allow 8050
```

#### 3. Tool Execution Fails

**Problem:** Tools return errors or timeouts

**Diagnosis:**
```bash
# Test tool directly
claude-mcp send server-name tool-name '{"param":"value"}'

# Check server logs
mcp server-name logs

# Test with curl
curl -X POST http://localhost:8050/sse \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"tool-name","arguments":{}},"id":1}'
```

**Common Causes:**
- Invalid parameters
- External API issues
- Database connection problems
- Authentication failures

#### 4. Memory/Performance Issues

**Problem:** High memory usage or slow responses

**Diagnosis:**
```bash
# Monitor resources
top -p $(pgrep -f "server-name")

# Check connections
ss -tlnp | grep 8050

# Profile Python servers
pip install py-spy
py-spy top --pid $(pgrep -f "server-name")
```

**Solutions:**
```bash
# Restart server
mcp server-name restart

# Check for memory leaks in logs
mcp server-name logs | grep -i memory

# Optimize configuration
# Reduce cache sizes, connection pools, etc.
```

### Debugging Tools

#### 1. Verbose Logging

```bash
# Enable debug mode
DEBUG=true mcp server-name start

# Or in .env
DEBUG=true
LOG_LEVEL=debug
```

#### 2. Network Debugging

```bash
# Monitor HTTP traffic
tcpdump -i lo -A -s 0 'port 8050'

# Test with different tools
curl -v http://localhost:8050/health
wget --debug http://localhost:8050/health
```

#### 3. MCP Protocol Debugging

```bash
# Test MCP protocol compliance
mcp-test server-name --verbose

# Manual protocol test
echo '{"jsonrpc":"2.0","method":"tools/list","params":{},"id":1}' | \
  websocat ws://localhost:8050/ws
```

### Performance Optimization

#### Server Optimization

```python
# In your server code
import uvloop  # For Python AsyncIO performance
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

# Connection pooling
from aiohttp_session import setup
from aiohttp_session.cookie_storage import EncryptedCookieStorage

# Caching
from functools import lru_cache

@lru_cache(maxsize=128)
async def expensive_operation(param):
    # Cached expensive operation
    pass
```

#### Database Optimization

```python
# Connection pooling
from sqlalchemy.pool import QueuePool

engine = create_async_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)
```

#### Monitoring and Metrics

```python
# Add metrics to your server
from prometheus_client import Counter, Histogram, generate_latest

REQUEST_COUNT = Counter('mcp_requests_total', 'Total requests')
REQUEST_DURATION = Histogram('mcp_request_duration_seconds', 'Request duration')

@mcp.tool()
async def monitored_tool(ctx: Context, param: str) -> str:
    REQUEST_COUNT.inc()
    with REQUEST_DURATION.time():
        # Your tool implementation
        pass
```

---

## Best Practices

### Development Best Practices

#### 1. Code Organization

```
mcp-your-server/
├── src/
│   ├── main.py              # Server entry point
│   ├── tools/               # Tool implementations
│   │   ├── __init__.py
│   │   ├── core_tools.py
│   │   └── custom_tools.py
│   ├── utils/               # Utility functions
│   │   ├── __init__.py
│   │   ├── database.py
│   │   └── external_apis.py
│   └── config.py            # Configuration management
├── tests/                   # Test files
├── docs/                    # Documentation
├── docker/                  # Docker files
├── .env.example            # Environment template
├── pyproject.toml          # Python dependencies
└── README.md               # Documentation
```

#### 2. Error Handling

```python
from mcp.types import McpError, ErrorCode

@mcp.tool()
async def robust_tool(ctx: Context, param: str) -> str:
    """Tool with proper error handling"""
    try:
        # Validate input
        if not param or len(param) < 1:
            raise McpError(
                ErrorCode.InvalidParams,
                "Parameter 'param' must be non-empty"
            )
        
        # Your implementation
        result = await external_api_call(param)
        
        if not result:
            raise McpError(
                ErrorCode.InternalError, 
                "External API returned empty result"
            )
        
        return json.dumps(result)
        
    except ValidationError as e:
        raise McpError(ErrorCode.InvalidParams, f"Validation error: {e}")
    except ConnectionError as e:
        raise McpError(ErrorCode.InternalError, f"Connection failed: {e}")
    except Exception as e:
        # Log the full error for debugging
        logger.exception(f"Unexpected error in robust_tool: {e}")
        raise McpError(ErrorCode.InternalError, "Internal server error")
```

#### 3. Configuration Management

```python
# src/config.py
import os
from pathlib import Path
from typing import Optional
from pydantic import BaseSettings, Field

class ServerConfig(BaseSettings):
    """Server configuration with validation"""
    
    host: str = Field(default="localhost", env="HOST")
    port: int = Field(default=8050, env="PORT") 
    debug: bool = Field(default=False, env="DEBUG")
    
    # External APIs
    openweather_api_key: Optional[str] = Field(env="OPENWEATHER_API_KEY")
    
    # Database
    database_url: Optional[str] = Field(env="DATABASE_URL")
    
    # Caching
    cache_enabled: bool = Field(default=True, env="CACHE_ENABLED")
    cache_ttl: int = Field(default=300, env="CACHE_TTL")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Usage in server
config = ServerConfig()
```

#### 4. Testing Strategy

```python
# tests/test_tools.py
import pytest
from unittest.mock import Mock, patch
from src.main import get_weather

@pytest.mark.asyncio
async def test_get_weather_success():
    """Test successful weather retrieval"""
    ctx = Mock()
    
    with patch('src.main.external_weather_api') as mock_api:
        mock_api.return_value = {"temperature": 22, "description": "sunny"}
        
        result = await get_weather(ctx, city="San Francisco")
        
        assert "temperature" in result
        assert "22" in result
        mock_api.assert_called_once_with("San Francisco")

@pytest.mark.asyncio 
async def test_get_weather_invalid_city():
    """Test weather retrieval with invalid city"""
    ctx = Mock()
    
    with pytest.raises(McpError) as exc_info:
        await get_weather(ctx, city="")
    
    assert exc_info.value.code == ErrorCode.InvalidParams
```

### Production Best Practices

#### 1. Security

```python
# Input validation
from pydantic import BaseModel, validator

class WeatherRequest(BaseModel):
    city: str
    units: str = "metric"
    
    @validator('city')
    def city_must_be_valid(cls, v):
        if not v or len(v) < 2:
            raise ValueError('City name too short')
        # Sanitize input
        return v.strip()[:100]  # Limit length
    
    @validator('units') 
    def units_must_be_valid(cls, v):
        if v not in ['metric', 'imperial', 'kelvin']:
            raise ValueError('Invalid units')
        return v

# Rate limiting
from collections import defaultdict
from time import time

rate_limits = defaultdict(list)

def rate_limit(max_requests: int = 10, window: int = 60):
    def decorator(func):
        async def wrapper(ctx, *args, **kwargs):
            client_id = getattr(ctx, 'client_id', 'default')
            now = time()
            
            # Clean old requests
            rate_limits[client_id] = [
                req_time for req_time in rate_limits[client_id]
                if now - req_time < window
            ]
            
            # Check rate limit
            if len(rate_limits[client_id]) >= max_requests:
                raise McpError(
                    ErrorCode.InvalidRequest,
                    "Rate limit exceeded"
                )
            
            rate_limits[client_id].append(now)
            return await func(ctx, *args, **kwargs)
        return wrapper
    return decorator
```

#### 2. Monitoring and Observability

```python
# Logging setup
import logging
import structlog

logging.basicConfig(level=logging.INFO)
logger = structlog.get_logger()

# Metrics collection
from prometheus_client import Counter, Histogram, Gauge

TOOL_CALLS = Counter('mcp_tool_calls_total', 'Tool calls', ['tool_name', 'status'])
TOOL_DURATION = Histogram('mcp_tool_duration_seconds', 'Tool duration', ['tool_name'])
ACTIVE_CONNECTIONS = Gauge('mcp_active_connections', 'Active connections')

def instrument_tool(func):
    async def wrapper(ctx, *args, **kwargs):
        tool_name = func.__name__
        
        with TOOL_DURATION.labels(tool_name=tool_name).time():
            try:
                result = await func(ctx, *args, **kwargs)
                TOOL_CALLS.labels(tool_name=tool_name, status='success').inc()
                return result
            except Exception as e:
                TOOL_CALLS.labels(tool_name=tool_name, status='error').inc()
                logger.error("Tool execution failed", 
                           tool=tool_name, error=str(e))
                raise
    return wrapper
```

#### 3. Deployment Automation

```bash
#!/bin/bash
# deploy.sh - Deployment automation script

set -e

SERVER_NAME="$1"
VERSION="$2"

if [ -z "$SERVER_NAME" ] || [ -z "$VERSION" ]; then
    echo "Usage: $0 <server-name> <version>"
    exit 1
fi

echo "Deploying $SERVER_NAME version $VERSION"

# Pre-deployment checks
echo "Running pre-deployment tests..."
mcp-test "$SERVER_NAME" --report "test-results-$(date +%Y%m%d-%H%M%S).json"

# Build and tag container
echo "Building container..."
cd "mcp-$SERVER_NAME"
docker build -t "$SERVER_NAME:$VERSION" .
docker tag "$SERVER_NAME:$VERSION" "$SERVER_NAME:latest"

# Deploy with zero downtime
echo "Deploying with rolling update..."
docker-compose -f docker-compose.prod.yml up -d --no-deps "$SERVER_NAME"

# Post-deployment verification
echo "Verifying deployment..."
sleep 10
mcp-test "$SERVER_NAME" --start

echo "✅ Deployment completed successfully"
```

#### 4. Backup and Recovery

```bash
#!/bin/bash
# backup-mcp-config.sh

BACKUP_DIR="$HOME/.mcp-backups/$(date +%Y%m%d)"
mkdir -p "$BACKUP_DIR"

# Backup configurations
cp ~/.mcp-servers.json "$BACKUP_DIR/"
cp -r ~/.mcp-runtime "$BACKUP_DIR/"

# Backup server data
for server in $(jq -r 'keys[]' ~/.mcp-servers.json); do
    server_path=$(jq -r ".$server.path" ~/.mcp-servers.json)
    if [ -d "$server_path" ]; then
        tar -czf "$BACKUP_DIR/$server-data.tar.gz" -C "$server_path" .
    fi
done

echo "Backup completed: $BACKUP_DIR"
```

### Integration Best Practices

#### 1. Claude Code Integration

```bash
# Create alias for common operations
alias cm='claude-mcp'
alias cms='claude-mcp status'
alias cml='claude-mcp memory list'

# Add to .zshrc/.bashrc
function remember() {
    claude-mcp memory save "$*"
}

function recall() {
    claude-mcp memory search "$*"
}
```

#### 2. Workflow Integration

```bash
# Git hooks integration
# .git/hooks/post-commit
#!/bin/bash
commit_msg=$(git log -1 --pretty=%B)
claude-mcp memory save "Committed: $commit_msg"
```

#### 3. Multi-Server Workflows

```python
# Server orchestration
class MCPOrchestrator:
    def __init__(self):
        self.servers = self._discover_servers()
    
    async def complex_workflow(self, user_input: str):
        """Execute multi-server workflow"""
        
        # Step 1: Save context to memory
        await self.call_server("mem0", "save_memory", {
            "text": f"User requested: {user_input}"
        })
        
        # Step 2: Process with appropriate server
        if "weather" in user_input.lower():
            result = await self.call_server("weather-api", "get_weather", {
                "city": self._extract_city(user_input)
            })
        elif "file" in user_input.lower():
            result = await self.call_server("file-manager", "list_files", {
                "path": self._extract_path(user_input)
            })
        
        # Step 3: Store result
        await self.call_server("mem0", "save_memory", {
            "text": f"Result: {result}"
        })
        
        return result
```

---

## Conclusion

This comprehensive MCP server management system provides:

✅ **Universal server management** with single-command operations
✅ **Intelligent routing** based on user intent analysis  
✅ **Complete development lifecycle** from creation to deployment
✅ **Comprehensive testing framework** for reliability
✅ **Production-ready deployment options**
✅ **Monitoring and troubleshooting tools**

### Quick Reference Commands

```bash
# Server Management
mcp list                     # List all servers
mcp server-name start       # Start server
mcp server-name stop        # Stop server
mcp server-name logs        # View logs
mcp status                  # Check all servers

# Development
mcp-create-server name --template python-fastmcp --port 8055
mcp-test server-name --start
claude-mcp memory save "text"
claude-mcp send server tool '{"param":"value"}'

# Deployment
docker-compose up -d
systemctl start mcp-server-name
kubectl apply -f deployment.yaml
```

This system transforms MCP server development from a complex, manual process into a streamlined, automated workflow that scales from development to production.