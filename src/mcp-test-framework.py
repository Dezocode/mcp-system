#!/usr/bin/env python3
"""
MCP Testing Framework - Comprehensive testing tools for MCP servers
"""

import asyncio
import json
import time
import requests
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import argparse

@dataclass
class TestResult:
    """Test result data structure"""
    name: str
    status: str  # "pass", "fail", "skip"
    message: str
    duration: float
    details: Optional[Dict] = None

@dataclass
class ServerTestSuite:
    """Test suite for an MCP server"""
    server_name: str
    base_url: str
    tests: List[Dict]
    setup_commands: List[str] = None
    teardown_commands: List[str] = None

class MCPTester:
    def __init__(self, config_file: str = "~/.mcp-servers.json"):
        self.config_file = Path(config_file).expanduser()
        self.servers = self._load_config()
        self.results = []
    
    def _load_config(self) -> Dict:
        """Load MCP server configuration"""
        if not self.config_file.exists():
            return {}
        return json.loads(self.config_file.read_text())
    
    async def test_server_health(self, server_name: str) -> TestResult:
        """Test if server is running and responsive"""
        start_time = time.time()
        
        try:
            if server_name not in self.servers:
                return TestResult(
                    name="server_health",
                    status="fail", 
                    message=f"Server {server_name} not found in configuration",
                    duration=time.time() - start_time
                )
            
            server = self.servers[server_name]
            port = server.get("port")
            
            if not port:
                return TestResult(
                    name="server_health",
                    status="fail",
                    message="No port configured for server",
                    duration=time.time() - start_time
                )
            
            # Check if server responds
            response = requests.get(f"http://localhost:{port}/health", timeout=5)
            
            if response.status_code == 200:
                return TestResult(
                    name="server_health",
                    status="pass",
                    message="Server is healthy",
                    duration=time.time() - start_time,
                    details={"response": response.json()}
                )
            else:
                return TestResult(
                    name="server_health", 
                    status="fail",
                    message=f"Server returned status {response.status_code}",
                    duration=time.time() - start_time
                )
                
        except requests.exceptions.ConnectionError:
            return TestResult(
                name="server_health",
                status="fail",
                message="Could not connect to server",
                duration=time.time() - start_time
            )
        except Exception as e:
            return TestResult(
                name="server_health",
                status="fail", 
                message=f"Health check failed: {str(e)}",
                duration=time.time() - start_time
            )
    
    async def test_mcp_protocol(self, server_name: str) -> TestResult:
        """Test MCP protocol compliance"""
        start_time = time.time()
        
        try:
            server = self.servers[server_name]
            port = server.get("port")
            url = f"http://localhost:{port}/sse"
            
            # Test tools/list
            payload = {
                "jsonrpc": "2.0",
                "method": "tools/list", 
                "params": {},
                "id": 1
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code != 200:
                return TestResult(
                    name="mcp_protocol",
                    status="fail",
                    message=f"tools/list returned {response.status_code}",
                    duration=time.time() - start_time
                )
            
            # For SSE, we need to parse the response differently
            # This is a simplified version
            return TestResult(
                name="mcp_protocol",
                status="pass",
                message="MCP protocol responding",
                duration=time.time() - start_time
            )
            
        except Exception as e:
            return TestResult(
                name="mcp_protocol",
                status="fail",
                message=f"Protocol test failed: {str(e)}",
                duration=time.time() - start_time
            )
    
    async def test_tool_execution(self, server_name: str, tool_name: str, 
                                 args: Dict = None) -> TestResult:
        """Test execution of a specific tool"""
        start_time = time.time()
        
        try:
            server = self.servers[server_name]
            port = server.get("port")
            url = f"http://localhost:{port}/sse"
            
            payload = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": args or {}
                },
                "id": 1
            }
            
            response = requests.post(url, json=payload, stream=True, timeout=10)
            
            # Parse SSE response
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data = line[6:]
                        if data:
                            try:
                                result = json.loads(data)
                                return TestResult(
                                    name=f"tool_{tool_name}",
                                    status="pass",
                                    message=f"Tool {tool_name} executed successfully",
                                    duration=time.time() - start_time,
                                    details={"result": result}
                                )
                            except json.JSONDecodeError:
                                continue
            
            return TestResult(
                name=f"tool_{tool_name}",
                status="fail",
                message=f"No valid response from tool {tool_name}",
                duration=time.time() - start_time
            )
            
        except Exception as e:
            return TestResult(
                name=f"tool_{tool_name}",
                status="fail",
                message=f"Tool execution failed: {str(e)}",
                duration=time.time() - start_time
            )
    
    async def run_custom_test(self, server_name: str, test_config: Dict) -> TestResult:
        """Run a custom test based on configuration"""
        start_time = time.time()
        
        try:
            test_name = test_config.get("name", "custom_test")
            test_type = test_config.get("type", "tool")
            
            if test_type == "tool":
                tool_name = test_config.get("tool")
                args = test_config.get("args", {})
                expected = test_config.get("expected")
                
                result = await self.test_tool_execution(server_name, tool_name, args)
                
                # Check expected results if provided
                if expected and result.status == "pass":
                    # Simple string matching for now
                    response_text = str(result.details.get("result", ""))
                    if expected not in response_text:
                        result.status = "fail"
                        result.message = f"Expected '{expected}' not found in response"
                
                result.name = test_name
                return result
            
            elif test_type == "http":
                endpoint = test_config.get("endpoint")
                method = test_config.get("method", "GET")
                expected_status = test_config.get("expected_status", 200)
                
                server = self.servers[server_name]
                port = server.get("port")
                url = f"http://localhost:{port}{endpoint}"
                
                response = requests.request(method, url, timeout=10)
                
                if response.status_code == expected_status:
                    return TestResult(
                        name=test_name,
                        status="pass",
                        message=f"HTTP {method} {endpoint} returned {response.status_code}",
                        duration=time.time() - start_time
                    )
                else:
                    return TestResult(
                        name=test_name,
                        status="fail",
                        message=f"Expected {expected_status}, got {response.status_code}",
                        duration=time.time() - start_time
                    )
            
            else:
                return TestResult(
                    name=test_name,
                    status="skip",
                    message=f"Unknown test type: {test_type}",
                    duration=time.time() - start_time
                )
                
        except Exception as e:
            return TestResult(
                name=test_config.get("name", "custom_test"),
                status="fail",
                message=f"Custom test failed: {str(e)}",
                duration=time.time() - start_time
            )
    
    async def run_server_tests(self, server_name: str, 
                              test_suite: ServerTestSuite = None) -> List[TestResult]:
        """Run complete test suite for a server"""
        results = []
        
        print(f"Testing server: {server_name}")
        
        # Basic health check
        health_result = await self.test_server_health(server_name)
        results.append(health_result)
        print(f"  Health: {health_result.status} - {health_result.message}")
        
        if health_result.status != "pass":
            print(f"  Skipping further tests due to health check failure")
            return results
        
        # MCP protocol test
        protocol_result = await self.test_mcp_protocol(server_name)
        results.append(protocol_result)
        print(f"  Protocol: {protocol_result.status} - {protocol_result.message}")
        
        # Common tool tests
        common_tools = ["hello_world", "get_status"]
        for tool in common_tools:
            tool_result = await self.test_tool_execution(server_name, tool)
            results.append(tool_result)
            print(f"  Tool {tool}: {tool_result.status} - {tool_result.message}")
        
        # Custom tests if provided
        if test_suite and test_suite.tests:
            for test_config in test_suite.tests:
                custom_result = await self.run_custom_test(server_name, test_config)
                results.append(custom_result)
                print(f"  {custom_result.name}: {custom_result.status} - {custom_result.message}")
        
        return results
    
    def generate_report(self, results: List[TestResult]) -> Dict:
        """Generate a comprehensive test report"""
        total = len(results)
        passed = len([r for r in results if r.status == "pass"])
        failed = len([r for r in results if r.status == "fail"])
        skipped = len([r for r in results if r.status == "skip"])
        
        total_duration = sum(r.duration for r in results)
        
        report = {
            "summary": {
                "total": total,
                "passed": passed, 
                "failed": failed,
                "skipped": skipped,
                "success_rate": f"{(passed/total*100):.1f}%" if total > 0 else "0%",
                "total_duration": f"{total_duration:.2f}s"
            },
            "results": [asdict(r) for r in results]
        }
        
        return report
    
    def start_server_if_needed(self, server_name: str) -> bool:
        """Start server if it's not running"""
        try:
            # Check if server is running
            result = subprocess.run(
                f"mcp {server_name} status", 
                shell=True, 
                capture_output=True, 
                text=True
            )
            
            if "running" in result.stdout.lower():
                print(f"Server {server_name} is already running")
                return True
            
            print(f"Starting server {server_name}...")
            start_result = subprocess.run(
                f"mcp {server_name} start",
                shell=True,
                capture_output=True,
                text=True
            )
            
            if start_result.returncode == 0:
                print(f"Server {server_name} started successfully")
                # Wait a moment for server to be ready
                time.sleep(3)
                return True
            else:
                print(f"Failed to start server {server_name}")
                print(f"Error: {start_result.stderr}")
                return False
                
        except Exception as e:
            print(f"Error managing server {server_name}: {e}")
            return False

# Predefined test suites for common server types
DEFAULT_TEST_SUITES = {
    "mem0": ServerTestSuite(
        server_name="mem0",
        base_url="http://localhost:8050",
        tests=[
            {
                "name": "save_memory",
                "type": "tool",
                "tool": "save_memory",
                "args": {"text": "Test memory for automated testing"},
                "expected": "Successfully saved memory"
            },
            {
                "name": "search_memories",
                "type": "tool", 
                "tool": "search_memories",
                "args": {"query": "test", "limit": 3}
            },
            {
                "name": "get_all_memories",
                "type": "tool",
                "tool": "get_all_memories",
                "args": {}
            }
        ]
    ),
    "filesystem": ServerTestSuite(
        server_name="filesystem",
        base_url="http://localhost:8051",
        tests=[
            {
                "name": "list_directory",
                "type": "tool",
                "tool": "list_directory",
                "args": {"path": "/tmp"}
            },
            {
                "name": "read_file",
                "type": "tool",
                "tool": "read_file", 
                "args": {"path": "/etc/hostname"}
            }
        ]
    )
}

async def main():
    parser = argparse.ArgumentParser(
        description="MCP Server Testing Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  mcp-test mem0                    # Test mem0 server
  mcp-test all                     # Test all configured servers  
  mcp-test mem0 --start            # Start server before testing
  mcp-test mem0 --report report.json # Save detailed report
        """
    )
    
    parser.add_argument("server", nargs="?", default="all",
                       help="Server name to test (or 'all' for all servers)")
    parser.add_argument("--start", action="store_true",
                       help="Start server before testing if not running")
    parser.add_argument("--report", help="Save detailed report to JSON file")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Verbose output")
    
    args = parser.parse_args()
    
    tester = MCPTester()
    all_results = []
    
    if not tester.servers:
        print("No MCP servers configured. Run 'mcp list' first.")
        return
    
    servers_to_test = list(tester.servers.keys()) if args.server == "all" else [args.server]
    
    for server_name in servers_to_test:
        if server_name not in tester.servers:
            print(f"Server {server_name} not found in configuration")
            continue
        
        # Start server if requested
        if args.start:
            if not tester.start_server_if_needed(server_name):
                print(f"Skipping tests for {server_name} due to startup failure")
                continue
        
        # Get test suite
        test_suite = DEFAULT_TEST_SUITES.get(server_name)
        
        # Run tests
        results = await tester.run_server_tests(server_name, test_suite)
        all_results.extend(results)
        
        print()  # Blank line between servers
    
    # Generate and display report
    report = tester.generate_report(all_results)
    
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Total tests: {report['summary']['total']}")
    print(f"Passed: {report['summary']['passed']}")
    print(f"Failed: {report['summary']['failed']}")
    print(f"Skipped: {report['summary']['skipped']}")
    print(f"Success rate: {report['summary']['success_rate']}")
    print(f"Total duration: {report['summary']['total_duration']}")
    
    # Save detailed report if requested
    if args.report:
        report_path = Path(args.report)
        report_path.write_text(json.dumps(report, indent=2))
        print(f"\\nDetailed report saved to: {report_path}")
    
    # Exit with appropriate code
    if report['summary']['failed'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())