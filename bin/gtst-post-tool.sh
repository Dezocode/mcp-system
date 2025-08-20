#!/bin/bash
# GTST POST-TOOL VERIFICATION HOOK
# Generated: 2025-08-14 16:44:00 CST (Chicago Time MANDATORY)
# Validates changes after Write/Edit/MultiEdit operations

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

echo "📊 GTST POST-TOOL VALIDATION - $(chicago_time)"
echo "Tool: $TOOL_NAME | Project: $(basename "$PROJECT_DIR")"

# Find latest trace file
TRACE_FILE=$(ls -t "$PROJECT_DIR/TRACE-"*"-CST-"*".md" 2>/dev/null | head -1 || echo "")

if [[ -n "$TRACE_FILE" ]]; then
    echo "📄 Updating trace file: $(basename "$TRACE_FILE")"
    
    # Update trace file with post-tool validation
    echo "" >> "$TRACE_FILE"
    echo "## POST-TOOL VALIDATION - $(chicago_time)" >> "$TRACE_FILE"
    echo "**Tool Used:** $TOOL_NAME" >> "$TRACE_FILE"
    echo "" >> "$TRACE_FILE"
    
    # Verify changes didn't introduce violations
    if [[ -d "$PROJECT_DIR/apps/chrome-container/" ]]; then
        NEW_VIOLATIONS=$(grep -rn "TODO\|FIXME\|PLACEHOLDER" "$PROJECT_DIR/apps/chrome-container/" 2>/dev/null | wc -l || echo 0)
        echo "📋 **Post-change violations:** $NEW_VIOLATIONS" >> "$TRACE_FILE"
        
        if [[ $NEW_VIOLATIONS -gt 0 ]]; then
            echo "⚠️  WARNING: $NEW_VIOLATIONS new violations introduced"
            echo "📋 Violations added by $TOOL_NAME operation"
            echo "**⚠️  VIOLATION ALERT:** $NEW_VIOLATIONS placeholders introduced by $TOOL_NAME - $(chicago_time)" >> "$TRACE_FILE"
        else
            echo "✅ No new violations introduced"
            echo "**✅ Clean:** No placeholders introduced - $(chicago_time)" >> "$TRACE_FILE"
        fi
        
        # Check for new duplicate functions
        NEW_DUPLICATES=$(grep -rn "function " "$PROJECT_DIR/apps/chrome-container/" --include="*.js" 2>/dev/null | awk -F: '{print $3}' | sort | uniq -d | wc -l || echo 0)
        echo "📋 **Duplicate functions:** $NEW_DUPLICATES" >> "$TRACE_FILE"
        
        if [[ $NEW_DUPLICATES -gt 0 ]]; then
            echo "⚠️  WARNING: $NEW_DUPLICATES duplicate functions present"
            echo "**⚠️  DUPLICATE ALERT:** $NEW_DUPLICATES competing implementations - $(chicago_time)" >> "$TRACE_FILE"
        else
            echo "✅ No duplicate functions detected"
            echo "**✅ Clean:** No competing implementations - $(chicago_time)" >> "$TRACE_FILE"
        fi
    fi
    
    # Check if prettier/langextract compliance needed
    if echo "$TOOL_NAME" | grep -Eq "Write|Edit|MultiEdit"; then
        echo "" >> "$TRACE_FILE"
        echo "### PRETTIER & LANGEXTRACT COMPLIANCE CHECK" >> "$TRACE_FILE"
        
        # Check for hardcoded strings
        if [[ -d "$PROJECT_DIR/apps/chrome-container/" ]]; then
            HARDCODED_STRINGS=$(grep -rn "console\.log\s*(" "$PROJECT_DIR/apps/chrome-container/" --include="*.js" 2>/dev/null | grep -v "traceDebug\|i18n\.t" | wc -l || echo 0)
            echo "📋 **Hardcoded strings:** $HARDCODED_STRINGS" >> "$TRACE_FILE"
            
            if [[ $HARDCODED_STRINGS -gt 0 ]]; then
                echo "⚠️  WARNING: $HARDCODED_STRINGS hardcoded strings detected"
                echo "📋 Consider using i18n.t('key') for user-facing text"
                echo "**⚠️  I18N ALERT:** $HARDCODED_STRINGS hardcoded strings - $(chicago_time)" >> "$TRACE_FILE"
            else
                echo "✅ No hardcoded strings detected"
                echo "**✅ I18N Clean:** No hardcoded strings - $(chicago_time)" >> "$TRACE_FILE"
            fi
        fi
        
        # Note: Prettier formatting should be run separately
        echo "📋 **Note:** Run \`npx prettier --write [files]\` for formatting" >> "$TRACE_FILE"
    fi
    
    # Update final status
    echo "" >> "$TRACE_FILE"
    echo "**Status Update:** Tool validation complete - $(chicago_time)" >> "$TRACE_FILE"
    
    # Provide summary statistics
    TOTAL_GREP_RESULTS=$(grep -c "ACTUAL RESULT:" "$TRACE_FILE" 2>/dev/null || echo 0)
    TOTAL_CST_TIMESTAMPS=$(grep -c "CST" "$TRACE_FILE" 2>/dev/null || echo 0)
    
    echo "📊 Current trace statistics:"
    echo "   📋 Grep results: $TOTAL_GREP_RESULTS"
    echo "   ⏰ Chicago timestamps: $TOTAL_CST_TIMESTAMPS"
    echo "   📄 File size: $(wc -l < "$TRACE_FILE" 2>/dev/null || echo 0) lines"
    
else
    echo "⚠️  WARNING: No trace file found for post-tool validation"
    echo "📋 Consider running /gtst to create proper trace documentation"
fi

# Check for critical errors in modified files
if [[ -d "$PROJECT_DIR/apps/chrome-container/" ]]; then
    # Basic syntax validation for JS files (if node is available)
    if command -v node > /dev/null 2>&1; then
        JS_ERRORS=0
        for js_file in $(find "$PROJECT_DIR/apps/chrome-container/" -name "*.js" -type f 2>/dev/null | head -5); do
            if ! node -c "$js_file" > /dev/null 2>&1; then
                JS_ERRORS=$((JS_ERRORS + 1))
                echo "❌ Syntax error in: $(basename "$js_file")"
            fi
        done
        
        if [[ $JS_ERRORS -eq 0 ]]; then
            echo "✅ Basic syntax validation passed"
        else
            echo "⚠️  $JS_ERRORS files have syntax errors"
        fi
    fi
fi

echo "🎯 POST-TOOL VALIDATION COMPLETE"
echo ""

exit 0