#!/usr/bin/env python3
"""
Direct Mem0 Usage - Bypass MCP and use Mem0 directly
"""

import sys
from pathlib import Path

# Add mcp-mem0 to path
sys.path.insert(0, str(Path.home() / "mcp-mem0" / "src"))

# Third-party imports (after path modification)
from dotenv import load_dotenv  # noqa: E402

# Local imports (after path modification)
from utils import get_mem0_client  # noqa: E402

# Load environment variables
load_dotenv(Path.home() / "mcp-mem0" / ".env")


def main_mem0_usage():
    # Get Mem0 client directly
    print("Initializing Mem0 client...")
    mem0 = get_mem0_client()

    print("Direct Mem0 Memory System")
    print("=" * 50)

    # Example: Save memories
    print("\n1. Saving memories...")
    messages = [
        {
            "role": "user",
            "content": "I prefer using Python for data science projects",
        }
    ]
    mem0.add(messages, user_id="user")
    print("   ✓ Saved preference")

    messages = [
        {
            "role": "user",
            "content": "My favorite IDE is VSCode with vim keybindings",
        }
    ]
    mem0.add(messages, user_id="user")
    print("   ✓ Saved IDE preference")

    # Example: Search memories
    print("\n2. Searching for 'programming'...")
    results = mem0.search("programming", user_id="user", limit=5)
    for i, result in enumerate(results, 1):
        if isinstance(result, dict):
            print(f"   {i}. {result.get('memory', result)}")
        else:
            print(f"   {i}. {result}")

    # Example: Get all memories
    print("\n3. All memories:")
    all_memories = mem0.get_all(user_id="user")
    if isinstance(all_memories, dict) and "results" in all_memories:
        memories = all_memories["results"]
    else:
        memories = all_memories

    for i, memory in enumerate(memories, 1):
        if isinstance(memory, dict):
            content = memory.get("memory", memory)
        else:
            content = memory
        print(f"   {i}. {content}")

    print("\n" + "=" * 50)
    print("You can now use mem0 directly in your Python scripts!")
    print("\nExample usage:")
    print("  from utils import get_mem0_client")
    print("  mem0 = get_mem0_client()")
    print('  mem0.add([{"role": "user", "content": "your text"}], user_id="user")')


if __name__ == "__main__":
    main_mem0_usage()
