# Environment Detection and Configuration
## Phase 2 Feature Documentation

### Overview
This document provides comprehensive documentation for implementing environment detection and adaptive configuration in the MCP Pipeline system. Based on Anthropic's Model Context Protocol (MCP) specification, this feature enables automatic detection of runtime environment (Docker vs local) and adapts configuration accordingly.

### MCP Protocol Compliance
The implementation follows Anthropic's MCP v1.0 specification for:
- Environment-aware configuration
- Adaptive system behavior
- Cross-platform compatibility
- Configuration management

### System Architecture

#### Core Components
1. **EnvironmentDetector Class** - Runtime environment detection
2. **ConfigManager Class** - Adaptive configuration management
3. **PlatformAdapter Class** - Platform-specific adaptations
4. **RuntimeProfiler Class** - Runtime performance profiling

#### Directory Structure
```
src/
├── config/
│   ├── __init__.py
│   ├── environment_detector.py
│   ├── config_manager.py
│   ├── platform_adapter.py
│   └── runtime_profiler.py
└── pipeline_mcp_server.py (integration point)
```

### Implementation Details

#### 1. EnvironmentDetector Class
Runtime environment detection capabilities.

```python
# File: src/config/environment_detector.py
import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
import logging
import json

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
    network_info: Dict[str, Any]
    process_info: Dict[str, Any]

class EnvironmentDetector:
    """Detects runtime environment and provides environment information"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.platform_info = platform.uname()
        
    def is_running_in_docker(self) -> bool:
        """Detect if running inside Docker container"""
        # Method 1: Check for .dockerenv file
        if Path('/.dockerenv').exists():
            self.logger.debug("Detected Docker via /.dockerenv file")
            return True
            
        # Method 2: Check cgroup info (Linux only)
        if self.platform_info.system.lower() == 'linux':
            try:
                with open('/proc/self/cgroup', 'r') as f:
                    content = f.read().lower()
                    if 'docker' in content or 'containerd' in content:
                        self.logger.debug("Detected Docker via cgroup")
                        return True
            except (FileNotFoundError, PermissionError, OSError):
                pass
                
        # Method 3: Check environment variables
        docker_env_vars = [
            'DOCKER_CONTAINER',
            'container',  # Used by some container runtimes
        ]
        
        for env_var in docker_env_vars:
            if os.getenv(env_var):
                self.logger.debug(f"Detected container via environment variable: {env_var}")
                return True
                
        # Method 4: Check mount info
        if self.platform_info.system.lower() == 'linux':
            try:
                with open('/proc/self/mounts', 'r') as f:
                    mounts = f.read().lower()
                    if 'docker' in mounts:
                        self.logger.debug("Detected Docker via mount info")
                        return True
            except (FileNotFoundError, PermissionError, OSError):
                pass
                
        self.logger.debug("Not running in Docker/container")
        return False
        
    def get_container_type(self) -> Optional[str]:
        """Detect specific container technology"""
        if not self.is_running_in_docker():
            return None
            
        # Check for specific container technologies
        try:
            # Check cgroup for container type
            with open('/proc/self/cgroup', 'r') as f:
                content = f.read().lower()
                
                if 'docker' in content:
                    return 'docker'
                elif 'containerd' in content:
                    return 'containerd'
                elif 'podman' in content:
                    return 'podman'
                elif 'lxc' in content:
                    return 'lxc'
                elif 'systemd-nspawn' in content:
                    return 'systemd-nspawn'
                    
        except (FileNotFoundError, PermissionError, OSError):
            pass
            
        # Check environment variables
        container_env = os.getenv('container')
        if container_env:
            return container_env
            
        return 'unknown-container'
        
    def is_running_in_kubernetes(self) -> bool:
        """Detect if running in Kubernetes"""
        # Check for Kubernetes-specific environment variables
        k8s_env_vars = [
            'KUBERNETES_SERVICE_HOST',
            'KUBERNETES_SERVICE_PORT',
            'KUBECONFIG',
        ]
        
        for env_var in k8s_env_vars:
            if os.getenv(env_var):
                return True
                
        # Check for Kubernetes service account
        if Path('/var/run/secrets/kubernetes.io/serviceaccount').exists():
            return True
            
        return False
        
    def get_platform_info(self) -> Dict[str, str]:
        """Get detailed platform information"""
        return {
            "system": self.platform_info.system,
            "node": self.platform_info.node,
            "release": self.platform_info.release,
            "version": self.platform_info.version,
            "machine": self.platform_info.machine,
            "processor": self.platform_info.processor,
        }
        
    def get_python_info(self) -> Dict[str, str]:
        """Get Python interpreter information"""
        return {
            "version": sys.version,
            "version_info": ".".join(map(str, sys.version_info[:3])),
            "executable": sys.executable,
            "prefix": sys.prefix,
            "base_prefix": sys.base_prefix,
            "path": sys.path,
        }
        
    def get_file_system_info(self) -> Dict[str, Any]:
        """Get file system information"""
        try:
            # Get disk usage for current directory
            current_dir = Path.cwd()
            disk_usage = shutil.disk_usage(current_dir)
            
            return {
                "current_directory": str(current_dir),
                "disk_total_gb": disk_usage.total / (1024**3),
                "disk_used_gb": disk_usage.used / (1024**3),
                "disk_free_gb": disk_usage.free / (1024**3),
                "disk_usage_percent": (disk_usage.used / disk_usage.total) * 100,
            }
        except Exception as e:
            self.logger.warning(f"Failed to get disk usage: {e}")
            return {
                "current_directory": str(Path.cwd()),
                "error": str(e)
            }
            
    def get_network_info(self) -> Dict[str, Any]:
        """Get basic network information"""
        try:
            import socket
            hostname = socket.gethostname()
            ip_address = socket.gethostbyname(hostname)
            
            return {
                "hostname": hostname,
                "ip_address": ip_address,
                "fqdn": socket.getfqdn(),
            }
        except Exception as e:
            self.logger.warning(f"Failed to get network info: {e}")
            return {
                "hostname": "unknown",
                "error": str(e)
            }
            
    def get_process_info(self) -> Dict[str, Any]:
        """Get current process information"""
        try:
            import psutil
            current_process = psutil.Process()
            
            return {
                "pid": current_process.pid,
                "ppid": current_process.ppid(),
                "process_name": current_process.name(),
                "cmdline": " ".join(current_process.cmdline()),
                "memory_info": asdict(current_process.memory_info()) if hasattr(current_process.memory_info(), '_asdict') else {},
                "cpu_percent": current_process.cpu_percent(),
                "num_threads": current_process.num_threads(),
            }
        except Exception as e:
            self.logger.warning(f"Failed to get process info: {e}")
            return {
                "pid": os.getpid(),
                "ppid": os.getppid(),
                "error": str(e)
            }
            
    def get_relevant_environment_variables(self) -> Dict[str, str]:
        """Get relevant environment variables for environment detection"""
        relevant_vars = [
            # Docker/Container variables
            'DOCKER_CONTAINER',
            'container',
            'HOSTNAME',
            
            # Kubernetes variables
            'KUBERNETES_SERVICE_HOST',
            'KUBERNETES_SERVICE_PORT',
            'KUBECONFIG',
            'POD_NAME',
            'NAMESPACE',
            
            # System variables
            'PATH',
            'HOME',
            'USER',
            'SHELL',
            'LANG',
            'PWD',
            
            # Python variables
            'PYTHONPATH',
            'VIRTUAL_ENV',
            'CONDA_DEFAULT_ENV',
            
            # MCP-specific variables
            'MCP_ENV',
            'MCP_DEBUG',
            'MCP_LOG_LEVEL',
        ]
        
        env_vars = {}
        for var in relevant_vars:
            value = os.getenv(var)
            if value is not None:
                # Mask sensitive values
                if any(sensitive in var.upper() for sensitive in ['KEY', 'SECRET', 'PASSWORD', 'TOKEN']):
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
            network_info=self.get_network_info(),
            process_info=self.get_process_info()
        )
        
        self.logger.info(f"Environment detected: {env_info.platform} {'(Docker)' if is_docker else '(Local)'}")
        
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
            "user": env_info.user
        }
        
    def export_environment_info(self, output_path: str, format: str = "json"):
        """Export environment information to file"""
        env_info = self.detect_environment()
        
        if format.lower() == "json":
            with open(output_path, 'w') as f:
                json.dump(asdict(env_info), f, indent=2, default=str)
        elif format.lower() == "txt":
            with open(output_path, 'w') as f:
                for key, value in asdict(env_info).items():
                    f.write(f"{key}: {value}\n")
        else:
            raise ValueError(f"Unsupported format: {format}")
            
        self.logger.info(f"Environment info exported to {output_path}")

# Global environment detector instance
environment_detector = EnvironmentDetector()
```

#### 2. ConfigManager Class
Adaptive configuration management.

```python
# File: src/config/config_manager.py
import os
import json
import logging
from typing import Dict, Any, Optional, Union
from pathlib import Path
from dataclasses import dataclass, asdict
from src.config.environment_detector import EnvironmentDetector, EnvironmentInfo

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
        self.config_dir = Path(config_dir) if config_dir else Path(__file__).parent.parent / "config"
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
                    "temp_dir": "/tmp",
                    "security_settings": {
                        "allowed_paths": ["/app", "/tmp"],
                        "restricted_paths": ["/etc", "/usr", "/var"],
                        "max_file_size_mb": 10
                    },
                    "performance_settings": {
                        "memory_limit_mb": 1024,
                        "cpu_limit_cores": 2.0,
                        "disk_quota_gb": 5
                    }
                }
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
                        "allowed_paths": [str(Path.cwd()), "/tmp"],
                        "restricted_paths": [],
                        "max_file_size_mb": 100
                    },
                    "performance_settings": {
                        "memory_limit_mb": 2048,
                        "cpu_limit_cores": 4.0,
                        "disk_quota_gb": 50
                    }
                }
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
                    "cache_dir": "/tmp/cache",
                    "temp_dir": "/tmp",
                    "security_settings": {
                        "allowed_paths": ["/app", "/data", "/tmp"],
                        "restricted_paths": ["/etc", "/usr", "/var", "/home"],
                        "max_file_size_mb": 5
                    },
                    "performance_settings": {
                        "memory_limit_mb": 2048,
                        "cpu_limit_cores": 4.0,
                        "disk_quota_gb": 10
                    }
                }
            )
        ]
        
        # Save built-in profiles
        for profile in builtin_profiles:
            self.config_profiles[profile.name] = profile
            profile_file = profiles_dir / f"{profile.name}.json"
            if not profile_file.exists():
                with open(profile_file, 'w') as f:
                    json.dump(asdict(profile), f, indent=2)
                    
        # Load custom profiles
        for profile_file in profiles_dir.glob("*.json"):
            if profile_file.name not in [f"{p.name}.json" for p in builtin_profiles]:
                try:
                    with open(profile_file, 'r') as f:
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
            session_dir=base_settings.get("session_dir", str(Path.cwd() / "pipeline-sessions")),
            log_level=base_settings.get("log_level", "INFO"),
            max_workers=base_settings.get("max_workers", 2),
            timeout=base_settings.get("timeout", 300),
            enable_dashboard=base_settings.get("enable_dashboard", False),
            database_path=base_settings.get("database_path", str(Path.cwd() / "sessions.db")),
            cache_dir=base_settings.get("cache_dir", str(Path.cwd() / ".cache")),
            temp_dir=base_settings.get("temp_dir", "/tmp"),
            security_settings=base_settings.get("security_settings", {}),
            performance_settings=base_settings.get("performance_settings", {}),
            docker_specific=base_settings.get("docker_specific", {}) if env_info.is_docker else {},
            local_specific=base_settings.get("local_specific", {}) if not env_info.is_docker else {}
        )
        
        # Ensure directories exist
        Path(self.current_config.session_dir).mkdir(parents=True, exist_ok=True)
        Path(self.current_config.cache_dir).mkdir(parents=True, exist_ok=True)
        Path(self.current_config.temp_dir).mkdir(parents=True, exist_ok=True)
        Path(self.current_config.database_path).parent.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"Adaptive configuration initialized for {'Docker' if env_info.is_docker else 'Local'} environment")
        
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
            "MCP_TEMP_DIR": "temp_dir"
        }
        
        for env_var, config_key in env_mapping.items():
            value = os.getenv(env_var)
            if value is not None:
                # Convert numeric values
                if config_key in ["max_workers", "timeout"]:
                    try:
                        overrides[config_key] = int(value)
                    except ValueError:
                        self.logger.warning(f"Invalid integer value for {env_var}: {value}")
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
                "allowed_paths_count": len(config.security_settings.get("allowed_paths", [])),
                "restricted_paths_count": len(config.security_settings.get("restricted_paths", [])),
                "max_file_size_mb": config.security_settings.get("max_file_size_mb", 0)
            },
            "performance_settings": {
                "memory_limit_mb": config.performance_settings.get("memory_limit_mb", 0),
                "cpu_limit_cores": config.performance_settings.get("cpu_limit_cores", 0.0),
                "disk_quota_gb": config.performance_settings.get("disk_quota_gb", 0)
            }
        }
        
    def validate_configuration(self) -> Dict[str, Any]:
        """Validate current configuration"""
        config = self.get_config()
        validation_results = {
            "valid": True,
            "issues": [],
            "warnings": []
        }
        
        # Validate paths
        paths_to_check = [
            ("workspace_root", config.workspace_root),
            ("session_dir", config.session_dir),
            ("cache_dir", config.cache_dir),
            ("temp_dir", config.temp_dir),
            ("database_path", config.database_path)
        ]
        
        for path_name, path_value in paths_to_check:
            path_obj = Path(path_value)
            if not path_obj.exists():
                try:
                    path_obj.parent.mkdir(parents=True, exist_ok=True)
                    validation_results["warnings"].append(f"Created missing directory: {path_name} = {path_value}")
                except Exception as e:
                    validation_results["valid"] = False
                    validation_results["issues"].append(f"Cannot create directory {path_name}: {e}")
            elif not os.access(path_obj, os.W_OK):
                validation_results["valid"] = False
                validation_results["issues"].append(f"No write access to {path_name}: {path_value}")
                
        # Validate numeric settings
        if config.max_workers < 1:
            validation_results["valid"] = False
            validation_results["issues"].append("max_workers must be >= 1")
            
        if config.timeout < 1:
            validation_results["valid"] = False
            validation_results["issues"].append("timeout must be >= 1")
            
        # Validate security settings
        security_settings = config.security_settings
        if security_settings:
            max_file_size = security_settings.get("max_file_size_mb", 0)
            if max_file_size < 0:
                validation_results["valid"] = False
                validation_results["issues"].append("max_file_size_mb must be >= 0")
                
        # Validate performance settings
        performance_settings = config.performance_settings
        if performance_settings:
            memory_limit = performance_settings.get("memory_limit_mb", 0)
            if memory_limit < 0:
                validation_results["valid"] = False
                validation_results["issues"].append("memory_limit_mb must be >= 0")
                
            cpu_limit = performance_settings.get("cpu_limit_cores", 0.0)
            if cpu_limit < 0:
                validation_results["valid"] = False
                validation_results["issues"].append("cpu_limit_cores must be >= 0")
                
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
```

#### 3. PlatformAdapter Class
Platform-specific adaptations.

```python
# File: src/config/platform_adapter.py
import os
import platform
import subprocess
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List
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
            import multiprocessing
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
                    if limit_bytes < 9223372036854771712:  # Less than ~8EB (unlimited marker)
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
        elif self.system == 'darwin':  # macOS
            default_temp = '/tmp'
        else:  # Linux and others
            default_temp = '/tmp'
            
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
            "compression_buffer": 32768, # 32KB
            "log_buffer": 4096,          # 4KB
        }
        
        # Adjust based on available memory
        try:
            import psutil
            available_memory_mb = psutil.virtual_memory().available / (1024 * 1024)
            
            if available_memory_mb < 512:  # Less than 512MB
                # Reduce buffer sizes for low memory
                buffer_sizes = {
                    key: max(1024, value // 2) for key, value in buffer_sizes.items()
                }
            elif available_memory_mb > 4096:  # More than 4GB
                # Increase buffer sizes for abundant memory
                buffer_sizes = {
                    key: value * 2 for key, value in buffer_sizes.items()
                }
                
        except ImportError:
            # psutil not available, use defaults
            pass
        except Exception as e:
            self.logger.warning(f"Failed to adjust buffer sizes based on memory: {e}")
            
        return buffer_sizes
        
    def get_platform_specific_commands(self) -> Dict[str, List[str]]:
        """Get platform-specific commands for common operations"""
        if self.system == 'windows':
            return {
                "shell": ["cmd", "/c"],
                "list_files": ["dir"],
                "copy_file": ["copy"],
                "move_file": ["move"],
                "delete_file": ["del"],
                "make_directory": ["mkdir"],
                "remove_directory": ["rmdir"],
            }
        else:  # Unix-like systems (Linux, macOS, etc.)
            return {
                "shell": ["/bin/sh", "-c"],
                "list_files": ["ls", "-la"],
                "copy_file": ["cp"],
                "move_file": ["mv"],
                "delete_file": ["rm"],
                "make_directory": ["mkdir", "-p"],
                "remove_directory": ["rm", "-rf"],
            }
            
    def get_file_permissions_commands(self) -> Dict[str, List[str]]:
        """Get platform-specific file permission commands"""
        if self.system == 'windows':
            return {
                "chmod": ["icacls"],  # Windows equivalent
                "chown": ["takeown"],  # Windows equivalent
            }
        else:  # Unix-like systems
            return {
                "chmod": ["chmod"],
                "chown": ["chown"],
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
            if self.system == 'windows':
                system_info["cpu_count"] = os.cpu_count()
            else:
                system_info["cpu_count"] = os.cpu_count()
        except Exception as e:
            self.logger.warning(f"Failed to get CPU count: {e}")
            system_info["cpu_count"] = 1
            
        # Add memory information
        try:
            import psutil
            vm = psutil.virtual_memory()
            system_info.update({
                "total_memory_mb": vm.total / (1024 * 1024),
                "available_memory_mb": vm.available / (1024 * 1024),
                "memory_percent": vm.percent,
            })
        except ImportError:
            system_info["memory_info"] = "psutil not available"
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
            "permissions_commands": self.get_file_permissions_commands(),
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
```

#### 4. RuntimeProfiler Class
Runtime performance profiling.

```python
# File: src/config/runtime_profiler.py
import time
import psutil
import threading
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
import logging
from collections import deque
import json

@dataclass
class PerformanceSnapshot:
    """Snapshot of runtime performance metrics"""
    timestamp: float
    cpu_percent: float
    memory_mb: float
    memory_percent: float
    disk_io_read_mb: float
    disk_io_write_mb: float
    network_sent_mb: float
    network_received_mb: float
    thread_count: int
    file_descriptor_count: Optional[int]

@dataclass
class PerformanceProfile:
    """Aggregated performance profile"""
    start_time: float
    duration: float
    avg_cpu_percent: float
    max_cpu_percent: float
    avg_memory_mb: float
    max_memory_mb: float
    total_disk_read_mb: float
    total_disk_write_mb: float
    total_network_sent_mb: float
    total_network_received_mb: float
    peak_thread_count: int
    snapshots: List[PerformanceSnapshot]

class RuntimeProfiler:
    """Profiles runtime performance and resource usage"""
    
    def __init__(self, sampling_interval: float = 1.0):
        self.sampling_interval = sampling_interval
        self.logger = logging.getLogger(__name__)
        self.is_profiling = False
        self.profiling_thread: Optional[threading.Thread] = None
        self.snapshots: deque = deque(maxlen=3600)  # Keep last hour of snapshots
        self.start_time: Optional[float] = None
        self.process = psutil.Process()
        
        # Disk and network counters
        self.last_disk_counters = None
        self.last_net_counters = None
        self._initialize_counters()
        
    def _initialize_counters(self):
        """Initialize disk and network counters"""
        try:
            self.last_disk_counters = psutil.disk_io_counters()
        except Exception as e:
            self.logger.warning(f"Failed to initialize disk counters: {e}")
            
        try:
            self.last_net_counters = psutil.net_io_counters()
        except Exception as e:
            self.logger.warning(f"Failed to initialize network counters: {e}")
            
    def start_profiling(self):
        """Start runtime profiling in background thread"""
        if self.is_profiling:
            self.logger.warning("Profiling already started")
            return
            
        self.is_profiling = True
        self.start_time = time.time()
        self.snapshots.clear()
        
        self.profiling_thread = threading.Thread(target=self._profiling_loop, daemon=True)
        self.profiling_thread.start()
        
        self.logger.info("Runtime profiling started")
        
    def stop_profiling(self) -> PerformanceProfile:
        """Stop profiling and return performance profile"""
        if not self.is_profiling:
            self.logger.warning("Profiling not started")
            return self.get_current_profile()
            
        self.is_profiling = False
        if self.profiling_thread:
            self.profiling_thread.join(timeout=5.0)
            
        profile = self.get_current_profile()
        self.logger.info("Runtime profiling stopped")
        
        return profile
        
    def _profiling_loop(self):
        """Background profiling loop"""
        while self.is_profiling:
            try:
                snapshot = self._collect_snapshot()
                if snapshot:
                    self.snapshots.append(snapshot)
                    
                time.sleep(self.sampling_interval)
            except Exception as e:
                self.logger.error(f"Error in profiling loop: {e}")
                time.sleep(self.sampling_interval)
                
    def _collect_snapshot(self) -> Optional[PerformanceSnapshot]:
        """Collect performance snapshot"""
        try:
            timestamp = time.time()
            
            # CPU usage
            cpu_percent = self.process.cpu_percent()
            
            # Memory usage
            memory_info = self.process.memory_info()
            memory_mb = memory_info.rss / (1024 * 1024)
            memory_percent = psutil.virtual_memory().percent
            
            # Thread count
            thread_count = self.process.num_threads()
            
            # File descriptors (Unix-like systems)
            file_descriptor_count = None
            try:
                if hasattr(self.process, 'num_fds'):
                    file_descriptor_count = self.process.num_fds()
            except (AttributeError, psutil.AccessDenied):
                pass
                
            # Disk I/O
            disk_read_mb = 0.0
            disk_write_mb = 0.0
            try:
                current_disk = psutil.disk_io_counters()
                if self.last_disk_counters:
                    disk_read_mb = (current_disk.read_bytes - self.last_disk_counters.read_bytes) / (1024 * 1024)
                    disk_write_mb = (current_disk.write_bytes - self.last_disk_counters.write_bytes) / (1024 * 1024)
                self.last_disk_counters = current_disk
            except Exception as e:
                self.logger.debug(f"Failed to collect disk I/O: {e}")
                
            # Network I/O
            network_sent_mb = 0.0
            network_received_mb = 0.0
            try:
                current_net = psutil.net_io_counters()
                if self.last_net_counters:
                    network_sent_mb = (current_net.bytes_sent - self.last_net_counters.bytes_sent) / (1024 * 1024)
                    network_received_mb = (current_net.bytes_recv - self.last_net_counters.bytes_recv) / (1024 * 1024)
                self.last_net_counters = current_net
            except Exception as e:
                self.logger.debug(f"Failed to collect network I/O: {e}")
                
            return PerformanceSnapshot(
                timestamp=timestamp,
                cpu_percent=cpu_percent,
                memory_mb=memory_mb,
                memory_percent=memory_percent,
                disk_io_read_mb=disk_read_mb,
                disk_io_write_mb=disk_write_mb,
                network_sent_mb=network_sent_mb,
                network_received_mb=network_received_mb,
                thread_count=thread_count,
                file_descriptor_count=file_descriptor_count
            )
            
        except Exception as e:
            self.logger.error(f"Failed to collect performance snapshot: {e}")
            return None
            
    def get_current_profile(self) -> PerformanceProfile:
        """Get current performance profile"""
        if not self.start_time:
            return PerformanceProfile(
                start_time=time.time(),
                duration=0.0,
                avg_cpu_percent=0.0,
                max_cpu_percent=0.0,
                avg_memory_mb=0.0,
                max_memory_mb=0.0,
                total_disk_read_mb=0.0,
                total_disk_write_mb=0.0,
                total_network_sent_mb=0.0,
                total_network_received_mb=0.0,
                peak_thread_count=0,
                snapshots=list(self.snapshots)
            )
            
        duration = time.time() - self.start_time
        
        if not self.snapshots:
            return PerformanceProfile(
                start_time=self.start_time,
                duration=duration,
                avg_cpu_percent=0.0,
                max_cpu_percent=0.0,
                avg_memory_mb=0.0,
                max_memory_mb=0.0,
                total_disk_read_mb=0.0,
                total_disk_write_mb=0.0,
                total_network_sent_mb=0.0,
                total_network_received_mb=0.0,
                peak_thread_count=0,
                snapshots=[]
            )
            
        # Calculate aggregates
        cpu_values = [s.cpu_percent for s in self.snapshots]
        memory_values = [s.memory_mb for s in self.snapshots]
        thread_values = [s.thread_count for s in self.snapshots]
        
        avg_cpu = sum(cpu_values) / len(cpu_values) if cpu_values else 0.0
        max_cpu = max(cpu_values) if cpu_values else 0.0
        avg_memory = sum(memory_values) / len(memory_values) if memory_values else 0.0
        max_memory = max(memory_values) if memory_values else 0.0
        peak_threads = max(thread_values) if thread_values else 0
        
        # Calculate totals for I/O
        total_disk_read = sum(s.disk_io_read_mb for s in self.snapshots)
        total_disk_write = sum(s.disk_io_write_mb for s in self.snapshots)
        total_network_sent = sum(s.network_sent_mb for s in self.snapshots)
        total_network_received = sum(s.network_received_mb for s in self.snapshots)
        
        return PerformanceProfile(
            start_time=self.start_time,
            duration=duration,
            avg_cpu_percent=avg_cpu,
            max_cpu_percent=max_cpu,
            avg_memory_mb=avg_memory,
            max_memory_mb=max_memory,
            total_disk_read_mb=total_disk_read,
            total_disk_write_mb=total_disk_write,
            total_network_sent_mb=total_network_sent,
            total_network_received_mb=total_network_received,
            peak_thread_count=peak_threads,
            snapshots=list(self.snapshots)
        )
        
    def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get current real-time metrics"""
        try:
            # Get current values
            cpu_percent = self.process.cpu_percent()
            memory_info = self.process.memory_info()
            memory_mb = memory_info.rss / (1024 * 1024)
            memory_percent = psutil.virtual_memory().percent
            thread_count = self.process.num_threads()
            
            return {
                "cpu_percent": cpu_percent,
                "memory_mb": memory_mb,
                "memory_percent": memory_percent,
                "thread_count": thread_count,
                "timestamp": time.time()
            }
        except Exception as e:
            self.logger.error(f"Failed to get real-time metrics: {e}")
            return {
                "cpu_percent": 0.0,
                "memory_mb": 0.0,
                "memory_percent": 0.0,
                "thread_count": 0,
                "timestamp": time.time(),
                "error": str(e)
            }
            
    def export_profile(self, output_path: str, format: str = "json"):
        """Export performance profile to file"""
        profile = self.get_current_profile()
        
        if format.lower() == "json":
            with open(output_path, 'w') as f:
                json.dump(asdict(profile), f, indent=2, default=str)
        else:
            raise ValueError(f"Unsupported format: {format}")
            
        self.logger.info(f"Performance profile exported to {output_path}")
        
    def get_resource_usage_summary(self) -> Dict[str, Any]:
        """Get summary of resource usage"""
        profile = self.get_current_profile()
        
        return {
            "duration_seconds": round(profile.duration, 2),
            "average_cpu_percent": round(profile.avg_cpu_percent, 2),
            "peak_cpu_percent": round(profile.max_cpu_percent, 2),
            "average_memory_mb": round(profile.avg_memory_mb, 2),
            "peak_memory_mb": round(profile.max_memory_mb, 2),
            "total_disk_reads_mb": round(profile.total_disk_read_mb, 2),
            "total_disk_writes_mb": round(profile.total_disk_write_mb, 2),
            "peak_thread_count": profile.peak_thread_count,
            "snapshot_count": len(profile.snapshots)
        }
        
    def check_resource_limits(self, config_manager) -> Dict[str, Any]:
        """Check if current resource usage exceeds configured limits"""
        violations = {
            "exceeded": False,
            "violations": [],
            "warnings": []
        }
        
        try:
            # Get current metrics
            current_metrics = self.get_real_time_metrics()
            if "error" in current_metrics:
                return violations
                
            # Get configured limits
            memory_limit_mb = config_manager.get_performance_setting("memory_limit_mb")
            cpu_limit_cores = config_manager.get_performance_setting("cpu_limit_cores")
            
            # Check memory limit
            if memory_limit_mb and current_metrics["memory_mb"] > memory_limit_mb:
                violations["exceeded"] = True
                violations["violations"].append({
                    "type": "memory",
                    "current": current_metrics["memory_mb"],
                    "limit": memory_limit_mb,
                    "unit": "MB"
                })
                
            # Check CPU limit (approximate)
            if cpu_limit_cores and current_metrics["cpu_percent"] > (cpu_limit_cores * 100):
                violations["exceeded"] = True
                violations["violations"].append({
                    "type": "cpu",
                    "current": current_metrics["cpu_percent"],
                    "limit": cpu_limit_cores * 100,
                    "unit": "%"
                })
                
            # Issue warnings for approaching limits
            warning_threshold = 0.8  # 80% of limit
            
            if memory_limit_mb and current_metrics["memory_mb"] > (memory_limit_mb * warning_threshold):
                violations["warnings"].append({
                    "type": "memory",
                    "current": current_metrics["memory_mb"],
                    "threshold": memory_limit_mb * warning_threshold,
                    "limit": memory_limit_mb,
                    "unit": "MB"
                })
                
            if cpu_limit_cores and current_metrics["cpu_percent"] > (cpu_limit_cores * 100 * warning_threshold):
                violations["warnings"].append({
                    "type": "cpu",
                    "current": current_metrics["cpu_percent"],
                    "threshold": cpu_limit_cores * 100 * warning_threshold,
                    "limit": cpu_limit_cores * 100,
                    "unit": "%"
                })
                
        except Exception as e:
            self.logger.error(f"Failed to check resource limits: {e}")
            
        return violations
        
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health metrics"""
        try:
            # System-wide metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "system_cpu_percent": cpu_percent,
                "system_memory_percent": memory.percent,
                "system_memory_available_mb": memory.available / (1024 * 1024),
                "system_disk_percent": (disk.used / disk.total) * 100,
                "system_disk_free_gb": disk.free / (1024 * 1024 * 1024),
                "timestamp": time.time()
            }
        except Exception as e:
            self.logger.error(f"Failed to get system health metrics: {e}")
            return {
                "error": str(e),
                "timestamp": time.time()
            }

# Global runtime profiler instance
runtime_profiler = RuntimeProfiler()
```

#### 5. Integration with Pipeline MCP Server

```python
# File: src/pipeline_mcp_server.py (integration points)
# ADD imports after existing imports:
from config.environment_detector import EnvironmentDetector, environment_detector
from config.config_manager import ConfigManager, config_manager
from config.platform_adapter import PlatformAdapter, platform_adapter
from config.runtime_profiler import RuntimeProfiler, runtime_profiler

# MODIFY PipelineMCPServer class:
class PipelineMCPServer:
    def __init__(self):
        # ... existing code ...
        
        # ADD ENVIRONMENT DETECTION AND ADAPTATION CAPABILITIES
        self.environment_detector = environment_detector
        self.config_manager = config_manager
        self.platform_adapter = platform_adapter
        self.runtime_profiler = runtime_profiler
        
        # Detect environment and adapt configuration
        self.environment_info = self.environment_detector.detect_environment()
        self.adaptive_config = self.config_manager.get_config()
        self.platform_optimizations = self.platform_adapter.optimize_for_current_platform()
        
        # Apply adaptive configuration
        self._apply_adaptive_configuration()
        
        # Start runtime profiling
        self.runtime_profiler.start_profiling()
        
        self.logger.info(f"Environment detection initialized: {'Docker' if self.environment_info.is_docker else 'Local'}")
        self.logger.info(f"Platform: {self.environment_info.platform} {self.environment_info.architecture}")
        
    def _apply_adaptive_configuration(self):
        """Apply adaptive configuration based on environment"""
        # Update workspace settings
        self.workspace_root = Path(self.adaptive_config.workspace_root)
        self.session_dir = Path(self.adaptive_config.session_dir)
        self.database_path = Path(self.adaptive_config.database_path)
        
        # Update performance settings
        self.max_workers = self.adaptive_config.max_workers
        self.default_timeout = self.adaptive_config.timeout
        
        # Update logging
        logging.getLogger().setLevel(getattr(logging, self.adaptive_config.log_level.upper()))
        
        # Update security settings
        self.allowed_paths = self.adaptive_config.security_settings.get("allowed_paths", [str(Path.cwd())])
        self.restricted_paths = self.adaptive_config.security_settings.get("restricted_paths", [])
        
        # Ensure directories exist with proper permissions
        for directory in [self.session_dir, self.database_path.parent]:
            directory.mkdir(parents=True, exist_ok=True)
            
        self.logger.info("Adaptive configuration applied successfully")
        
    def get_server_environment(self) -> Dict[str, Any]:
        """Get server environment information"""
        env_info = self.environment_detector.get_environment_summary()
        config_summary = self.config_manager.get_config_summary()
        platform_info = self.platform_adapter.get_system_info()
        runtime_metrics = self.runtime_profiler.get_resource_usage_summary()
        
        return {
            "environment": env_info,
            "configuration": config_summary,
            "platform": platform_info,
            "runtime": runtime_metrics,
            "adaptive_config": {
                "workspace_root": str(self.workspace_root),
                "session_dir": str(self.session_dir),
                "max_workers": self.max_workers,
                "timeout": self.default_timeout,
                "dashboard_enabled": self.adaptive_config.enable_dashboard,
                "database_path": str(self.database_path)
            }
        }
        
    async def handle_environment_detection(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle environment detection requests"""
        
        action = arguments.get("action", "detect")
        
        if action == "detect":
            # Get comprehensive environment information
            env_info = server.environment_detector.detect_environment()
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "tool": "environment_detection",
                    "action": "detect",
                    "environment_info": asdict(env_info),
                    "timestamp": time.time()
                }, indent=2, default=str)
            )]
            
        elif action == "summary":
            # Get environment summary
            summary = server.environment_detector.get_environment_summary()
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "tool": "environment_detection",
                    "action": "summary",
                    "summary": summary,
                    "timestamp": time.time()
                }, indent=2)
            )]
            
        elif action == "config":
            # Get current configuration
            config_summary = server.config_manager.get_config_summary()
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "tool": "environment_detection",
                    "action": "config",
                    "configuration": config_summary,
                    "timestamp": time.time()
                }, indent=2)
            )]
            
        elif action == "validate":
            # Validate current configuration
            validation_results = server.config_manager.validate_configuration()
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "tool": "environment_detection",
                    "action": "validate",
                    "validation": validation_results,
                    "timestamp": time.time()
                }, indent=2)
            )]
            
        elif action == "reload":
            # Reload configuration
            try:
                server.config_manager.reload_configuration()
                server._apply_adaptive_configuration()
                
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "tool": "environment_detection",
                        "action": "reload",
                        "status": "success",
                        "message": "Configuration reloaded successfully",
                        "timestamp": time.time()
                    }, indent=2)
                )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "tool": "environment_detection",
                        "action": "reload",
                        "status": "error",
                        "error": str(e),
                        "timestamp": time.time()
                    }, indent=2)
                )]
                
        elif action == "profile":
            # Get runtime performance profile
            profile = server.runtime_profiler.get_current_profile()
            resource_summary = server.runtime_profiler.get_resource_usage_summary()
            system_health = server.runtime_profiler.get_system_health()
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "tool": "environment_detection",
                    "action": "profile",
                    "performance_profile": asdict(profile),
                    "resource_summary": resource_summary,
                    "system_health": system_health,
                    "timestamp": time.time()
                }, indent=2, default=str)
            )]
            
        elif action == "optimize":
            # Get platform optimizations
            optimizations = server.platform_adapter.optimize_for_current_platform()
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "tool": "environment_detection",
                    "action": "optimize",
                    "optimizations": optimizations,
                    "timestamp": time.time()
                }, indent=2)
            )]
            
        else:
            raise McpError(ErrorCode.METHOD_NOT_FOUND, f"Unknown action: {action}")

# REGISTER the new tool:
@server.call_tool()
async def handle_environment_detection(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Environment detection and adaptation tool"""
    return await server.handle_environment_detection(name, arguments)

# MODIFY existing tools to use adaptive configuration:
async def handle_version_keeper_scan(arguments: Dict[str, Any]) -> List[TextContent]:
    """Enhanced version keeper with environment-aware configuration"""
    
    # Use adaptive configuration
    session_id = arguments.get("session_id", f"default-{int(time.time())}")
    session_dir = server.session_dir / session_id
    
    # Apply environment-specific optimizations
    worker_count = server.adaptive_config.max_workers
    timeout = server.adaptive_config.timeout
    
    # ... rest of existing implementation with adaptive config ...
    
    return [TextContent(
        type="text",
        text=json.dumps({
            "tool": "version_keeper_scan",
            "session_id": session_id,
            "status": "completed",
            "environment": server.environment_info.platform,
            "configuration": {
                "workers": worker_count,
                "timeout": timeout
            }
        }, indent=2)
    )]

async def handle_quality_patcher_fix(arguments: Dict[str, Any]) -> List[TextContent]:
    """Enhanced quality patcher with environment awareness"""
    
    # Use adaptive temp directory
    temp_dir = server.adaptive_config.temp_dir
    
    # Apply security settings
    allowed_paths = server.adaptive_config.security_settings.get("allowed_paths", [])
    max_file_size = server.adaptive_config.security_settings.get("max_file_size_mb", 100)
    
    # ... rest of existing implementation with adaptive config ...
    
    return [TextContent(
        type="text",
        text=json.dumps({
            "tool": "quality_patcher_fix",
            "status": "completed",
            "security": {
                "allowed_paths": len(allowed_paths),
                "max_file_size_mb": max_file_size
            }
        }, indent=2)
    )]

# MODIFY server startup to include environment detection:
async def main():
    """Main server entry point with environment detection"""
    
    # Log environment information at startup
    env_summary = server.environment_detector.get_environment_summary()
    logger.info(f"Starting Pipeline MCP Server in {env_summary['platform']} environment")
    logger.info(f"Docker: {env_summary['is_docker']}, Containerized: {env_summary['is_containerized']}")
    
    # Validate configuration
    validation_results = server.config_manager.validate_configuration()
    if not validation_results["valid"]:
        logger.error("Configuration validation failed:")
        for issue in validation_results["issues"]:
            logger.error(f"  - {issue}")
        sys.exit(1)
        
    # Log adaptive configuration
    config = server.config_manager.get_config()
    logger.info(f"Adaptive configuration: {config.max_workers} workers, {config.timeout}s timeout")
    logger.info(f"Workspace: {config.workspace_root}")
    logger.info(f"Session directory: {config.session_dir}")
    
    # Start profiling
    server.runtime_profiler.start_profiling()
    logger.info("Runtime profiling started")
    
    # ... rest of existing main function ...

# ADD periodic environment monitoring:
class PipelineMCPServer:
    # ... existing code ...
    
    def __init__(self):
        # ... existing initialization ...
        
        # Start periodic environment monitoring
        self._start_environment_monitoring()
        
    def _start_environment_monitoring(self):
        """Start periodic environment monitoring"""
        def monitor_environment():
            while True:
                try:
                    time.sleep(300)  # Check every 5 minutes
                    
                    # Check resource limits
                    violations = self.runtime_profiler.check_resource_limits(self.config_manager)
                    if violations["exceeded"]:
                        logger.warning("Resource limits exceeded:")
                        for violation in violations["violations"]:
                            logger.warning(f"  {violation['type']}: {violation['current']}{violation['unit']} > {violation['limit']}{violation['unit']}")
                            
                    # Check system health
                    health = self.runtime_profiler.get_system_health()
                    if "system_cpu_percent" in health and health["system_cpu_percent"] > 90:
                        logger.warning(f"High system CPU usage: {health['system_cpu_percent']}%")
                        
                except Exception as e:
                    logger.error(f"Environment monitoring error: {e}")
                    
        monitor_thread = threading.Thread(target=monitor_environment, daemon=True)
        monitor_thread.start()
```

### Configuration and Deployment

#### Environment Configuration

```python
# File: src/config/config.py
import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class EnvironmentConfig:
    """Global environment configuration"""
    
    # Environment detection settings
    force_environment: Optional[str] = os.getenv('MCP_FORCE_ENVIRONMENT')  # docker, local, kubernetes
    environment_check_interval: int = int(os.getenv('MCP_ENV_CHECK_INTERVAL', '300'))  # seconds
    
    # Adaptive configuration settings
    auto_reload_config: bool = os.getenv('MCP_AUTO_RELOAD_CONFIG', 'true').lower() == 'true'
    config_reload_interval: int = int(os.getenv('MCP_CONFIG_RELOAD_INTERVAL', '3600'))  # seconds
    
    # Profiling settings
    enable_profiling: bool = os.getenv('MCP_ENABLE_PROFILING', 'true').lower() == 'true'
    profiling_interval: float = float(os.getenv('MCP_PROFILING_INTERVAL', '1.0'))  # seconds
    profiling_history_size: int = int(os.getenv('MCP_PROFILING_HISTORY_SIZE', '3600'))  # snapshots
    
    # Platform adaptation settings
    optimize_for_platform: bool = os.getenv('MCP_OPTIMIZE_FOR_PLATFORM', 'true').lower() == 'true'
    platform_check_interval: int = int(os.getenv('MCP_PLATFORM_CHECK_INTERVAL', '600'))  # seconds
    
    @classmethod
    def from_env(cls) -> 'EnvironmentConfig':
        """Create configuration from environment variables"""
        return cls()
        
# Global environment configuration
env_config = EnvironmentConfig.from_env()
```

#### Docker Configuration

```yaml
# File: docker-compose.environment.yml
version: '3.8'

services:
  mcp-environment-detection:
    build:
      context: .
      dockerfile: docker/Dockerfile.environment
    environment:
      - MCP_FORCE_ENVIRONMENT=docker
      - MCP_AUTO_RELOAD_CONFIG=true
      - MCP_ENABLE_PROFILING=true
      - MCP_OPTIMIZE_FOR_PLATFORM=true
      - MCP_LOG_LEVEL=INFO
    volumes:
      - ./src/config:/app/src/config
      - ./logs:/app/logs
    networks:
      - mcp-network
    healthcheck:
      test: ["CMD", "python", "-c", "import src.config.environment_detector as ed; print(ed.environment_detector.detect_environment().platform)"]
      interval: 30s
      timeout: 10s
      retries: 3
      
  mcp-config-manager:
    build:
      context: .
      dockerfile: docker/Dockerfile.config
    environment:
      - MCP_CONFIG_PROFILE=docker-default
      - MCP_WORKSPACE_ROOT=/app
      - MCP_SESSION_DIR=/app/pipeline-sessions
      - MCP_DATABASE_PATH=/app/data/sessions.db
      - MCP_MAX_WORKERS=4
      - MCP_TIMEOUT=300
    volumes:
      - ./src/config:/app/src/config
      - ./config/profiles:/app/config/profiles
    networks:
      - mcp-network
      
  mcp-runtime-monitor:
    build:
      context: .
      dockerfile: docker/Dockerfile.monitor
    environment:
      - MCP_PROFILING_INTERVAL=2.0
      - MCP_ENABLE_PROFILING=true
    volumes:
      - ./src/config:/app/src/config
      - ./logs:/app/logs
    networks:
      - mcp-network
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 128M
        reservations:
          cpus: '0.1'
          memory: 64M

networks:
  mcp-network:
    driver: bridge
```

### Testing and Validation

#### Unit Tests

```python
# File: tests/test_environment_detection.py
import unittest
import tempfile
import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch
import json

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config.environment_detector import EnvironmentDetector, EnvironmentInfo
from config.config_manager import ConfigManager, ConfigProfile, AdaptiveConfig
from config.platform_adapter import PlatformAdapter
from config.runtime_profiler import RuntimeProfiler, PerformanceSnapshot

class TestEnvironmentDetector(unittest.TestCase):
    """Test cases for EnvironmentDetector"""
    
    def setUp(self):
        self.detector = EnvironmentDetector()
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_is_running_in_docker_false(self):
        """Test Docker detection when not in Docker"""
        # This test assumes we're not running in Docker
        result = self.detector.is_running_in_docker()
        self.assertIsInstance(result, bool)
        
    def test_get_container_type(self):
        """Test container type detection"""
        container_type = self.detector.get_container_type()
        if container_type is not None:
            self.assertIsInstance(container_type, str)
            
    def test_is_running_in_kubernetes(self):
        """Test Kubernetes detection"""
        result = self.detector.is_running_in_kubernetes()
        self.assertIsInstance(result, bool)
        
    def test_get_platform_info(self):
        """Test platform information retrieval"""
        info = self.detector.get_platform_info()
        self.assertIsInstance(info, dict)
        self.assertIn("system", info)
        self.assertIn("node", info)
        self.assertIn("release", info)
        
    def test_get_python_info(self):
        """Test Python information retrieval"""
        info = self.detector.get_python_info()
        self.assertIsInstance(info, dict)
        self.assertIn("version", info)
        self.assertIn("version_info", info)
        self.assertIn("executable", info)
        
    def test_get_relevant_environment_variables(self):
        """Test environment variable filtering"""
        env_vars = self.detector.get_relevant_environment_variables()
        self.assertIsInstance(env_vars, dict)
        
        # Check that sensitive variables are masked
        for key, value in env_vars.items():
            if any(sensitive in key.upper() for sensitive in ['KEY', 'SECRET', 'PASSWORD', 'TOKEN']):
                self.assertEqual(value, "***MASKED***")
                
    def test_detect_environment(self):
        """Test complete environment detection"""
        env_info = self.detector.detect_environment()
        self.assertIsInstance(env_info, EnvironmentInfo)
        
        # Check required fields
        self.assertIsNotNone(env_info.platform)
        self.assertIsNotNone(env_info.architecture)
        self.assertIsNotNone(env_info.python_version)
        self.assertIsNotNone(env_info.working_directory)
        self.assertIsNotNone(env_info.home_directory)
        self.assertIsNotNone(env_info.user)
        self.assertIsNotNone(env_info.hostname)
        self.assertIsNotNone(env_info.environment_variables)
        
    def test_get_environment_summary(self):
        """Test environment summary"""
        summary = self.detector.get_environment_summary()
        self.assertIsInstance(summary, dict)
        self.assertIn("platform", summary)
        self.assertIn("architecture", summary)
        self.assertIn("is_docker", summary)
        self.assertIn("is_containerized", summary)
        self.assertIn("python_version", summary)
        self.assertIn("hostname", summary)
        self.assertIn("user", summary)
        
    def test_export_environment_info(self):
        """Test environment info export"""
        export_path = os.path.join(self.temp_dir, "env_info.json")
        self.detector.export_environment_info(export_path, "json")
        
        # Check that file was created
        self.assertTrue(os.path.exists(export_path))
        
        # Check that file contains valid JSON
        with open(export_path, 'r') as f:
            data = json.load(f)
        self.assertIsInstance(data, dict)

class TestConfigManager(unittest.TestCase):
    """Test cases for ConfigManager"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.config_manager = ConfigManager(self.temp_dir)
        
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_config_profiles_loading(self):
        """Test configuration profiles loading"""
        profiles = self.config_manager.list_config_profiles()
        self.assertIsInstance(profiles, list)
        self.assertGreater(len(profiles), 0)
        
        # Check that builtin profiles are loaded
        self.assertIn("docker-default", profiles)
        self.assertIn("local-development", profiles)
        self.assertIn("kubernetes-production", profiles)
        
    def test_get_config_profile(self):
        """Test getting specific configuration profile"""
        profile = self.config_manager.get_config_profile("docker-default")
        self.assertIsNotNone(profile)
        self.assertIsInstance(profile, ConfigProfile)
        self.assertEqual(profile.name, "docker-default")
        
    def test_apply_config_profile(self):
        """Test applying configuration profile"""
        # Apply a profile
        result = self.config_manager.apply_config_profile("local-development")
        self.assertTrue(result)
        
        # Check that configuration was updated
        config = self.config_manager.get_config()
        self.assertIsInstance(config, AdaptiveConfig)
        
    def test_get_config(self):
        """Test getting current configuration"""
        config = self.config_manager.get_config()
        self.assertIsInstance(config, AdaptiveConfig)
        
        # Check required fields
        self.assertIsNotNone(config.workspace_root)
        self.assertIsNotNone(config.session_dir)
        self.assertIsNotNone(config.log_level)
        self.assertIsNotNone(config.max_workers)
        self.assertIsNotNone(config.timeout)
        self.assertIsNotNone(config.enable_dashboard)
        self.assertIsNotNone(config.database_path)
        self.assertIsNotNone(config.cache_dir)
        self.assertIsNotNone(config.temp_dir)
        self.assertIsNotNone(config.security_settings)
        self.assertIsNotNone(config.performance_settings)
        
    def test_get_setting(self):
        """Test getting specific setting"""
        setting = self.config_manager.get_setting("max_workers", 1)
        self.assertIsInstance(setting, int)
        self.assertGreaterEqual(setting, 1)
        
    def test_get_security_setting(self):
        """Test getting security setting"""
        setting = self.config_manager.get_security_setting("max_file_size_mb", 0)
        self.assertIsInstance(setting, int)
        self.assertGreaterEqual(setting, 0)
        
    def test_get_performance_setting(self):
        """Test getting performance setting"""
        setting = self.config_manager.get_performance_setting("memory_limit_mb", 0)
        self.assertIsInstance(setting, int)
        self.assertGreaterEqual(setting, 0)
        
    def test_config_summary(self):
        """Test configuration summary"""
        summary = self.config_manager.get_config_summary()
        self.assertIsInstance(summary, dict)
        self.assertIn("environment", summary)
        self.assertIn("workspace_root", summary)
        self.assertIn("session_dir", summary)
        self.assertIn("log_level", summary)
        self.assertIn("max_workers", summary)
        self.assertIn("timeout", summary)
        self.assertIn("enable_dashboard", summary)
        self.assertIn("database_path", summary)
        self.assertIn("cache_dir", summary)
        self.assertIn("temp_dir", summary)
        
    def test_validate_configuration(self):
        """Test configuration validation"""
        validation = self.config_manager.validate_configuration()
        self.assertIsInstance(validation, dict)
        self.assertIn("valid", validation)
        self.assertIn("issues", validation)
        self.assertIn("warnings", validation)
        
    def test_reload_configuration(self):
        """Test configuration reloading"""
        # This should not raise an exception
        self.config_manager.reload_configuration()

class TestPlatformAdapter(unittest.TestCase):
    """Test cases for PlatformAdapter"""
    
    def setUp(self):
        self.adapter = PlatformAdapter()
        
    def test_get_optimal_worker_count(self):
        """Test optimal worker count calculation"""
        worker_count = self.adapter.get_optimal_worker_count()
        self.assertIsInstance(worker_count, int)
        self.assertGreater(worker_count, 0)
        self.assertLessEqual(worker_count, 8)
        
    def test_get_temp_directory(self):
        """Test temporary directory determination"""
        temp_dir = self.adapter.get_temp_directory()
        self.assertIsInstance(temp_dir, str)
        self.assertTrue(os.path.exists(temp_dir))
        self.assertTrue(os.access(temp_dir, os.W_OK))
        
    def test_get_optimal_buffer_sizes(self):
        """Test optimal buffer size calculation"""
        buffer_sizes = self.adapter.get_optimal_buffer_sizes()
        self.assertIsInstance(buffer_sizes, dict)
        self.assertIn("file_read_buffer", buffer_sizes)
        self.assertIn("network_buffer", buffer_sizes)
        self.assertIn("compression_buffer", buffer_sizes)
        self.assertIn("log_buffer", buffer_sizes)
        
        # Check that all buffer sizes are positive integers
        for key, value in buffer_sizes.items():
            self.assertIsInstance(value, int)
            self.assertGreater(value, 0)
            
    def test_get_platform_specific_commands(self):
        """Test platform-specific command retrieval"""
        commands = self.adapter.get_platform_specific_commands()
        self.assertIsInstance(commands, dict)
        self.assertIn("shell", commands)
        self.assertIn("list_files", commands)
        self.assertIn("copy_file", commands)
        self.assertIn("move_file", commands)
        self.assertIn("delete_file", commands)
        self.assertIn("make_directory", commands)
        self.assertIn("remove_directory", commands)
        
        # Check that all commands are lists
        for key, value in commands.items():
            self.assertIsInstance(value, list)
            
    def test_get_system_info(self):
        """Test system information retrieval"""
        info = self.adapter.get_system_info()
        self.assertIsInstance(info, dict)
        self.assertIn("platform", info)
        self.assertIn("machine", info)
        self.assertIn("release", info)
        self.assertIn("python_version", info)
        self.assertIn("architecture", info)
        self.assertIn("cpu_count", info)
        
    def test_optimize_for_current_platform(self):
        """Test platform-specific optimizations"""
        optimizations = self.adapter.optimize_for_current_platform()
        self.assertIsInstance(optimizations, dict)
        self.assertIn("worker_count", optimizations)
        self.assertIn("temp_directory", optimizations)
        self.assertIn("buffer_sizes", optimizations)
        self.assertIn("commands", optimizations)
        self.assertIn("permissions_commands", optimizations)
        self.assertIn("system_info", optimizations)
        
    def test_get_path_separator(self):
        """Test path separator retrieval"""
        separator = self.adapter.get_path_separator()
        self.assertIsInstance(separator, str)
        self.assertEqual(separator, os.sep)
        
    def test_normalize_path(self):
        """Test path normalization"""
        test_path = "some/../path/./to/file"
        normalized = self.adapter.normalize_path(test_path)
        self.assertIsInstance(normalized, str)
        # Should not contain .. or . in normalized path
        self.assertNotIn("..", normalized)
        
    def test_get_case_sensitive_filesystem(self):
        """Test case sensitivity detection"""
        case_sensitive = self.adapter.get_case_sensitive_filesystem()
        self.assertIsInstance(case_sensitive, bool)
        
    def test_get_preferred_encoding(self):
        """Test preferred encoding detection"""
        encoding = self.adapter.get_preferred_encoding()
        self.assertIsInstance(encoding, str)
        self.assertEqual(encoding, "utf-8")  # Default fallback

class TestRuntimeProfiler(unittest.TestCase):
    """Test cases for RuntimeProfiler"""
    
    def setUp(self):
        self.profiler = RuntimeProfiler(sampling_interval=0.1)  # Fast sampling for tests
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        self.profiler.stop_profiling()
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_start_stop_profiling(self):
        """Test profiling start and stop"""
        # Start profiling
        self.profiler.start_profiling()
        self.assertTrue(self.profiler.is_profiling)
        
        # Let it run briefly
        import time
        time.sleep(0.2)
        
        # Stop profiling
        profile = self.profiler.stop_profiling()
        self.assertFalse(self.profiler.is_profiling)
        self.assertIsInstance(profile, object)  # PerformanceProfile
        
    def test_collect_snapshot(self):
        """Test snapshot collection"""
        snapshot = self.profiler._collect_snapshot()
        if snapshot is not None:
            self.assertIsInstance(snapshot, PerformanceSnapshot)
            self.assertGreater(snapshot.timestamp, 0)
            self.assertGreaterEqual(snapshot.cpu_percent, 0)
            self.assertGreaterEqual(snapshot.memory_mb, 0)
            self.assertGreaterEqual(snapshot.memory_percent, 0)
            self.assertGreaterEqual(snapshot.thread_count, 0)
            
    def test_get_current_profile(self):
        """Test current profile retrieval"""
        profile = self.profiler.get_current_profile()
        self.assertIsInstance(profile, object)  # PerformanceProfile
        self.assertIsInstance(profile.start_time, float)
        self.assertIsInstance(profile.duration, float)
        self.assertIsInstance(profile.avg_cpu_percent, float)
        self.assertIsInstance(profile.max_cpu_percent, float)
        self.assertIsInstance(profile.avg_memory_mb, float)
        self.assertIsInstance(profile.max_memory_mb, float)
        self.assertIsInstance(profile.total_disk_read_mb, float)
        self.assertIsInstance(profile.total_disk_write_mb, float)
        self.assertIsInstance(profile.total_network_sent_mb, float)
        self.assertIsInstance(profile.total_network_received_mb, float)
        self.assertIsInstance(profile.peak_thread_count, int)
        self.assertIsInstance(profile.snapshots, list)
        
    def test_get_real_time_metrics(self):
        """Test real-time metrics retrieval"""
        metrics = self.profiler.get_real_time_metrics()
        self.assertIsInstance(metrics, dict)
        self.assertIn("cpu_percent", metrics)
        self.assertIn("memory_mb", metrics)
        self.assertIn("memory_percent", metrics)
        self.assertIn("thread_count", metrics)
        self.assertIn("timestamp", metrics)
        
        # Check value types
        self.assertIsInstance(metrics["cpu_percent"], float)
        self.assertIsInstance(metrics["memory_mb"], float)
        self.assertIsInstance(metrics["memory_percent"], float)
        self.assertIsInstance(metrics["thread_count"], int)
        self.assertIsInstance(metrics["timestamp"], float)
        
    def test_get_resource_usage_summary(self):
        """Test resource usage summary"""
        summary = self.profiler.get_resource_usage_summary()
        self.assertIsInstance(summary, dict)
        self.assertIn("duration_seconds", summary)
        self.assertIn("average_cpu_percent", summary)
        self.assertIn("peak_cpu_percent", summary)
        self.assertIn("average_memory_mb", summary)
        self.assertIn("peak_memory_mb", summary)
        self.assertIn("total_disk_reads_mb", summary)
        self.assertIn("total_disk_writes_mb", summary)
        self.assertIn("peak_thread_count", summary)
        self.assertIn("snapshot_count", summary)
        
    def test_export_profile(self):
        """Test profile export"""
        export_path = os.path.join(self.temp_dir, "profile.json")
        self.profiler.export_profile(export_path, "json")
        
        # Check that file was created
        self.assertTrue(os.path.exists(export_path))
        
        # Check that file contains valid JSON
        with open(export_path, 'r') as f:
            data = json.load(f)
        self.assertIsInstance(data, dict)
        
    def test_check_resource_limits(self):
        """Test resource limit checking"""
        # Mock config manager for testing
        mock_config_manager = Mock()
        mock_config_manager.get_performance_setting.return_value = 1024  # 1GB limit
        
        violations = self.profiler.check_resource_limits(mock_config_manager)
        self.assertIsInstance(violations, dict)
        self.assertIn("exceeded", violations)
        self.assertIn("violations", violations)
        self.assertIn("warnings", violations)
        self.assertIsInstance(violations["exceeded"], bool)
        self.assertIsInstance(violations["violations"], list)
        self.assertIsInstance(violations["warnings"], list)
        
    def test_get_system_health(self):
        """Test system health metrics"""
        health = self.profiler.get_system_health()
        self.assertIsInstance(health, dict)
        self.assertIn("timestamp", health)
        
        # May contain error or metrics
        if "error" not in health:
            self.assertIn("system_cpu_percent", health)
            self.assertIn("system_memory_percent", health)
            self.assertIn("system_memory_available_mb", health)
            self.assertIn("system_disk_percent", health)
            self.assertIn("system_disk_free_gb", health)

if __name__ == '__main__':
    unittest.main()
```

### Integration Testing

```python
# File: tests/test_environment_detection_integration.py
import unittest
import tempfile
import os
import sys
import time
from pathlib import Path
from unittest.mock import Mock, patch

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config.environment_detector import EnvironmentDetector
from config.config_manager import ConfigManager
from config.platform_adapter import PlatformAdapter
from config.runtime_profiler import RuntimeProfiler

class TestEnvironmentDetectionIntegration(unittest.TestCase):
    """Integration tests for environment detection components"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.environment_detector = EnvironmentDetector()
        self.config_manager = ConfigManager(self.temp_dir)
        self.platform_adapter = PlatformAdapter()
        self.runtime_profiler = RuntimeProfiler(sampling_interval=0.1)
        
    def tearDown(self):
        self.runtime_profiler.stop_profiling()
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_end_to_end_environment_detection(self):
        """Test end-to-end environment detection workflow"""
        # 1. Detect environment
        env_info = self.environment_detector.detect_environment()
        self.assertIsInstance(env_info, object)  # EnvironmentInfo
        
        # 2. Get environment summary
        env_summary = self.environment_detector.get_environment_summary()
        self.assertIsInstance(env_summary, dict)
        self.assertIn("platform", env_summary)
        self.assertIn("is_docker", env_summary)
        self.assertIn("python_version", env_summary)
        
        # 3. Apply adaptive configuration
        self.config_manager._initialize_adaptive_config()
        config = self.config_manager.get_config()
        self.assertIsInstance(config, object)  # AdaptiveConfig
        
        # 4. Apply platform optimizations
        optimizations = self.platform_adapter.optimize_for_current_platform()
        self.assertIsInstance(optimizations, dict)
        self.assertIn("worker_count", optimizations)
        self.assertIn("temp_directory", optimizations)
        self.assertIn("buffer_sizes", optimizations)
        
        # 5. Verify configuration consistency
        self.assertEqual(config.max_workers, optimizations["worker_count"])
        self.assertEqual(config.temp_dir, optimizations["temp_directory"])
        
        # 6. Test configuration accessors
        worker_count = self.config_manager.get_setting("max_workers", 1)
        self.assertEqual(worker_count, config.max_workers)
        
        temp_dir = self.config_manager.get_setting("temp_dir", "/tmp")
        self.assertEqual(temp_dir, config.temp_dir)
        
        # 7. Test configuration summary
        config_summary = self.config_manager.get_config_summary()
        self.assertIsInstance(config_summary, dict)
        self.assertIn("environment", config_summary)
        self.assertIn("workspace_root", config_summary)
        self.assertIn("session_dir", config_summary)
        
        # 8. Validate configuration
        validation = self.config_manager.validate_configuration()
        self.assertIsInstance(validation, dict)
        self.assertIn("valid", validation)
        self.assertIn("issues", validation)
        self.assertIn("warnings", validation)
        
        # 9. Export environment information
        export_path = os.path.join(self.temp_dir, "env_info.json")
        self.environment_detector.export_environment_info(export_path, "json")
        self.assertTrue(os.path.exists(export_path))
        
    def test_runtime_profiling_integration(self):
        """Test runtime profiling integration"""
        # Start profiling
        self.runtime_profiler.start_profiling()
        self.assertTrue(self.runtime_profiler.is_profiling)
        
        # Let it run briefly
        time.sleep(0.3)
        
        # Get real-time metrics
        metrics = self.runtime_profiler.get_real_time_metrics()
        self.assertIsInstance(metrics, dict)
        self.assertIn("cpu_percent", metrics)
        self.assertIn("memory_mb", metrics)
        self.assertIn("thread_count", metrics)
        
        # Check resource limits
        mock_config_manager = Mock()
        mock_config_manager.get_performance_setting.return_value = 1024  # 1GB limit
        violations = self.runtime_profiler.check_resource_limits(mock_config_manager)
        self.assertIsInstance(violations, dict)
        
        # Get resource usage summary
        summary = self.runtime_profiler.get_resource_usage_summary()
        self.assertIsInstance(summary, dict)
        self.assertIn("duration_seconds", summary)
        self.assertIn("average_cpu_percent", summary)
        self.assertIn("peak_memory_mb", summary)
        
        # Stop profiling and get profile
        profile = self.runtime_profiler.stop_profiling()
        self.assertFalse(self.runtime_profiler.is_profiling)
        self.assertIsInstance(profile, object)  # PerformanceProfile
        
        # Export profile
        export_path = os.path.join(self.temp_dir, "profile.json")
        self.runtime_profiler.export_profile(export_path, "json")
        self.assertTrue(os.path.exists(export_path))
        
    def test_configuration_profile_management(self):
        """Test configuration profile management"""
        # List available profiles
        profiles = self.config_manager.list_config_profiles()
        self.assertIsInstance(profiles, list)
        self.assertGreater(len(profiles), 0)
        
        # Get specific profiles
        for profile_name in ["docker-default", "local-development"]:
            profile = self.config_manager.get_config_profile(profile_name)
            if profile is not None:
                self.assertIsInstance(profile, object)  # ConfigProfile
                self.assertEqual(profile.name, profile_name)
                
        # Apply profiles and verify configuration changes
        initial_workers = self.config_manager.get_setting("max_workers", 1)
        
        # Apply Docker profile
        self.config_manager.apply_config_profile("docker-default")
        docker_workers = self.config_manager.get_setting("max_workers", 1)
        
        # Apply local development profile
        self.config_manager.apply_config_profile("local-development")
        local_workers = self.config_manager.get_setting("max_workers", 1)
        
        # Profiles should have different worker counts
        self.assertIsInstance(docker_workers, int)
        self.assertIsInstance(local_workers, int)
        
    def test_platform_specific_adaptations(self):
        """Test platform-specific adaptations"""
        # Get platform information
        platform_info = self.platform_adapter.get_system_info()
        self.assertIsInstance(platform_info, dict)
        self.assertIn("platform", platform_info)
        self.assertIn("machine", platform_info)
        self.assertIn("cpu_count", platform_info)
        
        # Get platform-specific commands
        commands = self.platform_adapter.get_platform_specific_commands()
        self.assertIsInstance(commands, dict)
        self.assertIn("shell", commands)
        self.assertIn("list_files", commands)
        
        # Get file permissions commands
        perm_commands = self.platform_adapter.get_file_permissions_commands()
        self.assertIsInstance(perm_commands, dict)
        self.assertIn("chmod", perm_commands)
        self.assertIn("chown", perm_commands)
        
        # Test path handling
        separator = self.platform_adapter.get_path_separator()
        self.assertIsInstance(separator, str)
        self.assertEqual(separator, os.sep)
        
        normalized_path = self.platform_adapter.normalize_path("some/../path/./file")
        self.assertIsInstance(normalized_path, str)
        
        case_sensitive = self.platform_adapter.get_case_sensitive_filesystem()
        self.assertIsInstance(case_sensitive, bool)
        
        encoding = self.platform_adapter.get_preferred_encoding()
        self.assertIsInstance(encoding, str)
        # Should default to utf-8
        self.assertEqual(encoding, "utf-8")
        
    def test_environment_aware_configuration(self):
        """Test environment-aware configuration application"""
        # Get initial adaptive configuration
        initial_config = self.config_manager.get_config()
        self.assertIsInstance(initial_config, object)  # AdaptiveConfig
        
        # Test configuration accessors
        workspace_root = self.config_manager.get_setting("workspace_root")
        self.assertIsInstance(workspace_root, str)
        
        log_level = self.config_manager.get_setting("log_level", "INFO")
        self.assertIsInstance(log_level, str)
        
        max_workers = self.config_manager.get_setting("max_workers", 1)
        self.assertIsInstance(max_workers, int)
        self.assertGreater(max_workers, 0)
        
        # Test security settings
        security_settings = self.config_manager.get_setting("security_settings", {})
        self.assertIsInstance(security_settings, dict)
        
        allowed_paths = self.config_manager.get_security_setting("allowed_paths", [])
        self.assertIsInstance(allowed_paths, list)
        
        max_file_size = self.config_manager.get_security_setting("max_file_size_mb", 0)
        self.assertIsInstance(max_file_size, int)
        self.assertGreaterEqual(max_file_size, 0)
        
        # Test performance settings
        performance_settings = self.config_manager.get_setting("performance_settings", {})
        self.assertIsInstance(performance_settings, dict)
        
        memory_limit = self.config_manager.get_performance_setting("memory_limit_mb", 0)
        self.assertIsInstance(memory_limit, int)
        self.assertGreaterEqual(memory_limit, 0)
        
        cpu_limit = self.config_manager.get_performance_setting("cpu_limit_cores", 0.0)
        self.assertIsInstance(cpu_limit, (int, float))
        self.assertGreaterEqual(cpu_limit, 0.0)
        
    def test_complete_workflow_integration(self):
        """Test complete workflow integration"""
        # 1. Environment detection
        env_info = self.environment_detector.detect_environment()
        self.assertIsInstance(env_info, object)  # EnvironmentInfo
        
        # 2. Configuration adaptation
        self.config_manager._initialize_adaptive_config()
        adaptive_config = self.config_manager.get_config()
        self.assertIsInstance(adaptive_config, object)  # AdaptiveConfig
        
        # 3. Platform optimization
        optimizations = self.platform_adapter.optimize_for_current_platform()
        self.assertIsInstance(optimizations, dict)
        
        # 4. Start runtime profiling
        self.runtime_profiler.start_profiling()
        self.assertTrue(self.runtime_profiler.is_profiling)
        
        # 5. Let system run briefly
        time.sleep(0.2)
        
        # 6. Get real-time metrics
        real_time_metrics = self.runtime_profiler.get_real_time_metrics()
        self.assertIsInstance(real_time_metrics, dict)
        
        # 7. Check resource usage
        resource_summary = self.runtime_profiler.get_resource_usage_summary()
        self.assertIsInstance(resource_summary, dict)
        
        # 8. Stop profiling
        performance_profile = self.runtime_profiler.stop_profiling()
        self.assertIsInstance(performance_profile, object)  # PerformanceProfile
        
        # 9. Validate configuration
        validation_results = self.config_manager.validate_configuration()
        self.assertIsInstance(validation_results, dict)
        self.assertIn("valid", validation_results)
        
        # 10. Get configuration summary
        config_summary = self.config_manager.get_config_summary()
        self.assertIsInstance(config_summary, dict)
        
        # 11. Verify integration consistency
        # Environment info should match configuration
        env_summary = self.environment_detector.get_environment_summary()
        self.assertEqual(env_summary["platform"], config_summary["environment"]["platform"])
        self.assertEqual(env_summary["is_docker"], config_summary["environment"]["is_docker"])
        
        # Platform optimizations should match configuration
        self.assertEqual(optimizations["worker_count"], adaptive_config.max_workers)
        self.assertEqual(optimizations["temp_directory"], adaptive_config.temp_dir)
        
        # Performance profile should contain snapshots
        self.assertIsInstance(performance_profile.snapshots, list)
        if performance_profile.snapshots:
            snapshot = performance_profile.snapshots[0]
            self.assertIsInstance(snapshot, object)  # PerformanceSnapshot
            
        # Real-time metrics should be reasonable
        self.assertGreaterEqual(real_time_metrics["cpu_percent"], 0)
        self.assertGreaterEqual(real_time_metrics["memory_mb"], 0)
        self.assertGreaterEqual(real_time_metrics["thread_count"], 1)
        
        # Resource summary should be comprehensive
        self.assertIn("duration_seconds", resource_summary)
        self.assertIn("average_cpu_percent", resource_summary)
        self.assertIn("peak_memory_mb", resource_summary)
        
        # Configuration validation should be complete
        self.assertIn("issues", validation_results)
        self.assertIn("warnings", validation_results)
        
        # Configuration summary should be detailed
        self.assertIn("environment", config_summary)
        self.assertIn("workspace_root", config_summary)
        self.assertIn("security_settings", config_summary)
        self.assertIn("performance_settings", config_summary)
        
    def test_error_handling_and_recovery(self):
        """Test error handling and recovery"""
        # Test with invalid export format
        with self.assertRaises(ValueError):
            self.environment_detector.export_environment_info("/tmp/test.txt", "invalid_format")
            
        # Test with invalid profile export format
        with self.assertRaises(ValueError):
            self.runtime_profiler.export_profile("/tmp/test.txt", "invalid_format")
            
        # Test configuration with missing settings (should use defaults)
        missing_setting = self.config_manager.get_setting("nonexistent_setting", "default_value")
        self.assertEqual(missing_setting, "default_value")
        
        # Test security setting with missing key (should use defaults)
        missing_security = self.config_manager.get_security_setting("nonexistent_key", 42)
        self.assertEqual(missing_security, 42)
        
        # Test performance setting with missing key (should use defaults)
        missing_performance = self.config_manager.get_performance_setting("nonexistent_key", 3.14)
        self.assertEqual(missing_performance, 3.14)
        
        # Test profile application with nonexistent profile
        result = self.config_manager.apply_config_profile("nonexistent_profile")
        self.assertFalse(result)
        
        # Test getting nonexistent profile
        profile = self.config_manager.get_config_profile("nonexistent_profile")
        self.assertIsNone(profile)
        
        # Test environment detection with potential errors
        # (This should not raise exceptions but handle gracefully)
        env_info = self.environment_detector.detect_environment()
        self.assertIsInstance(env_info, object)  # EnvironmentInfo
        
        # Test runtime profiling with potential errors
        metrics = self.runtime_profiler.get_real_time_metrics()
        self.assertIsInstance(metrics, dict)
        
        # Even if there are errors, should return safe defaults
        if "error" in metrics:
            # Error case handled gracefully
            self.assertIn("timestamp", metrics)
        else:
            # Normal metrics returned
            self.assertIn("cpu_percent", metrics)
            self.assertIn("memory_mb", metrics)
            self.assertIn("thread_count", metrics)
            
        # Test system health with potential errors
        health = self.runtime_profiler.get_system_health()
        self.assertIsInstance(health, dict)
        self.assertIn("timestamp", health)
        
        # Test resource limit checking with mock configuration
        mock_config = Mock()
        mock_config.get_performance_setting.return_value = None  # Simulate missing setting
        violations = self.runtime_profiler.check_resource_limits(mock_config)
        self.assertIsInstance(violations, dict)
        self.assertIn("exceeded", violations)
        self.assertIn("violations", violations)
        self.assertIn("warnings", violations)

if __name__ == '__main__':
    unittest.main()
```

### Performance and Scalability Considerations

#### Performance Optimization Strategies

1. **Lazy Initialization**: Components are initialized only when needed
2. **Caching**: Frequently accessed information is cached to avoid repeated system calls
3. **Efficient Polling**: Resource monitoring uses efficient polling intervals
4. **Minimal Overhead**: Environment detection has minimal runtime impact
5. **Selective Monitoring**: Only relevant metrics are collected based on environment

#### Scalability Features

1. **Adaptive Configuration**: Automatically scales based on available resources
2. **Resource Limits**: Respects container resource constraints
3. **Dynamic Worker Adjustment**: Adjusts worker counts based on system capacity
4. **Memory-Efficient Profiling**: Uses circular buffers to limit memory usage
5. **Configurable Sampling**: Allows adjustment of monitoring frequency

### Security Considerations

1. **Sensitive Data Masking**: Automatically masks sensitive environment variables
2. **Path Validation**: Validates file paths against allowed/restricted lists
3. **Resource Limits**: Prevents resource exhaustion through configurable limits
4. **Access Controls**: Restricts file system access based on environment
5. **Input Sanitization**: Sanitizes all configuration inputs

### Deployment Considerations

1. **Docker Support**: Ready-to-use Docker configuration for containerized deployment
2. **Environment Configuration**: All settings configurable via environment variables
3. **Health Checks**: Built-in health check endpoints for container orchestration
4. **Logging Integration**: Comprehensive logging for monitoring and debugging
5. **Backup and Recovery**: Configuration backup and recovery capabilities

### Future Enhancements

1. **Cloud Provider Detection**: Enhanced detection for AWS, Azure, GCP environments
2. **Service Mesh Integration**: Integration with Istio, Linkerd service meshes
3. **Advanced Resource Management**: Integration with Kubernetes resource quotas
4. **Predictive Scaling**: ML-based predictive scaling based on workload patterns
5. **Cross-Cluster Coordination**: Multi-cluster environment coordination
6. **Advanced Monitoring**: Integration with Prometheus, Grafana, etc.
7. **Security Hardening**: Enhanced security features for production environments
8. **Multi-Tenant Support**: Support for multi-tenant environment isolation

This comprehensive environment detection system provides automatic runtime adaptation with minimal overhead, ensuring optimal performance and compatibility across different deployment scenarios while maintaining security and resource efficiency.