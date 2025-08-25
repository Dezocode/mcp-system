#!/bin/bash
# Enhanced Production Entrypoint with Monitoring and High Availability
# Features: Health monitoring, auto-recovery, performance optimization, security hardening

set -euo pipefail

echo "🚀 Starting Enhanced MCP Production Environment"
echo "================================================================="

# Enhanced production environment setup
export MCP_ENV=docker-prod
export MCP_OPTIMIZE_FOR_PLATFORM=true
export MCP_ENABLE_PROFILING=true
export MCP_SAFE_MODE=true
export MCP_LOG_LEVEL=${MCP_LOG_LEVEL:-INFO}

# Production directories with proper permissions
mkdir -p /app/{logs,pipeline-sessions,cache,data,config/profiles,monitoring}
chmod 755 /app/{logs,pipeline-sessions,cache,data,config,monitoring}

# Setup production logging
exec > >(tee -a /app/logs/prod-startup.log)
exec 2>&1

echo "📋 Production Environment Configuration:"
echo "  - Environment: ${MCP_ENV}"
echo "  - Platform Optimization: ${MCP_OPTIMIZE_FOR_PLATFORM}"
echo "  - Profiling: ${MCP_ENABLE_PROFILING}"
echo "  - Safe Mode: ${MCP_SAFE_MODE}"
echo "  - Log Level: ${MCP_LOG_LEVEL}"
echo "  - Workspace: ${MCP_WORKSPACE_ROOT:-/app}"

# Health monitoring system
setup_health_monitoring() {
    echo "🏥 Setting up production health monitoring..."
    
    cat > /app/health_monitor.py << 'EOF'
#!/usr/bin/env python3
"""
Production Health Monitoring System
Provides comprehensive health checks and auto-recovery
"""

import json
import logging
import os
import psutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

class ProductionHealthMonitor:
    def __init__(self):
        self.log_file = Path("/app/logs/health-monitor.log")
        self.status_file = Path("/app/monitoring/health-status.json")
        self.recovery_file = Path("/app/monitoring/recovery-log.json")
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Health thresholds
        self.cpu_threshold = 90.0
        self.memory_threshold = 90.0
        self.disk_threshold = 95.0
        self.response_timeout = 30
        
        # Recovery state
        self.recovery_attempts = 0
        self.max_recovery_attempts = 3
        
    def check_system_health(self):
        """Comprehensive system health check"""
        health_status = {
            "timestamp": datetime.now().isoformat(),
            "status": "healthy",
            "checks": {},
            "issues": []
        }
        
        try:
            # CPU check
            cpu_percent = psutil.cpu_percent(interval=1)
            health_status["checks"]["cpu"] = {
                "value": cpu_percent,
                "threshold": self.cpu_threshold,
                "status": "ok" if cpu_percent < self.cpu_threshold else "warning"
            }
            if cpu_percent >= self.cpu_threshold:
                health_status["issues"].append(f"High CPU usage: {cpu_percent:.1f}%")
                
            # Memory check
            memory = psutil.virtual_memory()
            health_status["checks"]["memory"] = {
                "percent": memory.percent,
                "available_gb": memory.available / (1024**3),
                "threshold": self.memory_threshold,
                "status": "ok" if memory.percent < self.memory_threshold else "warning"
            }
            if memory.percent >= self.memory_threshold:
                health_status["issues"].append(f"High memory usage: {memory.percent:.1f}%")
                
            # Disk check
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            health_status["checks"]["disk"] = {
                "percent": disk_percent,
                "free_gb": disk.free / (1024**3),
                "threshold": self.disk_threshold,
                "status": "ok" if disk_percent < self.disk_threshold else "critical"
            }
            if disk_percent >= self.disk_threshold:
                health_status["issues"].append(f"High disk usage: {disk_percent:.1f}%")
                
            # Process check
            mcp_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if any('mcp' in str(cmd).lower() for cmd in proc.info['cmdline'] or []):
                        mcp_processes.append({
                            "pid": proc.info['pid'],
                            "name": proc.info['name'],
                            "status": proc.status()
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
            health_status["checks"]["processes"] = {
                "mcp_processes": mcp_processes,
                "count": len(mcp_processes),
                "status": "ok" if mcp_processes else "critical"
            }
            
            if not mcp_processes:
                health_status["issues"].append("No MCP processes running")
                
            # Application health check
            try:
                result = subprocess.run([
                    sys.executable, "scripts/docker-health-check.py"
                ], capture_output=True, text=True, timeout=self.response_timeout, cwd="/app")
                
                health_status["checks"]["application"] = {
                    "return_code": result.returncode,
                    "response_time": "< 30s",
                    "status": "ok" if result.returncode == 0 else "critical"
                }
                
                if result.returncode != 0:
                    health_status["issues"].append("Application health check failed")
                    
            except subprocess.TimeoutExpired:
                health_status["checks"]["application"] = {
                    "status": "critical",
                    "error": "Health check timeout"
                }
                health_status["issues"].append("Application health check timeout")
                
            # Determine overall status
            if any(check.get("status") == "critical" for check in health_status["checks"].values()):
                health_status["status"] = "critical"
            elif any(check.get("status") == "warning" for check in health_status["checks"].values()):
                health_status["status"] = "degraded"
                
        except Exception as e:
            health_status["status"] = "error"
            health_status["error"] = str(e)
            self.logger.error(f"Health check failed: {e}")
            
        # Save status
        self.status_file.parent.mkdir(exist_ok=True)
        with open(self.status_file, 'w') as f:
            json.dump(health_status, f, indent=2)
            
        return health_status
        
    def attempt_recovery(self, health_status):
        """Attempt automatic recovery from health issues"""
        if self.recovery_attempts >= self.max_recovery_attempts:
            self.logger.error("Maximum recovery attempts reached")
            return False
            
        self.recovery_attempts += 1
        recovery_log = {
            "timestamp": datetime.now().isoformat(),
            "attempt": self.recovery_attempts,
            "issues": health_status.get("issues", []),
            "actions": []
        }
        
        self.logger.info(f"Attempting recovery #{self.recovery_attempts}")
        
        try:
            # Restart MCP processes if needed
            if not health_status["checks"].get("processes", {}).get("mcp_processes"):
                self.logger.info("Restarting MCP services...")
                result = subprocess.run([
                    sys.executable, "/app/mcp-claude-pipeline-enhanced.py",
                    "--execution-mode", "production"
                ], cwd="/app")
                recovery_log["actions"].append("restarted_mcp_services")
                
            # Clear cache if disk usage high
            if health_status["checks"].get("disk", {}).get("percent", 0) > 90:
                self.logger.info("Clearing cache...")
                subprocess.run(["find", "/app/cache", "-type", "f", "-delete"])
                recovery_log["actions"].append("cleared_cache")
                
            # Rotate logs if needed
            log_size = sum(f.stat().st_size for f in Path("/app/logs").glob("*") if f.is_file())
            if log_size > 100 * 1024 * 1024:  # 100MB
                self.logger.info("Rotating logs...")
                subprocess.run(["find", "/app/logs", "-name", "*.log", "-size", "+10M", "-delete"])
                recovery_log["actions"].append("rotated_logs")
                
            recovery_log["success"] = True
            self.logger.info("Recovery attempt completed")
            
        except Exception as e:
            recovery_log["success"] = False
            recovery_log["error"] = str(e)
            self.logger.error(f"Recovery attempt failed: {e}")
            
        # Save recovery log
        if self.recovery_file.exists():
            with open(self.recovery_file, 'r') as f:
                recovery_history = json.load(f)
        else:
            recovery_history = []
            
        recovery_history.append(recovery_log)
        
        with open(self.recovery_file, 'w') as f:
            json.dump(recovery_history, f, indent=2)
            
        return recovery_log["success"]
        
    def run_monitoring_loop(self):
        """Main monitoring loop"""
        self.logger.info("Starting production health monitoring loop")
        
        while True:
            try:
                health_status = self.check_system_health()
                
                if health_status["status"] in ["critical", "degraded"]:
                    self.logger.warning(f"Health status: {health_status['status']} - Issues: {health_status['issues']}")
                    
                    if health_status["status"] == "critical":
                        recovery_success = self.attempt_recovery(health_status)
                        if not recovery_success:
                            self.logger.error("Recovery failed, manual intervention may be required")
                else:
                    self.logger.info("System health: OK")
                    self.recovery_attempts = 0  # Reset recovery counter on healthy status
                    
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
                
            time.sleep(60)  # Check every minute

if __name__ == "__main__":
    monitor = ProductionHealthMonitor()
    monitor.run_monitoring_loop()
EOF
    
    chmod +x /app/health_monitor.py
    python3 /app/health_monitor.py &
    HEALTH_PID=$!
    echo "   Health monitor started (PID: $HEALTH_PID)"
}

# Performance optimization
setup_performance_optimization() {
    echo "⚡ Setting up production performance optimization..."
    
    # Create performance optimizer
    cat > /app/performance_optimizer.py << 'EOF'
#!/usr/bin/env python3
"""Production Performance Optimizer"""

import json
import os
import time
import psutil
from pathlib import Path

class PerformanceOptimizer:
    def __init__(self):
        self.metrics_file = Path("/app/monitoring/performance-metrics.json")
        self.optimization_log = Path("/app/logs/optimization.log")
        
    def collect_metrics(self):
        """Collect performance metrics"""
        return {
            "timestamp": time.time(),
            "cpu": {
                "percent": psutil.cpu_percent(interval=1),
                "count": psutil.cpu_count(),
                "freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
            },
            "memory": psutil.virtual_memory()._asdict(),
            "disk": psutil.disk_usage('/')._asdict(),
            "network": psutil.net_io_counters()._asdict(),
            "processes": len(psutil.pids())
        }
        
    def optimize_system(self):
        """Apply system optimizations"""
        optimizations = []
        
        # Memory optimization
        memory = psutil.virtual_memory()
        if memory.percent > 80:
            # Clear page cache (if running as root)
            try:
                os.system("sync && echo 1 > /proc/sys/vm/drop_caches")
                optimizations.append("cleared_page_cache")
            except:
                pass
                
        # Process optimization
        if len(psutil.pids()) > 200:
            # Clean up zombie processes
            os.system("ps aux | awk '$8 ~ /^Z/ { print $2 }' | xargs -r kill -9")
            optimizations.append("cleaned_zombies")
            
        return optimizations
        
    def run_optimization_loop(self):
        """Main optimization loop"""
        while True:
            metrics = self.collect_metrics()
            
            # Save metrics
            self.metrics_file.parent.mkdir(exist_ok=True)
            with open(self.metrics_file, 'w') as f:
                json.dump(metrics, f, indent=2)
                
            # Apply optimizations if needed
            optimizations = self.optimize_system()
            if optimizations:
                with open(self.optimization_log, 'a') as f:
                    f.write(f"{time.time()}: Applied optimizations: {optimizations}\n")
                    
            time.sleep(300)  # Optimize every 5 minutes

if __name__ == "__main__":
    optimizer = PerformanceOptimizer()
    optimizer.run_optimization_loop()
EOF
    
    python3 /app/performance_optimizer.py &
    PERF_OPT_PID=$!
    echo "   Performance optimizer started (PID: $PERF_OPT_PID)"
}

# Security hardening
setup_security_hardening() {
    echo "🔒 Applying production security hardening..."
    
    # Set secure file permissions
    find /app -type f -name "*.py" -exec chmod 644 {} \;
    find /app -type f -name "*.sh" -exec chmod 755 {} \;
    find /app -type d -exec chmod 755 {} \;
    
    # Secure sensitive files
    chmod 600 /app/config/profiles/* 2>/dev/null || true
    
    # Create security monitor
    cat > /app/security_monitor.py << 'EOF'
#!/usr/bin/env python3
"""Production Security Monitor"""

import json
import subprocess
import time
from pathlib import Path

class SecurityMonitor:
    def __init__(self):
        self.security_log = Path("/app/logs/security.log")
        
    def check_file_integrity(self):
        """Check file integrity"""
        critical_files = [
            "/app/mcp-claude-pipeline-enhanced.py",
            "/app/run-pipeline-enhanced",
            "/app/run-direct-pipeline-enhanced"
        ]
        
        issues = []
        for file_path in critical_files:
            if not Path(file_path).exists():
                issues.append(f"Critical file missing: {file_path}")
            elif not os.access(file_path, os.R_OK):
                issues.append(f"Critical file not readable: {file_path}")
                
        return issues
        
    def scan_for_threats(self):
        """Basic threat scanning"""
        threats = []
        
        # Check for suspicious processes
        try:
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if any(suspicious in line.lower() for suspicious in ['nc', 'netcat', 'ncat']):
                    threats.append(f"Suspicious process detected: {line.strip()}")
        except:
            pass
            
        return threats
        
    def run_security_loop(self):
        """Main security monitoring loop"""
        while True:
            integrity_issues = self.check_file_integrity()
            threats = self.scan_for_threats()
            
            if integrity_issues or threats:
                security_event = {
                    "timestamp": time.time(),
                    "integrity_issues": integrity_issues,
                    "threats": threats
                }
                
                with open(self.security_log, 'a') as f:
                    f.write(json.dumps(security_event) + '\n')
                    
            time.sleep(600)  # Check every 10 minutes

if __name__ == "__main__":
    monitor = SecurityMonitor()
    monitor.run_security_loop()
EOF
    
    python3 /app/security_monitor.py &
    SEC_PID=$!
    echo "   Security monitor started (PID: $SEC_PID)"
}

# Main production startup
main() {
    echo "🔧 Initializing enhanced production environment..."
    
    # Setup production components
    setup_health_monitoring
    setup_performance_optimization
    setup_security_hardening
    
    echo "🚀 Starting MCP production orchestrator..."
    
    # Start main MCP orchestrator
    exec python3 /app/mcp-claude-pipeline-enhanced.py \
        --execution-mode production \
        --log-level "${MCP_LOG_LEVEL}" \
        --session-dir /app/pipeline-sessions \
        --max-cycles 1000 \
        --target-issues 0
}

# Cleanup on exit
cleanup() {
    echo "🧹 Cleaning up production environment..."
    pkill -P $$
    exit 0
}

trap cleanup SIGTERM SIGINT

# Run main
main "$@"