#!/usr/bin/env python3
"""
Enhanced Demo: Docker Launch and AI Steering Capabilities
Demonstrates the new features added to the MCP Orchestrator Server
"""

import asyncio
import json
import sys
from pathlib import Path

# Add orchestrator to path
sys.path.insert(0, str(Path(__file__).parent))

from orchestrator.main import (
    handle_docker_launch,
    handle_docker_operation,
    handle_health_monitoring,
    orchestrator_server
)


async def demo_docker_launch():
    """Demonstrate Docker launch capabilities."""
    print("\n🚀 Docker Launch Capabilities Demo")
    print("=" * 50)
    
    # Test auto-detection
    print("\n1. Auto-platform Docker launch:")
    result = await handle_docker_launch({
        "platform": "auto",
        "wait_for_ready": False,
        "timeout": 30
    })
    demo_result = json.loads(result[0].text)
    print(f"   Platform detected: {demo_result.get('platform_detected')}")
    print(f"   Platform resolved: {demo_result.get('platform_resolved')}")
    print(f"   Success: {demo_result.get('success')}")
    print(f"   Message: {demo_result.get('message')}")
    
    # Test platform-specific
    print("\n2. Linux-specific Docker launch:")
    result = await handle_docker_launch({
        "platform": "linux",
        "wait_for_ready": False,
        "timeout": 30
    })
    demo_result = json.loads(result[0].text)
    print(f"   Success: {demo_result.get('success')}")
    print(f"   Message: {demo_result.get('message')}")


async def demo_platform_resolution():
    """Demonstrate enhanced platform resolution."""
    print("\n🌐 Enhanced Platform Resolution Demo")
    print("=" * 50)
    
    platform_info = orchestrator_server.platform_info
    print(f"\nPlatform: {platform_info['system']}")
    print(f"Architecture: {platform_info['architecture']}")
    print(f"Capabilities: {', '.join(platform_info['capabilities'])}")
    print(f"Docker Available: {platform_info['docker_available']}")
    print(f"FastAPI Available: {platform_info['fastapi_available']}")
    print(f"Watchdog Available: {platform_info['watchdog_available']}")
    
    if platform_info['system'] == 'Linux':
        print(f"SystemCtl Available: {platform_info.get('systemctl_available', 'Unknown')}")
        print(f"Docker Daemon Available: {platform_info.get('dockerd_available', 'Unknown')}")


async def demo_health_monitoring():
    """Demonstrate comprehensive health monitoring."""
    print("\n👁️ Health Monitoring Demo")
    print("=" * 50)
    
    # System health
    print("\n1. System Health:")
    result = await handle_health_monitoring({
        "scope": "system",
        "detailed": True
    })
    health_data = json.loads(result[0].text)
    
    if "system" in health_data:
        sys_health = health_data["system"]
        print(f"   CPU Usage: {sys_health.get('cpu_percent', 'N/A')}%")
        print(f"   Memory Usage: {sys_health.get('memory', {}).get('percent', 'N/A')}%")
        print(f"   Process Count: {sys_health.get('process_count', 'N/A')}")
    
    # Docker health
    print("\n2. Docker Health:")
    result = await handle_health_monitoring({
        "scope": "docker",
        "detailed": True
    })
    health_data = json.loads(result[0].text)
    
    if "docker" in health_data:
        docker_health = health_data["docker"]
        if "error" in docker_health:
            print(f"   Docker Status: Error - {docker_health['error']}")
        else:
            print(f"   Running Containers: {docker_health.get('containers_running', 'N/A')}")
            print(f"   Total Images: {docker_health.get('images', 'N/A')}")
            print(f"   Server Version: {docker_health.get('server_version', 'N/A')}")


def demo_web_api_info():
    """Demonstrate Web API configuration for AI steering."""
    print("\n🤖 AI Steering via Web API Demo")
    print("=" * 50)
    
    print("\nWeb API Configuration:")
    print(f"   FastAPI Available: {orchestrator_server.web_api.app is not None}")
    print(f"   Web Server Enabled: {orchestrator_server.web_server_enabled}")
    print(f"   Host: {orchestrator_server.web_server_host}")
    print(f"   Port: {orchestrator_server.web_server_port}")
    
    print("\nAPI Endpoints for AI Steering:")
    endpoints = [
        "GET  /api/status - Overall orchestrator status",
        "POST /api/docker/launch - Launch Docker via API",
        "POST /api/docker/operation - Execute Docker operations",
        "POST /api/container/management - Container management",
        "POST /api/environment/setup - Environment setup",
        "POST /api/health/monitoring - Health monitoring",
        "GET  /api/platforms/detect - Detect platform capabilities",
        "POST /api/config/update - Update configuration dynamically",
        "WS   /ws/updates - WebSocket for real-time updates"
    ]
    
    for endpoint in endpoints:
        print(f"   {endpoint}")
    
    print("\nExample React/JSON Usage:")
    print("   # Launch Docker via API")
    print("   curl -X POST http://localhost:8000/api/docker/launch \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -d '{\"platform\": \"auto\", \"wait_for_ready\": true}'")
    
    print("\n   # Get platform detection for React app")
    print("   curl http://localhost:8000/api/platforms/detect")
    
    print("\n   # WebSocket connection for real-time updates")
    print("   const ws = new WebSocket('ws://localhost:8000/ws/updates');")


async def main():
    """Main demo function."""
    print("🔧 Enhanced MCP Orchestrator Server Demo")
    print("Showcasing Docker Launch, AI Steering, and Platform Resolution")
    print("=" * 70)
    
    try:
        # Demo new features
        await demo_docker_launch()
        await demo_platform_resolution()
        await demo_health_monitoring()
        demo_web_api_info()
        
        print("\n✅ Enhanced Demo Complete!")
        print("\nNew Features Summary:")
        print("• Docker Desktop/daemon launch capabilities (Windows/Linux/WSL/Mac)")
        print("• AI steering via React/JSON framework communication")
        print("• Enhanced cross-platform resolution and detection")
        print("• FastAPI web interface with WebSocket support")
        print("• Dynamic configuration management")
        print("• Comprehensive health monitoring")
        
        print(f"\nTo start with Web API: python3 -m orchestrator.main --enable-web-api")
        print(f"To see platform info: python3 -m orchestrator.main --platform-info")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())