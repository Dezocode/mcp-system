"""
Tests for Environment Detection System
Comprehensive tests for environment detection, configuration management, and platform adaptation.
"""

import unittest
import tempfile
import os
import sys
import time
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch
import json

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config.environment_detector import EnvironmentDetector, EnvironmentInfo
from config.config_manager import ConfigManager, ConfigProfile, AdaptiveConfig
from config.platform_adapter import PlatformAdapter
from config.runtime_profiler import RuntimeProfiler, PerformanceSnapshot

class TestEnvironmentDetection(unittest.TestCase):
    """Test cases for Environment Detection System"""
    
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
        
    def test_environment_detection(self):
        """Test basic environment detection"""
        env_info = self.environment_detector.detect_environment()
        self.assertIsInstance(env_info, EnvironmentInfo)
        
        # Check required fields
        self.assertIsNotNone(env_info.platform)
        self.assertIsNotNone(env_info.architecture)
        self.assertIsInstance(env_info.is_docker, bool)
        self.assertIsInstance(env_info.is_containerized, bool)
        self.assertIsNotNone(env_info.python_version)
        self.assertIsNotNone(env_info.working_directory)
        self.assertIsNotNone(env_info.user)
        self.assertIsNotNone(env_info.hostname)
        
    def test_environment_summary(self):
        """Test environment summary"""
        summary = self.environment_detector.get_environment_summary()
        self.assertIsInstance(summary, dict)
        self.assertIn("platform", summary)
        self.assertIn("is_docker", summary)
        self.assertIn("python_version", summary)
        
    def test_docker_detection_methods(self):
        """Test Docker detection methods"""
        is_docker = self.environment_detector.is_running_in_docker()
        self.assertIsInstance(is_docker, bool)
        
        container_type = self.environment_detector.get_container_type()
        if container_type is not None:
            self.assertIsInstance(container_type, str)
            
    def test_kubernetes_detection(self):
        """Test Kubernetes detection"""
        is_k8s = self.environment_detector.is_running_in_kubernetes()
        self.assertIsInstance(is_k8s, bool)
        
    def test_configuration_management(self):
        """Test configuration management"""
        # List available profiles
        profiles = self.config_manager.list_config_profiles()
        self.assertIsInstance(profiles, list)
        self.assertGreater(len(profiles), 0)
        
        # Check that builtin profiles are loaded
        self.assertIn("docker-default", profiles)
        self.assertIn("local-development", profiles)
        self.assertIn("kubernetes-production", profiles)
        
        # Get current configuration
        config = self.config_manager.get_config()
        self.assertIsInstance(config, AdaptiveConfig)
        
    def test_platform_adaptation(self):
        """Test platform-specific adaptations"""
        worker_count = self.platform_adapter.get_optimal_worker_count()
        self.assertIsInstance(worker_count, int)
        self.assertGreater(worker_count, 0)
        self.assertLessEqual(worker_count, 8)
        
        temp_dir = self.platform_adapter.get_temp_directory()
        self.assertIsInstance(temp_dir, str)
        self.assertTrue(os.path.exists(temp_dir))
        
        buffer_sizes = self.platform_adapter.get_optimal_buffer_sizes()
        self.assertIsInstance(buffer_sizes, dict)
        self.assertIn("file_read_buffer", buffer_sizes)
        
        system_info = self.platform_adapter.get_system_info()
        self.assertIsInstance(system_info, dict)
        self.assertIn("platform", system_info)
        self.assertIn("cpu_count", system_info)
        
    def test_runtime_profiling(self):
        """Test runtime profiling"""
        # Start profiling
        self.runtime_profiler.start_profiling()
        self.assertTrue(self.runtime_profiler.is_profiling)
        
        # Let it run briefly
        time.sleep(0.2)
        
        # Get real-time metrics
        metrics = self.runtime_profiler.get_real_time_metrics()
        self.assertIsInstance(metrics, dict)
        self.assertIn("cpu_percent", metrics)
        self.assertIn("memory_mb", metrics)
        self.assertIn("thread_count", metrics)
        
        # Get resource usage summary
        summary = self.runtime_profiler.get_resource_usage_summary()
        self.assertIsInstance(summary, dict)
        self.assertIn("duration_seconds", summary)
        self.assertIn("average_cpu_percent", summary)
        
        # Stop profiling
        profile = self.runtime_profiler.stop_profiling()
        self.assertFalse(self.runtime_profiler.is_profiling)
        
    def test_config_validation(self):
        """Test configuration validation"""
        validation = self.config_manager.validate_configuration()
        self.assertIsInstance(validation, dict)
        self.assertIn("valid", validation)
        self.assertIn("issues", validation)
        self.assertIn("warnings", validation)
        
    def test_environment_export(self):
        """Test environment information export"""
        export_path = os.path.join(self.temp_dir, "env_info.json")
        self.environment_detector.export_environment_info(export_path, "json")
        
        # Check that file was created
        self.assertTrue(os.path.exists(export_path))
        
        # Check that file contains valid JSON
        with open(export_path, 'r') as f:
            data = json.load(f)
        self.assertIsInstance(data, dict)
        
    def test_profile_export(self):
        """Test performance profile export"""
        export_path = os.path.join(self.temp_dir, "profile.json")
        self.runtime_profiler.export_profile(export_path, "json")
        
        # Check that file was created
        self.assertTrue(os.path.exists(export_path))
        
        # Check that file contains valid JSON
        with open(export_path, 'r') as f:
            data = json.load(f)
        self.assertIsInstance(data, dict)
        
    def test_complete_integration(self):
        """Test complete environment detection integration"""
        # 1. Environment detection
        env_info = self.environment_detector.detect_environment()
        self.assertIsInstance(env_info, EnvironmentInfo)
        
        # 2. Configuration adaptation
        config = self.config_manager.get_config()
        self.assertIsInstance(config, AdaptiveConfig)
        
        # 3. Platform optimization
        optimizations = self.platform_adapter.optimize_for_current_platform()
        self.assertIsInstance(optimizations, dict)
        
        # 4. Runtime profiling
        self.runtime_profiler.start_profiling()
        time.sleep(0.1)
        metrics = self.runtime_profiler.get_real_time_metrics()
        profile = self.runtime_profiler.stop_profiling()
        
        # 5. Verify consistency
        env_summary = self.environment_detector.get_environment_summary()
        config_summary = self.config_manager.get_config_summary()
        
        self.assertEqual(env_summary["platform"], config_summary["environment"]["platform"])
        self.assertEqual(env_summary["is_docker"], config_summary["environment"]["is_docker"])
        
        # 6. Verify platform optimizations are reasonable
        self.assertIsInstance(optimizations["worker_count"], int)
        self.assertGreater(optimizations["worker_count"], 0)
        self.assertIsInstance(config.max_workers, int)
        self.assertGreater(config.max_workers, 0)

class TestMCPServerIntegration(unittest.TestCase):
    """Test MCP Server integration with environment detection"""
    
    def test_mcp_server_environment_integration(self):
        """Test that MCP server properly integrates environment detection"""
        from pipeline_mcp_server import pipeline_server
        
        # Test that environment detection is initialized
        self.assertIsNotNone(pipeline_server.environment_detector)
        self.assertIsNotNone(pipeline_server.config_manager)
        self.assertIsNotNone(pipeline_server.platform_adapter)
        self.assertIsNotNone(pipeline_server.runtime_profiler)
        
        # Test that environment info is available
        env_info = pipeline_server.environment_info
        self.assertIsNotNone(env_info)
        self.assertIsNotNone(env_info.platform)
        
        # Test that adaptive config is applied
        config = pipeline_server.adaptive_config
        self.assertIsNotNone(config)
        self.assertIsInstance(config.max_workers, int)
        self.assertGreater(config.max_workers, 0)
        
        # Test that profiling is started
        self.assertTrue(pipeline_server.runtime_profiler.is_profiling)
        
    def test_environment_detection_tool_functionality(self):
        """Test the environment detection tool functionality"""
        # Import the handler
        from pipeline_mcp_server import handle_environment_detection
        
        # Test different actions
        actions_to_test = ["detect", "summary", "config", "validate", "optimize"]
        
        for action in actions_to_test:
            result = asyncio.run(handle_environment_detection({"action": action}))
            self.assertIsInstance(result, list)
            self.assertEqual(len(result), 1)
            
            # Parse JSON response
            content = json.loads(result[0].text)
            self.assertEqual(content["tool"], "environment_detection")
            self.assertEqual(content["action"], action)
            self.assertIn("timestamp", content)

if __name__ == '__main__':
    import asyncio
    unittest.main()