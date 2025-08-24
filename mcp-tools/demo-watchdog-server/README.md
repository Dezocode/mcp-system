# demo-watchdog-server MCP Server

## Overview

demo-watchdog-server is an MCP (Model Context Protocol) server that provides [describe functionality].

## Installation

```bash
cd mcp-tools/demo-watchdog-server
pip install -e .
```

## Usage

### As MCP Server

Add to your MCP client configuration:

```json
{
  "demo-watchdog-server": {
    "command": "python",
    "args": ["src/main.py"],
    "cwd": "mcp-tools/demo-watchdog-server"
  }
}
```

### Direct Usage

```bash
python src/main.py
```

## Configuration

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
# Edit .env with your configuration
```

## Development

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black src/ tests/
isort src/ tests/
```

## API

### Tools

- `hello_world`: Say hello to someone

### Resources

- `config://info`: Get server information

## License

MIT License - see LICENSE file for details
