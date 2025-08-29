#!/usr/bin/env python3
"""
Real-time monitoring system for MCP pipeline
Provides live performance metrics and health status tracking
"""

import json
import logging
import threading
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class MetricPoint:
    """Individual metric measurement point"""

    timestamp: float
    value: Any
    tags: Dict[str, str] = None


@dataclass
class MonitoringEvent:
    """Monitoring event for tracking operations"""

    event_id: str
    event_type: str
    started_at: float
    ended_at: Optional[float] = None
    metadata: Dict[str, Any] = None
    status: str = "running"


class RealtimeMonitor:
    """Real-time monitoring system with performance tracking"""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.metrics: Dict[str, List[MetricPoint]] = {}
        self.events: Dict[str, MonitoringEvent] = {}
        self.alerts: List[Dict[str, Any]] = []
        self.performance_baseline: Optional[Dict[str, float]] = None
        self._lock = threading.RLock()

        # Performance tracking
        self.start_time = time.time()
        self.operation_counts = {}
        self.error_counts = {}
        self.response_times = {}

        logger.info(f"RealtimeMonitor initialized for session {session_id}")

    def start_monitoring(
        self, event_id: str, event_type: str, metadata: Dict[str, Any] = None
    ) -> str:
        """Start monitoring an operation"""
        with self._lock:
            event = MonitoringEvent(
                event_id=event_id,
                event_type=event_type,
                started_at=time.time(),
                metadata=metadata or {},
            )
            self.events[event_id] = event

            # Update operation counts
            self.operation_counts[event_type] = (
                self.operation_counts.get(event_type, 0) + 1
            )

            logger.debug(f"Started monitoring {event_type} with ID {event_id}")
            return event_id

    def stop_monitoring(self, event_id: str, status_data: Dict[str, Any] = None):
        """Stop monitoring an operation"""
        with self._lock:
            if event_id not in self.events:
                logger.warning(f"Event {event_id} not found for stopping")
                return

            event = self.events[event_id]
            event.ended_at = time.time()
            event.status = (
                status_data.get("status", "completed") if status_data else "completed"
            )

            if status_data:
                event.metadata.update(status_data)

            # Calculate and record response time
            response_time = event.ended_at - event.started_at
            event_type = event.event_type

            if event_type not in self.response_times:
                self.response_times[event_type] = []
            self.response_times[event_type].append(response_time)

            # Track errors
            if event.status == "error" or event.status == "failed":
                self.error_counts[event_type] = self.error_counts.get(event_type, 0) + 1

            logger.debug(
                f"Stopped monitoring {event_type} ({event_id}) - {response_time:.2f}s"
            )

    def record_metric(self, metric_name: str, value: Any, tags: Dict[str, str] = None):
        """Record a metric point"""
        with self._lock:
            if metric_name not in self.metrics:
                self.metrics[metric_name] = []

            metric_point = MetricPoint(timestamp=time.time(), value=value, tags=tags)

            self.metrics[metric_name].append(metric_point)

            # Keep only last 1000 points per metric to prevent memory growth
            if len(self.metrics[metric_name]) > 1000:
                self.metrics[metric_name] = self.metrics[metric_name][-1000:]

    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current monitoring metrics"""
        with self._lock:
            current_time = time.time()
            uptime = current_time - self.start_time

            # Calculate average response times
            avg_response_times = {}
            for event_type, times in self.response_times.items():
                if times:
                    avg_response_times[event_type] = sum(times) / len(times)

            # Calculate error rates
            error_rates = {}
            for event_type in self.operation_counts:
                total_ops = self.operation_counts[event_type]
                errors = self.error_counts.get(event_type, 0)
                error_rates[event_type] = (
                    (errors / total_ops) * 100 if total_ops > 0 else 0
                )

            # Active events
            active_events = [
                asdict(event)
                for event in self.events.values()
                if event.ended_at is None
            ]

            return {
                "session_id": self.session_id,
                "uptime_seconds": uptime,
                "timestamp": current_time,
                "operation_counts": self.operation_counts.copy(),
                "error_counts": self.error_counts.copy(),
                "average_response_times": avg_response_times,
                "error_rates": error_rates,
                "active_events": active_events,
                "total_events": len(self.events),
                "alerts": self.alerts[-10:],  # Last 10 alerts
                "metrics_count": {
                    name: len(points) for name, points in self.metrics.items()
                },
            }

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary statistics"""
        with self._lock:
            summary = {
                "session_id": self.session_id,
                "monitoring_duration": time.time() - self.start_time,
                "total_operations": sum(self.operation_counts.values()),
                "total_errors": sum(self.error_counts.values()),
                "operations_by_type": self.operation_counts.copy(),
                "errors_by_type": self.error_counts.copy(),
            }

            # Performance percentiles for each operation type
            percentiles = {}
            for event_type, times in self.response_times.items():
                if times:
                    sorted_times = sorted(times)
                    n = len(sorted_times)
                    percentiles[event_type] = {
                        "p50": sorted_times[int(n * 0.5)] if n > 0 else 0,
                        "p90": sorted_times[int(n * 0.9)] if n > 0 else 0,
                        "p95": sorted_times[int(n * 0.95)] if n > 0 else 0,
                        "p99": sorted_times[int(n * 0.99)] if n > 0 else 0,
                        "min": min(sorted_times),
                        "max": max(sorted_times),
                        "avg": sum(sorted_times) / n,
                    }

            summary["response_time_percentiles"] = percentiles
            return summary

    def add_alert(
        self,
        alert_type: str,
        message: str,
        severity: str = "info",
        metadata: Dict[str, Any] = None,
    ):
        """Add an alert to the monitoring system"""
        with self._lock:
            alert = {
                "timestamp": time.time(),
                "alert_type": alert_type,
                "message": message,
                "severity": severity,
                "session_id": self.session_id,
                "metadata": metadata or {},
            }

            self.alerts.append(alert)

            # Keep only last 100 alerts
            if len(self.alerts) > 100:
                self.alerts = self.alerts[-100:]

            logger.info(f"Alert [{severity}] {alert_type}: {message}")

    def check_performance_thresholds(self):
        """Check if performance metrics exceed thresholds and generate alerts"""
        with self._lock:
            for event_type, times in self.response_times.items():
                if not times:
                    continue

                avg_time = sum(times[-10:]) / min(len(times), 10)  # Last 10 operations

                # Alert if average response time > 30 seconds
                if avg_time > 30:
                    self.add_alert(
                        "performance_degradation",
                        f"{event_type} operations averaging {avg_time:.2f}s (threshold: 30s)",
                        "warning",
                        {"event_type": event_type, "avg_response_time": avg_time},
                    )

                # Alert if error rate > 10%
                total_ops = self.operation_counts.get(event_type, 0)
                errors = self.error_counts.get(event_type, 0)
                if total_ops > 0:
                    error_rate = (errors / total_ops) * 100
                    if error_rate > 10:
                        self.add_alert(
                            "high_error_rate",
                            f"{event_type} error rate: {error_rate:.1f}% (threshold: 10%)",
                            "error",
                            {"event_type": event_type, "error_rate": error_rate},
                        )

    def export_metrics(self, filepath: str):
        """Export all metrics to JSON file"""
        with self._lock:
            export_data = {
                "session_id": self.session_id,
                "export_timestamp": time.time(),
                "monitoring_period": {
                    "start": self.start_time,
                    "end": time.time(),
                    "duration": time.time() - self.start_time,
                },
                "metrics": {
                    name: [asdict(point) for point in points]
                    for name, points in self.metrics.items()
                },
                "events": {
                    event_id: asdict(event) for event_id, event in self.events.items()
                },
                "performance_summary": self.get_performance_summary(),
                "alerts": self.alerts,
            }

            with open(filepath, "w") as f:
                json.dump(export_data, f, indent=2, default=str)

            logger.info(f"Metrics exported to {filepath}")
