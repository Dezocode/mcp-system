#!/usr/bin/env python3
"""
MCP Server Generator - Create new MCP servers from templates
"""

import argparse
import json
import sys
from pathlib import Path


class MCPServerGenerator:
    def __init__(self):
        self.templates_dir = Path.home() / ".mcp-templates"
        self.templates_dir.mkdir(exist_ok=True)

        self.templates = {
            "python-official": {
                "name": "Python Official MCP Server",
                "description": "Python server using official Anthropic MCP protocol",
                "files": [
                    "src/main.py",
                    "pyproject.toml",
                    ".env.example",
                    "README.md",
                    "Dockerfile",
                    "docker-compose.yml",
                    "tests/test_server.py",
                ],
            },
            "python-fastmcp": {
                "name": "Python FastMCP Server (Legacy)",
                "description": "Python server using FastMCP framework (not recommended)",
                "files": [
                    "src/main.py",
                    "pyproject.toml",
                    ".env.example",
                    "README.md",
                    "Dockerfile",
                    "docker-compose.yml",
                    "tests/test_server.py",
                ],
            },
            "typescript-node": {
                "name": "TypeScript Node.js Server",
                "description": "TypeScript server using Node.js",
                "files": [
                    "src/index.ts",
                    "package.json",
                    "tsconfig.json",
                    ".env.example",
                    "README.md",
                    "Dockerfile",
                    "tests/server.test.ts",
                ],
            },
            "minimal-python": {
                "name": "Minimal Python Server",
                "description": "Bare-bones Python MCP server",
                "files": [
                    "main.py",
                    "requirements.txt",
                    ".env.example",
                    "README.md",
                ],
            },
        }

    def create_python_official_template(
        self, server_name: str, port: int, description: str
    ) -> dict:
        """Generate Python MCP server template using official Anthropic protocol"""

        # Main server file using official MCP protocol
        main_py = f'''#!/usr/bin/env python3
"""
{server_name} - Official MCP Server
{description}

This server follows the official Anthropic MCP protocol specification.
"""

import asyncio
import json
import logging
from typing import Any, Sequence
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types
from pydantic import AnyUrl

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("{server_name}")

# Server metadata
SERVER_NAME = "{server_name}"
SERVER_VERSION = "0.1.0"

class {server_name.title().replace("-", "")}Server:
    """
    Official MCP Server implementation for {server_name}.
    
    Follows Anthropic MCP protocol specification:
    - Uses stdio transport (recommended by Anthropic)
    - Implements standard MCP capabilities
    - Provides proper error handling
    """
    
    def __init__(self):
        self.server = Server(SERVER_NAME)
        self.setup_handlers()
    
    def setup_handlers(self):
        """Set up MCP protocol handlers following official patterns."""
        
        @self.server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            """
            List available tools.
            
            Returns the tools offered by this server.
            """
            return [
                types.Tool(
                    name="hello_world",
                    description="Say hello to someone",
                    inputSchema={{
                        "type": "object",
                        "properties": {{
                            "name": {{
                                "type": "string",
                                "description": "The name to greet"
                            }}
                        }},
                        "required": []
                    }}
                ),
                types.Tool(
                    name="get_status",
                    description="Get server status information",
                    inputSchema={{
                        "type": "object",
                        "properties": {{}},
                        "required": []
                    }}
                ),
                types.Tool(
                    name="example_tool",
                    description="Example tool demonstrating parameter handling",
                    inputSchema={{
                        "type": "object",
                        "properties": {{
                            "param1": {{
                                "type": "string",
                                "description": "A required string parameter"
                            }},
                            "param2": {{
                                "type": "integer",
                                "description": "An optional integer parameter",
                                "default": 10
                            }}
                        }},
                        "required": ["param1"]
                    }}
                )
            ]

        @self.server.call_tool()
        async def handle_call_tool(
            name: str, arguments: dict[str, Any] | None
        ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
            """
            Handle tool calls.
            
            Args:
                name: The name of the tool to call
                arguments: The arguments for the tool
                
            Returns:
                The result of the tool call
            """
            if arguments is None:
                arguments = {{}}

            try:
                if name == "hello_world":
                    return await self.hello_world(**arguments)
                elif name == "get_status":
                    return await self.get_status(**arguments)
                elif name == "example_tool":
                    return await self.example_tool(**arguments)
                else:
                    raise ValueError(f"Unknown tool: {{name}}")
            except Exception as e:
                logger.error(f"Error in tool {{name}}: {{e}}")
                raise

    async def hello_world(self, name: str = "World") -> list[types.TextContent]:
        """
        Say hello to someone.
        
        Args:
            name: The name to greet
            
        Returns:
            A greeting message
        """
        message = f"Hello, {{name}}! This is {{SERVER_NAME}} server."
        return [types.TextContent(type="text", text=message)]

    async def get_status(self) -> list[types.TextContent]:
        """
        Get server status information.
        
        Returns:
            Server status information in JSON format
        """
        status = {{
            "server": SERVER_NAME,
            "version": SERVER_VERSION,
            "status": "running",
            "description": "{description}",
            "capabilities": [
                "tools"
            ]
        }}
        return [types.TextContent(type="text", text=json.dumps(status, indent=2))]

    async def example_tool(self, param1: str, param2: int = 10) -> list[types.TextContent]:
        """
        Example tool demonstrating parameter handling.
        
        Args:
            param1: A required string parameter
            param2: An optional integer parameter (default: 10)
            
        Returns:
            Result of the operation
        """
        result = f"Processed '{{param1}}' with value {{param2}}"
        return [types.TextContent(type="text", text=result)]

    async def run(self):
        """Run the server using stdio transport (Anthropic recommended)."""
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name=SERVER_NAME,
                    server_version=SERVER_VERSION,
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={{}}
                    )
                )
            )


async def main():
    """Main entry point for the MCP server."""
    logger.info(f"Starting {{SERVER_NAME}} v{{SERVER_VERSION}}")
    logger.info("Using stdio transport (Anthropic MCP standard)")
    
    server = {server_name.title().replace("-", "")}Server()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
'''

        # pyproject.toml - Official MCP dependencies
        pyproject_toml = f"""[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "{server_name}"
version = "0.1.0"
description = "{description}"
authors = [
    {{name = "Your Name", email = "your.email@example.com"}}
]
readme = "README.md"
requires-python = ">=3.10"
dependencies = [
    "mcp>=1.0.0",
    "pydantic>=2.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "black>=23.0.0",
    "isort>=5.12.0",
    "mypy>=1.0.0",
    "pre-commit>=3.0.0",
    "ruff>=0.1.0",
]

[project.scripts]
{server_name} = "{server_name.replace('-', '_')}.main:main"

[tool.black]
line-length = 88
target-version = ['py310']
include = '\\.pyi?$'
extend-exclude = '''
/(
  # directories
  \\.eggs
  | \\.git
  | \\.hg
  | \\.mypy_cache
  | \\.tox
  | \\.venv
  | build
  | dist
)/
'''

[tool.isort]
profile = "black"
multi_line_output = 3
include_trailing_comma = true
force_grid_wrap = 0
use_parentheses = true
ensure_newline_before_comments = true
line_length = 88

[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_equality = true

[tool.ruff]
target-version = "py310"
line-length = 88
select = [
    "E",  # pycodestyle errors
    "W",  # pycodestyle warnings
    "F",  # pyflakes
    "I",  # isort
    "B",  # flake8-bugbear
    "C4", # flake8-comprehensions
    "UP", # pyupgrade
]
ignore = [
    "E501",  # line too long, handled by black
    "B008",  # do not perform function calls in argument defaults
    "C901",  # too complex
]

[tool.ruff.per-file-ignores]
"__init__.py" = ["F401"]
"""

        # .env.example - MCP standard configuration
        env_example = f"""# {server_name.upper()} MCP Server Configuration

# MCP server settings (optional - stdio is preferred)
# MCP_SERVER_PORT={port}
# MCP_SERVER_HOST=localhost

# Logging configuration
# LOG_LEVEL=INFO
# LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s

# Add your service-specific environment variables here
# DATABASE_URL=postgresql://user:pass@localhost:5432/{server_name.replace("-", "_")}
# API_KEY=your-api-key-here
# DEBUG=false

# Development settings
# DEVELOPMENT=true
"""

        # README.md - Official MCP standards documentation
        readme_md = f"""# {server_name.title().replace("-", " ")} MCP Server

{description}

This MCP server follows the **official Anthropic MCP protocol specification** and implements the standard MCP capabilities using stdio transport.

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

### Installation

1. **Clone and navigate to the server directory:**
   ```bash
   git clone <repository-url>
   cd {server_name}
   ```

2. **Install dependencies:**
   ```bash
   # Using uv (recommended)
   uv sync

   # Or using pip
   pip install -e .
   ```

3. **Configure environment (optional):**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration if needed
   ```

## 📋 Available Tools

This MCP server provides the following tools:

| Tool | Description | Parameters |
|------|-------------|------------|
| `hello_world` | Say hello to someone | `name` (optional): The name to greet |
| `get_status` | Get server status information | None |
| `example_tool` | Example tool demonstrating parameter handling | `param1` (required): String parameter<br>`param2` (optional): Integer parameter |

## 🔧 Usage

### Command Line Interface

```bash
# Run the server directly (stdio transport)
python src/main.py

# Or using the installed script
{server_name}

# Or with uv
uv run python src/main.py
```

### Claude Desktop Integration

Add this server to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{{
  "mcpServers": {{
    "{server_name}": {{
      "command": "uv",
      "args": ["run", "python", "/path/to/{server_name}/src/main.py"],
      "env": {{
        "LOG_LEVEL": "INFO"
      }}
    }}
  }}
}}
```

### Manual MCP Client Integration

If you're integrating with a custom MCP client:

```python
from mcp.client import StdioMCPClient

# Connect to the server
client = StdioMCPClient()
await client.connect(
    command=["python", "/path/to/{server_name}/src/main.py"]
)

# List available tools
tools = await client.list_tools()

# Call a tool
result = await client.call_tool("hello_world", {{"name": "World"}})
```

## 🏗️ Development

### Project Structure

```
{server_name}/
├── src/
│   └── main.py          # Main MCP server implementation
├── tests/
│   └── test_server.py   # Test suite
├── pyproject.toml       # Project configuration
├── .env.example         # Environment template
├── README.md           # This file
└── Dockerfile          # Container configuration
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov={server_name.replace('-', '_')}

# Run specific test
uv run pytest tests/test_server.py::test_hello_world
```

### Code Quality

```bash
# Format code
uv run black src/ tests/
uv run isort src/ tests/

# Lint code
uv run ruff check src/ tests/

# Type checking
uv run mypy src/
```

## 🐳 Docker Deployment

Build and run with Docker:

```bash
# Build image
docker build -t {server_name} .

# Run container
docker run --rm {server_name}

# Or with docker-compose
docker-compose up
```

## 🔧 Configuration

The server uses environment variables for configuration. See `.env.example` for available options.

### Important Configuration Notes

- **Transport**: This server uses stdio transport (Anthropic's recommended method)
- **No HTTP server**: Unlike FastMCP, this implementation follows the official MCP standard
- **Logging**: Configured via LOG_LEVEL environment variable

## 📚 MCP Protocol Reference

This server implements the official MCP protocol:

- **Protocol Version**: 2024-11-05
- **Transport**: stdio (stdin/stdout)
- **Capabilities**: tools
- **Documentation**: [Anthropic MCP Docs](https://docs.anthropic.com/mcp)

### Tool Call Format

Tools expect parameters in this format:

```json
{{
  "name": "tool_name",
  "arguments": {{
    "param1": "value1",
    "param2": "value2"
  }}
}}
```

### Response Format

Responses follow the MCP content format:

```json
[
  {{
    "type": "text",
    "text": "Response content here"
  }}
]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes following the code style
4. Run tests and ensure they pass
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔗 Additional Resources

- [Official MCP Documentation](https://docs.anthropic.com/mcp)
- [MCP Protocol Specification](https://docs.anthropic.com/mcp/specification)
- [Claude Desktop Configuration](https://docs.anthropic.com/claude/claude-desktop)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
"""

        # Dockerfile - Official MCP server container
        dockerfile = f"""# Official MCP Server Dockerfile
# Multi-stage build for smaller production image
FROM python:3.11-slim as builder

# Set build arguments
ARG BUILD_DATE
ARG VERSION=0.1.0

# Add metadata
LABEL org.opencontainers.image.title="{server_name}"
LABEL org.opencontainers.image.description="{description}"
LABEL org.opencontainers.image.version=$VERSION
LABEL org.opencontainers.image.created=$BUILD_DATE
LABEL org.opencontainers.image.source="https://github.com/your-org/{server_name}"
LABEL org.opencontainers.image.licenses="MIT"

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    build-essential \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Install uv for faster dependency management
RUN pip install uv

# Set up working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml ./
COPY README.md ./

# Install dependencies
RUN uv venv && uv pip install -e .

# Production stage
FROM python:3.11-slim as production

# Create non-root user for security
RUN groupadd -r mcpuser && useradd -r -g mcpuser mcpuser

# Set working directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy source code
COPY src/ ./src/

# Set ownership and permissions
RUN chown -R mcpuser:mcpuser /app
USER mcpuser

# Set environment variables
ENV PYTHONPATH=/app
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL=INFO

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD python -c "import sys; sys.exit(0)" || exit 1

# Default command (stdio transport)
CMD ["python", "src/main.py"]
"""

        # docker-compose.yml - MCP server composition
        docker_compose = f"""version: '3.8'

services:
  {server_name}:
    build: 
      context: .
      args:
        BUILD_DATE: ${{BUILD_DATE:-$(date -u +'%Y-%m-%dT%H:%M:%SZ')}}
        VERSION: ${{VERSION:-0.1.0}}
    environment:
      - LOG_LEVEL=INFO
      - PYTHONUNBUFFERED=1
    restart: unless-stopped
    # Note: MCP servers use stdio transport, not HTTP ports
    # volumes:
    #   - ./data:/app/data
    #   - ./.env:/app/.env
    
    # Uncomment if your MCP server needs external services
    # depends_on:
    #   - database
    #   - redis

  # Example database service (uncomment if needed)
  # database:
  #   image: postgres:15-alpine
  #   environment:
  #     POSTGRES_DB: {server_name.replace("-", "_")}
  #     POSTGRES_USER: postgres
  #     POSTGRES_PASSWORD: password
  #   volumes:
  #     - postgres_data:/var/lib/postgresql/data
  #   ports:
  #     - "5432:5432"
  #   healthcheck:
  #     test: ["CMD-SHELL", "pg_isready -U postgres"]
  #     interval: 10s
  #     timeout: 5s
  #     retries: 5

  # Example Redis service (uncomment if needed)
  # redis:
  #   image: redis:7-alpine
  #   ports:
  #     - "6379:6379"
  #   volumes:
  #     - redis_data:/data
  #   healthcheck:
  #     test: ["CMD", "redis-cli", "ping"]
  #     interval: 10s
  #     timeout: 3s
  #     retries: 3

# Uncomment if using persistent volumes
# volumes:
#   postgres_data:
#   redis_data:

networks:
  default:
    name: {server_name}_network
"""

        # Test file - Official MCP protocol tests
        test_py = f'''"""
Tests for {server_name} MCP server

Tests the official MCP protocol implementation.
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch
import mcp.types as types

# Import the server class
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from main import {server_name.title().replace("-", "")}Server


class TestMCPServer:
    """Test suite for the MCP server implementation."""

    @pytest.fixture
    async def server(self):
        """Create a test server instance."""
        return {server_name.title().replace("-", "")}Server()

    @pytest.mark.asyncio
    async def test_server_initialization(self, server):
        """Test that the server initializes correctly."""
        assert server.server.name == "{server_name}"
        assert hasattr(server, 'hello_world')
        assert hasattr(server, 'get_status')
        assert hasattr(server, 'example_tool')

    @pytest.mark.asyncio
    async def test_list_tools(self, server):
        """Test the list_tools handler."""
        # Mock the server's list_tools handler
        tools = await server.server._tool_handlers["list_tools"]()
        
        assert len(tools) == 3
        
        # Check hello_world tool
        hello_tool = next(tool for tool in tools if tool.name == "hello_world")
        assert hello_tool.description == "Say hello to someone"
        assert "name" in hello_tool.inputSchema["properties"]
        
        # Check get_status tool
        status_tool = next(tool for tool in tools if tool.name == "get_status")
        assert status_tool.description == "Get server status information"
        
        # Check example_tool
        example_tool = next(tool for tool in tools if tool.name == "example_tool")
        assert example_tool.description == "Example tool demonstrating parameter handling"
        assert "param1" in example_tool.inputSchema["properties"]
        assert "param2" in example_tool.inputSchema["properties"]

    @pytest.mark.asyncio
    async def test_hello_world_tool(self, server):
        """Test the hello_world tool."""
        # Test with default name
        result = await server.hello_world()
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Hello, World!" in result[0].text
        assert "{server_name}" in result[0].text

        # Test with custom name
        result = await server.hello_world(name="Alice")
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Hello, Alice!" in result[0].text

    @pytest.mark.asyncio
    async def test_get_status_tool(self, server):
        """Test the get_status tool."""
        result = await server.get_status()
        assert len(result) == 1
        assert result[0].type == "text"
        
        # Parse the JSON response
        status_data = json.loads(result[0].text)
        assert status_data["server"] == "{server_name}"
        assert status_data["version"] == "0.1.0"
        assert status_data["status"] == "running"
        assert "capabilities" in status_data

    @pytest.mark.asyncio
    async def test_example_tool(self, server):
        """Test the example_tool."""
        # Test with required parameter only
        result = await server.example_tool(param1="test")
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Processed 'test' with value 10" in result[0].text

        # Test with both parameters
        result = await server.example_tool(param1="test", param2=20)
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Processed 'test' with value 20" in result[0].text

    @pytest.mark.asyncio
    async def test_call_tool_handler(self, server):
        """Test the call_tool handler with various scenarios."""
        call_tool_handler = server.server._tool_handlers["call_tool"]
        
        # Test hello_world
        result = await call_tool_handler("hello_world", {{"name": "Test"}})
        assert len(result) == 1
        assert "Hello, Test!" in result[0].text
        
        # Test with empty arguments
        result = await call_tool_handler("hello_world", {{}})
        assert len(result) == 1
        assert "Hello, World!" in result[0].text
        
        # Test with None arguments
        result = await call_tool_handler("hello_world", None)
        assert len(result) == 1
        assert "Hello, World!" in result[0].text
        
        # Test unknown tool
        with pytest.raises(ValueError, match="Unknown tool"):
            await call_tool_handler("unknown_tool", {{}})

    @pytest.mark.asyncio
    async def test_tool_error_handling(self, server):
        """Test error handling in tool calls."""
        call_tool_handler = server.server._tool_handlers["call_tool"]
        
        # Test with invalid parameters (should raise appropriate error)
        with pytest.raises(TypeError):
            await call_tool_handler("example_tool", {{"param2": "not_an_int"}})

    def test_server_metadata(self, server):
        """Test server metadata and configuration."""
        assert hasattr(server, 'server')
        assert server.server.name == "{server_name}"

    @pytest.mark.asyncio 
    async def test_mcp_protocol_compliance(self, server):
        """Test MCP protocol compliance."""
        # Test that tools return proper MCP content types
        result = await server.hello_world()
        assert all(isinstance(content, types.TextContent) for content in result)
        assert all(content.type == "text" for content in result)
        
        result = await server.get_status()
        assert all(isinstance(content, types.TextContent) for content in result)
        
        result = await server.example_tool("test")
        assert all(isinstance(content, types.TextContent) for content in result)


# Integration tests
class TestMCPIntegration:
    """Integration tests for MCP server."""

    @pytest.mark.asyncio
    async def test_full_workflow(self):
        """Test a complete MCP workflow."""
        server = {server_name.title().replace("-", "")}Server()
        
        # List tools
        tools = await server.server._tool_handlers["list_tools"]()
        assert len(tools) > 0
        
        # Call each tool
        call_tool = server.server._tool_handlers["call_tool"]
        
        # Test hello_world
        result = await call_tool("hello_world", {{"name": "Integration Test"}})
        assert "Integration Test" in result[0].text
        
        # Test get_status
        result = await call_tool("get_status", {{}})
        status = json.loads(result[0].text)
        assert status["server"] == "{server_name}"
        
        # Test example_tool
        result = await call_tool("example_tool", {{"param1": "integration", "param2": 42}})
        assert "integration" in result[0].text
        assert "42" in result[0].text


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
'''

        return {
            "src/main.py": main_py,
            "pyproject.toml": pyproject_toml,
            ".env.example": env_example,
            "README.md": readme_md,
            "Dockerfile": dockerfile,
            "docker-compose.yml": docker_compose,
            "tests/test_server.py": test_py,
        }

    def create_typescript_template(
        self, server_name: str, port: int, description: str
    ) -> dict:
        """Generate TypeScript Node.js server template"""

        # package.json
        package_json = {
            "name": server_name,
            "version": "1.0.0",
            "description": description,
            "main": "dist/index.js",
            "scripts": {
                "build": "tsc",
                "start": "node dist/index.js",
                "dev": "ts-node src/index.ts",
                "test": "jest",
                "lint": "eslint src/**/*.ts",
                "format": "prettier --write src/**/*.ts",
            },
            "dependencies": {
                "@modelcontextprotocol/sdk": "latest",
                "dotenv": "^16.0.0",
                "express": "^4.18.0",
                "cors": "^2.8.5",
            },
            "devDependencies": {
                "@types/node": "^20.0.0",
                "@types/express": "^4.17.0",
                "@types/cors": "^2.8.0",
                "typescript": "^5.0.0",
                "ts-node": "^10.9.0",
                "jest": "^29.0.0",
                "@types/jest": "^29.0.0",
                "eslint": "^8.0.0",
                "prettier": "^3.0.0",
            },
        }

        # TypeScript main file
        index_ts = f"""/**
 * {server_name} MCP Server
 * {description}
 */

import {{ Server }} from '@modelcontextprotocol/sdk/server/index.js';
import {{ StdioServerTransport }} from '@modelcontextprotocol/sdk/server/stdio.js';
import {{
  CallToolRequestSchema,
  ErrorCode,
  ListToolsRequestSchema,
  McpError,
}} from '@modelcontextprotocol/sdk/types.js';
import express from 'express';
import cors from 'cors';
import * as dotenv from 'dotenv';

// Load environment variables
dotenv.config();

const SERVER_NAME = '{server_name}';
const SERVER_PORT = process.env.PORT ? parseInt(process.env.PORT) : {port};
const SERVER_HOST = process.env.HOST || 'localhost';

// Server state
interface ServerState {{
  initialized: boolean;
  startTime: Date;
}}

const state: ServerState = {{
  initialized: false,
  startTime: new Date()
}};

// Create MCP server
const server = new Server(
  {{
    name: SERVER_NAME,
    version: '1.0.0',
    description: '{description}'
  }},
  {{
    capabilities: {{
      tools: {{}}
    }}
  }}
);

// Tool definitions
const tools = [
  {{
    name: 'hello_world',
    description: 'Say hello to someone',
    inputSchema: {{
      type: 'object',
      properties: {{
        name: {{
          type: 'string',
          description: 'The name to greet',
          default: 'World'
        }}
      }}
    }}
  }},
  {{
    name: 'get_status',
    description: 'Get server status information',
    inputSchema: {{
      type: 'object',
      properties: {{}}
    }}
  }},
  {{
    name: 'example_tool',
    description: 'Example tool demonstrating parameter handling',
    inputSchema: {{
      type: 'object',
      properties: {{
        param1: {{
          type: 'string',
          description: 'A required string parameter'
        }},
        param2: {{
          type: 'number',
          description: 'An optional number parameter',
          default: 10
        }}
      }},
      required: ['param1']
    }}
  }}
];

// List tools handler
server.setRequestHandler(ListToolsRequestSchema, async () => {{
  return {{ tools }};
}});

// Call tool handler
server.setRequestHandler(CallToolRequestSchema, async (request) => {{
  const {{ name, arguments: args }} = request.params;

  switch (name) {{
    case 'hello_world': {{
      const name = args?.name || 'World';
      return {{
        content: [
          {{
            type: 'text',
            text: `Hello, ${{name}}! This is ${{SERVER_NAME}} server.`
          }}
        ]
      }};
    }}

    case 'get_status': {{
      const status = {{
        server: SERVER_NAME,
        status: 'running',
        initialized: state.initialized,
        port: SERVER_PORT,
        uptime: Date.now() - state.startTime.getTime()
      }};

      return {{
        content: [
          {{
            type: 'text',
            text: JSON.stringify(status, null, 2)
          }}
        ]
      }};
    }}

    case 'example_tool': {{
      const param1 = args?.param1;
      const param2 = args?.param2 || 10;

      if (!param1) {{
        throw new McpError(
          ErrorCode.InvalidParams,
          'param1 is required'
        );
      }}

      return {{
        content: [
          {{
            type: 'text',
            text: `Processed ${{param1}} with value ${{param2}}`
          }}
        ]
      }};
    }}

    default:
      throw new McpError(
        ErrorCode.MethodNotFound,
        `Tool ${{name}} not found`
      );
  }}
}});

// Initialize server
async function initializeServer(): Promise<void> {{
  console.log(`Starting ${{SERVER_NAME}} server...`);

  // Add your initialization logic here
  state.initialized = true;
  state.startTime = new Date();

  console.log(`${{SERVER_NAME}} server initialized`);
}}

// HTTP server for health checks and web interface
const app = express();
app.use(cors());
app.use(express.json());

app.get('/health', (req, res) => {{
  res.json({{
    status: 'healthy',
    server: SERVER_NAME,
    initialized: state.initialized,
    uptime: Date.now() - state.startTime.getTime()
  }});
}});

app.get('/tools', (req, res) => {{
  res.json({{ tools }});
}});

// Start servers
async function main(): Promise<void> {{
  try {{
    await initializeServer();

    // Start HTTP server
    app.listen(SERVER_PORT, SERVER_HOST, () => {{
      console.log(
        `${{SERVER_NAME}} HTTP server running on ` +
        `http://${{SERVER_HOST}}:${{SERVER_PORT}}`
      );
    }});

    // Start MCP server
    const transport = new StdioServerTransport();
    await server.connect(transport);

    console.log(`${{SERVER_NAME}} MCP server started`);
  }} catch (error) {{
    console.error('Failed to start server:', error);
    process.exit(1);
  }}
}}

// Handle graceful shutdown
process.on('SIGINT', async () => {{
  console.log('\\nShutting down server...');
  await server.close();
  process.exit(0);
}});

process.on('SIGTERM', async () => {{
  console.log('\\nShutting down server...');
  await server.close();
  process.exit(0);
}});

// Start the server
if (require.main === module) {{
  main().catch(console.error);
}}

export {{ server, state }};
"""

        # tsconfig.json
        tsconfig = {
            "compilerOptions": {
                "target": "ES2020",
                "module": "commonjs",
                "lib": ["ES2020"],
                "outDir": "./dist",
                "rootDir": "./src",
                "strict": True,
                "esModuleInterop": True,
                "skipLibCheck": True,
                "forceConsistentCasingInFileNames": True,
                "declaration": True,
                "declarationMap": True,
                "sourceMap": True,
                "removeComments": False,
            },
            "include": ["src/**/*"],
            "exclude": ["node_modules", "dist", "tests"],
        }

        # Test file
        test_ts = f"""/**
 * Tests for {server_name} MCP server
 */

import {{ server, state }} from '../src/index';

describe('{server_name} MCP Server', () => {{
  beforeEach(() => {{
    // Reset server state
    state.initialized = false;
  }});

  test('should initialize properly', () => {{
    expect(server).toBeDefined();
    expect(server.name).toBe('{server_name}');
  }});

  test('should handle hello_world tool', async () => {{
    // Add test implementation
    expect(true).toBe(true);
  }});

  test('should handle get_status tool', async () => {{
    // Add test implementation
    expect(true).toBe(true);
  }});

  test('should handle example_tool', async () => {{
    // Add test implementation
    expect(true).toBe(true);
  }});
}});
"""

        return {
            "src/index.ts": index_ts,
            "package.json": json.dumps(package_json, indent=2),
            "tsconfig.json": json.dumps(tsconfig, indent=2),
            ".env.example": (
                f"HOST=localhost\nPORT={port}\n# Add your environment variables here\n"
            ),
            "README.md": self._generate_readme(
                server_name, port, description, "TypeScript"
            ),
            "tests/server.test.ts": test_ts,
        }

    def create_minimal_python_template(
        self, server_name: str, port: int, description: str
    ) -> dict:
        """Generate minimal Python server template"""

        main_py = f'''#!/usr/bin/env python3
"""
{server_name} - Minimal MCP Server
{description}
"""

import json
import asyncio
from typing import Any, Dict
import os
from dotenv import load_dotenv

load_dotenv()

class MCPServer:
    def __init__(self, name: str, port: int):
        self.name = name
        self.port = port
        self.tools = {{}}
        self.register_default_tools()

    def tool(self, name: str = None):
        """Decorator to register tools"""
        def decorator(func):
            tool_name = name or func.__name__
            self.tools[tool_name] = func
            return func
        return decorator

    def register_default_tools(self):
        """Register default tools"""

        @self.tool()
        async def hello_world(name: str = "World") -> str:
            """Say hello to someone"""
            return f"Hello, {{name}}! This is {{self.name}} server."

        @self.tool()
        async def get_status() -> str:
            """Get server status"""
            return json.dumps({{
                "server": self.name,
                "status": "running",
                "port": self.port
            }}, indent=2)

    async def call_tool(self, tool_name: str, **kwargs) -> Any:
        """Call a tool by name"""
        if tool_name not in self.tools:
            raise ValueError(f"Tool {{tool_name}} not found")

        return await self.tools[tool_name](**kwargs)

    def list_tools(self) -> list:
        """List available tools"""
        return list(self.tools.keys())

    def run(self):
        """Run the server (simplified version)"""
        print(f"{{self.name}} MCP server running on port {{self.port}}")
        print(f"Available tools: {{', '.join(self.list_tools())}}")

        # In a real implementation, you would set up the MCP protocol here
        # This is a simplified version for demonstration
        import time
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print(f"\\nShutting down {{self.name}} server...")

# Initialize server
server = MCPServer("{server_name}", {port})

# Add your custom tools here
@server.tool()
async def example_tool(param1: str, param2: int = 10) -> str:
    """Example tool demonstrating parameter handling"""
    return f"Processed {{param1}} with value {{param2}}"

if __name__ == "__main__":
    server.run()
'''

        requirements_txt = """# Core dependencies
python-dotenv>=1.0.0

# Optional dependencies for full MCP implementation
# mcp>=0.1.0
# fastapi>=0.104.0
# uvicorn[standard]>=0.24.0
"""

        return {
            "main.py": main_py,
            "requirements.txt": requirements_txt,
            ".env.example": f"PORT={port}\n# Add your environment variables here\n",
            "README.md": self._generate_readme(
                server_name, port, description, "Python (Minimal)"
            ),
        }

    def _generate_readme(
        self,
        server_name: str,
        port: int,
        description: str,
        language: str,
    ) -> str:
        """Generate README.md for server"""

        return f"""# {server_name.title().replace("-", " ")} MCP Server

{description}

## Language/Framework

{language}

## Port

{port}

## Quick Start

1. Install dependencies
2. Copy `.env.example` to `.env` and configure
3. Start the server

## Integration

Add to `~/.mcp-servers.json`:

```json
{{
  "{server_name}": {{
    "name": "{server_name.title().replace('-', ' ')} MCP Server",
    "path": "~/path/to/{server_name}",
    "command": "your-start-command",
    "port": {port},
    "env_file": ".env"
  }}
}}
```

Then:

```bash
mcp {server_name} start
```
"""

    def create_server(
        self,
        name: str,
        template: str,
        port: int,
        description: str = None,
        path: str = None,
        complexity: str = "simple",
        force: bool = False,
        with_tests: bool = False,
        with_docs: bool = False,
    ) -> bool:
        """Create a new MCP server from template"""

        if template not in self.templates:
            print(f"Unknown template: {template}")
            print(f"Available templates: {', '.join(self.templates.keys())}")
            return False

        # Set defaults
        if not description:
            description = f"MCP server for {name}"
        if not path:
            # Default to mcp-tools directory for better organization
            if Path("mcp-tools").exists() or Path("mcp-setup").exists():
                path = Path("mcp-tools") / name
            else:
                path = Path.home() / f"mcp-{name}"
        else:
            path = Path(path).expanduser()

        # Check if path exists
        if path.exists() and not force:
            response = input(
                f"Directory {path} already exists. Continue? (y/N): "
            )
            if response.lower() != "y":
                return False

        # Create directory
        path.mkdir(parents=True, exist_ok=True)

        # Generate template files
        if template == "python-official":
            files = self.create_python_official_template(name, port, description)
        elif template == "python-fastmcp":
            files = self.create_python_fastmcp_template(name, port, description)
        elif template == "typescript-node":
            files = self.create_typescript_template(name, port, description)
        elif template == "minimal-python":
            files = self.create_minimal_python_template(name, port, description)
        else:
            print(f"Template {template} not implemented")
            return False

        # Write files
        for file_path, content in files.items():
            full_path = path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)
            print(f"Created: {full_path}")

        # Add to MCP configuration
        self._add_to_config(name, str(path), port, template)

        print(f"\\n✅ Successfully created {name} MCP server at {path}")
        print("\\n📋 Next steps:")
        print(f"1. cd {path}")
        if template.startswith("python"):
            print("2. pip install -e . (or uv pip install -e .)")
        elif template.startswith("typescript"):
            print("2. npm install")
            print("3. npm run build")
        print("3. Edit .env file with your configuration")
        print(f"4. mcp {name} start")

        return True

    def _add_to_config(self, name: str, path: str, port: int, template: str):
        """Add server to MCP configuration"""
        # Try project config first, then fall back to home directory
        project_config = Path("configs/.mcp-servers.json")
        home_config = Path.home() / ".mcp-servers.json"
        
        # Prefer project config if it exists or if we're in a project
        if project_config.parent.exists() or Path("mcp-setup").exists():
            config_file = project_config
            # Create configs directory if it doesn't exist
            config_file.parent.mkdir(exist_ok=True)
        else:
            config_file = home_config

        if config_file.exists():
            config = json.loads(config_file.read_text())
        else:
            config = {}

        # Determine command based on template - Official MCP uses stdio
        if template == "python-official":
            command = "python src/main.py"  # stdio transport
        elif template == "python-fastmcp":
            command = "uv run python src/main.py"  # legacy FastMCP
        elif template == "typescript-node":
            command = "npm start"
        elif template == "minimal-python":
            command = "python main.py"
        else:
            command = "your-start-command"

        # For official MCP servers, use stdio transport configuration
        if template == "python-official":
            config[name] = {
                "name": f"{name.title().replace('-', ' ')} MCP Server",
                "path": path,
                "command": command,
                "transport": "stdio",  # Official MCP uses stdio
                "env_file": ".env",
                "dependencies": {},
            }
        else:
            # Legacy configuration format
            config[name] = {
                "name": f"{name.title().replace('-', ' ')} MCP Server",
                "path": path,
                "command": command,
                "port": port,
                "env_file": ".env",
                "dependencies": {},
            }

        config_file.write_text(json.dumps(config, indent=2))
        print(f"Added {name} to MCP configuration at {config_file}")


def main_create_server():
    parser = argparse.ArgumentParser(
        description="Create new MCP servers from templates",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  mcp-create-server my-weather --template python-official --port 8055
  mcp-create-server file-manager --template typescript-node --port 8056
  mcp-create-server simple-calc --template minimal-python --port 8057
  mcp-create-server legacy-server --template python-fastmcp --port 8058
        """,
    )

    parser.add_argument("name", help="Server name (e.g., 'my-weather')")
    parser.add_argument(
        "--template",
        "-t",
        choices=[
            "python-official",
            "python-fastmcp",
            "typescript-node",
            "minimal-python",
        ],
        default="python-official",
        help="Template to use (default: python-official)",
    )
    parser.add_argument(
        "--port",
        "-p",
        type=int,
        default=8055,
        help="Port number (default: 8055)",
    )
    parser.add_argument("--description", "-d", help="Server description")
    parser.add_argument("--path", help="Custom path (default: mcp-tools/<name> or ~/mcp-<name>)")
    parser.add_argument("--complexity", "-c", 
                       choices=["simple", "standard", "advanced", "enterprise"],
                       default="simple",
                       help="Complexity level (affects generated features)")
    parser.add_argument("--force", "-f", action="store_true",
                       help="Overwrite existing files")
    parser.add_argument("--with-tests", action="store_true",
                       help="Include test scaffolding")
    parser.add_argument("--with-docs", action="store_true",
                       help="Include documentation templates")
    parser.add_argument(
        "--list-templates",
        action="store_true",
        help="List available templates",
    )

    args = parser.parse_args()

    generator = MCPServerGenerator()

    if args.list_templates:
        print("Available templates:")
        for name, info in generator.templates.items():
            print(f"  {name}: {info['description']}")
        return

    success = generator.create_server(
        args.name,
        args.template,
        args.port,
        args.description,
        args.path,
        args.complexity,
        args.force,
        args.with_tests,
        args.with_docs,
    )

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main_create_server()
