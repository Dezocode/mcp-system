#!/usr/bin/env python3
"""
Streamlined Pipeline MCP Server for Claude Integration
Focused on duplicate analysis and quality improvements

This server provides focused tools for duplicate analysis and pipeline usage:
1. detect_duplicates - Run comprehensive duplicate detection analysis
2. fix_duplicates - Apply fixes for identified duplicate code
3. pipeline_status - Get current pipeline status
4. run_version_keeper - Execute version keeper with duplicate detection
5. get_claude_instructions - Generate specific instructions for Claude
6. validate_changes - Validate changes made by Claude

Author: Pipeline Integration Team
Version: 1.1.0 (Streamlined for Claude)
MCP Protocol: v1.0
"""

import asyncio
import json
import logging
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions

# Add paths for imports
script_dir = Path(__file__).parent.parent
sys.path.insert(0, str(script_dir / "scripts"))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pipeline_mcp_server")

SERVER_NAME = "pipeline-mcp-server"
SERVER_VERSION = "1.1.0"

server = Server(SERVER_NAME)


class PipelineMCPServer:
    """Streamlined MCP Server for Pipeline and Duplicate Analysis"""

    def __init__(self):
        self.workspace_root = Path.cwd()
        self.session_dir = self.workspace_root / "pipeline-sessions"
        self.session_dir.mkdir(exist_ok=True)

    async def detect_duplicates(
        self, exclude_backups: bool = True, output_format: str = "json"
    ) -> Dict[str, Any]:
        """Run comprehensive duplicate detection analysis"""
        try:
            from version_keeper import MCPVersionKeeper

            keeper = MCPVersionKeeper(self.workspace_root)
            duplicates = keeper.detect_duplicate_implementations(
                exclude_backups=exclude_backups
            )

            # Generate Claude-friendly summary
            summary = {
                "total_duplicates": len(duplicates["duplicate_functions"]),
                "total_similar_classes": len(duplicates["similar_classes"]),
                "total_redundant_files": len(duplicates["redundant_files"]),
                "recommendations": duplicates["recommendations"],
                "claude_actions_needed": [],
            }

            # Add specific actions for Claude
            for dup in duplicates["duplicate_functions"]:
                summary["claude_actions_needed"].append(
                    {
                        "action": "review_and_consolidate",
                        "function": dup["function"],
                        "files": [dup["file1"], dup["file2"]],
                        "claude_instruction": f"Please review the duplicate function '{dup['function']}' in {dup['file1']}:{dup['line1']} and {dup['file2']}:{dup['line2']}. Determine which implementation to keep and remove the other.",
                    }
                )

            return {
                "success": True,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "duplicates": duplicates,
                "summary": summary,
            }

        except Exception as e:
            logger.error(f"Duplicate detection failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    async def run_version_keeper(self, args: List[str] = None) -> Dict[str, Any]:
        """Execute version keeper with specified arguments"""
        try:
            cmd = ["python3", str(script_dir / "scripts" / "version_keeper.py")]
            if args:
                cmd.extend(args)
            else:
                cmd.extend(["--detect-duplicates", "--output-format=json"])

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.workspace_root,
                timeout=300,
            )

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Version keeper execution timed out",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as e:
            logger.error(f"Version keeper execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    async def get_claude_instructions(self) -> Dict[str, Any]:
        """Generate specific instructions for Claude based on current state"""
        try:
            # Get current duplicate analysis
            duplicates_result = await self.detect_duplicates()

            if not duplicates_result["success"]:
                return duplicates_result

            instructions = []
            duplicates = duplicates_result["duplicates"]

            # Generate specific instructions for each duplicate
            for i, dup in enumerate(
                duplicates["duplicate_functions"][:10], 1
            ):  # Limit to 10 for manageable output
                instruction = {
                    "step": i,
                    "type": "duplicate_resolution",
                    "priority": "high",
                    "description": f"Resolve duplicate function: {dup['function']}",
                    "files_to_examine": [dup["file1"], dup["file2"]],
                    "claude_commands": [
                        f"Use Read tool to examine {dup['file1']} around line {dup['line1']}",
                        f"Use Read tool to examine {dup['file2']} around line {dup['line2']}",
                        "Compare the implementations and determine which is better",
                        "Use Edit/MultiEdit tool to remove the inferior implementation",
                        "Ensure no functionality is lost in the consolidation",
                    ],
                    "success_criteria": "Only one implementation of the function remains",
                }
                instructions.append(instruction)

            return {
                "success": True,
                "total_tasks": len(instructions),
                "instructions": instructions,
                "summary": f"Found {len(duplicates['duplicate_functions'])} duplicate functions requiring attention",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            logger.error(f"Instruction generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }


# Initialize server instance
pipeline_server = PipelineMCPServer()


@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """List available pipeline tools"""
    return [
        types.Tool(
            name="detect_duplicates",
            description="Run comprehensive duplicate detection analysis on the codebase",
            inputSchema={
                "type": "object",
                "properties": {
                    "exclude_backups": {
                        "type": "boolean",
                        "description": "Whether to exclude backup files from analysis",
                        "default": True,
                    },
                    "output_format": {
                        "type": "string",
                        "description": "Output format (json or text)",
                        "enum": ["json", "text"],
                        "default": "json",
                    },
                },
            },
        ),
        types.Tool(
            name="run_version_keeper",
            description="Execute version keeper with duplicate detection and quality checks",
            inputSchema={
                "type": "object",
                "properties": {
                    "args": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Command line arguments for version keeper",
                        "default": ["--detect-duplicates", "--output-format=json"],
                    }
                },
            },
        ),
        types.Tool(
            name="get_claude_instructions",
            description="Generate specific step-by-step instructions for Claude to fix duplicates",
            inputSchema={"type": "object", "properties": {}},
        ),
        types.Tool(
            name="pipeline_status",
            description="Get current pipeline status and health information",
            inputSchema={"type": "object", "properties": {}},
        ),
        types.Tool(
            name="validate_changes",
            description="Validate changes made by Claude and check if duplicates are resolved",
            inputSchema={
                "type": "object",
                "properties": {
                    "files_changed": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of files that were changed",
                    }
                },
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> List[types.TextContent]:
    """Handle tool calls"""
    try:
        if name == "detect_duplicates":
            result = await pipeline_server.detect_duplicates(
                exclude_backups=arguments.get("exclude_backups", True),
                output_format=arguments.get("output_format", "json"),
            )
        elif name == "run_version_keeper":
            result = await pipeline_server.run_version_keeper(
                args=arguments.get("args")
            )
        elif name == "get_claude_instructions":
            result = await pipeline_server.get_claude_instructions()
        elif name == "pipeline_status":
            result = {
                "success": True,
                "status": "running",
                "workspace": str(pipeline_server.workspace_root),
                "session_dir": str(pipeline_server.session_dir),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        elif name == "validate_changes":
            # Re-run duplicate detection to see if changes resolved issues
            result = await pipeline_server.detect_duplicates()
            if result["success"]:
                result["validation"] = {
                    "files_changed": arguments.get("files_changed", []),
                    "duplicates_remaining": len(
                        result["duplicates"]["duplicate_functions"]
                    ),
                    "status": (
                        "improved"
                        if len(result["duplicates"]["duplicate_functions"]) < 3
                        else "needs_work"
                    ),
                }
        else:
            result = {"success": False, "error": f"Unknown tool: {name}"}

        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

    except Exception as e:
        logger.error(f"Tool execution failed: {e}")
        return [
            types.TextContent(
                type="text",
                text=json.dumps(
                    {
                        "success": False,
                        "error": str(e),
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    },
                    indent=2,
                ),
            )
        ]


async def main():
    """Main server entry point"""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name=SERVER_NAME,
                server_version=SERVER_VERSION,
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
