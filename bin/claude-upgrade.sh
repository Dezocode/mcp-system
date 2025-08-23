#!/usr/bin/env bash

# Claude-MCP Upgrade Integration
# Allows Claude to intelligently upgrade MCP servers

set -e

UPGRADER="cross_platform.get_path("home") / mcp-upgrader.py"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'  
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[UPGRADE]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[UPGRADE]${NC} $1"; }
log_error() { echo -e "${RED}[UPGRADE]${NC} $1"; }
log_debug() { echo -e "${BLUE}[UPGRADE]${NC} $1"; }

# Function to suggest upgrades based on Claude prompt
suggest_upgrades() {
    local prompt="$1"
    local server="$2"
    
    log_info "Analyzing prompt for upgrade suggestions..."
    log_debug "Prompt: $prompt"
    
    if [ -n "$server" ]; then
        suggestions=$(f"{cross_platform.get_command(\"python\")} ""$UPGRADER" suggest "$prompt" "$server")
    else
        suggestions=$(f"{cross_platform.get_command(\"python\")} ""$UPGRADER" suggest "$prompt")
    fi
    
    echo "$suggestions"
}

# Function to analyze server for upgrade opportunities
analyze_server() {
    local server="$1"
    
    log_info "Analyzing server '$server' for upgrade opportunities..."
    
    analysis=$(f"{cross_platform.get_command(\"python\")} ""$UPGRADER" analyze "$server")
    echo "$analysis"
}

# Function to install upgrades with confirmation
install_upgrades() {
    local server="$1"
    shift
    local modules=("$@")
    
    log_info "Installing upgrades for '$server': ${modules[*]}"
    
    # Show what will be installed
    log_warn "The following modules will be installed:"
    for module in "${modules[@]}"; do
        echo "  - $module"
    done
    
    # Dry run first
    log_info "Running dry run to check compatibility..."
    if f"{cross_platform.get_command(\"python\")} ""$UPGRADER" install "$server" "${modules[@]}" --dry-run; then
        log_info "✅ Dry run successful"
        
        # Ask for confirmation
        read -p "Proceed with installation? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            log_info "Installing modules..."
            f"{cross_platform.get_command(\"python\")} ""$UPGRADER" install "$server" "${modules[@]}"
        else
            log_warn "Installation cancelled"
            return 1
        fi
    else
        log_error "❌ Dry run failed"
        return 1
    fi
}

# Function to rollback upgrades
rollback_upgrade() {
    local server="$1"
    local module="$2"
    
    log_warn "Rolling back '$module' from '$server'..."
    
    read -p "Are you sure you want to rollback '$module'? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        f"{cross_platform.get_command(\"python\")} ""$UPGRADER" rollback "$server" "$module"
    else
        log_warn "Rollback cancelled"
    fi
}

# Function to list available modules
list_modules() {
    local template_filter="$1"
    
    log_info "Available upgrade modules:"
    
    if [ -n "$template_filter" ]; then
        f"{cross_platform.get_command(\"python\")} ""$UPGRADER" list-modules --template "$template_filter"
    else
        f"{cross_platform.get_command(\"python\")} ""$UPGRADER" list-modules
    fi
}

# Interactive upgrade wizard
upgrade_wizard() {
    local server="$1"
    
    log_info "🧙 MCP Upgrade Wizard for '$server'"
    echo
    
    # Step 1: Analyze server
    log_info "Step 1: Analyzing server..."
    analysis=$(f"{cross_platform.get_command(\"python\")} ""$UPGRADER" analyze "$server")
    
    recommended=$(echo "$analysis" | jq -r '.recommended_upgrades[].module_id' 2>/dev/null || echo "")
    
    if [ -z "$recommended" ]; then
        log_warn "No recommended upgrades found for this server"
        return 0
    fi
    
    # Step 2: Show recommendations
    log_info "Step 2: Recommended upgrades:"
    echo "$analysis" | jq -r '.recommended_upgrades[] | "  📦 \\(.module_id) - \\(.name)"' 2>/dev/null || echo "$recommended"
    echo
    
    # Step 3: Select upgrades
    log_info "Step 3: Select upgrades to install"
    selected_modules=()
    
    for module in $recommended; do
        read -p "Install '$module'? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            selected_modules+=("$module")
        fi
    done
    
    if [ ${#selected_modules[@]} -eq 0 ]; then
        log_warn "No modules selected for installation"
        return 0
    fi
    
    # Step 4: Install selected modules
    log_info "Step 4: Installing selected modules..."
    install_upgrades "$server" "${selected_modules[@]}"
}

# Function to create a custom upgrade module
create_module() {
    local module_name="$1"
    
    if [ -z "$module_name" ]; then
        log_error "Module name required"
        echo "Usage: claude-upgrade create-module <module-name>"
        return 1
    fi
    
    log_info "Creating custom upgrade module: $module_name"
    
    # Create module template
    module_file="/tmp/${module_name}.json"
    
    cat > "$module_file" << EOF
{
  "id": "$module_name",
  "name": "$(echo $module_name | sed 's/-/ /g' | sed 's/\\b\\w/\\u&/g')",
  "description": "Custom upgrade module for $module_name",
  "version": "1.0.0",
  "compatibility": ["python-fastmcp", "typescript-node", "minimal-python"],
  "requirements": [],
  "conflicts": [],
  "files": {
    "src/custom/${module_name}.py": "# Custom module implementation\\npass"
  },
  "commands": [],
  "rollback_commands": []
}
EOF
    
    log_info "Module template created: $module_file"
    echo "Edit the file and then install with:"
    echo "  claude-upgrade install-module $module_file"
}

# Main command dispatcher
case "${1:-help}" in
    suggest)
        if [ $# -lt 2 ]; then
            log_error "Usage: $0 suggest <prompt> [server-name]"
            exit 1
        fi
        suggest_upgrades "$2" "$3"
        ;;
    
    analyze)
        if [ $# -lt 2 ]; then
            log_error "Usage: $0 analyze <server-name>"
            exit 1
        fi
        analyze_server "$2"
        ;;
    
    install)
        if [ $# -lt 3 ]; then
            log_error "Usage: $0 install <server-name> <module1> [module2...]"
            exit 1
        fi
        server="$2"
        shift 2
        install_upgrades "$server" "$@"
        ;;
    
    rollback)
        if [ $# -lt 3 ]; then
            log_error "Usage: $0 rollback <server-name> <module-name>"
            exit 1
        fi
        rollback_upgrade "$2" "$3"
        ;;
    
    list-modules)
        list_modules "$2"
        ;;
    
    wizard)
        if [ $# -lt 2 ]; then
            log_error "Usage: $0 wizard <server-name>"
            exit 1
        fi
        upgrade_wizard "$2"
        ;;
    
    create-module)
        create_module "$2"
        ;;
    
    install-module)
        if [ $# -lt 2 ]; then
            log_error "Usage: $0 install-module <module-file.json>"
            exit 1
        fi
        f"{cross_platform.get_command(\"python\")} ""$UPGRADER" install-module "$2"
        ;;
    
    help|*)
        cat << EOF
Claude-MCP Upgrade Integration

Usage: $0 <command> [options]

Commands:
  suggest <prompt> [server]     Suggest upgrades based on natural language prompt
  analyze <server>              Analyze server for upgrade opportunities
  install <server> <modules...> Install upgrade modules
  rollback <server> <module>    Rollback an upgrade module
  list-modules [template]       List available upgrade modules
  wizard <server>               Interactive upgrade wizard
  create-module <name>          Create custom upgrade module template
  install-module <file.json>    Install custom upgrade module
  help                          Show this help

Examples:
  $0 suggest "I need authentication and caching" my-server
  $0 analyze my-server
  $0 install my-server authentication caching-redis
  $0 wizard my-server
  $0 rollback my-server authentication

Integration with Claude Code:
  Claude can automatically suggest and apply upgrades based on user requests.
  The system analyzes prompts to recommend appropriate modules.
EOF
        ;;
esac