"""
Docker Health Check System
Provides comprehensive health checking for containerized MCP servers.
"""

import os
import time
import json
import logging
import tempfile
from typing import Dict, Any
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path


class HealthStatus(Enum):
    """Health check status values"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """Result of a health check"""
    status: HealthStatus
    message: str
    timestamp: float
    details: Dict[str, Any]
    duration_ms: float


class DockerHealthCheck:
    """Comprehensive health check system for Docker environments"""
    def __init__(self, config_manager=None):
        self.logger = logging.getLogger(__name__)
        self.config_manager = config_manager
        self.last_check_time = 0
        self.check_interval = 30.0  # Default 30 seconds

    def perform_comprehensive_health_check(self) -> HealthCheckResult:
        """Perform comprehensive health check"""
        start_time = time.time()

        try:
            # Collect all health metrics
            checks = {
                "filesystem": self._check_filesystem_health(),
                "memory": self._check_memory_health(),
                "network": self._check_network_health(),
                "mcp_server": self._check_mcp_server_health(),
                "configuration": self._check_configuration_health()
            }

            # Determine overall status
            overall_status = self._determine_overall_status(checks)

            duration_ms = (time.time() - start_time) * 1000

            result = HealthCheckResult(
                status=overall_status,
                message=self._generate_status_message(checks, overall_status),
                timestamp=time.time(),
                details=checks,
                duration_ms=duration_ms
            )

            self.last_check_time = time.time()
            return result

        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return HealthCheckResult(
                status=HealthStatus.UNHEALTHY,
                message=f"Health check error: {str(e)}",
                timestamp=time.time(),
                details={"error": str(e)},
                duration_ms=duration_ms
            )

    def _check_filesystem_health(self) -> Dict[str, Any]:
        """Check filesystem health"""
        try:
            import shutil

            # Check key directories
            directories_to_check = [
                "/app",
                tempfile.gettempdir(),
                ("/app/pipeline-sessions"
                 if Path("/app/pipeline-sessions").exists() else None)
            ]

            filesystem_status = {
                "status": "healthy",
                "directories": {},
                "disk_usage": {}
            }

            for directory in directories_to_check:
                if directory is None:
                    continue

                try:
                    # Check if directory exists and is writable
                    dir_path = Path(directory)
                    exists = dir_path.exists()
                    writable = (dir_path.is_dir() and
                                os.access(directory, os.W_OK) if exists else False)

                    # Get disk usage
                    if exists:
                        usage = shutil.disk_usage(directory)
                        disk_info = {
                            "total_gb": round(usage.total / (1024**3), 2),
                            "free_gb": round(usage.free / (1024**3), 2),
                            "used_percent": round((usage.used / usage.total) * 100, 2)
                        }
                        filesystem_status["disk_usage"][directory] = disk_info

                        # Check if disk usage is critical
                        if disk_info["used_percent"] > 90:
                            filesystem_status["status"] = "degraded"
                        elif disk_info["used_percent"] > 95:
                            filesystem_status["status"] = "unhealthy"
                    else:
                        disk_info = {"error": "Directory not found"}

                    filesystem_status["directories"][directory] = {
                        "exists": exists,
                        "writable": writable,
                        "disk_usage": disk_info
                    }

                except Exception as e:
                    filesystem_status["directories"][directory] = {
                        "error": str(e)
                    }
                    if filesystem_status["status"] == "healthy":
                        filesystem_status["status"] = "degraded"

            return filesystem_status

        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }

    def _check_memory_health(self) -> Dict[str, Any]:
        """Check memory health"""
        try:
            memory_status = {
                "status": "healthy",
                "memory_info": {}
            }

            # Try to get memory information (Linux)
            if Path("/proc/meminfo").exists():
                with open("/proc/meminfo", "r") as f:
                    meminfo = f.read()

                for line in meminfo.split('\n'):
                    if line.startswith('MemTotal:'):
                        total_kb = int(line.split()[1])
                        memory_status["memory_info"]["total_mb"] = total_kb / 1024
                    elif line.startswith('MemAvailable:'):
                        available_kb = int(line.split()[1])
                        memory_status["memory_info"]["available_mb"] = (
                            available_kb / 1024
                        )

                        # Calculate memory usage percentage
                        if "total_mb" in memory_status["memory_info"]:
                            used_mb = (
                                memory_status["memory_info"]["total_mb"] -
                                (available_kb / 1024)
                            )
                            usage_percent = (
                                (used_mb /
                                 memory_status["memory_info"]["total_mb"]) * 100
                            )
                            memory_status["memory_info"]["used_percent"] = (
                                round(usage_percent, 2)
                            )

                            # Set status based on usage
                            if usage_percent > 85:
                                memory_status["status"] = "degraded"
                            elif usage_percent > 95:
                                memory_status["status"] = "unhealthy"

            # Check for container memory limits
            if Path("/.dockerenv").exists():
                try:
                    # Try cgroup v1
                    with open('/sys/fs/cgroup/memory/memory.limit_in_bytes', 'r') as f:
                        limit_bytes = int(f.read().strip())
                        if limit_bytes < 9223372036854771712:  # Not unlimited
                            memory_status["memory_info"]["container_limit_mb"] = (
                                limit_bytes / (1024 * 1024)
                            )

                    with open('/sys/fs/cgroup/memory/memory.usage_in_bytes', 'r') as f:
                        usage_bytes = int(f.read().strip())
                        memory_status["memory_info"]["container_usage_mb"] = (
                            usage_bytes / (1024 * 1024)
                        )

                        if "container_limit_mb" in memory_status["memory_info"]:
                            container_usage_percent = (usage_bytes / limit_bytes) * 100
                            memory_status["memory_info"]["container_usage_percent"] = (
                                round(container_usage_percent, 2)
                            )

                except (FileNotFoundError, ValueError):
                    # Try cgroup v2
                    try:
                        with open('/sys/fs/cgroup/memory.max', 'r') as f:
                            content = f.read().strip()
                            if content != "max":
                                limit_bytes = int(content)
                                memory_status["memory_info"]["container_limit_mb"] = (
                                    limit_bytes / (1024 * 1024)
                                )

                        with open('/sys/fs/cgroup/memory.current', 'r') as f:
                            usage_bytes = int(f.read().strip())
                            memory_status["memory_info"]["container_usage_mb"] = (
                                usage_bytes / (1024 * 1024)
                            )

                    except (FileNotFoundError, ValueError):
                        pass

            return memory_status

        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }

    def _check_network_health(self) -> Dict[str, Any]:
        """Check network connectivity"""
        try:
            import socket

            network_status = {
                "status": "healthy",
                "connectivity": {}
            }

            # Check basic network configuration
            try:
                hostname = socket.gethostname()
                ip_address = socket.gethostbyname(hostname)
                network_status["connectivity"]["hostname"] = hostname
                network_status["connectivity"]["ip_address"] = ip_address
            except Exception as e:
                network_status["connectivity"]["error"] = str(e)
                network_status["status"] = "degraded"

            # Check if running in Docker and can resolve external DNS
            if Path("/.dockerenv").exists():
                try:
                    # Try to resolve a reliable DNS name
                    socket.gethostbyname("google.com")
                    network_status["connectivity"]["external_dns"] = "working"
                except Exception:
                    network_status["connectivity"]["external_dns"] = "failed"
                    network_status["status"] = "degraded"

            return network_status

        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }

    def _check_mcp_server_health(self) -> Dict[str, Any]:
        """Check MCP server specific health"""
        try:
            mcp_status = {
                "status": "healthy",
                "server_info": {}
            }

            # Check if we can access the pipeline server
            try:
                from src.pipeline_mcp_server import pipeline_server

                # Check if server is initialized
                if hasattr(pipeline_server, 'server'):
                    mcp_status["server_info"]["initialized"] = True
                    mcp_status["server_info"]["session_count"] = (
                        len(pipeline_server.sessions)
                    )

                    # Check if environment detection is working
                    if hasattr(pipeline_server, 'environment_info'):
                        env_info = pipeline_server.environment_info
                        mcp_status["server_info"]["environment"] = {
                            "platform": env_info.platform,
                            "is_docker": env_info.is_docker,
                            "python_version": env_info.python_version
                        }

                    # Check if profiling is active
                    if hasattr(pipeline_server, 'runtime_profiler'):
                        mcp_status["server_info"]["profiling_active"] = (
                            pipeline_server.runtime_profiler.is_profiling
                        )

                else:
                    mcp_status["server_info"]["initialized"] = False
                    mcp_status["status"] = "degraded"

            except ImportError:
                mcp_status["server_info"]["import_error"] = (
                    "Cannot import pipeline_server"
                )
                mcp_status["status"] = "degraded"
            except Exception as e:
                mcp_status["server_info"]["error"] = str(e)
                mcp_status["status"] = "degraded"

            return mcp_status

        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }

    def _check_configuration_health(self) -> Dict[str, Any]:
        """Check configuration health"""
        try:
            config_status = {
                "status": "healthy",
                "config_info": {}
            }

            if self.config_manager:
                try:
                    # Validate configuration
                    validation = self.config_manager.validate_configuration()
                    config_status["config_info"]["validation"] = validation

                    if not validation["valid"]:
                        config_status["status"] = "degraded"

                    # Get config summary
                    summary = self.config_manager.get_config_summary()
                    config_status["config_info"]["summary"] = {
                        "environment": summary["environment"]["platform"],
                        "is_docker": summary["environment"]["is_docker"],
                        "max_workers": summary["max_workers"],
                        "log_level": summary["log_level"]
                    }

                except Exception as e:
                    config_status["config_info"]["error"] = str(e)
                    config_status["status"] = "degraded"
            else:
                config_status["config_info"]["note"] = "No config manager available"

            return config_status

        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }

    def _determine_overall_status(
        self, checks: Dict[str, Dict[str, Any]]
    ) -> HealthStatus:
        """Determine overall health status from individual checks"""
        statuses = []

        for check_name, check_result in checks.items():
            status_str = check_result.get("status", "unknown")
            if status_str == "healthy":
                statuses.append(HealthStatus.HEALTHY)
            elif status_str == "degraded":
                statuses.append(HealthStatus.DEGRADED)
            elif status_str == "unhealthy":
                statuses.append(HealthStatus.UNHEALTHY)
            else:
                statuses.append(HealthStatus.UNKNOWN)

        # If any check is unhealthy, overall is unhealthy
        if HealthStatus.UNHEALTHY in statuses:
            return HealthStatus.UNHEALTHY

        # If any check is degraded, overall is degraded
        if HealthStatus.DEGRADED in statuses:
            return HealthStatus.DEGRADED

        # If all checks are healthy, overall is healthy
        if all(status == HealthStatus.HEALTHY for status in statuses):
            return HealthStatus.HEALTHY

        # Otherwise unknown
        return HealthStatus.UNKNOWN

    def _generate_status_message(
        self, checks: Dict[str, Dict[str, Any]], overall_status: HealthStatus
    ) -> str:
        """Generate human-readable status message"""
        if overall_status == HealthStatus.HEALTHY:
            return "All systems operational"
        elif overall_status == HealthStatus.DEGRADED:
            issues = []
            for check_name, check_result in checks.items():
                if check_result.get("status") in ["degraded", "unhealthy"]:
                    issues.append(check_name)
            return f"System degraded - issues with: {', '.join(issues)}"
        elif overall_status == HealthStatus.UNHEALTHY:
            issues = []
            for check_name, check_result in checks.items():
                if check_result.get("status") == "unhealthy":
                    issues.append(check_name)
            return f"System unhealthy - critical issues with: {', '.join(issues)}"
        else:
            return "System status unknown"

    def get_health_check_endpoint_response(self) -> Dict[str, Any]:
        """Get health check response suitable for container orchestrators"""
        result = self.perform_comprehensive_health_check()

        # Format for container health check
        response = {
            "status": result.status.value,
            "timestamp": result.timestamp,
            "message": result.message,
            "duration_ms": result.duration_ms
        }

        # Add summary of issues for degraded/unhealthy status
        if result.status != HealthStatus.HEALTHY:
            issues = []
            for check_name, check_result in result.details.items():
                if check_result.get("status") in ["degraded", "unhealthy"]:
                    issues.append({
                        "component": check_name,
                        "status": check_result.get("status"),
                        "error": check_result.get("error")
                    })
            response["issues"] = issues

        return response

    def export_health_report(self, output_path: str):
        """Export detailed health report to file"""
        result = self.perform_comprehensive_health_check()

        with open(output_path, 'w') as f:
            json.dump(asdict(result), f, indent=2, default=str)

        self.logger.info(f"Health report exported to {output_path}")


# Global health check instance
docker_health_check = DockerHealthCheck()
