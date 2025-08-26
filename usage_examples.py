#!/usr/bin/env python3
"""
Enhanced MCP Crafter Usage Examples
Demonstrates the complete workflow for creating complex MCP servers
"""

import json

# Example 1: Simple Claude Form for Weather Server
weather_server_form = {
    "server_name": "advanced-weather-api",
    "description": "Advanced weather MCP server with caching and monitoring",
    "complexity": "advanced",
    "capabilities": ["tools", "monitoring", "caching", "rate_limiting"],
    "template_base": "enterprise-python",
    "custom_tools": [
        {
            "name": "get_current_weather",
            "description": "Get current weather for a city",
            "parameters": {
                "city": {"type": "string", "required": True},
                "units": {"type": "string", "enum": ["metric", "imperial"], "default": "metric"}
            },
            "implementation": '''
# Get weather from API
import httpx
api_key = os.getenv("WEATHER_API_KEY")
url = f"https://api.openweathermap.org/data/2.5/weather?q={kwargs['city']}&appid={api_key}&units={kwargs.get('units', 'metric')}"
async with httpx.AsyncClient() as client:
    response = await client.get(url)
    return response.json()
'''
        },
        {
            "name": "get_forecast",
            "description": "Get weather forecast for a city",
            "parameters": {
                "city": {"type": "string", "required": True},
                "days": {"type": "integer", "default": 5, "minimum": 1, "maximum": 7}
            },
            "implementation": '''
# Get forecast from API
import httpx
api_key = os.getenv("WEATHER_API_KEY") 
url = f"https://api.openweathermap.org/data/2.5/forecast?q={kwargs['city']}&appid={api_key}&cnt={kwargs.get('days', 5) * 8}"
async with httpx.AsyncClient() as client:
    response = await client.get(url)
    return response.json()
'''
        }
    ],
    "dependencies": ["httpx", "redis"],
    "environment_vars": {
        "WEATHER_API_KEY": "your-openweathermap-api-key",
        "REDIS_URL": "redis://localhost:6379/0",
        "CACHE_TTL": "3600"
    },
    "deployment_config": {
        "docker": True,
        "compose": True,
        "kubernetes": False,
        "git": True
    },
    "metadata": {
        "author": "Enhanced MCP Crafter",
        "version": "1.0.0",
        "tags": ["weather", "api", "caching"]
    }
}

# Example 2: Complex Enterprise Workflow
enterprise_workflow = {
    "workflow_name": "ai-powered-data-pipeline",
    "servers": [
        {
            "name": "data-ingestion",
            "role": "Data ingestion and validation",
            "capabilities": ["tools", "monitoring", "persistence", "webhooks"],
            "custom_tools": [
                {
                    "name": "ingest_data",
                    "description": "Ingest data from various sources",
                    "parameters": {"source": {"type": "string"}, "format": {"type": "string"}}
                }
            ],
            "dependencies": ["sqlalchemy", "pandas", "requests"],
            "connections": ["data-processing", "notification-service"]
        },
        {
            "name": "data-processing", 
            "role": "ML processing and analysis",
            "capabilities": ["tools", "monitoring", "caching", "streaming"],
            "custom_tools": [
                {
                    "name": "process_data",
                    "description": "Process data with ML models",
                    "parameters": {"data_id": {"type": "string"}, "model": {"type": "string"}}
                }
            ],
            "dependencies": ["scikit-learn", "numpy", "redis"],
            "connections": ["data-ingestion", "ml-inference", "notification-service"]
        },
        {
            "name": "ml-inference",
            "role": "ML model inference and predictions", 
            "capabilities": ["tools", "monitoring", "authentication", "rate_limiting"],
            "custom_tools": [
                {
                    "name": "predict",
                    "description": "Make ML predictions",
                    "parameters": {"input_data": {"type": "object"}, "model": {"type": "string"}}
                }
            ],
            "dependencies": ["torch", "transformers", "pyjwt"],
            "connections": ["data-processing", "notification-service"]
        },
        {
            "name": "notification-service",
            "role": "Notifications and alerting",
            "capabilities": ["tools", "webhooks", "rate_limiting"],
            "custom_tools": [
                {
                    "name": "send_notification",
                    "description": "Send notifications via various channels",
                    "parameters": {"message": {"type": "string"}, "channel": {"type": "string"}}
                }
            ],
            "dependencies": ["httpx", "email-validator"],
            "connections": ["data-ingestion", "data-processing", "ml-inference"]
        }
    ],
    "orchestration": {
        "type": "microservices",
        "auto_deploy": True,
        "kubernetes": True,
        "monitoring": True,
        "service_mesh": True
    }
}

# Example 3: Streaming IoT Server
iot_streaming_form = {
    "server_name": "iot-streaming-hub",
    "description": "Real-time IoT data streaming and analytics hub",
    "complexity": "enterprise", 
    "capabilities": ["tools", "streaming", "monitoring", "persistence", "authentication"],
    "template_base": "streaming-websocket",
    "custom_tools": [
        {
            "name": "register_device",
            "description": "Register new IoT device",
            "parameters": {
                "device_id": {"type": "string", "required": True},
                "device_type": {"type": "string", "required": True},
                "location": {"type": "object"}
            }
        },
        {
            "name": "stream_sensor_data",
            "description": "Stream sensor data in real-time",
            "parameters": {
                "device_id": {"type": "string", "required": True},
                "sensor_data": {"type": "object", "required": True},
                "timestamp": {"type": "string"}
            }
        },
        {
            "name": "get_analytics",
            "description": "Get real-time analytics for devices",
            "parameters": {
                "device_ids": {"type": "array", "items": {"type": "string"}},
                "time_range": {"type": "string", "default": "1h"}
            }
        }
    ],
    "dependencies": ["websockets", "sqlalchemy", "pandas", "redis"],
    "environment_vars": {
        "DATABASE_URL": "postgresql://user:pass@localhost:5432/iot_hub",
        "REDIS_URL": "redis://localhost:6379/0",
        "WEBSOCKET_PORT": "8765",
        "JWT_SECRET": "your-jwt-secret"
    },
    "deployment_config": {
        "docker": True,
        "compose": True,
        "kubernetes": True,
        "scaling": {
            "min_replicas": 2,
            "max_replicas": 10,
            "cpu_threshold": 70
        }
    }
}

print("🎯 Enhanced MCP Crafter Usage Examples")
print("=" * 60)

examples = [
    {
        "title": "Advanced Weather API Server",
        "description": "Enterprise weather server with caching and rate limiting",
        "form": weather_server_form,
        "use_case": "Weather data API with enterprise features"
    },
    {
        "title": "AI-Powered Data Pipeline Workflow", 
        "description": "Complex multi-server workflow for data processing",
        "form": enterprise_workflow,
        "use_case": "Enterprise data pipeline with ML processing"
    },
    {
        "title": "IoT Streaming Hub",
        "description": "Real-time IoT data streaming and analytics",
        "form": iot_streaming_form,
        "use_case": "IoT device management and real-time analytics"
    }
]

for i, example in enumerate(examples, 1):
    print(f"\n{i}. 🚀 {example['title']}")
    print(f"   📝 {example['description']}")
    print(f"   🎯 Use Case: {example['use_case']}")
    
    # Show key configuration
    if "server_name" in example["form"]:
        form = example["form"]
        print(f"   🔧 Server: {form.get('server_name', 'N/A')}")
        print(f"   📊 Complexity: {form.get('complexity', 'N/A')}")
        print(f"   ⚙️  Capabilities: {', '.join(form.get('capabilities', []))}")
        print(f"   🛠️  Custom Tools: {len(form.get('custom_tools', []))}")
    elif "workflow_name" in example["form"]:
        workflow = example["form"]
        print(f"   🔧 Workflow: {workflow.get('workflow_name', 'N/A')}")
        print(f"   📊 Servers: {len(workflow.get('servers', []))}")
        print(f"   ⚙️  Orchestration: {workflow.get('orchestration', {}).get('type', 'N/A')}")
    
    print(f"   📄 Config file: example_{i}_config.json")

# Save example configurations
for i, example in enumerate(examples, 1):
    filename = f"example_{i}_config.json"
    with open(filename, "w") as f:
        json.dump(example["form"], f, indent=2)
    print(f"   ✅ Saved: {filename}")

print("\n" + "=" * 60)
print("📋 How to Use These Examples")
print("=" * 60)

usage_instructions = [
    "📂 **Via CLI with form file:**",
    "   mcp-crafter create --form example_1_config.json",
    "",
    "🎮 **Via Python API:**",
    "   from mcp_crafter import EnhancedMCPCrafter",
    "   crafter = EnhancedMCPCrafter()",
    "   build_id = await crafter.process_claude_form(form_data)",
    "",
    "🔧 **Via Crafter MCP Server:**",
    "   # Use the create_mcp_server tool with form data",
    "   # Use create_complex_workflow for multi-server setups",
    "",
    "🖥️  **Via Interactive CLI:**",
    "   mcp-crafter create weather-api --complexity advanced",
    "   # Follow prompts for configuration",
    "",
    "👁️  **Continuous Mode:**",
    "   mcp-crafter watch",
    "   # Monitors for changes and processes forms automatically"
]

for instruction in usage_instructions:
    print(instruction)

print("\n" + "=" * 60)
print("🎉 Ready for Complex MCP Server Generation!")
print("=" * 60)

print("""
The Enhanced MCP Crafter can now handle:

✅ **Enterprise-grade servers** with full capability modules
✅ **Complex multi-server workflows** with orchestration
✅ **Real-time streaming** and WebSocket integration  
✅ **ML inference servers** with model management
✅ **IoT data hubs** with device management
✅ **Microservice architectures** with service mesh
✅ **Kubernetes deployment** with auto-scaling
✅ **Continuous monitoring** and health checks

Each generated server includes:
🏗️  Complete source code structure
🐳 Docker and Docker Compose configurations
☸️  Kubernetes manifests (when enabled)
🧪 Comprehensive test suites
📚 Full documentation
🔧 Development and production scripts
⚙️  Environment configuration templates

Start creating complex MCP servers now! 🚀
""")

print(f"\n📊 Total examples generated: {len(examples)}")
print("Ready to process with Enhanced MCP Crafter! 🎯")