# MCP System Installation Guide

This comprehensive guide will walk you through installing the MCP System on a fresh macOS, Linux, or Windows machine.

## 🚀 Quick Installation (Recommended)

### One-Click Install

```bash
# Clone and install in one command
git clone https://github.com/dezocode/mcp-system.git && cd mcp-system && ./install.sh
```

### Alternative Methods

#### Method 1: Direct Download
```bash
# Download latest release
curl -sSL https://github.com/dezocode/mcp-system/releases/latest/download/mcp-system.tar.gz | tar -xz
cd mcp-system-*/
./install.sh
```

#### Method 2: PyPI Installation
```bash
pip install mcp-system
mcp-system-setup
```

#### Method 3: Docker
```bash
docker run --rm -it dezocode/mcp-system:latest mcp-universal --help
```

## 📋 Prerequisites

### Required Dependencies

#### macOS
```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install prerequisites
brew install python@3.12 git node@18
```

#### Ubuntu/Debian Linux
```bash
# Update package manager
sudo apt update

# Install prerequisites
sudo apt install -y python3.12 python3.12-venv python3-pip git nodejs npm curl build-essential
```

#### Rocky Linux/RHEL/CentOS
```bash
# Install prerequisites
sudo dnf install -y python3.12 python3-pip git nodejs npm curl gcc gcc-c++ make
```

#### Windows (PowerShell)
```powershell
# Install Python 3.12+ from python.org
# Install Git from git-scm.com
# Install Node.js 18+ from nodejs.org

# Or use Chocolatey
choco install python git nodejs
```

### Optional Dependencies

#### For Database Features
```bash
# PostgreSQL (for database migrations module)
# macOS
brew install postgresql

# Ubuntu/Debian
sudo apt install -y postgresql postgresql-contrib

# Rocky Linux/RHEL
sudo dnf install -y postgresql postgresql-server
```

#### For Caching Features
```bash
# Redis (for caching module)
# macOS
brew install redis

# Ubuntu/Debian
sudo apt install -y redis-server

# Rocky Linux/RHEL
sudo dnf install -y redis
```

#### For Container Features
```bash
# Docker (for containerized deployments)
# Follow official Docker installation guide for your platform
# https://docs.docker.com/get-docker/
```

## 🔧 Step-by-Step Installation

### 1. System Preparation

#### Check Prerequisites
```bash
# Verify Python version (3.8+ required, 3.12+ recommended)
python3 --version

# Verify Git
git --version

# Verify Node.js (for TypeScript templates)
node --version
npm --version
```

#### Set Up Environment
```bash
# Create directory for MCP tools
mkdir -p ~/bin

# Add to PATH (add this to your shell profile)
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc  # or ~/.zshrc
source ~/.bashrc  # or ~/.zshrc
```

### 2. Download and Install

#### Clone Repository
```bash
# Clone the repository
git clone https://github.com/dezocode/mcp-system.git
cd mcp-system

# Verify download
ls -la
```

#### Run Installer
```bash
# Make installer executable
chmod +x install.sh

# Run installation
./install.sh
```

#### Installation Output
```
🚀 Starting One-Click MCP System Installation
==================================================
✅ Prerequisites check passed
✅ Directories created
✅ Components packaged
✅ Documentation packaged
✅ Universal launcher created
✅ Project initializer created
✅ Claude Code integration configured
✅ PATH integration complete
✅ Installation manifest created
==================================================
🎉 One-Click MCP System Installation Complete!
```

### 3. Verification

#### Test Installation
```bash
# Restart terminal or refresh PATH
source ~/.bashrc  # or ~/.zshrc

# Test commands
mcp-universal --help
mcp-init-project --help

# Check system status
mcp-universal bridge status
```

#### Run Installation Test
```bash
# Run comprehensive test suite
python3 scripts/test_installation.py
```

#### Expected Test Output
```
🧪 MCP System Installation Test
========================================
✅ Prerequisites OK
✅ Installation completed
✅ Commands working
✅ Project initialization OK
✅ Server creation OK
✅ Claude integration OK
✅ Upgrade system OK
========================================
📊 Test Results: 7/7 passed
🎉 All tests passed! MCP System is ready to use.
```

## ⚙️ Configuration

### Environment Configuration

#### Create Environment File
```bash
# Copy example configuration
cp .env.example ~/.mcp-system/.env

# Edit configuration
nano ~/.mcp-system/.env
```

#### Essential Settings
```bash
# System paths
MCP_SYSTEM_PATH="$HOME/.mcp-system"
MCP_AUTO_DISCOVERY=true
MCP_SAFE_MODE=true

# Default server settings
DEFAULT_HOST=localhost
DEFAULT_PORT_START=8050
DEFAULT_TEMPLATE=python-fastmcp

# Claude integration
CLAUDE_AUTO_INIT=true
CLAUDE_CONFIG_BACKUP=true
```

### Claude Desktop Configuration

The installer automatically configures Claude Desktop integration. Manual configuration:

```json
{
  "mcpServers": {
    "mcp-system": {
      "command": "mcp-universal",
      "args": ["router"],
      "env": {
        "MCP_SYSTEM_PATH": "/Users/yourname/.mcp-system",
        "MCP_AUTO_DISCOVERY": "true"
      }
    }
  }
}
```

### Shell Integration

#### Bash
Add to `~/.bashrc`:
```bash
# MCP System Integration
export PATH="$HOME/bin:$PATH"
export MCP_SYSTEM_PATH="$HOME/.mcp-system"

# Optional: Auto-initialize MCP in Claude projects
cd() {
    builtin cd "$@"
    if [[ -d .claude && -f mcp-universal ]]; then
        mcp-universal bridge auto-init
    fi
}
```

#### Zsh
Add to `~/.zshrc`:
```zsh
# MCP System Integration
export PATH="$HOME/bin:$PATH"
export MCP_SYSTEM_PATH="$HOME/.mcp-system"

# Optional: Auto-complete for MCP commands
autoload -U compinit
compinit
```

## 🚀 First Use

### Initialize Your First Project

#### Python Project
```bash
# Navigate to Python project
cd my-python-project

# Initialize MCP
mcp-init-project
# 🎯 Python project detected
# ✅ Created my-python-project-tools server

# Start using
./mcp my-python-project-tools start
```

#### Node.js Project
```bash
# Navigate to Node.js project
cd my-node-project

# Initialize MCP
mcp-init-project
# 🎯 Node.js project detected
# ✅ Created my-node-project-tools server

# Start using
./mcp my-node-project-tools start
```

#### Claude Code Project
```bash
# Navigate to Claude project (contains .claude/ directory)
cd my-claude-project

# Auto-initialize (detects Claude automatically)
mcp-universal
# ✅ Claude project detected - MCP integration active!

# Create project-specific tools
./mcp create assistant-tools --template python-fastmcp
```

### Create Your First Custom Server

```bash
# Create a weather tools server
mcp-universal create weather-tools --template python-fastmcp --port 8055

# Navigate to server directory
cd ~/mcp-weather-tools

# Install dependencies
pip install -r requirements.txt

# Edit server code
nano src/main.py

# Test the server
mcp-universal test weather-tools --start

# Deploy
mcp-universal weather-tools start
```

## 🔧 Troubleshooting

### Common Issues

#### Permission Denied
```bash
# Fix permissions
chmod +x ~/bin/mcp-*
chmod +x ~/.mcp-system/components/*
```

#### PATH Not Updated
```bash
# Manually add to PATH
export PATH="$HOME/bin:$PATH"

# Make permanent
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

#### Python Version Issues
```bash
# Check Python version
python3 --version

# If too old, install newer version
# macOS
brew install python@3.12

# Ubuntu
sudo apt install python3.12
```

#### Claude Integration Not Working
```bash
# Check Claude config
cat ~/.claude/claude_desktop_config.json

# Reinitialize bridge
mcp-universal bridge init

# Check bridge status
mcp-universal bridge status
```

### Getting Help

#### Check Logs
```bash
# View system logs
tail -f ~/.mcp-system/logs/*.log

# View server logs
mcp-universal my-server logs
```

#### Run Diagnostics
```bash
# System status
mcp-universal status

# Environment analysis
mcp-universal discover analyze

# Installation test
python3 scripts/test_installation.py
```

#### Reset Installation
```bash
# Complete reinstall
rm -rf ~/.mcp-system ~/bin/mcp-*
./install.sh
```

## 🎯 Next Steps

### Learn the Basics
1. Read the [Quick Start Guide](MCP-Quick-Start-Guide.md)
2. Explore the [Complete Documentation](MCP-Complete-Documentation.md)
3. Try the [Upgrade System](MCP-Upgrader-Documentation.md)

### Build Your First Server
1. Use `mcp-universal create` to generate a server
2. Customize the server code for your needs
3. Test with `mcp-universal test`
4. Deploy with `mcp-universal start`

### Join the Community
- **GitHub Issues**: Report bugs and request features
- **GitHub Discussions**: Ask questions and share projects
- **Contributing**: See [CONTRIBUTING.md](CONTRIBUTING.md)

---

**🎉 Congratulations! Your MCP System is now installed and ready to use.**

Continue with the [Quick Start Guide](MCP-Quick-Start-Guide.md) to begin creating and managing MCP servers.