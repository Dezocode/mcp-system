# Phase 2 Implementation Claude Plan
**Advanced MCP Server Features & Docker Integration**  
**Generated:** August 21, 2025  
**Based on:** Original Phase 2 plans + GitHub Agent Docker deployment + Current system state  
**Approach:** Line-by-line implementation with zero-downtime migration

---

## 🎯 Executive Assessment

### Current State vs. Phase 2 Vision
The GitHub Agent has provided **foundational Docker infrastructure** (docker-compose.prod.yml, deploy.sh, nginx.conf), but the **advanced MCP server features** from the original Phase 2 plan remain unimplemented. This plan bridges that gap systematically.

### Validation of Original Phase 2 Approach
✅ **VALID**: Real-time monitoring, parallel processing, ML predictions  
✅ **VALID**: Advanced session management with persistence  
✅ **PARTIALLY IMPLEMENTED**: Docker deployment (basic version exists)  
✅ **VALID**: Configuration management and environment detection  
❌ **NEEDS UPDATE**: Original assumes clean state, but we have 1,209 undefined functions

---

## 📋 DETAILED TODO LIST WITH SUBTABLES

## 🔴 Phase 2.0: Critical Foundation Fixes (Week 0)
*Must complete before implementing advanced features*

### ✅ TODO: Fix MCP Import Crisis
**Priority:** CRITICAL - Blocks 20% of test suite

| Subtask | Files | Lines | Action | Time Est. |
|---------|-------|-------|--------|-----------|
| 2.0.1 | `src/pipeline_mcp_server.py` | 31, 45 | Remove invalid MCP imports | 30 min |
| 2.0.2 | `src/exceptions.py` | NEW | Create custom exception system | 1 hour |
| 2.0.3 | `src/pipeline_mcp_server.py` | 416-733 | Replace all McpError references | 2 hours |
| 2.0.4 | `tests/test_pipeline_integration.py` | 200 | Update test expectations | 30 min |

**Detailed Implementation:**

#### Subtask 2.0.1: Remove Invalid MCP Imports
```python
# File: src/pipeline_mcp_server.py
# Line 31: REMOVE
# from src.mcp_local_types import ErrorCode

# Line 45: REMOVE  
# McpError

# ADD INSTEAD:
from enum import Enum

class ErrorCode(Enum):
    METHOD_NOT_FOUND = "method_not_found"
    INVALID_PARAMS = "invalid_params"
    INTERNAL_ERROR = "internal_error"
```

#### Subtask 2.0.2: Create Custom Exception System
```python
# File: src/exceptions.py (NEW FILE)
from typing import Any, Optional
from enum import Enum

class MCPErrorCode(Enum):
    METHOD_NOT_FOUND = "method_not_found"
    INVALID_PARAMS = "invalid_params" 
    INTERNAL_ERROR = "internal_error"
    SESSION_NOT_FOUND = "session_not_found"
    VALIDATION_FAILED = "validation_failed"

class MCPSystemError(Exception):
    """Custom MCP System Exception to replace McpError"""
    def __init__(self, error_code: MCPErrorCode, message: str, details: Optional[dict] = None):
        self.error_code = error_code
        self.message = message
        self.details = details or {}
        super().__init__(f"{error_code.value}: {message}")
        
    def to_dict(self):
        return {
            "error_code": self.error_code.value,
            "message": self.message,
            "details": self.details
        }
```

#### Subtask 2.0.3: Replace McpError References
```python
# File: src/pipeline_mcp_server.py
# Import the new exception (ADD after line 20)
from src.exceptions import MCPSystemError, MCPErrorCode

# Line 416: REPLACE
raise McpError(ErrorCode.METHOD_NOT_FOUND, f"Tool '{tool_name}' not found")
# WITH:
raise MCPSystemError(MCPErrorCode.METHOD_NOT_FOUND, f"Tool '{tool_name}' not found")

# Line 425: REPLACE
raise McpError(ErrorCode.INTERNAL_ERROR, f"Tool execution failed: {str(e)}")
# WITH:
raise MCPSystemError(MCPErrorCode.INTERNAL_ERROR, f"Tool execution failed: {str(e)}")

# Continue for all 11 remaining McpError instances...
```

---

### ✅ TODO: Resolve Undefined Function Calls
**Priority:** CRITICAL - 1,209 undefined functions block runtime

| Subtask | Files | Count | Action | Time Est. |
|---------|-------|-------|--------|-----------|
| 2.0.5 | `mcp-file-sync-manager.py` | 6 | Fix argparse usage | 1 hour |
| 2.0.6 | `scripts/claude_code_integration_loop.py` | 1 | Fix syntax error line 1269 | 30 min |
| 2.0.7 | Multiple files | 1,202 | Systematic import fixes | 8 hours |

**Detailed Implementation:**

#### Subtask 2.0.5: Fix ArgParse Issues
```python
# File: mcp-file-sync-manager.py
# ADD at top (line 1):
import argparse
import sys
from pathlib import Path

# Line 576-585: VERIFY parser initialization exists
# ADD if missing:
def main():
    parser = argparse.ArgumentParser(description="MCP File Sync Manager")
    parser.add_argument('--config', help='Configuration file path')
    parser.add_argument('--sync', action='store_true', help='Run sync operation')
    parser.add_argument('--backup', action='store_true', help='Create backup')
    args = parser.parse_args()
    
    sync_manager = MCPFileSyncManager(args.config)
    # ... rest of main logic
```

---

### ✅ TODO: Remove Duplicate Files
**Priority:** HIGH - Prevents confusion and maintenance issues

| Subtask | Action | Files Affected | Validation | Time Est. |
|---------|--------|----------------|------------|-----------|
| 2.0.8 | Remove core/ duplicates | 6 files | Ensure src/ versions work | 2 hours |
| 2.0.9 | Remove config duplicates | Multiple | Consolidate to single config | 1 hour |
| 2.0.10 | Clean snapshot files | 150+ files | Archive before removal | 1 hour |

**Detailed Implementation:**

#### Subtask 2.0.8: Remove Core Directory Duplicates
```bash
# Validation before removal:
diff src/claude_code_mcp_bridge.py core/claude-code-mcp-bridge.py
diff src/mcp_local_types.py core/mcp-create-server.py

# After validation, remove duplicates:
rm -f core/claude-code-mcp-bridge.py
rm -f core/mcp-create-server.py
rm -f core/mcp-router.py
rm -f core/mcp-test-framework.py
rm -f core/mcp-upgrader.py
rm -f configs/.mcp-system/components/*.py
```

---

## 🟡 Phase 2.1: Advanced MCP Server Features (Week 1-2)

### ✅ TODO: Implement Real-Time Pipeline Monitoring
**Priority:** HIGH - Core Phase 2 feature  
**Dependencies:** 2.0.1-2.0.4 complete

| Subtask | Files | Action | Integration Point | Time Est. |
|---------|-------|--------|------------------|-----------|
| 2.1.1 | `src/monitoring/` | Create monitoring module | New directory | 4 hours |
| 2.1.2 | `src/pipeline_mcp_server.py` | Add monitoring hooks | Lines 200-280 | 3 hours |
| 2.1.3 | WebSocket dashboard | Real-time updates | Port 3000 | 6 hours |
| 2.1.4 | Monitoring tests | Validation suite | `tests/` | 2 hours |

**Detailed Implementation:**

#### Subtask 2.1.1: Create Monitoring Module
```python
# File: src/monitoring/__init__.py (NEW)
"""Real-time pipeline monitoring system"""

# File: src/monitoring/realtime_monitor.py (NEW)
import asyncio
import time
import json
from typing import Dict, Any, List
from datetime import datetime, timezone

class RealtimeMonitor:
    """Real-time session monitoring with WebSocket support"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.start_time = None
        self.current_operation = None
        self.metrics = {}
        self.subscribers = set()  # WebSocket connections
        
    def start_monitoring(self, operation: str):
        """Start monitoring a specific operation"""
        self.current_operation = operation
        self.start_time = time.time()
        self.metrics[operation] = {
            "start_time": self.start_time,
            "status": "running"
        }
        
        # Broadcast to WebSocket subscribers
        self._broadcast_update({
            "session_id": self.session_id,
            "operation": operation,
            "status": "started",
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
    def stop_monitoring(self, operation: str, result_data: Dict[str, Any]):
        """Stop monitoring and record results"""
        end_time = time.time()
        duration = end_time - self.metrics[operation]["start_time"]
        
        self.metrics[operation].update({
            "end_time": end_time,
            "duration": duration,
            "status": "completed",
            "result_summary": self._extract_result_summary(result_data)
        })
        
        # Broadcast completion
        self._broadcast_update({
            "session_id": self.session_id,
            "operation": operation,
            "status": "completed",
            "duration": duration,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
    def _broadcast_update(self, update: Dict[str, Any]):
        """Broadcast update to all WebSocket subscribers"""
        # Implementation for WebSocket broadcasting
        pass
        
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current monitoring metrics"""
        return {
            "session_id": self.session_id,
            "current_operation": self.current_operation,
            "metrics": self.metrics,
            "total_operations": len(self.metrics)
        }
```

#### Subtask 2.1.2: Add Monitoring Hooks to MCP Server
```python
# File: src/pipeline_mcp_server.py
# ADD after line 20:
from monitoring.realtime_monitor import RealtimeMonitor
from monitoring.metrics_collector import MetricsCollector

# MODIFY PipelineSession class around line 80:
class PipelineSession:
    def __init__(self, session_id: str):
        # ... existing code ...
        
        # ADD MONITORING CAPABILITIES
        self.realtime_monitor = RealtimeMonitor(session_id)
        self.metrics_collector = MetricsCollector()
        self.performance_baseline = None
        
    def get_status_dict(self) -> Dict[str, Any]:
        # ... existing code ...
        
        # ADD MONITORING DATA
        status["monitoring"] = self.realtime_monitor.get_current_metrics()
        return status

# MODIFY handle_version_keeper_scan around line 220:
async def handle_version_keeper_scan(arguments: Dict[str, Any]) -> List[TextContent]:
    # ... existing code until session setup ...
    
    # ADD MONITORING START
    session.realtime_monitor.start_monitoring("version_keeper_scan")
    
    try:
        # ... existing command execution code ...
        
        # PARSE RESULT AND EXTRACT METRICS
        result_data = {
            "issues_found": 0,  # Extract from command output
            "files_analyzed": 0,  # Extract from command output
            "duration": 0  # Will be calculated by monitor
        }
        
        # ADD MONITORING STOP
        session.realtime_monitor.stop_monitoring("version_keeper_scan", result_data)
        
        # ... existing return code ...
        
    except Exception as e:
        # ADD ERROR MONITORING
        session.realtime_monitor.stop_monitoring("version_keeper_scan", {
            "error": str(e),
            "status": "failed"
        })
        raise
```

---

### ✅ TODO: Implement Parallel Processing Engine
**Priority:** HIGH - Performance critical feature  
**Dependencies:** 2.1.1-2.1.2 complete

| Subtask | Files | Action | Performance Target | Time Est. |
|---------|-------|--------|-------------------|-----------|
| 2.1.5 | `src/processing/` | Create parallel execution module | 3x speed improvement | 5 hours |
| 2.1.6 | `src/pipeline_mcp_server.py` | Integrate with pipeline_run_full | Lines 400-450 | 3 hours |
| 2.1.7 | Resource management | CPU/memory limits | Configurable limits | 2 hours |
| 2.1.8 | Parallel tests | Validation and benchmarks | `tests/` | 2 hours |

**Detailed Implementation:**

#### Subtask 2.1.5: Create Parallel Processing Module
```python
# File: src/processing/__init__.py (NEW)
"""Parallel processing engine for MCP pipeline"""

# File: src/processing/parallel_executor.py (NEW)
import asyncio
import concurrent.futures
from typing import List, Dict, Any, Callable
import multiprocessing

class ParallelExecutor:
    """Async parallel task execution with resource management"""
    
    def __init__(self, max_workers: int = None):
        self.max_workers = max_workers or min(4, multiprocessing.cpu_count())
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers)
        self.task_queue = asyncio.Queue()
        self.active_tasks = set()
        
    async def execute_parallel(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute multiple tasks in parallel"""
        # Create coroutines for each task
        coroutines = []
        for task in tasks:
            coroutine = self._execute_single_task(task)
            coroutines.append(coroutine)
            
        # Execute all tasks concurrently
        results = await asyncio.gather(*coroutines, return_exceptions=True)
        
        # Process results and handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "task_id": tasks[i].get("id", i),
                    "status": "failed",
                    "error": str(result)
                })
            else:
                processed_results.append(result)
                
        return processed_results
        
    async def _execute_single_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single task asynchronously"""
        task_type = task.get("type", "unknown")
        
        if task_type == "version_keeper":
            return await self._execute_version_keeper(task)
        elif task_type == "quality_patcher":
            return await self._execute_quality_patcher(task)
        else:
            raise ValueError(f"Unknown task type: {task_type}")
            
    async def _execute_version_keeper(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute version keeper task in thread pool"""
        loop = asyncio.get_event_loop()
        
        def run_version_keeper():
            import subprocess
            cmd = task.get("command", [])
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            return {
                "task_id": task.get("id"),
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
        return await loop.run_in_executor(self.executor, run_version_keeper)

# File: src/processing/job_queue.py (NEW)
import heapq
import asyncio
from typing import Dict, Any, Optional
from enum import Enum

class Priority(Enum):
    HIGH = 1
    MEDIUM = 2  
    LOW = 3

class JobQueue:
    """Priority-based job queue for task scheduling"""
    
    def __init__(self):
        self._queue = []
        self._index = 0
        self._lock = asyncio.Lock()
        
    async def put(self, task: Dict[str, Any], priority: Priority = Priority.MEDIUM):
        """Add task to queue with priority"""
        async with self._lock:
            heapq.heappush(self._queue, (priority.value, self._index, task))
            self._index += 1
            
    async def get(self) -> Optional[Dict[str, Any]]:
        """Get highest priority task from queue"""
        async with self._lock:
            if self._queue:
                _, _, task = heapq.heappop(self._queue)
                return task
            return None
```

#### Subtask 2.1.6: Integrate Parallel Processing
```python
# File: src/pipeline_mcp_server.py
# ADD import after line 25:
from processing.parallel_executor import ParallelExecutor
from processing.job_queue import JobQueue, Priority

# MODIFY handle_pipeline_run_full around line 420:
async def handle_pipeline_run_full(arguments: Dict[str, Any]) -> List[TextContent]:
    # ... existing setup code ...
    
    # ADD PARALLEL EXECUTOR INITIALIZATION
    parallel_executor = ParallelExecutor(max_workers=3)
    
    # MODIFY the pipeline cycle loop:
    for cycle in range(1, max_cycles + 1):
        cycle_start_time = time.time()
        
        # CREATE PARALLEL TASKS FOR CURRENT CYCLE
        parallel_tasks = [
            {
                "id": f"version_keeper_{cycle}",
                "type": "version_keeper", 
                "command": version_keeper_cmd,
                "session_dir": session_dir_path
            },
            {
                "id": f"quality_patcher_{cycle}",
                "type": "quality_patcher",
                "command": quality_patcher_cmd,
                "depends_on": f"version_keeper_{cycle}"  # Sequential dependency
            }
        ]
        
        # EXECUTE TASKS IN PARALLEL (where possible)
        version_keeper_result = await parallel_executor.execute_parallel([parallel_tasks[0]])
        
        # Check if we need quality patcher
        if version_keeper_result[0].get("returncode") != 0:
            quality_patcher_result = await parallel_executor.execute_parallel([parallel_tasks[1]])
            
        # ... rest of existing cycle logic ...
```

---

### ✅ TODO: Advanced Session Management with Persistence
**Priority:** MEDIUM - Reliability feature  
**Dependencies:** 2.1.1-2.1.6 complete

| Subtask | Files | Action | Storage Backend | Time Est. |
|---------|-------|--------|----------------|-----------|
| 2.1.9 | `src/session/` | Create session persistence | SQLite/Redis | 4 hours |
| 2.1.10 | `src/pipeline_mcp_server.py` | Add checkpoint system | Lines 80-120 | 2 hours |
| 2.1.11 | Recovery mechanism | Crash recovery logic | Automatic restore | 3 hours |
| 2.1.12 | Session clustering | Multi-instance coordination | Redis pub/sub | 4 hours |

**Detailed Implementation:**

#### Subtask 2.1.9: Create Session Persistence
```python
# File: src/session/__init__.py (NEW)
"""Advanced session management and persistence"""

# File: src/session/session_persistence.py (NEW)
import json
import sqlite3
import asyncio
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime, timezone

class SessionPersistence:
    """Session state persistence with SQLite backend"""
    
    def __init__(self, session_id: str, db_path: Path = None):
        self.session_id = session_id
        self.db_path = db_path or Path("pipeline_sessions.db")
        self._init_database()
        
    def _init_database(self):
        """Initialize SQLite database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                state TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'active'
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS checkpoints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                checkpoint_type TEXT,
                state TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions (session_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
    async def save_session_state(self, state: Dict[str, Any]):
        """Save current session state"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        state_json = json.dumps(state, default=str)
        
        cursor.execute('''
            INSERT OR REPLACE INTO sessions (session_id, state, updated_at)
            VALUES (?, ?, ?)
        ''', (self.session_id, state_json, datetime.now(timezone.utc)))
        
        conn.commit()
        conn.close()
        
    async def create_checkpoint(self, checkpoint_type: str, state: Dict[str, Any]):
        """Create a recovery checkpoint"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        state_json = json.dumps(state, default=str)
        
        cursor.execute('''
            INSERT INTO checkpoints (session_id, checkpoint_type, state)
            VALUES (?, ?, ?)
        ''', (self.session_id, checkpoint_type, state_json))
        
        conn.commit()
        conn.close()
        
    async def restore_session(self) -> Optional[Dict[str, Any]]:
        """Restore session from last saved state"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT state FROM sessions WHERE session_id = ?
        ''', (self.session_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return json.loads(result[0])
        return None

# File: src/session/session_recovery.py (NEW)
import asyncio
import logging
from typing import Dict, Any, Optional
from .session_persistence import SessionPersistence

class SessionRecovery:
    """Automatic session recovery system"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.persistence = SessionPersistence(session_id)
        self.logger = logging.getLogger(f"recovery.{session_id}")
        
    async def setup_recovery(self, session_state: Dict[str, Any]):
        """Setup recovery mechanism for session"""
        # Create initial checkpoint
        await self.persistence.create_checkpoint("initialization", session_state)
        self.logger.info(f"Recovery setup complete for session {self.session_id}")
        
    async def handle_crash_recovery(self) -> Optional[Dict[str, Any]]:
        """Handle recovery from unexpected crash"""
        self.logger.info(f"Attempting crash recovery for session {self.session_id}")
        
        # Try to restore from last saved state
        restored_state = await self.persistence.restore_session()
        
        if restored_state:
            self.logger.info(f"Session {self.session_id} restored from checkpoint")
            return restored_state
        else:
            self.logger.warning(f"No recovery data found for session {self.session_id}")
            return None
            
    async def create_operation_checkpoint(self, operation: str, state: Dict[str, Any]):
        """Create checkpoint before starting risky operation"""
        checkpoint_type = f"before_{operation}"
        await self.persistence.create_checkpoint(checkpoint_type, state)
        self.logger.debug(f"Created checkpoint before {operation}")
```

#### Subtask 2.1.10: Add Checkpoint System to MCP Server
```python
# File: src/pipeline_mcp_server.py
# ADD imports after line 25:
from session.session_persistence import SessionPersistence
from session.session_recovery import SessionRecovery

# MODIFY PipelineSession class around line 80:
class PipelineSession:
    def __init__(self, session_id: str):
        # ... existing code ...
        
        # ADD ADVANCED SESSION FEATURES
        self.persistence_manager = SessionPersistence(session_id)
        self.recovery_handler = SessionRecovery(session_id)
        self.checkpoint_interval = 30  # seconds
        self.last_checkpoint = time.time()
        
        # Setup recovery mechanism
        asyncio.create_task(self._setup_session_recovery())
        
    async def _setup_session_recovery(self):
        """Setup recovery mechanism for this session"""
        initial_state = self.get_status_dict()
        await self.recovery_handler.setup_recovery(initial_state)
        
    async def create_checkpoint(self, operation: str = None):
        """Create session checkpoint"""
        current_state = self.get_status_dict()
        
        if operation:
            await self.recovery_handler.create_operation_checkpoint(operation, current_state)
        else:
            await self.persistence_manager.save_session_state(current_state)
            
        self.last_checkpoint = time.time()
        
    def should_create_checkpoint(self) -> bool:
        """Check if it's time for automatic checkpoint"""
        return (time.time() - self.last_checkpoint) >= self.checkpoint_interval

# MODIFY all handle_* methods to add checkpointing:
async def handle_version_keeper_scan(arguments: Dict[str, Any]) -> List[TextContent]:
    # ... existing setup code ...
    
    # ADD CHECKPOINT BEFORE RISKY OPERATION
    await session.create_checkpoint("version_keeper_scan")
    
    try:
        # ... existing command execution ...
        
        # CREATE CHECKPOINT AFTER SUCCESS
        if session.should_create_checkpoint():
            await session.create_checkpoint()
            
        # ... existing return code ...
        
    except Exception as e:
        # Log the error but don't checkpoint failed state
        logger.error(f"Version keeper scan failed: {e}")
        raise
```

---

## 🟢 Phase 2.2: Docker Integration Enhancement (Week 3-4)
*Building on existing GitHub Agent Docker files*

### ✅ TODO: Enhance Existing Docker Configuration
**Priority:** MEDIUM - Build on GitHub Agent foundation  
**Dependencies:** Phase 2.1 complete

| Subtask | Files | Current State | Enhancement | Time Est. |
|---------|-------|---------------|-------------|-----------|
| 2.2.1 | `docker-compose.prod.yml` | Basic setup | Add monitoring services | 2 hours |
| 2.2.2 | `deploy.sh` | Simple deployment | Add health checks & rollback | 3 hours |
| 2.2.3 | `nginx.conf` | Basic proxy | Add load balancing | 2 hours |
| 2.2.4 | Dockerfile optimization | Single stage | Multi-stage build | 2 hours |

**Detailed Implementation:**

#### Subtask 2.2.1: Enhance Docker Compose with Monitoring
```yaml
# File: docker-compose.prod.yml (ENHANCE EXISTING)
# ADD to existing services:

  mcp-dashboard:
    build:
      context: .
      dockerfile: docker/Dockerfile.dashboard
    ports:
      - "3000:3000"
    environment:
      - MCP_SERVER_URL=http://mcp-system:8080
      - WEBSOCKET_ENABLED=true
    depends_on:
      - mcp-system
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin123
    volumes:
      - grafana-data:/var/lib/grafana
    depends_on:
      - prometheus

# ADD to volumes section:
  prometheus-data:
  grafana-data:
```

#### Subtask 2.2.2: Enhance Deployment Script
```bash
# File: deploy.sh (ENHANCE EXISTING)
# ADD after line 20 (existing color definitions):

# Health check function
check_service_health() {
    local service_name=$1
    local max_attempts=30
    local attempt=1
    
    log_info "Checking health of $service_name..."
    
    while [ $attempt -le $max_attempts ]; do
        if docker-compose ps $service_name | grep -q "healthy\|Up"; then
            log_info "✅ $service_name is healthy"
            return 0
        fi
        
        log_warn "Attempt $attempt/$max_attempts: $service_name not ready..."
        sleep 10
        ((attempt++))
    done
    
    log_error "❌ $service_name failed health check after $max_attempts attempts"
    return 1
}

# Rollback function  
rollback_deployment() {
    log_warn "🔄 Starting rollback process..."
    
    # Stop new containers
    docker-compose down
    
    # Restore from backup if available
    if [ -f "docker-compose.backup.yml" ]; then
        log_info "Restoring previous configuration..."
        cp docker-compose.backup.yml docker-compose.prod.yml
        docker-compose up -d
        log_info "✅ Rollback completed"
    else
        log_error "❌ No backup configuration found"
        exit 1
    fi
}

# ADD after existing deployment logic (around line 100):
# Create backup of current configuration
cp docker-compose.prod.yml docker-compose.backup.yml

# Deploy with health checks
log_info "🚀 Starting enhanced deployment..."
docker-compose up -d

# Health check sequence
SERVICES=("postgres" "redis" "mcp-system" "mcp-dashboard" "prometheus" "grafana")

for service in "${SERVICES[@]}"; do
    if ! check_service_health $service; then
        log_error "Health check failed for $service"
        rollback_deployment
        exit 1
    fi
done

log_info "🎉 All services healthy - deployment successful!"
```

---

### ✅ TODO: Environment Detection and Configuration
**Priority:** MEDIUM - Smart deployment adaptation  
**Dependencies:** 2.2.1-2.2.2 complete

| Subtask | Files | Action | Detection Method | Time Est. |
|---------|-------|--------|-----------------|-----------|
| 2.2.5 | `src/config/environment_detector.py` | Create detector | Check env vars & filesystem | 2 hours |
| 2.2.6 | `src/config/docker_config.py` | Docker-specific config | Override defaults | 1 hour |
| 2.2.7 | `src/pipeline_mcp_server.py` | Integrate detection | Lines 100-150 | 1 hour |
| 2.2.8 | Configuration validation | Ensure all paths work | Both environments | 1 hour |

**Detailed Implementation:**

#### Subtask 2.2.5: Create Environment Detector
```python
# File: src/config/environment_detector.py (NEW)
import os
import platform
from pathlib import Path
from typing import Dict, Any

class EnvironmentDetector:
    """Detect runtime environment and adapt configuration"""
    
    def __init__(self):
        self.platform = platform.system().lower()
        
    def is_running_in_docker(self) -> bool:
        """Detect if running inside Docker container"""
        # Method 1: Check for .dockerenv file
        if Path('/.dockerenv').exists():
            return True
            
        # Method 2: Check environment variables
        if os.getenv('DOCKER_CONTAINER'):
            return True
            
        # Method 3: Check cgroup info (Linux only)
        if self.platform == 'linux':
            try:
                with open('/proc/self/cgroup', 'r') as f:
                    if 'docker' in f.read().lower():
                        return True
            except (FileNotFoundError, PermissionError):
                pass
                
        return False
        
    def get_environment_info(self) -> Dict[str, Any]:
        """Get comprehensive environment information"""
        return {
            "platform": self.platform,
            "is_docker": self.is_running_in_docker(),
            "python_version": platform.python_version(),
            "working_directory": str(Path.cwd()),
            "environment_variables": {
                "PATH": os.getenv("PATH"),
                "HOME": os.getenv("HOME"),
                "USER": os.getenv("USER"),
                "MCP_ENV": os.getenv("MCP_ENV", "development")
            }
        }
        
    def get_recommended_config(self) -> Dict[str, Any]:
        """Get environment-specific configuration recommendations"""
        if self.is_running_in_docker():
            return {
                "workspace_root": "/app",
                "session_dir": "/app/pipeline-sessions", 
                "log_level": "INFO",
                "enable_dashboard": True,
                "max_workers": 4,
                "database_path": "/app/data/sessions.db"
            }
        else:
            return {
                "workspace_root": str(Path.cwd()),
                "session_dir": str(Path.cwd() / "pipeline-sessions"),
                "log_level": "DEBUG", 
                "enable_dashboard": False,
                "max_workers": 2,
                "database_path": str(Path.cwd() / "sessions.db")
            }
```

#### Subtask 2.2.6: Create Docker-Specific Configuration
```python
# File: src/config/docker_config.py (NEW)
import os
from typing import Dict, Any
from pathlib import Path

class DockerConfig:
    """Docker-specific configuration overrides"""
    
    def __init__(self):
        self.config = self._load_docker_config()
        
    def _load_docker_config(self) -> Dict[str, Any]:
        """Load configuration optimized for Docker environment"""
        return {
            # File system paths
            "workspace_root": Path("/app"),
            "session_dir": Path("/app/pipeline-sessions"), 
            "config_dir": Path("/app/config"),
            "logs_dir": Path("/app/logs"),
            
            # Database configuration
            "database": {
                "type": "postgresql",
                "host": os.getenv("POSTGRES_HOST", "postgres"),
                "port": int(os.getenv("POSTGRES_PORT", "5432")),
                "database": os.getenv("POSTGRES_DB", "pipeline_mcp"),
                "username": os.getenv("POSTGRES_USER", "mcp_user"),
                "password": os.getenv("POSTGRES_PASSWORD", "secure_password")
            },
            
            # Redis configuration
            "redis": {
                "host": os.getenv("REDIS_HOST", "redis"),
                "port": int(os.getenv("REDIS_PORT", "6379")),
                "db": int(os.getenv("REDIS_DB", "0"))
            },
            
            # MCP server configuration
            "mcp_server": {
                "port": int(os.getenv("MCP_SERVER_PORT", "8080")),
                "host": "0.0.0.0",  # Listen on all interfaces in Docker
                "max_workers": int(os.getenv("MAX_WORKERS", "4")),
                "timeout": int(os.getenv("REQUEST_TIMEOUT", "300"))
            },
            
            # Monitoring configuration
            "monitoring": {
                "enable_dashboard": os.getenv("ENABLE_DASHBOARD", "true").lower() == "true",
                "dashboard_port": int(os.getenv("DASHBOARD_PORT", "3000")),
                "metrics_enabled": True,
                "prometheus_endpoint": "/metrics"
            }
        }
        
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
                
        return value
        
    def update(self, updates: Dict[str, Any]):
        """Update configuration with new values"""
        self.config.update(updates)
```

#### Subtask 2.2.7: Integrate Environment Detection
```python
# File: src/pipeline_mcp_server.py
# ADD imports after line 25:
from config.environment_detector import EnvironmentDetector
from config.docker_config import DockerConfig

# MODIFY PipelineMCPServer.__init__ around line 120:
class PipelineMCPServer:
    def __init__(self):
        # ADD ENVIRONMENT DETECTION
        self.env_detector = EnvironmentDetector()
        self.is_docker = self.env_detector.is_running_in_docker()
        
        # CONFIGURE BASED ON ENVIRONMENT
        if self.is_docker:
            self.config = DockerConfig()
            self.workspace_root = Path("/app")
            self.session_dir = Path("/app/pipeline-sessions")
            self.database_path = Path("/app/data/sessions.db")
            print("🐳 Running in Docker environment")
            print(f"   📁 Workspace: {self.workspace_root}")
            print(f"   💾 Sessions: {self.session_dir}")
        else:
            # Use existing local configuration
            self.config = None
            self.workspace_root = Path.cwd()
            self.session_dir = self.workspace_root / "pipeline-sessions"
            self.database_path = self.workspace_root / "sessions.db"
            print("💻 Running in local environment")
            
        # Ensure directories exist
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        
        # ... rest of existing initialization ...
        
    def get_server_info(self) -> Dict[str, Any]:
        """Get server information including environment details"""
        base_info = {
            "server_version": "2.0.0-phase2",
            "environment": self.env_detector.get_environment_info(),
            "configuration": {
                "workspace_root": str(self.workspace_root),
                "session_dir": str(self.session_dir),
                "is_docker": self.is_docker
            }
        }
        
        if self.is_docker and self.config:
            base_info["docker_config"] = {
                "mcp_server_port": self.config.get("mcp_server.port"),
                "dashboard_enabled": self.config.get("monitoring.enable_dashboard"),
                "max_workers": self.config.get("mcp_server.max_workers")
            }
            
        return base_info
```

---

## 🔵 Phase 2.3: Advanced Monitoring & Intelligence (Week 5-6)

### ✅ TODO: ML-Powered Quality Prediction
**Priority:** LOW - Enhancement feature  
**Dependencies:** Phase 2.1 complete

| Subtask | Files | Action | ML Framework | Time Est. |
|---------|-------|--------|-------------|-----------|
| 2.3.1 | `src/intelligence/` | Create ML module | scikit-learn | 6 hours |
| 2.3.2 | Training data collection | Historical analysis | JSON logs | 3 hours |
| 2.3.3 | Integration with version_keeper | AI predictions | Lines 2490-2520 | 2 hours |
| 2.3.4 | Model validation | Accuracy testing | >80% accuracy target | 2 hours |

**Detailed Implementation:**

#### Subtask 2.3.1: Create ML Quality Prediction Module
```python
# File: src/intelligence/__init__.py (NEW)
"""AI/ML components for predictive quality analysis"""

# File: src/intelligence/quality_predictor.py (NEW)
import pickle
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from typing import List, Dict, Any, Tuple
from pathlib import Path
import ast
import os

class QualityPredictor:
    """ML-powered code quality prediction system"""
    
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.model_path = Path(__file__).parent / "models" / "quality_model.pkl"
        self.vectorizer_path = Path(__file__).parent / "models" / "vectorizer.pkl"
        self._load_or_train_model()
        
    def _load_or_train_model(self):
        """Load existing model or train new one"""
        if self.model_path.exists() and self.vectorizer_path.exists():
            self._load_model()
        else:
            self._train_initial_model()
            
    def _load_model(self):
        """Load pre-trained model and vectorizer"""
        with open(self.model_path, 'rb') as f:
            self.model = pickle.load(f)
        with open(self.vectorizer_path, 'rb') as f:
            self.vectorizer = pickle.load(f)
            
    def _train_initial_model(self):
        """Train initial model with synthetic data"""
        # Create training data based on common code patterns
        training_data = self._generate_training_data()
        
        # Extract features
        code_samples, labels = zip(*training_data)
        
        # Vectorize code samples
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words=None,
            ngram_range=(1, 2)
        )
        features = self.vectorizer.fit_transform(code_samples)
        
        # Train model
        self.model = RandomForestClassifier(
            n_estimators=100,
            random_state=42
        )
        self.model.fit(features, labels)
        
        # Save model
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.model_path, 'wb') as f:
            pickle.dump(self.model, f)
        with open(self.vectorizer_path, 'wb') as f:
            pickle.dump(self.vectorizer, f)
            
    def _generate_training_data(self) -> List[Tuple[str, int]]:
        """Generate synthetic training data for initial model"""
        # Code patterns that typically have issues
        problematic_patterns = [
            "import *",  # Wildcard imports
            "except:",   # Bare except clauses
            "eval(",     # Use of eval
            "exec(",     # Use of exec
            "global ",   # Global variables
            "# TODO",    # Unfinished code
            "# FIXME",   # Known issues
            "print(",    # Debug prints left in code
        ]
        
        # Good code patterns
        good_patterns = [
            "def test_",           # Test functions
            "\"\"\"",             # Docstrings
            "try:\n    ",         # Proper exception handling
            "if __name__ == '__main__':",  # Main guards
            "class ",             # Class definitions
            "return ",            # Functions that return values
        ]
        
        training_data = []
        
        # Add problematic patterns (label = 1 for issues)
        for pattern in problematic_patterns:
            training_data.append((f"def example():\n    {pattern}\n    pass", 1))
            
        # Add good patterns (label = 0 for no issues)  
        for pattern in good_patterns:
            training_data.append((f"def example():\n    {pattern}\n    pass", 0))
            
        return training_data
        
    def predict_quality_issues(self, workspace_files: Path) -> List[Dict[str, Any]]:
        """Predict quality issues in workspace files"""
        if not self.model or not self.vectorizer:
            return []
            
        predictions = []
        
        # Analyze Python files in workspace
        for py_file in workspace_files.rglob("*.py"):
            if py_file.is_file() and py_file.stat().st_size < 1024 * 1024:  # Skip huge files
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # Extract features and predict
                    features = self.vectorizer.transform([content])
                    probability = self.model.predict_proba(features)[0]
                    
                    # If high probability of issues (>0.6)
                    if probability[1] > 0.6:
                        predictions.append({
                            "file": str(py_file.relative_to(workspace_files)),
                            "predicted_issues": True,
                            "confidence": float(probability[1]),
                            "type": "ml_prediction"
                        })
                        
                except (UnicodeDecodeError, SyntaxError, OSError):
                    # Skip files with encoding or syntax issues
                    continue
                    
        return predictions
        
    def calculate_accuracy(self, predictions: List[Dict[str, Any]], 
                          actual_results: Dict[str, Any]) -> float:
        """Calculate prediction accuracy against actual results"""
        if not predictions:
            return 0.0
            
        # Extract files with actual issues
        actual_issue_files = set()
        if "details" in actual_results:
            for category, issues in actual_results["details"].items():
                if isinstance(issues, dict) and "issues" in issues:
                    for issue in issues["issues"]:
                        if "file" in issue:
                            actual_issue_files.add(issue["file"])
                            
        # Calculate accuracy
        correct_predictions = 0
        total_predictions = len(predictions)
        
        for pred in predictions:
            pred_file = pred["file"]
            if pred["predicted_issues"] and pred_file in actual_issue_files:
                correct_predictions += 1
            elif not pred["predicted_issues"] and pred_file not in actual_issue_files:
                correct_predictions += 1
                
        return (correct_predictions / total_predictions) * 100 if total_predictions > 0 else 0
```

#### Subtask 2.3.3: Integrate ML Predictions with Version Keeper
```python
# File: scripts/version_keeper.py
# ADD import after line 50:
try:
    from intelligence.quality_predictor import QualityPredictor
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("⚠️ ML quality prediction not available - install scikit-learn")

# MODIFY run_claude_integrated_linting method around line 2490:
def run_claude_integrated_linting(self, output_format="text", output_file=None, session_dir=None):
    """Enhanced with ML-powered quality prediction"""
    
    # ADD ML PREDICTION BEFORE STANDARD LINTING
    if ML_AVAILABLE:
        print("🧠 Running AI quality prediction...")
        quality_predictor = QualityPredictor()
        
        predicted_issues = quality_predictor.predict_quality_issues(
            workspace_files=self.repo_path
        )
        
        print(f"🔮 AI Prediction: {len(predicted_issues)} potential issues detected")
        
        # Display top predictions
        for pred in predicted_issues[:5]:  # Show top 5
            print(f"   📄 {pred['file']} (confidence: {pred['confidence']:.2f})")
    else:
        predicted_issues = []
    
    # ... existing linting code ...
    
    # MODIFY the lint report generation (around line 2510):
    lint_report = {
        # ... existing lint report fields ...
        
        # ADD AI PREDICTION DATA
        "ai_predictions": {
            "enabled": ML_AVAILABLE,
            "predictions": predicted_issues,
            "total_predicted": len(predicted_issues),
            "model_version": "1.0.0"
        }
    }
    
    # ADD ACCURACY CALCULATION (after lint results are available)
    if ML_AVAILABLE and predicted_issues:
        accuracy = quality_predictor.calculate_accuracy(predicted_issues, lint_report)
        lint_report["ai_predictions"]["accuracy"] = accuracy
        print(f"🎯 AI Prediction Accuracy: {accuracy:.1f}%")
    
    # ... rest of existing code ...
    
    return lint_report
```

---

## 📊 IMPLEMENTATION TIMELINE & VALIDATION

### Week-by-Week Implementation Schedule

| Week | Phase | Tasks | Validation Criteria | Success Metrics |
|------|-------|-------|-------------------|----------------|
| **Week 0** | Critical Fixes | 2.0.1-2.0.10 | All tests pass (100%) | 0 undefined functions |
| **Week 1** | Real-time Monitoring | 2.1.1-2.1.4 | WebSocket dashboard functional | <5s response time |
| **Week 2** | Parallel Processing | 2.1.5-2.1.8 | 3x performance improvement | Concurrent execution |
| **Week 3** | Session Management | 2.1.9-2.1.12 | Crash recovery works | 99% session reliability |
| **Week 4** | Docker Enhancement | 2.2.1-2.2.8 | Production deployment | Health checks pass |
| **Week 5** | ML Intelligence | 2.3.1-2.3.4 | >80% prediction accuracy | Smart quality gates |

### Validation Checkpoints

#### Phase 2.0 Validation (Week 0 End)
```bash
# Validation commands to run:
python3 tests/test_pipeline_integration.py
python3 scripts/version_keeper.py --comprehensive-lint --lint-only
python3 src/pipeline_mcp_server.py --validate

# Expected results:
# ✅ 5/5 tests passing (100%)
# ✅ 0 undefined functions
# ✅ No MCP import errors
# ✅ All duplicate files removed
```

#### Phase 2.1 Validation (Week 2 End)
```bash
# Start MCP server with monitoring
python3 src/pipeline_mcp_server.py

# In another terminal - test parallel processing
curl -X POST localhost:8080/tools/pipeline_run_full \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test", "max_cycles": 2}'

# Expected results:
# ✅ Real-time dashboard accessible at localhost:3000
# ✅ Parallel execution of version_keeper + quality_patcher
# ✅ Session persistence working (check database)
# ✅ WebSocket updates in dashboard
```

#### Phase 2.2 Validation (Week 4 End)
```bash
# Test Docker deployment
./deploy.sh

# Check all services healthy
docker-compose ps

# Expected results:
# ✅ All 6 services running (mcp-system, postgres, redis, dashboard, prometheus, grafana)
# ✅ Health checks passing
# ✅ Environment detection working
# ✅ Rollback mechanism tested
```

#### Final Phase 2 Validation (Week 6 End)
```bash
# Complete end-to-end test
python3 tests/phase2/test_full_pipeline_docker.py

# Performance benchmark
python3 tests/benchmarks/performance_test.py

# Expected results:
# ✅ Complete pipeline in Docker: <10 minutes
# ✅ ML predictions: >80% accuracy
# ✅ Zero downtime deployment
# ✅ All monitoring dashboards functional
```

---

## 🎯 SUCCESS CRITERIA & ROLLBACK PLAN

### Definition of Done for Phase 2

| Feature | Acceptance Criteria | Measurement |
|---------|-------------------|-------------|
| **Real-time Monitoring** | WebSocket dashboard shows live pipeline status | Response time <5s |
| **Parallel Processing** | 3x performance improvement over sequential | Benchmark comparison |
| **Session Persistence** | 99.9% recovery rate from crashes | Stress testing |
| **Docker Integration** | Zero-downtime deployment with rollback | Production testing |
| **ML Predictions** | >80% accuracy in quality issue prediction | Historical validation |
| **Environment Detection** | Automatic adaptation Docker vs local | Configuration tests |

### Rollback Strategy

#### Critical Issues Rollback (Any Phase)
```bash
# Emergency rollback to current stable state
git stash
git reset --hard HEAD~1
./deploy.sh --rollback

# Restore service
docker-compose down
docker-compose -f docker-compose.backup.yml up -d
```

#### Phase-by-Phase Rollback Points

| Phase | Rollback Trigger | Action | Recovery Time |
|-------|-----------------|--------|---------------|
| 2.0 | Test failure >50% | Revert MCP fixes | <1 hour |
| 2.1 | Performance degradation | Disable monitoring | <30 min |
| 2.2 | Docker deployment failure | Use local mode | <15 min |
| 2.3 | ML prediction errors | Disable ML features | <5 min |

---

## 📈 EXPECTED OUTCOMES

### Phase 2 Completion Benefits
1. **Performance**: 300% improvement in pipeline execution speed
2. **Reliability**: 99.9% uptime with automatic crash recovery
3. **Observability**: Real-time monitoring and predictive analytics
4. **Scalability**: Docker deployment ready for multi-instance production
5. **Intelligence**: AI-powered quality prediction reducing manual review time by 60%

### Technical Debt Reduction
- 1,209 undefined functions → 0
- MCP import errors → Custom error system
- Duplicate files → Clean architecture
- Manual deployment → Automated with rollback
- Reactive quality → Predictive quality

This comprehensive Phase 2 Implementation Plan provides a systematic approach to building upon the GitHub Agent's Docker foundation while implementing the advanced MCP server features envisioned in the original plan. Each TODO item is broken down with specific file locations, code changes, and validation criteria to ensure successful implementation.