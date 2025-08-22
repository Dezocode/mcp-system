"""
Environment Detector for MCP System
Detects runtime environment (Docker vs local) and provides environment information.
"""

import json
import logging
import os
import platform
import shutil
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass
class EnvironmentInfo:
    """Comprehensive environment information"""

    platform: str
    architecture: str
    is_docker: bool
    is_containerized: bool
    container_type: Optional[str]
    python_version: str
    working_directory: str
    home_directory: str
    user: str
    hostname: str
    environment_variables: Dict[str, str]
    file_system_info: Dict[str, Any]


class EnvironmentDetector:
    """Detects runtime environment and provides environment information"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.platform_info = platform.uname()

    def is_running_in_docker(self) -> bool:
        """Detect if running inside Docker container"""
        # Method 1: Check for .dockerenv file
        if Path("/.dockerenv").exists():
            self.logger.debug("Detected Docker via /.dockerenv file")
            return True

        # Method 2: Check cgroup info (Linux only)
        if self.platform_info.system.lower() == "linux":
            try:
                with open("/proc/self/cgroup", "r") as f:
                    content = f.read().lower()
                    if "docker" in content or "containerd" in content:
                        self.logger.debug("Detected Docker via cgroup")
                        return True
            except (FileNotFoundError, PermissionError, OSError):
                pass

        # Method 3: Check environment variables
        docker_env_vars = [
            "DOCKER_CONTAINER",
            "container",  # Used by some container runtimes
        ]

        for env_var in docker_env_vars:
            if os.getenv(env_var):
                self.logger.debug(
                    f"Detected container via environment variable: {env_var}"
                )
                return True

        self.logger.debug("Not running in Docker/container")
        return False

    def get_container_type(self) -> Optional[str]:
        """Detect specific container technology"""
        if not self.is_running_in_docker():
            return None

        # Check for specific container technologies
        try:
            # Check cgroup for container type
            with open("/proc/self/cgroup", "r") as f:
                content = f.read().lower()

                if "docker" in content:
                    return "docker"
                elif "containerd" in content:
                    return "containerd"
                elif "podman" in content:
                    return "podman"
                elif "lxc" in content:
                    return "lxc"

        except (FileNotFoundError, PermissionError, OSError):
            pass

        # Check environment variables
        container_env = os.getenv("container")
        if container_env:
            return container_env

        return "unknown-container"

    def is_running_in_kubernetes(self) -> bool:
        """Detect if running in Kubernetes"""
        # Check for Kubernetes-specific environment variables
        k8s_env_vars = [
            "KUBERNETES_SERVICE_HOST",
            "KUBERNETES_SERVICE_PORT",
            "KUBECONFIG",
        ]

        for env_var in k8s_env_vars:
            if os.getenv(env_var):
                return True

        # Check for Kubernetes service account
        if Path("/var/run/secrets/kubernetes.io/serviceaccount").exists():
            return True

        return False

    def get_file_system_info(self) -> Dict[str, Any]:
        """Get file system information"""
        try:
            # Get disk usage for current directory
            current_dir = Path.cwd()
            disk_usage = shutil.disk_usage(current_dir)

            return {
                "current_directory": str(current_dir),
                "disk_total_gb": round(disk_usage.total / (1024**3), 2),
                "disk_used_gb": round(disk_usage.used / (1024**3), 2),
                "disk_free_gb": round(disk_usage.free / (1024**3), 2),
                "disk_usage_percent": round(
                    (disk_usage.used / disk_usage.total) * 100, 2
                ),
            }
        except Exception as e:
            self.logger.warning(f"Failed to get disk usage: {e}")
            return {"current_directory": str(Path.cwd()), "error": str(e)}

    def get_relevant_environment_variables(self) -> Dict[str, str]:
        """Get relevant environment variables for environment detection"""
        relevant_vars = [
            # Docker/Container variables
            "DOCKER_CONTAINER",
            "container",
            "HOSTNAME",
            # Kubernetes variables
            "KUBERNETES_SERVICE_HOST",
            "KUBERNETES_SERVICE_PORT",
            "KUBECONFIG",
            "POD_NAME",
            "NAMESPACE",
            # System variables
            "PATH",
            "HOME",
            "USER",
            "SHELL",
            "LANG",
            "PWD",
            # Python variables
            "PYTHONPATH",
            "VIRTUAL_ENV",
            "CONDA_DEFAULT_ENV",
            # MCP-specific variables
            "MCP_ENV",
            "MCP_DEBUG",
            "MCP_LOG_LEVEL",
        ]

        env_vars = {}
        for var in relevant_vars:
            value = os.getenv(var)
            if value is not None:
                # Mask sensitive values
                if any(
                    sensitive in var.upper()
                    for sensitive in ["KEY", "SECRET", "PASSWORD", "TOKEN"]
                ):
                    env_vars[var] = "***MASKED***"
                else:
                    env_vars[var] = value

        return env_vars

    def detect_environment(self) -> EnvironmentInfo:
        """Detect complete environment information"""
        is_docker = self.is_running_in_docker()
        container_type = self.get_container_type() if is_docker else None
        is_containerized = is_docker or container_type is not None

        env_info = EnvironmentInfo(
            platform=self.platform_info.system,
            architecture=self.platform_info.machine,
            is_docker=is_docker,
            is_containerized=is_containerized,
            container_type=container_type,
            python_version=".".join(map(str, sys.version_info[:3])),
            working_directory=str(Path.cwd()),
            home_directory=os.path.expanduser("~"),
            user=os.getenv("USER", os.getenv("USERNAME", "unknown")),
            hostname=self.platform_info.node,
            environment_variables=self.get_relevant_environment_variables(),
            file_system_info=self.get_file_system_info(),
        )

        self.logger.info(
            f"Environment detected: {env_info.platform} "
            f"{'(Docker)' if is_docker else '(Local)'}"
        )

        return env_info

    def get_environment_summary(self) -> Dict[str, Any]:
        """Get concise environment summary"""
        env_info = self.detect_environment()

        return {
            "platform": env_info.platform,
            "architecture": env_info.architecture,
            "is_docker": env_info.is_docker,
            "is_containerized": env_info.is_containerized,
            "container_type": env_info.container_type,
            "python_version": env_info.python_version,
            "is_kubernetes": self.is_running_in_kubernetes(),
            "hostname": env_info.hostname,
            "user": env_info.user,
        }

    def export_environment_info(self, output_path: str, format: str = "json"):
        """Export environment information to file"""
        env_info = self.detect_environment()

        if format.lower() == "json":
            with open(output_path, "w") as f:
                json.dump(asdict(env_info), f, indent=2, default=str)
        elif format.lower() == "txt":
            with open(output_path, "w") as f:
                for key, value in asdict(env_info).items():
                    f.write(f"{key}: {value}\n")
        else:
            raise ValueError(f"Unsupported format: {format}")

        self.logger.info(f"Environment info exported to {output_path}")


# Global environment detector instance


environment_detector = EnvironmentDetector()
