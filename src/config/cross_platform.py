#!/usr/bin/env python3
"""
Cross-Platform Path and Environment Resolution System
Automatically handles Linux, Windows, macOS, WSL, and Docker environments
"""

import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


class CrossPlatformResolver:
    """Unified cross-platform path and environment resolver"""

    def __init__(self):
        self._cache = {}
        self.platform_info = self._detect_platform()
        self.paths = self._resolve_paths()
        self.commands = self._resolve_commands()

    def _detect_platform(self) -> Dict[str, Any]:
        """Comprehensive platform detection"""
        info = {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": sys.version,
            "is_64bit": sys.maxsize > 2**32,
        }

        # Detect special environments
        info["is_docker"] = self._is_docker()
        info["is_wsl"] = self._is_wsl()
        info["is_github_actions"] = os.environ.get("GITHUB_ACTIONS") == "true"
        info["is_ci"] = any(
            os.environ.get(var)
            for var in ["CI", "CONTINUOUS_INTEGRATION", "JENKINS", "TRAVIS"]
        )

        # Determine primary platform
        if info["is_docker"]:
            info["platform"] = "docker"
        elif info["is_wsl"]:
            info["platform"] = "wsl"
        elif info["system"] == "Darwin":
            info["platform"] = "macos"
        elif info["system"] == "Windows":
            info["platform"] = "windows"
        elif info["system"] == "Linux":
            info["platform"] = "linux"
        else:
            info["platform"] = "unknown"

        return info

    def _is_docker(self) -> bool:
        """Detect if running in Docker container"""
        # Method 1: Check for .dockerenv file
        if os.path.exists("/.dockerenv"):
            return True

        # Method 2: Check cgroup
        try:
            with open("/proc/self/cgroup", "r") as f:
                return "docker" in f.read()
        except:
            pass

        # Method 3: Check environment variable
        return os.environ.get("MCP_ENV") == "docker"

    def _is_wsl(self) -> bool:
        """Detect if running in WSL"""
        if platform.system() != "Linux":
            return False

        # Check for WSL-specific indicators
        try:
            with open("/proc/version", "r") as f:
                return "microsoft" in f.read().lower()
        except:
            pass

        # Check for WSL environment variables
        return "WSL_DISTRO_NAME" in os.environ or "WSL_INTEROP" in os.environ

    def _resolve_paths(self) -> Dict[str, Path]:
        """Resolve all system paths based on platform"""
        paths = {}

        # Get base directories
        if self.platform_info["is_docker"]:
            paths["home"] = Path("/app")
            paths["config"] = Path("/app/config")
            paths["data"] = Path("/app/data")
            paths["cache"] = Path("/app/cache")
            paths["temp"] = Path("/tmp")
        else:
            paths["home"] = Path.home()

            # Config directory
            if self.platform_info["platform"] == "windows":
                paths["config"] = (
                    Path(
                        os.environ.get("APPDATA", paths["home"] / "AppData" / "Roaming")
                    )
                    / "mcp-system"
                )
            elif self.platform_info["platform"] == "macos":
                paths["config"] = (
                    paths["home"] / "Library" / "Application Support" / "mcp-system"
                )
            else:  # Linux, WSL
                paths["config"] = (
                    Path(os.environ.get("XDG_CONFIG_HOME", paths["home"] / ".config"))
                    / "mcp-system"
                )

            # Data directory
            if self.platform_info["platform"] == "windows":
                paths["data"] = (
                    Path(
                        os.environ.get(
                            "LOCALAPPDATA", paths["home"] / "AppData" / "Local"
                        )
                    )
                    / "mcp-system"
                )
            elif self.platform_info["platform"] == "macos":
                paths["data"] = (
                    paths["home"]
                    / "Library"
                    / "Application Support"
                    / "mcp-system"
                    / "data"
                )
            else:  # Linux, WSL
                paths["data"] = (
                    Path(
                        os.environ.get(
                            "XDG_DATA_HOME", paths["home"] / ".local" / "share"
                        )
                    )
                    / "mcp-system"
                )

            # Cache directory
            if self.platform_info["platform"] == "windows":
                paths["cache"] = (
                    Path(os.environ.get("TEMP", "/tmp")) / "mcp-system-cache"
                )
            elif self.platform_info["platform"] == "macos":
                paths["cache"] = paths["home"] / "Library" / "Caches" / "mcp-system"
            else:  # Linux, WSL
                paths["cache"] = (
                    Path(os.environ.get("XDG_CACHE_HOME", paths["home"] / ".cache"))
                    / "mcp-system"
                )

            # Temp directory
            paths["temp"] = Path(
                os.environ.get("TMPDIR", os.environ.get("TEMP", "/tmp"))
            )

        # MCP-specific paths
        paths["mcp_home"] = paths["config"] / ".mcp-system"
        paths["mcp_bin"] = (
            paths["home"] / "bin"
            if self.platform_info["platform"] != "windows"
            else paths["home"] / "Scripts"
        )
        paths["mcp_components"] = paths["mcp_home"] / "components"
        paths["mcp_templates"] = paths["mcp_home"] / "templates"
        paths["mcp_backups"] = paths["mcp_home"] / "backups"
        paths["mcp_logs"] = paths["data"] / "logs"
        paths["mcp_sessions"] = paths["data"] / "sessions"

        # Project root (current working directory or detected)
        paths["project_root"] = self._find_project_root()

        # Scripts and source
        paths["scripts"] = paths["project_root"] / "scripts"
        paths["src"] = paths["project_root"] / "src"
        paths["core"] = paths["project_root"] / "core"

        return paths

    def _find_project_root(self) -> Path:
        """Find the project root directory"""
        # Start from current directory
        current = Path.cwd()

        # Look for indicators of project root
        indicators = [
            "pyproject.toml",
            "requirements.txt",
            ".git",
            "Dockerfile",
            "docker-compose.yml",
        ]

        # Search up to 5 levels
        for _ in range(5):
            for indicator in indicators:
                if (current / indicator).exists():
                    return current
            if current.parent == current:
                break
            current = current.parent

        # Default to current directory
        return Path.cwd()

    def _resolve_commands(self) -> Dict[str, str]:
        """Resolve command paths based on platform"""
        commands = {}

        # Python command
        if self.platform_info["platform"] == "windows":
            commands["python"] = (
                self._find_command(["python", "python3", "py"]) or "python"
            )
        else:
            commands["python"] = self._find_command(["python3", "python"]) or "python3"

        # Pip command
        if self.platform_info["platform"] == "windows":
            commands["pip"] = self._find_command(["pip", "pip3"]) or "pip"
        else:
            commands["pip"] = self._find_command(["pip3", "pip"]) or "pip3"

        # Git command
        commands["git"] = self._find_command(["git"]) or "git"

        # Docker command
        if self.platform_info["is_wsl"]:
            # Try Windows Docker first in WSL
            win_docker = Path(
                "/mnt/c/Program Files/Docker/Docker/resources/bin/docker.exe"
            )
            if win_docker.exists():
                commands["docker"] = str(win_docker)
            else:
                commands["docker"] = self._find_command(["docker"]) or "docker"
        else:
            commands["docker"] = self._find_command(["docker"]) or "docker"

        # Shell command
        if self.platform_info["platform"] == "windows":
            commands["shell"] = os.environ.get("COMSPEC", "cmd.exe")
            commands["shell_flag"] = "/c"
        else:
            commands["shell"] = os.environ.get("SHELL", "/bin/bash")
            commands["shell_flag"] = "-c"

        return commands

    def _find_command(self, names: list) -> Optional[str]:
        """Find the first available command from a list"""
        for name in names:
            path = shutil.which(name)
            if path:
                return path
        return None

    def get_path(self, key: str) -> Path:
        """Get a resolved path by key"""
        return self.paths.get(key, Path.cwd())

    def get_command(self, key: str) -> str:
        """Get a resolved command by key"""
        return self.commands.get(key, key)

    def run_command(self, cmd: list, **kwargs) -> subprocess.CompletedProcess:
        """Run a command with platform-appropriate settings"""
        # Adjust command for platform
        if self.platform_info["platform"] == "windows":
            # Use shell=True on Windows for better compatibility
            kwargs.setdefault("shell", True)

        # Set encoding
        kwargs.setdefault("encoding", "utf-8")
        kwargs.setdefault("errors", "replace")

        return subprocess.run(cmd, **kwargs)

    def make_executable(self, filepath: Path):
        """Make a file executable on Unix-like systems"""
        if self.platform_info["platform"] not in ["windows"]:
            import stat

            current = filepath.stat().st_mode
            filepath.chmod(current | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)

    def normalize_path(self, path: str) -> str:
        """Normalize path for current platform"""
        path = os.path.expanduser(path)
        path = os.path.expandvars(path)
        path = os.path.normpath(path)

        # Handle WSL paths
        if self.platform_info["is_wsl"] and path.startswith("/mnt/"):
            # Keep WSL mount paths as-is
            return path

        return str(Path(path).resolve())

    def get_file_separator(self) -> str:
        """Get the appropriate file separator"""
        return os.sep

    def get_path_separator(self) -> str:
        """Get the PATH environment variable separator"""
        return ";" if self.platform_info["platform"] == "windows" else ":"

    def to_dict(self) -> Dict[str, Any]:
        """Export configuration as dictionary"""
        return {
            "platform_info": self.platform_info,
            "paths": {k: str(v) for k, v in self.paths.items()},
            "commands": self.commands,
        }

    def save_config(self, filepath: Optional[Path] = None):
        """Save configuration to file"""
        if not filepath:
            filepath = self.paths["config"] / "platform_config.json"

        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    def ensure_directories(self):
        """Ensure all required directories exist"""
        for key, path in self.paths.items():
            if key.startswith("mcp_"):
                path.mkdir(parents=True, exist_ok=True)


# Global instance
cross_platform = CrossPlatformResolver()


# Convenience functions
def get_path(key: str) -> Path:
    """Get a resolved path"""
    return cross_platform.get_path(key)


def get_command(key: str) -> str:
    """Get a resolved command"""
    return cross_platform.get_command(key)


def run_cross_platform(cmd: list, **kwargs) -> subprocess.CompletedProcess:
    """Run a command cross-platform"""
    return cross_platform.run_command(cmd, **kwargs)


def get_platform() -> str:
    """Get the current platform"""
    return cross_platform.platform_info["platform"]


def is_docker() -> bool:
    """Check if running in Docker"""
    return cross_platform.platform_info["is_docker"]


def is_wsl() -> bool:
    """Check if running in WSL"""
    return cross_platform.platform_info["is_wsl"]


if __name__ == "__main__":
    # Test the resolver
    print("Cross-Platform Configuration:")
    print(json.dumps(cross_platform.to_dict(), indent=2))

    # Ensure directories
    cross_platform.ensure_directories()
    print(f"\n✅ Directories created at {cross_platform.paths['mcp_home']}")
