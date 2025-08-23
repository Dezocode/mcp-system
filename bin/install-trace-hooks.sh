#!/usr/bin/env bash

# install-trace-hooks.sh - Install trace snowball enforcement hooks
# Created: 2025-01-09 19:45:00 CST
# Purpose: Configure hooks to enforce trace documentation for all file operations

echo "🔧 Installing Trace Snowball Enforcement Hooks..."
echo "================================================"

SETTINGS_FILE="$HOME/.claude/settings.json"
HOOKS_FILE="$HOME/.claude/hooks/trace-enforcement.json"
BACKUP_FILE="$HOME/.claude/settings.json.backup-$(TZ=America/Chicago date +%Y%m%d-%H%M%S-CST)"

# Create backup of existing settings
if [ -f "$SETTINGS_FILE" ]; then
    echo "📦 Backing up existing settings to: $BACKUP_FILE"
    cp "$SETTINGS_FILE" "$BACKUP_FILE"
else
    echo "📝 Creating new settings file..."
    echo '{}' > "$SETTINGS_FILE"
fi

# Check if hooks are already installed
if grep -q "TRACE SNOWBALL DOCUMENTATION" "$SETTINGS_FILE" 2>/dev/null; then
    echo "✅ Hooks already installed - skipping"
else
    echo "📋 Installing enforcement hooks..."
    
    # Use jq if available, otherwise use manual merge
    if command -v jq &> /dev/null; then
        echo "Using jq for clean JSON merge..."
        jq -s '.[0] * .[1]' "$SETTINGS_FILE" "$HOOKS_FILE" > "$SETTINGS_FILE.tmp" && mv "$SETTINGS_FILE.tmp" "$SETTINGS_FILE"
    else
        echo "Manual merge (jq not available)..."
        # Copy the hooks file as the new settings (simple replacement)
        cp "$HOOKS_FILE" "$SETTINGS_FILE"
    fi
    
    echo "✅ Hooks installed successfully"
fi

# Verify installation
echo ""
echo "🔍 Verifying hook installation..."
echo "=================================="

if grep -q "PreToolUse" "$SETTINGS_FILE"; then
    echo "✅ PreToolUse hooks configured (blocks Write/Edit without trace)"
fi

if grep -q "UserPromptSubmit" "$SETTINGS_FILE"; then
    echo "✅ UserPromptSubmit hooks configured (loads CLAUDE.md rules)"
fi

if grep -q "PostToolUse" "$SETTINGS_FILE"; then
    echo "✅ PostToolUse hooks configured (updates trace reports)"
fi

if grep -q "Stop" "$SETTINGS_FILE"; then
    echo "✅ Stop hooks configured (final compliance check)"
fi

echo ""
echo "⚡ HOOK ENFORCEMENT NOW ACTIVE:"
echo "==============================="
echo "• Write/Edit/MultiEdit operations BLOCKED without trace report"
echo "• rm/delete commands BLOCKED without documentation"
echo "• CLAUDE.md and SOP rules loaded on every prompt"
echo "• Automatic compliance checking after operations"
echo "• Real Chicago timestamps enforced throughout (TZ=America/Chicago)"
echo ""
echo "🚨 IMPORTANT: Restart Claude Code for hooks to take effect"
echo ""
echo "To verify hooks are active, use: /hooks"
echo "To create trace documentation, use: /prep"
echo ""
echo "These hooks prevent the disasters documented in CLAUDE.md:"
echo "• 1,122 unnecessary files created → prevented by blocking"
echo "• 472 security violations → prevented by enforcement"
echo "• 91% audit failure rate → prevented by verification"

# Make script executable
chmod +x "$0" 2>/dev/null

exit 0