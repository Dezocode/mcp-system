#!/usr/bin/env python3
"""
Universal MCP System Installer
Packages all MCP components and creates permissionless bridge for Claude Code CLI
"""

import os
import sys
import json
import shutil
import subprocess
import platform
from pathlib import Path
from typing import Dict, List, Optional
import tempfile
import zipfile

class MCPSystemInstaller:
    def __init__(self):
        self.home = Path.home()
        self.install_dir = self.home / ".mcp-system"
        self.bin_dir = self.home / "bin"
        self.claude_settings_dir = self.home / ".claude"
        self.current_dir = Path(__file__).parent
        
        # Components to package
        self.components = {
            "mcp": "Universal MCP server launcher",
            "mcp-router.py": "Intelligent server router",
            "claude-mcp.sh": "Claude integration helper", 
            "mcp-create-server.py": "Server template generator",
            "mcp-test-framework.py": "Testing framework",
            "mcp-upgrader.py": "Modular upgrade system",
            "claude-upgrade.sh": "Upgrade integration helper"
        }
        
        self.documentation = {
            "MCP-Complete-Documentation.md": "Complete system documentation",
            "MCP-Upgrader-Documentation.md": "Upgrade system documentation", 
            "MCP-Quick-Start-Guide.md": "Quick start guide"
        }

    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are met"""
        print("🔍 Checking prerequisites...")
        
        required = ["python3", "git"]
        missing = []
        
        for cmd in required:
            if shutil.which(cmd) is None:
                missing.append(cmd)
        
        if missing:
            print(f"❌ Missing required tools: {', '.join(missing)}")
            return False
            
        # Check Python version
        if sys.version_info < (3, 8):
            print("❌ Python 3.8+ required")
            return False
            
        print("✅ Prerequisites met")
        return True

    def create_directories(self):
        """Create necessary directories"""
        print("📁 Creating directories...")
        
        directories = [
            self.install_dir,
            self.bin_dir,
            self.claude_settings_dir,
            self.install_dir / "components",
            self.install_dir / "docs",
            self.install_dir / "templates",
            self.install_dir / "backups"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            
        print("✅ Directories created")

    def package_components(self):
        """Package all MCP components"""
        print("📦 Packaging components...")
        
        components_dir = self.install_dir / "components"
        
        # Copy core components
        for component, description in self.components.items():
            source = self.current_dir / component
            dest = components_dir / component
            
            if source.exists():
                shutil.copy2(source, dest)
                # Make executable if it's a script
                if component.endswith(('.sh', '.py')) or not component.endswith(('.md', '.json')):
                    dest.chmod(0o755)
                print(f"  ✅ {component}")
            else:
                print(f"  ⚠️  {component} not found, creating placeholder")
                self.create_placeholder(dest, description)

    def package_documentation(self):
        """Package documentation"""
        print("📚 Packaging documentation...")
        
        docs_dir = self.install_dir / "docs"
        
        for doc, description in self.documentation.items():
            source = self.current_dir / doc
            dest = docs_dir / doc
            
            if source.exists():
                shutil.copy2(source, dest)
                print(f"  ✅ {doc}")
            else:
                print(f"  ⚠️  {doc} not found")

    def create_placeholder(self, path: Path, description: str):
        """Create placeholder for missing components"""
        if path.suffix == '.py':
            content = f'''#!/usr/bin/env python3
"""
{description}
Placeholder - Component not found during installation
"""
print("⚠️  This component was not found during installation")
print("Please check the installation or contact support")
'''
        elif path.suffix == '.sh':
            content = f'''#!/bin/bash
# {description}
# Placeholder - Component not found during installation
echo "⚠️  This component was not found during installation"
echo "Please check the installation or contact support"
'''
        else:
            content = f"# {description}\nPlaceholder - Component not found during installation"
            
        path.write_text(content)

    def create_universal_launcher(self):
        """Create universal MCP launcher that works in any project"""
        print("🚀 Creating universal launcher...")
        
        launcher_content = f'''#!/usr/bin/env python3
"""
Universal MCP System Launcher
Auto-detects and initializes MCP system in any project
"""

import os
import sys
import json
from pathlib import Path
import subprocess

class MCPBridge:
    def __init__(self):
        self.home = Path.home()
        self.install_dir = self.home / ".mcp-system"
        self.components_dir = self.install_dir / "components"
        self.current_project = Path.cwd()
        
    def detect_project_type(self):
        """Detect current project type and configuration"""
        project_indicators = {{
            "package.json": "nodejs",
            "pyproject.toml": "python",
            "Cargo.toml": "rust", 
            "go.mod": "go",
            ".claude": "claude-project"
        }}
        
        for indicator, project_type in project_indicators.items():
            if (self.current_project / indicator).exists():
                return project_type
        return "generic"
    
    def initialize_project_mcp(self):
        """Initialize MCP system for current project"""
        project_type = self.detect_project_type()
        
        print(f"🎯 Detected project type: {{project_type}}")
        print(f"📍 Current directory: {{self.current_project}}")
        
        # Create project-specific MCP configuration
        mcp_config_dir = self.current_project / ".mcp"
        mcp_config_dir.mkdir(exist_ok=True)
        
        config = {{
            "project_type": project_type,
            "mcp_system_path": str(self.install_dir),
            "servers": {{}},
            "claude_integration": True,
            "auto_start": ["mem0"],
            "project_root": str(self.current_project)
        }}
        
        config_file = mcp_config_dir / "config.json"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
            
        print(f"✅ MCP configuration created: {{config_file}}")
        
        # Create project-specific launcher
        self.create_project_launcher()
        
        # Initialize Claude settings integration
        self.setup_claude_integration()
        
        return config
    
    def create_project_launcher(self):
        """Create project-specific MCP launcher"""
        launcher_path = self.current_project / "mcp"
        
        launcher_content = '''#!/bin/bash
# Project-specific MCP launcher
# Auto-generated by MCP System Installer

MCP_SYSTEM_DIR="{install_dir}"
PROJECT_ROOT="$(pwd)"

# Source the universal MCP system
export PATH="$MCP_SYSTEM_DIR/components:$PATH"
export MCP_PROJECT_ROOT="$PROJECT_ROOT"

# Forward all commands to universal MCP launcher
exec "$MCP_SYSTEM_DIR/components/mcp" "$@"
'''.format(install_dir=self.install_dir)
        
        with open(launcher_path, 'w') as f:
            f.write(launcher_content)
        launcher_path.chmod(0o755)
        
        print(f"✅ Project launcher created: {{launcher_path}}")
    
    def setup_claude_integration(self):
        """Setup Claude Code CLI integration"""
        claude_dir = self.current_project / ".claude"
        claude_dir.mkdir(exist_ok=True)
        
        # Create Claude-specific MCP configuration
        claude_mcp_config = {{
            "mcpServers": {{}},
            "mcp_system_integration": {{
                "enabled": True,
                "system_path": str(self.install_dir),
                "auto_discovery": True,
                "project_root": str(self.current_project)
            }}
        }}
        
        claude_config_file = claude_dir / "claude_desktop_config.json"
        
        # Merge with existing configuration if present
        if claude_config_file.exists():
            try:
                with open(claude_config_file, 'r') as f:
                    existing_config = json.load(f)
                existing_config.update(claude_mcp_config)
                claude_mcp_config = existing_config
            except json.JSONDecodeError:
                print("⚠️  Existing Claude config invalid, creating new one")
        
        with open(claude_config_file, 'w') as f:
            json.dump(claude_mcp_config, f, indent=2)
            
        print(f"✅ Claude integration configured: {{claude_config_file}}")
    
    def run(self, args):
        """Main entry point"""
        if not self.install_dir.exists():
            print("❌ MCP system not installed. Run install-mcp-system.py first")
            return 1
            
        if len(args) > 1 and args[1] == "init":
            self.initialize_project_mcp()
            return 0
            
        # Forward to appropriate MCP component
        if len(args) > 1:
            command = args[1]
            component_map = {{
                "create": "mcp-create-server.py",
                "test": "mcp-test-framework.py", 
                "upgrade": "claude-upgrade.sh",
                "router": "mcp-router.py"
            }}
            
            if command in component_map:
                component_path = self.components_dir / component_map[command]
                if component_path.exists():
                    subprocess.run([str(component_path)] + args[2:])
                    return 0
        
        # Default to main MCP launcher
        main_launcher = self.components_dir / "mcp"
        if main_launcher.exists():
            subprocess.run([str(main_launcher)] + args[1:])
        else:
            print("❌ MCP launcher not found")
            return 1

if __name__ == "__main__":
    bridge = MCPBridge()
    sys.exit(bridge.run(sys.argv))
'''
        
        launcher_path = self.bin_dir / "mcp-bridge"
        launcher_path.write_text(launcher_content)
        launcher_path.chmod(0o755)
        
        print("✅ Universal launcher created")

    def create_claude_settings_integration(self):
        """Create safe Claude settings integration"""
        print("⚙️  Setting up Claude settings integration...")
        
        # Create Claude MCP settings template
        claude_settings = {
            "mcpServers": {
                "mcp-system": {
                    "command": str(self.bin_dir / "mcp-bridge"),
                    "args": ["router"],
                    "env": {
                        "MCP_SYSTEM_PATH": str(self.install_dir)
                    }
                }
            },
            "mcp_system_integration": {
                "enabled": True,
                "auto_discovery": True,
                "safe_mode": True,
                "system_path": str(self.install_dir)
            }
        }
        
        # Global Claude settings
        global_claude_config = self.claude_settings_dir / "claude_desktop_config.json"
        
        if global_claude_config.exists():
            print("  📝 Backing up existing Claude configuration...")
            backup_path = self.claude_settings_dir / "claude_desktop_config.backup.json"
            shutil.copy2(global_claude_config, backup_path)
            
            try:
                with open(global_claude_config, 'r') as f:
                    existing_config = json.load(f)
                
                # Safely merge configurations
                if "mcpServers" not in existing_config:
                    existing_config["mcpServers"] = {}
                
                existing_config["mcpServers"]["mcp-system"] = claude_settings["mcpServers"]["mcp-system"]
                existing_config["mcp_system_integration"] = claude_settings["mcp_system_integration"]
                
                with open(global_claude_config, 'w') as f:
                    json.dump(existing_config, f, indent=2)
                    
                print("  ✅ Merged with existing Claude configuration")
                
            except json.JSONDecodeError:
                print("  ⚠️  Existing Claude config invalid, creating new one")
                with open(global_claude_config, 'w') as f:
                    json.dump(claude_settings, f, indent=2)
        else:
            with open(global_claude_config, 'w') as f:
                json.dump(claude_settings, f, indent=2)
            print("  ✅ Created new Claude configuration")

    def create_initialization_hook(self):
        """Create project initialization hook"""
        print("🔗 Creating initialization hook...")
        
        hook_content = '''#!/usr/bin/env python3
"""
Auto-initialization hook for new projects
Detects when Claude Code is used in a new project and offers MCP setup
"""

import os
import sys
from pathlib import Path
import json

def detect_new_project():
    """Detect if this is a new project without MCP setup"""
    current_dir = Path.cwd()
    return not (current_dir / ".mcp").exists()

def offer_mcp_setup():
    """Offer to set up MCP for this project"""
    print("🎯 MCP System detected!")
    print("This project doesn't have MCP configured yet.")
    
    response = input("Would you like to initialize MCP for this project? (y/N): ")
    if response.lower() in ['y', 'yes']:
        os.system("mcp-bridge init")
        print("✅ MCP system initialized for this project")
        print("You can now use 'mcp' commands in this project")
    else:
        print("ℹ️  You can initialize MCP later with: mcp-bridge init")

if __name__ == "__main__":
    if detect_new_project():
        offer_mcp_setup()
'''
        
        hook_path = self.install_dir / "components" / "auto-init-hook.py"
        hook_path.write_text(hook_content)
        hook_path.chmod(0o755)
        
        print("✅ Initialization hook created")

    def setup_path_integration(self):
        """Setup PATH integration for universal access"""
        print("🔧 Setting up PATH integration...")
        
        # Add to various shell configs
        shell_configs = [
            self.home / ".bashrc",
            self.home / ".zshrc", 
            self.home / ".profile"
        ]
        
        path_line = f'export PATH="{self.bin_dir}:$PATH"'
        mcp_line = f'export MCP_SYSTEM_PATH="{self.install_dir}"'
        
        for config_file in shell_configs:
            if config_file.exists():
                content = config_file.read_text()
                
                # Check if already added
                if str(self.bin_dir) not in content:
                    with open(config_file, 'a') as f:
                        f.write(f"\n# MCP System Integration\n")
                        f.write(f"{path_line}\n")
                        f.write(f"{mcp_line}\n")
                    print(f"  ✅ Added to {config_file.name}")
                else:
                    print(f"  ✅ Already configured in {config_file.name}")

    def create_installer_package(self):
        """Create distributable installer package"""
        print("📦 Creating installer package...")
        
        package_dir = self.current_dir / "mcp-system-package"
        package_dir.mkdir(exist_ok=True)
        
        # Create single-file installer
        installer_content = f'''#!/usr/bin/env python3
"""
MCP System One-Click Installer
Contains all components for offline installation
"""

import base64
import gzip
import json
import os
import sys
from pathlib import Path
import tempfile
import zipfile

# Embedded package data (base64 encoded gzipped tar)
PACKAGE_DATA = """
{self.encode_package()}
"""

def extract_and_install():
    """Extract embedded package and run installation"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Decode and extract package
        package_bytes = base64.b64decode(PACKAGE_DATA)
        package_path = Path(temp_dir) / "mcp-system.tar.gz"
        package_path.write_bytes(package_bytes)
        
        # Extract
        import tarfile
        with tarfile.open(package_path) as tar:
            tar.extractall(temp_dir)
        
        # Run installer
        installer_path = Path(temp_dir) / "install-mcp-system.py"
        os.system(f"python3 {{installer_path}}")

if __name__ == "__main__":
    extract_and_install()
'''
        
        package_installer = package_dir / "install-mcp-system-oneclick.py"
        package_installer.write_text(installer_content)
        package_installer.chmod(0o755)
        
        print("✅ Installer package created")

    def encode_package(self) -> str:
        """Encode installation files for embedding"""
        # This would contain the actual package encoding logic
        # For now, return placeholder
        return "placeholder_package_data"

    def run_installation(self):
        """Run complete installation process"""
        print("🚀 Starting MCP System Installation")
        print("=" * 50)
        
        try:
            # Check prerequisites
            if not self.check_prerequisites():
                return False
            
            # Create directories
            self.create_directories()
            
            # Package components
            self.package_components()
            self.package_documentation()
            
            # Create universal launcher
            self.create_universal_launcher()
            
            # Setup Claude integration
            self.create_claude_settings_integration()
            
            # Create initialization hook
            self.create_initialization_hook()
            
            # Setup PATH integration
            self.setup_path_integration()
            
            # Create installer package
            self.create_installer_package()
            
            print("\n" + "=" * 50)
            print("🎉 MCP System Installation Complete!")
            print("\n📋 Next Steps:")
            print("1. Restart your terminal or run: source ~/.bashrc")
            print("2. Navigate to any project directory")
            print("3. Run: mcp-bridge init")
            print("4. Start using: mcp list, mcp-create-server, etc.")
            print("\n📚 Documentation available in:")
            print(f"   {self.install_dir / 'docs'}")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Installation failed: {e}")
            return False

def main():
    installer = MCPSystemInstaller()
    success = installer.run_installation()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()