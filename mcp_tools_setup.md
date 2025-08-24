# MCP Tools Setup and Standardization Guide

## Overview

The `mcp-tools` directory serves as the standardized location for all MCP (Model Context Protocol) servers within the MCP System. This guide outlines the standard folder structure, watchdog monitoring system, and best practices for organizing MCP tools.

## Standard Directory Structure

### Root Structure
```
mcp-tools/
├── <server-name>/          # Individual MCP server directory
│   ├── src/                # Source code
│   │   └── main.py        # Main server entry point
│   ├── tests/             # Test files
│   │   └── test_server.py # Server tests
│   ├── README.md          # Server documentation
│   ├── pyproject.toml     # Python project configuration
│   ├── .env.example       # Environment variables template
│   ├── Dockerfile         # Docker configuration
│   └── docker-compose.yml # Docker Compose configuration
├── _templates/            # Server templates (created by system)
├── _standards/            # Standard configurations
└── _monitoring/           # Watchdog monitoring logs
```

### Required Files for Each MCP Server

1. **src/main.py** - Main server implementation
2. **README.md** - Server documentation and usage
3. **pyproject.toml** - Python dependencies and project metadata
4. **.env.example** - Environment variables template
5. **tests/test_server.py** - Basic server tests
6. **Dockerfile** - Container configuration
7. **docker-compose.yml** - Service orchestration

## Watchdog Monitoring System

The MCP Tools directory uses the Python `watchdog` library to monitor file changes and enforce standardization.

### Monitoring Features

- **File Creation Monitoring**: Automatically validates new files against standards
- **Structure Validation**: Ensures required directories and files exist
- **Real-time Updates**: Monitors changes to configuration files
- **Path Standardization**: Automatically updates references to moved files

### Monitored Events

1. **File Creation**: Validates structure compliance
2. **File Modification**: Checks for configuration updates
3. **File Deletion**: Warns about missing required files
4. **Directory Changes**: Maintains structure integrity

## Path Standardization

### Standard Paths

All MCP server references should use the standardized `mcp-tools/` prefix:

```json
{
  "server-name": {
    "name": "My MCP Server",
    "path": "mcp-tools/server-name",
    "command": "python src/main.py",
    "transport": "stdio"
  }
}
```

### Legacy Path Migration

The system automatically updates legacy paths to the standard format:

- `~/mcp-*` → `mcp-tools/*`
- `./servers/*` → `mcp-tools/*`
- Relative paths → `mcp-tools/*`

## Creating New MCP Servers

### Using the Generator

```bash
# Create a new MCP server in the standard location
python core/mcp-create-server.py --name my-server --template python-official

# Server will be created at: mcp-tools/my-server/
```

### Manual Creation

1. Create directory: `mcp-tools/your-server-name/`
2. Copy from template or existing server
3. Update configuration files
4. Register in `configs/.mcp-servers.json`

## Configuration Management

### Server Registration

Add your server to `configs/.mcp-servers.json`:

```json
{
  "your-server": {
    "name": "Your MCP Server",
    "path": "mcp-tools/your-server",
    "command": "python src/main.py",
    "transport": "stdio",
    "env_file": ".env",
    "dependencies": {}
  }
}
```

### Environment Variables

Each server should include:

- `.env.example` - Template with all required variables
- `.env` - Local configuration (git-ignored)
- Environment variable validation in `src/main.py`

## Validation and Testing

### Structure Validation

```bash
# Validate all mcp-tools servers
python scripts/validate_mcp_tools.py

# Validate specific server
python scripts/validate_mcp_tools.py --server server-name
```

### Automated Testing

```bash
# Run tests for all servers
cd mcp-tools && find . -name "test_*.py" -exec python -m pytest {} \;

# Test specific server
cd mcp-tools/server-name && python -m pytest tests/
```

## Monitoring and Logs

### Watchdog Logs

Monitor file system events:

```bash
# View monitoring logs
tail -f mcp-tools/_monitoring/watchdog.log

# View structure validation logs
tail -f mcp-tools/_monitoring/validation.log
```

### Health Checks

```bash
# Check all servers health
python scripts/health_check_mcp_tools.py

# Check specific server
python scripts/health_check_mcp_tools.py --server server-name
```

## Best Practices

### Directory Naming

- Use kebab-case: `my-server-name`
- Descriptive but concise names
- Avoid special characters except hyphens

### File Organization

- Keep source code in `src/` directory
- Tests in `tests/` directory
- Documentation in root `README.md`
- Configuration files in root directory

### Version Management

- Use semantic versioning in `pyproject.toml`
- Tag releases appropriately
- Maintain CHANGELOG.md for significant changes

### Documentation

- Clear README.md with usage examples
- Inline code documentation
- API documentation for tools and resources

## Troubleshooting

### Common Issues

1. **Server not found**: Check path in `.mcp-servers.json`
2. **Permission errors**: Ensure proper file permissions
3. **Missing dependencies**: Check `pyproject.toml` and install requirements
4. **Port conflicts**: Update port assignments in configuration

### Debug Mode

Enable debug logging:

```bash
export MCP_DEBUG=1
python scripts/mcp_tools_monitor.py --debug
```

## Migration Guide

### Migrating Existing Servers

1. Move server directory to `mcp-tools/`
2. Update path in `.mcp-servers.json`
3. Validate structure with validation script
4. Test server functionality
5. Update any hardcoded paths in code

### Batch Migration

```bash
# Migrate all servers to standard location
python scripts/migrate_to_mcp_tools.py --all

# Migrate specific server
python scripts/migrate_to_mcp_tools.py --server server-name
```

## Integration with MCP System

The mcp-tools directory integrates with:

- **MCP Server Management**: Automatic discovery and registration
- **Docker Orchestration**: Standardized container deployment
- **Pipeline Integration**: Automated testing and validation
- **Configuration Management**: Centralized server configuration

## Security Considerations

- Environment files (`.env`) are git-ignored
- Secrets should use environment variables
- Regular security scans with bandit
- Container security best practices

---

*This documentation is maintained automatically by the MCP System watchdog monitoring. Last updated: 2025-08-24T23:06:00Z*