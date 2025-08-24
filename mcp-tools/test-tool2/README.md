# Test Tool2 MCP Server

MCP server for test-tool2

## Overview

This MCP server provides the following tools:

- `hello_world`: Say hello to someone
- `get_status`: Get server status information
- `example_tool`: Example tool demonstrating parameter handling

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd test-tool2
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
test-tool2

# Or with uv
uv run python src/main.py
```

The server will start on `http://localhost:8055` by default.

### Configuration

Edit `.env` file to customize:

- `HOST`: Server host (default: localhost)
- `PORT`: Server port (default: 8055)
- Add other configuration variables as needed

### Docker

Build and run with Docker:

```bash
docker build -t test-tool2 .
docker run -p 8055:8055 test-tool2
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
    """Description of what this tool does.

    Args:
        ctx: The MCP server provided context
        param: Description of parameter

    Returns:
        Description of return value
    """
    # Your implementation here
    return f"Result: {param}"
```

2. Restart the server to load the new tool.

### Testing

Run tests:

```bash
pytest tests/
```

Run with coverage:

```bash
pytest tests/ --cov=test_tool2
```

## Integration

Add this server to your MCP configuration (`~/.mcp-servers.json`):

```json
{
  "test-tool2": {
    "name": "Test Tool2 MCP Server",
    "path": "~/path/to/test-tool2",
    "command": "uv run python src/main.py",
    "port": 8055,
    "env_file": ".env",
    "dependencies": {}
  }
}
```

Then start it:

```bash
mcp test-tool2 start
```

## License

This project is licensed under the MIT License.
