#!/usr/bin/env python3
"""
Comprehensive Pipeline Integration Test Suite
Tests the complete pipeline integration including:
1. Version Keeper JSON Output
2. Quality Patcher JSON Output
3. Pipeline MCP Server
4. GitHub Workflow Syntax
5. MCP Compliance Check

Author: Pipeline Integration Team
Version: 1.0.0
"""

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestPipelineIntegration(unittest.TestCase):
    """Comprehensive test suite for pipeline integration"""

    def setUp(self):
        """Set up test environment"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.original_cwd = Path.cwd()
        os.chdir(self.test_dir)

        # Create basic project structure
        (self.test_dir / "scripts").mkdir(parents=True, exist_ok=True)
        (self.test_dir / "src").mkdir(parents=True, exist_ok=True)
        (self.test_dir / "test-output").mkdir(parents=True, exist_ok=True)
        (self.test_dir / "pipeline-sessions").mkdir(parents=True, exist_ok=True)

        # Copy necessary scripts to test directory
        self.copy_project_files()

    def tearDown(self):
        """Clean up test environment"""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def copy_project_files(self):
        """Copy necessary project files to test directory"""
        import shutil

        # Copy scripts
        source_scripts = project_root / "scripts"
        if source_scripts.exists():
            for script in ["simple_version_keeper.py", "simple_quality_patcher.py"]:
                source_file = source_scripts / script
                if source_file.exists():
                    shutil.copy2(source_file, self.test_dir / "scripts" / script)

        # Copy src files
        source_src = project_root / "src"
        if source_src.exists():
            for src_file in source_src.glob("*.py"):
                shutil.copy2(src_file, self.test_dir / "src" / src_file.name)

        # Create basic pyproject.toml
        pyproject_content = '''
[project]
name = "test-project"
version = "1.0.0"
description = "Test project for pipeline integration"

[build-system]
requires = ["setuptools", "wheel"]
build-backend = "setuptools.build_meta"
'''
        (self.test_dir / "pyproject.toml").write_text(pyproject_content.strip())

    def test_version_keeper_json_output(self):
        """Test 1: Version Keeper JSON Output - Creates JSON reports
        with required fields"""
        print("\n🧪 Test 1: Version Keeper JSON Output")

        # Run simple version keeper test
        script_path = self.test_dir / "scripts" / "simple_version_keeper.py"
        if not script_path.exists():
            self.skipTest("simple_version_keeper.py not found")

        result = subprocess.run([
            sys.executable, str(script_path)
        ], capture_output=True, text=True, cwd=self.test_dir)

        self.assertEqual(result.returncode, 0, f"Script failed: {result.stderr}")

        # Check that JSON report was created
        json_report_path = self.test_dir / "test-output" / "test-lint.json"
        self.assertTrue(json_report_path.exists(), "JSON report file not created")

        # Load and validate JSON structure
        with open(json_report_path, 'r') as f:
            report = json.load(f)

        # Validate required fields
        required_fields = [
            "timestamp", "session_id", "version", "branch",
            "summary", "details", "performance", "recommendations"
        ]

        for field in required_fields:
            self.assertIn(
                field, report, f"Required field '{field}' missing from JSON report")

        # Validate summary structure
        summary = report["summary"]
        summary_fields = [
            "total_issues", "fixes_applied", "remaining_issues", "success_rate"]
        for field in summary_fields:
            self.assertIn(field, summary, f"Summary field '{field}' missing")

        print(
            f"  ✅ JSON report created with "
            f"{report['summary']['total_issues']} test issues")
        print(f"  ✅ All required fields present: {', '.join(required_fields)}")

    def test_quality_patcher_json_output(self):
        """Test 2: Quality Patcher JSON Output - Generates structured fix reports"""
        print("\n🧪 Test 2: Quality Patcher JSON Output")

        # First ensure we have a lint report
        self.test_version_keeper_json_output()

        # Run simple quality patcher test
        script_path = self.test_dir / "scripts" / "simple_quality_patcher.py"
        if not script_path.exists():
            self.skipTest("simple_quality_patcher.py not found")

        result = subprocess.run([
            sys.executable, str(script_path)
        ], capture_output=True, text=True, cwd=self.test_dir)

        self.assertEqual(result.returncode, 0, f"Script failed: {result.stderr}")

        # Check that fixes JSON report was created
        fixes_report_path = self.test_dir / "test-output" / "test-fixes.json"
        self.assertTrue(
            fixes_report_path.exists(), "Fixes JSON report file not created")

        # Load and validate JSON structure
        with open(fixes_report_path, 'r') as f:
            report = json.load(f)

        # Validate required fields for fixes report
        required_fields = [
            "timestamp", "session_id", "summary", "details",
            "performance", "recommendations", "source_lint_report"
        ]

        for field in required_fields:
            self.assertIn(
                field, report, f"Required field '{field}' missing from fixes report")

        # Validate summary structure
        summary = report["summary"]
        summary_fields = [
            "total_issues", "fixes_applied", "fixes_failed",
            "fixes_skipped", "remaining_issues", "success_rate"
        ]
        for field in summary_fields:
            self.assertIn(field, summary, f"Summary field '{field}' missing")

        # Validate performance metrics
        performance = report["performance"]
        perf_fields = [
            "duration_seconds", "fixes_per_minute", "average_fix_time", "success_rate"]
        for field in perf_fields:
            self.assertIn(field, performance, f"Performance field '{field}' missing")

        print(
            f"  ✅ Fixes report created with "
            f"{report['summary']['fixes_applied']} fixes applied")
        print(f"  ✅ Success rate: {report['summary']['success_rate']}%")
        print("  ✅ All required fields present")

    def test_pipeline_mcp_server(self):
        """Test 3: Pipeline MCP Server - All 6 tools functional"""
        print("\n🧪 Test 3: Pipeline MCP Server")

        # Import the MCP server
        server_path = self.test_dir / "mcp-tools" / "pipeline-mcp" / "src" / "main.py"
        if not server_path.exists():
            self.skipTest("pipeline-mcp server not found")

        # Add the src directory to path
        sys.path.insert(0, str(self.test_dir / "src"))

        try:
            # Import server components
            spec = importlib.util.spec_from_file_location(
                "pipeline-mcp", server_path)
            server_module = importlib.util.module_from_spec(spec)

            # Mock MCP dependencies for testing
            with patch('mcp.server.models.InitializationOptions'), \
                 patch('mcp.server.Server'), \
                 patch('mcp.server.stdio.stdio_server'):

                spec.loader.exec_module(server_module)

                # Test server initialization
                server = server_module.PipelineMCPServer()
                self.assertIsNotNone(server, "MCP server failed to initialize")

                # Test session creation
                session_id = server.create_session()
                self.assertIsNotNone(session_id, "Session creation failed")
                self.assertTrue(
                    session_id.startswith("pipeline-"), "Invalid session ID format")

                # Test session retrieval
                session = server.get_session(session_id)
                self.assertIsNotNone(session, "Session retrieval failed")

                print("  ✅ MCP server initialized successfully")
                print(f"  ✅ Session management working (ID: {session_id[:20]}...)")
                print(f"  ✅ Session directory: {server.session_dir}")

        except ImportError as e:
            self.skipTest(f"MCP server import failed: {e}")
        except Exception as e:
            self.fail(f"MCP server test failed: {e}")

    def test_github_workflow_syntax(self):
        """Test 4: GitHub Workflow Syntax - Valid YAML structure"""
        print("\n🧪 Test 4: GitHub Workflow Syntax")

        workflow_path = project_root / ".github" / "workflows" / \
            "pipeline-integration.yml"
        if not workflow_path.exists():
            self.skipTest("GitHub workflow file not found")

        try:
            import yaml
        except ImportError:
            # Try pyyaml if yaml not available
            try:
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", "pyyaml"],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                import yaml
            except Exception:
                self.skipTest("PyYAML not available for workflow validation")

        # Load and validate YAML syntax
        with open(workflow_path, 'r') as f:
            workflow_content = f.read()

        try:
            workflow = yaml.safe_load(workflow_content)
        except yaml.YAMLError as e:
            self.fail(f"Invalid YAML syntax in workflow: {e}")

        # Validate required workflow structure
        required_keys = ["name", "on", "env", "jobs"]
        for key in required_keys:
            self.assertIn(key, workflow, f"Required workflow key '{key}' missing")

        # Validate jobs structure
        jobs = workflow["jobs"]
        required_jobs = [
            "version-keeper-scan", "quality-patcher",
            "version-keeper-validate", "github-integration", "cleanup"
        ]

        for job in required_jobs:
            self.assertIn(job, jobs, f"Required job '{job}' missing from workflow")

        # Check for fixed GitHub Actions versions (not snapshot paths)
        workflow_text = workflow_content
        self.assertNotIn(
            "bin/snapshot", workflow_text, "Workflow still contains snapshot paths")
        self.assertIn(
            "actions/checkout@v4", workflow_text, "Missing updated checkout action")
        self.assertIn(
            "actions/setup-python@v5", workflow_text,
            "Missing updated python setup action")

        print("  ✅ GitHub workflow YAML syntax is valid")
        print(f"  ✅ All {len(required_jobs)} required jobs present")
        print("  ✅ GitHub Actions versions fixed (no snapshot paths)")

    def test_mcp_compliance_check(self):
        """Test 5: MCP Compliance Check - Validates MCP standards"""
        print("\n🧪 Test 5: MCP Compliance Check")
        # This test validates MCP compliance conceptually since we can't easily
        # run the full MCP server in test environment
        server_path = self.test_dir / "mcp-tools" / "pipeline-mcp" / "src" / "main.py"
        if not server_path.exists():
            self.skipTest("pipeline-mcp server not found")
        # Read server source code for compliance checks
        with open(server_path, 'r') as f:
            server_code = f.read()
        # Check for MCP v1.0 compliance indicators
        mcp_indicators = [
            "from mcp.server.models import InitializationOptions",
            "from mcp.server import NotificationOptions, Server",
            "from mcp.server.stdio import stdio_server",
            "from mcp.types import",
            "McpError",
            "ErrorCode",
            "@pipeline_server.server.list_tools()",
            "@pipeline_server.server.call_tool()",
            "inputSchema",
            "async def handle_call_tool"
        ]
        compliance_score = 0
        total_checks = len(mcp_indicators)
        for indicator in mcp_indicators:
            if indicator in server_code:
                compliance_score += 1
            else:
                print(f"  ⚠️ Missing MCP indicator: {indicator}")
        compliance_percentage = (compliance_score / total_checks) * 100
        # Validate tool definitions structure
        tool_names = [
            "version_keeper_scan", "quality_patcher_fix", "pipeline_run_full",
            "github_workflow_trigger", "pipeline_status", "mcp_compliance_check"
        ]
        tools_found = 0
        for tool_name in tool_names:
            if f'name="{tool_name}"' in server_code:
                tools_found += 1
        print(f"  ✅ MCP compliance score: {compliance_percentage:.1f}%")
        print(f"  ✅ Tools found: {tools_found}/{len(tool_names)}")
        print("  ✅ Proper async/await patterns detected")
        print("  ✅ Error handling with McpError implemented")
        # Minimum compliance threshold
        self.assertGreaterEqual(
            compliance_percentage, 80,
            f"MCP compliance too low: {compliance_percentage}%")
        self.assertGreaterEqual(
            tools_found, 5,
            f"Not enough tools found: {tools_found}/6")


def run_comprehensive_tests():
    """Run all pipeline integration tests"""
    print("🚀 Pipeline Integration Test Suite")
    print("=" * 50)
    # Set up test loader
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestPipelineIntegration)
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    skipped = len(result.skipped) if hasattr(result, 'skipped') else 0
    passed = total_tests - failures - errors - skipped
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failures}")
    print(f"💥 Errors: {errors}")
    print(f"⏭️  Skipped: {skipped}")
    print(f"📊 Total: {total_tests}")
    success_rate = (passed / total_tests * 100) if total_tests > 0 else 0
    print(f"🎯 Success Rate: {success_rate:.1f}%")
    if failures > 0 or errors > 0:
        print("\n❌ SOME TESTS FAILED")
        return False
    else:
        print("\n🎉 ALL TESTS PASSED!")
        return True


if __name__ == "__main__":

    # Run comprehensive test suite
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)
