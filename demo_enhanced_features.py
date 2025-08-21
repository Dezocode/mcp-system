#!/usr/bin/env python3
"""
MCP System Environment Detection and Health Monitoring Demo
Demonstrates the enhanced capabilities of the MCP system with environment detection.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

async def demo_environment_detection():
    """Demonstrate environment detection capabilities"""
    print("🌍 Environment Detection Demo")
    print("=" * 50)
    
    from config.environment_detector import environment_detector
    from config.config_manager import config_manager
    from config.platform_adapter import platform_adapter
    from config.runtime_profiler import runtime_profiler
    
    # 1. Environment Detection
    print("\n1. 🔍 Environment Detection:")
    env_info = environment_detector.detect_environment()
    print(f"   Platform: {env_info.platform} {env_info.architecture}")
    print(f"   Docker: {env_info.is_docker}")
    print(f"   Container: {env_info.is_containerized}")
    print(f"   Python: {env_info.python_version}")
    print(f"   User: {env_info.user}")
    print(f"   Hostname: {env_info.hostname}")
    
    # 2. Adaptive Configuration
    print("\n2. ⚙️ Adaptive Configuration:")
    config = config_manager.get_config()
    print(f"   Workspace: {config.workspace_root}")
    print(f"   Sessions: {config.session_dir}")
    print(f"   Workers: {config.max_workers}")
    print(f"   Log Level: {config.log_level}")
    print(f"   Dashboard: {config.enable_dashboard}")
    
    # 3. Platform Optimizations
    print("\n3. 🔧 Platform Optimizations:")
    optimizations = platform_adapter.optimize_for_current_platform()
    print(f"   Optimal Workers: {optimizations['worker_count']}")
    print(f"   Temp Directory: {optimizations['temp_directory']}")
    print(f"   Buffer Sizes: {list(optimizations['buffer_sizes'].keys())}")
    
    # 4. Runtime Profiling
    print("\n4. 📊 Runtime Profiling:")
    runtime_profiler.start_profiling()
    await asyncio.sleep(1)  # Let it collect some data
    
    metrics = runtime_profiler.get_real_time_metrics()
    print(f"   CPU: {metrics['cpu_percent']:.1f}%")
    print(f"   Memory: {metrics['memory_mb']:.1f} MB")
    print(f"   Threads: {metrics['thread_count']}")
    
    profile = runtime_profiler.stop_profiling()
    summary = runtime_profiler.get_resource_usage_summary()
    print(f"   Duration: {summary['duration_seconds']:.1f}s")
    print(f"   Avg CPU: {summary['average_cpu_percent']:.1f}%")

async def demo_mcp_tools():
    """Demonstrate MCP tools functionality"""
    print("\n\n🛠️ MCP Tools Demo")
    print("=" * 50)
    
    from pipeline_mcp_server import handle_list_tools, handle_environment_detection, handle_health_monitoring
    
    # 1. List Available Tools
    print("\n1. 📋 Available Tools:")
    tools = await handle_list_tools()
    for i, tool in enumerate(tools, 1):
        print(f"   {i}. {tool.name}")
    
    # 2. Test Environment Detection Tool
    print("\n2. 🌍 Environment Detection Tool:")
    result = await handle_environment_detection({"action": "summary"})
    data = json.loads(result[0].text)
    summary = data["summary"]
    print(f"   Platform: {summary['platform']}")
    print(f"   Docker: {summary['is_docker']}")
    print(f"   Python: {summary['python_version']}")
    
    # 3. Test Health Monitoring Tool
    print("\n3. 🏥 Health Monitoring Tool:")
    result = await handle_health_monitoring({"action": "health_check"})
    data = json.loads(result[0].text)
    health = data["health_status"]
    print(f"   Status: {health['status']}")
    print(f"   Duration: {health['duration_ms']:.2f}ms")
    print(f"   Message: {health['message']}")

async def demo_docker_health_check():
    """Demonstrate Docker health check capabilities"""
    print("\n\n🐳 Docker Health Check Demo")
    print("=" * 50)
    
    from docker.health_check import docker_health_check
    from config.config_manager import config_manager
    
    # Set up health check
    docker_health_check.config_manager = config_manager
    
    # Perform comprehensive health check
    print("\n🔍 Comprehensive Health Check:")
    result = docker_health_check.perform_comprehensive_health_check()
    
    print(f"   Overall Status: {result.status.value}")
    print(f"   Message: {result.message}")
    print(f"   Duration: {result.duration_ms:.2f}ms")
    
    print("\n📊 Component Status:")
    for component, details in result.details.items():
        status = details.get("status", "unknown")
        print(f"   {component}: {status}")

async def main():
    """Main demo function"""
    print("🚀 MCP System Enhanced Features Demo")
    print("====================================")
    
    try:
        await demo_environment_detection()
        await demo_mcp_tools()
        await demo_docker_health_check()
        
        print("\n\n✅ Demo completed successfully!")
        print("\n🎯 Key Features Demonstrated:")
        print("   ✓ Automatic environment detection")
        print("   ✓ Adaptive configuration management")
        print("   ✓ Platform-specific optimizations")
        print("   ✓ Real-time performance monitoring")
        print("   ✓ Enhanced MCP tools")
        print("   ✓ Docker health checking")
        
        print("\n🐳 For Docker deployment:")
        print("   docker build -f Dockerfile.enhanced -t mcp-system .")
        print("   docker-compose -f docker-compose.enhanced.yml up")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())