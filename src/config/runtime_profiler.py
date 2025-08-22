"""
Runtime Profiler for MCP System
Provides runtime performance profiling and resource monitoring.
"""

import time
import threading
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
import logging
from collections import deque
import json
import os


@dataclass
class PerformanceSnapshot:
    """Snapshot of runtime performance metrics"""
    timestamp: float
    cpu_percent: float
    memory_mb: float
    memory_percent: float
    thread_count: int


@dataclass
class PerformanceProfile:
    """Aggregated performance profile"""
    start_time: float
    duration: float
    avg_cpu_percent: float
    max_cpu_percent: float
    avg_memory_mb: float
    max_memory_mb: float
    peak_thread_count: int
    snapshots: List[PerformanceSnapshot]


class RuntimeProfiler:
    """Profiles runtime performance and resource usage"""

    def __init__(self, sampling_interval: float = 1.0):
        self.sampling_interval = sampling_interval
        self.logger = logging.getLogger(__name__)
        self.is_profiling = False
        self.profiling_thread: Optional[threading.Thread] = None
        self.snapshots: deque = deque(maxlen=3600)  # Keep last hour of snapshots
        self.start_time: Optional[float] = None

    def start_profiling(self):
        """Start runtime profiling in background thread"""
        if self.is_profiling:
            self.logger.warning("Profiling already started")
            return

        self.is_profiling = True
        self.start_time = time.time()
        self.snapshots.clear()

        self.profiling_thread = threading.Thread(
            target=self._profiling_loop, daemon=True
        )
        self.profiling_thread.start()

        self.logger.info("Runtime profiling started")

    def stop_profiling(self) -> PerformanceProfile:
        """Stop profiling and return performance profile"""
        if not self.is_profiling:
            self.logger.warning("Profiling not started")
            return self.get_current_profile()

        self.is_profiling = False
        if self.profiling_thread:
            self.profiling_thread.join(timeout=5.0)

        profile = self.get_current_profile()
        self.logger.info("Runtime profiling stopped")

        return profile

    def _profiling_loop(self):
        """Background profiling loop"""
        while self.is_profiling:
            try:
                snapshot = self._collect_snapshot()
                if snapshot:
                    self.snapshots.append(snapshot)

                time.sleep(self.sampling_interval)
            except Exception as e:
                self.logger.error(f"Error in profiling loop: {e}")
                time.sleep(self.sampling_interval)

    def _collect_snapshot(self) -> Optional[PerformanceSnapshot]:
        """Collect performance snapshot"""
        try:
            timestamp = time.time()

            # Get basic metrics without external dependencies
            # This is a simplified version that doesn't require psutil

            # CPU usage - simplified estimation based on load average (Linux)
            cpu_percent = 0.0
            if os.name == 'posix':
                try:
                    load_avg = os.getloadavg()[0]  # 1-minute load average
                    cpu_count = os.cpu_count() or 1
                    cpu_percent = min(100.0, (load_avg / cpu_count) * 100)
                except (OSError, AttributeError):
                    pass

            # Memory usage - simplified estimation
            memory_mb = 0.0
            memory_percent = 0.0
            if os.name == 'posix':
                try:
                    # Very basic memory estimation from /proc/self/status
                    with open('/proc/self/status', 'r') as f:
                        for line in f:
                            if line.startswith('VmRSS:'):
                                # RSS memory in kB
                                memory_kb = int(line.split()[1])
                                memory_mb = memory_kb / 1024
                                break

                    # Get system memory from /proc/meminfo for percentage
                    with open('/proc/meminfo', 'r') as f:
                        for line in f:
                            if line.startswith('MemTotal:'):
                                total_kb = int(line.split()[1])
                                if memory_kb > 0:
                                    memory_percent = (memory_kb / total_kb) * 100
                                break
                except (FileNotFoundError, PermissionError, ValueError):
                    pass

            # Thread count
            thread_count = threading.active_count()

            return PerformanceSnapshot(
                timestamp=timestamp,
                cpu_percent=cpu_percent,
                memory_mb=memory_mb,
                memory_percent=memory_percent,
                thread_count=thread_count
            )

        except Exception as e:
            self.logger.error(f"Failed to collect performance snapshot: {e}")
            return None

    def get_current_profile(self) -> PerformanceProfile:
        """Get current performance profile"""
        if not self.start_time:
            return PerformanceProfile(
                start_time=time.time(),
                duration=0.0,
                avg_cpu_percent=0.0,
                max_cpu_percent=0.0,
                avg_memory_mb=0.0,
                max_memory_mb=0.0,
                peak_thread_count=0,
                snapshots=list(self.snapshots)
            )

        duration = time.time() - self.start_time

        if not self.snapshots:
            return PerformanceProfile(
                start_time=self.start_time,
                duration=duration,
                avg_cpu_percent=0.0,
                max_cpu_percent=0.0,
                avg_memory_mb=0.0,
                max_memory_mb=0.0,
                peak_thread_count=0,
                snapshots=[]
            )

        # Calculate aggregates
        cpu_values = [s.cpu_percent for s in self.snapshots]
        memory_values = [s.memory_mb for s in self.snapshots]
        thread_values = [s.thread_count for s in self.snapshots]

        avg_cpu = sum(cpu_values) / len(cpu_values) if cpu_values else 0.0
        max_cpu = max(cpu_values) if cpu_values else 0.0
        avg_memory = sum(memory_values) / len(memory_values) if memory_values else 0.0
        max_memory = max(memory_values) if memory_values else 0.0
        peak_threads = max(thread_values) if thread_values else 0

        return PerformanceProfile(
            start_time=self.start_time,
            duration=duration,
            avg_cpu_percent=avg_cpu,
            max_cpu_percent=max_cpu,
            avg_memory_mb=avg_memory,
            max_memory_mb=max_memory,
            peak_thread_count=peak_threads,
            snapshots=list(self.snapshots)
        )

    def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get current real-time metrics"""
        try:
            snapshot = self._collect_snapshot()
            if snapshot:
                return {
                    "cpu_percent": snapshot.cpu_percent,
                    "memory_mb": snapshot.memory_mb,
                    "memory_percent": snapshot.memory_percent,
                    "thread_count": snapshot.thread_count,
                    "timestamp": snapshot.timestamp
                }
        except Exception as e:
            self.logger.error(f"Failed to get real-time metrics: {e}")

        return {
            "cpu_percent": 0.0,
            "memory_mb": 0.0,
            "memory_percent": 0.0,
            "thread_count": 0,
            "timestamp": time.time(),
            "error": "Failed to collect metrics"
        }

    def export_profile(self, output_path: str, format: str = "json"):
        """Export performance profile to file"""
        profile = self.get_current_profile()

        if format.lower() == "json":
            with open(output_path, 'w') as f:
                json.dump(asdict(profile), f, indent=2, default=str)
        else:
            raise ValueError(f"Unsupported format: {format}")

        self.logger.info(f"Performance profile exported to {output_path}")

    def get_resource_usage_summary(self) -> Dict[str, Any]:
        """Get summary of resource usage"""
        profile = self.get_current_profile()

        return {
            "duration_seconds": round(profile.duration, 2),
            "average_cpu_percent": round(profile.avg_cpu_percent, 2),
            "peak_cpu_percent": round(profile.max_cpu_percent, 2),
            "average_memory_mb": round(profile.avg_memory_mb, 2),
            "peak_memory_mb": round(profile.max_memory_mb, 2),
            "peak_thread_count": profile.peak_thread_count,
            "snapshot_count": len(profile.snapshots)
        }

    def check_resource_limits(self, config_manager) -> Dict[str, Any]:
        """Check if current resource usage exceeds configured limits"""
        violations = {
            "exceeded": False,
            "violations": [],
            "warnings": []
        }

        try:
            # Get current metrics
            current_metrics = self.get_real_time_metrics()
            if "error" in current_metrics:
                return violations

            # Get configured limits
            memory_limit_mb = config_manager.get_performance_setting("memory_limit_mb")
            cpu_limit_cores = config_manager.get_performance_setting("cpu_limit_cores")

            # Check memory limit
            if memory_limit_mb and current_metrics["memory_mb"] > memory_limit_mb:
                violations["exceeded"] = True
                violations["violations"].append({
                    "type": "memory",
                    "current": current_metrics["memory_mb"],
                    "limit": memory_limit_mb,
                    "unit": "MB"
                })

            # Check CPU limit (approximate)
            if (cpu_limit_cores and
                    current_metrics["cpu_percent"] > (cpu_limit_cores * 100)):
                violations["exceeded"] = True
                violations["violations"].append({
                    "type": "cpu",
                    "current": current_metrics["cpu_percent"],
                    "limit": cpu_limit_cores * 100,
                    "unit": "%"
                })

            # Issue warnings for approaching limits
            warning_threshold = 0.8  # 80% of limit

            if (memory_limit_mb and
                    current_metrics["memory_mb"] >
                    (memory_limit_mb * warning_threshold)):
                violations["warnings"].append({
                    "type": "memory",
                    "current": current_metrics["memory_mb"],
                    "threshold": memory_limit_mb * warning_threshold,
                    "limit": memory_limit_mb,
                    "unit": "MB"
                })

        except Exception as e:
            self.logger.error(f"Failed to check resource limits: {e}")

        return violations

    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health metrics"""
        try:
            # Basic system health from what we can easily get
            health = {
                "timestamp": time.time()
            }

            # Load average (Linux/Unix)
            if os.name == 'posix':
                try:
                    load_avg = os.getloadavg()
                    health["load_average_1m"] = load_avg[0]
                    health["load_average_5m"] = load_avg[1]
                    health["load_average_15m"] = load_avg[2]

                    cpu_count = os.cpu_count() or 1
                    health["cpu_count"] = cpu_count
                    health["load_percent_1m"] = (load_avg[0] / cpu_count) * 100
                except (OSError, AttributeError):
                    pass

            # Basic memory info (Linux)
            if os.path.exists('/proc/meminfo'):
                try:
                    with open('/proc/meminfo', 'r') as f:
                        meminfo = f.read()
                        for line in meminfo.split('\n'):
                            if line.startswith('MemTotal:'):
                                total_kb = int(line.split()[1])
                                health["system_memory_total_mb"] = total_kb / 1024
                            elif line.startswith('MemAvailable:'):
                                available_kb = int(line.split()[1])
                                health["system_memory_available_mb"] = (
                                    available_kb / 1024
                                )
                                if 'system_memory_total_mb' in health:
                                    used_mb = (
                                        health["system_memory_total_mb"] -
                                        (available_kb / 1024)
                                    )
                                    health["system_memory_used_percent"] = (
                                        (used_mb /
                                         health["system_memory_total_mb"]) * 100
                                    )
                except (FileNotFoundError, ValueError):
                    pass

            return health

        except Exception as e:
            self.logger.error(f"Failed to get system health metrics: {e}")
            return {
                "error": str(e),
                "timestamp": time.time()
            }


# Global runtime profiler instance
runtime_profiler = RuntimeProfiler()
