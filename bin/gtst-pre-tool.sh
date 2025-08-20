#!/bin/bash
# GTST PRE-TOOL VALIDATION HOOK
# Generated: 2025-08-14 16:44:00 CST (Chicago Time MANDATORY)
# Blocks Write/Edit/MultiEdit without proper GTST compliance

set -euo pipefail

# Chicago Time Function
chicago_time() {
    TZ=America/Chicago date '+%Y-%m-%d %H:%M:%S CST'
}

# Parse JSON input from Claude Code
if [[ -t 0 ]]; then
    # Running in test mode
    PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"
    TOOL_NAME="${1:-Write}"
else
    # Running from hook
    read -r HOOK_INPUT
    PROJECT_DIR=$(echo "$HOOK_INPUT" | jq -r '.cwd // ""' 2>/dev/null || echo "$(pwd)")
    TOOL_NAME=$(echo "$HOOK_INPUT" | jq -r '.tool_name // ""' 2>/dev/null || echo "Unknown")
fi

echo "🔍 GTST PRE-TOOL VALIDATION - $(chicago_time)"
echo "Tool: $TOOL_NAME | Project: $(basename "$PROJECT_DIR")"

# Check for TRACE file existence
TRACE_FILES=$(ls -t "$PROJECT_DIR/TRACE-"*"-CST-"*".md" 2>/dev/null | head -1 || echo "")

if [[ -z "$TRACE_FILES" ]]; then
    echo ""
    echo "🚨 GTST VIOLATION: No trace documentation found"
    echo "📋 REQUIRED: Create TRACE-YYYYMMDD-HHMMSS-CST-feature.md"
    echo "🔍 MUST contain 7+ grep command results with 'ACTUAL RESULT:'"
    echo "⏱️  MUST use Chicago timestamps (CST)"
    echo "📄 Template: Use DOM-EXPECTED-FUNCTIONS.md format"
    echo "❌ BLOCKING TOOL EXECUTION"
    echo ""
    exit 2
fi

TRACE_FILE="$TRACE_FILES"
echo "📄 Found trace file: $(basename "$TRACE_FILE")"

# Validate trace file content
GREP_COUNT=$(grep -c "ACTUAL RESULT:" "$TRACE_FILE" 2>/dev/null || echo 0)
CST_COUNT=$(grep -c "CST" "$TRACE_FILE" 2>/dev/null || echo 0)

echo "📊 Grep results documented: $GREP_COUNT (need ≥7)"
echo "⏰ Chicago timestamps: $CST_COUNT (need ≥3)"

if [[ $GREP_COUNT -lt 7 ]]; then
    echo ""
    echo "⚠️  WARNING: Insufficient grep verification"
    echo "📋 REQUIRED: Document at least 7 grep commands with results"
    echo "🔍 Add commands like:"
    echo "   grep -rn 'getElementById' apps/chrome-container/ --include='*.js'"
    echo "   ACTUAL RESULT: X references found - $(chicago_time)"
    echo ""
    # Warning but don't block
fi

if [[ $CST_COUNT -lt 3 ]]; then
    echo "⚠️  WARNING: Need more Chicago timestamps in trace file"
fi

# Check for placeholder violations
if [[ -d "$PROJECT_DIR/apps/chrome-container/" ]]; then
    VIOLATION_COUNT=$(grep -rn "TODO\|FIXME\|PLACEHOLDER" "$PROJECT_DIR/apps/chrome-container/" 2>/dev/null | wc -l || echo 0)
    
    if [[ $VIOLATION_COUNT -gt 0 ]]; then
        echo ""
        echo "🚨 PLACEHOLDER VIOLATIONS: $VIOLATION_COUNT found"
        echo "❌ BLOCKING: Must eliminate all placeholders before code changes"
        echo "📋 Run: grep -rn 'TODO\|FIXME\|PLACEHOLDER' apps/chrome-container/"
        echo "🔧 Replace with actual implementation"
        echo ""
        exit 2
    fi
    
    echo "✅ Placeholder check: No violations"
fi

# Check for duplicate functions
if [[ -d "$PROJECT_DIR/apps/chrome-container/" ]]; then
    DUPLICATE_COUNT=$(grep -rn "function " "$PROJECT_DIR/apps/chrome-container/" --include="*.js" 2>/dev/null | awk -F: '{print $3}' | sort | uniq -d | wc -l || echo 0)
    
    if [[ $DUPLICATE_COUNT -gt 0 ]]; then
        echo "⚠️  WARNING: $DUPLICATE_COUNT duplicate functions detected"
        echo "📋 Consider consolidating duplicate implementations"
    else
        echo "✅ Duplicate check: No competing functions"
    fi
fi

# Architecture compliance check
if [[ -f "$PROJECT_DIR/my-web-app-architecture.md" ]]; then
    echo "✅ Architecture rules: Available for reference"
else
    echo "⚠️  WARNING: my-web-app-architecture.md not found"
fi

echo "🎯 PRE-TOOL VALIDATION COMPLETE - Proceeding with $TOOL_NAME"
echo ""

exit 0