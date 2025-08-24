#!/usr/bin/env python3
"""
MCP Tools Watchdog Monitor - File system monitoring for standardized MCP tools structure
"""

import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set

import yaml
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class MCPToolsStandardizer:
    """Handles standardization of MCP tools directory structure and paths"""
    
    def __init__(self, mcp_tools_path: Path):
        self.mcp_tools_path = Path(mcp_tools_path)
        self.monitoring_path = self.mcp_tools_path / "_monitoring"
        self.standards_path = self.mcp_tools_path / "_standards"
        self.templates_path = self.mcp_tools_path / "_templates"
        
        # Ensure monitoring directories exist
        self.monitoring_path.mkdir(exist_ok=True)
        self.standards_path.mkdir(exist_ok=True)
        self.templates_path.mkdir(exist_ok=True)
        
        # Setup logging
        self.setup_logging()
        
        # Standard structure requirements
        self.required_files = {
            "src/main.py",
            "README.md",
            "pyproject.toml",
            ".env.example"
        }
        
        self.recommended_files = {
            "tests/test_server.py",
            "Dockerfile",
            "docker-compose.yml"
        }
        
    def setup_logging(self):
        """Setup logging for monitoring activities"""
        log_file = self.monitoring_path / "watchdog.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def validate_server_structure(self, server_path: Path) -> Dict[str, List[str]]:
        """Validate MCP server directory structure"""
        results = {
            "missing_required": [],
            "missing_recommended": [],
            "extra_files": [],
            "valid": True
        }
        
        if not server_path.is_dir():
            results["valid"] = False
            return results
            
        # Check required files
        for required_file in self.required_files:
            file_path = server_path / required_file
            if not file_path.exists():
                results["missing_required"].append(required_file)
                results["valid"] = False
                
        # Check recommended files
        for rec_file in self.recommended_files:
            file_path = server_path / rec_file
            if not file_path.exists():
                results["missing_recommended"].append(rec_file)
                
        return results
    
    def get_server_directories(self) -> List[Path]:
        """Get all server directories in mcp-tools (excluding system directories)"""
        servers = []
        for item in self.mcp_tools_path.iterdir():
            if (item.is_dir() and 
                not item.name.startswith("_") and 
                not item.name.startswith(".")):
                servers.append(item)
        return servers
    
    def update_path_references(self, old_path: str, new_path: str):
        """Update path references in configuration files"""
        config_files = [
            Path.cwd() / "configs" / ".mcp-servers.json",
            Path.cwd() / ".mcp-server-config.json",
            Path.cwd() / ".mcp-sync-config.json"
        ]
        
        for config_file in config_files:
            if config_file.exists():
                self._update_json_paths(config_file, old_path, new_path)
    
    def _update_json_paths(self, config_file: Path, old_path: str, new_path: str):
        """Update paths in JSON configuration files"""
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            updated = False
            for server_name, server_config in config.items():
                if isinstance(server_config, dict) and 'path' in server_config:
                    if server_config['path'] == old_path:
                        server_config['path'] = new_path
                        updated = True
                        self.logger.info(f"Updated path for {server_name}: {old_path} -> {new_path}")
            
            if updated:
                with open(config_file, 'w') as f:
                    json.dump(config, f, indent=2)
                self.logger.info(f"Updated configuration file: {config_file}")
                
        except Exception as e:
            self.logger.error(f"Error updating {config_file}: {e}")
    
    def standardize_existing_servers(self):
        """Standardize existing server structures"""
        servers = self.get_server_directories()
        
        for server_path in servers:
            self.logger.info(f"Validating server: {server_path.name}")
            validation = self.validate_server_structure(server_path)
            
            if not validation["valid"]:
                self.logger.warning(f"Server {server_path.name} missing required files: {validation['missing_required']}")
                
            if validation["missing_recommended"]:
                self.logger.info(f"Server {server_path.name} missing recommended files: {validation['missing_recommended']}")
    
    def create_server_template(self, server_name: str, template_type: str = "python-official"):
        """Create a new server from template"""
        server_path = self.mcp_tools_path / server_name
        
        if server_path.exists():
            self.logger.error(f"Server {server_name} already exists")
            return False
            
        server_path.mkdir()
        
        # Create standard structure
        (server_path / "src").mkdir()
        (server_path / "tests").mkdir()
        
        # Create main.py template
        main_py_content = self._get_main_py_template(server_name, template_type)
        (server_path / "src" / "main.py").write_text(main_py_content)
        
        # Create other standard files
        self._create_standard_files(server_path, server_name)
        
        self.logger.info(f"Created new MCP server: {server_name}")
        return True
    
    def _get_main_py_template(self, server_name: str, template_type: str) -> str:
        """Get main.py template content"""
        return f'''#!/usr/bin/env python3
"""
{server_name} - MCP Server
Generated using MCP Tools standardized template
"""

import asyncio
import json
import logging
from typing import Any, Dict, List

from mcp.server.fastmcp import FastMCP
from mcp.server.models import InitializationOptions


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the MCP server
mcp = FastMCP("{server_name}")


@mcp.tool()
def hello_world(name: str = "World") -> str:
    """
    Say hello to someone
    
    Args:
        name: The name to greet
        
    Returns:
        A greeting message
    """
    return f"Hello, {{name}}! This is {server_name} MCP Server."


@mcp.resource("config://info")
def get_server_info() -> Dict[str, Any]:
    """Get server information"""
    return {{
        "name": "{server_name}",
        "version": "1.0.0",
        "description": "MCP Server created with standardized template"
    }}


async def main():
    """Main entry point"""
    try:
        # Run the server
        async with mcp.run_server() as server:
            await server.serve()
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {{e}}")


if __name__ == "__main__":
    asyncio.run(main())
'''
    
    def _create_standard_files(self, server_path: Path, server_name: str):
        """Create standard files for a new server"""
        
        # pyproject.toml
        pyproject_content = f'''[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "{server_name}"
version = "1.0.0"
description = "MCP Server - {server_name}"
authors = [{{name = "MCP System", email = "admin@mcpsystem.dev"}}]
dependencies = [
    "mcp>=1.0.0",
    "fastmcp>=0.1.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "black>=23.9.0",
    "isort>=5.12.0",
]

[tool.black]
line-length = 88
target-version = ['py38']

[tool.isort]
profile = "black"
'''
        (server_path / "pyproject.toml").write_text(pyproject_content)
        
        # README.md
        readme_content = f'''# {server_name} MCP Server

## Overview

{server_name} is an MCP (Model Context Protocol) server that provides [describe functionality].

## Installation

```bash
cd mcp-tools/{server_name}
pip install -e .
```

## Usage

### As MCP Server

Add to your MCP client configuration:

```json
{{
  "{server_name}": {{
    "command": "python",
    "args": ["src/main.py"],
    "cwd": "mcp-tools/{server_name}"
  }}
}}
```

### Direct Usage

```bash
python src/main.py
```

## Configuration

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
# Edit .env with your configuration
```

## Development

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black src/ tests/
isort src/ tests/
```

## API

### Tools

- `hello_world`: Say hello to someone

### Resources

- `config://info`: Get server information

## License

MIT License - see LICENSE file for details
'''
        (server_path / "README.md").write_text(readme_content)
        
        # .env.example
        env_example = f'''# {server_name} MCP Server Configuration

# Server settings
SERVER_NAME={server_name}
LOG_LEVEL=INFO

# Add your environment variables here
# EXAMPLE_API_KEY=your_api_key_here
'''
        (server_path / ".env.example").write_text(env_example)
        
        # Test file
        test_content = f'''#!/usr/bin/env python3
"""
Tests for {server_name} MCP Server
"""

import pytest
import asyncio
from src.main import mcp


class Test{server_name.replace("-", "").title()}Server:
    """Test cases for {server_name} server"""
    
    def test_hello_world(self):
        """Test hello_world tool"""
        result = mcp.call_tool("hello_world", {{"name": "Test"}})
        assert "Hello, Test!" in result
        
    def test_hello_world_default(self):
        """Test hello_world tool with default name"""
        result = mcp.call_tool("hello_world", {{}})
        assert "Hello, World!" in result
        
    @pytest.mark.asyncio
    async def test_server_info_resource(self):
        """Test server info resource"""
        info = mcp.get_resource("config://info")
        assert info["name"] == "{server_name}"
        assert "version" in info
'''
        (server_path / "tests" / "test_server.py").write_text(test_content)


class MCPToolsEventHandler(FileSystemEventHandler):
    """Handle file system events for MCP Tools directory"""
    
    def __init__(self, standardizer: MCPToolsStandardizer):
        super().__init__()
        self.standardizer = standardizer
        
    def on_created(self, event):
        """Handle file/directory creation"""
        if event.is_directory:
            path = Path(event.src_path)
            if path.parent == self.standardizer.mcp_tools_path:
                # New server directory created
                if not path.name.startswith("_"):
                    self.standardizer.logger.info(f"New server directory detected: {path.name}")
                    # Validate structure after a short delay to allow file creation
                    time.sleep(1)
                    validation = self.standardizer.validate_server_structure(path)
                    if not validation["valid"]:
                        self.standardizer.logger.warning(
                            f"New server {path.name} missing required files: {validation['missing_required']}"
                        )
    
    def on_modified(self, event):
        """Handle file modification"""
        if not event.is_directory:
            path = Path(event.src_path)
            if path.name in [".mcp-servers.json", ".mcp-server-config.json"]:
                self.standardizer.logger.info(f"Configuration file modified: {path.name}")
    
    def on_moved(self, event):
        """Handle file/directory moves"""
        if event.is_directory:
            old_path = Path(event.src_path)
            new_path = Path(event.dest_path)
            
            if (old_path.parent == self.standardizer.mcp_tools_path and 
                new_path.parent == self.standardizer.mcp_tools_path):
                # Server directory renamed
                self.standardizer.logger.info(f"Server renamed: {old_path.name} -> {new_path.name}")
                self.standardizer.update_path_references(
                    f"mcp-tools/{old_path.name}",
                    f"mcp-tools/{new_path.name}"
                )


def main():
    """Main entry point for MCP Tools watchdog monitor"""
    import argparse
    
    parser = argparse.ArgumentParser(description="MCP Tools Watchdog Monitor")
    parser.add_argument("--mcp-tools-path", default="mcp-tools", 
                       help="Path to mcp-tools directory")
    parser.add_argument("--validate-only", action="store_true",
                       help="Only validate existing structure, don't start monitoring")
    parser.add_argument("--create-server", help="Create a new server with given name")
    parser.add_argument("--template", default="python-official", 
                       help="Template type for new server")
    
    args = parser.parse_args()
    
    # Initialize standardizer
    mcp_tools_path = Path(args.mcp_tools_path).resolve()
    standardizer = MCPToolsStandardizer(mcp_tools_path)
    
    if args.create_server:
        # Create new server
        success = standardizer.create_server_template(args.create_server, args.template)
        if success:
            print(f"✅ Created new MCP server: {args.create_server}")
        else:
            print(f"❌ Failed to create server: {args.create_server}")
        return
    
    # Validate existing structure
    print("🔍 Validating existing MCP Tools structure...")
    standardizer.standardize_existing_servers()
    
    if args.validate_only:
        print("✅ Validation complete")
        return
    
    # Start file system monitoring
    event_handler = MCPToolsEventHandler(standardizer)
    observer = Observer()
    observer.schedule(event_handler, str(mcp_tools_path), recursive=True)
    
    print(f"👁️  Starting MCP Tools watchdog monitor on: {mcp_tools_path}")
    print("Press Ctrl+C to stop monitoring")
    
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("🛑 Watchdog monitor stopped")
    
    observer.join()


if __name__ == "__main__":
    main()