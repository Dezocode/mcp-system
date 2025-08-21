#!/usr/bin/env python3
"""
Test Pipeline Integration - Validate the enhanced CI/CD pipeline
"""

import asyncio
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Dict, List


class PipelineIntegrationTest:
    """Test the enhanced pipeline integration"""

    def __init__(self, repo_path: Path = None):
        self.repo_path = repo_path or Path.cwd()
        self.test_session_id = f"test-{int(time.time())}"
        self.session_dir = self.repo_path / "pipeline-sessions" / self.test_session_id

    def setup_test_session(self):
        """Set up test session directory"""
        self.session_dir.mkdir(parents=True, exist_ok=True)
        print(f"🧪 Test session: {self.test_session_id}")
        print(f"📁 Session dir: {self.session_dir}")

    def test_version_keeper_json_output(self) -> bool:
        """Test Version Keeper JSON output functionality"""
        print("\n🔍 Testing Version Keeper JSON output...")
        
        cmd = [
            sys.executable,
            "scripts/version_keeper.py",
            "--lint-only",
            "--comprehensive-lint",
            "--output-format=json",
            "--output-file",
            str(self.session_dir / "test-lint-report.json"),
            "--session-id",
            self.test_session_id,
        ]

        try:
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=60
            )

            # Check if JSON file was created
            json_file = self.session_dir / "test-lint-report.json"
            if not json_file.exists():
                print(f"❌ JSON file not created: {json_file}")
                return False

            # Validate JSON structure
            with open(json_file) as f:
                report = json.load(f)

            required_fields = ["timestamp", "summary", "details"]
            for field in required_fields:
                if field not in report:
                    print(f"❌ Missing required field: {field}")
                    return False

            print("✅ Version Keeper JSON output working")
            return True

        except Exception as e:
            print(f"❌ Version Keeper test failed: {e}")
            return False

    def test_quality_patcher_json_output(self) -> bool:
        """Test Quality Patcher JSON output functionality"""
        print("\n🔧 Testing Quality Patcher JSON output...")
        
        # First create a lint report for the quality patcher to use
        lint_report = {
            "timestamp": time.time(),
            "issues": [
                {
                    "type": "flake8",
                    "file": "test_file.py",
                    "line": 1,
                    "message": "Test issue"
                }
            ]
        }
        
        lint_file = self.session_dir / "test-lint-input.json"
        with open(lint_file, "w") as f:
            json.dump(lint_report, f)

        cmd = [
            sys.executable,
            "scripts/claude_quality_patcher.py",
            "--lint-report",
            str(lint_file),
            "--max-fixes=1",
            "--non-interactive",
            "--output-format=json",
            "--output-file",
            str(self.session_dir / "test-fixes-report.json"),
            "--session-dir",
            str(self.session_dir),
        ]

        try:
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=60
            )

            # Check if JSON file was created
            json_file = self.session_dir / "test-fixes-report.json"
            if not json_file.exists():
                print(f"❌ JSON file not created: {json_file}")
                return False

            # Validate JSON structure
            with open(json_file) as f:
                report = json.load(f)

            required_fields = ["timestamp", "summary", "session_results"]
            for field in required_fields:
                if field not in report:
                    print(f"❌ Missing required field: {field}")
                    return False

            print("✅ Quality Patcher JSON output working")
            return True

        except Exception as e:
            print(f"❌ Quality Patcher test failed: {e}")
            return False

    async def test_pipeline_mcp_server(self) -> bool:
        """Test Pipeline MCP Server functionality"""
        print("\n🚀 Testing Pipeline MCP Server...")
        
        try:
            # Import the MCP server
            sys.path.insert(0, str(self.repo_path / "src"))
            from pipeline_mcp_server import PipelineMCPServer
            
            # Create server instance
            server = PipelineMCPServer(self.repo_path)
            
            # Test version keeper scan tool
            scan_result = await server._version_keeper_scan({
                "session_id": self.test_session_id,
                "lint_only": True,
                "comprehensive": False  # Use fast mode for testing
            })
            
            if not scan_result or not scan_result[0].text:
                print("❌ MCP Server scan failed")
                return False
                
            print("✅ Pipeline MCP Server working")
            return True

        except Exception as e:
            print(f"❌ Pipeline MCP Server test failed: {e}")
            return False

    def test_github_workflow_syntax(self) -> bool:
        """Test GitHub workflow YAML syntax"""
        print("\n📋 Testing GitHub workflow syntax...")
        
        workflow_file = self.repo_path / ".github/workflows/pipeline-integration.yml"
        if not workflow_file.exists():
            print(f"❌ Workflow file not found: {workflow_file}")
            return False

        try:
            import yaml
            with open(workflow_file) as f:
                yaml_content = yaml.safe_load(f)
            
            # Check required fields
            required_fields = ["name", "on", "jobs"]
            for field in required_fields:
                if field not in yaml_content:
                    print(f"❌ Missing required workflow field: {field}")
                    return False

            # Check required jobs
            required_jobs = ["version-keeper-scan", "quality-patcher", "version-keeper-validate", "github-integration"]
            for job in required_jobs:
                if job not in yaml_content["jobs"]:
                    print(f"❌ Missing required job: {job}")
                    return False

            print("✅ GitHub workflow syntax valid")
            return True

        except Exception as e:
            print(f"❌ GitHub workflow test failed: {e}")
            return False

    def test_mcp_compliance(self) -> bool:
        """Test MCP compliance check functionality"""
        print("\n🔍 Testing MCP compliance check...")
        
        try:
            sys.path.insert(0, str(self.repo_path / "src"))
            from pipeline_mcp_server import PipelineMCPServer
            
            server = PipelineMCPServer(self.repo_path)
            
            # Run compliance check
            compliance_result = asyncio.run(server._mcp_compliance_check({
                "server_path": "src/",
                "fix_issues": False
            }))
            
            if not compliance_result or not compliance_result[0].text:
                print("❌ MCP compliance check failed")
                return False
                
            result_text = compliance_result[0].text
            if "Compliance Score:" not in result_text:
                print("❌ MCP compliance check missing score")
                return False
                
            print("✅ MCP compliance check working")
            return True

        except Exception as e:
            print(f"❌ MCP compliance test failed: {e}")
            return False

    def run_all_tests(self) -> Dict[str, bool]:
        """Run all integration tests"""
        print("🚀 Starting Pipeline Integration Tests")
        print("=" * 50)
        
        self.setup_test_session()
        
        tests = {
            "version_keeper_json": self.test_version_keeper_json_output,
            "quality_patcher_json": self.test_quality_patcher_json_output,
            "pipeline_mcp_server": lambda: asyncio.run(self.test_pipeline_mcp_server()),
            "github_workflow_syntax": self.test_github_workflow_syntax,
            "mcp_compliance": self.test_mcp_compliance,
        }
        
        results = {}
        for test_name, test_func in tests.items():
            try:
                results[test_name] = test_func()
            except Exception as e:
                print(f"❌ Test {test_name} crashed: {e}")
                results[test_name] = False
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 Test Results Summary")
        print("=" * 50)
        
        passed = sum(results.values())
        total = len(results)
        
        for test_name, passed_test in results.items():
            status = "✅ PASS" if passed_test else "❌ FAIL"
            print(f"{status} {test_name}")
        
        print(f"\n🎯 Overall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Pipeline integration is ready.")
        else:
            print("⚠️  Some tests failed. Please review and fix issues.")
        
        return results


def main():
    """Main test entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Pipeline Integration")
    parser.add_argument(
        "--repo-path",
        type=Path,
        default=None,
        help="Repository path (default: current directory)"
    )
    
    args = parser.parse_args()
    
    tester = PipelineIntegrationTest(args.repo_path)
    results = tester.run_all_tests()
    
    # Exit with error code if any tests failed
    if not all(results.values()):
        sys.exit(1)


if __name__ == "__main__":
    main()