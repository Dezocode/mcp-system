#!/usr/bin/env bash

# MCP Universal Launcher - Start any MCP server with dependencies
# Usage: ./mcp-launcher.sh [server-name] [action] [options]

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
MCP_BASE_DIR="${MCP_BASE_DIR:-$HOME/mcp-servers}"
MCP_CONFIG_FILE="${MCP_CONFIG_FILE:-$HOME/.mcp-config.json}"

# Functions
log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }

# Check dependencies
check_deps() {
    local server=$1
    case $server in
        mem0)
            # Check PostgreSQL
            if ! docker ps | grep -q mem0-postgres; then
                log_info "Starting PostgreSQL..."
                docker start mem0-postgres 2>/dev/null || \
                docker run --name mem0-postgres \
                    -e POSTGRES_PASSWORD=mysecretpassword \
                    -e POSTGRES_DB=mem0db \
                    -p 5432:5432 -d pgvector/pgvector:pg16
            fi
            
            # Check Ollama
            if ! curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
                log_info "Starting Ollama..."
                ollama serve >/dev/null 2>&1 &
                sleep 2
            fi
            ;;
        *)
            log_info "No specific dependencies for $server"
            ;;
    esac
}

# Start MCP server
start_server() {
    local server=$1
    local mode=${2:-background}
    
    log_info "Starting MCP server: $server"
    
    # Check dependencies first
    check_deps $server
    
    case $server in
        mem0)
            cd ~/mcp-mem0
            if [ "$mode" = "foreground" ]; then
                uv run python src/main.py
            else
                nohup uv run python src/main.py > /tmp/mcp-$server.log 2>&1 &
                echo $! > /tmp/mcp-$server.pid
                log_info "Server started with PID $(cat /tmp/mcp-$server.pid)"
                log_info "Logs: tail -f /tmp/mcp-$server.log"
            fi
            ;;
        *)
            log_error "Unknown server: $server"
            exit 1
            ;;
    esac
}

# Stop MCP server
stop_server() {
    local server=$1
    
    if [ -f /tmp/mcp-$server.pid ]; then
        PID=$(cat /tmp/mcp-$server.pid)
        if kill -0 $PID 2>/dev/null; then
            kill $PID
            rm /tmp/mcp-$server.pid
            log_info "Stopped server $server (PID $PID)"
        else
            log_warn "Server $server not running"
            rm /tmp/mcp-$server.pid
        fi
    else
        log_warn "No PID file found for $server"
    fi
}

# Status check
status_server() {
    local server=$1
    
    if [ -f /tmp/mcp-$server.pid ]; then
        PID=$(cat /tmp/mcp-$server.pid)
        if kill -0 $PID 2>/dev/null; then
            log_info "Server $server is running (PID $PID)"
            
            # Check actual connectivity
            case $server in
                mem0)
                    if curl -s http://localhost:8050/sse >/dev/null 2>&1; then
                        log_info "✓ Server responding at http://localhost:8050"
                    else
                        log_warn "Server process running but not responding"
                    fi
                    ;;
            esac
        else
            log_error "Server $server is not running"
            rm /tmp/mcp-$server.pid
        fi
    else
        log_error "Server $server is not running (no PID file)"
    fi
}

# Main command handler
main() {
    local server=${1:-mem0}
    local action=${2:-start}
    
    case $action in
        start)
            start_server $server background
            ;;
        start-fg)
            start_server $server foreground
            ;;
        stop)
            stop_server $server
            ;;
        restart)
            stop_server $server
            sleep 2
            start_server $server background
            ;;
        status)
            status_server $server
            ;;
        logs)
            if [ -f /tmp/mcp-$server.log ]; then
                tail -f /tmp/mcp-$server.log
            else
                log_error "No logs found for $server"
            fi
            ;;
        *)
            echo "Usage: $0 [server-name] [start|stop|restart|status|logs|start-fg]"
            echo "Examples:"
            echo "  $0 mem0 start     # Start mem0 server in background"
            echo "  $0 mem0 stop      # Stop mem0 server"
            echo "  $0 mem0 status    # Check server status"
            echo "  $0 mem0 logs      # Follow server logs"
            exit 1
            ;;
    esac
}

main "$@"