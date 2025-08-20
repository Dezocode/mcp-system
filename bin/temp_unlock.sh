#!/bin/bash
# Temporary unlock for development work

echo "🔓 Temporarily unlocking pipeline files for development..."

# Make files writable
chmod +w run-pipeline run-direct-pipeline mcp-claude-pipeline.py 2>/dev/null

echo "✅ Files temporarily unlocked"
echo "⚠️  Remember to re-protect after changes"