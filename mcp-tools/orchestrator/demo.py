#!/usr/bin/env python3
"""
MCP Orchestrator Demo Script
Demonstrates the key capabilities of the orchestrator MCP server.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add the orchestrator to the path
sys.path.insert(0, str(Path(__file__).parent))

from orchestrator.main import (
    handle_cli_resolution,
    handle_docker_operation,
    handle_environment_setup,
    handle_health_monitoring,
    handle_list_tools,
    handle_watchdog_monitoring,
    handle_windows_integration,
    orchestrator_server,
)


async def demo_orchestrator():
    """Run orchestrator demonstration."""
    print("🚀 MCP Orchestrator Server Demo")
    print("=" * 50)

    # 1. List all available tools
    print("\n📋 1. Available Tools:")
    tools = await handle_list_tools()
    for i, tool in enumerate(tools, 1):
        print(f"   {i}. {tool.name}")
        print(f"      {tool.description}")

    # 2. Environment detection
    print("\n🔍 2. Environment Detection:")
    env_result = await handle_environment_setup({"action": "detect", "components": []})
    env_data = json.loads(env_result[0].text)
    detection = env_data["results"]["detection"]
    print(f"   Platform: {detection['platform']} {detection['architecture']}")
    print(f"   Python: {detection['python_version']}")
    print(f"   Docker Available: {detection['docker_available']}")
    print(f"   Watchdog Available: {detection['watchdog_available']}")

    # 3. Docker status check
    print("\n🐳 3. Docker Status:")
    docker_result = await handle_docker_operation(
        {"operation": "ps", "options": {"all": True}}
    )
    docker_data = json.loads(docker_result[0].text)
    docker_status = docker_data["docker_status"]
    print(f"   Docker Available: {docker_status['available']}")
    print(f"   Docker Running: {docker_status['running']}")
    if docker_status.get("version"):
        print(f"   Docker Version: {docker_status['version']}")
    print(f"   Containers: {docker_status.get('containers', 'N/A')}")
    print(f"   Images: {docker_status.get('images', 'N/A')}")

    # 4. Windows integration check
    print("\n🏢 4. Windows Integration:")
    windows_result = await handle_windows_integration({"action": "integration_check"})
    windows_data = json.loads(windows_result[0].text)
    integration_status = windows_data["integration_status"]
    print(f"   Platform: {integration_status['platform']}")
    if integration_status["wsl"]["is_wsl"]:
        print(f"   WSL Environment: Yes")
        print(
            f"   Available Distros: {len(integration_status['wsl']['available_distros'])}"
        )
    else:
        print(f"   WSL Environment: No")

    # 5. Health monitoring
    print("\n💓 5. System Health:")
    health_result = await handle_health_monitoring(
        {"scope": "system", "detailed": False}
    )
    health_data = json.loads(health_result[0].text)
    system_health = health_data["health_data"]["system"]
    print(f"   CPU Usage: {system_health['cpu_percent']:.1f}%")
    print(f"   Memory Usage: {system_health['memory']['percent']:.1f}%")
    print(f"   Process Count: {system_health['process_count']}")

    # 6. Watchdog monitoring demo
    print("\n👁️ 6. Watchdog Monitoring:")
    # Start monitoring the current directory
    monitor_result = await handle_watchdog_monitoring(
        {"action": "start", "path": str(Path.cwd()), "recursive": False}
    )
    monitor_data = json.loads(monitor_result[0].text)
    if monitor_data["success"]:
        monitor_id = monitor_data["monitor_id"]
        print(f"   ✅ Started monitoring: {monitor_id}")

        # Get monitoring status
        status_result = await handle_watchdog_monitoring(
            {"action": "status", "monitor_id": monitor_id}
        )
        status_data = json.loads(status_result[0].text)
        print(f"   📊 Monitor active for path: {status_data['monitor_status']['path']}")

        # Stop monitoring
        stop_result = await handle_watchdog_monitoring(
            {"action": "stop", "monitor_id": monitor_id}
        )
        stop_data = json.loads(stop_result[0].text)
        print(f"   🛑 Monitoring stopped: {stop_data['success']}")

    # 7. CLI resolution demo
    print("\n⚡ 7. CLI Resolution:")
    # Test safe command validation
    cli_result = await handle_cli_resolution(
        {"command": ["echo", "Hello from orchestrator!"], "validate_only": True}
    )
    cli_data = json.loads(cli_result[0].text)
    print(f"   ✅ Command validation: {cli_data['valid']}")
    print(f"   Message: {cli_data['validation_message']}")

    # Test dangerous command blocking
    danger_result = await handle_cli_resolution(
        {"command": ["rm", "-rf", "/important"], "validate_only": True}
    )
    danger_data = json.loads(danger_result[0].text)
    print(f"   🛡️ Dangerous command blocked: {not danger_data['valid']}")

    print("\n🎉 Demo Complete!")
    print("=" * 50)
    print("\nThe orchestrator provides:")
    print("✅ Windows Docker integration with WSL support")
    print("✅ Real-time file system monitoring via watchdog")
    print("✅ Safe CLI command resolution and execution")
    print("✅ Comprehensive health monitoring")
    print("✅ Environment detection and configuration")
    print("✅ Container lifecycle management")
    print("✅ Full MCP v1.0 protocol compliance")

    print(f"\n🔧 Server Status:")
    print(f"   Name: {orchestrator_server.server.name}")
    print(f"   Workspace: {orchestrator_server.workspace_root}")
    print(
        f"   Docker Available: {orchestrator_server.windows_docker.docker_client is not None}"
    )
    print(f"   Watchdog Available: {orchestrator_server.watchdog.enabled}")
    print(f"   Tools Available: {len(tools)}")


if __name__ == "__main__":
    try:
        asyncio.run(demo_orchestrator())
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        sys.exit(1)
