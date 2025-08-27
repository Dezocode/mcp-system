"""
Configuration Manager for MCP System
Provides adaptive configuration management based on environment detection.
"""

import json
import logging
import os
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from .environment_detector import EnvironmentDetector


@dataclass
class ConfigProfile:
    """Configuration profile for specific environments"""

    name: str
    description: str
    settings: Dict[str, Any]
    enabled: bool = True


@dataclass
class AdaptiveConfig:
    """Adaptive configuration based on environment"""

    workspace_root: str
    session_dir: str
    log_level: str
    max_workers: int
    timeout: int
    enable_dashboard: bool
    database_path: str
    cache_dir: str
    temp_dir: str
    security_settings: Dict[str, Any]
    performance_settings: Dict[str, Any]
    docker_specific: Dict[str, Any]
    local_specific: Dict[str, Any]


class ConfigManager:
    """Manages adaptive configuration based on environment"""

    def __init__(self, config_dir: str = None):
        self.config_dir = (
            Path(config_dir) if config_dir else Path(__file__).parent.parent / "config"
        )
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self.logger = logging.getLogger(__name__)
        self.environment_detector = EnvironmentDetector()
        self.current_config: Optional[AdaptiveConfig] = None
        self.config_profiles: Dict[str, ConfigProfile] = {}

        self._load_config_profiles()
        self._initialize_adaptive_config()

    def _load_config_profiles(self):
        """Load configuration profiles from files"""
        profiles_dir = self.config_dir / "profiles"
        profiles_dir.mkdir(exist_ok=True)

        # Load built-in profiles
        builtin_profiles = [
            ConfigProfile(
                name="docker-default",
                description="Default configuration for Docker environments",
                settings={
                    "workspace_root": "/app",
                    "session_dir": "/app/pipeline-sessions",
                    "log_level": "INFO",
                    "max_workers": 4,
                    "timeout": 300,
                    "enable_dashboard": True,
                    "database_path": "/app/data/sessions.db",
                    "cache_dir": "/app/cache",
                    "temp_dir": tempfile.gettempdir(),
                    "security_settings": {
                        "allowed_paths": ["/app", tempfile.gettempdir()],
                        "restricted_paths": ["/etc", "/usr", "/var"],
                        "max_file_size_mb": 10,
                    },
                    "performance_settings": {
                        "memory_limit_mb": 1024,
                        "cpu_limit_cores": 2.0,
                        "disk_quota_gb": 5,
                    },
                },
            ),
            ConfigProfile(
                name="local-development",
                description="Optimized configuration for local development",
                settings={
                    "workspace_root": str(Path.cwd()),
                    "session_dir": str(Path.cwd() / "pipeline-sessions"),
                    "log_level": "DEBUG",
                    "max_workers": 2,
                    "timeout": 600,
                    "enable_dashboard": False,
                    "database_path": str(Path.cwd() / "sessions.db"),
                    "cache_dir": str(Path.cwd() / ".cache"),
                    "temp_dir": str(Path.cwd() / "temp"),
                    "security_settings": {
                        "allowed_paths": [str(Path.cwd()), tempfile.gettempdir()],
                        "restricted_paths": [],
                        "max_file_size_mb": 100,
                    },
                    "performance_settings": {
                        "memory_limit_mb": 2048,
                        "cpu_limit_cores": 4.0,
                        "disk_quota_gb": 50,
                    },
                },
            ),
            ConfigProfile(
                name="kubernetes-production",
                description="Production configuration for Kubernetes environments",
                settings={
                    "workspace_root": "/app",
                    "session_dir": "/app/pipeline-sessions",
                    "log_level": "WARNING",
                    "max_workers": 8,
                    "timeout": 180,
                    "enable_dashboard": True,
                    "database_path": "/data/sessions.db",
                    "cache_dir": os.path.join(tempfile.gettempdir(), "cache"),
                    "temp_dir": tempfile.gettempdir(),
                    "security_settings": {
                        "allowed_paths": ["/app", "/data", tempfile.gettempdir()],
                        "restricted_paths": ["/etc", "/usr", "/var", "/home"],
                        "max_file_size_mb": 5,
                    },
                    "performance_settings": {
                        "memory_limit_mb": 2048,
                        "cpu_limit_cores": 4.0,
                        "disk_quota_gb": 10,
                    },
                },
            ),
        ]

        # Save built-in profiles
        for profile in builtin_profiles:
            self.config_profiles[profile.name] = profile
            profile_file = profiles_dir / f"{profile.name}.json"
            if not profile_file.exists():
                with open(profile_file, "w") as f:
                    json.dump(asdict(profile), f, indent=2)

        # Load custom profiles
        for profile_file in profiles_dir.glob("*.json"):
            if profile_file.name not in [f"{p.name}.json" for p in builtin_profiles]:
                try:
                    with open(profile_file, "r") as f:
                        profile_data = json.load(f)
                    profile = ConfigProfile(**profile_data)
                    self.config_profiles[profile.name] = profile
                except Exception as e:
                    self.logger.warning(f"Failed to load profile {profile_file}: {e}")

    def _initialize_adaptive_config(self):
        """Initialize adaptive configuration based on detected environment"""
        env_info = self.environment_detector.detect_environment()

        # Determine appropriate base configuration
        if env_info.is_docker:
            if self.environment_detector.is_running_in_kubernetes():
                base_profile = self.config_profiles.get("kubernetes-production")
            else:
                base_profile = self.config_profiles.get("docker-default")
        else:
            base_profile = self.config_profiles.get("local-development")

        if base_profile is None:
            # Fallback to local development config
            base_profile = self.config_profiles.get("local-development")

        # Apply base configuration
        base_settings = base_profile.settings.copy() if base_profile else {}

        # Override with environment variables
        env_overrides = self._get_environment_overrides()
        base_settings.update(env_overrides)

        # Create adaptive config
        self.current_config = AdaptiveConfig(
            workspace_root=base_settings.get("workspace_root", str(Path.cwd())),
            session_dir=base_settings.get(
                "session_dir", str(Path.cwd() / "pipeline-sessions")
            ),
            log_level=base_settings.get("log_level", "INFO"),
            max_workers=base_settings.get("max_workers", 2),
            timeout=base_settings.get("timeout", 300),
            enable_dashboard=base_settings.get("enable_dashboard", False),
            database_path=base_settings.get(
                "database_path", str(Path.cwd() / "sessions.db")
            ),
            cache_dir=base_settings.get("cache_dir", str(Path.cwd() / ".cache")),
            temp_dir=base_settings.get("temp_dir", tempfile.gettempdir()),
            security_settings=base_settings.get("security_settings", {}),
            performance_settings=base_settings.get("performance_settings", {}),
            docker_specific=(
                base_settings.get("docker_specific", {}) if env_info.is_docker else {}
            ),
            local_specific=(
                base_settings.get("local_specific", {})
                if not env_info.is_docker
                else {}
            ),
        )

        # Ensure directories exist
        Path(self.current_config.session_dir).mkdir(parents=True, exist_ok=True)
        Path(self.current_config.cache_dir).mkdir(parents=True, exist_ok=True)
        Path(self.current_config.temp_dir).mkdir(parents=True, exist_ok=True)
        Path(self.current_config.database_path).parent.mkdir(
            parents=True, exist_ok=True
        )

        self.logger.info(
            f"Adaptive configuration initialized for "
            f"{'Docker' if env_info.is_docker else 'Local'} environment"
        )

    def _get_environment_overrides(self) -> Dict[str, Any]:
        """Get configuration overrides from environment variables"""
        overrides = {}

        # Map environment variables to config keys
        env_mapping = {
            "MCP_WORKSPACE_ROOT": "workspace_root",
            "MCP_SESSION_DIR": "session_dir",
            "MCP_LOG_LEVEL": "log_level",
            "MCP_MAX_WORKERS": "max_workers",
            "MCP_TIMEOUT": "timeout",
            "MCP_ENABLE_DASHBOARD": "enable_dashboard",
            "MCP_DATABASE_PATH": "database_path",
            "MCP_CACHE_DIR": "cache_dir",
            "MCP_TEMP_DIR": "temp_dir",
        }

        for env_var, config_key in env_mapping.items():
            value = os.getenv(env_var)
            if value is not None:
                # Convert numeric values
                if config_key in ["max_workers", "timeout"]:
                    try:
                        overrides[config_key] = int(value)
                    except ValueError:
                        self.logger.warning(
                            f"Invalid integer value for {env_var}: {value}"
                        )
                elif config_key == "enable_dashboard":
                    overrides[config_key] = value.lower() in ["true", "1", "yes"]
                else:
                    overrides[config_key] = value

        return overrides

    def get_config(self) -> AdaptiveConfig:
        """Get current adaptive configuration"""
        if self.current_config is None:
            self._initialize_adaptive_config()
        return self.current_config

    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get specific configuration setting"""
        config = self.get_config()
        return getattr(config, key, default)

    def get_security_setting(self, key: str, default: Any = None) -> Any:
        """Get specific security setting"""
        config = self.get_config()
        return config.security_settings.get(key, default)

    def get_performance_setting(self, key: str, default: Any = None) -> Any:
        """Get specific performance setting"""
        config = self.get_config()
        return config.performance_settings.get(key, default)

    def reload_configuration(self):
        """Reload configuration based on current environment"""
        self.logger.info("Reloading configuration...")
        self._initialize_adaptive_config()

    def get_config_profile(self, profile_name: str) -> Optional[ConfigProfile]:
        """Get specific configuration profile"""
        return self.config_profiles.get(profile_name)

    def list_config_profiles(self) -> List[str]:
        """List available configuration profiles"""
        return list(self.config_profiles.keys())

    def apply_config_profile(self, profile_name: str) -> bool:
        """Apply specific configuration profile"""
        profile = self.get_config_profile(profile_name)
        if profile is None or not profile.enabled:
            self.logger.warning(f"Profile {profile_name} not found or disabled")
            return False

        # Apply profile settings
        if self.current_config:
            for key, value in profile.settings.items():
                if hasattr(self.current_config, key):
                    setattr(self.current_config, key, value)
                elif key == "security_settings":
                    self.current_config.security_settings.update(value)
                elif key == "performance_settings":
                    self.current_config.performance_settings.update(value)

        self.logger.info(f"Applied configuration profile: {profile_name}")
        return True

    def get_config_summary(self) -> Dict[str, Any]:
        """Get summary of current configuration"""
        config = self.get_config()
        env_summary = self.environment_detector.get_environment_summary()

        return {
            "environment": env_summary,
            "workspace_root": config.workspace_root,
            "session_dir": config.session_dir,
            "log_level": config.log_level,
            "max_workers": config.max_workers,
            "timeout": config.timeout,
            "enable_dashboard": config.enable_dashboard,
            "database_path": config.database_path,
            "cache_dir": config.cache_dir,
            "temp_dir": config.temp_dir,
            "security_settings": {
                "allowed_paths_count": len(
                    config.security_settings.get("allowed_paths", [])
                ),
                "restricted_paths_count": len(
                    config.security_settings.get("restricted_paths", [])
                ),
                "max_file_size_mb": config.security_settings.get("max_file_size_mb", 0),
            },
            "performance_settings": {
                "memory_limit_mb": config.performance_settings.get(
                    "memory_limit_mb", 0
                ),
                "cpu_limit_cores": config.performance_settings.get(
                    "cpu_limit_cores", 0.0
                ),
                "disk_quota_gb": config.performance_settings.get("disk_quota_gb", 0),
            },
        }

    def validate_configuration(self) -> Dict[str, Any]:
        """Validate current configuration"""
        config = self.get_config()
        validation_results = {"valid": True, "issues": [], "warnings": []}

        # Validate paths
        paths_to_check = [
            ("workspace_root", config.workspace_root),
            ("session_dir", config.session_dir),
            ("cache_dir", config.cache_dir),
            ("temp_dir", config.temp_dir),
            ("database_path", config.database_path),
        ]

        for path_name, path_value in paths_to_check:
            path_obj = Path(path_value)
            if not path_obj.exists():
                try:
                    if path_name == "database_path":
                        path_obj.parent.mkdir(parents=True, exist_ok=True)
                    else:
                        path_obj.mkdir(parents=True, exist_ok=True)
                    validation_results["warnings"].append(
                        f"Created missing directory: {path_name} = {path_value}"
                    )
                except Exception as e:
                    validation_results["valid"] = False
                    validation_results["issues"].append(
                        f"Cannot create directory {path_name}: {e}"
                    )
            elif not os.access(
                path_obj.parent if path_name == "database_path" else path_obj, os.W_OK
            ):
                validation_results["valid"] = False
                validation_results["issues"].append(
                    f"No write access to {path_name}: {path_value}"
                )

        # Validate numeric settings
        if config.max_workers < 1:
            validation_results["valid"] = False
            validation_results["issues"].append("max_workers must be >= 1")

        if config.timeout < 1:
            validation_results["valid"] = False
            validation_results["issues"].append("timeout must be >= 1")

        if not validation_results["valid"]:
            self.logger.error("Configuration validation failed:")
            for issue in validation_results["issues"]:
                self.logger.error(f"  - {issue}")

        if validation_results["warnings"]:
            for warning in validation_results["warnings"]:
                self.logger.warning(f"  - {warning}")

        return validation_results


# Global config manager instance


config_manager = ConfigManager()
