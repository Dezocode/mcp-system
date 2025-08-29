#!/usr/bin/env python3
"""
Permissionless Claude Code CLI Bridge for MCP System
Automatically detects Claude Code usage and provides seamless MCP integration
"""

import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.config.cross_platform import cross_platform


class ClaudeCodeMCPBridge:
    def __init__(self):
        self.home = Path.home()
        self.claude_dir = self.home / ".claude"
        self.mcp_system_dir = self.home / ".mcp-system"
        self.current_project = Path.cwd()
        self.project_mcp_dir = self.current_project / ".mcp"

        # Auto-detection patterns
        self.claude_indicators = [
            ".claude",
            "claude_desktop_config.json",
            ".claude-session",
            "CLAUDE.md",
        ]

        self.project_patterns = {
            "python": [
                "pyproject.toml",
                "setup.py",
                "requirements.txt",
                "Pipfile",
            ],
            "nodejs": [
                "package.json",
                "node_modules",
                "yarn.lock",
            ],
            "rust": ["Cargo.toml", "Cargo.lock"],
            "go": ["go.mod", "go.sum"],
            "web": [
                "index.html",
                "src/",
                "public/",
            ],
            "git": [".git"],
        }

    def detect_claude_code_usage(self) -> bool:
        """Detect if Claude Code is being used in current context"""
        # Check for Claude-specific environment variables
        claude_env_vars = [
            "CLAUDE_CODE_SESSION",
            "CLAUDE_DESKTOP_CONFIG",
            "ANTHROPIC_API_KEY",
        ]

        for var in claude_env_vars:
            if os.getenv(var):
                return True

        # Check for Claude configuration files
        for indicator in self.claude_indicators:
            if (self.current_project / indicator).exists():
                return True
            if (self.home / indicator).exists():
                return True

        # Check if running in Claude Code context
        if "claude" in str(sys.argv[0]).lower():
            return True

        return False

    def detect_project_type(self) -> List[str]:
        """Detect current project type(s)"""
        detected_types = []

        for (
            project_type,
            patterns,
        ) in self.project_patterns.items():
            for pattern in patterns:
                if (self.current_project / pattern).exists():
                    detected_types.append(project_type)
                    break

        return detected_types if detected_types else ["generic"]

    def get_claude_config_path(
        self,
    ) -> Optional[Path]:
        """Find Claude configuration file"""
        possible_paths = [
            self.current_project / ".claude" / "claude_desktop_config.json",
            self.current_project / "claude_desktop_config.json",
            self.claude_dir / "claude_desktop_config.json",
            Path.home()
            / "Library"
            / "Application Support"
            / "Claude"
            / "claude_desktop_config.json",
            Path.home() / ".config" / "Claude" / "claude_desktop_config.json",
        ]

        for path in possible_paths:
            if path.exists():
                return path

        return None

    def create_safe_mcp_integration(
        self,
    ) -> Dict[str, Any]:
        """Create safe MCP integration configuration"""
        project_types = self.detect_project_type()

        # Base MCP configuration
        mcp_config = {
            "mcpServers": {},
            "mcp_system_integration": {
                "enabled": True,
                "auto_discovery": True,
                "safe_mode": True,
                "project_types": project_types,
                "project_root": str(self.current_project),
                "system_path": str(self.mcp_system_dir),
                "bridge_version": "1.0.0",
                "permissions": {
                    "read_files": True,
                    "write_files": False,  # Safe default
                    "execute_commands": False,  # Safe default
                    "network_access": False,  # Safe default
                },
            },
        }

        # Add project-specific MCP servers based on detected types
        if "python" in project_types:
            mcp_config["mcpServers"]["python-tools"] = {
                "command": str(self.mcp_system_dir / "core" / "mcp-router.py"),
                "args": ["python-tools"],
                "env": {"PROJECT_TYPE": "python"},
            }

        if "nodejs" in project_types:
            mcp_config["mcpServers"]["nodejs-tools"] = {
                "command": str(self.mcp_system_dir / "core" / "mcp-router.py"),
                "args": ["nodejs-tools"],
                "env": {"PROJECT_TYPE": "nodejs"},
            }

        # Always include universal tools
        mcp_config["mcpServers"]["mcp-universal"] = {
            "command": str(self.mcp_system_dir / "components" / "mcp-router.py"),
            "args": ["universal"],
            "env": {
                "PROJECT_ROOT": str(self.current_project),
                "PROJECT_TYPES": ",".join(project_types),
            },
        }

        # Add memory server if available
        if (self.mcp_system_dir / "components" / "mcp").exists():
            mcp_config["mcpServers"]["mem0"] = {
                "command": str(self.mcp_system_dir / "components" / "mcp"),
                "args": [
                    "mem0",
                    "start-for-claude",
                ],
                "env": {"PROJECT_CONTEXT": str(self.current_project)},
            }

        return mcp_config

    def merge_claude_config(self, new_config: Dict[str, Any]) -> bool:
        """Safely merge MCP config with existing Claude configuration"""
        claude_config_path = self.get_claude_config_path()

        if claude_config_path is None:
            # Create new configuration
            claude_config_path = (
                self.current_project / ".claude" / "claude_desktop_config.json"
            )
            claude_config_path.parent.mkdir(parents=True, exist_ok=True)
            existing_config = {}
        else:
            # Load existing configuration
            try:
                with open(claude_config_path, "r") as f:
                    existing_config = json.load(f)
            except json.JSONDecodeError:
                print("⚠️  Existing Claude config invalid, backing up and creating new")
                backup_path = claude_config_path.with_suffix(".backup.json")
                claude_config_path.rename(backup_path)
                existing_config = {}

        # Backup existing configuration
        if claude_config_path.exists():
            backup_path = claude_config_path.with_suffix(
                f".backup.{int(time.time())}.json"
            )
            with open(backup_path, "w") as f:
                json.dump(existing_config, f, indent=2)

        # Safely merge configurations
        if "mcpServers" not in existing_config:
            existing_config["mcpServers"] = {}

        # Only add MCP servers that don't conflict
        for (
            server_name,
            server_config,
        ) in new_config["mcpServers"].items():
            if server_name not in existing_config["mcpServers"]:
                existing_config["mcpServers"][server_name] = server_config
            else:
                # Add with unique name if conflict
                counter = 1
                unique_name = f"{server_name}-{counter}"
                while unique_name in existing_config["mcpServers"]:
                    counter += 1
                    unique_name = f"{server_name}-{counter}"
                existing_config["mcpServers"][unique_name] = server_config

        # Add system integration config
        existing_config["mcp_system_integration"] = new_config["mcp_system_integration"]

        # Write merged configuration
        try:
            with open(claude_config_path, "w") as f:
                json.dump(existing_config, f, indent=2)
            return True
        except Exception as e:
            print(f"❌ Failed to write Claude configuration: {e}")
            return False

    def create_project_mcp_config(self):
        """Create project-specific MCP configuration"""
        self.project_mcp_dir.mkdir(exist_ok=True)

        project_types = self.detect_project_type()

        project_config = {
            "project_info": {
                "name": self.current_project.name,
                "path": str(self.current_project),
                "types": project_types,
                "created": time.time(),
            },
            "mcp_integration": {
                "enabled": True,
                "auto_start": True,
                "safe_mode": True,
            },
            "servers": {
                "enabled": [],
                "available": [
                    "mem0",
                    "python-tools",
                    "nodejs-tools",
                    "universal",
                ],
            },
            "claude_code_integration": {
                "bridge_active": True,
                "config_path": str(self.get_claude_config_path()),
                "last_updated": time.time(),
            },
        }

        config_file = self.project_mcp_dir / "config.json"
        with open(config_file, "w") as f:
            json.dump(project_config, f, indent=2)

        return config_file

    def setup_permissionless_integration(
        self,
    ) -> bool:
        """Setup permissionless integration with Claude Code"""
        print("🔗 Setting up permissionless Claude Code integration...")

        try:
            # 1. Check if MCP system is installed
            if not self.mcp_system_dir.exists():
                print("❌ MCP system not found. Please install first with:")
                print(
                    f"    {cross_platform.get_command('python')} install-mcp-system.py"
                )
                return False

            # 2. Create project MCP configuration
            project_config_path = self.create_project_mcp_config()
            print(f"✅ Project configuration: {project_config_path}")

            # 3. Create safe MCP integration
            mcp_config = self.create_safe_mcp_integration()

            # 4. Merge with Claude configuration
            if self.merge_claude_config(mcp_config):
                print("✅ Claude configuration updated")
            else:
                print("❌ Failed to update Claude configuration")
                return False

            # 5. Create project-specific launchers
            self.create_project_launchers()

            # 6. Setup environment
            self.setup_project_environment()

            print("\n🎉 Permissionless integration complete!")
            print("Claude Code can now seamlessly use MCP tools in this project")

            return True

        except Exception as e:
            print(f"❌ Integration failed: {e}")
            return False

    def create_project_launchers(self):
        """Create project-specific MCP launchers"""
        launchers = {
            "mcp": "Universal MCP launcher",
            "mcp-create": "Create new MCP server",
            "mcp-test": "Test MCP servers",
            "mcp-upgrade": "Upgrade MCP servers",
        }

        for (
            launcher_name,
            description,
        ) in launchers.items():
            launcher_path = self.current_project / launcher_name

            launcher_content = f"""#!/usr/bin/env bash
# {description}
# Auto-generated by Claude Code MCP Bridge

MCP_SYSTEM_DIR="{self.mcp_system_dir}"
PROJECT_ROOT="{self.current_project}"

# Set environment
export MCP_PROJECT_ROOT="$PROJECT_ROOT"
export MCP_SYSTEM_PATH="$MCP_SYSTEM_DIR"

# Map commands to components
case "{launcher_name}" in
    "mcp")
        exec "$MCP_SYSTEM_DIR/components/mcp" "$@"
        ;;
    "mcp-create")
        exec "$MCP_SYSTEM_DIR/core/mcp-create-server.py" "$@"
        ;;
    "mcp-test")
        exec "$MCP_SYSTEM_DIR/core/mcp-test-framework.py" "$@"
        ;;
    "mcp-upgrade")
        exec "$MCP_SYSTEM_DIR/components/claude-upgrade.sh" "$@"
        ;;
esac
"""

            launcher_path.write_text(launcher_content)
            launcher_path.chmod(0o755)

        print(f"✅ Created project launchers: {', '.join(launchers.keys())}")

    def setup_project_environment(self):
        """Setup project-specific environment"""
        # Create .env file if it doesn't exist
        env_file = self.current_project / ".env"
        env_additions = [
            f"MCP_SYSTEM_PATH={self.mcp_system_dir}",
            f"MCP_PROJECT_ROOT={self.current_project}",
            "MCP_BRIDGE_ENABLED=true",
        ]

        if env_file.exists():
            content = env_file.read_text()
            for addition in env_additions:
                if addition.split("=")[0] not in content:
                    content += f"\n{addition}"
            env_file.write_text(content)
        else:
            env_file.write_text("\n".join(env_additions) + "\n")

        print("✅ Environment configured")

    def check_integration_status(
        self,
    ) -> Dict[str, Any]:
        """Check current integration status"""
        status = {
            "claude_detected": self.detect_claude_code_usage(),
            "mcp_system_installed": self.mcp_system_dir.exists(),
            "project_configured": self.project_mcp_dir.exists(),
            "claude_config_found": self.get_claude_config_path() is not None,
            "project_types": self.detect_project_type(),
            "project_launchers": [],
        }

        # Check for project launchers
        launchers = [
            "mcp",
            "mcp-create",
            "mcp-test",
            "mcp-upgrade",
        ]
        for launcher in launchers:
            if (self.current_project / launcher).exists():
                status["project_launchers"].append(launcher)

        return status

    def auto_init_if_needed(self):
        """Automatically initialize MCP if Claude Code is detected"""
        if not self.detect_claude_code_usage():
            return False

        status = self.check_integration_status()

        if not status["mcp_system_installed"]:
            print("🎯 Claude Code detected but MCP system not installed")
            print(f"Run: {cross_platform.get_command('python')} install-mcp-system.py")
            return False

        if not status["project_configured"]:
            print("🎯 Claude Code detected - initializing MCP integration...")
            return self.setup_permissionless_integration()

        print("✅ MCP integration already active")
        return True

    def run_bridge_command(self, args: List[str]):
        """Run bridge command"""
        if len(args) == 0 or args[0] in [
            "help",
            "--help",
            "-h",
        ]:
            self.show_help()
            return

        command = args[0]

        if command == "init":
            self.setup_permissionless_integration()
        elif command == "status":
            status = self.check_integration_status()
            self.show_status(status)
        elif command == "auto-init":
            self.auto_init_if_needed()
        elif command == "config":
            self.show_config()
        else:
            print(f"❌ Unknown command: {command}")
            self.show_help()

    def show_help(self):
        """Show help information"""
        print(
            """
Claude Code MCP Bridge - Permissionless Integration

Commands:
  init        Initialize MCP integration for current project
  status      Show integration status
  auto-init   Auto-initialize if Claude Code detected
  config      Show current configuration
  help        Show this help

Examples:
  claude-code-mcp-bridge init
  claude-code-mcp-bridge status
  claude-code-mcp-bridge auto-init

The bridge automatically detects Claude Code usage and provides
seamless MCP integration without requiring special permissions.
"""
        )

    def show_status(self, status: Dict[str, Any]):
        """Show integration status"""
        print("🔍 Claude Code MCP Bridge Status")
        print("=" * 40)

        indicators = {
            "claude_detected": "Claude Code detected",
            "mcp_system_installed": "MCP system installed",
            "project_configured": "Project configured",
            "claude_config_found": "Claude config found",
        }

        for (
            key,
            description,
        ) in indicators.items():
            icon = "✅" if status[key] else "❌"
            print(f"{icon} {description}")

        print(f"\n📁 Project types: {', '.join(status['project_types'])}")

        if status["project_launchers"]:
            print(f"🚀 Available launchers: {', '.join(status['project_launchers'])}")

        if status["claude_config_found"]:
            config_path = self.get_claude_config_path()
            print(f"⚙️  Claude config: {config_path}")

    def show_config(self):
        """Show current configuration"""
        if self.project_mcp_dir.exists():
            config_file = self.project_mcp_dir / "config.json"
            if config_file.exists():
                with open(config_file, "r") as f:
                    config = json.load(f)
                print(json.dumps(config, indent=2))
            else:
                print("❌ No project configuration found")
        else:
            print("❌ Project not configured for MCP")


def main_bridge():
    bridge = ClaudeCodeMCPBridge()

    # Auto-initialize if no arguments provided and Claude Code detected
    if len(sys.argv) == 1:
        if bridge.detect_claude_code_usage():
            bridge.auto_init_if_needed()
        else:
            bridge.show_help()
    else:
        bridge.run_bridge_command(sys.argv[1:])


if __name__ == "__main__":
    main_bridge()
