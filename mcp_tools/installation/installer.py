#!/usr/bin/env python3
"""
MCP System Installer
Port of the main installer to the src/ module structure
"""

import sys
import json
import shutil
from pathlib import Path


class MCPSystemInstaller:
    """Main installer class for MCP System"""

    def __init__(self, install_dir: str = None):
        self.home = Path.home()
        self.install_dir = (Path(install_dir) if install_dir
                            else self.home / ".mcp-system")
        self.bin_dir = self.home / "bin"
        self.claude_dir = self.home / ".claude"

    def check_prerequisites(self) -> bool:
        """Check system prerequisites"""
        # Check Python version
        if sys.version_info < (3, 8):
            print(f"❌ Python 3.8+ required, found "
                  f"{sys.version_info.major}.{sys.version_info.minor}")
            return False

        # Check if git is available
        if not shutil.which("git"):
            print("⚠️  Git not found - some features may be limited")

        return True

    def create_directories(self) -> bool:
        """Create necessary directories"""
        try:
            directories = [
                self.install_dir,
                self.install_dir / "components",
                self.install_dir / "docs",
                self.install_dir / "templates",
                self.install_dir / "backups",
                self.install_dir / "logs",
                self.bin_dir,
                self.claude_dir
            ]

            for directory in directories:
                directory.mkdir(parents=True, exist_ok=True)

            return True
        except Exception as e:
            print(f"❌ Failed to create directories: {e}")
            return False

    def install_components(self) -> bool:
        """Install MCP components"""
        try:
            # Get the current script directory
            current_dir = Path(__file__).parent.parent
            core_dir = current_dir / "core"

            # Copy core components
            if core_dir.exists():
                for file in core_dir.glob("*.py"):
                    dest = self.install_dir / "components" / file.name
                    shutil.copy2(file, dest)
                    dest.chmod(0o755)

            return True
        except Exception as e:
            print(f"❌ Failed to install components: {e}")
            return False

    def setup_claude_integration(self) -> bool:
        """Setup Claude Code integration"""
        try:
            config_file = self.claude_dir / "claude_desktop_config.json"

            # Create basic MCP configuration
            mcp_config = {
                "mcpServers": {
                    "mcp-system": {
                        "command": str(self.bin_dir / "mcp-universal"),
                        "args": ["router"],
                        "env": {
                            "MCP_SYSTEM_PATH": str(self.install_dir),
                            "MCP_AUTO_DISCOVERY": "true"
                        }
                    }
                }
            }

            # Merge with existing config if it exists
            if config_file.exists():
                with open(config_file, 'r') as f:
                    existing = json.load(f)

                if "mcpServers" not in existing:
                    existing["mcpServers"] = {}

                existing["mcpServers"]["mcp-system"] = (
                    mcp_config["mcpServers"]["mcp-system"])

                with open(config_file, 'w') as f:
                    json.dump(existing, f, indent=2)
            else:
                with open(config_file, 'w') as f:
                    json.dump(mcp_config, f, indent=2)

            return True
        except Exception as e:
            print(f"❌ Failed to setup Claude integration: {e}")
            return False


def main():
    """Main installer entry point"""
    installer = MCPSystemInstaller()

    print("🚀 MCP System Installer")
    print("=" * 40)

    if not installer.check_prerequisites():
        sys.exit(1)

    if not installer.create_directories():
        sys.exit(1)

    if not installer.install_components():
        sys.exit(1)

    if not installer.setup_claude_integration():
        sys.exit(1)

    print("✅ MCP System installation complete!")


if __name__ == "__main__":
    main()
