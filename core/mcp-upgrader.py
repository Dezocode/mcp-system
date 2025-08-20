#!/usr/bin/env python3
"""
MCP Upgrader - Modular upgrade system for MCP servers
Allows Claude to intelligently upgrade servers while maintaining compatibility
"""

import argparse
import json
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class UpgradeModule:
    """Represents an upgrade module"""

    id: str
    name: str
    description: str
    version: str
    compatibility: List[str]  # Compatible templates
    requirements: List[str]  # Required modules
    conflicts: List[str]  # Conflicting modules
    files: Dict[str, str]  # Files to add/modify
    commands: List[str]  # Commands to run
    rollback_commands: List[str]  # Rollback commands
    schema_version: str = "1.0"


@dataclass
class ServerInfo:
    """Information about a server"""

    name: str
    path: Path
    template: str
    version: str
    installed_modules: List[str]
    config: Dict
    last_upgraded: Optional[str] = None


@dataclass
class UpgradeResult:
    """Result of an upgrade operation"""

    success: bool
    server_name: str
    modules_applied: List[str]
    backup_path: Optional[str]
    errors: List[str]
    warnings: List[str]
    duration: float


class MCPUpgrader:
    def __init__(self, config_file: str = "~/.mcp-servers.json"):
        self.config_file = Path(config_file).expanduser()
        self.upgrade_dir = Path.home() / ".mcp-upgrades"
        self.backup_dir = Path.home() / ".mcp-backups"
        self.modules_dir = self.upgrade_dir / "modules"

        # Create directories
        self.upgrade_dir.mkdir(exist_ok=True)
        self.backup_dir.mkdir(exist_ok=True)
        self.modules_dir.mkdir(exist_ok=True)

        self.servers = self._load_servers()
        self.available_modules = self._load_upgrade_modules()

        # Initialize default modules
        self._initialize_default_modules()

    def _load_servers(self) -> Dict[str, ServerInfo]:
        """Load server configurations"""
        if not self.config_file.exists():
            return {}

        config = json.loads(self.config_file.read_text())
        servers = {}

        for name, server_config in config.items():
            path = Path(server_config.get("path", "")).expanduser()
            if not path.exists():
                continue

            # Detect server info
            template = self._detect_template(path)
            version = self._detect_version(path)
            installed_modules = self._detect_installed_modules(path)

            servers[name] = ServerInfo(
                name=name,
                path=path,
                template=template,
                version=version,
                installed_modules=installed_modules,
                config=server_config,
            )

        return servers

    def _detect_template(self, path: Path) -> str:
        """Detect server template type"""
        if (path / "pyproject.toml").exists() and (
            path / "src" / "main.py"
        ).exists():
            return "python-fastmcp"
        elif (path / "package.json").exists() and (
            path / "src" / "index.ts"
        ).exists():
            return "typescript-node"
        elif (path / "main.py").exists():
            return "minimal-python"
        else:
            return "unknown"

    def _detect_version(self, path: Path) -> str:
        """Detect server version"""
        # Try different version detection methods
        methods = [
            lambda: self._version_from_pyproject(path),
            lambda: self._version_from_package_json(path),
            lambda: self._version_from_git(path),
            lambda: "1.0.0",  # Default
        ]

        for method in methods:
            try:
                version = method()
                if version:
                    return version
            except Exception:
                continue

        return "1.0.0"

    def _version_from_pyproject(self, path: Path) -> Optional[str]:
        """Get version from pyproject.toml"""
        pyproject = path / "pyproject.toml"
        if pyproject.exists():
            import tomllib

            with open(pyproject, "rb") as f:
                data = tomllib.load(f)
                return data.get("project", {}).get("version")
        return None

    def _version_from_package_json(self, path: Path) -> Optional[str]:
        """Get version from package.json"""
        package_json = path / "package.json"
        if package_json.exists():
            data = json.loads(package_json.read_text())
            return data.get("version")
        return None

    def _version_from_git(self, path: Path) -> Optional[str]:
        """Get version from git tags"""
        try:
            result = subprocess.run(
                ["git", "describe", "--tags", "--abbrev=0"],
                cwd=path,
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                return result.stdout.strip().lstrip("v")
        except Exception:
            pass
        return None

    def _detect_installed_modules(self, path: Path) -> List[str]:
        """Detect installed upgrade modules"""
        upgrade_manifest = path / ".mcp-upgrades.json"
        if upgrade_manifest.exists():
            try:
                data = json.loads(upgrade_manifest.read_text())
                return data.get("installed_modules", [])
            except Exception:
                pass
        return []

    def _load_upgrade_modules(
        self,
    ) -> Dict[str, UpgradeModule]:
        """Load available upgrade modules"""
        modules = {}

        # Load from modules directory
        for module_file in self.modules_dir.glob("*.json"):
            try:
                data = json.loads(module_file.read_text())
                module = UpgradeModule(**data)
                modules[module.id] = module
            except Exception as e:
                print(f"Warning: Failed to load module {module_file}: {e}")

        return modules

    def _initialize_default_modules(self):
        """Initialize default upgrade modules"""
        default_modules = self._get_default_modules()

        for module_data in default_modules:
            module_id = module_data["id"]
            module_file = self.modules_dir / f"{module_id}.json"

            if not module_file.exists():
                module_file.write_text(json.dumps(module_data, indent=2))
                print(f"Created default module: {module_id}")

    def _get_default_modules(self) -> List[Dict]:
        """Get default upgrade modules"""
        return [
            {
                "id": "logging-enhancement",
                "name": "Enhanced Logging",
                "description": (
                    "Add structured logging with correlation IDs and metrics"
                ),
                "version": "1.0.0",
                "compatibility": [
                    "python-fastmcp",
                    "minimal-python",
                ],
                "requirements": [],
                "conflicts": [],
                "files": {
                    "src/utils/logging.py": self._get_logging_enhancement_code(),
                    "requirements-logging.txt": (
                        "structlog>=23.1.0\\nprometheus-client>=0.17.0"
                    ),
                },
                "commands": ["pip install -r requirements-logging.txt"],
                "rollback_commands": [
                    "pip uninstall -y structlog prometheus-client"
                ],
            },
            {
                "id": "authentication",
                "name": "JWT Authentication",
                "description": "Add JWT-based authentication to MCP tools",
                "version": "1.0.0",
                "compatibility": [
                    "python-fastmcp",
                    "typescript-node",
                ],
                "requirements": [],
                "conflicts": [],
                "files": {
                    "src/middleware/auth.py": self._get_auth_middleware_code(),
                    "requirements-auth.txt": (
                        "pyjwt[crypto]>=2.8.0\\ncryptography>=41.0.0"
                    ),
                },
                "commands": ["pip install -r requirements-auth.txt"],
                "rollback_commands": [
                    "pip uninstall -y pyjwt cryptography"
                ],
            },
            {
                "id": "caching-redis",
                "name": "Redis Caching",
                "description": "Add Redis-based caching for expensive operations",
                "version": "1.0.0",
                "compatibility": [
                    "python-fastmcp",
                    "typescript-node",
                    "minimal-python",
                ],
                "requirements": [],
                "conflicts": ["caching-memory"],
                "files": {
                    "src/utils/cache.py": self._get_redis_cache_code(),
                    "requirements-cache.txt": "redis>=4.6.0\\naioredis>=2.0.0",
                },
                "commands": ["pip install -r requirements-cache.txt"],
                "rollback_commands": ["pip uninstall -y redis aioredis"],
            },
            {
                "id": "database-migrations",
                "name": "Database Migration System",
                "description": "Add Alembic-based database migrations",
                "version": "1.0.0",
                "compatibility": ["python-fastmcp"],
                "requirements": [],
                "conflicts": [],
                "files": {
                    "migrations/env.py": self._get_migration_env_code(),
                    "migrations/script.py.mako": self._get_migration_template_code(),
                    "src/utils/database.py": self._get_database_utils_code(),
                    "requirements-db.txt": "alembic>=1.12.0\\nsqlalchemy>=2.0.0",
                },
                "commands": [
                    "pip install -r requirements-db.txt",
                    "alembic init migrations",
                ],
                "rollback_commands": [
                    "pip uninstall -y alembic sqlalchemy"
                ],
            },
            {
                "id": "monitoring-metrics",
                "name": "Prometheus Metrics",
                "description": "Add comprehensive Prometheus metrics collection",
                "version": "1.0.0",
                "compatibility": [
                    "python-fastmcp",
                    "typescript-node",
                ],
                "requirements": ["logging-enhancement"],
                "conflicts": [],
                "files": {
                    "src/utils/metrics.py": self._get_metrics_code(),
                    "requirements-metrics.txt": "prometheus-client>=0.17.0",
                },
                "commands": ["pip install -r requirements-metrics.txt"],
                "rollback_commands": [
                    "pip uninstall -y prometheus-client"
                ],
            },
            {
                "id": "api-versioning",
                "name": "API Versioning",
                "description": (
                    "Add API versioning support with backwards compatibility"
                ),
                "version": "1.0.0",
                "compatibility": [
                    "python-fastmcp",
                    "typescript-node",
                ],
                "requirements": [],
                "conflicts": [],
                "files": {
                    "src/middleware/versioning.py": self._get_versioning_code(),
                    "src/schemas/v1/__init__.py": "",
                    "src/schemas/v2/__init__.py": "",
                },
                "commands": [],
                "rollback_commands": [],
            },
        ]

    def analyze_server(self, server_name: str) -> Dict[str, Any]:
        """Analyze a server for upgrade opportunities"""
        if server_name not in self.servers:
            return {"error": f"Server {server_name} not found"}

        server = self.servers[server_name]
        analysis = {
            "server_name": server_name,
            "current_template": server.template,
            "current_version": server.version,
            "installed_modules": server.installed_modules,
            "available_upgrades": [],
            "compatibility_issues": [],
            "recommended_upgrades": [],
        }

        # Find compatible upgrade modules
        for (
            module_id,
            module,
        ) in self.available_modules.items():
            if module_id in server.installed_modules:
                continue

            # Check template compatibility
            if (
                server.template not in module.compatibility
                and "all" not in module.compatibility
            ):
                analysis["compatibility_issues"].append(
                    {
                        "module": module_id,
                        "issue": f"Template {server.template} not supported",
                    }
                )
                continue

            # Check requirements
            missing_requirements = [
                req
                for req in module.requirements
                if req not in server.installed_modules
            ]

            # Check conflicts
            conflicts = [
                conflict
                for conflict in module.conflicts
                if conflict in server.installed_modules
            ]

            upgrade_info = {
                "module_id": module_id,
                "name": module.name,
                "description": module.description,
                "version": module.version,
                "missing_requirements": missing_requirements,
                "conflicts": conflicts,
                "can_install": len(missing_requirements) == 0
                and len(conflicts) == 0,
            }

            analysis["available_upgrades"].append(upgrade_info)

            # Add to recommendations if installable and useful
            if upgrade_info["can_install"]:
                analysis["recommended_upgrades"].append(upgrade_info)

        return analysis

    def create_backup(self, server_name: str) -> str:
        """Create a backup of the server"""
        if server_name not in self.servers:
            raise ValueError(f"Server {server_name} not found")

        server = self.servers[server_name]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{server_name}_{timestamp}"
        backup_path = self.backup_dir / backup_name

        # Create backup directory
        backup_path.mkdir(exist_ok=True)

        # Copy server files
        shutil.copytree(
            server.path,
            backup_path / "server",
            dirs_exist_ok=True,
        )

        # Save metadata
        metadata = {
            "server_name": server_name,
            "backup_time": timestamp,
            "original_path": str(server.path),
            "template": server.template,
            "version": server.version,
            "installed_modules": server.installed_modules,
        }

        (backup_path / "metadata.json").write_text(
            json.dumps(metadata, indent=2)
        )

        print(f"✅ Backup created: {backup_path}")
        return str(backup_path)

    def apply_upgrade_module(
        self,
        server_name: str,
        module_id: str,
        dry_run: bool = False,
    ) -> UpgradeResult:
        """Apply an upgrade module to a server"""
        start_time = time.time()
        result = UpgradeResult(
            success=False,
            server_name=server_name,
            modules_applied=[],
            backup_path=None,
            errors=[],
            warnings=[],
            duration=0,
        )

        try:
            # Validate inputs
            if server_name not in self.servers:
                result.errors.append(f"Server {server_name} not found")
                return result

            if module_id not in self.available_modules:
                result.errors.append(f"Module {module_id} not found")
                return result

            server = self.servers[server_name]
            module = self.available_modules[module_id]

            # Check compatibility
            if (
                server.template not in module.compatibility
                and "all" not in module.compatibility
            ):
                result.errors.append(
                    f"Module {module_id} not compatible with template {server.template}"
                )
                return result

            # Check if already installed
            if module_id in server.installed_modules:
                result.warnings.append(
                    f"Module {module_id} already installed"
                )
                return result

            # Check requirements
            missing_requirements = [
                req
                for req in module.requirements
                if req not in server.installed_modules
            ]
            if missing_requirements:
                result.errors.append(
                    f"Missing required modules: {', '.join(missing_requirements)}"
                )
                return result

            # Check conflicts
            conflicts = [
                conflict
                for conflict in module.conflicts
                if conflict in server.installed_modules
            ]
            if conflicts:
                result.errors.append(
                    f"Conflicting modules installed: {', '.join(conflicts)}"
                )
                return result

            if dry_run:
                result.success = True
                result.modules_applied = [module_id]
                print(
                    f"✅ Dry run successful for {module_id} on {server_name}"
                )
                return result

            # Create backup
            print(f"Creating backup for {server_name}...")
            result.backup_path = self.create_backup(server_name)

            # Apply files
            print(f"Applying module {module_id}...")
            for file_path, content in module.files.items():
                target_path = server.path / file_path
                target_path.parent.mkdir(parents=True, exist_ok=True)
                target_path.write_text(content)
                print(f"  Created: {file_path}")

            # Run commands
            for command in module.commands:
                print(f"  Running: {command}")
                result_cmd = subprocess.run(
                    command,
                    shell=True,
                    cwd=server.path,
                    capture_output=True,
                    text=True,
                )
                if result_cmd.returncode != 0:
                    result.errors.append(f"Command failed: {command}")
                    result.errors.append(f"Error: {result_cmd.stderr}")
                    return result

            # Update server manifest
            self._update_server_manifest(server_name, module_id)

            result.success = True
            result.modules_applied = [module_id]

            print(f"✅ Successfully applied {module_id} to {server_name}")

        except Exception as e:
            result.errors.append(f"Unexpected error: {str(e)}")

        finally:
            result.duration = time.time() - start_time

        return result

    def _update_server_manifest(self, server_name: str, module_id: str):
        """Update server's upgrade manifest"""
        server = self.servers[server_name]
        manifest_path = server.path / ".mcp-upgrades.json"

        if manifest_path.exists():
            manifest = json.loads(manifest_path.read_text())
        else:
            manifest = {
                "schema_version": "1.0",
                "installed_modules": [],
                "upgrade_history": [],
            }

        # Add module to installed list
        if module_id not in manifest["installed_modules"]:
            manifest["installed_modules"].append(module_id)

        # Add to history
        manifest["upgrade_history"].append(
            {
                "module_id": module_id,
                "installed_at": datetime.now().isoformat(),
                "version": self.available_modules[module_id].version,
            }
        )

        manifest_path.write_text(json.dumps(manifest, indent=2))

        # Update in-memory server info
        server.installed_modules.append(module_id)

    def rollback_module(
        self, server_name: str, module_id: str
    ) -> UpgradeResult:
        """Rollback an upgrade module"""
        start_time = time.time()
        result = UpgradeResult(
            success=False,
            server_name=server_name,
            modules_applied=[],
            backup_path=None,
            errors=[],
            warnings=[],
            duration=0,
        )

        try:
            if server_name not in self.servers:
                result.errors.append(f"Server {server_name} not found")
                return result

            server = self.servers[server_name]

            if module_id not in server.installed_modules:
                result.errors.append(f"Module {module_id} not installed")
                return result

            if module_id not in self.available_modules:
                result.warnings.append(
                    (
                        f"Module {module_id} definition not found, "
                        f"manual cleanup may be required"
                    )
                )
            else:
                module = self.available_modules[module_id]

                # Run rollback commands
                for command in module.rollback_commands:
                    print(f"  Rolling back: {command}")
                    subprocess.run(command, shell=True, cwd=server.path)

                # Remove files (be careful here)
                for file_path in module.files.keys():
                    target_path = server.path / file_path
                    if target_path.exists():
                        target_path.unlink()
                        print(f"  Removed: {file_path}")

            # Update manifest
            self._remove_from_server_manifest(server_name, module_id)

            result.success = True
            print(
                f"✅ Successfully rolled back {module_id} from {server_name}"
            )

        except Exception as e:
            result.errors.append(f"Rollback error: {str(e)}")

        finally:
            result.duration = time.time() - start_time

        return result

    def _remove_from_server_manifest(
        self, server_name: str, module_id: str
    ):
        """Remove module from server manifest"""
        server = self.servers[server_name]
        manifest_path = server.path / ".mcp-upgrades.json"

        if manifest_path.exists():
            manifest = json.loads(manifest_path.read_text())

            # Remove from installed modules
            if module_id in manifest["installed_modules"]:
                manifest["installed_modules"].remove(module_id)

            # Add rollback entry to history
            manifest["upgrade_history"].append(
                {
                    "module_id": module_id,
                    "action": "rollback",
                    "rolled_back_at": datetime.now().isoformat(),
                }
            )

            manifest_path.write_text(json.dumps(manifest, indent=2))

            # Update in-memory server info
            if module_id in server.installed_modules:
                server.installed_modules.remove(module_id)

    def batch_upgrade(
        self,
        server_name: str,
        module_ids: List[str],
        dry_run: bool = False,
    ) -> List[UpgradeResult]:
        """Apply multiple upgrade modules in dependency order"""
        results = []

        # Sort modules by dependencies
        sorted_modules = self._sort_modules_by_dependencies(module_ids)

        print(
            f"Upgrading {server_name} with modules: {', '.join(sorted_modules)}"
        )

        for module_id in sorted_modules:
            result = self.apply_upgrade_module(
                server_name, module_id, dry_run
            )
            results.append(result)

            if not result.success:
                print(
                    f"❌ Failed to apply {module_id}, stopping batch upgrade"
                )
                break

        return results

    def _sort_modules_by_dependencies(
        self, module_ids: List[str]
    ) -> List[str]:
        """Sort modules by their dependency requirements"""
        sorted_modules = []
        remaining = set(module_ids)

        while remaining:
            # Find modules with no unmet dependencies
            installable = []
            for module_id in remaining:
                if module_id not in self.available_modules:
                    continue

                module = self.available_modules[module_id]
                unmet_deps = [
                    req
                    for req in module.requirements
                    if req not in sorted_modules and req in remaining
                ]

                if not unmet_deps:
                    installable.append(module_id)

            if not installable:
                # Circular dependency or missing modules
                sorted_modules.extend(list(remaining))
                break

            # Add installable modules
            for module_id in installable:
                sorted_modules.append(module_id)
                remaining.remove(module_id)

        return sorted_modules

    def suggest_upgrades_for_prompt(
        self, prompt: str, server_name: str = None
    ) -> Dict[str, Any]:
        """Analyze prompt and suggest relevant upgrades"""
        suggestions = {
            "prompt": prompt,
            "suggested_modules": [],
            "reasoning": [],
        }

        prompt_lower = prompt.lower()

        # Keyword-based suggestions
        upgrade_keywords = {
            "authentication": [
                "auth",
                "login",
                "jwt",
                "token",
                "security",
                "permission",
            ],
            "logging-enhancement": [
                "log",
                "debug",
                "monitor",
                "trace",
                "error",
            ],
            "caching-redis": [
                "cache",
                "performance",
                "speed",
                "redis",
                "fast",
            ],
            "database-migrations": [
                "database",
                "migration",
                "schema",
                "db",
                "table",
            ],
            "monitoring-metrics": [
                "metrics",
                "prometheus",
                "monitor",
                "health",
                "stats",
            ],
            "api-versioning": [
                "version",
                "api",
                "compatibility",
                "backward",
            ],
        }

        for module_id, keywords in upgrade_keywords.items():
            if any(keyword in prompt_lower for keyword in keywords):
                if module_id in self.available_modules:
                    module = self.available_modules[module_id]
                    suggestions["suggested_modules"].append(
                        {
                            "module_id": module_id,
                            "name": module.name,
                            "description": module.description,
                            "confidence": (
                                "high"
                                if sum(
                                    1
                                    for k in keywords
                                    if k in prompt_lower
                                )
                                > 1
                                else "medium"
                            ),
                        }
                    )
                    suggestions["reasoning"].append(
                        (
                            f"Detected keywords related to {module.name}: "
                            f"{[k for k in keywords if k in prompt_lower]}"
                        )
                    )

        # Server-specific filtering
        if server_name and server_name in self.servers:
            server = self.servers[server_name]
            suggestions["suggested_modules"] = [
                mod
                for mod in suggestions["suggested_modules"]
                if (
                    server.template
                    in self.available_modules[
                        mod["module_id"]
                    ].compatibility
                    or "all"
                    in self.available_modules[
                        mod["module_id"]
                    ].compatibility
                )
            ]

        return suggestions

    def list_available_modules(
        self, template_filter: str = None
    ) -> List[Dict]:
        """List all available upgrade modules"""
        modules = []

        for (
            module_id,
            module,
        ) in self.available_modules.items():
            if (
                template_filter
                and template_filter not in module.compatibility
            ):
                continue

            modules.append(
                {
                    "id": module_id,
                    "name": module.name,
                    "description": module.description,
                    "version": module.version,
                    "compatibility": module.compatibility,
                    "requirements": module.requirements,
                    "conflicts": module.conflicts,
                }
            )

        return modules

    def install_custom_module(self, module_file: str) -> bool:
        """Install a custom upgrade module"""
        try:
            module_path = Path(module_file)
            if not module_path.exists():
                print(f"❌ Module file not found: {module_file}")
                return False

            # Load and validate module
            module_data = json.loads(module_path.read_text())
            module = UpgradeModule(**module_data)

            # Install to modules directory
            target_path = self.modules_dir / f"{module.id}.json"
            target_path.write_text(json.dumps(module_data, indent=2))

            # Reload modules
            self.available_modules[module.id] = module

            print(f"✅ Installed custom module: {module.id}")
            return True

        except Exception as e:
            print(f"❌ Failed to install module: {e}")
            return False

    # Code generation methods for default modules
    def _get_logging_enhancement_code(self) -> str:
        return '''"""
Enhanced logging utilities with structured logging and correlation IDs
"""

import structlog
import logging
import uuid
from contextvars import ContextVar
from typing import Optional

# Context variable for correlation ID
correlation_id: ContextVar[Optional[str]] = ContextVar('correlation_id', default=None)

def setup_logging(level: str = "INFO", format_json: bool = True):
    """Setup structured logging with correlation IDs"""

    logging.basicConfig(
        level=getattr(logging, level.upper()),
        handlers=[logging.StreamHandler()]
    )

    processors = [
        structlog.contextvars.merge_contextvars,
        add_correlation_id,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if format_json:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

def add_correlation_id(logger, method_name, event_dict):
    """Add correlation ID to log events"""
    corr_id = correlation_id.get()
    if corr_id:
        event_dict["correlation_id"] = corr_id
    return event_dict

def new_correlation_id() -> str:
    """Generate a new correlation ID"""
    return str(uuid.uuid4())

def set_correlation_id(corr_id: str):
    """Set correlation ID for current context"""
    correlation_id.set(corr_id)

# Get structured logger
logger = structlog.get_logger()
'''

    def _get_auth_middleware_code(self) -> str:
        return '''"""
JWT Authentication middleware for MCP tools
"""

import jwt
import os
from datetime import datetime, timedelta
from functools import wraps
from typing import Optional, Dict, Any
from mcp.types import McpError, ErrorCode

# Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this")
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = 24

class AuthError(Exception):
    pass

def generate_token(user_id: str, permissions: list = None) -> str:
    """Generate a JWT token"""
    payload = {
        "user_id": user_id,
        "permissions": permissions or [],
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRY_HOURS),
        "iat": datetime.utcnow()
    }

    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def verify_token(token: str) -> Dict[str, Any]:
    """Verify and decode a JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthError("Token has expired")
    except jwt.InvalidTokenError:
        raise AuthError("Invalid token")

def require_auth(permissions: list = None):
    """Decorator to require authentication for MCP tools"""
    def decorator(func):
        @wraps(func)
        async def wrapper(ctx, *args, **kwargs):
            # Extract token from context (implementation depends on your setup)
            token = getattr(ctx, 'auth_token', None)

            if not token:
                raise McpError(
                    ErrorCode.InvalidRequest,
                    "Authentication required"
                )

            try:
                payload = verify_token(token)

                # Check permissions if specified
                if permissions:
                    user_permissions = payload.get("permissions", [])
                    if not any(perm in user_permissions for perm in permissions):
                        raise McpError(
                            ErrorCode.InvalidRequest,
                            "Insufficient permissions"
                        )

                # Add user info to context
                ctx.user_id = payload["user_id"]
                ctx.permissions = payload.get("permissions", [])

                return await func(ctx, *args, **kwargs)

            except AuthError as e:
                raise McpError(ErrorCode.InvalidRequest, str(e))

        return wrapper
    return decorator

# Example usage:
# @require_auth(permissions=["admin"])
# async def admin_tool(ctx, ...):
#     pass
'''

    def _get_redis_cache_code(self) -> str:
        return '''"""
Redis-based caching utilities for MCP servers
"""

import json
import os
import hashlib
from typing import Any, Optional, Callable
import redis.asyncio as redis
from functools import wraps

# Redis configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
CACHE_TTL = int(os.getenv("CACHE_TTL", "300"))  # 5 minutes default

# Redis client
_redis_client = None

async def get_redis_client():
    """Get Redis client instance"""
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(REDIS_URL)
    return _redis_client

def cache_key(*args, **kwargs) -> str:
    """Generate cache key from arguments"""
    key_data = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True)
    return hashlib.md5(key_data.encode()).hexdigest()

def cached(ttl: int = CACHE_TTL, key_prefix: str = "mcp"):
    """Decorator to cache function results in Redis"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            func_name = func.__name__
            key = f"{key_prefix}:{func_name}:{cache_key(*args, **kwargs)}"

            # Try to get from cache
            client = await get_redis_client()
            cached_result = await client.get(key)

            if cached_result:
                return json.loads(cached_result)

            # Execute function and cache result
            result = await func(*args, **kwargs)

            # Cache the result
            await client.setex(
                key,
                ttl,
                json.dumps(result, default=str)
            )

            return result

        return wrapper
    return decorator

async def invalidate_cache(pattern: str):
    """Invalidate cache entries matching pattern"""
    client = await get_redis_client()
    keys = await client.keys(pattern)
    if keys:
        await client.delete(*keys)

async def get_cache_stats() -> dict:
    """Get cache statistics"""
    client = await get_redis_client()
    info = await client.info()
    return {
        "connected_clients": info.get("connected_clients", 0),
        "used_memory": info.get("used_memory_human", "0B"),
        "keyspace_hits": info.get("keyspace_hits", 0),
        "keyspace_misses": info.get("keyspace_misses", 0)
    }

# Example usage:
# @cached(ttl=600, key_prefix="weather")
# async def get_weather_data(city: str):
#     # Expensive API call
#     pass
'''

    def _get_migration_env_code(self) -> str:
        return '''"""
Alembic migration environment
"""

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os

# Import your model's Base
# from src.models import Base
# target_metadata = Base.metadata
target_metadata = None

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

def get_url():
    return os.getenv("DATABASE_URL", "sqlite:///./app.db")

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode."""
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
'''

    def _get_migration_template_code(self) -> str:
        return '''"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade() -> None:
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
'''

    def _get_database_utils_code(self) -> str:
        return '''"""
Database utilities with migration support
"""

import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from alembic import command
from alembic.config import Config

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./app.db")

engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_db_session():
    """Get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

def run_migrations():
    """Run database migrations"""
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")

def create_migration(message: str):
    """Create a new migration"""
    alembic_cfg = Config("alembic.ini")
    command.revision(alembic_cfg, autogenerate=True, message=message)
'''

    def _get_metrics_code(self) -> str:
        return '''"""
Prometheus metrics collection for MCP servers
"""

import time
import os
from functools import wraps
from prometheus_client import (
    Counter, Histogram, Gauge, start_http_server, CONTENT_TYPE_LATEST,
    generate_latest
)
from typing import Callable

# Metrics
REQUEST_COUNT = Counter(
    'mcp_requests_total',
    'Total MCP requests',
    ['server_name', 'tool_name', 'status']
)

REQUEST_DURATION = Histogram(
    'mcp_request_duration_seconds',
    'MCP request duration in seconds',
    ['server_name', 'tool_name']
)

ACTIVE_CONNECTIONS = Gauge(
    'mcp_active_connections',
    'Number of active MCP connections',
    ['server_name']
)

TOOL_ERRORS = Counter(
    'mcp_tool_errors_total',
    'Total tool execution errors',
    ['server_name', 'tool_name', 'error_type']
)

SERVER_INFO = Gauge(
    'mcp_server_info',
    'Server information',
    ['server_name', 'version', 'template']
)

def setup_metrics(server_name: str, port: int = 8001):
    """Setup metrics collection"""
    # Start metrics server
    start_http_server(port)

    # Set server info
    server_version = os.getenv("SERVER_VERSION", "unknown")
    server_template = os.getenv("SERVER_TEMPLATE", "unknown")
    SERVER_INFO.labels(
        server_name=server_name,
        version=server_version,
        template=server_template
    ).set(1)

    print(f"📊 Metrics server started on port {port}")

def track_requests(server_name: str):
    """Decorator to track request metrics"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            tool_name = func.__name__
            start_time = time.time()

            try:
                result = await func(*args, **kwargs)
                REQUEST_COUNT.labels(
                    server_name=server_name,
                    tool_name=tool_name,
                    status="success"
                ).inc()
                return result

            except Exception as e:
                REQUEST_COUNT.labels(
                    server_name=server_name,
                    tool_name=tool_name,
                    status="error"
                ).inc()

                TOOL_ERRORS.labels(
                    server_name=server_name,
                    tool_name=tool_name,
                    error_type=type(e).__name__
                ).inc()

                raise
            finally:
                duration = time.time() - start_time
                REQUEST_DURATION.labels(
                    server_name=server_name,
                    tool_name=tool_name
                ).observe(duration)

        return wrapper
    return decorator

def connection_tracker(server_name: str):
    """Context manager to track connections"""
    class ConnectionTracker:
        def __enter__(self):
            ACTIVE_CONNECTIONS.labels(server_name=server_name).inc()
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            ACTIVE_CONNECTIONS.labels(server_name=server_name).dec()

    return ConnectionTracker()

# Example usage:
# setup_metrics("my-server", port=8001)
#
# @track_requests("my-server")
# async def my_tool(ctx, param: str):
#     with connection_tracker("my-server"):
#         # Tool implementation
#         pass
'''

    def _get_versioning_code(self) -> str:
        return '''"""
API versioning support for MCP servers
"""

import re
from typing import Dict, Any, Callable, Optional
from functools import wraps
from mcp.types import McpError, ErrorCode

# Version registry
_version_registry: Dict[str, Dict[str, Callable]] = {}

def register_version(tool_name: str, version: str):
    """Register a tool version"""
    def decorator(func: Callable):
        if tool_name not in _version_registry:
            _version_registry[tool_name] = {}
        _version_registry[tool_name][version] = func
        return func
    return decorator

def get_tool_version(tool_name: str, version: str) -> Optional[Callable]:
    """Get a specific version of a tool"""
    return _version_registry.get(tool_name, {}).get(version)

def get_latest_version(tool_name: str) -> Optional[Callable]:
    """Get the latest version of a tool"""
    versions = _version_registry.get(tool_name, {})
    if not versions:
        return None

    # Sort versions semantically
    sorted_versions = sorted(versions.keys(), reverse=True)
    return versions[sorted_versions[0]]

def version_compatible(requested: str, available: List[str]) -> str:
    """Find compatible version"""
    # Simple compatibility check - can be enhanced
    if requested in available:
        return requested

    # Find highest compatible version
    req_parts = list(map(int, requested.split('.')))

    compatible = []
    for version in available:
        ver_parts = list(map(int, version.split('.')))

        # Major version must match, minor can be higher
        if (ver_parts[0] == req_parts[0] and
            ver_parts[1] >= req_parts[1]):
            compatible.append(version)

    return max(compatible) if compatible else None

def versioned_tool(default_version: str = "1.0"):
    """Decorator for versioned tools"""
    def decorator(func: Callable):
        tool_name = func.__name__

        @wraps(func)
        async def wrapper(ctx, *args, **kwargs):
            # Extract version from context or use default
            requested_version = getattr(ctx, 'api_version', default_version)

            # Find appropriate version
            available_versions = list(_version_registry.get(tool_name, {}).keys())

            if not available_versions:
                # No versioned implementations, use original
                return await func(ctx, *args, **kwargs)

            compatible_version = version_compatible(
                requested_version, available_versions
            )

            if not compatible_version:
                raise McpError(
                    ErrorCode.InvalidRequest,
                    f"No compatible version found for {tool_name} v{requested_version}"
                )

            # Call appropriate version
            versioned_func = _version_registry[tool_name][compatible_version]
            return await versioned_func(ctx, *args, **kwargs)

        return wrapper
    return decorator

# Backward compatibility helpers
def deprecated(version: str, message: str = ""):
    """Mark a tool version as deprecated"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(ctx, *args, **kwargs):
            # Log deprecation warning
            print(f"⚠️  Warning: {func.__name__} v{version} is deprecated. {message}")
            return await func(ctx, *args, **kwargs)
        return wrapper
    return decorator

# Example usage:
# @versioned_tool(default_version="1.0")
# async def get_data(ctx, param: str):
#     # This is the main implementation
#     pass
#
# @register_version("get_data", "1.0")
# async def get_data_v1(ctx, param: str):
#     # v1.0 implementation
#     pass
#
# @register_version("get_data", "2.0")
# async def get_data_v2(ctx, param: str, new_param: str = "default"):
#     # v2.0 implementation with new parameter
#     pass
'''


def main_upgrader():
    parser = argparse.ArgumentParser(
        description="MCP Server Upgrader - Modular upgrade system for MCP servers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  mcp-upgrader analyze my-server
  mcp-upgrader suggest "I need authentication for my server" my-server
  mcp-upgrader install my-server authentication logging-enhancement
  mcp-upgrader rollback my-server authentication
  mcp-upgrader list-modules --template python-fastmcp
        """,
    )

    subparsers = parser.add_subparsers(
        dest="command", help="Available commands"
    )

    # Analyze command
    analyze_parser = subparsers.add_parser(
        "analyze", help="Analyze server for upgrades"
    )
    analyze_parser.add_argument("server", help="Server name")

    # Suggest command
    suggest_parser = subparsers.add_parser(
        "suggest", help="Suggest upgrades based on prompt"
    )
    suggest_parser.add_argument(
        "prompt", help="Description of what you need"
    )
    suggest_parser.add_argument(
        "server", nargs="?", help="Server name (optional)"
    )

    # Install command
    install_parser = subparsers.add_parser(
        "install", help="Install upgrade modules"
    )
    install_parser.add_argument("server", help="Server name")
    install_parser.add_argument(
        "modules", nargs="+", help="Module IDs to install"
    )
    install_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Dry run mode",
    )

    # Rollback command
    rollback_parser = subparsers.add_parser(
        "rollback", help="Rollback upgrade module"
    )
    rollback_parser.add_argument("server", help="Server name")
    rollback_parser.add_argument("module", help="Module ID to rollback")

    # List modules command
    list_parser = subparsers.add_parser(
        "list-modules", help="List available modules"
    )
    list_parser.add_argument("--template", help="Filter by template")

    # Install custom module command
    custom_parser = subparsers.add_parser(
        "install-module", help="Install custom module"
    )
    custom_parser.add_argument(
        "module_file", help="Path to module JSON file"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    upgrader = MCPUpgrader()

    if args.command == "analyze":
        analysis = upgrader.analyze_server(args.server)
        print(json.dumps(analysis, indent=2))

    elif args.command == "suggest":
        suggestions = upgrader.suggest_upgrades_for_prompt(
            args.prompt, args.server
        )
        print(json.dumps(suggestions, indent=2))

    elif args.command == "install":
        results = upgrader.batch_upgrade(
            args.server, args.modules, args.dry_run
        )

        print(f"\\nUpgrade Results for {args.server}:")
        print("=" * 50)

        for result in results:
            status = "✅ SUCCESS" if result.success else "❌ FAILED"
            module_name = (
                result.modules_applied[0] if result.modules_applied else 'Unknown'
            )
            print(f"{status} {module_name}")

            if result.errors:
                for error in result.errors:
                    print(f"  Error: {error}")

            if result.warnings:
                for warning in result.warnings:
                    print(f"  Warning: {warning}")

        # Overall status
        all_success = all(r.success for r in results)
        if all_success:
            print("\\n🎉 All modules installed successfully!")
        else:
            print("\\n💥 Some modules failed to install")
            sys.exit(1)

    elif args.command == "rollback":
        result = upgrader.rollback_module(args.server, args.module)

        if result.success:
            print(f"✅ Successfully rolled back {args.module}")
        else:
            print(f"❌ Failed to rollback {args.module}")
            for error in result.errors:
                print(f"  Error: {error}")
            sys.exit(1)

    elif args.command == "list-modules":
        modules = upgrader.list_available_modules(args.template)

        print("Available Upgrade Modules:")
        print("=" * 50)

        for module in modules:
            print(f"📦 {module['id']}")
            print(f"   Name: {module['name']}")
            print(f"   Description: {module['description']}")
            print(f"   Version: {module['version']}")
            print(f"   Compatible: {', '.join(module['compatibility'])}")

            if module["requirements"]:
                print(f"   Requires: {', '.join(module['requirements'])}")

            if module["conflicts"]:
                print(f"   Conflicts: {', '.join(module['conflicts'])}")

            print()

    elif args.command == "install-module":
        success = upgrader.install_custom_module(args.module_file)
        if not success:
            sys.exit(1)


if __name__ == "__main__":
    main_upgrader()
