#!/bin/bash
# Enhanced Development Entrypoint with Hot-reload and Debugging
# Features: File change detection, automatic server restart, state preservation, debug mode

set -euo pipefail

echo "🚀 Starting Enhanced MCP Development Environment"
echo "================================================================="

# Enhanced environment setup
export MCP_ENV=docker-dev
export MCP_DEBUG_MODE=true
export MCP_ENABLE_HOT_RELOAD=true
export MCP_LOG_LEVEL=DEBUG
export MCP_AUTO_RELOAD_CONFIG=true

# Enhanced development directories
mkdir -p /app/{logs,pipeline-sessions,cache,data,config/profiles}

# Setup development logging
exec > >(tee -a /app/logs/dev-startup.log)
exec 2>&1

echo "📋 Development Environment Configuration:"
echo "  - Hot Reload: ${MCP_ENABLE_HOT_RELOAD}"
echo "  - Debug Mode: ${MCP_DEBUG_MODE}"
echo "  - Log Level: ${MCP_LOG_LEVEL}"
echo "  - Workspace: ${MCP_WORKSPACE_ROOT:-/app}"

# File watcher for hot-reload
start_file_watcher() {
    echo "👁️  Starting file watcher for hot-reload..."
    
    # Create file watcher script
    cat > /app/file_watcher.py << 'EOF'
#!/usr/bin/env python3
"""
Enhanced File Watcher for MCP Development
Provides hot-reload capabilities with intelligent restart logic
"""

import os
import sys
import time
import signal
import subprocess
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class MCPFileHandler(FileSystemEventHandler):
    def __init__(self, restart_callback):
        self.restart_callback = restart_callback
        self.last_restart = 0
        self.restart_cooldown = 2  # seconds
        
    def on_modified(self, event):
        if event.is_directory:
            return
            
        # Filter relevant files
        if not any(event.src_path.endswith(ext) for ext in ['.py', '.json', '.yml', '.yaml', '.sh']):
            return
            
        # Avoid restart spam
        current_time = time.time()
        if current_time - self.last_restart < self.restart_cooldown:
            return
            
        print(f"🔄 File changed: {event.src_path}")
        self.last_restart = current_time
        self.restart_callback()

class MCPHotReloader:
    def __init__(self):
        self.process = None
        self.observer = None
        self.restart_count = 0
        
    def start_mcp_server(self):
        """Start the MCP server process"""
        if self.process:
            self.stop_mcp_server()
            
        print(f"🚀 Starting MCP server (restart #{self.restart_count})")
        
        cmd = [
            sys.executable,
            "mcp-claude-pipeline-enhanced.py",
            "--execution-mode", "development",
            "--log-level", "DEBUG",
            "--session-dir", "/app/pipeline-sessions"
        ]
        
        self.process = subprocess.Popen(
            cmd,
            cwd="/app",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        
        # Log output in background
        def log_output():
            for line in self.process.stdout:
                print(f"[MCP] {line}", end='')
                
        import threading
        threading.Thread(target=log_output, daemon=True).start()
        
    def stop_mcp_server(self):
        """Stop the MCP server process"""
        if self.process:
            print("🛑 Stopping MCP server...")
            self.process.terminate()
            try:
                self.process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
            self.process = None
            
    def restart_mcp_server(self):
        """Restart the MCP server"""
        self.restart_count += 1
        print(f"🔄 Restarting MCP server (restart #{self.restart_count})")
        self.start_mcp_server()
        
    def start_watching(self):
        """Start file system watching"""
        print("👁️  Starting file system watcher...")
        
        self.observer = Observer()
        handler = MCPFileHandler(self.restart_mcp_server)
        
        # Watch key directories
        watch_dirs = ["/app/src", "/app/scripts", "/app/mcp-tools"]
        for watch_dir in watch_dirs:
            if Path(watch_dir).exists():
                self.observer.schedule(handler, watch_dir, recursive=True)
                print(f"   Watching: {watch_dir}")
                
        self.observer.start()
        
    def run(self):
        """Main run loop"""
        def signal_handler(signum, frame):
            print("\n🛑 Shutting down hot reloader...")
            self.stop_mcp_server()
            if self.observer:
                self.observer.stop()
                self.observer.join()
            sys.exit(0)
            
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        try:
            self.start_mcp_server()
            self.start_watching()
            
            print("✅ Hot reloader active - watching for file changes...")
            print("   Press Ctrl+C to stop")
            
            # Keep alive
            while True:
                time.sleep(1)
                
                # Check if process died
                if self.process and self.process.poll() is not None:
                    print("⚠️  MCP server process died, restarting...")
                    self.restart_mcp_server()
                    
        except KeyboardInterrupt:
            print("\n🛑 Hot reloader interrupted")
        finally:
            self.stop_mcp_server()
            if self.observer:
                self.observer.stop()
                self.observer.join()

if __name__ == "__main__":
    reloader = MCPHotReloader()
    reloader.run()
EOF
    
    chmod +x /app/file_watcher.py
    python3 /app/file_watcher.py &
    FILE_WATCHER_PID=$!
    echo "   File watcher started (PID: $FILE_WATCHER_PID)"
}

# Debug toolkit setup
setup_debug_toolkit() {
    echo "🔧 Setting up development debug toolkit..."
    
    # Create debug helper script
    cat > /app/debug_toolkit.sh << 'EOF'
#!/bin/bash
# Development Debug Toolkit

echo "🔍 MCP Development Debug Toolkit"
echo "=================================="

case "${1:-help}" in
    "logs")
        echo "📋 Recent logs:"
        tail -f /app/logs/*.log
        ;;
    "status")
        echo "📊 MCP System Status:"
        echo "  Environment: ${MCP_ENV}"
        echo "  Debug Mode: ${MCP_DEBUG_MODE}"
        echo "  Hot Reload: ${MCP_ENABLE_HOT_RELOAD}"
        echo "  Processes:"
        ps aux | grep -E "(python|mcp)" | grep -v grep
        ;;
    "restart")
        echo "🔄 Restarting MCP server..."
        pkill -f "mcp-claude-pipeline-enhanced.py"
        sleep 2
        echo "✅ Server restart initiated"
        ;;
    "shell")
        echo "🐚 Entering debug shell..."
        /bin/bash
        ;;
    "help"|*)
        echo "Available commands:"
        echo "  logs    - Show live logs"
        echo "  status  - Show system status"
        echo "  restart - Restart MCP server"
        echo "  shell   - Enter debug shell"
        ;;
esac
EOF
    
    chmod +x /app/debug_toolkit.sh
    echo "   Debug toolkit available at: /app/debug_toolkit.sh"
}

# Performance monitoring for development
setup_performance_monitoring() {
    echo "📊 Setting up development performance monitoring..."
    
    # Create performance monitor
    cat > /app/performance_monitor.py << 'EOF'
#!/usr/bin/env python3
"""Development Performance Monitor"""

import psutil
import time
import json
from pathlib import Path

def monitor_performance():
    while True:
        metrics = {
            "timestamp": time.time(),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent,
            "process_count": len(psutil.pids())
        }
        
        # Log to performance file
        perf_file = Path("/app/logs/performance.jsonl")
        with open(perf_file, "a") as f:
            f.write(json.dumps(metrics) + "\n")
        
        time.sleep(30)  # Monitor every 30 seconds

if __name__ == "__main__":
    monitor_performance()
EOF
    
    python3 /app/performance_monitor.py &
    PERF_PID=$!
    echo "   Performance monitor started (PID: $PERF_PID)"
}

# Main development startup
main() {
    echo "🔧 Initializing enhanced development environment..."
    
    # Setup components
    setup_debug_toolkit
    setup_performance_monitoring
    
    # Start file watcher if hot reload enabled
    if [[ "${MCP_ENABLE_HOT_RELOAD}" == "true" ]]; then
        start_file_watcher
    else
        echo "🚀 Starting MCP server in development mode..."
        exec python3 /app/mcp-claude-pipeline-enhanced.py \
            --execution-mode development \
            --log-level DEBUG \
            --session-dir /app/pipeline-sessions
    fi
    
    # Keep container alive in hot-reload mode
    echo "✅ Development environment ready!"
    echo "   - Logs: /app/logs/"
    echo "   - Sessions: /app/pipeline-sessions/"
    echo "   - Debug toolkit: /app/debug_toolkit.sh"
    
    # Wait for processes
    wait
}

# Cleanup on exit
cleanup() {
    echo "🧹 Cleaning up development environment..."
    pkill -P $$
    exit 0
}

trap cleanup SIGTERM SIGINT

# Run main
main "$@"