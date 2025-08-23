#!/usr/bin/env bash
#
# MCP System Universal Cross-Platform Uninstaller
# Safely removes only components installed by install.sh
# Supports Linux, Windows (WSL/Native), macOS, and Docker environments
#

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[MCP UNINSTALLER]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[MCP UNINSTALLER]${NC} $1"; }
log_error() { echo -e "${RED}[MCP UNINSTALLER]${NC} $1"; }
log_debug() { echo -e "${BLUE}[MCP UNINSTALLER]${NC} $1"; }

# Configuration
DRY_RUN=${DRY_RUN:-false}
KEEP_DATA=${KEEP_DATA:-false}
FORCE=${FORCE:-false}

# Installation tracking file
INSTALL_MANIFEST=".mcp-install-manifest.json"

# Detect platform and environment (same as installer)
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
    if [ -f "src/config/cross_platform.py" ]; then
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
" 2>/dev/null || get_fallback_paths
    else
        get_fallback_paths
    fi
}

# Fallback path resolution when cross_platform.py is not available
get_fallback_paths() {
    local platform=$(detect_platform)
    local home_dir=""
    local bin_dir=""
    local config_dir=""
    local cache_dir=""
    local logs_dir=""
    local temp_dir=""
    
    case $platform in
        "docker")
            home_dir="/app"
            bin_dir="/usr/local/bin"
            config_dir="/etc/mcp"
            cache_dir="/var/cache/mcp"
            logs_dir="/var/log/mcp"
            temp_dir="/tmp/mcp"
            ;;
        "wsl"|"linux")
            home_dir="$HOME"
            bin_dir="$HOME/bin"
            config_dir="$HOME/.config"
            cache_dir="$HOME/.cache"
            logs_dir="$HOME/.local/share/logs"
            temp_dir="/tmp"
            ;;
        "macos")
            home_dir="$HOME"
            bin_dir="$HOME/bin"
            config_dir="$HOME/.config"
            cache_dir="$HOME/Library/Caches"
            logs_dir="$HOME/Library/Logs"
            temp_dir="/tmp"
            ;;
        "windows")
            # Windows paths in Bash environment (Git Bash/MSYS)
            home_dir="$HOME"
            bin_dir="$HOME/bin"
            config_dir="$HOME/.config"
            cache_dir="$HOME/AppData/Local/Cache"
            logs_dir="$HOME/AppData/Local/Logs"
            temp_dir="$TEMP"
            ;;
        *)
            home_dir="$HOME"
            bin_dir="$HOME/bin"
            config_dir="$HOME/.config"
            cache_dir="$HOME/.cache"
            logs_dir="$HOME/.local/share/logs"
            temp_dir="/tmp"
            ;;
    esac
    
    echo "home=$home_dir"
    echo "mcp_home=$home_dir"
    echo "bin=$bin_dir"
    echo "config=$config_dir"
    echo "cache=$cache_dir"
    echo "logs=$logs_dir"
    echo "temp=$temp_dir"
}

# Create installation manifest for tracking
create_manifest() {
    eval $(get_platform_paths)
    
    cat > "$INSTALL_MANIFEST" << EOF
{
    "timestamp": "$(date -Iseconds)",
    "platform": "$(detect_platform)",
    "directories_created": [
        "$mcp_home/.mcp-system",
        "$mcp_home/.mcp-system/components",
        "$mcp_home/.mcp-system/docs",
        "$mcp_home/.mcp-system/templates",
        "$mcp_home/.mcp-system/backups",
        "$mcp_home/.mcp-system/logs",
        "$mcp_home/.mcp-system/cache",
        "$mcp_home/bin",
        "$config",
        "$logs",
        "$cache",
        "templates",
        "templates/servers",
        "templates/clients",
        "templates/tools",
        "templates/configs",
        "templates/scripts"
    ],
    "files_created": [
        "$mcp_home/bin/mcp-universal",
        "$mcp_home/bin/mcp-universal.bat",
        "templates/servers/basic_server.py"
    ],
    "environment_modifications": [
        "PATH",
        "MCP_SYSTEM_PATH",
        "MCP_AUTO_DISCOVERY",
        "MCP_SAFE_MODE"
    ],
    "python_packages": [
        "mcp-system"
    ],
    "profile_files_modified": []
}
EOF
}

# Safe file removal
safe_remove() {
    local item="$1"
    local item_type="$2" # "file" or "dir"
    
    if [ "$DRY_RUN" = "true" ]; then
        log_debug "[DRY RUN] Would remove $item_type: $item"
        return 0
    fi
    
    if [ ! -e "$item" ]; then
        log_debug "$item_type not found: $item"
        return 0
    fi
    
    case $item_type in
        "file")
            if [ -f "$item" ]; then
                rm -f "$item"
                log_debug "Removed file: $item"
            fi
            ;;
        "dir")
            if [ -d "$item" ] && [ -z "$(ls -A "$item" 2>/dev/null)" ]; then
                rmdir "$item"
                log_debug "Removed empty directory: $item"
            elif [ -d "$item" ] && [ "$FORCE" = "true" ]; then
                rm -rf "$item"
                log_warn "Force removed directory: $item"
            elif [ -d "$item" ]; then
                log_warn "Directory not empty, skipping: $item"
            fi
            ;;
    esac
}

# Remove Python package
remove_python_package() {
    log_info "Removing Python package..."
    
    # Check if package is installed
    if python3 -c "import pkg_resources; pkg_resources.get_distribution('mcp-system')" &>/dev/null; then
        if [ "$DRY_RUN" = "true" ]; then
            log_debug "[DRY RUN] Would uninstall mcp-system package"
        else
            local pip_args=""
            local platform=$(detect_platform)
            
            if [[ "$platform" != "docker" ]] && [[ "$VIRTUAL_ENV" == "" ]]; then
                pip_args="--user"
            fi
            
            if python3 -m pip uninstall $pip_args -y mcp-system; then
                log_info "✅ Python package removed"
            else
                log_warn "Failed to remove Python package"
            fi
        fi
    else
        log_debug "MCP system package not found"
    fi
}

# Remove executables
remove_executables() {
    log_info "Removing executable scripts..."
    
    eval $(get_platform_paths)
    
    local executables=(
        "$mcp_home/bin/mcp-universal"
        "$mcp_home/bin/mcp-universal.bat"
    )
    
    for exe in "${executables[@]}"; do
        safe_remove "$exe" "file"
    done
}

# Remove templates (only if they're our generated ones)
remove_templates() {
    log_info "Removing generated templates..."
    
    # Only remove our basic template if it matches exactly
    if [ -f "templates/servers/basic_server.py" ]; then
        if grep -q "Auto-generated by MCP System Installer" "templates/servers/basic_server.py"; then
            safe_remove "templates/servers/basic_server.py" "file"
        else
            log_debug "Custom server template found, keeping: templates/servers/basic_server.py"
        fi
    fi
    
    # Remove empty template directories (only if empty)
    local template_dirs=(
        "templates/scripts"
        "templates/configs"
        "templates/tools"
        "templates/clients"
        "templates/servers"
        "templates"
    )
    
    for dir in "${template_dirs[@]}"; do
        safe_remove "$dir" "dir"
    done
}

# Remove directories
remove_directories() {
    log_info "Removing MCP directories..."
    
    eval $(get_platform_paths)
    
    if [ "$KEEP_DATA" = "true" ]; then
        log_warn "Keeping data directories as requested"
        return 0
    fi
    
    # Remove in reverse order of creation
    local dirs_to_remove=(
        "$cache"
        "$logs" 
        "$config"
        "$mcp_home/.mcp-system/cache"
        "$mcp_home/.mcp-system/logs"
        "$mcp_home/.mcp-system/backups"
        "$mcp_home/.mcp-system/templates"
        "$mcp_home/.mcp-system/docs"
        "$mcp_home/.mcp-system/components"
        "$mcp_home/.mcp-system"
    )
    
    for dir in "${dirs_to_remove[@]}"; do
        # Only remove if it's an MCP-specific directory
        if [[ "$dir" == *".mcp-system"* ]] || [[ "$dir" == *"mcp"* ]]; then
            safe_remove "$dir" "dir"
        else
            log_debug "Skipping system directory: $dir"
        fi
    done
    
    # Only remove bin directory if it's empty and we created it
    if [ -d "$mcp_home/bin" ] && [ -z "$(ls -A "$mcp_home/bin" 2>/dev/null)" ]; then
        safe_remove "$mcp_home/bin" "dir"
    fi
}

# Remove environment modifications from shell profiles
remove_environment() {
    log_info "Removing environment modifications..."
    
    eval $(get_platform_paths)
    local platform=$(detect_platform)
    
    # Determine shell profile files to check
    local profile_files=()
    case $platform in
        "linux"|"wsl"|"docker")
            [ -f "$home/.bashrc" ] && profile_files+=("$home/.bashrc")
            [ -f "$home/.zshrc" ] && profile_files+=("$home/.zshrc")
            [ -f "$home/.profile" ] && profile_files+=("$home/.profile")
            ;;
        "macos")
            [ -f "$home/.zshrc" ] && profile_files+=("$home/.zshrc")
            [ -f "$home/.bash_profile" ] && profile_files+=("$home/.bash_profile")
            ;;
        "windows")
            log_debug "Windows environment cleanup may require manual PATH removal"
            return 0
            ;;
    esac
    
    # Remove MCP environment block from each profile
    for profile in "${profile_files[@]}"; do
        if [ -f "$profile" ] && grep -q "# MCP System Environment" "$profile"; then
            if [ "$DRY_RUN" = "true" ]; then
                log_debug "[DRY RUN] Would remove MCP environment from: $profile"
            else
                # Create backup
                cp "$profile" "$profile.mcp-backup-$(date +%s)"
                
                # Remove MCP environment block
                sed -i '/# MCP System Environment/,/^$/d' "$profile"
                log_debug "Removed MCP environment from: $profile"
            fi
        fi
    done
}

# Show what would be removed
show_removal_plan() {
    log_info "📋 Uninstallation Plan"
    echo "======================"
    
    eval $(get_platform_paths)
    
    echo "Platform: $(detect_platform)"
    echo "Dry Run: $DRY_RUN"
    echo "Keep Data: $KEEP_DATA"
    echo "Force Remove: $FORCE"
    echo ""
    
    echo "🗂️  Directories to remove:"
    echo "   - $mcp_home/.mcp-system (and subdirectories)"
    echo "   - $mcp_home/bin (if empty)"
    echo "   - templates/ (if empty)"
    echo ""
    
    echo "📄 Files to remove:"
    echo "   - $mcp_home/bin/mcp-universal"
    echo "   - $mcp_home/bin/mcp-universal.bat"
    echo "   - templates/servers/basic_server.py (if auto-generated)"
    echo ""
    
    echo "🐍 Python packages to remove:"
    echo "   - mcp-system"
    echo ""
    
    echo "🔧 Environment modifications to remove:"
    echo "   - PATH entries pointing to MCP"
    echo "   - MCP_SYSTEM_PATH variable"
    echo "   - MCP_AUTO_DISCOVERY variable"
    echo "   - MCP_SAFE_MODE variable"
    echo ""
    
    if [ "$KEEP_DATA" = "true" ]; then
        echo "⚠️  Data directories will be KEPT"
    else
        echo "🗑️  Data directories will be removed"
    fi
}

# Main uninstallation flow
main() {
    log_info "🧹 MCP System Universal Uninstaller Starting"
    log_info "Platform: $(detect_platform)"
    echo "=============================================="
    
    # Show what will be removed
    show_removal_plan
    
    if [ "$DRY_RUN" != "true" ] && [ "$FORCE" != "true" ]; then
        echo ""
        read -p "Continue with uninstallation? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Uninstallation cancelled"
            exit 0
        fi
    fi
    
    echo ""
    log_info "Starting uninstallation..."
    
    # Remove in reverse order of installation
    remove_environment
    remove_executables
    remove_templates
    remove_python_package
    remove_directories
    
    # Remove manifest file
    safe_remove "$INSTALL_MANIFEST" "file"
    
    if [ "$DRY_RUN" = "true" ]; then
        echo "=============================================="
        log_info "🔍 Dry run completed - no changes made"
        log_info "Run without DRY_RUN=true to actually remove files"
    else
        echo "=============================================="
        log_info "🎉 MCP System Uninstallation Complete!"
        log_info "All MCP system components have been removed"
        
        if [ "$KEEP_DATA" = "true" ]; then
            log_warn "Data directories were preserved as requested"
        fi
        
        log_info "You may need to restart your terminal to clear environment variables"
    fi
}

# Handle script arguments and flags
usage() {
    cat << EOF
Usage: $0 [OPTIONS] [COMMAND]

Commands:
    uninstall    Remove MCP system (default)
    plan         Show what would be removed without doing it
    check        Check what MCP components are installed

Options:
    --dry-run           Show what would be removed without doing it
    --keep-data         Keep data directories and backups
    --force             Force removal without confirmation
    --help              Show this help message

Environment Variables:
    DRY_RUN=true        Same as --dry-run
    KEEP_DATA=true      Same as --keep-data  
    FORCE=true          Same as --force

Examples:
    $0                  # Interactive uninstall
    $0 --dry-run        # See what would be removed
    $0 --keep-data      # Remove software but keep data
    $0 --force          # Remove without confirmation
    DRY_RUN=true $0     # Environment variable version

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --keep-data)
            KEEP_DATA=true
            shift
            ;;
        --force)
            FORCE=true
            shift
            ;;
        --help)
            usage
            exit 0
            ;;
        plan)
            DRY_RUN=true
            shift
            ;;
        check)
            log_info "Checking MCP system installation..."
            eval $(get_platform_paths)
            
            echo "Platform: $(detect_platform)"
            echo "MCP directories:"
            [ -d "$mcp_home/.mcp-system" ] && echo "  ✅ $mcp_home/.mcp-system" || echo "  ❌ $mcp_home/.mcp-system"
            [ -d "$mcp_home/bin" ] && echo "  ✅ $mcp_home/bin" || echo "  ❌ $mcp_home/bin"
            
            echo "Executables:"
            [ -f "$mcp_home/bin/mcp-universal" ] && echo "  ✅ mcp-universal" || echo "  ❌ mcp-universal"
            
            echo "Python package:"
            if python3 -c "import pkg_resources; pkg_resources.get_distribution('mcp-system')" &>/dev/null; then
                echo "  ✅ mcp-system package installed"
            else
                echo "  ❌ mcp-system package not found"
            fi
            
            exit 0
            ;;
        uninstall|*)
            # Default command or unknown - proceed with uninstall
            shift
            ;;
    esac
done

# Run main uninstaller
main