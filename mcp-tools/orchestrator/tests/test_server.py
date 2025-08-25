#!/usr/bin/env python3
"""
Test suite for MCP Orchestrator Server
Tests Windows Docker integration, CLI resolution, and watchdog monitoring.
"""

import asyncio
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

import pytest

# Add the src directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from main import (
    WindowsDockerIntegration,
    WatchdogMonitor,
    CLIResolver,
    OrchestratorServer,
    handle_docker_operation,
    handle_environment_setup,
    handle_container_management,
    handle_watchdog_monitoring,
    handle_cli_resolution,
    handle_windows_integration,
    handle_health_monitoring,
    handle_deployment_orchestration
)


class TestWindowsDockerIntegration:
    """Test Windows Docker Desktop and WSL integration."""
    
    def test_initialization(self):
        """Test WindowsDockerIntegration initialization."""
        integration = WindowsDockerIntegration()
        
        assert hasattr(integration, "is_windows")
        assert hasattr(integration, "wsl_distro")
        assert hasattr(integration, "wsl_user")
        assert hasattr(integration, "docker_desktop_enabled")
    
    def test_wsl_distro_parsing(self):
        """Test WSL distro output parsing."""
        integration = WindowsDockerIntegration()
        
        # Mock WSL output
        wsl_output = """  NAME                   STATE           VERSION
* Ubuntu                 Running         2
  docker-desktop         Running         2
  docker-desktop-data    Running         2"""
        
        distros = integration._parse_wsl_distros(wsl_output)
        
        assert len(distros) == 3
        assert distros[0]["name"] == "Ubuntu"
        assert distros[0]["state"] == "Running"
        assert distros[0]["version"] == "2"
        assert distros[0]["default"] is True
    
    @patch('subprocess.run')
    def test_detect_wsl_environment_windows(self, mock_run):
        """Test WSL environment detection on Windows."""
        integration = WindowsDockerIntegration()
        integration.is_windows = True
        
        # Mock successful WSL command
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = """  NAME                   STATE           VERSION
* Ubuntu                 Running         2"""
        
        wsl_info = integration.detect_wsl_environment()
        
        assert wsl_info["is_wsl"] is True
        assert len(wsl_info["available_distros"]) > 0
    
    @pytest.mark.asyncio
    async def test_execute_docker_command(self):
        """Test Docker command execution."""
        integration = WindowsDockerIntegration()
        
        with patch('asyncio.create_subprocess_exec') as mock_subprocess:
            # Mock process
            mock_process = Mock()
            mock_process.communicate = AsyncMock(return_value=(b"test output", b""))
            mock_process.returncode = 0
            mock_subprocess.return_value = mock_process
            
            returncode, stdout, stderr = await integration.execute_docker_command(
                ["docker", "version"]
            )
            
            assert returncode == 0
            assert stdout == "test output"
            assert stderr == ""
    
    @patch('docker.from_env')
    def test_get_docker_desktop_status(self, mock_docker):
        """Test Docker Desktop status retrieval."""
        # Mock Docker client
        mock_client = Mock()
        mock_client.ping.return_value = True
        mock_client.version.return_value = {"Version": "20.10.0"}
        mock_client.containers.list.return_value = []
        mock_client.images.list.return_value = []
        mock_docker.return_value = mock_client
        
        integration = WindowsDockerIntegration()
        integration.docker_client = mock_client
        
        status = integration.get_docker_desktop_status()
        
        assert status["available"] is True
        assert status["running"] is True
        assert status["version"] == "20.10.0"
        assert status["containers"] == 0
        assert status["images"] == 0


class TestWatchdogMonitor:
    """Test watchdog file system monitoring."""
    
    def test_initialization(self):
        """Test WatchdogMonitor initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            monitor = WatchdogMonitor(Path(temp_dir))
            
            assert monitor.workspace_root == Path(temp_dir)
            assert isinstance(monitor.observers, dict)
            assert isinstance(monitor.monitored_paths, list)
    
    @patch.dict(os.environ, {"WATCHDOG_ENABLED": "true"})
    def test_start_monitoring_enabled(self):
        """Test starting file monitoring when enabled."""
        with tempfile.TemporaryDirectory() as temp_dir:
            monitor = WatchdogMonitor(Path(temp_dir))
            monitor.enabled = True
            
            with patch('main.WATCHDOG_AVAILABLE', True), \
                 patch('main.Observer') as mock_observer_class:
                
                mock_observer = Mock()
                mock_observer_class.return_value = mock_observer
                
                monitor_id = monitor.start_monitoring(temp_dir)
                
                assert "Error:" not in monitor_id
                assert monitor_id in monitor.observers
                mock_observer.start.assert_called_once()
    
    def test_stop_monitoring(self):
        """Test stopping file monitoring."""
        with tempfile.TemporaryDirectory() as temp_dir:
            monitor = WatchdogMonitor(Path(temp_dir))
            
            # Add a mock observer
            mock_observer = Mock()
            test_id = "test_monitor_123"
            monitor.observers[test_id] = {
                "observer": mock_observer,
                "handler": Mock(),
                "path": temp_dir,
                "started": 1234567890
            }
            
            success = monitor.stop_monitoring(test_id)
            
            assert success is True
            assert test_id not in monitor.observers
            mock_observer.stop.assert_called_once()
            mock_observer.join.assert_called_once()
    
    def test_get_monitoring_status(self):
        """Test monitoring status retrieval."""
        with tempfile.TemporaryDirectory() as temp_dir:
            monitor = WatchdogMonitor(Path(temp_dir))
            
            status = monitor.get_monitoring_status()
            
            assert "enabled" in status
            assert "available" in status
            assert "active_monitors" in status
            assert "monitored_paths" in status
            assert "monitors" in status


class TestCLIResolver:
    """Test CLI command resolution and execution."""
    
    def test_initialization(self):
        """Test CLIResolver initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            resolver = CLIResolver(Path(temp_dir))
            
            assert resolver.workspace_root == Path(temp_dir)
            assert resolver.timeout > 0
            assert hasattr(resolver, "safe_mode")
            assert hasattr(resolver, "allowed_operations")
    
    def test_validate_command_safe(self):
        """Test command validation in safe mode."""
        with tempfile.TemporaryDirectory() as temp_dir:
            resolver = CLIResolver(Path(temp_dir))
            resolver.safe_mode = True
            
            # Test safe command
            is_valid, msg = resolver.validate_command(["echo", "hello"])
            assert is_valid is True
            
            # Test dangerous command
            is_valid, msg = resolver.validate_command(["rm", "-rf", "/"])
            assert is_valid is False
            assert "dangerous" in msg.lower()
    
    def test_validate_docker_operations(self):
        """Test Docker operation validation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            resolver = CLIResolver(Path(temp_dir))
            resolver.allowed_operations = ["start", "stop", "status"]
            
            # Test allowed operation
            is_valid, msg = resolver.validate_command(["docker", "start", "container"])
            assert is_valid is True
            
            # Test disallowed operation
            is_valid, msg = resolver.validate_command(["docker", "rm", "container"])
            assert is_valid is False
            assert "not allowed" in msg
    
    @pytest.mark.asyncio
    async def test_execute_command_success(self):
        """Test successful command execution."""
        with tempfile.TemporaryDirectory() as temp_dir:
            resolver = CLIResolver(Path(temp_dir))
            
            with patch('asyncio.create_subprocess_exec') as mock_subprocess:
                # Mock successful process
                mock_process = Mock()
                mock_process.communicate = AsyncMock(return_value=(b"success", b""))
                mock_process.returncode = 0
                mock_subprocess.return_value = mock_process
                
                result = await resolver.execute_command(["echo", "test"])
                
                assert result["success"] is True
                assert result["returncode"] == 0
                assert result["stdout"] == "success"
    
    @pytest.mark.asyncio
    async def test_execute_command_timeout(self):
        """Test command timeout handling."""
        with tempfile.TemporaryDirectory() as temp_dir:
            resolver = CLIResolver(Path(temp_dir))
            resolver.timeout = 1  # 1 second timeout
            
            with patch('asyncio.create_subprocess_exec') as mock_subprocess:
                # Mock process that times out
                mock_process = Mock()
                mock_process.communicate = AsyncMock(side_effect=asyncio.TimeoutError())
                mock_process.kill = AsyncMock()
                mock_process.wait = AsyncMock()
                mock_subprocess.return_value = mock_process
                
                result = await resolver.execute_command(["sleep", "10"])
                
                assert result["success"] is False
                assert "timeout" in result["error"].lower()


class TestOrchestratorServer:
    """Test main orchestrator server functionality."""
    
    def test_initialization(self):
        """Test OrchestratorServer initialization."""
        server = OrchestratorServer()
        
        assert hasattr(server, "server")
        assert hasattr(server, "workspace_root")
        assert hasattr(server, "session_dir")
        assert hasattr(server, "windows_docker")
        assert hasattr(server, "watchdog")
        assert hasattr(server, "cli_resolver")
    
    def test_session_directory_creation(self):
        """Test that session directory is created."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.dict(os.environ, {"MCP_SESSION_DIR": str(Path(temp_dir) / "sessions")}):
                server = OrchestratorServer()
                
                assert server.session_dir.exists()


class TestToolHandlers:
    """Test MCP tool handler functions."""
    
    @pytest.mark.asyncio
    async def test_handle_docker_operation(self):
        """Test Docker operation handler."""
        with patch('main.orchestrator_server') as mock_server:
            mock_windows_docker = Mock()
            mock_windows_docker.execute_docker_command = AsyncMock(
                return_value=(0, "Docker version 20.10.0", "")
            )
            mock_windows_docker.get_docker_desktop_status.return_value = {
                "available": True, "running": True
            }
            mock_server.windows_docker = mock_windows_docker
            
            result = await handle_docker_operation({
                "operation": "ps",
                "use_wsl": False,
                "options": {}
            })
            
            assert len(result) == 1
            response = json.loads(result[0].text)
            assert response["tool"] == "docker_operation"
            assert response["operation"] == "ps"
            assert response["success"] is True
    
    @pytest.mark.asyncio
    async def test_handle_environment_setup_detect(self):
        """Test environment setup detection."""
        with patch('main.orchestrator_server') as mock_server:
            mock_server.workspace_root = Path("/test")
            mock_server.windows_docker.is_windows = False
            mock_server.environment_detector = None
            
            result = await handle_environment_setup({
                "action": "detect",
                "components": [],
                "force": False
            })
            
            assert len(result) == 1
            response = json.loads(result[0].text)
            assert response["tool"] == "environment_setup"
            assert response["action"] == "detect"
            assert "results" in response
            assert "detection" in response["results"]
    
    @pytest.mark.asyncio
    async def test_handle_container_management_list(self):
        """Test container management list operation."""
        with patch('main.orchestrator_server') as mock_server:
            # Mock Docker client
            mock_container = Mock()
            mock_container.short_id = "abc123"
            mock_container.name = "test_container"
            mock_container.status = "running"
            mock_container.image.tags = ["test:latest"]
            
            mock_docker_client = Mock()
            mock_docker_client.containers.list.return_value = [mock_container]
            
            mock_windows_docker = Mock()
            mock_windows_docker.docker_client = mock_docker_client
            mock_server.windows_docker = mock_windows_docker
            
            result = await handle_container_management({
                "action": "list",
                "options": {"all": True}
            })
            
            assert len(result) == 1
            response = json.loads(result[0].text)
            assert response["tool"] == "container_management"
            assert response["action"] == "list"
            assert response["success"] is True
            assert len(response["containers"]) == 1
    
    @pytest.mark.asyncio
    async def test_handle_watchdog_monitoring_start(self):
        """Test watchdog monitoring start operation."""
        with patch('main.orchestrator_server') as mock_server:
            mock_watchdog = Mock()
            mock_watchdog.start_monitoring.return_value = "monitor_abc123"
            mock_server.watchdog = mock_watchdog
            
            result = await handle_watchdog_monitoring({
                "action": "start",
                "path": "/test/path",
                "recursive": True
            })
            
            assert len(result) == 1
            response = json.loads(result[0].text)
            assert response["tool"] == "watchdog_monitoring"
            assert response["action"] == "start"
            assert response["monitor_id"] == "monitor_abc123"
            assert response["success"] is True
    
    @pytest.mark.asyncio
    async def test_handle_cli_resolution_validate(self):
        """Test CLI resolution validation."""
        with patch('main.orchestrator_server') as mock_server:
            mock_cli_resolver = Mock()
            mock_cli_resolver.validate_command.return_value = (True, "Valid command")
            mock_server.cli_resolver = mock_cli_resolver
            
            result = await handle_cli_resolution({
                "command": ["echo", "test"],
                "validate_only": True
            })
            
            assert len(result) == 1
            response = json.loads(result[0].text)
            assert response["tool"] == "cli_resolution"
            assert response["validate_only"] is True
            assert response["valid"] is True
            assert response["success"] is True
    
    @pytest.mark.asyncio
    async def test_handle_windows_integration_wsl_status(self):
        """Test Windows integration WSL status."""
        with patch('main.orchestrator_server') as mock_server:
            mock_windows_docker = Mock()
            mock_windows_docker.detect_wsl_environment.return_value = {
                "is_wsl": True,
                "distro": "Ubuntu",
                "available_distros": [{"name": "Ubuntu", "state": "Running"}]
            }
            mock_server.windows_docker = mock_windows_docker
            
            result = await handle_windows_integration({
                "action": "wsl_status"
            })
            
            assert len(result) == 1
            response = json.loads(result[0].text)
            assert response["tool"] == "windows_integration"
            assert response["action"] == "wsl_status"
            assert response["success"] is True
            assert "wsl_environment" in response
    
    @pytest.mark.asyncio
    async def test_handle_health_monitoring_system(self):
        """Test health monitoring system scope."""
        with patch('main.orchestrator_server') as mock_server:
            mock_server.windows_docker.docker_client = None
            mock_server.docker_health_check = None
            
            with patch('psutil.cpu_percent', return_value=25.0), \
                 patch('psutil.virtual_memory') as mock_memory, \
                 patch('psutil.disk_usage') as mock_disk, \
                 patch('psutil.boot_time', return_value=1234567890), \
                 patch('psutil.pids', return_value=list(range(100))):
                
                mock_memory.return_value._asdict.return_value = {"total": 8000000000, "available": 4000000000}
                mock_disk.return_value._asdict.return_value = {"total": 100000000000, "free": 50000000000}
                
                result = await handle_health_monitoring({
                    "scope": "system",
                    "detailed": True
                })
                
                assert len(result) == 1
                response = json.loads(result[0].text)
                assert response["tool"] == "health_monitoring"
                assert response["scope"] == "system"
                assert response["success"] is True
                assert "health_data" in response
                assert "system" in response["health_data"]
    
    @pytest.mark.asyncio
    async def test_handle_deployment_orchestration_dry_run(self):
        """Test deployment orchestration dry run."""
        result = await handle_deployment_orchestration({
            "workflow": "development",
            "dry_run": True,
            "steps": []
        })
        
        assert len(result) == 1
        response = json.loads(result[0].text)
        assert response["tool"] == "deployment_orchestration"
        assert response["workflow"] == "development"
        assert response["dry_run"] is True
        assert response["success"] is True
        assert "execution_results" in response
        
        # Check that all steps were skipped in dry run
        for step_result in response["execution_results"]:
            assert "skipped (dry run)" in step_result["status"]


class TestIntegration:
    """Integration tests for the complete orchestrator."""
    
    @pytest.mark.asyncio
    async def test_docker_and_watchdog_integration(self):
        """Test integration between Docker operations and watchdog monitoring."""
        with patch('main.orchestrator_server') as mock_server:
            # Setup mocks
            mock_windows_docker = Mock()
            mock_watchdog = Mock()
            
            mock_windows_docker.execute_docker_command = AsyncMock(
                return_value=(0, "container started", "")
            )
            mock_windows_docker.get_docker_desktop_status.return_value = {"available": True}
            mock_watchdog.start_monitoring.return_value = "monitor_123"
            
            mock_server.windows_docker = mock_windows_docker
            mock_server.watchdog = mock_watchdog
            
            # Start monitoring
            monitor_result = await handle_watchdog_monitoring({
                "action": "start",
                "path": "/var/lib/docker",
                "recursive": True
            })
            
            # Perform Docker operation
            docker_result = await handle_docker_operation({
                "operation": "start",
                "target": "test_container"
            })
            
            # Verify both operations succeeded
            monitor_response = json.loads(monitor_result[0].text)
            docker_response = json.loads(docker_result[0].text)
            
            assert monitor_response["success"] is True
            assert docker_response["success"] is True
    
    def test_environment_variables_configuration(self):
        """Test that environment variables are properly loaded."""
        with tempfile.TemporaryDirectory() as temp_dir:
            env_file = Path(temp_dir) / ".env"
            env_file.write_text("""
DOCKER_TIMEOUT=60
WSL_DISTRO=TestDistro
WATCHDOG_ENABLED=false
MCP_LOG_LEVEL=DEBUG
""")
            
            with patch.dict(os.environ, {}):
                with patch('main.load_dotenv') as mock_load_dotenv:
                    mock_load_dotenv.return_value = True
                    
                    # Mock the environment variables
                    with patch.dict(os.environ, {
                        "DOCKER_TIMEOUT": "60",
                        "WSL_DISTRO": "TestDistro",
                        "WATCHDOG_ENABLED": "false",
                        "MCP_LOG_LEVEL": "DEBUG"
                    }):
                        integration = WindowsDockerIntegration()
                        monitor = WatchdogMonitor(Path(temp_dir))
                        
                        assert integration.wsl_distro == "TestDistro"
                        assert monitor.enabled is False


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])