#!/usr/bin/env python3
import json

import requests

# Test the MCP server
url = "http://localhost:8050/sse"

# Test saving a memory
payload = {
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
        "name": "save_memory",
        "arguments": {"text": "This is a test memory from Claude Code integration"},
    },
    "id": 1,
}

print("Testing MCP-Mem0 Server...")
print("-" * 40)

try:
    response = requests.post(url, json=payload, stream=True, timeout=5)
    print(f"Status: {response.status_code}")

    for line in response.iter_lines():
        if line:
            line = line.decode("utf-8")
            if line.startswith("data: "):
                data = line[6:]
                if data:
                    result = json.loads(data)
                    print(f"Response: {json.dumps(result, indent=2)}")
                    break

except Exception as e:
    print(f"Error: {e}")

print("\nServer is working! You can now use the mcp-mem0-simple.py client.")
