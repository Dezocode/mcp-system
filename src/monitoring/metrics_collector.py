#!/usr/bin/env python3
"""
Metrics collection system for MCP pipeline
Provides comprehensive metrics gathering and aggregation
"""

import logging
import threading
import time
from collections import defaultdict, deque
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional

import psutil

logger = logging.getLogger(__name__)


@dataclass
class SystemMetrics:
    """System resource metrics snapshot"""

    timestamp: float
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_available_mb: float
    disk_io_read_mb: float
    disk_io_write_mb: float
    network_io_sent_mb: float
    network_io_recv_mb: float
    process_count: int
    load_average: tuple = None


@dataclass
class PipelineMetrics:
    """Pipeline-specific metrics"""

    timestamp: float
    session_id: str
    operations_completed: int
    operations_failed: int
    total_execution_time: float
    avg_response_time: float
    throughput_ops_per_second: float
    quality_score: float = 0.0
    issues_fixed: int = 0
    issues_remaining: int = 0


class MetricsCollector:
    """Comprehensive metrics collection system"""

    def __init__(self, collection_interval: float = 5.0):
        self.collection_interval = collection_interval
        self.is_collecting = False
        self.collection_thread: Optional[threading.Thread] = None

        # Metrics storage (limited to prevent memory growth)
        self.system_metrics: deque = deque(maxlen=1000)  # Last 1000 system snapshots
        self.pipeline_metrics: deque = deque(
            maxlen=1000
        )  # Last 1000 pipeline snapshots

        # Aggregated metrics
        self.hourly_aggregates: Dict[str, Dict] = defaultdict(dict)
        self.daily_aggregates: Dict[str, Dict] = defaultdict(dict)

        # Performance baselines
        self.baseline_metrics: Optional[Dict[str, float]] = None
        self.performance_thresholds = {
            "cpu_percent": 80.0,
            "memory_percent": 85.0,
            "avg_response_time": 30.0,
            "error_rate": 10.0,
        }

        # Historical tracking
        self.last_disk_io = None
        self.last_network_io = None

        logger.info("MetricsCollector initialized")

    def start_collection(self):
        """Start automatic metrics collection"""
        if self.is_collecting:
            logger.warning("Metrics collection already running")
            return

        self.is_collecting = True
        self.collection_thread = threading.Thread(
            target=self._collection_loop, daemon=True
        )
        self.collection_thread.start()
        logger.info(
            f"Started metrics collection (interval: {self.collection_interval}s)"
        )

    def stop_collection(self):
        """Stop automatic metrics collection"""
        self.is_collecting = False
        if self.collection_thread and self.collection_thread.is_alive():
            self.collection_thread.join(timeout=self.collection_interval + 1)
        logger.info("Stopped metrics collection")

    def _collection_loop(self):
        """Main collection loop running in separate thread"""
        while self.is_collecting:
            try:
                # Collect system metrics
                system_snapshot = self._collect_system_metrics()
                if system_snapshot:
                    self.system_metrics.append(system_snapshot)

                # Check performance thresholds
                self._check_performance_thresholds(system_snapshot)

                time.sleep(self.collection_interval)

            except Exception as e:
                logger.error(f"Error in metrics collection loop: {e}")
                time.sleep(self.collection_interval)

    def _collect_system_metrics(self) -> Optional[SystemMetrics]:
        """Collect current system metrics"""
        try:
            # CPU and Memory
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()

            # Disk I/O
            disk_io = psutil.disk_io_counters()
            if disk_io and self.last_disk_io:
                disk_read_mb = (disk_io.read_bytes - self.last_disk_io.read_bytes) / (
                    1024 * 1024
                )
                disk_write_mb = (
                    disk_io.write_bytes - self.last_disk_io.write_bytes
                ) / (1024 * 1024)
            else:
                disk_read_mb = disk_write_mb = 0.0
            self.last_disk_io = disk_io

            # Network I/O
            network_io = psutil.net_io_counters()
            if network_io and self.last_network_io:
                net_sent_mb = (
                    network_io.bytes_sent - self.last_network_io.bytes_sent
                ) / (1024 * 1024)
                net_recv_mb = (
                    network_io.bytes_recv - self.last_network_io.bytes_recv
                ) / (1024 * 1024)
            else:
                net_sent_mb = net_recv_mb = 0.0
            self.last_network_io = network_io

            # Process count
            process_count = len(psutil.pids())

            # Load average (Unix-like systems)
            load_avg = None
            try:
                load_avg = psutil.getloadavg()
            except AttributeError:
                # Windows doesn't have getloadavg
                pass

            return SystemMetrics(
                timestamp=time.time(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_used_mb=memory.used / (1024 * 1024),
                memory_available_mb=memory.available / (1024 * 1024),
                disk_io_read_mb=disk_read_mb,
                disk_io_write_mb=disk_write_mb,
                network_io_sent_mb=net_sent_mb,
                network_io_recv_mb=net_recv_mb,
                process_count=process_count,
                load_average=load_avg,
            )

        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
            return None

    def record_pipeline_metrics(self, session_id: str, metrics_data: Dict[str, Any]):
        """Record pipeline-specific metrics"""
        try:
            pipeline_snapshot = PipelineMetrics(
                timestamp=time.time(),
                session_id=session_id,
                operations_completed=metrics_data.get("operations_completed", 0),
                operations_failed=metrics_data.get("operations_failed", 0),
                total_execution_time=metrics_data.get("total_execution_time", 0.0),
                avg_response_time=metrics_data.get("avg_response_time", 0.0),
                throughput_ops_per_second=metrics_data.get(
                    "throughput_ops_per_second", 0.0
                ),
                quality_score=metrics_data.get("quality_score", 0.0),
                issues_fixed=metrics_data.get("issues_fixed", 0),
                issues_remaining=metrics_data.get("issues_remaining", 0),
            )

            self.pipeline_metrics.append(pipeline_snapshot)
            logger.debug(f"Recorded pipeline metrics for session {session_id}")

        except Exception as e:
            logger.error(f"Failed to record pipeline metrics: {e}")

    def _check_performance_thresholds(self, system_metrics: SystemMetrics):
        """Check if system metrics exceed performance thresholds"""
        if not system_metrics:
            return

        alerts = []

        # CPU threshold
        if system_metrics.cpu_percent > self.performance_thresholds["cpu_percent"]:
            alerts.append(
                {
                    "type": "cpu_high",
                    "message": f"CPU usage {system_metrics.cpu_percent:.1f}% exceeds threshold {self.performance_thresholds['cpu_percent']}%",
                    "severity": "warning",
                    "value": system_metrics.cpu_percent,
                }
            )

        # Memory threshold
        if (
            system_metrics.memory_percent
            > self.performance_thresholds["memory_percent"]
        ):
            alerts.append(
                {
                    "type": "memory_high",
                    "message": f"Memory usage {system_metrics.memory_percent:.1f}% exceeds threshold {self.performance_thresholds['memory_percent']}%",
                    "severity": "warning",
                    "value": system_metrics.memory_percent,
                }
            )

        # Log alerts
        for alert in alerts:
            logger.warning(f"Performance Alert: {alert['message']}")

    def get_current_system_summary(self) -> Dict[str, Any]:
        """Get current system metrics summary"""
        if not self.system_metrics:
            return {"status": "no_data", "message": "No system metrics available"}

        latest = self.system_metrics[-1]

        # Calculate trends from last 10 measurements
        recent_metrics = list(self.system_metrics)[-10:]
        cpu_trend = self._calculate_trend([m.cpu_percent for m in recent_metrics])
        memory_trend = self._calculate_trend([m.memory_percent for m in recent_metrics])

        return {
            "timestamp": latest.timestamp,
            "current": asdict(latest),
            "trends": {"cpu_trend": cpu_trend, "memory_trend": memory_trend},
            "thresholds": self.performance_thresholds,
            "status": "healthy" if self._is_system_healthy(latest) else "degraded",
        }

    def get_pipeline_summary(self, session_id: str = None) -> Dict[str, Any]:
        """Get pipeline metrics summary"""
        if not self.pipeline_metrics:
            return {"status": "no_data", "message": "No pipeline metrics available"}

        # Filter by session if specified
        relevant_metrics = self.pipeline_metrics
        if session_id:
            relevant_metrics = [
                m for m in self.pipeline_metrics if m.session_id == session_id
            ]

        if not relevant_metrics:
            return {
                "status": "no_data",
                "message": f"No metrics for session {session_id}",
            }

        latest = relevant_metrics[-1]

        # Calculate aggregates
        total_ops = sum(m.operations_completed for m in relevant_metrics)
        total_failures = sum(m.operations_failed for m in relevant_metrics)
        avg_quality = sum(m.quality_score for m in relevant_metrics) / len(
            relevant_metrics
        )

        return {
            "timestamp": latest.timestamp,
            "session_id": session_id or "all",
            "latest": asdict(latest),
            "aggregates": {
                "total_operations": total_ops,
                "total_failures": total_failures,
                "success_rate": (
                    ((total_ops - total_failures) / total_ops * 100)
                    if total_ops > 0
                    else 0
                ),
                "average_quality_score": avg_quality,
            },
            "metrics_count": len(relevant_metrics),
        }

    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from list of values"""
        if len(values) < 2:
            return "stable"

        recent_avg = sum(values[-3:]) / len(values[-3:])
        older_avg = (
            sum(values[:-3]) / len(values[:-3]) if len(values) > 3 else values[0]
        )

        diff_percent = (
            ((recent_avg - older_avg) / older_avg * 100) if older_avg > 0 else 0
        )

        if diff_percent > 5:
            return "increasing"
        elif diff_percent < -5:
            return "decreasing"
        else:
            return "stable"

    def _is_system_healthy(self, metrics: SystemMetrics) -> bool:
        """Determine if system is healthy based on current metrics"""
        return (
            metrics.cpu_percent < self.performance_thresholds["cpu_percent"]
            and metrics.memory_percent < self.performance_thresholds["memory_percent"]
        )

    def export_metrics(
        self, filepath: str, include_system: bool = True, include_pipeline: bool = True
    ):
        """Export all collected metrics to JSON file"""
        export_data = {
            "export_timestamp": time.time(),
            "collection_interval": self.collection_interval,
            "performance_thresholds": self.performance_thresholds,
        }

        if include_system and self.system_metrics:
            export_data["system_metrics"] = [asdict(m) for m in self.system_metrics]
            export_data["system_summary"] = self.get_current_system_summary()

        if include_pipeline and self.pipeline_metrics:
            export_data["pipeline_metrics"] = [asdict(m) for m in self.pipeline_metrics]
            export_data["pipeline_summary"] = self.get_pipeline_summary()

        import json

        with open(filepath, "w") as f:
            json.dump(export_data, f, indent=2, default=str)

        logger.info(f"Metrics exported to {filepath}")

    def set_baseline(self):
        """Set current system state as performance baseline"""
        if not self.system_metrics:
            logger.warning("No system metrics available to set baseline")
            return

        recent_metrics = list(self.system_metrics)[-10:]  # Last 10 measurements

        self.baseline_metrics = {
            "cpu_percent": sum(m.cpu_percent for m in recent_metrics)
            / len(recent_metrics),
            "memory_percent": sum(m.memory_percent for m in recent_metrics)
            / len(recent_metrics),
            "timestamp": time.time(),
        }

        logger.info(f"Performance baseline set: {self.baseline_metrics}")

    def get_performance_deviation(self) -> Dict[str, float]:
        """Get current performance deviation from baseline"""
        if not self.baseline_metrics or not self.system_metrics:
            return {}

        current = self.system_metrics[-1]

        return {
            "cpu_deviation": current.cpu_percent - self.baseline_metrics["cpu_percent"],
            "memory_deviation": current.memory_percent
            - self.baseline_metrics["memory_percent"],
            "baseline_age_hours": (time.time() - self.baseline_metrics["timestamp"])
            / 3600,
        }
