#!/bin/bash
# GTST FINAL VALIDATION HOOK
# Generated: 2025-08-14 16:44:00 CST (Chicago Time MANDATORY)
# Comprehensive final validation on Stop event

set -euo pipefail

# Chicago Time Function
chicago_time() {
    TZ=America/Chicago date '+%Y-%m-%d %H:%M:%S CST'
}

# Parse JSON input from Claude Code
if [[ -t 0 ]]; then
    # Running in test mode
    PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"
else
    # Running from hook
    read -r HOOK_INPUT
    PROJECT_DIR=$(echo "$HOOK_INPUT" | jq -r '.cwd // ""' 2>/dev/null || echo "$(pwd)")
fi

echo ""
echo "🚨 GTST FINAL VALIDATION - $(chicago_time)"
echo "════════════════════════════════════════════"

# Find latest trace file
TRACE_FILE=$(ls -t "$PROJECT_DIR/TRACE-"*"-CST-"*".md" 2>/dev/null | head -1 || echo "")

if [[ -n "$TRACE_FILE" ]]; then
    echo "✅ Trace file: $(basename "$TRACE_FILE")"
    
    # Comprehensive validation metrics
    GREP_COUNT=$(grep -c "ACTUAL RESULT:" "$TRACE_FILE" 2>/dev/null || echo 0)
    CST_COUNT=$(grep -c "CST" "$TRACE_FILE" 2>/dev/null || echo 0)
    TEMPLATE_ELEMENTS=$(grep -c "Element Properties\|Snowball Action Chain\|File Dependencies" "$TRACE_FILE" 2>/dev/null || echo 0)
    WORD_COUNT=$(wc -w < "$TRACE_FILE" 2>/dev/null || echo 0)
    
    echo "📊 COMPREHENSIVE METRICS:"
    echo "   📋 Grep results: $GREP_COUNT (need ≥7)"
    echo "   ⏰ Chicago timestamps: $CST_COUNT (need ≥5)"
    echo "   📄 Template elements: $TEMPLATE_ELEMENTS (need ≥3)"
    echo "   📝 Word count: $WORD_COUNT (target ≥1000)"
    
    # Violation checks
    VIOLATION_COUNT=0
    DUPLICATE_COUNT=0
    EMPTY_FUNCTIONS=0
    
    if [[ -d "$PROJECT_DIR/apps/chrome-container/" ]]; then
        VIOLATION_COUNT=$(grep -rn "TODO\|FIXME\|PLACEHOLDER" "$PROJECT_DIR/apps/chrome-container/" 2>/dev/null | wc -l || echo 0)
        DUPLICATE_COUNT=$(grep -rn "function " "$PROJECT_DIR/apps/chrome-container/" --include="*.js" 2>/dev/null | awk -F: '{print $3}' | sort | uniq -d | wc -l || echo 0)
        EMPTY_FUNCTIONS=$(grep -rn "function.*\(\)\s*\{\s*\}" "$PROJECT_DIR/apps/chrome-container/" --include="*.js" 2>/dev/null | wc -l || echo 0)
    fi
    
    echo "🔍 CODE QUALITY METRICS:"
    echo "   🚫 Placeholder violations: $VIOLATION_COUNT (need 0)"
    echo "   🔄 Duplicate functions: $DUPLICATE_COUNT (need 0)" 
    echo "   📭 Empty functions: $EMPTY_FUNCTIONS (need 0)"
    
    # Architecture compliance
    ARCH_COMPLIANCE="Unknown"
    if [[ -f "$PROJECT_DIR/my-web-app-architecture.md" ]]; then
        ARCH_COMPLIANCE="Available"
    fi
    
    DOM_TEMPLATE="Unknown"
    if [[ -f "$PROJECT_DIR/DOM-EXPECTED-FUNCTIONS.md" ]]; then
        DOM_TEMPLATE="Available"
    fi
    
    echo "📐 ARCHITECTURE COMPLIANCE:"
    echo "   🏗️  Architecture rules: $ARCH_COMPLIANCE"
    echo "   📋 DOM template: $DOM_TEMPLATE"
    
    # Calculate compliance score
    SCORE=0
    MAX_SCORE=100
    
    # Grep verification (20 points)
    if [[ $GREP_COUNT -ge 7 ]]; then
        SCORE=$((SCORE + 20))
        echo "   ✅ Grep verification: PASS (+20)"
    else
        echo "   ❌ Grep verification: FAIL (need ≥7, got $GREP_COUNT)"
    fi
    
    # Chicago timestamps (15 points)
    if [[ $CST_COUNT -ge 5 ]]; then
        SCORE=$((SCORE + 15))
        echo "   ✅ Chicago timestamps: PASS (+15)"
    else
        echo "   ❌ Chicago timestamps: FAIL (need ≥5, got $CST_COUNT)"
    fi
    
    # Placeholder elimination (25 points)
    if [[ $VIOLATION_COUNT -eq 0 ]]; then
        SCORE=$((SCORE + 25))
        echo "   ✅ Placeholder elimination: PASS (+25)"
    else
        echo "   ❌ Placeholder elimination: FAIL ($VIOLATION_COUNT violations)"
    fi
    
    # Duplicate elimination (20 points)
    if [[ $DUPLICATE_COUNT -eq 0 ]]; then
        SCORE=$((SCORE + 20))
        echo "   ✅ Duplicate elimination: PASS (+20)"
    else
        echo "   ❌ Duplicate elimination: FAIL ($DUPLICATE_COUNT duplicates)"
    fi
    
    # Complete implementation (10 points)
    if [[ $EMPTY_FUNCTIONS -eq 0 ]]; then
        SCORE=$((SCORE + 10))
        echo "   ✅ Complete implementation: PASS (+10)"
    else
        echo "   ❌ Complete implementation: FAIL ($EMPTY_FUNCTIONS empty functions)"
    fi
    
    # Template compliance (10 points)
    if [[ $TEMPLATE_ELEMENTS -ge 3 ]]; then
        SCORE=$((SCORE + 10))
        echo "   ✅ Template compliance: PASS (+10)"
    else
        echo "   ❌ Template compliance: FAIL (need ≥3 elements, got $TEMPLATE_ELEMENTS)"
    fi
    
    echo ""
    echo "📊 FINAL GTST COMPLIANCE SCORE: $SCORE/$MAX_SCORE"
    
    # Add final validation to trace file
    echo "" >> "$TRACE_FILE"
    echo "## FINAL GTST VALIDATION - $(chicago_time)" >> "$TRACE_FILE"
    echo "**Compliance Score:** $SCORE/$MAX_SCORE" >> "$TRACE_FILE"
    echo "**Grep Results:** $GREP_COUNT (need ≥7)" >> "$TRACE_FILE"
    echo "**Chicago Timestamps:** $CST_COUNT (need ≥5)" >> "$TRACE_FILE"
    echo "**Violations:** $VIOLATION_COUNT (need 0)" >> "$TRACE_FILE"
    echo "**Duplicates:** $DUPLICATE_COUNT (need 0)" >> "$TRACE_FILE"
    echo "**Empty Functions:** $EMPTY_FUNCTIONS (need 0)" >> "$TRACE_FILE"
    echo "**Word Count:** $WORD_COUNT" >> "$TRACE_FILE"
    echo "" >> "$TRACE_FILE"
    
    # Final determination
    if [[ $SCORE -ge 85 ]] && [[ $VIOLATION_COUNT -eq 0 ]] && [[ $GREP_COUNT -ge 7 ]]; then
        echo "🎯 ✅ GTST COMPLIANCE: ALL REQUIREMENTS SATISFIED"
        echo "🚀 Ready for production deployment"
        echo "**STATUS:** ✅ APPROVED FOR DEPLOYMENT - $(chicago_time)" >> "$TRACE_FILE"
    elif [[ $SCORE -ge 70 ]] && [[ $VIOLATION_COUNT -eq 0 ]]; then
        echo "🎯 ⚠️  GTST COMPLIANCE: ACCEPTABLE WITH WARNINGS"
        echo "📋 Consider addressing remaining issues"
        echo "**STATUS:** ⚠️  CONDITIONALLY APPROVED - $(chicago_time)" >> "$TRACE_FILE"
    else
        echo "🚨 ❌ GTST VIOLATIONS: Requirements not met"
        echo "🛑 Must resolve all critical issues before approval"
        echo "**STATUS:** ❌ REQUIRES REMEDIATION - $(chicago_time)" >> "$TRACE_FILE"
    fi
    
else
    echo "❌ CRITICAL: No trace file found"
    echo "📋 REQUIRED: Create TRACE-YYYYMMDD-HHMMSS-CST-feature.md"
    echo "🎯 Run: /gtst to create proper documentation"
fi

# Performance and architecture recommendations
echo ""
echo "🎯 NEXT STEPS RECOMMENDATIONS:"

if [[ $VIOLATION_COUNT -gt 0 ]]; then
    echo "   1. 🚫 Eliminate $VIOLATION_COUNT placeholder violations"
    echo "      📋 Command: grep -rn 'TODO\|FIXME\|PLACEHOLDER' apps/chrome-container/"
fi

if [[ $DUPLICATE_COUNT -gt 0 ]]; then
    echo "   2. 🔄 Consolidate $DUPLICATE_COUNT duplicate functions"
    echo "      📋 Use ye-code-combiner agent for consolidation"
fi

if [[ $GREP_COUNT -lt 7 ]]; then
    echo "   3. 🔍 Add $((7 - GREP_COUNT)) more grep verification commands"
    echo "      📋 Document actual results with 'ACTUAL RESULT:' prefix"
fi

if [[ -n "$TRACE_FILE" ]]; then
    echo "   4. 📄 Trace file maintained at: $(basename "$TRACE_FILE")"
fi

echo "   5. 🔧 Run prettier and langextract for code quality"
echo "      📋 Commands: npx prettier --write [files]"

echo "════════════════════════════════════════════"
echo ""

exit 0