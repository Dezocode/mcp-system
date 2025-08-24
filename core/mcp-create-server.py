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
            "python-fastmcp": {
                "name": "Python FastMCP Server",
                "description": "Python server using FastMCP framework",
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

    def create_python_fastmcp_template(
        self, server_name: str, port: int, description: str
    ) -> dict:
        """Generate Python FastMCP server template files"""

        # Main server file
        main_py = f'''"""
{server_name} - MCP Server
{description}
"""

from mcp.server.fastmcp import FastMCP, Context
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass
from dotenv import load_dotenv
import asyncio
import json
import os

load_dotenv()

# Server configuration
SERVER_NAME = "{server_name}"
SERVER_PORT = {port}
SERVER_HOST = os.getenv("HOST", "localhost")

@dataclass
class {server_name.title().replace("-", "")}Context:
    """Context for the {server_name} MCP server."""
    # Add your context variables here
    initialized: bool = False

@asynccontextmanager
async def server_lifespan(
    server: FastMCP
) -> AsyncIterator[{server_name.title().replace("-", "")}Context]:
    """
    Manages the server lifecycle.

    Args:
        server: The FastMCP server instance

    Yields:
        Context: The server context
    """
    # Initialize your server resources here
    print(f"Starting {{SERVER_NAME}} server...")

    context = {server_name.title().replace("-", "")}Context(initialized=True)

    try:
        yield context
    finally:
        # Cleanup resources here
        print(f"Shutting down {{SERVER_NAME}} server...")

# Initialize FastMCP server
mcp = FastMCP(
    SERVER_NAME,
    description="{description}",
    lifespan=server_lifespan,
    host=SERVER_HOST,
    port=SERVER_PORT
)

@mcp.tool()
async def hello_world(ctx: Context, name: str = "World") -> str:
    """Say hello to someone.

    Args:
        ctx: The MCP server provided context
        name: The name to greet

    Returns:
        A greeting message
    """
    return f"Hello, {{name}}! This is {{SERVER_NAME}} server."

@mcp.tool()
async def get_status(ctx: Context) -> str:
    """Get server status.

    Args:
        ctx: The MCP server provided context

    Returns:
        Server status information
    """
    context = ctx.request_context.lifespan_context
    return json.dumps({{
        "server": SERVER_NAME,
        "status": "running",
        "initialized": context.initialized,
        "port": SERVER_PORT
    }}, indent=2)

# Add your custom tools here
@mcp.tool()
async def example_tool(ctx: Context, param1: str, param2: int = 10) -> str:
    """Example tool demonstrating parameter handling.

    Args:
        ctx: The MCP server provided context
        param1: A required string parameter
        param2: An optional integer parameter (default: 10)

    Returns:
        Result of the operation
    """
    return f"Processed {{param1}} with value {{param2}}"

if __name__ == "__main__":
    print(f"Starting {{SERVER_NAME}} MCP server on {{SERVER_HOST}}:{{SERVER_PORT}}")
    mcp.run()
'''

        # pyproject.toml
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
requires-python = ">=3.8"
dependencies = [
    "mcp",
    "python-dotenv",
    "fastapi",
    "uvicorn[standard]",
    "pydantic",
]

[project.optional-dependencies]
dev = [
    "pytest",
    "pytest-asyncio",
    "black",
    "isort",
    "mypy",
    "pre-commit",
]

[project.scripts]
{server_name} = "{server_name}.main:main"

[tool.black]
line-length = 88
target-version = ['py38']

[tool.isort]
profile = "black"
multi_line_output = 3

[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
"""

        # .env.example
        env_example = f"""# {server_name.upper()} Server Configuration

# Server settings
HOST=localhost
PORT={port}

# Add your environment variables here
# DATABASE_URL=postgresql://user:pass@localhost:5432/{server_name.replace("-", "_")}
# API_KEY=your-api-key-here
# DEBUG=true
"""

        # README.md
        readme_md = f"""# {server_name.title().replace("-", " ")} MCP Server

{description}

## Overview

This MCP server provides the following tools:

- `hello_world`: Say hello to someone
- `get_status`: Get server status information
- `example_tool`: Example tool demonstrating parameter handling

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd {server_name}
```

2. Install dependencies:
```bash
pip install -e .
```

3. Copy environment configuration:
```bash
cp .env.example .env
# Edit .env with your configuration
```

## Usage

### Start the server:

```bash
# Development mode
python src/main.py

# Or using the installed script
{server_name}

# Or with uv
uv run python src/main.py
```

The server will start on `http://localhost:{port}` by default.

### Configuration

Edit `.env` file to customize:

- `HOST`: Server host (default: localhost)
- `PORT`: Server port (default: {port})
- Add other configuration variables as needed

### Docker

Build and run with Docker:

```bash
docker build -t {server_name} .
docker run -p {port}:{port} {server_name}
```

Or use Docker Compose:

```bash
docker-compose up -d
```

## Development

### Adding New Tools

1. Add a new function decorated with `@mcp.tool()`:

```python
@mcp.tool()
async def my_new_tool(ctx: Context, param: str) -> str:
    \"\"\"Description of what this tool does.

    Args:
        ctx: The MCP server provided context
        param: Description of parameter

    Returns:
        Description of return value
    \"\"\"
    # Your implementation here
    return f"Result: {{param}}"
```

2. Restart the server to load the new tool.

### Testing

Run tests:

```bash
pytest tests/
```

Run with coverage:

```bash
pytest tests/ --cov={server_name.replace("-", "_")}
```

## Integration

Add this server to your MCP configuration (`~/.mcp-servers.json`):

```json
{{
  "{server_name}": {{
    "name": "{server_name.title().replace('-', ' ')} MCP Server",
    "path": "~/path/to/{server_name}",
    "command": "uv run python src/main.py",
    "port": {port},
    "env_file": ".env",
    "dependencies": {{}}
  }}
}}
```

Then start it:

```bash
mcp {server_name} start
```

## License

This project is licensed under the MIT License.
"""

        # Dockerfile
        dockerfile = f"""FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY pyproject.toml ./
RUN pip install -e .

# Copy source code
COPY src/ ./src/
COPY .env.example ./.env

# Expose port
EXPOSE {port}

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:{port}/health || exit 1

# Run server
CMD ["python", "src/main.py"]
"""

        # docker-compose.yml
        docker_compose = f"""version: '3.8'

services:
  {server_name}:
    build: .
    ports:
      - "{port}:{port}"
    environment:
      - HOST=0.0.0.0
      - PORT={port}
    restart: unless-stopped
    # volumes:
    #   - ./data:/app/data
    # depends_on:
    #   - database

  # Uncomment and configure if you need a database
  # database:
  #   image: postgres:15
  #   environment:
  #     POSTGRES_DB: {server_name.replace("-", "_")}
  #     POSTGRES_USER: postgres
  #     POSTGRES_PASSWORD: password
  #   volumes:
  #     - postgres_data:/var/lib/postgresql/data
  #   ports:
  #     - "5432:5432"

# volumes:
#   postgres_data:
"""

        # Test file
        test_py = f'''"""
Tests for {server_name} MCP server
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock
from mcp.server.fastmcp import Context

# Import your server modules here
# from src.main import hello_world, get_status, example_tool

@pytest.mark.asyncio
async def test_hello_world():
    \"\"\"Test the hello_world tool\"\"\"
    # Mock context
    ctx = Mock(spec=Context)

    # Test with default name
    result = await hello_world(ctx)
    assert "Hello, World!" in result
    assert "{server_name}" in result

    # Test with custom name
    result = await hello_world(ctx, name="Alice")
    assert "Hello, Alice!" in result

@pytest.mark.asyncio
async def test_get_status():
    \"\"\"Test the get_status tool\"\"\"
    # Mock context
    ctx = Mock(spec=Context)
    ctx.request_context = Mock()
    ctx.request_context.lifespan_context = Mock()
    ctx.request_context.lifespan_context.initialized = True

    result = await get_status(ctx)
    status_data = json.loads(result)

    assert status_data["server"] == "{server_name}"
    assert status_data["status"] == "running"
    assert status_data["initialized"] is True
    assert status_data["port"] == {port}

@pytest.mark.asyncio
async def test_example_tool():
    \"\"\"Test the example_tool\"\"\"
    ctx = Mock(spec=Context)

    # Test with required parameter
    result = await example_tool(ctx, param1="test")
    assert "Processed test with value 10" == result

    # Test with both parameters
    result = await example_tool(ctx, param1="test", param2=20)
    assert "Processed test with value 20" == result

# Add more tests for your custom tools here
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
        if template == "python-fastmcp":
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

        # Determine command based on template
        if template == "python-fastmcp":
            command = "uv run python src/main.py"
        elif template == "typescript-node":
            command = "npm start"
        elif template == "minimal-python":
            command = "python main.py"
        else:
            command = "your-start-command"

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
  mcp-create-server my-weather --template python-fastmcp --port 8055
  mcp-create-server file-manager --template typescript-node --port 8056
  mcp-create-server simple-calc --template minimal-python --port 8057
        """,
    )

    parser.add_argument("name", help="Server name (e.g., 'my-weather')")
    parser.add_argument(
        "--template",
        "-t",
        choices=[
            "python-fastmcp",
            "typescript-node",
            "minimal-python",
        ],
        default="python-fastmcp",
        help="Template to use (default: python-fastmcp)",
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
