#!/usr/bin/env bash

# 🔧 FIXMAPPEDCODE - Automated Code Resolution System
# Processes codemap reports and fixes unresolved calls while enforcing SOP compliance
# CRITICAL: Enforces prettier-lang SOP and end-to-end SOP compliance

set -e

PROJECT_DIR="${1:-$(pwd)}"
CODEMAP_TOOL_DIR="cross_platform.get_path("home") / my-web-app/codemap-tool"
REPORTS_DIR="$CODEMAP_TOOL_DIR/tmp"

echo "🔧 FIXMAPPEDCODE SYSTEM ACTIVATED"
echo "📁 Project Directory: $PROJECT_DIR"
echo "📊 Reports Directory: $REPORTS_DIR"
echo ""

# Check if codemap reports exist
if [[ ! -d "$REPORTS_DIR" ]]; then
    echo "❌ No codemap reports found. Run /codemap first."
    exit 1
fi

# Find latest actionable report
LATEST_REPORT=$(find "$REPORTS_DIR" -name "actionable-report-*.md" -o -name "actionable-report.md" | sort -r | head -1)

if [[ -z "$LATEST_REPORT" || ! -f "$LATEST_REPORT" ]]; then
    echo "❌ No actionable reports found. Generate codemap first with /codemap command."
    exit 1
fi

echo "📋 Processing report: $(basename "$LATEST_REPORT")"
echo ""

# CRITICAL: Enforce prettier-lang SOP before any code changes
echo "🚨 ENFORCING PRETTIER-LANG SOP (MANDATORY)"
"$HOME/.claude/scripts/enforce-prettier-lang-sop.sh" "$PROJECT_DIR"
echo ""

# Extract critical statistics from report
BROKEN_COUNT=$(grep "BROKEN/UNRESOLVED" "$LATEST_REPORT" | grep -o '[0-9]*' | head -1 || echo "0")
BROKEN_PERCENT=$(grep "Broken Percentage" "$LATEST_REPORT" | grep -o '[0-9.]*%' || echo "0%")

echo "🚨 CRITICAL METRICS FROM REPORT:"
echo "   • Broken/Unresolved Calls: $BROKEN_COUNT"
echo "   • Broken Percentage: $BROKEN_PERCENT"
echo ""

if [[ "$BROKEN_COUNT" -eq 0 ]]; then
    echo "✅ No unresolved calls found. Code is already clean."
    echo "🔍 Checking for duplicates and formatting compliance..."
    
    # Run duplicate detection
    "$HOME/.claude/scripts/detect-duplicates.sh" "$PROJECT_DIR"
else
    echo "🔧 FIXING UNRESOLVED CALLS - AGENT INTERVENTION REQUIRED"
    echo ""
    echo "📋 AGENT INSTRUCTIONS:"
    echo "   1. ✅ PRETTIER-LANG SOP COMPLIANCE (MANDATORY):"
    echo "      • Run 'npx prettier --check .' before ANY code changes"
    echo "      • Run 'npx prettier --write [modified-files]' after EVERY edit"
    echo "      • Run 'npx langextract --check' before string changes"
    echo "      • Run 'npx langextract --extract' after string modifications"
    echo ""
    echo "   2. 🚨 UNRESOLVED CALL RESOLUTION:"
    echo "      • Process each of the $BROKEN_COUNT unresolved calls"
    echo "      • Verify function definitions exist or create them"
    echo "      • Fix import/require statements for missing modules"
    echo "      • Remove false positives (Node.js built-ins)"
    echo ""
    echo "   3. 🗑️  DUPLICATE/PLACEHOLDER REMOVAL:"
    echo "      • Remove competing implementations"
    echo "      • Consolidate duplicate functions"
    echo "      • Remove placeholder/template code"
    echo "      • Remove unused imports and variables"
    echo ""
    echo "   4. 📋 END-TO-END SOP COMPLIANCE:"
    echo "      • Maintain existing file structure"
    echo "      • Follow established patterns"
    echo "      • Test functionality after changes"
    echo "      • Ensure no regressions"
fi

echo ""
echo "🎯 AGENT PROMPT GENERATED:"

# Find latest agent input file
LATEST_AGENT_INPUT=$(find "$REPORTS_DIR" -name "agent-input-*.md" -o -name "agent-input.md" | sort -r | head -1)

if [[ -f "$LATEST_AGENT_INPUT" ]]; then
    echo "📄 Agent prompt file: $(basename "$LATEST_AGENT_INPUT")"
    echo ""
    echo "🔍 TOP PRIORITY ISSUES FROM REPORT:"
    echo ""
    
    # Extract first few unresolved calls for immediate action
    grep -A 10 "BROKEN CALLS REQUIRING IMMEDIATE FIX" "$LATEST_REPORT" | head -20 || echo "   • Review full report for detailed breakdown"
    
    echo ""
    echo "📋 MANDATORY SOP ENFORCEMENT CHECKLIST:"
    echo "   □ Prettier formatting applied to ALL modified files"
    echo "   □ LangExtract applied to ALL string changes"
    echo "   □ Duplicates/placeholders removed"
    echo "   □ End-to-end functionality verified"
    echo "   □ No competing implementations remaining"
    echo ""
    echo "⚡ AGENT MUST NOW PROCESS THE GENERATED REPORTS AND FIX EACH UNRESOLVED CALL"
    echo "📈 Complete resolution of all $BROKEN_COUNT broken calls required"
    echo ""
    
    # Show directory structure for context
    echo "📁 PROJECT STRUCTURE CONTEXT:"
    if [[ -d "$PROJECT_DIR" ]]; then
        find "$PROJECT_DIR" -name "*.js" -o -name "*.html" -o -name "*.css" | grep -v node_modules | head -10
        echo "   ... (showing first 10 files)"
    fi
    
else
    echo "⚠️  No agent input file found"
fi

echo ""
echo "🚨 CRITICAL: Agent must fix ALL unresolved calls before claiming completion"
echo "📊 Progress tracking: Monitor broken call count reduction"
echo "✅ Success criteria: 0 broken calls, all duplicates removed, SOP compliant"
echo ""
echo ""
echo "📋 ENFORCING END-TO-END SOP COMPLIANCE"
"$HOME/.claude/scripts/check-end-to-end-sop.sh" "$PROJECT_DIR"

echo ""
echo "🔄 To re-run analysis after fixes: /codemap"
echo "🔧 To continue fixing: /fixmappedcode"