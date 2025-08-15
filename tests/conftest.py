"""
Pytest configuration and shared fixtures
"""

import pytest
import tempfile
import os
from pathlib import Path
import shutil

@pytest.fixture(scope="session")
def test_data_dir():
    """Fixture providing test data directory"""
    return Path(__file__).parent / "data"

@pytest.fixture
def isolated_env():
    """Fixture providing isolated environment for testing"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Save original environment
        original_env = dict(os.environ)
        original_cwd = os.getcwd()
        
        # Set up isolated environment
        temp_path = Path(temp_dir)
        os.environ['HOME'] = str(temp_path)
        os.environ['MCP_SYSTEM_PATH'] = str(temp_path / '.mcp-system')
        os.chdir(temp_path)
        
        yield temp_path
        
        # Restore original environment
        os.environ.clear()
        os.environ.update(original_env)
        os.chdir(original_cwd)

@pytest.fixture
def mock_project_dir():
    """Fixture providing a mock project directory"""
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir)
        
        # Create common project files
        (project_path / "README.md").write_text("# Test Project")
        (project_path / ".gitignore").write_text("*.pyc\n__pycache__/")
        
        yield project_path

@pytest.fixture
def python_project_dir():
    """Fixture providing a Python project directory"""
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir)
        
        # Create Python project structure
        (project_path / "pyproject.toml").write_text("""
[project]
name = "test-project"
version = "0.1.0"
""")
        (project_path / "requirements.txt").write_text("fastapi>=0.100.0")
        (project_path / "src").mkdir()
        (project_path / "src" / "__init__.py").write_text("")
        (project_path / "src" / "main.py").write_text("print('Hello, World!')")
        
        yield project_path

@pytest.fixture
def nodejs_project_dir():
    """Fixture providing a Node.js project directory"""
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir)
        
        # Create Node.js project structure
        package_json = {
            "name": "test-project",
            "version": "1.0.0",
            "main": "index.js",
            "dependencies": {
                "@modelcontextprotocol/sdk": "^1.0.0"
            }
        }
        
        import json
        (project_path / "package.json").write_text(json.dumps(package_json, indent=2))
        (project_path / "index.js").write_text("console.log('Hello, World!');")
        
        yield project_path

@pytest.fixture
def claude_project_dir():
    """Fixture providing a Claude project directory"""
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir)
        
        # Create Claude project structure
        claude_dir = project_path / ".claude"
        claude_dir.mkdir()
        
        claude_config = {
            "mcpServers": {}
        }
        
        import json
        (claude_dir / "claude_desktop_config.json").write_text(
            json.dumps(claude_config, indent=2)
        )
        (project_path / "CLAUDE.md").write_text("# Claude Project Instructions")
        
        yield project_path