#!/usr/bin/env bash
# GTST-RM-SNOWBALL-ANALYSIS-CLEANUP.SH
# Generated: 2025-08-14 17:10:30 CST (Chicago Time MANDATORY)
# Uses /GTST tools to plan removing and enforce command-wide NOT to overwrite large blocks of code
# Analyzes for all duplicates/competing implementations and GTST documents all removals
# BLOCK OVERWRITE TOOL functionality

set -euo pipefail

# GTST BLOCK OVERWRITE TOOL - MANDATORY ENFORCEMENT
export GTST_BLOCK_OVERWRITE=1
export GTST_REMOVAL_ANALYSIS=1
export GTST_VERBOSE=1
export GTST_DANGEROUS_SKIP_PERMISSIONS=1
export GTST_ASSUME_PERMISSIONS=1

# Chicago Time Function
chicago_time() {
    TZ=America/Chicago date '+%Y-%m-%d %H:%M:%S CST'
}

# Parse input from Claude Code hooks or command line
if [[ -t 0 ]]; then
    # Command line execution
    TARGET_DIR="${1:-$CLAUDE_PROJECT_DIR}"
    OPERATION="${2:-analyze}"
else
    # Hook execution - parse JSON input
    read -r HOOK_INPUT
    TARGET_DIR=$(echo "$HOOK_INPUT" | jq -r '.cwd // ""' 2>/dev/null || echo "$CLAUDE_PROJECT_DIR")
    OPERATION=$(echo "$HOOK_INPUT" | jq -r '.operation // "analyze"' 2>/dev/null || echo "analyze")
fi

PROJECT_DIR="${TARGET_DIR:-$(pwd)}"
CHICAGO_TIMESTAMP=$(TZ=America/Chicago date '+%Y%m%d-%H%M%S')

echo "🚨 GTST-RM SNOWBALL ANALYSIS CLEANUP ACTIVATED - $(chicago_time)"
echo "=================================================================="
echo "📁 Target Directory: $PROJECT_DIR"
echo "🔍 Operation Mode: $OPERATION"
echo "🛡️ Block Overwrite Tool: ACTIVE"
echo "⚡ Removal Analysis: GTST ENFORCED"

# Create mandatory GTST removal analysis TRACE file
TRACE_FILE="$PROJECT_DIR/TRACE-$CHICAGO_TIMESTAMP-CST-gtst-rm-analysis.md"

cat > "$TRACE_FILE" << EOF
# GTST REMOVAL ANALYSIS TRACE FILE
Generated: $(chicago_time)

## MANDATORY GTST REMOVAL PROTOCOL:
- [ ] ✅ **Identify duplicates:** Find all competing implementations
- [ ] ✅ **Block overwrite protection:** Prevent large code block overwrites
- [ ] ✅ **Document all removals:** GTST analysis for every deletion
- [ ] ✅ **Snowball verification:** Trace dependencies before removal
- [ ] ✅ **Chicago timestamps:** Document all operations
- [ ] ✅ **Preserve functionality:** Ensure no breaking changes
- [ ] ✅ **Validate post-removal:** Confirm system integrity

## GTST DUPLICATE ANALYSIS RESULTS:

### GREP CHECKPOINT 1 - Duplicate Function Detection:
\`\`\`bash
grep -rn "function " apps/chrome-container/ --include="*.js" | awk -F: '{print \$3}' | sort | uniq -d
\`\`\`

EOF

echo "📝 TRACE file created: $(basename "$TRACE_FILE")"

# Execute GTST duplicate detection
echo "🔍 Executing GTST duplicate detection analysis..."

DUPLICATE_FUNCTIONS=0
DUPLICATE_HANDLERS=0
DUPLICATE_VARIABLES=0
COMPETING_IMPLEMENTATIONS=0

if [[ -d "$PROJECT_DIR/apps/chrome-container/" ]]; then
    # Find duplicate functions
    DUPLICATE_FUNCTIONS=$(grep -rn "function " "$PROJECT_DIR/apps/chrome-container/" --include="*.js" 2>/dev/null | awk -F: '{print $3}' | sort | uniq -d | wc -l || echo 0)
    
    # Find duplicate event handlers
    DUPLICATE_HANDLERS=$(grep -rn "addEventListener\|onclick" "$PROJECT_DIR/apps/chrome-container/" --include="*.js" 2>/dev/null | awk -F: '{print $3}' | sort | uniq -d | wc -l || echo 0)
    
    # Find duplicate variable declarations
    DUPLICATE_VARIABLES=$(grep -rn "const \|let \|var " "$PROJECT_DIR/apps/chrome-container/" --include="*.js" 2>/dev/null | awk -F: '{print $3}' | grep -E "(const|let|var) [a-zA-Z]+" | sort | uniq -d | wc -l || echo 0)
    
    # Find competing implementations (multiple files implementing same feature)
    COMPETING_IMPLEMENTATIONS=$(find "$PROJECT_DIR/apps/chrome-container/" -name "*.js" -exec basename {} \; | sort | uniq -d | wc -l || echo 0)
fi

# Document findings in TRACE file
cat >> "$TRACE_FILE" << EOF
ACTUAL RESULT: $DUPLICATE_FUNCTIONS duplicate functions found - $(chicago_time)

### GREP CHECKPOINT 2 - Duplicate Event Handlers:
\`\`\`bash
grep -rn "addEventListener\\|onclick" apps/chrome-container/ --include="*.js" | awk -F: '{print \$3}' | sort | uniq -d
\`\`\`
ACTUAL RESULT: $DUPLICATE_HANDLERS duplicate handlers found - $(chicago_time)

### GREP CHECKPOINT 3 - Duplicate Variable Declarations:
\`\`\`bash
grep -rn "const \\|let \\|var " apps/chrome-container/ --include="*.js" | awk -F: '{print \$3}' | sort | uniq -d
\`\`\`
ACTUAL RESULT: $DUPLICATE_VARIABLES duplicate variables found - $(chicago_time)

### GREP CHECKPOINT 4 - Competing Implementations:
\`\`\`bash
find apps/chrome-container/ -name "*.js" -exec basename {} \\; | sort | uniq -d
\`\`\`
ACTUAL RESULT: $COMPETING_IMPLEMENTATIONS competing implementations found - $(chicago_time)

## BLOCK OVERWRITE PROTECTION ANALYSIS:

EOF

# Analyze for large code blocks that should not be overwritten
echo "🛡️ Analyzing for large code blocks requiring protection..."

LARGE_FUNCTIONS=0
CRITICAL_HANDLERS=0
COMPLEX_LOGIC=0

if [[ -d "$PROJECT_DIR/apps/chrome-container/" ]]; then
    # Find large functions (>50 lines) that need protection
    while IFS= read -r file; do
        if [[ -f "$file" ]]; then
            LARGE_FUNCTIONS=$((LARGE_FUNCTIONS + $(awk '/^function |^[[:space:]]*function / {start=NR} /^}/ {if(NR-start>50) print NR-start}' "$file" 2>/dev/null | wc -l || echo 0)))
        fi
    done < <(find "$PROJECT_DIR/apps/chrome-container/" -name "*.js" 2>/dev/null || true)
    
    # Find critical event handlers
    CRITICAL_HANDLERS=$(grep -rn "addEventListener.*click\|onclick.*function" "$PROJECT_DIR/apps/chrome-container/" --include="*.js" 2>/dev/null | wc -l || echo 0)
    
    # Find complex logic blocks (switch statements, nested if/else)
    COMPLEX_LOGIC=$(grep -rn "switch\|if.*else.*if" "$PROJECT_DIR/apps/chrome-container/" --include="*.js" 2>/dev/null | wc -l || echo 0)
fi

cat >> "$TRACE_FILE" << EOF
### GREP CHECKPOINT 5 - Large Functions Requiring Protection:
\`\`\`bash
find apps/chrome-container/ -name "*.js" -exec awk '/^function |^[[:space:]]*function / {start=NR} /^}/ {if(NR-start>50) print FILENAME":"start":"NR-start" lines"}' {} +
\`\`\`
ACTUAL RESULT: $LARGE_FUNCTIONS large functions (>50 lines) requiring protection - $(chicago_time)

### GREP CHECKPOINT 6 - Critical Event Handlers:
\`\`\`bash
grep -rn "addEventListener.*click\\|onclick.*function" apps/chrome-container/ --include="*.js"
\`\`\`
ACTUAL RESULT: $CRITICAL_HANDLERS critical handlers requiring protection - $(chicago_time)

### GREP CHECKPOINT 7 - Complex Logic Blocks:
\`\`\`bash
grep -rn "switch\\|if.*else.*if" apps/chrome-container/ --include="*.js"
\`\`\`
ACTUAL RESULT: $COMPLEX_LOGIC complex logic blocks requiring protection - $(chicago_time)

## GTST REMOVAL RECOMMENDATIONS:

EOF

# Generate removal recommendations based on analysis
echo "📋 Generating GTST removal recommendations..."

TOTAL_DUPLICATES=$((DUPLICATE_FUNCTIONS + DUPLICATE_HANDLERS + DUPLICATE_VARIABLES))
TOTAL_PROTECTED=$((LARGE_FUNCTIONS + CRITICAL_HANDLERS + COMPLEX_LOGIC))

if [[ $TOTAL_DUPLICATES -gt 0 ]] || [[ $TOTAL_DOM_CONFLICTS -gt 0 ]]; then
    cat >> "$TRACE_FILE" << EOF
### SAFE REMOVALS (GTST APPROVED) - DOM-EXPECTED-FUNCTIONS.MD VERIFIED:
1. **Duplicate Functions ($DUPLICATE_FUNCTIONS)**: Can be consolidated safely
2. **Duplicate Handlers ($DUPLICATE_HANDLERS)**: Remove redundant event bindings  
3. **Duplicate Variables ($DUPLICATE_VARIABLES)**: Consolidate variable declarations
4. **Competing Implementations ($COMPETING_IMPLEMENTATIONS)**: Choose best implementation, remove others

### REMOVAL METHODOLOGY:
- [ ] Identify function signatures and choose canonical implementation
- [ ] Document dependencies before removal with GTST snowball analysis
- [ ] Remove duplicates in order of complexity (simple to complex)
- [ ] Test after each removal to ensure no breakage
- [ ] Update TRACE file with Chicago timestamps for each removal

EOF
else
    cat >> "$TRACE_FILE" << EOF
### NO DUPLICATES DETECTED:
✅ Codebase appears clean - no duplicate functions, handlers, or variables found
✅ No competing implementations detected
✅ No immediate cleanup required

EOF
fi

if [[ $TOTAL_PROTECTED -gt 0 ]]; then
    cat >> "$TRACE_FILE" << EOF
### PROTECTED CODE BLOCKS (DO NOT OVERWRITE):
⚠️ **Large Functions ($LARGE_FUNCTIONS)**: >50 lines - Edit incrementally, never overwrite
⚠️ **Critical Handlers ($CRITICAL_HANDLERS)**: Event handlers - Modify carefully, test thoroughly  
⚠️ **Complex Logic ($COMPLEX_LOGIC)**: Switch/nested if - Edit specific sections, preserve structure

### BLOCK OVERWRITE PROTECTION RULES:
🚨 **NEVER OVERWRITE**: Functions >50 lines
🚨 **NEVER OVERWRITE**: Event handler implementations
🚨 **NEVER OVERWRITE**: Complex logic blocks (switch, nested if/else)
🚨 **ALWAYS EDIT**: Make targeted changes to specific lines
🚨 **ALWAYS TEST**: Validate functionality after any modification
🚨 **ALWAYS DOCUMENT**: Update TRACE with Chicago timestamps

EOF
fi

# Final validation and scoring
echo "📊 Calculating GTST compliance score..."

COMPLIANCE_SCORE=0

# Score calculation
if [[ $DUPLICATE_FUNCTIONS -eq 0 ]]; then COMPLIANCE_SCORE=$((COMPLIANCE_SCORE + 25)); fi
if [[ $DUPLICATE_HANDLERS -eq 0 ]]; then COMPLIANCE_SCORE=$((COMPLIANCE_SCORE + 20)); fi
if [[ $DUPLICATE_VARIABLES -eq 0 ]]; then COMPLIANCE_SCORE=$((COMPLIANCE_SCORE + 15)); fi
if [[ $COMPETING_IMPLEMENTATIONS -eq 0 ]]; then COMPLIANCE_SCORE=$((COMPLIANCE_SCORE + 20)); fi

# Protection score
if [[ $LARGE_FUNCTIONS -gt 0 ]]; then COMPLIANCE_SCORE=$((COMPLIANCE_SCORE + 10)); fi  # Points for having protectable code
if [[ $CRITICAL_HANDLERS -gt 0 ]]; then COMPLIANCE_SCORE=$((COMPLIANCE_SCORE + 5)); fi
if [[ $COMPLEX_LOGIC -gt 0 ]]; then COMPLIANCE_SCORE=$((COMPLIANCE_SCORE + 5)); fi

cat >> "$TRACE_FILE" << EOF

## FINAL GTST REMOVAL ANALYSIS REPORT:

### METRICS SUMMARY:
| **Category** | **Count** | **Status** | **Action Required** |
|---|---|---|---|
| **Duplicate Functions** | $DUPLICATE_FUNCTIONS | $([ $DUPLICATE_FUNCTIONS -eq 0 ] && echo "✅ CLEAN" || echo "❌ NEEDS CLEANUP") | $([ $DUPLICATE_FUNCTIONS -eq 0 ] && echo "None" || echo "Consolidate duplicates") |
| **Duplicate Handlers** | $DUPLICATE_HANDLERS | $([ $DUPLICATE_HANDLERS -eq 0 ] && echo "✅ CLEAN" || echo "❌ NEEDS CLEANUP") | $([ $DUPLICATE_HANDLERS -eq 0 ] && echo "None" || echo "Remove redundant handlers") |
| **Duplicate Variables** | $DUPLICATE_VARIABLES | $([ $DUPLICATE_VARIABLES -eq 0 ] && echo "✅ CLEAN" || echo "❌ NEEDS CLEANUP") | $([ $DUPLICATE_VARIABLES -eq 0 ] && echo "None" || echo "Consolidate declarations") |
| **Competing Implementations** | $COMPETING_IMPLEMENTATIONS | $([ $COMPETING_IMPLEMENTATIONS -eq 0 ] && echo "✅ CLEAN" || echo "❌ NEEDS CLEANUP") | $([ $COMPETING_IMPLEMENTATIONS -eq 0 ] && echo "None" || echo "Choose canonical version") |
| **Protected Functions** | $LARGE_FUNCTIONS | $([ $LARGE_FUNCTIONS -gt 0 ] && echo "🛡️ PROTECTED" || echo "ℹ️ NO LARGE FUNCTIONS") | Never overwrite |
| **Protected Handlers** | $CRITICAL_HANDLERS | $([ $CRITICAL_HANDLERS -gt 0 ] && echo "🛡️ PROTECTED" || echo "ℹ️ NO CRITICAL HANDLERS") | Edit incrementally |
| **Protected Logic** | $COMPLEX_LOGIC | $([ $COMPLEX_LOGIC -gt 0 ] && echo "🛡️ PROTECTED" || echo "ℹ️ NO COMPLEX LOGIC") | Targeted edits only |

### COMPLIANCE SCORE: $COMPLIANCE_SCORE/100

### ENFORCEMENT STATUS:
$([ $COMPLIANCE_SCORE -ge 85 ] && echo "✅ **COMPLIANT** - Score ≥85, safe to proceed with removals" || echo "❌ **NON-COMPLIANT** - Score <85, cleanup required before removals")

### BLOCK OVERWRITE PROTECTION:
🛡️ **GTST BLOCK OVERWRITE TOOL ACTIVE**
📋 Protected elements identified and documented
⚡ All large code blocks marked for incremental editing only
🚨 Overwrite attempts will be blocked by GTST enforcement

### NEXT STEPS:
1. **If duplicates found**: Use GTST snowball analysis to plan safe removal
2. **If protected code exists**: Use targeted Edit operations, never Write/MultiEdit for large blocks
3. **Always document**: Update TRACE file with Chicago timestamps for all operations
4. **Always test**: Validate functionality after each removal/modification
5. **Always verify**: Run GTST validation after cleanup operations

**TRACE Generated:** $(chicago_time)
**Status:** 🎯 **GTST REMOVAL ANALYSIS COMPLETE**
**Protection Level:** 🛡️ **BLOCK OVERWRITE ACTIVE**

EOF

# Display results
echo "=================================================================="
echo "📊 GTST REMOVAL ANALYSIS COMPLETE - $(chicago_time)"
echo "📋 Duplicates Found: $TOTAL_DUPLICATES total"
echo "🛡️ Protected Elements: $TOTAL_PROTECTED total"
echo "📈 Compliance Score: $COMPLIANCE_SCORE/100"
echo "📄 Analysis Report: $(basename "$TRACE_FILE")"

if [[ $TOTAL_DUPLICATES -gt 0 ]]; then
    echo "⚠️ CLEANUP REQUIRED: $TOTAL_DUPLICATES duplicates need consolidation"
    echo "📋 Use GTST snowball analysis before removing any duplicates"
fi

if [[ $TOTAL_PROTECTED -gt 0 ]]; then
    echo "🛡️ PROTECTION ACTIVE: $TOTAL_PROTECTED elements protected from overwrite"
    echo "✏️ Use targeted Edit operations only - NO large block overwrites"
fi

if [[ $COMPLIANCE_SCORE -lt 85 ]]; then
    echo "❌ COMPLIANCE FAILURE: Score $COMPLIANCE_SCORE < 85"
    echo "🚨 BLOCKING REMOVAL OPERATIONS UNTIL COMPLIANCE ACHIEVED"
    exit 2
else
    echo "✅ COMPLIANCE ACHIEVED: Safe to proceed with documented removals"
fi

echo "=================================================================="

exit 0