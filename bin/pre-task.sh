#!/usr/bin/env bash
# Pre-task hook for automated MCP pipeline
# Triggers before each Claude Code task execution

echo "🔧 Pre-task hook: Preparing automated fix environment"

# DIAGNOSTIC: Check Claude Code status and permissions
echo "🔍 Environment diagnostics..."
if command -v claude >/dev/null 2>&1; then
    echo "✅ Claude Code CLI available"
    # Check if authenticated
    if claude --version >/dev/null 2>&1; then
        echo "✅ Claude Code accessible"
    else
        echo "⚠️ Claude Code authentication issues detected"
    fi
else
    echo "⚠️ Claude Code CLI not available - using fallback mode"
fi

# Check file permissions
if [[ -w "." ]]; then
    echo "✅ Write permissions available"
else
    echo "❌ No write permissions in current directory"
fi

# Check for required tools
if command -v rg >/dev/null 2>&1; then
    echo "✅ ripgrep available"
else
    echo "⚠️ ripgrep not found - some features may be limited"
fi

# Set environment for automated execution
export CLAUDE_AUTOMATED_MODE=true
export CLAUDE_SKIP_CONFIRMATIONS=true

# Ensure quality patcher is ready
if [[ -f "scripts/claude_quality_patcher.py" ]]; then
    echo "✅ Quality patcher ready"
else
    echo "❌ Quality patcher not found"
    exit 1
fi

# Prepare latest lint report
echo "📊 Ensuring fresh lint data available"
if [[ -d "reports" ]]; then
    latest_report=$(ls -t reports/claude-lint-report-*.json 2>/dev/null | head -1)
    if [[ -n "$latest_report" ]]; then
        echo "✅ Latest report: $latest_report"
    fi
fi

echo "🚀 Pre-task hook complete - ready for automated execution"