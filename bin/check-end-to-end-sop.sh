#!/usr/bin/env bash

# 📋 END-TO-END SOP COMPLIANCE CHECKER
# Verifies compliance with project structure, patterns, and SOP requirements

PROJECT_DIR="${1:-$(pwd)}"

echo "📋 END-TO-END SOP COMPLIANCE CHECKER"
echo "📁 Project Directory: $PROJECT_DIR"
echo ""

cd "$PROJECT_DIR" || {
    echo "❌ Cannot access project directory: $PROJECT_DIR"
    exit 1
}

# Phase 1: File Structure Compliance
echo "🔍 PHASE 1: FILE STRUCTURE COMPLIANCE"
echo ""

# Check for essential project files
ESSENTIAL_FILES=(
    "package.json"
    "main.js"
    "src/"
    "public/"
)

STRUCTURE_VIOLATIONS=0

echo "✅ Checking essential project structure:"
for file in "${ESSENTIAL_FILES[@]}"; do
    if [[ -e "$file" ]]; then
        echo "   ✅ $file exists"
    else
        echo "   ❌ $file MISSING"
        STRUCTURE_VIOLATIONS=$((STRUCTURE_VIOLATIONS + 1))
    fi
done

# Phase 2: Pattern Compliance
echo ""
echo "🔍 PHASE 2: ESTABLISHED PATTERN COMPLIANCE"
echo ""

# Check for proper module loading order
echo "🔍 Checking module loading patterns:"

if [[ -f "main.js" ]]; then
    echo "   📄 Analyzing main.js module loading..."
    
    # Check for proper require/import order
    REQUIRES_COUNT=$(grep -c "require(" main.js 2>/dev/null || echo "0")
    IMPORTS_COUNT=$(grep -c "import.*from" main.js 2>/dev/null || echo "0")
    
    echo "   📊 Module loading stats:"
    echo "      • require() statements: $REQUIRES_COUNT"
    echo "      • import statements: $IMPORTS_COUNT"
    
    if [[ "$REQUIRES_COUNT" -gt 0 && "$IMPORTS_COUNT" -gt 0 ]]; then
        echo "   ⚠️  Mixed module loading detected (require + import)"
    fi
fi

# Phase 3: Security Pattern Compliance
echo ""
echo "🔍 PHASE 3: SECURITY PATTERN COMPLIANCE"
echo ""

# Check for execute_script violations (from CLAUDE.md history)
EXECUTE_SCRIPT_COUNT=$(find . -name "*.js" -not -path "*/node_modules/*" -exec grep -c "execute_script\|executeScript" {} \; | awk '{sum += $1} END {print sum}')

if [[ "$EXECUTE_SCRIPT_COUNT" -gt 0 ]]; then
    echo "   ❌ SECURITY VIOLATION: $EXECUTE_SCRIPT_COUNT execute_script usages found"
    echo "   🚨 CLAUDE.md history shows this causes security architecture destruction"
    echo "   📋 Must use ActionChains-only approach"
else
    echo "   ✅ No execute_script violations found"
fi

# Check for proper ActionChains usage
ACTIONCHAINS_COUNT=$(find . -name "*.js" -not -path "*/node_modules/*" -exec grep -c "ActionChains\|action_chain" {} \; | awk '{sum += $1} END {print sum}')

if [[ "$ACTIONCHAINS_COUNT" -gt 0 ]]; then
    echo "   ✅ ActionChains usage found: $ACTIONCHAINS_COUNT instances"
else
    echo "   ⚠️  No ActionChains usage detected"
fi

# Phase 4: Functionality Compliance
echo ""
echo "🔍 PHASE 4: FUNCTIONALITY COMPLIANCE"
echo ""

# Check for proper error handling
echo "🔍 Error handling patterns:"

ERROR_HANDLERS=$(find . -name "*.js" -not -path "*/node_modules/*" -exec grep -c "try\|catch\|process\.on.*error" {} \; | awk '{sum += $1} END {print sum}')
echo "   📊 Error handling blocks: $ERROR_HANDLERS"

# Check for proper IPC handlers
IPC_HANDLERS=$(find . -name "*.js" -not -path "*/node_modules/*" -exec grep -c "ipcMain\.handle\|ipcRenderer\.invoke" {} \; | awk '{sum += $1} END {print sum}')
echo "   📊 IPC handlers: $IPC_HANDLERS"

# Phase 5: Documentation Compliance
echo ""
echo "🔍 PHASE 5: DOCUMENTATION COMPLIANCE"
echo ""

# Check for CLAUDE.md compliance
if [[ -f "CLAUDE.md" ]]; then
    echo "   ✅ CLAUDE.md exists"
    
    # Check for critical sections
    if grep -q "EXTREME CODE QUALITY MANDATE" CLAUDE.md 2>/dev/null; then
        echo "   ✅ Contains code quality mandate"
    else
        echo "   ⚠️  Missing code quality mandate section"
    fi
else
    echo "   ⚠️  CLAUDE.md not found"
fi

# Phase 6: Generate Compliance Report
echo ""
echo "📋 END-TO-END SOP COMPLIANCE REPORT"
echo ""

TOTAL_VIOLATIONS=$((STRUCTURE_VIOLATIONS + (EXECUTE_SCRIPT_COUNT > 0 ? 1 : 0)))

echo "📊 COMPLIANCE METRICS:"
echo "   • File Structure Violations: $STRUCTURE_VIOLATIONS"
echo "   • Security Pattern Violations: $(( EXECUTE_SCRIPT_COUNT > 0 ? 1 : 0 ))"
echo "   • Error Handlers: $ERROR_HANDLERS"
echo "   • IPC Handlers: $IPC_HANDLERS"
echo "   • ActionChains Usage: $ACTIONCHAINS_COUNT"
echo ""

if [[ "$TOTAL_VIOLATIONS" -eq 0 ]]; then
    echo "✅ END-TO-END SOP COMPLIANCE ACHIEVED"
    echo "🎯 Project follows established patterns and security requirements"
else
    echo "❌ END-TO-END SOP VIOLATIONS DETECTED"
    echo ""
    echo "📋 REQUIRED AGENT ACTIONS:"
    
    if [[ "$STRUCTURE_VIOLATIONS" -gt 0 ]]; then
        echo "   1. 📁 Fix file structure violations"
        echo "      • Ensure essential files exist"
        echo "      • Follow established directory patterns"
    fi
    
    if [[ "$EXECUTE_SCRIPT_COUNT" -gt 0 ]]; then
        echo "   2. 🔒 Fix security pattern violations"
        echo "      • Replace execute_script with ActionChains"
        echo "      • Follow pointer-native architecture"
    fi
fi

echo ""
echo "📋 END-TO-END SOP CHECKLIST FOR AGENT:"
echo "   □ Essential files exist (package.json, main.js, src/, public/)"
echo "   □ Proper module loading patterns maintained"
echo "   □ No execute_script security violations"
echo "   □ ActionChains used for browser automation"
echo "   □ Proper error handling implemented"
echo "   □ IPC handlers follow established patterns"
echo "   □ Functionality verified after changes"
echo "   □ No regressions introduced"
echo ""
echo "🎯 Success criteria: 0 violations, all patterns maintained"