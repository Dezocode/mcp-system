#!/usr/bin/env python3
"""
MCP-Mem0 Client - Example integration script for interacting with the MCP memory server
"""

import asyncio
import json
import sys
from typing import Any, Dict, Optional

import aiohttp


class MCPMem0Client:
    def __init__(self, base_url: str = "http://localhost:8050"):
        self.base_url = base_url
        self.session_id = None

    async def send_request(
        self, method: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict:
        """Send a JSON-RPC request to the MCP server via SSE"""

        request = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": 1,
        }

        async with aiohttp.ClientSession() as session:
            headers = {
                "Content-Type": "application/json",
                "Accept": "text/event-stream",
            }

            # For SSE, we need to establish a connection and send messages
            async with session.post(
                f"{self.base_url}/sse", json=request, headers=headers
            ) as response:

                # Read the SSE response
                async for line in response.content:
                    line = line.decode("utf-8").strip()
                    if line.startswith("data: "):
                        data = line[6:]  # Remove 'data: ' prefix
                        if data:
                            try:
                                return json.loads(data)
                            except json.JSONDecodeError:
                                continue

    async def save_memory(self, text: str) -> str:
        """Save text to memory"""
        result = await self.send_request(
            "tools/call", {"name": "save_memory", "arguments": {"text": text}}
        )
        return result.get("content", [{}])[0].get("text", "Error saving memory")

    async def search_memories(self, query: str, limit: int = 3) -> str:
        """Search memories"""
        result = await self.send_request(
            "tools/call",
            {
                "name": "search_memories",
                "arguments": {"query": query, "limit": limit},
            },
        )
        return result.get("content", [{}])[0].get(
            "text", "Error searching memories"
        )

    async def get_all_memories(self) -> str:
        """Get all memories"""
        result = await self.send_request(
            "tools/call", {"name": "get_all_memories", "arguments": {}}
        )
        return result.get("content", [{}])[0].get(
            "text", "Error retrieving memories"
        )

    async def delete_memory(self, memory_id: str) -> str:
        """Delete a specific memory"""
        result = await self.send_request(
            "tools/call",
            {"name": "delete_memory", "arguments": {"memory_id": memory_id}},
        )
        return result.get("content", [{}])[0].get(
            "text", "Error deleting memory"
        )

    async def delete_all_memories(self) -> str:
        """Delete all memories"""
        result = await self.send_request(
            "tools/call", {"name": "delete_all_memories", "arguments": {}}
        )
        return result.get("content", [{}])[0].get(
            "text", "Error deleting memories"
        )


async def main():
    # Create client
    client = MCPMem0Client()

    print("MCP-Mem0 Client Demo")
    print("=" * 50)

    # Example operations
    print("\n1. Saving a memory...")
    result = await client.save_memory(
        (
            "My favorite programming language is Python. "
            "I love its simplicity and readability."
        )
    )
    print(f"   Result: {result}")

    print("\n2. Saving another memory...")
    result = await client.save_memory(
        (
            "I'm working on an MCP server integration for long-term "
            "memory storage using Mem0."
        )
    )
    print(f"   Result: {result}")

    print("\n3. Searching memories...")
    result = await client.search_memories("programming language", limit=5)
    print(f"   Result: {result}")

    print("\n4. Getting all memories...")
    result = await client.get_all_memories()
    print(f"   Result: {result}")

    print("\n" + "=" * 50)
    print("Demo completed!")


if __name__ == "__main__":
    # Check if aiohttp is available (already imported at top)
    try:
        aiohttp.ClientSession
    except NameError:
        print("Please install aiohttp: pip install aiohttp")
        sys.exit(1)

    asyncio.run(main())
