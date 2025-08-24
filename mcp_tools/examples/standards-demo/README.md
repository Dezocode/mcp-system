# Standards Demo MCP Server

Demo server using official Anthropic MCP standards

This MCP server follows the **official Anthropic MCP protocol specification** and implements the standard MCP capabilities using stdio transport.

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

### Installation

1. **Clone and navigate to the server directory:**
   ```bash
   git clone <repository-url>
   cd standards-demo
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
standards-demo

# Or with uv
uv run python src/main.py
```

### Claude Desktop Integration

Add this server to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "standards-demo": {
      "command": "uv",
      "args": ["run", "python", "/path/to/standards-demo/src/main.py"],
      "env": {
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### Manual MCP Client Integration

If you're integrating with a custom MCP client:

```python
from mcp.client import StdioMCPClient

# Connect to the server
client = StdioMCPClient()
await client.connect(
    command=["python", "/path/to/standards-demo/src/main.py"]
)

# List available tools
tools = await client.list_tools()

# Call a tool
result = await client.call_tool("hello_world", {"name": "World"})
```

## 🏗️ Development

### Project Structure

```
standards-demo/
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
uv run pytest --cov=standards_demo

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
docker build -t standards-demo .

# Run container
docker run --rm standards-demo

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
{
  "name": "tool_name",
  "arguments": {
    "param1": "value1",
    "param2": "value2"
  }
}
```

### Response Format

Responses follow the MCP content format:

```json
[
  {
    "type": "text",
    "text": "Response content here"
  }
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
