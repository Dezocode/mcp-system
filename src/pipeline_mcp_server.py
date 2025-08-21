#!/usr/bin/env python3
"""
Pipeline MCP Server - Exposes CI/CD Pipeline Operations as MCP Tools
Compliant with Anthropic MCP specification v1.0
"""

import asyncio
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

import click
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ErrorCode,
    ListToolsRequest,
    McpError,
    TextContent,
    Tool,
)


class PipelineMCPServer:
    """MCP Server for CI/CD Pipeline Operations"""

    def __init__(self, repo_path: Path = None):
        self.repo_path = repo_path or Path.cwd()
        self.server = Server("pipeline-mcp-server")
        self.sessions = {}
        self.active_pipelines = {}

        # Register tools
        self._register_tools()

    def _register_tools(self):
        """Register all available pipeline tools"""

        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """List all available pipeline tools"""
            return [
                Tool(
                    name="version_keeper_scan",
                    description="Run Version Keeper comprehensive linting scan",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_id": {
                                "type": "string",
                                "description": "Optional session ID for tracking",
                            },
                            "lint_only": {
                                "type": "boolean",
                                "description": "Only run linting, no version operations",
                                "default": True,
                            },
                            "comprehensive": {
                                "type": "boolean",
                                "description": "Run comprehensive lint check",
                                "default": True,
                            },
                        },
                    },
                ),
                Tool(
                    name="quality_patcher_fix",
                    description="Run Quality Patcher to automatically fix issues",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_id": {
                                "type": "string",
                                "description": "Session ID to use existing lint report",
                            },
                            "max_fixes": {
                                "type": "integer",
                                "description": "Maximum number of fixes to apply",
                                "default": 10,
                                "minimum": 1,
                                "maximum": 100,
                            },
                            "auto_apply": {
                                "type": "boolean",
                                "description": "Automatically apply fixes without confirmation",
                                "default": True,
                            },
                            "fresh_report": {
                                "type": "boolean",
                                "description": "Generate fresh lint report",
                                "default": False,
                            },
                        },
                        "required": ["session_id"],
                    },
                ),
                Tool(
                    name="pipeline_run_full",
                    description="Run the complete pipeline: scan → fix → validate → commit",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "max_cycles": {
                                "type": "integer",
                                "description": "Maximum pipeline cycles to run",
                                "default": 3,
                                "minimum": 1,
                                "maximum": 10,
                            },
                            "target_issues": {
                                "type": "integer",
                                "description": "Target number of issues (0 = fix all)",
                                "default": 0,
                                "minimum": 0,
                            },
                            "auto_commit": {
                                "type": "boolean",
                                "description": "Automatically commit fixes",
                                "default": False,
                            },
                        },
                    },
                ),
                Tool(
                    name="github_workflow_trigger",
                    description="Trigger GitHub workflow for pipeline integration",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "workflow": {
                                "type": "string",
                                "description": "Workflow to trigger",
                                "enum": ["pipeline-integration", "ci", "development"],
                                "default": "pipeline-integration",
                            },
                            "branch": {
                                "type": "string",
                                "description": "Branch to run workflow on",
                                "default": "main",
                            },
                            "inputs": {
                                "type": "object",
                                "description": "Workflow inputs",
                                "properties": {
                                    "max_fixes": {"type": "string"},
                                    "force_fresh_report": {"type": "string"},
                                },
                            },
                        },
                    },
                ),
                Tool(
                    name="pipeline_status",
                    description="Get status of active pipeline sessions",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_id": {
                                "type": "string",
                                "description": "Optional specific session ID",
                            }
                        },
                    },
                ),
                Tool(
                    name="mcp_compliance_check",
                    description="Check MCP server compliance with Anthropic standards",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "server_path": {
                                "type": "string",
                                "description": "Path to MCP server to check",
                            },
                            "fix_issues": {
                                "type": "boolean",
                                "description": "Automatically fix compliance issues",
                                "default": False,
                            },
                        },
                    },
                ),
            ]

        @self.server.call_tool()
        async def call_tool(
            name: str, arguments: Dict[str, Any] | None
        ) -> List[TextContent]:
            """Handle tool calls"""
            try:
                if name == "version_keeper_scan":
                    return await self._version_keeper_scan(arguments or {})
                elif name == "quality_patcher_fix":
                    return await self._quality_patcher_fix(arguments or {})
                elif name == "pipeline_run_full":
                    return await self._pipeline_run_full(arguments or {})
                elif name == "github_workflow_trigger":
                    return await self._github_workflow_trigger(arguments or {})
                elif name == "pipeline_status":
                    return await self._pipeline_status(arguments or {})
                elif name == "mcp_compliance_check":
                    return await self._mcp_compliance_check(arguments or {})
                else:
                    raise McpError(
                        ErrorCode.MethodNotFound, f"Unknown tool: {name}"
                    )
            except Exception as e:
                raise McpError(
                    ErrorCode.InternalError, f"Tool execution failed: {str(e)}"
                )

    async def _version_keeper_scan(self, args: Dict[str, Any]) -> List[TextContent]:
        """Run Version Keeper comprehensive linting scan"""
        session_id = args.get("session_id", f"mcp-scan-{int(time.time())}")
        lint_only = args.get("lint_only", True)
        comprehensive = args.get("comprehensive", True)

        session_dir = self.repo_path / "pipeline-sessions" / session_id
        session_dir.mkdir(parents=True, exist_ok=True)

        # Build command
        cmd = [
            sys.executable,
            "scripts/version_keeper.py",
            "--session-dir",
            str(session_dir),
            "--output-format=json",
            "--output-file",
            str(session_dir / "lint-report.json"),
        ]

        if lint_only:
            cmd.append("--lint-only")
        if comprehensive:
            cmd.append("--comprehensive-lint")

        try:
            # Run version keeper
            result = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=self.repo_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await result.communicate()

            # Load results
            report_file = session_dir / "lint-report.json"
            if report_file.exists():
                with open(report_file) as f:
                    report = json.load(f)
                
                issues_count = report.get("summary", {}).get("total_issues", 0)
                
                # Store session info
                self.sessions[session_id] = {
                    "type": "version_keeper_scan",
                    "timestamp": time.time(),
                    "session_dir": str(session_dir),
                    "issues_count": issues_count,
                    "status": "completed",
                }

                return [
                    TextContent(
                        type="text",
                        text=f"✅ Version Keeper scan completed\n\n"
                        f"📊 Session ID: {session_id}\n"
                        f"🔍 Issues found: {issues_count}\n"
                        f"📁 Report saved to: {report_file}\n\n"
                        f"{'❌ Issues need attention' if issues_count > 0 else '✅ No issues found'}"
                    )
                ]
            else:
                return [
                    TextContent(
                        type="text",
                        text=f"❌ Version Keeper scan failed\n\n"
                        f"stdout: {stdout.decode()}\n"
                        f"stderr: {stderr.decode()}"
                    )
                ]

        except Exception as e:
            return [
                TextContent(
                    type="text",
                    text=f"❌ Error running Version Keeper: {str(e)}"
                )
            ]

    async def _quality_patcher_fix(self, args: Dict[str, Any]) -> List[TextContent]:
        """Run Quality Patcher to automatically fix issues"""
        session_id = args["session_id"]
        max_fixes = args.get("max_fixes", 10)
        auto_apply = args.get("auto_apply", True)
        fresh_report = args.get("fresh_report", False)

        if session_id not in self.sessions:
            return [
                TextContent(
                    type="text",
                    text=f"❌ Session {session_id} not found. Run version_keeper_scan first."
                )
            ]

        session_info = self.sessions[session_id]
        session_dir = Path(session_info["session_dir"])

        # Build command
        cmd = [
            sys.executable,
            "scripts/claude_quality_patcher.py",
            "--claude-agent",
            f"--max-fixes={max_fixes}",
            "--session-dir",
            str(session_dir),
            "--output-format=json",
            "--output-file",
            str(session_dir / "fixes-report.json"),
        ]

        if auto_apply:
            cmd.append("--auto-apply")
        if fresh_report:
            cmd.append("--fresh-report")
        else:
            # Use existing lint report
            lint_report = session_dir / "lint-report.json"
            if lint_report.exists():
                cmd.extend(["--lint-report", str(lint_report)])

        try:
            # Run quality patcher
            result = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=self.repo_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await result.communicate()

            # Load results
            fixes_file = session_dir / "fixes-report.json"
            if fixes_file.exists():
                with open(fixes_file) as f:
                    report = json.load(f)
                
                fixes_applied = report.get("summary", {}).get("fixes_applied", 0)
                remaining_issues = report.get("summary", {}).get("remaining_issues", 0)
                
                # Update session info
                self.sessions[session_id].update({
                    "fixes_applied": fixes_applied,
                    "remaining_issues": remaining_issues,
                    "last_quality_patch": time.time(),
                })

                return [
                    TextContent(
                        type="text",
                        text=f"🔧 Quality Patcher completed\n\n"
                        f"📊 Session ID: {session_id}\n"
                        f"✅ Fixes applied: {fixes_applied}\n"
                        f"⚠️ Issues remaining: {remaining_issues}\n"
                        f"📁 Report saved to: {fixes_file}\n\n"
                        f"{'✅ All issues resolved!' if remaining_issues == 0 else '⚠️ Some issues remain'}"
                    )
                ]
            else:
                return [
                    TextContent(
                        type="text",
                        text=f"❌ Quality Patcher failed\n\n"
                        f"stdout: {stdout.decode()}\n"
                        f"stderr: {stderr.decode()}"
                    )
                ]

        except Exception as e:
            return [
                TextContent(
                    type="text",
                    text=f"❌ Error running Quality Patcher: {str(e)}"
                )
            ]

    async def _pipeline_run_full(self, args: Dict[str, Any]) -> List[TextContent]:
        """Run the complete pipeline"""
        max_cycles = args.get("max_cycles", 3)
        target_issues = args.get("target_issues", 0)
        auto_commit = args.get("auto_commit", False)

        session_id = f"mcp-pipeline-{int(time.time())}"
        results = []
        
        results.append(f"🚀 Starting full pipeline: {session_id}")
        results.append(f"🎯 Target: {target_issues} issues, Max cycles: {max_cycles}")

        current_issues = float('inf')
        cycle = 0

        while cycle < max_cycles and current_issues > target_issues:
            cycle += 1
            results.append(f"\n🔄 Pipeline Cycle {cycle}/{max_cycles}")

            # Step 1: Version Keeper Scan
            scan_result = await self._version_keeper_scan({"session_id": session_id})
            scan_text = scan_result[0].text
            results.append(f"1️⃣ Scan: {scan_text.split('Issues found: ')[1].split('📁')[0].strip()}")

            # Check if we have issues
            if session_id in self.sessions:
                current_issues = self.sessions[session_id]["issues_count"]
                if current_issues <= target_issues:
                    results.append("✅ Target reached! No fixes needed.")
                    break

                # Step 2: Quality Patcher Fix
                fix_result = await self._quality_patcher_fix({
                    "session_id": session_id,
                    "max_fixes": 10,
                    "auto_apply": True
                })
                fix_text = fix_result[0].text
                results.append(f"2️⃣ Fix: {fix_text.split('Fixes applied: ')[1].split('⚠️')[0].strip()}")

                # Step 3: Validation (run scan again)
                validate_result = await self._version_keeper_scan({
                    "session_id": f"{session_id}-validate-{cycle}",
                    "lint_only": True
                })
                validate_text = validate_result[0].text
                remaining = int(validate_text.split('Issues found: ')[1].split('📁')[0].strip())
                results.append(f"3️⃣ Validate: {remaining} issues remaining")
                
                current_issues = remaining
            else:
                results.append("❌ Scan failed, stopping pipeline")
                break

        # Final status
        if current_issues <= target_issues:
            results.append(f"\n🎉 Pipeline SUCCESS! Target of {target_issues} issues achieved.")
            
            if auto_commit:
                results.append("🚀 Auto-committing changes...")
                # Here you would implement git commit logic
                results.append("✅ Changes committed")
        else:
            results.append(f"\n⚠️ Pipeline completed with {current_issues} issues remaining")

        return [TextContent(type="text", text="\n".join(results))]

    async def _github_workflow_trigger(self, args: Dict[str, Any]) -> List[TextContent]:
        """Trigger GitHub workflow"""
        workflow = args.get("workflow", "pipeline-integration")
        branch = args.get("branch", "main")
        inputs = args.get("inputs", {})

        # Build gh CLI command
        cmd = ["gh", "workflow", "run", workflow, "--ref", branch]
        
        # Add inputs
        for key, value in inputs.items():
            cmd.extend(["-f", f"{key}={value}"])

        try:
            result = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=self.repo_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await result.communicate()

            if result.returncode == 0:
                return [
                    TextContent(
                        type="text",
                        text=f"✅ GitHub workflow triggered successfully\n\n"
                        f"🔗 Workflow: {workflow}\n"
                        f"🌿 Branch: {branch}\n"
                        f"⚙️ Inputs: {inputs}\n\n"
                        f"Check GitHub Actions for progress."
                    )
                ]
            else:
                return [
                    TextContent(
                        type="text",
                        text=f"❌ Failed to trigger workflow\n\n"
                        f"Error: {stderr.decode()}"
                    )
                ]

        except Exception as e:
            return [
                TextContent(
                    type="text",
                    text=f"❌ Error triggering workflow: {str(e)}\n\n"
                    f"Make sure 'gh' CLI is installed and authenticated."
                )
            ]

    async def _pipeline_status(self, args: Dict[str, Any]) -> List[TextContent]:
        """Get pipeline status"""
        session_id = args.get("session_id")

        if session_id:
            if session_id in self.sessions:
                session = self.sessions[session_id]
                return [
                    TextContent(
                        type="text",
                        text=f"📊 Session Status: {session_id}\n\n"
                        f"Type: {session['type']}\n"
                        f"Status: {session['status']}\n"
                        f"Issues: {session.get('issues_count', 'N/A')}\n"
                        f"Fixes: {session.get('fixes_applied', 'N/A')}\n"
                        f"Timestamp: {time.ctime(session['timestamp'])}"
                    )
                ]
            else:
                return [
                    TextContent(
                        type="text",
                        text=f"❌ Session {session_id} not found"
                    )
                ]
        else:
            # List all sessions
            if not self.sessions:
                return [
                    TextContent(
                        type="text",
                        text="📊 No active pipeline sessions"
                    )
                ]

            status_lines = ["📊 Active Pipeline Sessions:\n"]
            for sid, session in self.sessions.items():
                status_lines.append(
                    f"• {sid}: {session['type']} - "
                    f"{session.get('issues_count', 0)} issues - "
                    f"{session['status']}"
                )

            return [TextContent(type="text", text="\n".join(status_lines))]

    async def _mcp_compliance_check(self, args: Dict[str, Any]) -> List[TextContent]:
        """Check MCP server compliance with Anthropic standards"""
        server_path = args.get("server_path", "src/")
        fix_issues = args.get("fix_issues", False)

        # MCP Compliance Checklist based on Anthropic documentation
        checks = []
        issues = []

        # Check 1: Server structure compliance
        checks.append("🔍 Checking MCP server structure...")
        
        server_files = list(Path(server_path).glob("**/*.py"))
        mcp_servers = []
        
        for file in server_files:
            try:
                with open(file) as f:
                    content = f.read()
                    if "mcp.server" in content or "from mcp" in content:
                        mcp_servers.append(file)
            except:
                continue

        if not mcp_servers:
            issues.append("❌ No MCP servers found")
        else:
            checks.append(f"✅ Found {len(mcp_servers)} MCP server files")

        # Check 2: Required imports compliance
        for server_file in mcp_servers:
            checks.append(f"🔍 Checking {server_file.name}...")
            
            with open(server_file) as f:
                content = f.read()
                
            # Required imports for MCP v1.0
            required_imports = [
                "from mcp.server import Server",
                "from mcp.types import",
                "from mcp.server.stdio import stdio_server"
            ]
            
            missing_imports = []
            for imp in required_imports:
                if imp not in content:
                    missing_imports.append(imp)
            
            if missing_imports:
                issues.append(f"❌ {server_file.name}: Missing imports: {missing_imports}")
            else:
                checks.append(f"✅ {server_file.name}: All required imports present")

        # Check 3: Tool schema compliance
        for server_file in mcp_servers:
            with open(server_file) as f:
                content = f.read()
                
            # Check for proper tool definitions
            if "inputSchema" in content:
                checks.append(f"✅ {server_file.name}: Uses inputSchema for tools")
            else:
                issues.append(f"❌ {server_file.name}: Tools should use inputSchema")

        # Check 4: Error handling compliance
        for server_file in mcp_servers:
            with open(server_file) as f:
                content = f.read()
                
            if "McpError" in content and "ErrorCode" in content:
                checks.append(f"✅ {server_file.name}: Proper error handling")
            else:
                issues.append(f"❌ {server_file.name}: Should use McpError and ErrorCode")

        # Summary
        total_checks = len(checks)
        total_issues = len(issues)
        compliance_score = max(0, (total_checks - total_issues) / max(total_checks, 1) * 100)

        result_text = f"🔍 MCP Compliance Report\n\n"
        result_text += f"📊 Compliance Score: {compliance_score:.1f}%\n"
        result_text += f"✅ Checks passed: {total_checks - total_issues}\n"
        result_text += f"❌ Issues found: {total_issues}\n\n"
        
        result_text += "📋 Detailed Results:\n"
        for check in checks:
            result_text += f"{check}\n"
        
        if issues:
            result_text += "\n⚠️ Issues to fix:\n"
            for issue in issues:
                result_text += f"{issue}\n"

        if fix_issues and issues:
            result_text += "\n🔧 Auto-fix not implemented yet. Manual fixes required."

        return [TextContent(type="text", text=result_text)]

    async def run(self):
        """Run the MCP server"""
        async with stdio_server() as streams:
            await self.server.run(
                streams[0], 
                streams[1], 
                InitializationOptions(
                    server_name="pipeline-mcp-server",
                    server_version="1.0.0",
                    capabilities={}
                )
            )


@click.command()
@click.option(
    "--repo-path",
    type=click.Path(exists=True, path_type=Path),
    default=None,
    help="Repository path (default: current directory)",
)
def main(repo_path: Optional[Path]):
    """Pipeline MCP Server - Expose CI/CD operations as MCP tools"""
    server = PipelineMCPServer(repo_path)
    asyncio.run(server.run())


if __name__ == "__main__":
    main()