#!/usr/bin/env python3
"""
MCP Router - Intelligent routing layer for Claude Code to use MCP servers
Analyzes user prompts and automatically selects/starts appropriate MCP servers
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

from src.config.cross_platform import cross_platform


class MCPRouter:
    def __init__(self):
        self.config_file = Path.home() / ".mcp-servers.json"
        self.servers = json.loads(self.config_file.read_text())

        # Define keyword mappings for automatic server selection
        self.server_keywords = {
            "mem0": [
                "memory",
                "remember",
                "recall",
                "memorize",
                "forget",
                "memories",
                "store",
                "retrieve",
            ],
            "filesystem": [
                "file",
                "directory",
                "folder",
                "read",
                "write",
                "create",
                "delete",
                "ls",
                "cat",
                "edit",
            ],
            "github": [
                "github",
                "repository",
                "repo",
                "commit",
                "pull request",
                "pr",
                "issue",
                "branch",
                "git",
            ],
            "slack": [
                "slack",
                "message",
                "channel",
                "dm",
                "workspace",
                "thread",
            ],
            "weather": [
                "weather",
                "temperature",
                "forecast",
                "rain",
                "snow",
                "climate",
                "sunny",
                "cloudy",
            ],
            "browser": [
                "browse",
                "web",
                "website",
                "url",
                "internet",
                "search",
                "google",
                "webpage",
            ],
            "database": [
                "database",
                "sql",
                "query",
                "table",
                "postgres",
                "mysql",
                "mongodb",
                "db",
            ],
            "email": [
                "email",
                "mail",
                "send",
                "inbox",
                "gmail",
                "outlook",
                "message",
            ],
        }

        # Task patterns for more complex matching
        self.task_patterns = {
            "mem0": [
                r"(save|store|remember|memorize).*for (later|future)",
                r"what.*(did|have) (i|we|you).*(say|mention|discuss)",
                r"recall.*previous",
            ],
            "filesystem": [
                r"(read|open|view|show).*file",
                r"(create|write|edit|modify).*file",
                r"list.*(files|directories)",
                r"(delete|remove).*file",
            ],
            "github": [
                r"(create|open|close).*issue",
                r"(create|merge).*pull request",
                r"(push|commit).*to.*(github|repo)",
            ],
        }

    def analyze_prompt(self, prompt: str) -> List[str]:
        """Analyze a user prompt and determine which MCP servers are needed"""
        prompt_lower = prompt.lower()
        relevant_servers = []
        scores = {}

        # Check keyword matches
        for server, keywords in self.server_keywords.items():
            score = sum(1 for keyword in keywords if keyword in prompt_lower)
            if score > 0:
                scores[server] = score

        # Check pattern matches (higher weight)
        for server, patterns in self.task_patterns.items():
            for pattern in patterns:
                if re.search(pattern, prompt_lower):
                    scores[server] = scores.get(server, 0) + 3

        # Sort by score and return servers with score > 0
        relevant_servers = sorted(
            [(server, score) for server, score in scores.items() if score > 0],
            key=lambda x: x[1],
            reverse=True,
        )

        return [server for server, _ in relevant_servers]

    def start_required_servers(self, servers: List[str]) -> Dict[str, bool]:
        """Start the required MCP servers"""
        results = {}

        for server in servers:
            if server not in self.servers:
                results[server] = False
                continue

            # Check if already running
            cmd = f"{cross_platform.get_path('home')}/mcp {server} status"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

            if "running" in result.stdout.lower():
                print(f"✅ {server} already running")
                results[server] = True
            else:
                print(f"Starting {server}...")
                cmd = f"{cross_platform.get_path('home')}/mcp {server} start"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                results[server] = result.returncode == 0

                if results[server]:
                    print(f"✅ {server} started")
                else:
                    print(f"❌ Failed to start {server}")

        return results

    def route_request(self, prompt: str, tool: str, data: Any) -> Dict:
        """Route a request to the appropriate MCP server"""
        # Analyze prompt to find relevant servers
        servers = self.analyze_prompt(prompt)

        if not servers:
            # Try to infer from tool name
            if "memory" in tool.lower() or "mem" in tool.lower():
                servers = ["mem0"]
            elif "file" in tool.lower() or "fs" in tool.lower():
                servers = ["filesystem"]
            else:
                return {
                    "error": "Could not determine appropriate MCP server",
                    "suggestion": "Please specify which server to use",
                }

        # Start required servers
        self.start_required_servers(servers[:1])  # Start only the top match

        # Send request to the most relevant server
        primary_server = servers[0]
        server_config = self.servers.get(primary_server)

        if not server_config:
            return {"error": f"Server {primary_server} not configured"}

        port = server_config.get("port")

        # Send the actual request
        import requests

        url = f"http://localhost:{port}/sse"
        payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {"name": tool, "arguments": data},
            "id": 1,
        }

        try:
            response = requests.post(url, json=payload, stream=True, timeout=5)

            for line in response.iter_lines():
                if line:
                    line = line.decode("utf-8")
                    if line.startswith("data: "):
                        data = line[6:]
                        if data:
                            result = json.loads(data)
                            return {"server": primary_server, "result": result}

            return {"error": "No response from server"}

        except Exception as e:
            return {"error": str(e), "server": primary_server}

    def interactive_mode(self):
        """Interactive mode for testing router logic"""
        print("MCP Router - Interactive Mode")
        print("=" * 50)
        print("Type your request and I'll determine which MCP server to use.")
        print("Type 'quit' to exit.\n")

        while True:
            try:
                prompt = input("Your request: ").strip()

                if prompt.lower() in ["quit", "exit"]:
                    break

                if not prompt:
                    continue

                servers = self.analyze_prompt(prompt)

                if servers:
                    print("\n🎯 Recommended servers (in order):")
                    for i, server in enumerate(servers, 1):
                        config = self.servers.get(server, {})
                        print(f"   {i}. {server}: {config.get('name', 'Unknown')}")

                    # Ask if they want to start the servers
                    response = input("\nStart these servers? (y/n): ").strip().lower()
                    if response == "y":
                        results = self.start_required_servers(servers)
                        print("\nServer startup results:")
                        for server, success in results.items():
                            status = "✅ Started" if success else "❌ Failed"
                            print(f"   {server}: {status}")
                else:
                    print("\n❓ No specific server identified.")
                    print("   Available servers:", ", ".join(self.servers.keys()))

                print()

            except KeyboardInterrupt:
                print("\n\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}")


# CLI for Claude Code integration
def main_router():
    parser = argparse.ArgumentParser(
        description="MCP Router - Intelligent MCP server selection"
    )
    parser.add_argument(
        "--analyze", help="Analyze a prompt and return recommended servers"
    )
    parser.add_argument("--route", help="Route a request to appropriate server")
    parser.add_argument("--tool", help="Tool name for routing")
    parser.add_argument("--data", help="JSON data for the tool")
    parser.add_argument("--interactive", action="store_true", help="Interactive mode")

    args = parser.parse_args()

    router = MCPRouter()

    if args.interactive:
        router.interactive_mode()

    elif args.analyze:
        servers = router.analyze_prompt(args.analyze)
        result = {
            "prompt": args.analyze,
            "recommended_servers": servers,
            "primary": servers[0] if servers else None,
        }
        print(json.dumps(result, indent=2))

    elif args.route:
        if not args.tool:
            print("Error: --tool required with --route")
            sys.exit(1)

        data = json.loads(args.data) if args.data else {}
        result = router.route_request(args.route, args.tool, data)
        print(json.dumps(result, indent=2))

    else:
        # Default: show server recommendations for stdin
        if not sys.stdin.isatty():
            prompt = sys.stdin.read().strip()
            servers = router.analyze_prompt(prompt)
            if servers:
                print(f"Recommended MCP servers: {', '.join(servers)}")
                router.start_required_servers(servers[:1])
            else:
                print("No specific MCP server identified")


if __name__ == "__main__":
    main_router()
