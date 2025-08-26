# Enhanced MCP Crafter - Robust Server Generation System

## Overview

The Enhanced MCP Crafter is a robust system for generating complex MCP (Model Context Protocol) servers with advanced features including watchdog pathing, CLI integration, automation, and monitoring capabilities. It extends the existing mcp-system with sophisticated server generation capabilities designed to meet the requirements for building 100% stable MCP servers with built-in automation.

## 🌟 Key Features

### 1. **Robust Resolution Capabilities**
- Advanced template system with modular components
- Automatic dependency resolution and path management
- Intelligent feature integration and conflict resolution
- Error handling and validation throughout the generation process

### 2. **Watchdog Pathing Integration**
- Real-time file system monitoring using Python watchdog
- Automatic path resolution and monitoring setup
- Event-driven file change handling with custom callbacks
- Configurable watch paths and recursive monitoring options

### 3. **CLI Total Integration**
- Complete command-line interface for every generated server
- Built-in server management commands (start, stop, status, config)
- Direct tool calling from command line
- Configuration management and log viewing capabilities

### 4. **Asynchronous Form Processing**
- Accept and process forms from Claude or other clients
- Queue-based asynchronous processing for complex operations
- Form validation and structured data handling
- Support for chained form submissions and orchestration

### 5. **Built-in Automation**
- Scheduled health checks and system monitoring
- Automatic log cleanup and maintenance tasks
- Custom task scheduling with configurable intervals
- Background task management and lifecycle handling

### 6. **Modular Architecture**
- Hierarchical component structure for easy extension
- Feature modules that can be added independently
- Template inheritance with enhanced capabilities
- Plugin-like architecture for custom functionality

### 7. **Continuous Tweaking**
- Runtime configuration updates without restart
- Dynamic feature enabling/disabling
- Real-time parameter adjustment via API
- Hot-reloading of configuration changes

## 🚀 Quick Start

### Command Line Usage

```bash
# Generate a basic enhanced server
mcp-crafter my-server --template python-fastmcp --port 8055

# Generate with specific features
mcp-crafter weather-api \
  --template python-fastmcp \
  --port 8060 \
  --features watchdog cli automation monitoring \
  --description "Weather API with full monitoring"

# Generate with custom dependencies
mcp-crafter file-manager \
  --template python-fastmcp \
  --features watchdog automation \
  --dependencies aiofiles boto3 \
  --env AWS_REGION=us-east-1 \
  --env LOG_LEVEL=INFO
```

### MCP Server Usage

The Enhanced MCP Crafter is also available as an MCP server for integration with Claude:

```bash
# Start the crafter as an MCP server
mcp-crafter-server
```

Add to your Claude configuration:
```json
{
  "mcp-crafter": {
    "command": "path/to/mcp-system/bin/mcp-crafter-server",
    "description": "Enhanced MCP server generation and orchestration"
  }
}
```

## 📋 Available Templates

### 1. **python-fastmcp** (Default)
- Modern FastMCP-based Python server
- Built-in FastAPI integration for HTTP endpoints
- Async/await support throughout
- Production-ready configuration

### 2. **typescript-node**
- TypeScript-based Node.js server
- Full type safety and modern ES modules
- Express.js integration for HTTP API
- Comprehensive testing setup

### 3. **minimal-python**
- Lightweight Python implementation
- Minimal dependencies for simple use cases
- Basic MCP protocol implementation
- Easy to customize and extend

## 🔧 Available Features

### Watchdog Monitoring
```bash
--features watchdog
```
- Real-time file system monitoring
- Automatic change detection and event handling
- Configurable watch paths and patterns
- Integration with automation and monitoring systems

**Generated Components:**
- `src/components/watchdog_component.py`
- File change handlers and event processing
- Configuration for watch paths and patterns

### CLI Integration
```bash
--features cli
```
- Full command-line interface for server management
- Configuration management and tool calling
- Status monitoring and log access
- Built-in help and documentation

**Generated Components:**
- `src/cli.py` with complete CLI implementation
- Commands: start, stop, status, config-set, config-get, call-tool, logs
- Integration with the main server for direct communication

### Automation
```bash
--features automation
```
- Scheduled health checks and system monitoring
- Automatic log cleanup and maintenance
- Custom task scheduling with intervals
- Background process management

**Generated Components:**
- `src/components/automation_component.py`
- Health check automation
- Log cleanup scheduling
- Configurable task intervals

### Monitoring
```bash
--features monitoring
```
- System metrics collection (CPU, memory, disk, network)
- Application performance tracking
- Health status reporting
- Export support for external monitoring systems

**Generated Components:**
- `src/components/monitoring_component.py`
- Metrics collection and storage
- Prometheus export capabilities
- Health status aggregation

## 🏗️ Architecture

### Enhanced Template Generator
```
EnhancedMCPCrafter
├── Base Template Generation (from existing mcp-create-server.py)
├── Feature Module System
│   ├── WatchdogModule
│   ├── CLIModule  
│   ├── AutomationModule
│   └── MonitoringModule
├── Template Enhancement Pipeline
├── Configuration Management
└── Integration Validation
```

### Generated Server Structure
```
my-enhanced-server/
├── src/
│   ├── main.py                 # Enhanced main server with all features
│   ├── cli.py                  # CLI interface (if enabled)
│   └── components/
│       ├── __init__.py
│       ├── watchdog_component.py    # File monitoring (if enabled)
│       ├── automation_component.py  # Scheduled tasks (if enabled)
│       └── monitoring_component.py  # Metrics collection (if enabled)
├── pyproject.toml              # Enhanced with feature dependencies
├── docker-compose.yml          # Standard Docker setup
├── docker-compose.enhanced.yml # Enhanced with monitoring stack
├── README.md                   # Feature documentation
├── .env.example               # Feature-specific environment variables
└── tests/
    └── test_server.py         # Basic tests
```

## 🔄 MCP Server Integration

The Enhanced MCP Crafter can be used as an MCP server itself, providing tools for:

### 1. `crafter_generate_server`
Generate enhanced MCP servers with full feature sets:

```json
{
  "name": "weather-service",
  "template": "python-fastmcp",
  "description": "Weather service with monitoring",
  "port": 8060,
  "features": ["watchdog", "cli", "monitoring"],
  "dependencies": ["httpx", "pydantic"],
  "environment": {"API_KEY": "your-key"}
}
```

### 2. `crafter_process_form`
Process Claude forms and requests asynchronously:

```json
{
  "form_type": "server_generation",
  "requirements": {
    "name": "claude-generated-server",
    "features": ["cli", "automation"],
    "description": "Server generated from Claude form"
  },
  "async_mode": true
}
```

### 3. `crafter_add_watchdog`
Add file monitoring to existing servers:

```json
{
  "server_path": "/path/to/existing/server",
  "watch_paths": ["src/", "config/", ".env"]
}
```

### 4. `crafter_enhance_cli`
Add CLI capabilities to existing servers:

```json
{
  "server_path": "/path/to/existing/server",
  "additional_commands": ["backup", "restore"]
}
```

### 5. `crafter_orchestrate`
Orchestrate multiple server operations:

```json
{
  "tasks": [
    {
      "type": "generate",
      "config": {
        "name": "api-server",
        "template": "python-fastmcp",
        "features": ["cli", "monitoring"]
      }
    },
    {
      "type": "generate", 
      "config": {
        "name": "worker-server",
        "template": "minimal-python",
        "features": ["automation"]
      },
      "dependencies": ["api-server"]
    }
  ],
  "execution_mode": "dependency_order"
}
```

### 6. `crafter_continuous_tweak`
Runtime configuration and tweaking:

```json
{
  "server_name": "weather-service",
  "operation": "update_config",
  "parameters": {
    "monitoring.interval": 30,
    "automation.enabled": true
  }
}
```

## 🔧 Configuration Examples

### Environment Variables
```bash
# Core server settings
HOST=localhost
PORT=8055

# Watchdog settings (if enabled)
WATCHDOG_ENABLED=true
WATCH_PATHS=.,config/,src/
WATCHDOG_RECURSIVE=true

# Automation settings (if enabled)
AUTOMATION_ENABLED=true
HEALTH_CHECK_INTERVAL=5m
LOG_CLEANUP_INTERVAL=24h

# Monitoring settings (if enabled)
MONITORING_ENABLED=true
METRICS_COLLECTION_INTERVAL=30
METRICS_EXPORT_ENABLED=false
```

### Docker Compose with Monitoring
```yaml
version: '3.8'
services:
  my-server:
    build: .
    ports:
      - "8055:8055"
    environment:
      - MONITORING_ENABLED=true
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

## 🧪 Testing Generated Servers

Every generated server includes testing capabilities:

```bash
# Navigate to generated server
cd /path/to/generated/server

# Install in development mode
pip install -e .

# Copy and edit configuration
cp .env.example .env

# Test CLI functionality
my-server-cli --help
my-server-cli start --port 8055

# Test server status
my-server-cli status

# Call tools directly
my-server-cli call-tool get_enhanced_status
```

## 🔗 Integration with Existing MCP System

The Enhanced MCP Crafter integrates seamlessly with the existing mcp-system:

### With Claude Bridge
```bash
# The crafter works with existing Claude integration
claude-mcp analyze "Generate a file management server with monitoring"
```

### With MCP Router
Generated servers automatically integrate with the existing MCP router for intelligent request routing.

### With Pipeline Server
Enhanced servers can be orchestrated alongside the existing pipeline server for comprehensive automation workflows.

## 🚀 Advanced Usage

### Custom Feature Modules
The system is designed to be extensible. You can add custom feature modules:

```python
# In enhanced_mcp_crafter.py
def _generate_custom_module(self, request: EnhancedServerRequest) -> Dict[str, str]:
    """Generate your custom feature module"""
    # Implementation here
    return {"src/components/custom_component.py": custom_content}

# Register in feature_modules
self.feature_modules["custom"] = self._generate_custom_module
```

### Orchestration Workflows
Create complex workflows with multiple servers:

```python
orchestration_config = {
    "tasks": [
        {
            "type": "generate",
            "config": {
                "name": "auth-service",
                "template": "python-fastmcp",
                "features": ["cli", "monitoring"],
                "port": 8001
            }
        },
        {
            "type": "generate", 
            "config": {
                "name": "api-gateway",
                "template": "typescript-node",
                "features": ["watchdog", "cli", "monitoring"],
                "port": 8000
            },
            "dependencies": ["auth-service"]
        },
        {
            "type": "enhance",
            "config": {
                "server_path": "/path/to/existing/legacy-server",
                "add_features": ["monitoring", "automation"]
            },
            "dependencies": ["api-gateway"]
        }
    ],
    "execution_mode": "dependency_order"
}
```

## 📖 Best Practices

### 1. **Server Design**
- Use meaningful server names that reflect their purpose
- Include comprehensive descriptions for generated servers
- Choose appropriate ports that don't conflict with existing services
- Select only the features you actually need to minimize complexity

### 2. **Feature Selection**
- **CLI**: Always recommended for development and debugging
- **Monitoring**: Essential for production deployments
- **Watchdog**: Useful for configuration-driven servers
- **Automation**: Recommended for long-running services

### 3. **Development Workflow**
1. Generate server with basic features first
2. Test core functionality
3. Add additional features incrementally
4. Use the CLI interface for debugging and configuration
5. Monitor performance with built-in metrics

### 4. **Production Deployment**
- Always include monitoring and automation features
- Use the enhanced Docker Compose configuration
- Set up proper environment variable management
- Configure log aggregation and alerting
- Test continuous tweaking capabilities before production

## 🔧 Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Ensure Python path is set correctly
   export PYTHONPATH="/path/to/mcp-system:$PYTHONPATH"
   ```

2. **Missing Dependencies**
   ```bash
   # Install required packages
   pip install watchdog schedule psutil click requests
   ```

3. **Port Conflicts**
   ```bash
   # Check for conflicts and use different ports
   netstat -tlnp | grep :8055
   ```

4. **Permission Issues**
   ```bash
   # Ensure scripts are executable
   chmod +x bin/mcp-crafter bin/mcp-crafter-server
   ```

### Debugging Generated Servers

```bash
# Use CLI for debugging
my-server-cli status
my-server-cli logs
my-server-cli call-tool get_enhanced_status

# Check configuration
my-server-cli config-get

# Test individual features
my-server-cli config-set monitoring.enabled true
```

## 🤝 Contributing

The Enhanced MCP Crafter is designed to be extensible. Contributions are welcome for:

- New feature modules
- Additional templates
- Enhanced orchestration capabilities
- Improved error handling and validation
- Documentation and examples

## 📄 License

This project is licensed under the MIT License, consistent with the mcp-system project.

---

## 🎯 Example Workflows

### Weather Service with Full Features
```bash
mcp-crafter weather-service \
  --template python-fastmcp \
  --port 8060 \
  --features watchdog cli automation monitoring \
  --dependencies httpx python-dotenv \
  --env API_KEY=your-weather-api-key \
  --env UPDATE_INTERVAL=300 \
  --description "Weather service with comprehensive monitoring and automation"
```

### File Management System
```bash
mcp-crafter file-manager \
  --template python-fastmcp \
  --port 8065 \
  --features watchdog cli automation \
  --dependencies aiofiles pathspec \
  --env WATCH_DIRECTORIES=/data,/config \
  --description "File management system with automatic organization"
```

### Microservice Orchestration
```python
# Using the MCP server interface
{
  "tool": "crafter_orchestrate",
  "arguments": {
    "tasks": [
      {
        "type": "generate",
        "config": {
          "name": "user-service",
          "template": "python-fastmcp",
          "features": ["cli", "monitoring"],
          "port": 8001
        }
      },
      {
        "type": "generate",
        "config": {
          "name": "notification-service", 
          "template": "typescript-node",
          "features": ["watchdog", "automation"],
          "port": 8002
        }
      },
      {
        "type": "generate",
        "config": {
          "name": "api-gateway",
          "template": "python-fastmcp",
          "features": ["watchdog", "cli", "monitoring", "automation"],
          "port": 8000
        },
        "dependencies": ["user-service", "notification-service"]
      }
    ],
    "execution_mode": "dependency_order"
  }
}
```

This comprehensive system provides the robust resolution and modular architecture needed to build complex, stable MCP servers with built-in automation and continuous tweaking capabilities, exactly as specified in the requirements.