#!/usr/bin/env bash

echo "🚀 MCP System - GitHub Repository Setup Helper"
echo "=============================================="
echo ""

# Check if we're in the right directory
if [ ! -f "README.md" ] || [ ! -f "install.sh" ]; then
    echo "❌ Error: Please run this script from the mcp-system-complete directory"
    echo "   cd cross_platform.get_path("home") / mcp-system-complete"
    echo "   ./quick-setup.sh"
    exit 1
fi

echo "📁 Current directory: $(pwd)"
echo "📊 Files ready for upload: $(find . -type f | wc -l | tr -d ' ') files"
echo ""

# Check git status
echo "🔍 Checking git repository status..."
if [ ! -d ".git" ]; then
    echo "❌ No git repository found. Initializing..."
    git init
    git add .
    git commit -m "Initial release: Complete MCP System v1.0.0"
    git branch -M main
fi

# Check if remote exists
if ! git remote | grep -q origin; then
    echo "🔗 Adding GitHub remote..."
    git remote add origin https://github.com/Dezocode/mcp-system.git
fi

echo "✅ Git repository prepared"
echo ""

# Show current status
echo "📋 Repository Status:"
echo "   Branch: $(git branch --show-current)"
echo "   Remote: $(git remote get-url origin 2>/dev/null || echo 'Not set')"
echo "   Last commit: $(git log -1 --oneline 2>/dev/null || echo 'No commits')"
echo ""

echo "🚨 IMPORTANT: You must create the repository on GitHub first!"
echo ""
echo "📝 Next Steps:"
echo "1. 🌐 Go to: https://github.com/Dezocode"
echo "2. 🆕 Click 'New repository'"
echo "3. 📝 Repository name: mcp-system"
echo "4. 📄 Description: 🚀 Universal MCP server management system with permissionless Claude Code CLI integration"
echo "5. 🌍 Make it Public"
echo "6. ❌ Do NOT check any initialization boxes"
echo "7. ✅ Click 'Create repository'"
echo ""
echo "8. 🚀 Then run: git push -u origin main"
echo ""

# Test if repository exists
echo "🧪 Testing if repository exists..."
if git ls-remote origin >/dev/null 2>&1; then
    echo "✅ Repository exists! Ready to push."
    echo ""
    echo "🚀 Run this command to upload:"
    echo "   git push -u origin main"
else
    echo "❌ Repository doesn't exist yet."
    echo "   Please create it on GitHub first (steps above)"
fi

echo ""
echo "🎯 After successful push, visit:"
echo "   https://github.com/Dezocode/mcp-system"
echo ""
echo "🎊 Then create your first release with tag v1.0.0"