# Claude Desktop Integration

To use the Orchestrator MCP server with Claude Desktop, add the following configuration to your Claude Desktop configuration file:

## Configuration File Location

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

## Configuration

```json
{
  "mcpServers": {
    "orchestrator": {
      "command": "python",
      "args": [
        "-m", 
        "orchestrator.main"
      ],
      "cwd": "/path/to/mcp-system/mcp-tools/orchestrator",
      "env": {
        "MCP_WORKSPACE_ROOT": "/path/to/mcp-system",
        "MCP_SESSION_DIR": "./pipeline-sessions",
        "DOCKER_HOST": "unix:///var/run/docker.sock",
        "WATCHDOG_ENABLED": "true",
        "MCP_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

## Windows WSL Configuration

For Windows users with WSL2 and Docker Desktop:

```json
{
  "mcpServers": {
    "orchestrator": {
      "command": "wsl",
      "args": [
        "-d", "Ubuntu",
        "python3",
        "-m", "orchestrator.main"
      ],
      "cwd": "/mnt/c/path/to/mcp-system/mcp-tools/orchestrator",
      "env": {
        "WSL_DISTRO": "Ubuntu",
        "WSL_USER": "yourusername",
        "DOCKER_DESKTOP_ENABLED": "true",
        "MCP_WORKSPACE_ROOT": "/mnt/c/path/to/mcp-system",
        "WATCHDOG_ENABLED": "true"
      }
    }
  }
}
```

## Verification

1. Restart Claude Desktop after adding the configuration
2. In a new conversation, you should see "orchestrator" in the available MCP tools
3. Test with a simple command:
   ```
   Use the orchestrator to check Docker status
   ```

## Available Tools

The orchestrator provides these tools:

1. **docker_operation** - Execute Docker commands with WSL integration
2. **environment_setup** - Setup and configure MCP environment  
3. **container_management** - Manage Docker container lifecycle
4. **watchdog_monitoring** - Monitor file systems and services
5. **cli_resolution** - Execute CLI commands safely
6. **windows_integration** - Windows-specific Docker operations
7. **health_monitoring** - System and Docker health checks
8. **deployment_orchestration** - Automate deployment workflows

## Troubleshooting

### Tool Not Appearing
- Check Claude Desktop logs for connection errors
- Verify the Python path and working directory
- Ensure all dependencies are installed

### Docker Integration Issues
- Verify Docker Desktop is running
- Check Docker socket permissions
- For WSL: Ensure WSL2 integration is enabled in Docker Desktop

### Permission Issues
- Ensure the user has Docker socket access
- For Linux: Add user to docker group: `sudo usermod -aG docker $USER`
- For Windows: Ensure Docker Desktop has WSL integration enabled