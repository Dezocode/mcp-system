#!/usr/bin/env bash
#
# MCP System Universal Cross-Platform Installer
# Supports Linux, Windows (WSL/Native), macOS, and Docker environments
#

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[MCP INSTALLER]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[MCP INSTALLER]${NC} $1"; }
log_error() { echo -e "${RED}[MCP INSTALLER]${NC} $1"; }
log_debug() { echo -e "${BLUE}[MCP INSTALLER]${NC} $1"; }

# Detect platform and environment
detect_platform() {
    local platform_info=""
    
    # Check if we're in Docker
    if [ -f /.dockerenv ]; then
        platform_info="docker"
    # Check if we're in WSL
    elif grep -qEi "(Microsoft|WSL)" /proc/version 2>/dev/null; then
        platform_info="wsl"
    # Check operating system
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        platform_info="linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        platform_info="macos"
    elif [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        platform_info="windows"
    else
        platform_info="unknown"
    fi
    
    echo "$platform_info"
}

# Get cross-platform paths using Python resolver
get_platform_paths() {
    python3 -c "
import sys, os
sys.path.insert(0, 'src')
from config.cross_platform import cross_platform

paths = {
    'home': str(cross_platform.get_path('home')),
    'mcp_home': str(cross_platform.get_path('mcp_home')),
    'bin': str(cross_platform.get_path('bin')),
    'config': str(cross_platform.get_path('config')),
    'cache': str(cross_platform.get_path('cache')),
    'logs': str(cross_platform.get_path('logs')),
    'temp': str(cross_platform.get_path('temp'))
}

for key, path in paths.items():
    print(f'{key}={path}')
"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking system prerequisites..."
    
    local platform=$(detect_platform)
    log_debug "Detected platform: $platform"
    
    # Check Python 3
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is required but not installed"
        case $platform in
            "linux"|"wsl")
                log_info "Install with: sudo apt update && sudo apt install python3 python3-pip python3-venv"
                ;;
            "macos")
                log_info "Install with: brew install python3"
                ;;
            "windows")
                log_info "Download from: https://www.python.org/downloads/windows/"
                ;;
        esac
        return 1
    fi
    
    # Check pip
    if ! python3 -m pip --version &> /dev/null; then
        log_error "pip is required but not available"
        case $platform in
            "linux"|"wsl")
                log_info "Install with: sudo apt install python3-pip"
                ;;
            "macos")
                log_info "pip should be included with Python 3"
                ;;
            "windows")
                log_info "Reinstall Python with pip option enabled"
                ;;
        esac
        return 1
    fi
    
    # Check git
    if ! command -v git &> /dev/null; then
        log_warn "Git not found - some features may be limited"
        case $platform in
            "linux"|"wsl")
                log_info "Install with: sudo apt install git"
                ;;
            "macos")
                log_info "Install with: xcode-select --install"
                ;;
            "windows")
                log_info "Download from: https://git-scm.com/download/win"
                ;;
        esac
    fi
    
    log_info "✅ Prerequisites check completed"
    return 0
}

# Create directory structure
create_directories() {
    log_info "Creating MCP system directories..."
    
    # Get platform-specific paths
    eval $(get_platform_paths)
    
    local dirs=(
        "$mcp_home/.mcp-system/components"
        "$mcp_home/.mcp-system/docs" 
        "$mcp_home/.mcp-system/templates"
        "$mcp_home/.mcp-system/backups"
        "$mcp_home/.mcp-system/logs"
        "$mcp_home/.mcp-system/cache"
        "$mcp_home/bin"
        "$config"
        "$logs"
        "$cache"
    )
    
    for dir in "${dirs[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            log_debug "Created directory: $dir"
        fi
    done
    
    log_info "✅ Directory structure created"
}

# Install Python dependencies
install_dependencies() {
    log_info "Installing Python dependencies..."
    
    # Check if requirements.txt exists
    if [ ! -f "requirements.txt" ]; then
        log_error "requirements.txt not found"
        return 1
    fi
    
    # Handle externally managed Python environments
    local pip_args="--user"
    local platform=$(detect_platform)
    
    if [[ "$platform" == "docker" ]] || [[ "$VIRTUAL_ENV" != "" ]]; then
        pip_args=""
    fi
    
    # Install dependencies
    if python3 -m pip install $pip_args -r requirements.txt; then
        log_info "✅ Python dependencies installed"
    else
        log_warn "Standard pip install failed, trying with --break-system-packages"
        if python3 -m pip install --break-system-packages -r requirements.txt; then
            log_info "✅ Python dependencies installed (with system packages override)"
        else
            log_error "Failed to install Python dependencies"
            return 1
        fi
    fi
    
    return 0
}

# Install MCP system package
install_package() {
    log_info "Installing MCP system package..."
    
    # Check if pyproject.toml exists
    if [ ! -f "pyproject.toml" ]; then
        log_error "pyproject.toml not found"
        return 1
    fi
    
    local pip_args="--user -e"
    local platform=$(detect_platform)
    
    if [[ "$platform" == "docker" ]] || [[ "$VIRTUAL_ENV" != "" ]]; then
        pip_args="-e"
    fi
    
    # Install package in development mode
    if python3 -m pip install $pip_args .; then
        log_info "✅ MCP system package installed"
    else
        log_warn "Standard pip install failed, trying with --break-system-packages"
        if python3 -m pip install --break-system-packages -e .; then
            log_info "✅ MCP system package installed (with system packages override)"
        else
            log_error "Failed to install MCP system package"
            return 1
        fi
    fi
    
    return 0
}

# Create templates directory structure
create_templates() {
    log_info "Creating template directory structure..."
    
    eval $(get_platform_paths)
    local templates_dir="templates"
    
    # Create templates directory if it doesn't exist
    mkdir -p "$templates_dir"
    
    # Create basic template categories
    local template_dirs=(
        "$templates_dir/servers"
        "$templates_dir/clients" 
        "$templates_dir/tools"
        "$templates_dir/configs"
        "$templates_dir/scripts"
    )
    
    for dir in "${template_dirs[@]}"; do
        mkdir -p "$dir"
        log_debug "Created template directory: $dir"
    done
    
    # Create a basic server template if none exists
    if [ ! -f "$templates_dir/servers/basic_server.py" ]; then
        cat > "$templates_dir/servers/basic_server.py" << 'EOF'
#!/usr/bin/env python3
"""
Basic MCP Server Template
Auto-generated by MCP System Installer
"""

from mcp.server import Server
from mcp.types import Tool, TextContent
import asyncio

server = Server("basic-server")

@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="hello",
            description="Say hello",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string", 
                        "description": "Name to greet"
                    }
                },
                "required": ["name"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "hello":
        return [TextContent(
            type="text",
            text=f"Hello, {arguments.get('name', 'World')}!"
        )]
    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    from mcp.server.stdio import stdio_server
    await stdio_server(server)

if __name__ == "__main__":
    asyncio.run(main())
EOF
        log_debug "Created basic server template"
    fi
    
    log_info "✅ Template structure created"
}

# Setup PATH and environment
setup_environment() {
    log_info "Setting up environment variables..."
    
    eval $(get_platform_paths)
    local platform=$(detect_platform)
    
    # Determine shell profile
    local profile_file=""
    case $platform in
        "linux"|"wsl"|"docker")
            if [ -n "$BASH_VERSION" ]; then
                profile_file="$home/.bashrc"
            elif [ -n "$ZSH_VERSION" ]; then
                profile_file="$home/.zshrc" 
            else
                profile_file="$home/.profile"
            fi
            ;;
        "macos")
            if [ -n "$ZSH_VERSION" ]; then
                profile_file="$home/.zshrc"
            else
                profile_file="$home/.bash_profile"
            fi
            ;;
        "windows")
            log_warn "Manual PATH setup may be required on Windows"
            return 0
            ;;
    esac
    
    if [ -n "$profile_file" ] && [ -w "$(dirname "$profile_file")" ]; then
        # Add MCP system paths to profile
        local export_lines=(
            "# MCP System Environment"
            "export PATH=\"$mcp_home/bin:\$PATH\""
            "export MCP_SYSTEM_PATH=\"$mcp_home/.mcp-system\""
            "export MCP_AUTO_DISCOVERY=true"
            "export MCP_SAFE_MODE=true"
        )
        
        # Check if already added
        if ! grep -q "MCP System Environment" "$profile_file" 2>/dev/null; then
            echo "" >> "$profile_file"
            for line in "${export_lines[@]}"; do
                echo "$line" >> "$profile_file"
            done
            log_info "✅ Environment variables added to $profile_file"
            log_warn "Run 'source $profile_file' or restart your terminal"
        else
            log_debug "Environment variables already configured"
        fi
    fi
}

# Create executable scripts
create_executables() {
    log_info "Creating executable scripts..."
    
    eval $(get_platform_paths)
    
    # Create mcp-universal wrapper script
    local wrapper_script="$mcp_home/bin/mcp-universal"
    cat > "$wrapper_script" << EOF
#!/usr/bin/env python3
"""
MCP Universal Command Line Interface
Cross-platform wrapper for MCP system
"""

import sys
import os

# Add MCP system to Python path
mcp_system_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.mcp-system')
if os.path.exists(mcp_system_path):
    sys.path.insert(0, mcp_system_path)

try:
    from src.cli.main import main
    if __name__ == "__main__":
        main()
except ImportError as e:
    print(f"Error: Could not import MCP system: {e}")
    print("Please ensure the MCP system is properly installed")
    sys.exit(1)
EOF
    
    chmod +x "$wrapper_script"
    log_debug "Created executable: $wrapper_script"
    
    # Create platform-specific launcher
    local platform=$(detect_platform)
    case $platform in
        "windows")
            # Create .bat file for Windows
            local bat_script="$mcp_home/bin/mcp-universal.bat"
            cat > "$bat_script" << 'EOF'
@echo off
python3 "%~dp0mcp-universal" %*
EOF
            log_debug "Created Windows batch file: $bat_script"
            ;;
    esac
    
    log_info "✅ Executable scripts created"
}

# Verify installation
verify_installation() {
    log_info "Verifying installation..."
    
    eval $(get_platform_paths)
    
    # Check if mcp-universal is accessible
    local mcp_cmd="$mcp_home/bin/mcp-universal"
    if [ -x "$mcp_cmd" ]; then
        log_debug "mcp-universal executable found"
        
        # Try to run basic command
        if "$mcp_cmd" --version &>/dev/null || "$mcp_cmd" --help &>/dev/null; then
            log_info "✅ MCP system is working correctly"
        else
            log_warn "mcp-universal found but may have issues"
        fi
    else
        log_error "mcp-universal not found or not executable"
        return 1
    fi
    
    # Check Python package
    if python3 -c "import mcp; print('MCP package available')" &>/dev/null; then
        log_debug "MCP Python package accessible"
    else
        log_warn "MCP Python package may not be properly installed"
    fi
    
    return 0
}

# Main installation flow
main() {
    log_info "🚀 MCP System Universal Installer Starting"
    log_info "Platform: $(detect_platform)"
    echo "=============================================="
    
    # Run installation steps
    if ! check_prerequisites; then
        log_error "Prerequisites check failed"
        exit 1
    fi
    
    create_directories
    
    if ! install_dependencies; then
        log_error "Dependency installation failed" 
        exit 1
    fi
    
    if ! install_package; then
        log_error "Package installation failed"
        exit 1
    fi
    
    create_templates
    setup_environment
    create_executables
    
    if verify_installation; then
        echo "=============================================="
        log_info "🎉 MCP System Installation Complete!"
        log_info "Run 'mcp-universal --help' to get started"
        log_info "Or add $mcp_home/bin to your PATH if needed"
    else
        log_warn "Installation completed with warnings"
        log_info "Check the output above for any issues"
    fi
}

# Handle script arguments
case "${1:-install}" in
    "install")
        main
        ;;
    "check")
        check_prerequisites
        ;;
    "paths")
        get_platform_paths
        ;;
    "platform")
        echo "Platform: $(detect_platform)"
        ;;
    *)
        echo "Usage: $0 {install|check|paths|platform}"
        exit 1
        ;;
esac