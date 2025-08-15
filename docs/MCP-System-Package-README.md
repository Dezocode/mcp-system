# MCP System - Universal Package

## 🎯 One-Click Installation & Permissionless Claude Code Integration

This package provides a complete MCP (Model Context Protocol) server management system with seamless Claude Code CLI integration that works in any project without requiring special permissions.

## 🚀 Quick Installation

### Method 1: One-Click Installer (Recommended)
```bash
curl -sSL https://raw.githubusercontent.com/your-repo/mcp-system/main/one-click-mcp-installer.sh | bash
```

### Method 2: Manual Installation
```bash
# Download package
git clone https://github.com/your-repo/mcp-system.git
cd mcp-system

# Run installer
chmod +x one-click-mcp-installer.sh
./one-click-mcp-installer.sh
```

### Method 3: Python Installer
```bash
python3 install-mcp-system.py
```

## ✨ Features

### 🔄 **Permissionless Integration**
- Automatically detects Claude Code usage in any project
- No special permissions or configuration required
- Safe integration with existing Claude settings
- Works in any directory structure

### 🎯 **Auto-Discovery**
- Detects project types (Python, Node.js, Rust, Go, etc.)
- Automatically suggests appropriate MCP servers
- Intelligent routing based on context

### 🛠️ **Complete Toolchain**
- **Universal Launcher**: `mcp-universal` - works anywhere
- **Server Creator**: Create new MCP servers from templates
- **Testing Framework**: Comprehensive testing capabilities  
- **Upgrade System**: Modular server enhancement
- **Claude Bridge**: Seamless Claude Code integration

### 🔒 **Safe & Secure**
- Backup existing configurations
- Safe merging of Claude settings
- Non-destructive installation
- Rollback capabilities

## 📋 Available Commands

### After Installation
```bash
# Universal launcher (works in any directory)
mcp-universal                    # Auto-detect and initialize
mcp-universal create my-server   # Create new server
mcp-universal test [server]      # Test servers
mcp-universal upgrade server     # Upgrade server

# Project initialization
mcp-init-project                 # Initialize MCP for current project

# Claude Code bridge
mcp-universal bridge init        # Manual Claude integration
mcp-universal bridge status      # Check integration status
```

### Project-Specific (Auto-Created)
```bash
# In any project after initialization
./mcp create weather-server      # Create server for this project
./mcp-test                       # Test project servers
./mcp-upgrade                    # Upgrade project servers
```

## 🎯 Usage Examples

### Example 1: Claude Code Project
```bash
# Navigate to your Claude project
cd my-claude-project

# Auto-initialize (detects .claude directory)
mcp-universal
# ✅ Claude project detected - MCP integration active!

# Use MCP tools
./mcp create weather-tools --template python-fastmcp
./mcp-test weather-tools
```

### Example 2: Python Project
```bash
# Navigate to Python project
cd my-python-app

# Initialize MCP
mcp-init-project
# 🎯 Python project detected
# ✅ Created my-python-app-tools server

# Start using
./mcp my-python-app-tools start
```

### Example 3: Any Project
```bash
# Works in any directory
cd /any/project/directory

# Auto-detect and initialize
mcp-universal
# 🎯 Generic project - setting up basic MCP integration

# Create custom server
mcp-universal create api-tools --template typescript-node
```

## 🏗️ Architecture

```
Project Directory
├── .mcp/                    # Project MCP configuration
├── mcp*                     # Project-specific launchers
└── .claude/                 # Claude Code integration
    └── claude_desktop_config.json

~/.mcp-system/               # System installation
├── components/              # All MCP tools
├── docs/                   # Documentation
├── templates/              # Server templates
└── backups/                # Configuration backups

~/bin/                      # User binaries
├── mcp-universal           # Universal launcher
└── mcp-init-project        # Project initializer
```

## 🔧 Integration Details

### Claude Code CLI Integration

The system automatically integrates with Claude Code CLI:

1. **Auto-Detection**: Detects Claude projects via `.claude` directory or `CLAUDE.md`
2. **Safe Configuration**: Merges with existing Claude settings safely
3. **Permissionless**: No special permissions required
4. **Context-Aware**: Adapts to project type and structure

### Configuration Files

#### Project Configuration (`.mcp/config.json`)
```json
{
  "project_info": {
    "name": "my-project",
    "types": ["python", "claude"],
    "path": "/path/to/project"
  },
  "mcp_integration": {
    "enabled": true,
    "auto_start": true,
    "safe_mode": true
  },
  "claude_code_integration": {
    "bridge_active": true,
    "config_path": ".claude/claude_desktop_config.json"
  }
}
```

#### Claude Configuration (Automatically Merged)
```json
{
  "mcpServers": {
    "mcp-system": {
      "command": "~/bin/mcp-universal",
      "args": ["router"],
      "env": {
        "MCP_SYSTEM_PATH": "~/.mcp-system",
        "MCP_AUTO_DISCOVERY": "true"
      }
    }
  },
  "mcp_system_integration": {
    "enabled": true,
    "auto_discovery": true,
    "safe_mode": true
  }
}
```

## 🛠️ Development

### Creating Custom Servers
```bash
# Create from template
mcp-universal create my-server --template python-fastmcp --port 8060

# Navigate to server
cd ~/mcp-my-server

# Develop your tools
# Edit src/main.py

# Test
mcp-universal test my-server --start

# Deploy
./mcp my-server start
```

### Available Templates
- **python-fastmcp**: Full-featured Python MCP server
- **typescript-node**: TypeScript/Node.js MCP server  
- **minimal-python**: Lightweight Python server
- **custom**: Custom template generator

### Testing & Debugging
```bash
# Test specific server
mcp-universal test server-name --verbose

# Test all servers
mcp-universal test all --report

# Check logs
tail -f ~/.mcp-system/logs/server-name.log

# Debug connectivity
curl http://localhost:8050/health
```

## 🔄 Upgrade System

### Modular Upgrades
```bash
# Suggest upgrades based on needs
mcp-universal upgrade suggest "I need authentication and caching" my-server

# Interactive upgrade wizard
mcp-universal upgrade wizard my-server

# Install specific modules
mcp-universal upgrade install my-server authentication caching-redis

# Available modules:
# - logging-enhancement: Structured logging
# - authentication: JWT auth system
# - caching-redis: Redis caching layer
# - database-migrations: Schema management
# - monitoring-metrics: Prometheus metrics
# - api-versioning: Version management
```

## 📚 Documentation

After installation, comprehensive documentation is available:

```bash
# View documentation
ls ~/.mcp-system/docs/

# Quick start guide
cat ~/.mcp-system/docs/MCP-Quick-Start-Guide.md

# Complete documentation
cat ~/.mcp-system/docs/MCP-Complete-Documentation.md

# Upgrade system docs
cat ~/.mcp-system/docs/MCP-Upgrader-Documentation.md
```

## 🆘 Troubleshooting

### Common Issues

#### Installation Problems
```bash
# Check prerequisites
python3 --version  # Should be 3.8+
which git

# Reinstall
rm -rf ~/.mcp-system ~/bin/mcp-*
./one-click-mcp-installer.sh
```

#### Claude Integration Issues
```bash
# Check integration status
mcp-universal bridge status

# Reinitialize
mcp-universal bridge init

# Check Claude config
cat ~/.claude/claude_desktop_config.json
```

#### Server Problems
```bash
# Check server status
mcp-universal status

# Check logs
tail -f ~/.mcp-system/logs/*.log

# Restart problematic server
./mcp server-name restart
```

### Recovery Procedures

#### Restore Claude Configuration
```bash
# List backups
ls ~/.claude/claude_desktop_config.backup.*

# Restore from backup
cp ~/.claude/claude_desktop_config.backup.TIMESTAMP ~/.claude/claude_desktop_config.json
```

#### Complete System Reset
```bash
# Remove installation
rm -rf ~/.mcp-system
rm -f ~/bin/mcp-*

# Remove from shell configs
# Edit ~/.bashrc, ~/.zshrc to remove MCP lines

# Reinstall
./one-click-mcp-installer.sh
```

## 🌟 Advanced Features

### CI/CD Integration
```yaml
# .github/workflows/mcp.yml
name: MCP Integration
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Setup MCP
      run: |
        curl -sSL https://raw.githubusercontent.com/your-repo/mcp-system/main/one-click-mcp-installer.sh | bash
        source ~/.bashrc
    - name: Test MCP Servers
      run: mcp-universal test all --report ci-report.json
```

### Docker Integration
```dockerfile
# Dockerfile
FROM python:3.11-slim

# Install MCP System
RUN curl -sSL https://your-repo/one-click-mcp-installer.sh | bash
ENV PATH="/root/bin:$PATH"
ENV MCP_SYSTEM_PATH="/root/.mcp-system"

# Your application
COPY . /app
WORKDIR /app

# Initialize MCP for container
RUN mcp-init-project

CMD ["./mcp", "all", "start"]
```

## 📞 Support

- **Issues**: Report at repository issues page
- **Documentation**: Check `~/.mcp-system/docs/`
- **Logs**: Available in `~/.mcp-system/logs/`
- **Community**: Join the MCP community discussions

## 📋 Package Contents

This package includes:

### Core Components
- ✅ Universal MCP launcher (`mcp-universal`)
- ✅ Intelligent server router
- ✅ Server template generator
- ✅ Comprehensive testing framework
- ✅ Modular upgrade system

### Integration Tools
- ✅ Claude Code CLI bridge
- ✅ Auto-discovery system
- ✅ Project initialization
- ✅ Safe configuration merging

### Documentation
- ✅ Complete system documentation
- ✅ Quick start guide
- ✅ Upgrade system guide
- ✅ Troubleshooting manual

### Safety Features
- ✅ Configuration backups
- ✅ Rollback capabilities
- ✅ Non-destructive installation
- ✅ Safe mode operations

---

**🎉 Ready to transform your development workflow with seamless MCP integration!**

```bash
# Get started now:
curl -sSL https://your-repo/one-click-mcp-installer.sh | bash
```