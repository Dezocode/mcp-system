"""
Configuration and Environment Detection Module
Provides adaptive configuration management and environment detection for MCP servers.
"""

from .config_manager import AdaptiveConfig, ConfigManager, ConfigProfile, config_manager
from .environment_detector import (
    EnvironmentDetector,
    EnvironmentInfo,
    environment_detector,
)
from .platform_adapter import PlatformAdapter, platform_adapter
from .runtime_profiler import (
    PerformanceProfile,
    PerformanceSnapshot,
    RuntimeProfiler,
    runtime_profiler,
)

__all__ = [
    "EnvironmentDetector",
    "EnvironmentInfo",
    "environment_detector",
    "ConfigManager",
    "ConfigProfile",
    "AdaptiveConfig",
    "config_manager",
    "PlatformAdapter",
    "platform_adapter",
    "RuntimeProfiler",
    "PerformanceSnapshot",
    "PerformanceProfile",
    "runtime_profiler",
]
