#!/usr/bin/env python3
"""
MCP Tools Watchdog Demonstration
Shows the standardized mcp-tools functionality in action
"""

import sys
import time
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent / "scripts"))

from mcp_tools_monitor import MCPToolsStandardizer
from migrate_to_mcp_tools import MCPPathMigrator
from validate_mcp_tools import MCPToolsValidator


def main():
    """Demonstrate mcp-tools standardization and watchdog functionality"""

    print("🚀 MCP Tools Standardization & Watchdog Demonstration")
    print("=" * 60)

    mcp_tools_path = Path("mcp-tools")

    # 1. Show current structure
    print("\n📁 Current mcp-tools structure:")
    print("-" * 30)
    if mcp_tools_path.exists():
        for item in sorted(mcp_tools_path.iterdir()):
            if item.is_dir():
                if item.name.startswith("_"):
                    print(f"  📂 {item.name} (system directory)")
                else:
                    print(f"  🔧 {item.name} (MCP server)")

    # 2. Validate existing servers
    print("\n🔍 Validating existing MCP servers:")
    print("-" * 35)
    validator = MCPToolsValidator(mcp_tools_path)
    is_valid, report = validator.generate_report()

    # Show summary
    lines = report.split("\n")
    for line in lines:
        if "✅" in line or "❌" in line or "Overall status:" in line:
            print(f"  {line}")

    # 3. Show legacy path detection
    print("\n📍 Legacy path detection:")
    print("-" * 25)
    migrator = MCPPathMigrator()
    legacy_servers = migrator.find_legacy_servers()

    if legacy_servers:
        print(f"  Found {len(legacy_servers)} servers with legacy paths:")
        for name, path in list(legacy_servers.items())[:3]:  # Show first 3
            print(f"    • {name}: {path}")
        if len(legacy_servers) > 3:
            print(f"    ... and {len(legacy_servers) - 3} more")
    else:
        print("  ✅ All servers using standardized paths")

    # 4. Demonstrate standardizer capabilities
    print("\n⚙️  Standardizer capabilities:")
    print("-" * 30)
    standardizer = MCPToolsStandardizer(mcp_tools_path)

    print("  ✅ Watchdog monitoring support")
    print("  ✅ Real-time structure validation")
    print("  ✅ Template-based server creation")
    print("  ✅ Automatic path reference updates")
    print("  ✅ Standards enforcement")

    # 5. Show available commands
    print("\n🛠️  Available management commands:")
    print("-" * 35)
    print("  • python scripts/mcp_tools_monitor.py --validate-only")
    print("    └─ Validate existing structure")
    print("  • python scripts/mcp_tools_monitor.py --create-server <name>")
    print("    └─ Create new standardized server")
    print("  • python scripts/validate_mcp_tools.py")
    print("    └─ Comprehensive validation report")
    print("  • python scripts/migrate_to_mcp_tools.py --all --dry-run")
    print("    └─ Preview legacy server migration")

    # 6. Show monitoring log location
    monitoring_log = mcp_tools_path / "_monitoring" / "watchdog.log"
    if monitoring_log.exists():
        print(f"\n📊 Monitoring logs: {monitoring_log}")
        print("    Use 'tail -f' to watch real-time events")

    print("\n✨ MCP Tools standardization is active and ready!")
    print("   All new servers will use the standardized structure.")
    print("   Watchdog monitoring ensures compliance automatically.")


if __name__ == "__main__":
    main()
