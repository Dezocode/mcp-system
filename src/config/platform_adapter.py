"""
Platform Adapter for MCP System
Handles platform-specific adaptations and optimizations.
"""

import os
import platform
import multiprocessing
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional
import logging


class PlatformAdapter:
    """Handles platform-specific adaptations and optimizations"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.system = platform.system().lower()
        self.machine = platform.machine().lower()
        self.release = platform.release()

    def get_optimal_worker_count(self) -> int:
        """Get optimal worker count based on system resources"""
        try:
            cpu_count = multiprocessing.cpu_count()

            # For Docker containers, respect CPU limits
            if self._is_running_in_docker():
                cpu_limit = self._get_docker_cpu_limit()
                if cpu_limit and cpu_limit < cpu_count:
                    return max(1, int(cpu_limit))

            # Limit workers to prevent resource exhaustion
            return min(cpu_count, 8)  # Cap at 8 workers

        except Exception as e:
            self.logger.warning(f"Failed to determine optimal worker count: {e}")
            return 2

    def get_memory_limit_mb(self) -> Optional[int]:
        """Get memory limit in MB if running in container"""
        if self._is_running_in_docker():
            # Try to get Docker memory limit
            try:
                with open('/sys/fs/cgroup/memory/memory.limit_in_bytes', 'r') as f:
                    limit_bytes = int(f.read().strip())
                    # Less than ~8EB (unlimited marker)
                    if limit_bytes < 9223372036854771712:
                        return limit_bytes // (1024 * 1024)  # Convert to MB
            except (FileNotFoundError, ValueError, PermissionError):
                pass

            # Try cgroup v2
            try:
                with open('/sys/fs/cgroup/memory.max', 'r') as f:
                    content = f.read().strip()
                    if content != "max":
                        limit_bytes = int(content)
                        return limit_bytes // (1024 * 1024)  # Convert to MB
            except (FileNotFoundError, ValueError, PermissionError):
                pass

        return None

    def get_temp_directory(self) -> str:
        """Get appropriate temporary directory for current platform"""
        # Check environment variables first
        temp_dirs = [
            os.getenv('TMPDIR'),
            os.getenv('TEMP'),
            os.getenv('TMP'),
        ]

        for temp_dir in temp_dirs:
            if temp_dir and os.path.exists(temp_dir) and os.access(temp_dir, os.W_OK):
                return temp_dir

        # Platform-specific defaults
        if self.system == 'windows':
            default_temp = 'C:\\Temp'
        else:  # macOS, Linux and others
            default_temp = tempfile.gettempdir()

        # Ensure temp directory exists and is writable
        Path(default_temp).mkdir(parents=True, exist_ok=True)

        if os.access(default_temp, os.W_OK):
            return default_temp
        else:
            # Fallback to current directory
            fallback_temp = str(Path.cwd() / 'temp')
            Path(fallback_temp).mkdir(parents=True, exist_ok=True)
            return fallback_temp

    def get_optimal_buffer_sizes(self) -> Dict[str, int]:
        """Get optimal buffer sizes based on platform and available memory"""
        # Base buffer sizes
        buffer_sizes = {
            "file_read_buffer": 8192,    # 8KB
            "network_buffer": 16384,     # 16KB
            "compression_buffer": 32768,  # 32KB
            "log_buffer": 4096,          # 4KB
        }

        # Adjust based on available memory
        try:
            # Try to get memory info via /proc/meminfo on Linux
            if self.system == 'linux':
                with open('/proc/meminfo', 'r') as f:
                    meminfo = f.read()
                    for line in meminfo.split('\n'):
                        if line.startswith('MemAvailable:'):
                            available_kb = int(line.split()[1])
                            available_mb = available_kb / 1024

                            if available_mb < 512:  # Less than 512MB
                                # Reduce buffer sizes for low memory
                                buffer_sizes = {
                                    key: max(1024, value // 2)
                                    for key, value in buffer_sizes.items()
                                }
                            elif available_mb > 4096:  # More than 4GB
                                # Increase buffer sizes for abundant memory
                                buffer_sizes = {
                                    key: value * 2
                                    for key, value in buffer_sizes.items()
                                }
                            break
        except Exception as e:
            self.logger.warning(f"Failed to adjust buffer sizes based on memory: {e}")

        return buffer_sizes

    def get_platform_specific_commands(self) -> Dict[str, str]:
        """Get platform-specific commands for common operations"""
        if self.system == 'windows':
            return {
                "shell": "cmd",
                "list_files": "dir",
                "copy_file": "copy",
                "move_file": "move",
                "delete_file": "del",
                "make_directory": "mkdir",
                "remove_directory": "rmdir",
            }
        else:  # Unix-like systems (Linux, macOS, etc.)
            return {
                "shell": "/bin/sh",
                "list_files": "ls -la",
                "copy_file": "cp",
                "move_file": "mv",
                "delete_file": "rm",
                "make_directory": "mkdir -p",
                "remove_directory": "rm -rf",
            }

    def get_system_info(self) -> Dict[str, Any]:
        """Get detailed system information"""
        system_info = {
            "platform": self.system,
            "machine": self.machine,
            "release": self.release,
            "python_version": platform.python_version(),
            "architecture": platform.architecture()[0],
        }

        # Add CPU information
        try:
            system_info["cpu_count"] = multiprocessing.cpu_count()
        except Exception as e:
            self.logger.warning(f"Failed to get CPU count: {e}")
            system_info["cpu_count"] = 1

        # Add memory information (Linux only for now)
        if self.system == 'linux':
            try:
                with open('/proc/meminfo', 'r') as f:
                    meminfo = f.read()
                    for line in meminfo.split('\n'):
                        if line.startswith('MemTotal:'):
                            total_kb = int(line.split()[1])
                            system_info["total_memory_mb"] = total_kb / 1024
                        elif line.startswith('MemAvailable:'):
                            available_kb = int(line.split()[1])
                            system_info["available_memory_mb"] = available_kb / 1024

            except Exception as e:
                self.logger.warning(f"Failed to get memory info: {e}")
                system_info["memory_info"] = f"Error: {e}"

        return system_info

    def optimize_for_current_platform(self) -> Dict[str, Any]:
        """Apply platform-specific optimizations"""
        optimizations = {
            "worker_count": self.get_optimal_worker_count(),
            "temp_directory": self.get_temp_directory(),
            "buffer_sizes": self.get_optimal_buffer_sizes(),
            "commands": self.get_platform_specific_commands(),
            "system_info": self.get_system_info(),
        }

        # Apply memory limit if detected
        memory_limit = self.get_memory_limit_mb()
        if memory_limit:
            optimizations["memory_limit_mb"] = memory_limit

        self.logger.info(f"Platform optimizations applied for {self.system}")

        return optimizations

    def _is_running_in_docker(self) -> bool:
        """Check if running in Docker container"""
        # Check for .dockerenv file
        if Path('/.dockerenv').exists():
            return True

        # Check cgroup info (Linux only)
        if self.system == 'linux':
            try:
                with open('/proc/self/cgroup', 'r') as f:
                    if 'docker' in f.read().lower():
                        return True
            except (FileNotFoundError, PermissionError):
                pass

        return False

    def _get_docker_cpu_limit(self) -> Optional[float]:
        """Get Docker CPU limit if running in container"""
        # Try cgroup v1
        try:
            with open('/sys/fs/cgroup/cpu/cpu.cfs_quota_us', 'r') as f:
                quota = int(f.read().strip())
            with open('/sys/fs/cgroup/cpu/cpu.cfs_period_us', 'r') as f:
                period = int(f.read().strip())

            if quota > 0 and period > 0:
                return quota / period
        except (FileNotFoundError, ValueError, PermissionError):
            pass

        # Try cgroup v2
        try:
            with open('/sys/fs/cgroup/cpu.max', 'r') as f:
                content = f.read().strip().split()
                if len(content) == 2 and content[0] != "max":
                    quota = int(content[0])
                    period = int(content[1])
                    return quota / period
        except (FileNotFoundError, ValueError, PermissionError):
            pass

        return None

    def get_path_separator(self) -> str:
        """Get appropriate path separator for current platform"""
        return os.sep

    def normalize_path(self, path: str) -> str:
        """Normalize path for current platform"""
        return os.path.normpath(path)

    def get_case_sensitive_filesystem(self) -> bool:
        """Check if filesystem is case-sensitive"""
        if self.system == 'windows':
            return False
        elif self.system == 'darwin':  # macOS
            # HFS+ is typically case-insensitive, APFS can be either
            return False
        else:  # Linux and other Unix-like
            return True

    def get_preferred_encoding(self) -> str:
        """Get preferred text encoding for current platform"""
        # Try to detect from environment
        preferred_encodings = [
            'utf-8',  # Default fallback
        ]

        # Check locale environment variables
        locale_vars = ['LC_ALL', 'LC_CTYPE', 'LANG']
        for var in locale_vars:
            locale_value = os.getenv(var, '')
            if '.' in locale_value:
                encoding = locale_value.split('.')[-1]
                if encoding.lower() not in ['utf-8', 'utf8']:
                    preferred_encodings.insert(0, encoding)

        return preferred_encodings[0]


# Global platform adapter instance
platform_adapter = PlatformAdapter()
