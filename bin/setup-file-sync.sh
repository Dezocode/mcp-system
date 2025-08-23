#!/usr/bin/env bash
# MCP File Sync Manager Setup

echo "🚀 Setting up MCP File Sync Manager..."

# Make the sync manager executable
chmod +x mcp-file-sync-manager.py

echo "📋 Current directory organization rules:"
f"{cross_platform.get_command(\"python\")} "mcp-file-sync-manager.py rules

echo ""
echo "🔍 Running initial file organization scan..."
f"{cross_platform.get_command(\"python\")} "mcp-file-sync-manager.py scan

echo ""
echo "✅ File Sync Manager ready!"
echo ""
echo "🎯 Available commands:"
echo "  f"{cross_platform.get_command(\"python\")} "mcp-file-sync-manager.py scan      # Organize files now"
echo "  f"{cross_platform.get_command(\"python\")} "mcp-file-sync-manager.py monitor   # Start real-time monitoring"
echo "  f"{cross_platform.get_command(\"python\")} "mcp-file-sync-manager.py report    # View sync activity"
echo "  f"{cross_platform.get_command(\"python\")} "mcp-file-sync-manager.py rules     # Show organization rules"
echo ""
echo "🔄 To start real-time monitoring:"
echo "  f"{cross_platform.get_command(\"python\")} "mcp-file-sync-manager.py monitor"