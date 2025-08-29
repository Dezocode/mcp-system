#!/usr/bin/env python3
"""
Comprehensive test suite for massive pipeline MCP improvements
Tests all Phase 2.1 enhancements: monitoring, parallel processing, and Claude protocol integration
"""

import asyncio
import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "mcp-tools/pipeline-mcp/src"))


class TestMassivePipelineImprovements:
    """Test suite for massive pipeline MCP improvements"""

    @pytest.fixture
    def pipeline_server(self):
        """Fixture for pipeline server"""
        from main import pipeline_server

        return pipeline_server

    def test_real_time_monitoring_system(self, pipeline_server):
        """Test real-time monitoring system integration"""
        session_id = pipeline_server.create_session()
        session = pipeline_server.get_session(session_id)

        # Test monitoring initialization
        assert session.realtime_monitor is not None
        assert session.metrics_collector is not None

        # Test monitoring functionality
        session.update_status("testing", "monitoring_test")
        metrics = session.realtime_monitor.get_current_metrics()

        assert "uptime_seconds" in metrics
        assert "operation_counts" in metrics
        assert "session_id" in metrics
        assert metrics["session_id"] == session_id

    def test_parallel_processing_engine(self, pipeline_server):
        """Test parallel processing engine integration"""
        # Test parallel executor
        assert pipeline_server.parallel_executor is not None
        assert pipeline_server.parallel_executor.max_workers == 3

        # Test job queue
        assert pipeline_server.job_queue is not None
        queue_status = pipeline_server.job_queue.get_queue_status()
        assert queue_status["max_concurrent"] == 3
        assert queue_status["queue_size"] == 0

    def test_performance_summary(self, pipeline_server):
        """Test performance summary functionality"""
        parallel_summary = pipeline_server.parallel_executor.get_performance_summary()

        assert "resource_configuration" in parallel_summary
        assert "execution_statistics" in parallel_summary
        assert "performance_metrics" in parallel_summary
        assert parallel_summary["resource_configuration"]["max_thread_workers"] == 3

    def test_claude_agent_protocol_integration(self, pipeline_server):
        """Test Claude Agent Protocol integration"""
        session_id = pipeline_server.create_session()
        session = pipeline_server.get_session(session_id)

        # Claude protocol availability depends on environment
        # Test graceful handling when not available
        assert hasattr(session, "claude_protocol")

    @pytest.mark.asyncio
    async def test_enhanced_tool_list(self, pipeline_server):
        """Test enhanced tool list with all massive improvements"""
        from main import handle_list_tools

        tools = await handle_list_tools()

        # Should have at least 8 tools (or 9 with Claude protocol)
        assert len(tools) >= 8

        tool_names = [tool.name for tool in tools]

        # Verify all expected tools are present
        expected_tools = [
            "version_keeper_scan",
            "quality_patcher_fix",
            "pipeline_run_full",
            "github_workflow_trigger",
            "pipeline_status",
            "environment_detection",
            "health_monitoring",
            "mcp_compliance_check",
        ]

        for tool_name in expected_tools:
            assert tool_name in tool_names

    @pytest.mark.asyncio
    async def test_enhanced_session_management(self, pipeline_server):
        """Test enhanced session management with monitoring"""
        from main import handle_pipeline_status

        # Create session
        session_id = pipeline_server.create_session()
        session = pipeline_server.get_session(session_id)

        # Update session with monitoring data
        session.update_status("testing", "session_management_test")

        # Get enhanced status
        result = await handle_pipeline_status({"session_id": session_id})
        status_text = result[0].text
        import json

        status_data = json.loads(status_text)

        assert status_data["tool"] == "pipeline_status"
        assert status_data["status"] == "success"
        assert "monitoring" in status_data["results"]["session"]

    def test_metrics_collection_system(self, pipeline_server):
        """Test metrics collection system"""
        session_id = pipeline_server.create_session()
        session = pipeline_server.get_session(session_id)

        # Test metrics collector
        metrics_collector = session.metrics_collector
        system_summary = metrics_collector.get_current_system_summary()

        assert "status" in system_summary
        # Should be healthy or have some status

    def test_monitoring_alerts(self, pipeline_server):
        """Test monitoring alert system"""
        session_id = pipeline_server.create_session()
        session = pipeline_server.get_session(session_id)

        # Test alert generation
        monitor = session.realtime_monitor
        monitor.add_alert("test_alert", "Test alert message", "info")

        metrics = monitor.get_current_metrics()
        assert len(metrics["alerts"]) > 0
        assert metrics["alerts"][0]["alert_type"] == "test_alert"

    def test_performance_improvement_tracking(self, pipeline_server):
        """Test performance improvement tracking"""
        session_id = pipeline_server.create_session()
        session = pipeline_server.get_session(session_id)

        # Test performance tracking
        monitor = session.realtime_monitor

        # Start and stop a mock operation
        event_id = monitor.start_monitoring("test_op", "test_operation")
        monitor.stop_monitoring(event_id, {"status": "success"})

        metrics = monitor.get_current_metrics()
        assert metrics["operation_counts"]["test_operation"] == 1

    def test_session_persistence(self, pipeline_server):
        """Test session persistence functionality"""
        session_id = pipeline_server.create_session()
        session = pipeline_server.get_session(session_id)

        # Test session data structure
        status_dict = session.get_status_dict()

        assert "session_id" in status_dict
        assert "monitoring" in status_dict
        assert "execution_time" in status_dict
        assert status_dict["session_id"] == session_id

    @pytest.mark.asyncio
    async def test_environment_detection_tool(self, pipeline_server):
        """Test environment detection tool with enhancements"""
        from main import handle_environment_detection

        result = await handle_environment_detection({"action": "detect"})
        result_text = result[0].text
        import json

        result_data = json.loads(result_text)

        assert result_data["tool"] == "environment_detection"
        assert result_data["action"] == "detect"
        assert "environment_info" in result_data

    @pytest.mark.asyncio
    async def test_health_monitoring_tool(self, pipeline_server):
        """Test health monitoring tool"""
        from main import handle_health_monitoring

        result = await handle_health_monitoring({"action": "health_check"})
        result_text = result[0].text
        import json

        result_data = json.loads(result_text)

        assert result_data["tool"] == "health_monitoring"
        assert result_data["action"] == "health_check"

    def test_massive_improvements_integration(self, pipeline_server):
        """Test that all massive improvements work together"""
        session_id = pipeline_server.create_session()
        session = pipeline_server.get_session(session_id)

        # Test all major components are present and initialized
        assert session.realtime_monitor is not None
        assert session.metrics_collector is not None
        assert pipeline_server.parallel_executor is not None
        assert pipeline_server.job_queue is not None

        # Test they're properly configured for 3x speedup
        assert pipeline_server.parallel_executor.max_workers == 3
        assert pipeline_server.job_queue.max_concurrent_jobs == 3

        # Test monitoring is active
        metrics = session.realtime_monitor.get_current_metrics()
        assert "uptime_seconds" in metrics

        print("✅ All massive improvements successfully integrated and functional!")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
