# MCP Server Management - Quick Start Guide

## 🚀 5-Minute Setup

### 1. Install the System
```bash
# Make tools available globally  
export PATH="$HOME/bin:$PATH"

# Test installation
mcp list
claude-mcp help
mcp-create-server --help
```

### 2. Start Your First Server
```bash
# Start the memory server (already configured)
mcp mem0 start

# Check status
mcp status

# Test it
claude-mcp memory save "I love this MCP system!"
claude-mcp memory search "MCP"
```

### 3. Create Your Own Server
```bash
# Generate a new weather server
mcp-create-server my-weather --template python-fastmcp --port 8055

# Navigate and setup
cd ~/mcp-my-weather
uv pip install -e .
cp .env.example .env

# Start it
mcp my-weather start
```

### 4. Test Everything
```bash
# Test all servers
mcp-test all --start

# Use Claude integration
claude-mcp analyze "Get weather for San Francisco and remember it"
```

## 📋 Command Cheat Sheet

### Server Management
```bash
mcp list                          # List all servers
mcp server-name start            # Start specific server  
mcp server-name stop             # Stop server
mcp server-name restart          # Restart server
mcp server-name logs             # View logs
mcp server-name status           # Check status
mcp all start                    # Start all servers
mcp status                       # Check all servers
```

### Development
```bash
mcp-create-server name --template python-fastmcp --port 8055
mcp-create-server name --template typescript-node --port 8056
mcp-create-server name --template minimal-python --port 8057
```

### Testing  
```bash
mcp-test server-name             # Test specific server
mcp-test all                     # Test all servers
mcp-test server-name --start     # Start server before testing
mcp-test all --report report.json # Save detailed report
```

### Claude Integration
```bash
claude-mcp memory save "text"         # Save to memory
claude-mcp memory search "query"      # Search memories  
claude-mcp memory list                # List all memories
claude-mcp send server tool '{"data":"value"}'  # Send to server
claude-mcp analyze "user prompt"      # Auto-select servers
claude-mcp status                     # Check all servers
```

## 🔧 Common Workflows

### Daily Development
```bash
# Morning startup
mcp all start
mcp status

# Work with memory  
claude-mcp memory save "Working on the user authentication feature today"

# Test changes
mcp-test my-server --start

# Evening shutdown
mcp all stop
```

### Creating New Features
```bash
# 1. Create server
mcp-create-server feature-name --template python-fastmcp --port 8060

# 2. Develop
cd ~/mcp-feature-name
# Edit src/main.py, add your tools

# 3. Test
mcp-test feature-name --start

# 4. Deploy
mcp feature-name start
```

### Debugging Issues
```bash
# Check what's running
mcp status

# View logs  
mcp server-name logs

# Restart problematic server
mcp server-name restart

# Test connectivity
curl http://localhost:8050/health

# Full system test
mcp-test all
```

## 🏗️ Architecture Overview

```
User Commands (claude-mcp, mcp) 
         ↓
Smart Router (mcp-router.py)
         ↓  
Server Manager (mcp launcher)
         ↓
Individual MCP Servers (mem0, github, custom)
         ↓
Infrastructure (PostgreSQL, Ollama, Redis)
```

## 📚 Next Steps

1. **Read the full documentation**: `MCP-Complete-Documentation.md`
2. **Create your first custom server**: Follow the template guide
3. **Set up production deployment**: Use Docker Compose 
4. **Join the community**: Share your servers and configurations

## 🆘 Need Help?

- **Logs**: `mcp server-name logs`
- **Status**: `mcp status`  
- **Test**: `mcp-test server-name`
- **Documentation**: See `MCP-Complete-Documentation.md`
- **Templates**: `mcp-create-server --list-templates`

---

**🎉 You're now ready to build and manage MCP servers like a pro!**