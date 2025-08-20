#!/bin/bash

# Claude Code MCP Integration Helper
# This script can be used as a tool in Claude Code to automatically
# select and interact with MCP servers based on user prompts

set -e

ROUTER="/Users/dezmondhollins/mcp-router.py"
MCP_CMD="/Users/dezmondhollins/mcp"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[MCP]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[MCP]${NC} $1"; }
log_error() { echo -e "${RED}[MCP]${NC} $1"; }

# Function to analyze prompt and start appropriate servers
setup_mcp_for_prompt() {
    local prompt="$1"
    
    log_info "Analyzing prompt for MCP server requirements..."
    
    # Use router to analyze prompt
    servers=$(python3 "$ROUTER" --analyze "$prompt" | jq -r '.recommended_servers[]' 2>/dev/null || echo "")
    
    if [ -z "$servers" ]; then
        log_warn "No specific MCP servers identified for this task"
        return 0
    fi
    
    log_info "Recommended servers: $(echo $servers | tr '\n' ' ')"
    
    # Start the primary server
    primary_server=$(echo "$servers" | head -n1)
    log_info "Starting primary server: $primary_server"
    
    if python3 "$MCP_CMD" "$primary_server" start; then
        log_info "✅ $primary_server is ready"
        
        # Get server details
        port=$(jq -r ".${primary_server}.port" ~/.mcp-servers.json 2>/dev/null || echo "unknown")
        log_info "Server accessible at: http://localhost:$port"
        
        # Return server info for Claude Code to use
        echo "MCP_SERVER=$primary_server"
        echo "MCP_PORT=$port"
        echo "MCP_URL=http://localhost:$port"
        
    else
        log_error "Failed to start $primary_server"
        return 1
    fi
}

# Function to send data to MCP server
send_to_mcp() {
    local server="$1"
    local tool="$2"
    local data="$3"
    
    log_info "Sending to $server: $tool"
    
    result=$(python3 "$ROUTER" --route "Using $tool" --tool "$tool" --data "$data")
    
    if echo "$result" | jq -e '.error' >/dev/null 2>&1; then
        log_error "$(echo "$result" | jq -r '.error')"
        return 1
    else
        log_info "✅ Success"
        echo "$result" | jq '.result'
    fi
}

# Function to interact with memory
memory() {
    local action="$1"
    shift
    
    case "$action" in
        save|store)
            local text="$*"
            send_to_mcp "mem0" "save_memory" "{\"text\": \"$text\"}"
            ;;
        search|find)
            local query="$*"
            send_to_mcp "mem0" "search_memories" "{\"query\": \"$query\", \"limit\": 5}"
            ;;
        list|all)
            send_to_mcp "mem0" "get_all_memories" "{}"
            ;;
        *)
            echo "Usage: memory [save|search|list] [text/query]"
            return 1
            ;;
    esac
}

# Main command dispatcher
case "${1:-help}" in
    analyze)
        shift
        setup_mcp_for_prompt "$*"
        ;;
    
    memory)
        shift
        memory "$@"
        ;;
    
    send)
        if [ $# -lt 4 ]; then
            echo "Usage: $0 send <server> <tool> <json_data>"
            exit 1
        fi
        send_to_mcp "$2" "$3" "$4"
        ;;
    
    list)
        log_info "Available MCP servers:"
        python3 "$MCP_CMD" list
        ;;
    
    status)
        log_info "MCP server status:"
        python3 "$MCP_CMD" status
        ;;
    
    interactive)
        log_info "Starting interactive MCP router..."
        python3 "$ROUTER" --interactive
        ;;
    
    help|*)
        cat << EOF
Claude Code MCP Integration Helper

Usage: $0 <command> [options]

Commands:
  analyze <prompt>           Analyze prompt and start appropriate servers
  memory save <text>         Save text to memory
  memory search <query>      Search memories
  memory list                List all memories
  send <server> <tool> <data> Send data to specific server
  list                       List all available servers
  status                     Show server status
  interactive                Start interactive router
  help                       Show this help

Examples:
  $0 analyze "Remember my coding preferences"
  $0 memory save "I prefer Python for data science"
  $0 memory search "programming language"
  $0 send mem0 save_memory '{"text":"Hello world"}'

Integration with Claude Code:
  Add this to your PATH and use as a tool in Claude Code sessions.
  Claude can automatically determine which MCP servers to use based on context.
EOF
        ;;
esac