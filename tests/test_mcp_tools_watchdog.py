#!/usr/bin/env python3
"""
Test MCP Tools Watchdog Functionality
"""

import shutil
import sys
import tempfile
import time
from pathlib import Path

import pytest

# Add the scripts directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from mcp_tools_monitor import MCPToolsStandardizer
from migrate_to_mcp_tools import MCPPathMigrator
from validate_mcp_tools import MCPToolsValidator


class TestMCPToolsWatchdog:
    """Test suite for MCP Tools watchdog functionality"""

    @pytest.fixture
    def temp_mcp_tools(self):
        """Create temporary mcp-tools directory for testing"""
        temp_dir = Path(tempfile.mkdtemp())
        mcp_tools_dir = temp_dir / "mcp-tools"
        mcp_tools_dir.mkdir()

        yield mcp_tools_dir

        # Cleanup
        shutil.rmtree(temp_dir)

    def test_standardizer_initialization(self, temp_mcp_tools):
        """Test MCPToolsStandardizer initialization"""
        standardizer = MCPToolsStandardizer(temp_mcp_tools)

        # Check that system directories are created
        assert (temp_mcp_tools / "_monitoring").exists()
        assert (temp_mcp_tools / "_standards").exists()
        assert (temp_mcp_tools / "_templates").exists()

    def test_server_validation(self, temp_mcp_tools):
        """Test server structure validation"""
        standardizer = MCPToolsStandardizer(temp_mcp_tools)

        # Create a test server with minimal structure
        test_server = temp_mcp_tools / "test-server"
        test_server.mkdir()
        (test_server / "src").mkdir()
        (test_server / "src" / "main.py").write_text("# Test server")
        (test_server / "README.md").write_text("# Test Server")
        (test_server / "pyproject.toml").write_text("[project]\nname = 'test-server'")
        (test_server / ".env.example").write_text("# Example env")

        # Validate structure
        validation = standardizer.validate_server_structure(test_server)
        assert validation["valid"] is True
        assert len(validation["missing_required"]) == 0

    def test_incomplete_server_validation(self, temp_mcp_tools):
        """Test validation of incomplete server structure"""
        standardizer = MCPToolsStandardizer(temp_mcp_tools)

        # Create incomplete server (missing required files)
        test_server = temp_mcp_tools / "incomplete-server"
        test_server.mkdir()
        (test_server / "src").mkdir()
        (test_server / "src" / "main.py").write_text("# Test server")
        # Missing README.md, pyproject.toml, .env.example

        validation = standardizer.validate_server_structure(test_server)
        assert validation["valid"] is False
        assert "README.md" in validation["missing_required"]
        assert "pyproject.toml" in validation["missing_required"]
        assert ".env.example" in validation["missing_required"]

    def test_server_template_creation(self, temp_mcp_tools):
        """Test creating server from template"""
        standardizer = MCPToolsStandardizer(temp_mcp_tools)

        # Create server from template
        success = standardizer.create_server_template("new-test-server")
        assert success is True

        # Verify structure was created
        server_path = temp_mcp_tools / "new-test-server"
        assert server_path.exists()
        assert (server_path / "src" / "main.py").exists()
        assert (server_path / "README.md").exists()
        assert (server_path / "pyproject.toml").exists()
        assert (server_path / ".env.example").exists()
        assert (server_path / "tests" / "test_server.py").exists()

        # Validate the created structure
        validation = standardizer.validate_server_structure(server_path)
        assert validation["valid"] is True

    def test_validator_initialization(self, temp_mcp_tools):
        """Test MCPToolsValidator initialization"""
        validator = MCPToolsValidator(temp_mcp_tools)
        assert validator.mcp_tools_path == temp_mcp_tools

    def test_validator_with_servers(self, temp_mcp_tools):
        """Test validator with multiple servers"""
        # Create standardizer and add a server
        standardizer = MCPToolsStandardizer(temp_mcp_tools)
        standardizer.create_server_template("test-server")

        # Validate using validator
        validator = MCPToolsValidator(temp_mcp_tools)
        servers = validator.get_servers()
        assert len(servers) == 1
        assert servers[0].name == "test-server"

        # Generate report
        is_valid, report = validator.generate_report()
        assert "test-server" in report
        assert "✅" in report  # Should be valid

    def test_path_migrator_legacy_detection(self):
        """Test legacy path detection"""
        migrator = MCPPathMigrator(Path.cwd())

        # Test various path formats
        assert migrator._needs_migration("~/mcp-test-server") is True
        assert migrator._needs_migration("mcp-tools/test-server") is False
        assert migrator._needs_migration("/absolute/path") is False

    def test_get_server_directories(self, temp_mcp_tools):
        """Test getting server directories"""
        standardizer = MCPToolsStandardizer(temp_mcp_tools)

        # Initially no servers
        servers = standardizer.get_server_directories()
        assert len(servers) == 0

        # Create some servers
        (temp_mcp_tools / "server1").mkdir()
        (temp_mcp_tools / "server2").mkdir()
        (temp_mcp_tools / "_system").mkdir()  # Should be ignored

        servers = standardizer.get_server_directories()
        assert len(servers) == 2
        server_names = {s.name for s in servers}
        assert server_names == {"server1", "server2"}


def test_integration_example():
    """Integration test showing typical usage"""
    # This test uses the actual mcp-tools directory
    mcp_tools_path = Path.cwd() / "mcp-tools"

    if not mcp_tools_path.exists():
        pytest.skip("mcp-tools directory not found")

    # Test validator
    validator = MCPToolsValidator(mcp_tools_path)
    servers = validator.get_servers()
    assert len(servers) > 0  # Should have existing servers

    # Test standardizer
    standardizer = MCPToolsStandardizer(mcp_tools_path)

    # Validate existing servers
    for server in servers:
        validation = standardizer.validate_server_structure(server)
        # All existing servers should have the basic structure
        assert isinstance(validation, dict)
        assert "valid" in validation


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])
