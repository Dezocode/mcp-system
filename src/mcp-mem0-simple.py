#!/usr/bin/env python3
"""
Simple MCP-Mem0 Client using standard requests
"""

import requests
import json
import sys

class SimpleMCPClient:
    def __init__(self, base_url="http://localhost:8050"):
        self.base_url = base_url
        
    def call_tool(self, tool_name, arguments=None):
        """Call an MCP tool via HTTP"""
        
        # MCP uses JSON-RPC format
        payload = {
            "jsonrpc": "2.0",
            "method": f"tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments or {}
            },
            "id": 1
        }
        
        try:
            # Send POST request with SSE headers
            response = requests.post(
                f"{self.base_url}/sse",
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "text/event-stream"
                },
                stream=True
            )
            
            # Parse SSE response
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data = line[6:]
                        if data:
                            try:
                                result = json.loads(data)
                                if "result" in result:
                                    content = result["result"].get("content", [])
                                    if content and len(content) > 0:
                                        return content[0].get("text", "No response")
                                return json.dumps(result, indent=2)
                            except json.JSONDecodeError:
                                continue
                                
        except requests.exceptions.RequestException as e:
            return f"Error: {e}"
        
        return "No response received"

def main():
    client = SimpleMCPClient()
    
    print("Simple MCP-Mem0 Client")
    print("=" * 50)
    print("\nCommands:")
    print("  save <text>     - Save a memory")
    print("  search <query>  - Search memories")
    print("  list            - List all memories")
    print("  delete <id>     - Delete a memory")
    print("  clear           - Delete all memories")
    print("  quit            - Exit")
    print()
    
    while True:
        try:
            command = input("mcp-mem0> ").strip()
            
            if not command:
                continue
                
            parts = command.split(maxsplit=1)
            cmd = parts[0].lower()
            
            if cmd == "quit" or cmd == "exit":
                print("Goodbye!")
                break
                
            elif cmd == "save" and len(parts) > 1:
                text = parts[1]
                result = client.call_tool("save_memory", {"text": text})
                print(f"Result: {result}")
                
            elif cmd == "search" and len(parts) > 1:
                query = parts[1]
                result = client.call_tool("search_memories", {"query": query, "limit": 5})
                print(f"Results:\n{result}")
                
            elif cmd == "list":
                result = client.call_tool("get_all_memories")
                print(f"All memories:\n{result}")
                
            elif cmd == "delete" and len(parts) > 1:
                memory_id = parts[1]
                result = client.call_tool("delete_memory", {"memory_id": memory_id})
                print(f"Result: {result}")
                
            elif cmd == "clear":
                confirm = input("Delete all memories? (yes/no): ")
                if confirm.lower() == "yes":
                    result = client.call_tool("delete_all_memories")
                    print(f"Result: {result}")
                else:
                    print("Cancelled")
                    
            else:
                print("Invalid command. Type 'quit' to exit.")
                
        except KeyboardInterrupt:
            print("\nUse 'quit' to exit")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    # Check if requests is installed
    try:
        import requests
    except ImportError:
        print("Please install requests: pip install requests")
        sys.exit(1)
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:8050/sse", timeout=1)
    except:
        print("Error: MCP server is not running at http://localhost:8050")
        print("Start it with: cd mcp-mem0 && uv run python src/main.py")
        sys.exit(1)
    
    main()