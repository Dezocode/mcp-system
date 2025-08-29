"""MCP System - Core Package

Universal MCP server management system with Claude Code integration.
Provides tools for server discovery, installation, upgrade management,
and seamless integration with Claude Desktop.
"""

__version__ = "1.0.0"
__author__ = "DezoCode"
__email__ = "contact@dezocode.com"
__description__ = "Universal MCP server management system with Claude Code integration"

# Core system imports
# Pipeline MCP server moved to mcp-tools/pipeline-mcp/src/main.py
# Import conditionally since it's now in standardized location
try:
    import sys
    from pathlib import Path

    pipeline_server_path = (
        Path(__file__).parent.parent / "mcp-tools" / "pipeline-mcp" / "src"
    )
    sys.path.insert(0, str(pipeline_server_path))
    import main as pipeline_mcp_server
except ImportError:
    pipeline_mcp_server = None
from . import auto_discovery_system, claude_code_mcp_bridge, install_mcp_system

# Configuration and environment detection
try:
    from .config import (
        config_manager,
        environment_detector,
        platform_adapter,
        runtime_profiler,
    )
except ImportError:
    # Graceful degradation if config modules are not available
    config_manager = None
    environment_detector = None
    platform_adapter = None
    runtime_profiler = None

# Docker integration
try:
    from .docker import health_check
except ImportError:
    health_check = None

# Core exports for external usage
__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__email__",
    "__description__",
    # Main modules
    "pipeline_mcp_server",
    "auto_discovery_system",
    "claude_code_mcp_bridge",
    "install_mcp_system",
    # Configuration
    "config_manager",
    "environment_detector",
    "platform_adapter",
    "runtime_profiler",
    # Docker
    "health_check",
    # Core functions
    "get_system_info",
    "initialize_system",
    "validate_installation",
]


def get_system_info():
    """Get comprehensive system information and status"""
    info = {
        "version": __version__,
        "author": __author__,
        "description": __description__,
        "modules": {
            "pipeline_mcp_server": pipeline_mcp_server is not None,
            "auto_discovery": True,
            "claude_bridge": True,
            "installer": True,
            "config_manager": config_manager is not None,
            "environment_detector": environment_detector is not None,
            "docker_integration": health_check is not None,
        },
    }

    # Add environment detection if available
    if environment_detector:
        try:
            env_info = environment_detector.detect_environment()
            info["environment"] = {
                "platform": env_info.platform,
                "architecture": env_info.architecture,
                "is_docker": env_info.is_docker,
                "is_kubernetes": env_info.is_kubernetes,
            }
        except Exception:
            info["environment"] = {"status": "detection_failed"}

    return info


def initialize_system(config_path=None):
    """Initialize the MCP system with optional configuration"""
    initialization_status = {"success": True, "components": {}, "errors": []}

    try:
        # Initialize configuration manager
        if config_manager:
            try:
                if config_path:
                    config_manager.load_config(config_path)
                initialization_status["components"]["config"] = True
            except Exception as e:
                initialization_status["components"]["config"] = False
                initialization_status["errors"].append(
                    f"Config initialization failed: {e}"
                )

        # Initialize environment detection
        if environment_detector:
            try:
                environment_detector.detect_environment()
                initialization_status["components"]["environment_detector"] = True
            except Exception as e:
                initialization_status["components"]["environment_detector"] = False
                initialization_status["errors"].append(
                    f"Environment detection failed: {e}"
                )

        # Initialize runtime profiler
        if runtime_profiler:
            try:
                runtime_profiler.start_profiling()
                initialization_status["components"]["runtime_profiler"] = True
            except Exception as e:
                initialization_status["components"]["runtime_profiler"] = False
                initialization_status["errors"].append(f"Runtime profiler failed: {e}")

    except Exception as e:
        initialization_status["success"] = False
        initialization_status["errors"].append(f"System initialization failed: {e}")

    return initialization_status


def validate_installation():
    """Validate the MCP system installation and dependencies"""
    validation_results = {"valid": True, "components": {}, "issues": []}

    # Check core modules
    core_modules = [
        "pipeline_mcp_server",
        "auto_discovery_system",
        "claude_code_mcp_bridge",
        "install_mcp_system",
    ]

    for module_name in core_modules:
        try:
            module = globals().get(module_name)
            validation_results["components"][module_name] = module is not None
            if module is None:
                validation_results["issues"].append(
                    f"Core module {module_name} not available"
                )
        except Exception as e:
            validation_results["components"][module_name] = False
            validation_results["issues"].append(
                f"Module {module_name} validation failed: {e}"
            )

    # Check optional components
    optional_components = {
        "config_manager": config_manager,
        "environment_detector": environment_detector,
        "platform_adapter": platform_adapter,
        "runtime_profiler": runtime_profiler,
        "docker_health_check": health_check,
    }

    for comp_name, comp_module in optional_components.items():
        validation_results["components"][comp_name] = comp_module is not None
        if comp_module is None:
            validation_results["issues"].append(
                f"Optional component {comp_name} not available"
            )

    # Determine overall validity
    required_components = [
        "pipeline_mcp_server",
        "auto_discovery_system",
        "claude_code_mcp_bridge",
    ]
    missing_required = [
        comp
        for comp in required_components
        if not validation_results["components"].get(comp, False)
    ]

    if missing_required:
        validation_results["valid"] = False
        validation_results["issues"].append(
            f"Missing required components: {missing_required}"
        )

    return validation_results
