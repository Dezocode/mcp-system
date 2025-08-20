#!/bin/bash

# 🎨 PRETTIER-LANG SOP ENFORCEMENT SYSTEM
# CRITICAL: Enforces CLAUDE.md prettier and langextract requirements
# ZERO TOLERANCE for formatting violations or hardcoded strings

PROJECT_DIR="${1:-$(pwd)}"

echo "🎨 PRETTIER-LANG SOP ENFORCEMENT SYSTEM"
echo "📁 Target Directory: $PROJECT_DIR"
echo ""
echo "🚨 CRITICAL: This enforces CLAUDE.md EXTREME CODE QUALITY MANDATE"
echo "❌ VIOLATION = IMMEDIATE TASK TERMINATION"
echo ""

cd "$PROJECT_DIR" || {
    echo "❌ Cannot access project directory: $PROJECT_DIR"
    exit 1
}

# Phase 1: Pre-check Prettier Status
echo "🔍 PHASE 1: PRETTIER FORMAT VALIDATION"
echo ""

if command -v npx >/dev/null 2>&1; then
    echo "✅ npx available - checking prettier status"
    
    if npx prettier --check . 2>/dev/null; then
        echo "✅ All files are properly formatted"
        PRETTIER_STATUS="CLEAN"
    else
        echo "❌ FORMATTING VIOLATIONS DETECTED"
        echo ""
        echo "🚨 CRITICAL VIOLATION: Unformatted code found"
        echo "📋 Files requiring formatting:"
        npx prettier --check . 2>&1 | grep -E "\.(js|ts|jsx|tsx|css|html|json|md)$" | head -10
        echo ""
        PRETTIER_STATUS="VIOLATIONS"
    fi
else
    echo "⚠️  npx not available - skipping prettier check"
    PRETTIER_STATUS="UNAVAILABLE"
fi

# Phase 2: LangExtract String Validation
echo ""
echo "🔍 PHASE 2: LANGEXTRACT STRING VALIDATION"
echo ""

if command -v npx >/dev/null 2>&1; then
    echo "✅ Checking for hardcoded strings"
    
    # Check for hardcoded strings in JavaScript files
    HARDCODED_STRINGS=$(find . -name "*.js" -not -path "*/node_modules/*" -exec grep -l "console\.log\s*(\s*['\"]" {} \; 2>/dev/null | wc -l)
    HARDCODED_ERRORS=$(find . -name "*.js" -not -path "*/node_modules/*" -exec grep -l "console\.error\s*(\s*['\"]" {} \; 2>/dev/null | wc -l)
    HARDCODED_TITLES=$(find . -name "*.js" -not -path "*/node_modules/*" -exec grep -l "setTitle\s*(\s*['\"]" {} \; 2>/dev/null | wc -l)
    
    TOTAL_HARDCODED=$((HARDCODED_STRINGS + HARDCODED_ERRORS + HARDCODED_TITLES))
    
    if [[ "$TOTAL_HARDCODED" -gt 0 ]]; then
        echo "❌ LANGEXTRACT VIOLATIONS DETECTED"
        echo "📊 Hardcoded strings found: $TOTAL_HARDCODED files"
        echo ""
        echo "🚨 CRITICAL VIOLATION: Hardcoded strings must use i18n.t()"
        echo ""
        echo "📋 Files with hardcoded strings:"
        find . -name "*.js" -not -path "*/node_modules/*" -exec grep -l "console\.log\s*(\s*['\"]" {} \; 2>/dev/null | head -5
        echo ""
        echo "✅ Required format examples:"
        echo "   ❌ console.log('Error occurred');"
        echo "   ✅ console.log(i18n.t('errors.general'));"
        echo ""
        echo "   ❌ setTitle('My App');"
        echo "   ✅ setTitle(i18n.t('app.title'));"
        echo ""
        LANGEXTRACT_STATUS="VIOLATIONS"
    else
        echo "✅ No hardcoded strings detected"
        LANGEXTRACT_STATUS="CLEAN"
    fi
else
    echo "⚠️  npx not available - skipping langextract check"
    LANGEXTRACT_STATUS="UNAVAILABLE"
fi

# Phase 3: Generate Enforcement Report
echo ""
echo "🚨 PRETTIER-LANG SOP ENFORCEMENT REPORT"
echo ""

echo "📊 COMPLIANCE STATUS:"
echo "   • Prettier Formatting: $PRETTIER_STATUS"
echo "   • LangExtract Strings: $LANGEXTRACT_STATUS"
echo ""

# Determine overall compliance
OVERALL_STATUS="COMPLIANT"
VIOLATIONS_FOUND=0

if [[ "$PRETTIER_STATUS" == "VIOLATIONS" ]]; then
    OVERALL_STATUS="NON-COMPLIANT"
    VIOLATIONS_FOUND=$((VIOLATIONS_FOUND + 1))
fi

if [[ "$LANGEXTRACT_STATUS" == "VIOLATIONS" ]]; then
    OVERALL_STATUS="NON-COMPLIANT"
    VIOLATIONS_FOUND=$((VIOLATIONS_FOUND + 1))
fi

echo "🎯 OVERALL STATUS: $OVERALL_STATUS"
echo ""

if [[ "$OVERALL_STATUS" == "NON-COMPLIANT" ]]; then
    echo "❌ CRITICAL: SOP VIOLATIONS DETECTED ($VIOLATIONS_FOUND categories)"
    echo ""
    echo "📋 MANDATORY AGENT ACTIONS:"
    
    if [[ "$PRETTIER_STATUS" == "VIOLATIONS" ]]; then
        echo "   1. 🎨 PRETTIER FORMATTING (MANDATORY):"
        echo "      • Run: npx prettier --write ."
        echo "      • Verify: npx prettier --check ."
        echo "      • Status: MUST return 0 issues"
        echo ""
    fi
    
    if [[ "$LANGEXTRACT_STATUS" == "VIOLATIONS" ]]; then
        echo "   2. 🌐 LANGEXTRACT STRINGS (MANDATORY):"
        echo "      • Replace ALL hardcoded strings with i18n.t()"
        echo "      • Run: npx langextract --extract"
        echo "      • Verify: npx langextract --validate"
        echo "      • Status: MUST pass validation"
        echo ""
    fi
    
    echo "🚨 ENFORCEMENT PROTOCOL:"
    echo "   • VIOLATION = IMMEDIATE TASK TERMINATION"
    echo "   • NO EXCEPTIONS - NO MERCY"
    echo "   • ALL violations must be fixed before proceeding"
    echo ""
    echo "⚡ After fixes, re-run: /fixmappedcode to verify compliance"
    
else
    echo "✅ SOP COMPLIANCE ACHIEVED"
    echo "📋 All prettier and langextract requirements met"
    echo "🎯 Ready to proceed with code fixes"
fi

echo ""
echo "📋 ENFORCEMENT CHECKLIST FOR AGENT:"
echo "   □ npx prettier --write . (format all files)"
echo "   □ npx prettier --check . (verify 0 issues)"
echo "   □ Replace hardcoded strings with i18n.t()"
echo "   □ npx langextract --extract (update translations)"
echo "   □ npx langextract --validate (verify strings)"
echo ""
echo "🔥 REMEMBER: CLAUDE.md states these are ARCHITECTURAL VIOLATIONS"
echo "🔥 Unformatted code and hardcoded strings DESTROY maintainability"