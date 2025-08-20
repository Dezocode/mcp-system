# Claude Code + MCP Server Integration

## How It Works

The integration consists of **3 layers** that make MCP servers compatible with Claude Code:

### 1. **Intelligent Router** (`mcp-router.py`)
- Analyzes user prompts using keywords and patterns
- Automatically determines which MCP server(s) are needed
- Routes requests to appropriate servers

### 2. **Universal Launcher** (`mcp`)
- Manages multiple MCP servers with single commands
- Handles dependencies (PostgreSQL, Ollama, etc.)
- Provides unified interface for server management

### 3. **Claude Integration Helper** (`claude-mcp.sh`)
- Bridge between Claude Code and MCP servers
- Provides simple commands for Claude to use
- Handles automatic server selection and startup

## Usage Examples

### For Claude Code Users:

1. **Automatic Server Selection:**
```bash
claude-mcp analyze "Save this coding preference to memory"
# Output: Starts mem0 server automatically
```

2. **Direct Memory Operations:**
```bash
claude-mcp memory save "I prefer TypeScript for frontend development"
claude-mcp memory search "programming language"
claude-mcp memory list
```

3. **Manual Server Management:**
```bash
mcp list                    # See all available servers
mcp mem0 start             # Start memory server
mcp github start           # Start GitHub server
mcp all start              # Start all servers
```

### For Claude (AI Assistant):

When users mention tasks related to:
- **Memory/Storage** → Automatically uses `mem0` server
- **File Operations** → Uses `filesystem` server  
- **GitHub Tasks** → Uses `github` server
- **Weather** → Uses `weather` server

## Server Selection Logic

The router analyzes prompts for:

### Keywords:
- `memory`, `remember`, `recall` → `mem0`
- `file`, `directory`, `read`, `write` → `filesystem`
- `github`, `repository`, `commit` → `github`
- `weather`, `forecast`, `temperature` → `weather`

### Patterns:
- "save this for later" → `mem0`
- "read that file" → `filesystem`
- "create a pull request" → `github`

## Configuration

All servers are defined in `~/.mcp-servers.json`:

```json
{
  "mem0": {
    "name": "Memory Server",
    "path": "~/mcp-mem0",
    "command": "uv run python src/main.py",
    "port": 8050,
    "dependencies": {...}
  },
  "github": {
    "name": "GitHub Server", 
    "path": "~/mcp-github",
    "command": "python -m mcp_github",
    "port": 8052
  }
}
```

## Limitations & Solutions

### Current Limitation:
❌ Claude Code CLI cannot directly connect to MCP servers

### Our Solution:
✅ **Smart Proxy Layer** that:
- Analyzes user intent from natural language
- Automatically starts required servers
- Routes requests to appropriate servers
- Returns results in a format Claude Code can use

### Result:
Claude Code can now:
- 🎯 Automatically select MCP servers based on user prompts
- 🚀 Start servers on-demand
- 💾 Store and retrieve memories
- 📁 Manage files
- 🔗 Interact with GitHub
- 🌤️ Get weather data
- And more...

## Example Workflow:

1. **User**: "Remember that I'm working on a React project with TypeScript"
2. **Router**: Detects "remember" → selects `mem0` server
3. **Launcher**: Starts `mem0` + dependencies (PostgreSQL, Ollama)  
4. **Helper**: Sends data to memory server
5. **Result**: Memory stored and confirmation returned

Later:
1. **User**: "What programming languages do I prefer?"
2. **Router**: Detects memory query → uses `mem0`
3. **Helper**: Searches existing memories
4. **Result**: Returns "TypeScript for React projects"

This creates a **seamless experience** where Claude Code can intelligently use MCP servers without manual configuration!