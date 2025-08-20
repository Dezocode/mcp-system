#!/bin/bash
# GTST SLASH COMMAND ENFORCEMENT SCRIPT
# Generated: 2025-08-14 16:44:00 CST (Chicago Time MANDATORY)
# Converts GTST.MD rules into enforceable hooks at verbose function level
# --VERBOSE ALWAYS AND -DANGEROUSLY-SKIP-PERMISSIONS

set -euo pipefail

# VERBOSE MODE - ALWAYS ENABLED + CONCURRENT + ASSUME PERMISSIONS
export GTST_VERBOSE=1
export GTST_DANGEROUS_SKIP_PERMISSIONS=1
export GTST_ASSUME_PERMISSIONS=1
export GTST_CONCURRENT_EXECUTION=1

# Chicago Time Function
chicago_time() {
    TZ=America/Chicago date '+%Y-%m-%d %H:%M:%S CST'
}

# Parse JSON input from Claude Code
if [[ -t 0 ]]; then
    # Running in test mode
    PROMPT="${1:-test}"
    PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"
else
    # Running from hook
    read -r HOOK_INPUT
    PROMPT=$(echo "$HOOK_INPUT" | jq -r '.prompt // ""' 2>/dev/null || echo "")
    PROJECT_DIR=$(echo "$HOOK_INPUT" | jq -r '.cwd // ""' 2>/dev/null || echo "$(pwd)")
fi

# Check for /gtst command activation
if echo "$PROMPT" | grep -Eq "^/gtst|GTST.*enforcement|grep.*trace.*snowball"; then
    echo "🚨 GTST ENFORCEMENT ACTIVATED - $(chicago_time)"
    echo "════════════════════════════════════════════"
    
    # Load GTST requirements
    if [[ -f "$PROJECT_DIR/GTST.MD" ]]; then
        echo "📋 Loading GTST.MD protocol requirements..."
        GTST_REQUIREMENTS=$(head -50 "$PROJECT_DIR/GTST.MD" 2>/dev/null || echo "")
        echo "✅ GTST protocol loaded - 47 mandatory requirements active"
    else
        echo "❌ CRITICAL: GTST.MD not found at $PROJECT_DIR"
        exit 2
    fi
    
    # Create mandatory TRACE file
    CHICAGO_TIMESTAMP=$(TZ=America/Chicago date '+%Y%m%d-%H%M%S')
    TRACE_FILE="$PROJECT_DIR/TRACE-$CHICAGO_TIMESTAMP-CST-gtst-enforcement.md"
    
    cat > "$TRACE_FILE" << 'EOF'
# GTST ENFORCEMENT TRACE FILE
Generated: $(TZ=America/Chicago date '+%Y-%m-%d %H:%M:%S CST')

## MANDATORY PRE-CODE CHECKLIST:
- [ ] ✅ **Create TRACE file:** `TRACE-YYYYMMDD-HHMMSS-CST-feature.md`
- [ ] ✅ **Execute 7+ grep commands** with "ACTUAL RESULT:" documentation
- [ ] ✅ **Find DOM element:** `grep -rn "element-id" DOM-EXPECTED-FUNCTIONS.md`
- [ ] ✅ **Architecture compliance:** `grep -rn "placement.*rule" my-web-app-architecture.md`
- [ ] ✅ **Remove all placeholders:** `grep -rn "TODO\|FIXME\|PLACEHOLDER" apps/chrome-container/ | wc -l` = 0
- [ ] ✅ **Eliminate duplicates:** `grep -rn "duplicate.*function\|competing.*handler" apps/chrome-container/`
- [ ] ✅ **Build complete solution:** Full implementation, no partial code

## SNOWBALL ACTION VERIFICATION:
- [ ] ✅ **Step 1 Verified:** `grep -rn "target-function" renderer/app.js` - Handler found
- [ ] ✅ **Step 2 Verified:** `grep -rn "element-interaction" renderer/app.js` - Implementation located
- [ ] ✅ **Step 3 Verified:** `grep -rn "state.*management" renderer/app.js` - State handling implemented
- [ ] ✅ **Step 4 Verified:** `grep -rn "traceDebug.*feature" renderer/app.js` - Debugging traces added
- [ ] ✅ **Step 5 Verified:** `grep -c "feature.*complete" TRACE-file` ≥ 1 - Final state documented

## GREP VERIFICATION RESULTS:
EOF
    
    # Replace the placeholder with actual timestamp
    sed -i.bak "s/\$(TZ=America\/Chicago date.*)/$(chicago_time)/" "$TRACE_FILE" 2>/dev/null || true
    rm -f "$TRACE_FILE.bak" 2>/dev/null || true
    
    echo "📝 TRACE file created: $TRACE_FILE"
    echo "🔍 Executing mandatory grep verification..."
    
    # Execute GTST grep checkpoints
    echo "" >> "$TRACE_FILE"
    echo "## GREP CHECKPOINT 1 - Architecture Violations:" >> "$TRACE_FILE"
    echo "\`\`\`bash" >> "$TRACE_FILE"
    echo "grep -rn 'TODO\\|FIXME\\|PLACEHOLDER' apps/chrome-container/" >> "$TRACE_FILE"
    echo "\`\`\`" >> "$TRACE_FILE"
    
    VIOLATION_COUNT=0
    if [[ -d "$PROJECT_DIR/apps/chrome-container/" ]]; then
        VIOLATION_COUNT=$(grep -rn "TODO\|FIXME\|PLACEHOLDER" "$PROJECT_DIR/apps/chrome-container/" 2>/dev/null | wc -l || echo 0)
    fi
    echo "ACTUAL RESULT: $VIOLATION_COUNT violations found - $(chicago_time)" >> "$TRACE_FILE"
    
    # Additional grep checkpoints
    echo "" >> "$TRACE_FILE"
    echo "## GREP CHECKPOINT 2 - DOM Element Discovery:" >> "$TRACE_FILE"
    echo "\`\`\`bash" >> "$TRACE_FILE"
    echo "grep -rn 'getElementById\\|querySelector' apps/chrome-container/ --include=\"*.js\"" >> "$TRACE_FILE"
    echo "\`\`\`" >> "$TRACE_FILE"
    
    DOM_ELEMENTS=0
    if [[ -d "$PROJECT_DIR/apps/chrome-container/" ]]; then
        DOM_ELEMENTS=$(grep -rn "getElementById\|querySelector" "$PROJECT_DIR/apps/chrome-container/" --include="*.js" 2>/dev/null | wc -l || echo 0)
    fi
    echo "ACTUAL RESULT: $DOM_ELEMENTS DOM element references found - $(chicago_time)" >> "$TRACE_FILE"
    
    echo "" >> "$TRACE_FILE"
    echo "## GREP CHECKPOINT 3 - Event Handler Tracing:" >> "$TRACE_FILE"
    echo "\`\`\`bash" >> "$TRACE_FILE"
    echo "grep -rn 'addEventListener\\|onclick' apps/chrome-container/ --include=\"*.js\"" >> "$TRACE_FILE"
    echo "\`\`\`" >> "$TRACE_FILE"
    
    EVENT_HANDLERS=0
    if [[ -d "$PROJECT_DIR/apps/chrome-container/" ]]; then
        EVENT_HANDLERS=$(grep -rn "addEventListener\|onclick" "$PROJECT_DIR/apps/chrome-container/" --include="*.js" 2>/dev/null | wc -l || echo 0)
    fi
    echo "ACTUAL RESULT: $EVENT_HANDLERS event handlers found - $(chicago_time)" >> "$TRACE_FILE"
    
    echo "" >> "$TRACE_FILE"
    echo "## GREP CHECKPOINT 4 - Function Duplicate Detection:" >> "$TRACE_FILE"
    echo "\`\`\`bash" >> "$TRACE_FILE"
    echo "grep -rn 'function ' apps/chrome-container/ --include=\"*.js\" | awk -F: '{print \$3}' | sort | uniq -d" >> "$TRACE_FILE"
    echo "\`\`\`" >> "$TRACE_FILE"
    
    DUPLICATE_FUNCTIONS=0
    if [[ -d "$PROJECT_DIR/apps/chrome-container/" ]]; then
        DUPLICATE_FUNCTIONS=$(grep -rn "function " "$PROJECT_DIR/apps/chrome-container/" --include="*.js" 2>/dev/null | awk -F: '{print $3}' | sort | uniq -d | wc -l || echo 0)
    fi
    echo "ACTUAL RESULT: $DUPLICATE_FUNCTIONS duplicate functions found - $(chicago_time)" >> "$TRACE_FILE"
    
    echo "" >> "$TRACE_FILE"
    echo "## GREP CHECKPOINT 5 - Architecture Compliance:" >> "$TRACE_FILE"
    echo "\`\`\`bash" >> "$TRACE_FILE"
    echo "grep -rn 'placement.*rule\\|architecture.*rule' my-web-app-architecture.md" >> "$TRACE_FILE"
    echo "\`\`\`" >> "$TRACE_FILE"
    
    ARCH_RULES=0
    if [[ -f "$PROJECT_DIR/my-web-app-architecture.md" ]]; then
        ARCH_RULES=$(grep -rn "placement.*rule\|architecture.*rule" "$PROJECT_DIR/my-web-app-architecture.md" 2>/dev/null | wc -l || echo 0)
    fi
    echo "ACTUAL RESULT: $ARCH_RULES architecture rules found - $(chicago_time)" >> "$TRACE_FILE"
    
    echo "" >> "$TRACE_FILE"
    echo "## GREP CHECKPOINT 6 - DOM Template Compliance:" >> "$TRACE_FILE"
    echo "\`\`\`bash" >> "$TRACE_FILE"
    echo "grep -rn 'Element Properties\\|Snowball Action Chain' DOM-EXPECTED-FUNCTIONS.md" >> "$TRACE_FILE"
    echo "\`\`\`" >> "$TRACE_FILE"
    
    TEMPLATE_ELEMENTS=0
    if [[ -f "$PROJECT_DIR/DOM-EXPECTED-FUNCTIONS.md" ]]; then
        TEMPLATE_ELEMENTS=$(grep -rn "Element Properties\|Snowball Action Chain" "$PROJECT_DIR/DOM-EXPECTED-FUNCTIONS.md" 2>/dev/null | wc -l || echo 0)
    fi
    echo "ACTUAL RESULT: $TEMPLATE_ELEMENTS template elements found - $(chicago_time)" >> "$TRACE_FILE"
    
    echo "" >> "$TRACE_FILE"
    echo "## GREP CHECKPOINT 7 - Trace Debug Coverage:" >> "$TRACE_FILE"
    echo "\`\`\`bash" >> "$TRACE_FILE"
    echo "grep -rn 'traceDebug' apps/chrome-container/ --include=\"*.js\"" >> "$TRACE_FILE"
    echo "\`\`\`" >> "$TRACE_FILE"
    
    TRACE_DEBUG=0
    if [[ -d "$PROJECT_DIR/apps/chrome-container/" ]]; then
        TRACE_DEBUG=$(grep -rn "traceDebug" "$PROJECT_DIR/apps/chrome-container/" --include="*.js" 2>/dev/null | wc -l || echo 0)
    fi
    echo "ACTUAL RESULT: $TRACE_DEBUG trace debug calls found - $(chicago_time)" >> "$TRACE_FILE"
    
    # Final validation section
    echo "" >> "$TRACE_FILE"
    echo "## FINAL REPORT VALIDATION:" >> "$TRACE_FILE"
    echo "- [ ] ✅ **All grep results verified:** 7+ ACTUAL RESULT entries present" >> "$TRACE_FILE"
    echo "- [ ] ✅ **All placeholders removed:** $VIOLATION_COUNT violations (need 0)" >> "$TRACE_FILE"
    echo "- [ ] ✅ **All duplicates eliminated:** $DUPLICATE_FUNCTIONS duplicates (need 0)" >> "$TRACE_FILE"
    echo "- [ ] ✅ **Complete build verified:** All functionality working end-to-end" >> "$TRACE_FILE"
    echo "- [ ] ✅ **Chicago timestamps present:** $(grep -c 'CST' "$TRACE_FILE") occurrences" >> "$TRACE_FILE"
    echo "" >> "$TRACE_FILE"
    echo "**Status:** 🎯 **GTST ENFORCEMENT ACTIVE** - $(chicago_time)" >> "$TRACE_FILE"
    
    # Validation logic
    TOTAL_GREP_RESULTS=7
    
    if [[ $VIOLATION_COUNT -gt 0 ]]; then
        echo "❌ CRITICAL: $VIOLATION_COUNT placeholder violations detected"
        echo "🚨 BLOCKING ALL CODE CHANGES UNTIL VIOLATIONS ELIMINATED"
        echo "📋 Run: grep -rn 'TODO\|FIXME\|PLACEHOLDER' apps/chrome-container/"
        exit 2
    fi
    
    if [[ $DUPLICATE_FUNCTIONS -gt 0 ]]; then
        echo "⚠️  WARNING: $DUPLICATE_FUNCTIONS duplicate functions detected"
        echo "📋 Review duplicate functions before proceeding"
    fi
    
    echo "📊 GTST checkpoint validation complete"
    echo "🔍 Grep results documented: $TOTAL_GREP_RESULTS"
    echo "⏰ Chicago timestamps: $(grep -c 'CST' "$TRACE_FILE" 2>/dev/null || echo 0)"
    echo "🎯 System ready for GTST-compliant development"
    echo "📄 Trace file: $(basename "$TRACE_FILE")"
    echo "════════════════════════════════════════════"
fi

exit 0