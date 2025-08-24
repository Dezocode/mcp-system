#!/usr/bin/env python3
"""
MCP Manager - Unified API and CLI for managing MCP servers
"""

import argparse
import atexit
import json
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional

import requests


class MCPManager:
    def __init__(self, config_file: str = "~/.mcp-servers.json"):
        self.config_file = Path(config_file).expanduser()
        self.servers = self.load_config()
        self.running_servers = {}

        # Register cleanup on exit
        atexit.register(self.cleanup)
        signal.signal(signal.SIGINT, self.handle_interrupt)
        signal.signal(signal.SIGTERM, self.handle_interrupt)

    def load_config(self) -> Dict:
        """Load server configurations"""
        default_config = {
            "mem0": {
                "name": "Mem0 Memory Server",
                "path": "~/mcp-mem0",
                "command": "uv run python src/main.py",
                "port": 8050,
                "dependencies": {
                    "postgres": {
                        "type": "docker",
                        "image": "pgvector/pgvector:pg16",
                        "name": "mem0-postgres",
                        "env": {
                            "POSTGRES_PASSWORD": "mysecretpassword",
                            "POSTGRES_DB": "mem0db",
                        },
                        "ports": {"5432": "5432"},
                    },
                    "ollama": {
                        "type": "service",
                        "command": "ollama serve",
                        "check_url": "http://localhost:11434/api/tags",
                    },
                },
            }
        }

        if not self.config_file.exists():
            self.config_file.write_text(json.dumps(default_config, indent=2))
            return default_config

        return json.loads(self.config_file.read_text())

    def start_dependencies(self, server_name: str) -> bool:
        """Start server dependencies"""
        server = self.servers.get(server_name)
        if not server:
            return False

        deps = server.get("dependencies", {})
        for dep_name, dep_config in deps.items():
            if dep_config["type"] == "docker":
                # Check if container exists and is running
                result = subprocess.run(
                    f"docker ps -q -f name={dep_config['name']}",
                    shell=True,
                    capture_output=True,
                    text=True,
                )

                if not result.stdout.strip():
                    # Try to start existing container
                    start_result = subprocess.run(
                        f"docker start {dep_config['name']}",
                        shell=True,
                        capture_output=True,
                    )

                    if start_result.returncode != 0:
                        # Create new container
                        env_args = " ".join(
                            [
                                f"-e {k}={v}"
                                for k, v in dep_config.get("env", {}).items()
                            ]
                        )
                        port_args = " ".join(
                            [
                                f"-p {k}:{v}"
                                for k, v in dep_config.get("ports", {}).items()
                            ]
                        )

                        cmd = (
                            f"docker run --name {dep_config['name']} "
                            f"{env_args} {port_args} -d {dep_config['image']}"
                        )
                        subprocess.run(cmd, shell=True, check=True)
                        time.sleep(3)  # Wait for container to start

            elif dep_config["type"] == "service":
                # Check if service is running
                if "check_url" in dep_config:
                    try:
                        requests.get(dep_config["check_url"], timeout=1)
                    except Exception:
                        # Start service in background
                        subprocess.Popen(
                            dep_config["command"],
                            shell=True,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                        )
                        time.sleep(2)

        return True

    def start_server(self, server_name: str, foreground: bool = False) -> Dict:
        """Start an MCP server"""
        if server_name not in self.servers:
            return {
                "success": False,
                "error": f"Unknown server: {server_name}",
            }

        server = self.servers[server_name]

        # Start dependencies
        print(f"Starting dependencies for {server_name}...")
        self.start_dependencies(server_name)

        # Start server
        path = Path(server.get("path", ".")).expanduser()
        command = server.get("command")

        if not path.exists():
            return {
                "success": False,
                "error": f"Server path not found: {path}",
            }

        print(f"Starting {server_name} server...")

        if foreground:
            subprocess.run(command, shell=True, cwd=path)
            return {"success": True, "message": "Server stopped"}
        else:
            process = subprocess.Popen(
                command,
                shell=True,
                cwd=path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            self.running_servers[server_name] = {
                "process": process,
                "pid": process.pid,
                "started_at": time.time(),
            }

            # Wait and check if server started
            time.sleep(2)
            if process.poll() is None:
                return {
                    "success": True,
                    "pid": process.pid,
                    "port": server.get("port"),
                    "message": f"Server started on port {server.get('port')}",
                }
            else:
                stderr = (
                    process.stderr.read().decode() if process.stderr else ""
                )
                return {
                    "success": False,
                    "error": f"Server failed to start: {stderr}",
                }

    def stop_server(self, server_name: str) -> Dict:
        """Stop an MCP server"""
        if server_name in self.running_servers:
            info = self.running_servers[server_name]
            process = info["process"]

            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()

                del self.running_servers[server_name]
                return {
                    "success": True,
                    "message": f"Server {server_name} stopped",
                }
            else:
                del self.running_servers[server_name]
                return {"success": False, "error": "Server already stopped"}

        return {"success": False, "error": f"Server {server_name} not running"}

    def status(self, server_name: Optional[str] = None) -> Dict:
        """Get status of servers"""
        if server_name:
            if server_name in self.running_servers:
                info = self.running_servers[server_name]
                process = info["process"]

                if process.poll() is None:
                    server_config = self.servers.get(server_name, {})
                    return {
                        "success": True,
                        "status": "running",
                        "pid": info["pid"],
                        "uptime": time.time() - info["started_at"],
                        "port": server_config.get("port"),
                    }
                else:
                    del self.running_servers[server_name]
                    return {"success": True, "status": "stopped"}
            else:
                return {"success": True, "status": "stopped"}
        else:
            # Return all server statuses
            statuses = {}
            for name in self.servers:
                statuses[name] = self.status(name)
            return {"success": True, "servers": statuses}

    def send_data(self, server_name: str, tool: str, data: Any) -> Dict:
        """Send data to an MCP server"""
        if server_name not in self.servers:
            return {
                "success": False,
                "error": f"Unknown server: {server_name}",
            }

        server = self.servers[server_name]
        port = server.get("port")

        if not port:
            return {"success": False, "error": "Server port not configured"}

        # Check if server is running
        status = self.status(server_name)
        if status.get("status") != "running":
            return {"success": False, "error": "Server not running"}

        # Send MCP request
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
                            return {"success": True, "result": result}

            return {"success": False, "error": "No response from server"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def cleanup(self):
        """Clean up running servers"""
        for server_name in list(self.running_servers.keys()):
            self.stop_server(server_name)

    def handle_interrupt(self, signum, frame):
        """Handle interrupt signals"""
        print("\nShutting down servers...")
        self.cleanup()
        sys.exit(0)


def main_manager():
    parser = argparse.ArgumentParser(description="MCP Server Manager")
    parser.add_argument(
        "action",
        choices=["start", "stop", "restart", "status", "send", "list"],
    )
    parser.add_argument("server", nargs="?", default="mem0", help="Server name")
    parser.add_argument("--data", help="Data to send (JSON string)")
    parser.add_argument("--tool", help="Tool name for send action")
    parser.add_argument("--fg", action="store_true", help="Run in foreground")

    args = parser.parse_args()

    manager = MCPManager()

    if args.action == "list":
        servers = manager.servers
        print("Available servers:")
        for name, config in servers.items():
            print(f"  - {name}: {config.get('name', 'No description')}")

    elif args.action == "start":
        result = manager.start_server(args.server, args.fg)
        if result["success"]:
            print(f"✓ {result['message']}")
        else:
            print(f"✗ {result['error']}")
            sys.exit(1)

    elif args.action == "stop":
        result = manager.stop_server(args.server)
        if result["success"]:
            print(f"✓ {result['message']}")
        else:
            print(f"✗ {result['error']}")

    elif args.action == "restart":
        manager.stop_server(args.server)
        time.sleep(2)
        result = manager.start_server(args.server)
        if result["success"]:
            print(f"✓ Server restarted: {result['message']}")
        else:
            print(f"✗ {result['error']}")

    elif args.action == "status":
        result = manager.status(args.server if args.server != "mem0" else None)
        if args.server != "mem0" or result.get("status"):
            print(json.dumps(result, indent=2))
        else:
            print(json.dumps(result, indent=2))

    elif args.action == "send":
        if not args.tool:
            print("Error: --tool required for send action")
            sys.exit(1)

        data = json.loads(args.data) if args.data else {}
        result = manager.send_data(args.server, args.tool, data)

        if result["success"]:
            print(json.dumps(result["result"], indent=2))
        else:
            print(f"Error: {result['error']}")
            sys.exit(1)


if __name__ == "__main__":
    main_manager()
