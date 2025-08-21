# Enhanced MCP System: Docker Integration & Environment Detection

This document describes the comprehensive Docker integration and environment detection features implemented for the MCP System.

## 🌟 Overview

The enhanced MCP System provides:

- **Automatic Environment Detection**: Detects Docker, Kubernetes, and local environments
- **Adaptive Configuration**: Configuration automatically adapts based on detected environment  
- **Platform Optimization**: Performance optimizations for different platforms
- **Health Monitoring**: Comprehensive health checks for containerized deployments
- **Real-time Profiling**: Runtime performance monitoring and resource tracking

## 🏗️ Architecture

### Environment Detection System

```
src/config/
├── environment_detector.py    # Core environment detection
├── config_manager.py         # Adaptive configuration management
├── platform_adapter.py       # Platform-specific optimizations
└── runtime_profiler.py       # Performance monitoring
```

**Key Features:**
- Detects Docker containers via multiple methods (/.dockerenv, cgroups, env vars)
- Identifies container types (Docker, containerd, Podman, LXC)
- Kubernetes environment detection
- Platform-specific resource optimization
- Real-time performance profiling

### Docker Integration System

```
src/docker/
└── health_check.py          # Comprehensive health checking
```

**Health Check Components:**
- **Filesystem**: Disk usage, directory accessibility, write permissions
- **Memory**: System and container memory limits, usage monitoring
- **Network**: Connectivity testing, DNS resolution
- **MCP Server**: Server initialization, session management, profiling status
- **Configuration**: Config validation, profile consistency

## 🚀 Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the enhanced MCP server
python src/pipeline_mcp_server.py

# Test environment detection
python demo_enhanced_features.py
```

### Docker Deployment

```bash
# Build enhanced container
docker build -f Dockerfile.enhanced -t mcp-system .

# Run with health checks
docker run -p 8080:8080 --name mcp-server mcp-system

# Check health status
docker exec mcp-server python scripts/docker-health-check.py
```

### Docker Compose (Recommended)

```bash
# Start complete stack with monitoring
docker-compose -f docker-compose.enhanced.yml up

# Start with optional monitoring services
docker-compose -f docker-compose.enhanced.yml --profile monitoring up

# Check service health
docker-compose -f docker-compose.enhanced.yml ps
```

## ⚙️ Configuration

### Environment Variables

The system automatically configures itself but can be customized via environment variables:

```bash
# Environment Detection
MCP_ENV=docker                    # Force environment type
MCP_FORCE_ENVIRONMENT=kubernetes  # Override detection
MCP_AUTO_RELOAD_CONFIG=true       # Enable config reloading

# MCP Server Configuration  
MCP_LOG_LEVEL=INFO               # Logging level
MCP_MAX_WORKERS=4                # Worker processes
MCP_TIMEOUT=300                  # Request timeout
MCP_ENABLE_DASHBOARD=true        # Enable dashboard

# Paths
MCP_WORKSPACE_ROOT=/app          # Workspace directory
MCP_SESSION_DIR=/app/sessions    # Session storage
MCP_DATABASE_PATH=/app/data/db   # Database file
MCP_CACHE_DIR=/app/cache         # Cache directory

# Performance Monitoring
MCP_ENABLE_PROFILING=true        # Enable profiling
MCP_PROFILING_INTERVAL=2.0       # Sampling interval
MCP_PROFILING_HISTORY_SIZE=3600  # History retention
```

### Configuration Profiles

Three built-in profiles automatically selected based on environment:

1. **local-development**: Development settings, debug logging, fewer workers
2. **docker-default**: Production Docker settings, balanced resources
3. **kubernetes-production**: High-performance K8s settings, resource limits

## 🛠️ MCP Tools

### Environment Detection Tool

```bash
# Basic environment detection
mcp-tool environment_detection --action detect

# Get environment summary  
mcp-tool environment_detection --action summary

# Validate configuration
mcp-tool environment_detection --action validate

# Get performance profile
mcp-tool environment_detection --action profile

# Reload configuration
mcp-tool environment_detection --action reload
```

### Health Monitoring Tool

```bash
# Basic health check
mcp-tool health_monitoring --action health_check

# Comprehensive health analysis
mcp-tool health_monitoring --action comprehensive

# Export detailed health report
mcp-tool health_monitoring --action export --export_path /tmp/health.json
```

## 🏥 Health Monitoring

### Container Health Checks

The system provides multiple levels of health monitoring:

1. **Docker HEALTHCHECK**: Basic container health via `scripts/docker-health-check.py`
2. **MCP Tool**: Detailed health analysis via `health_monitoring` tool
3. **API Endpoint**: Health status via HTTP endpoint (if enabled)

### Health Check Responses

```json
{
  "status": "healthy|degraded|unhealthy",
  "timestamp": 1640995200.0,
  "message": "All systems operational",
  "duration_ms": 2.5,
  "issues": []
}
```

### Monitoring Integration

The enhanced Docker Compose includes optional monitoring services:

- **Prometheus**: Metrics collection on port 9090
- **Grafana**: Visualization dashboard on port 3000

```bash
# Start with monitoring
docker-compose -f docker-compose.enhanced.yml --profile monitoring up

# Access Grafana
open http://localhost:3000
# Username: admin, Password: admin
```

## 📊 Performance Monitoring

### Real-time Metrics

The runtime profiler continuously monitors:

- CPU usage percentage
- Memory consumption (RSS)
- Thread count
- Disk I/O operations
- Network traffic
- System load average

### Performance Profiles

```python
# Access profiler in Python
from config.runtime_profiler import runtime_profiler

# Get real-time metrics
metrics = runtime_profiler.get_real_time_metrics()

# Get performance summary
summary = runtime_profiler.get_resource_usage_summary()

# Export detailed profile
runtime_profiler.export_profile("/tmp/profile.json")
```

## 🔧 Development

### Testing Environment Detection

```bash
# Run environment detection tests
pytest tests/test_environment_detection.py -v

# Test Docker health checks
python scripts/docker-health-check.py

# Run the demo
python demo_enhanced_features.py
```

### Adding Custom Configuration Profiles

1. Create profile file in `src/config/profiles/`:

```json
{
  "name": "custom-profile",
  "description": "Custom configuration profile",
  "enabled": true,
  "settings": {
    "workspace_root": "/custom",
    "max_workers": 8,
    "log_level": "INFO",
    "security_settings": {
      "allowed_paths": ["/custom", "/tmp"],
      "max_file_size_mb": 50
    }
  }
}
```

2. Apply profile programmatically:

```python
from config.config_manager import config_manager
config_manager.apply_config_profile("custom-profile")
```

## 🐳 Production Deployment

### Security Considerations

The enhanced Docker configuration includes security best practices:

- **Non-root user**: Containers run as `mcpuser`
- **Multi-stage builds**: Minimal attack surface
- **Resource limits**: CPU and memory constraints
- **Network isolation**: Dedicated Docker network
- **Health monitoring**: Automated failure detection

### Scaling

For production scaling:

1. **Horizontal**: Multiple container instances behind load balancer
2. **Vertical**: Adjust CPU/memory limits via environment variables
3. **Kubernetes**: Use the kubernetes-production profile for K8s deployments

### Backup and Recovery

Important data volumes:

- `mcp-data`: Database and persistent state
- `mcp-sessions`: Active pipeline sessions  
- `mcp-logs`: Application logs
- `mcp-cache`: Performance cache

```bash
# Backup volumes
docker run --rm -v mcp-data:/data -v $(pwd):/backup alpine tar czf /backup/mcp-data.tar.gz /data

# Restore volumes  
docker run --rm -v mcp-data:/data -v $(pwd):/backup alpine tar xzf /backup/mcp-data.tar.gz -C /
```

## 🎯 Migration Guide

### From Basic to Enhanced Docker Setup

1. **Backup existing data**:
   ```bash
   docker-compose down
   docker run --rm -v mcp_sessions:/data alpine tar czf sessions-backup.tar.gz /data
   ```

2. **Switch to enhanced configuration**:
   ```bash
   docker build -f Dockerfile.enhanced -t mcp-system .
   docker-compose -f docker-compose.enhanced.yml up
   ```

3. **Verify health status**:
   ```bash
   docker exec mcp-pipeline-server python scripts/docker-health-check.py
   ```

## 📚 API Reference

### Environment Detection API

All environment detection functions are available via the MCP `environment_detection` tool:

- `detect`: Full environment information
- `summary`: Concise environment summary
- `config`: Current configuration details
- `validate`: Configuration validation
- `reload`: Reload configuration
- `profile`: Performance profiling data
- `optimize`: Platform optimizations

### Health Monitoring API

Health monitoring via the MCP `health_monitoring` tool:

- `health_check`: Basic health status
- `comprehensive`: Detailed health analysis  
- `export`: Export health report to file

## 🤝 Contributing

When contributing to the enhanced Docker features:

1. **Test environment detection** across different platforms
2. **Validate health checks** in various deployment scenarios
3. **Update documentation** for new configuration options
4. **Add tests** for new environment detection features

## 📝 Changelog

### v2.0.0 - Enhanced Docker Integration

- ✅ Comprehensive environment detection system
- ✅ Adaptive configuration management  
- ✅ Platform-specific optimizations
- ✅ Docker health monitoring system
- ✅ Real-time performance profiling
- ✅ Enhanced MCP tools (environment_detection, health_monitoring)
- ✅ Production-ready Docker configuration
- ✅ Kubernetes support
- ✅ Comprehensive test suite

---

**Next Steps**: The enhanced MCP System is now ready for production Docker deployments with comprehensive monitoring, adaptive configuration, and health checking capabilities.