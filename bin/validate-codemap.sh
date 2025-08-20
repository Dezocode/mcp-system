#!/bin/bash

# CODEMAP Validation Script
# Ensures AI has completed comprehensive function-level analysis
# Version: 1.0

set -euo pipefail

PROJECT_ROOT="${CLAUDE_PROJECT_DIR:-$(pwd)}"
CODEMAP_FILE="${PROJECT_ROOT}/CODEMAP-DEPENDENCY-GRAPH.svg"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${BLUE}[CODEMAP-VALIDATOR]${NC} $1"
}

error() {
    echo -e "${RED}[VALIDATION ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[VALIDATION SUCCESS]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[VALIDATION WARNING]${NC} $1"
}

# Main validation function
validate_codemap() {
    log "Starting CODEMAP validation..."
    
    if [[ ! -f "$CODEMAP_FILE" ]]; then
        error "CODEMAP file not found: $CODEMAP_FILE"
        return 1
    fi
    
    log "Found CODEMAP file: $CODEMAP_FILE"
    
    # Check if it's still a template
    if grep -q "TEMPLATE CREATED - AI ANALYSIS REQUIRED" "$CODEMAP_FILE"; then
        error "CODEMAP is still a template - AI analysis not completed"
        warn "AI must replace template sections with actual function mapping"
        return 1
    fi
    
    # Validation checks
    local score=0
    local max_score=10
    
    # Check 1: Function line numbers present
    if grep -q "L:[0-9]" "$CODEMAP_FILE"; then
        success "✅ Function line numbers found"
        ((score++))
    else
        error "❌ Missing function line numbers"
    fi
    
    # Check 2: Multiple layers present
    if grep -q "LAYER [1-4]" "$CODEMAP_FILE"; then
        success "✅ Layer structure found"
        ((score++))
    else
        error "❌ Missing layer structure"
    fi
    
    # Check 3: Arrow connections present
    if grep -q "marker-end" "$CODEMAP_FILE"; then
        success "✅ Connection arrows found"
        ((score++))
    else
        error "❌ Missing connection arrows"
    fi
    
    # Check 4: JavaScript functions mapped
    if grep -c "function.*(" "$CODEMAP_FILE" > /dev/null; then
        success "✅ JavaScript functions mapped"
        ((score++))
    else
        error "❌ Missing JavaScript function mapping"
    fi
    
    # Check 5: HTML elements mapped
    if grep -q "onclick\\|addEventListener\\|button\\|form" "$CODEMAP_FILE"; then
        success "✅ HTML elements mapped"
        ((score++))
    else
        error "❌ Missing HTML element mapping"
    fi
    
    # Check 6: IPC handlers present
    if grep -q "ipcMain\\|ipcRenderer\\|electronAPI" "$CODEMAP_FILE"; then
        success "✅ IPC handlers mapped"
        ((score++))
    else
        error "❌ Missing IPC handler mapping"
    fi
    
    # Check 7: Backend services mapped
    if grep -q "src/\\|backend\\|service" "$CODEMAP_FILE"; then
        success "✅ Backend services mapped"
        ((score++))
    else
        error "❌ Missing backend service mapping"
    fi
    
    # Check 8: Missing connections identified
    if grep -q "MISSING\\|NO HANDLER\\|BROKEN" "$CODEMAP_FILE"; then
        success "✅ Missing connections identified"
        ((score++))
    else
        warn "⚠️ No missing connections identified - verify completeness"
    fi
    
    # Check 9: Color coding present
    if grep -q "fill.*url(#.*Gradient)" "$CODEMAP_FILE"; then
        success "✅ Color coding implemented"
        ((score++))
    else
        error "❌ Missing color coding"
    fi
    
    # Check 10: Comprehensive legend
    if grep -q "LEGEND" "$CODEMAP_FILE" && grep -q "Connection" "$CODEMAP_FILE"; then
        success "✅ Comprehensive legend found"
        ((score++))
    else
        error "❌ Missing or incomplete legend"
    fi
    
    # Calculate final score
    local percentage=$((score * 100 / max_score))
    
    echo ""
    log "VALIDATION COMPLETE"
    echo "Score: $score/$max_score ($percentage%)"
    
    if [[ $percentage -ge 90 ]]; then
        success "🎯 EXCELLENT: CODEMAP meets comprehensive analysis standards"
        return 0
    elif [[ $percentage -ge 70 ]]; then
        warn "⚠️ GOOD: CODEMAP mostly complete but needs improvement"
        return 0
    elif [[ $percentage -ge 50 ]]; then
        error "❌ POOR: CODEMAP needs significant improvement"
        return 1
    else
        error "❌ FAILED: CODEMAP is inadequate - comprehensive AI analysis required"
        return 1
    fi
}

# Run validation
validate_codemap "$@"