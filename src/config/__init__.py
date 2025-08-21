"""
Configuration and Environment Detection Module
Provides adaptive configuration management and environment detection for MCP servers.
"""

from .environment_detector import EnvironmentDetector, EnvironmentInfo, environment_detector
from .config_manager import ConfigManager, ConfigProfile, AdaptiveConfig, config_manager
from .platform_adapter import PlatformAdapter, platform_adapter
from .runtime_profiler import RuntimeProfiler, PerformanceSnapshot, PerformanceProfile, runtime_profiler

__all__ = [
    'EnvironmentDetector',
    'EnvironmentInfo', 
    'environment_detector',
    'ConfigManager',
    'ConfigProfile',
    'AdaptiveConfig',
    'config_manager',
    'PlatformAdapter',
    'platform_adapter',
    'RuntimeProfiler',
    'PerformanceSnapshot',
    'PerformanceProfile',
    'runtime_profiler'
]