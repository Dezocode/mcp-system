#!/usr/bin/env bash
#
# One-Click MCP System Installer
# Packages everything together for universal deployment
#

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[MCP-INSTALLER]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[MCP-INSTALLER]${NC} $1"; }
log_error() { echo -e "${RED}[MCP-INSTALLER]${NC} $1"; }
log_debug() { echo -e "${BLUE}[MCP-INSTALLER]${NC} $1"; }

# Installation configuration
INSTALL_DIR="$HOME/.mcp-system"
BIN_DIR="$HOME/bin"
CLAUDE_DIR="$HOME/.claude"
CURRENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Python
    if ! command -v f"{cross_platform.get_command(\"python\")} "&> /dev/null; then
        log_error "Python 3 is required but not installed"
        return 1
    fi
    
    # Check Python version
    python_version=$(f"{cross_platform.get_command(\"python\")} "-c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    python_major=$(echo $python_version | cut -d. -f1)
    python_minor=$(echo $python_version | cut -d. -f2)
    
    if [[ $python_major -lt 3 ]] || [[ $python_major -eq 3 && $python_minor -lt 8 ]]; then
        log_error "Python 3.8+ required, found $python_version"
        return 1
    fi
    
    # Check Git
    if ! command -v git &> /dev/null; then
        log_warn "Git not found - some features may be limited"
    fi
    
    log_info "✅ Prerequisites check passed"
    return 0
}

# Create directory structure
create_directories() {
    log_info "Creating directory structure..."
    
    directories=(
        "$INSTALL_DIR"
        "$INSTALL_DIR/components"
        "$INSTALL_DIR/docs"
        "$INSTALL_DIR/templates"
        "$INSTALL_DIR/backups"
        "$INSTALL_DIR/logs"
        "$BIN_DIR"
        "$CLAUDE_DIR"
    )
    
    for dir in "${directories[@]}"; do
        mkdir -p "$dir"
    done
    
    log_info "✅ Directories created"
}

# Package all components
package_components() {
    log_info "Packaging MCP components..."
    
    components=(
        "mcp"
        "mcp-router.py"
        "claude-mcp.sh"
        "mcp-create-server.py"
        "mcp-test-framework.py"
        "mcp-upgrader.py"
        "claude-upgrade.sh"
        "install-mcp-system.py"
        "claude-code-mcp-bridge.py"
    )
    
    for component in "${components[@]}"; do
        if [ -f "$CURRENT_DIR/$component" ]; then
            cp "$CURRENT_DIR/$component" "$INSTALL_DIR/components/"
            chmod +x "$INSTALL_DIR/components/$component"
            log_debug "  ✅ $component"
        else
            log_warn "  ⚠️  $component not found, creating placeholder"
            create_placeholder "$INSTALL_DIR/components/$component"
        fi
    done
    
    log_info "✅ Components packaged"
}

# Package documentation
package_documentation() {
    log_info "Packaging documentation..."
    
    docs=(
        "MCP-Complete-Documentation.md"
        "MCP-Upgrader-Documentation.md"
        "MCP-Quick-Start-Guide.md"
    )
    
    for doc in "${docs[@]}"; do
        if [ -f "$CURRENT_DIR/$doc" ]; then
            cp "$CURRENT_DIR/$doc" "$INSTALL_DIR/docs/"
            log_debug "  ✅ $doc"
        else
            log_warn "  ⚠️  $doc not found"
        fi
    done
    
    log_info "✅ Documentation packaged"
}

# Create placeholder for missing components
create_placeholder() {
    local file_path="$1"
    local file_name=$(basename "$file_path")
    
    if [[ "$file_path" == *.py ]]; then
        cat > "$file_path" << 'PLACEHOLDER_EOF'
#!/usr/bin/env python3
"""
Placeholder component - not found during installation
"""
print("⚠️  Component not available")
print("Please check installation or contact support")
PLACEHOLDER_EOF
    elif [[ "$file_path" == *.sh ]] || [[ ! "$file_path" == *.* ]]; then
        cat > "$file_path" << 'PLACEHOLDER_EOF'
#!/usr/bin/env bash
# Placeholder component
echo "⚠️  Component not available"
echo "Please check installation or contact support"
PLACEHOLDER_EOF
    fi
    
    chmod +x "$file_path"
}

# Create universal MCP launcher
create_universal_launcher() {
    log_info "Creating universal launcher..."
    
    cat > "$BIN_DIR/mcp-universal" << 'EOF'
#!/usr/bin/env python3
"""
Universal MCP System Launcher
Works in any project directory with auto-detection
"""

import os
import sys
import json
import subprocess
from pathlib import Path

class UniversalMCPLauncher:
    def __init__(self):
        self.home = Path.home()
        self.install_dir = self.home / ".mcp-system"
        self.current_project = Path.cwd()
        
    def detect_context(self):
        """Detect current project context"""
        # Check for project indicators
        indicators = {
            "python": ["pyproject.toml", "setup.py", "requirements.txt"],
            "nodejs": ["package.json", "node_modules"],
            "rust": ["Cargo.toml"],
            "go": ["go.mod"],
            "claude": [".claude", "CLAUDE.md"]
        }
        
        detected = []
        for context_type, patterns in indicators.items():
            for pattern in patterns:
                if (self.current_project / pattern).exists():
                    detected.append(context_type)
                    break
        
        return detected if detected else ["generic"]
    
    def auto_initialize(self):
        """Auto-initialize MCP for current project"""
        contexts = self.detect_context()
        
        if "claude" in contexts:
            # Claude project detected - run bridge
            bridge_path = self.install_dir / "components" / "claude-code-mcp-bridge.py"
            if bridge_path.exists():
                subprocess.run([sys.executable, str(bridge_path), "auto-init"])
                return True
        
        return False
    
    def route_command(self, args):
        """Route command to appropriate component"""
        if not args:
            # No arguments - try auto-initialization
            if self.auto_initialize():
                return 0
            else:
                self.show_help()
                return 0
        
        command = args[0]
        component_map = {
            "create": "mcp-create-server.py",
            "test": "mcp-test-framework.py",
            "upgrade": "claude-upgrade.sh",
            "router": "mcp-router.py",
            "bridge": "claude-code-mcp-bridge.py"
        }
        
        if command in component_map:
            component_path = self.install_dir / "components" / component_map[command]
            if component_path.exists():
                subprocess.run([sys.executable, str(component_path)] + args[1:])
                return 0
        
        # Default to main MCP launcher
        main_launcher = self.install_dir / "components" / "mcp"
        if main_launcher.exists():
            subprocess.run([str(main_launcher)] + args)
        else:
            print(f"❌ Component '{command}' not found")
            return 1
    
    def show_help(self):
        """Show help information"""
        contexts = self.detect_context()
        print(f"""
🎯 Universal MCP Launcher
📍 Current directory: {self.current_project}
🔍 Detected contexts: {', '.join(contexts)}

Commands:
  mcp-universal create <name>    Create new MCP server
  mcp-universal test [server]    Test MCP servers
  mcp-universal upgrade <server> Upgrade MCP server
  mcp-universal bridge init     Initialize Claude Code bridge
  mcp-universal <server> <cmd>  Control specific server

Auto-initialization:
  Running 'mcp-universal' in a Claude project automatically initializes MCP integration.
""")

if __name__ == "__main__":
    launcher = UniversalMCPLauncher()
    sys.exit(launcher.route_command(sys.argv[1:]))
EOF
    
    chmod +x "$BIN_DIR/mcp-universal"
    log_info "✅ Universal launcher created"
}

# Setup Claude Code integration
setup_claude_integration() {
    log_info "Setting up Claude Code integration..."
    
    # Create Claude configuration template
    cat > /tmp/claude_config_template.json << 'CONFIG_EOF'
{
  "mcpServers": {
    "mcp-system": {
      "command": "PLACEHOLDER_BIN_DIR/mcp-universal",
      "args": ["router"],
      "env": {
        "MCP_SYSTEM_PATH": "PLACEHOLDER_INSTALL_DIR",
        "MCP_AUTO_DISCOVERY": "true"
      }
    }
  },
  "mcp_system_integration": {
    "enabled": true,
    "auto_discovery": true,
    "safe_mode": true,
    "installation_path": "PLACEHOLDER_INSTALL_DIR",
    "version": "1.0.0"
  }
}
CONFIG_EOF
    
    # Replace placeholders
    sed -i.bak "s|PLACEHOLDER_BIN_DIR|$BIN_DIR|g" /tmp/claude_config_template.json
    sed -i.bak "s|PLACEHOLDER_INSTALL_DIR|$INSTALL_DIR|g" /tmp/claude_config_template.json
    
    claude_config_file="$CLAUDE_DIR/claude_desktop_config.json"
    
    if [ -f "$claude_config_file" ]; then
        log_info "Backing up existing Claude configuration..."
        cp "$claude_config_file" "$claude_config_file.backup.$(date +%s)"
        
        # Merge configurations using Python
        f"{cross_platform.get_command(\"python\")} "-c "
import json
import sys

try:
    with open('$claude_config_file', 'r') as f:
        existing = json.load(f)
except:
    existing = {}

with open('/tmp/claude_config_template.json', 'r') as f:
    new_config = json.load(f)

if 'mcpServers' not in existing:
    existing['mcpServers'] = {}

existing['mcpServers']['mcp-system'] = new_config['mcpServers']['mcp-system']
existing['mcp_system_integration'] = new_config['mcp_system_integration']

with open('$claude_config_file', 'w') as f:
    json.dump(existing, f, indent=2)

print('✅ Merged with existing Claude configuration')
"
    else
        cp /tmp/claude_config_template.json "$claude_config_file"
        log_info "✅ Created new Claude configuration"
    fi
    
    # Cleanup
    rm -f /tmp/claude_config_template.json /tmp/claude_config_template.json.bak
}

# Setup PATH integration
setup_path_integration() {
    log_info "Setting up PATH integration..."
    
    shell_configs=(
        "$HOME/.bashrc"
        "$HOME/.zshrc"
        "$HOME/.profile"
    )
    
    export_line="export PATH=\"$BIN_DIR:\$PATH\""
    mcp_env_line="export MCP_SYSTEM_PATH=\"$INSTALL_DIR\""
    
    for config_file in "${shell_configs[@]}"; do
        if [ -f "$config_file" ]; then
            # Check if already added
            if ! grep -q "$BIN_DIR" "$config_file"; then
                echo "" >> "$config_file"
                echo "# MCP System Integration" >> "$config_file"
                echo "$export_line" >> "$config_file"
                echo "$mcp_env_line" >> "$config_file"
                log_debug "  ✅ Added to $(basename "$config_file")"
            else
                log_debug "  ✅ Already configured in $(basename "$config_file")"
            fi
        fi
    done
    
    # Export for current session
    export PATH="$BIN_DIR:$PATH"
    export MCP_SYSTEM_PATH="$INSTALL_DIR"
    
    log_info "✅ PATH integration complete"
}

# Create project initialization script
create_project_init() {
    log_info "Creating project initialization script..."
    
    cat > "$BIN_DIR/mcp-init-project" << 'INIT_EOF'
#!/usr/bin/env bash
#
# MCP Project Initializer
# Automatically sets up MCP for any project
#

SCRIPT_DIR="$HOME/.mcp-system"

# Auto-detect and initialize
if [ -d ".claude" ] || [ -f "CLAUDE.md" ]; then
    echo "🎯 Claude project detected - initializing MCP integration..."
    f"{cross_platform.get_command(\"python\")} ""$SCRIPT_DIR/components/claude-code-mcp-bridge.py" init
elif [ -f "package.json" ]; then
    echo "🎯 Node.js project detected"
    mcp-universal create "$(basename $(pwd))-tools" --template typescript-node
elif [ -f "pyproject.toml" ] || [ -f "setup.py" ]; then
    echo "🎯 Python project detected"
    mcp-universal create "$(basename $(pwd))-tools" --template python-fastmcp
else
    echo "🎯 Generic project - setting up basic MCP integration"
    mcp-universal create "$(basename $(pwd))-tools" --template minimal-python
fi
INIT_EOF
    
    chmod +x "$BIN_DIR/mcp-init-project"
    log_info "✅ Project initializer created"
}

# Create installation manifest
create_installation_manifest() {
    log_info "Creating installation manifest..."
    
    manifest='{
  "installation": {
    "version": "1.0.0",
    "date": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'",
    "system": "'$(uname -s)'",
    "install_dir": "'$INSTALL_DIR'",
    "bin_dir": "'$BIN_DIR'"
  },
  "components": {
    "universal_launcher": "'$BIN_DIR'/mcp-universal",
    "project_initializer": "'$BIN_DIR'/mcp-init-project",
    "claude_bridge": "'$INSTALL_DIR'/components/claude-code-mcp-bridge.py",
    "main_installer": "'$INSTALL_DIR'/components/install-mcp-system.py"
  },
  "integration": {
    "claude_config": "'$CLAUDE_DIR'/claude_desktop_config.json",
    "path_configured": true,
    "auto_discovery": true
  }
}'
    
    echo "$manifest" > "$INSTALL_DIR/installation-manifest.json"
    log_info "✅ Installation manifest created"
}

# Main installation process
main() {
    log_info "🚀 Starting One-Click MCP System Installation"
    echo "=================================================="
    
    # Check prerequisites
    if ! check_prerequisites; then
        log_error "Prerequisites check failed"
        exit 1
    fi
    
    # Create directories
    create_directories
    
    # Package components
    package_components
    package_documentation
    
    # Create launchers
    create_universal_launcher
    create_project_init
    
    # Setup integrations
    setup_claude_integration
    setup_path_integration
    
    # Create manifest
    create_installation_manifest
    
    echo "=================================================="
    log_info "🎉 One-Click MCP System Installation Complete!"
    echo ""
    log_info "📋 Quick Start:"
    echo "  1. Restart your terminal or run: source ~/.bashrc"
    echo "  2. Navigate to any project directory"
    echo "  3. Run: mcp-universal"
    echo "  4. Or initialize: mcp-init-project"
    echo ""
    log_info "📚 Documentation:"
    echo "  View docs: ls $INSTALL_DIR/docs/"
    echo ""
    log_info "🔧 Claude Code Integration:"
    echo "  Automatically active in projects with .claude/ directory"
    echo "  Manual init: mcp-universal bridge init"
    echo ""
    log_info "✨ The system is ready for permissionless use in any project!"
}

# Run installation
main "$@"