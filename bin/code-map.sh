#!/usr/bin/env bash

# CODE MAP TOOL - Comprehensive Function-Level Dependency Grapher
# Uses the codemap-tool from my-web-app project
# Version: 3.0 - Direct integration with codemap-tool

set -euo pipefail

# Configuration
PROJECT_ROOT="${CLAUDE_PROJECT_DIR:-$(pwd)}"
CODEMAP_TOOL_DIR="cross_platform.get_path("home") / my-web-app/codemap-tool"
OUTPUT_FILE="${PROJECT_ROOT}/CODEMAP-DEPENDENCY-GRAPH.svg"
TEMP_DIR="/tmp/codemap-$$"
LOG_FILE="${TEMP_DIR}/codemap.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Logging function
log() {
    if [[ -d "$(dirname "$LOG_FILE")" ]]; then
        echo -e "${BLUE}[CODEMAP]${NC} $1" | tee -a "$LOG_FILE"
    else
        echo -e "${BLUE}[CODEMAP]${NC} $1"
    fi
}

error() {
    if [[ -d "$(dirname "$LOG_FILE")" ]]; then
        echo -e "${RED}[CODEMAP ERROR]${NC} $1" | tee -a "$LOG_FILE" >&2
    else
        echo -e "${RED}[CODEMAP ERROR]${NC} $1" >&2
    fi
}

success() {
    if [[ -d "$(dirname "$LOG_FILE")" ]]; then
        echo -e "${GREEN}[CODEMAP SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
    else
        echo -e "${GREEN}[CODEMAP SUCCESS]${NC} $1"
    fi
}

warn() {
    if [[ -d "$(dirname "$LOG_FILE")" ]]; then
        echo -e "${YELLOW}[CODEMAP WARNING]${NC} $1" | tee -a "$LOG_FILE"
    else
        echo -e "${YELLOW}[CODEMAP WARNING]${NC} $1"
    fi
}

# Setup temporary directory
setup_temp() {
    mkdir -p "$TEMP_DIR"
    log "Created temp directory: $TEMP_DIR"
}

# Cleanup function
cleanup() {
    if [[ -d "$TEMP_DIR" ]]; then
        rm -rf "$TEMP_DIR"
        log "Cleaned up temp directory"
    fi
}
trap cleanup EXIT

# Analyze project structure and create comprehensive mapping
analyze_project() {
    log "Starting comprehensive project analysis..."
    
    # Find all relevant files
    find "$PROJECT_ROOT" -type f \( \
        -name "*.js" -o \
        -name "*.html" -o \
        -name "*.css" -o \
        -name "*.json" \
    \) -not -path "*/node_modules/*" \
      -not -path "*/.git/*" \
      -not -path "*/screenshots/*" \
      -not -path "*chrome-data*" \
      > "$TEMP_DIR/all_files.txt"
    
    local file_count=$(wc -l < "$TEMP_DIR/all_files.txt")
    log "Found $file_count files to analyze"
    
    # Create analysis report
    cat > "$TEMP_DIR/analysis_requirements.md" << 'EOF'
# MANDATORY CODEMAP REQUIREMENTS

## CRITICAL: AI MUST GENERATE COMPREHENSIVE SVG DEPENDENCY GRAPH

### REQUIRED ELEMENTS:
1. **ALL JavaScript functions with line numbers**
2. **ALL HTML elements with IDs and event handlers** 
3. **ALL CSS selectors and their relationships**
4. **ALL IPC handlers and their connections**
5. **ALL file dependencies (imports/requires)**
6. **COMPLETE end-to-end connection mapping**

### SVG STRUCTURE REQUIREMENTS:
- Width: 4000px minimum, Height: 3000px minimum
- Layered approach: HTML → Frontend JS → IPC Bridge → Backend JS → Services
- Color-coded by file type with gradients
- Arrow connections with relationship labels
- Function names with line numbers
- Missing/broken connections highlighted in RED
- Legend explaining all elements

### MANDATORY ANALYSIS DEPTH:
- Function-to-function call chains
- Event handler to backend service mapping  
- IPC communication paths
- Import/require dependency chains
- CSS class usage tracking
- HTML element interaction flows

### VALIDATION REQUIREMENTS:
- Zero unanswered function calls allowed
- All arrows must have source and target
- All relationships must be labeled
- Missing handlers identified and marked
- Complete end-to-end paths verified

### OUTPUT FORMAT:
- Valid XML/SVG with proper declarations
- Embedded CSS styles for interactivity
- Comprehensive legend and documentation
- Export to: CODEMAP-DEPENDENCY-GRAPH.svg
EOF

    log "Analysis requirements document created"
}

# Generate the SVG dependency graph
generate_svg() {
    log "Generating comprehensive SVG dependency graph..."
    
    # Get current project files with function extraction
    local js_files=""
    local html_files=""
    local css_files=""
    
    while IFS= read -r file; do
        case "$file" in
            *.js) js_files="${js_files}\n- $file" ;;
            *.html) html_files="${html_files}\n- $file" ;;
            *.css) css_files="${css_files}\n- $file" ;;
        esac
    done < "$TEMP_DIR/all_files.txt"
    
    # Create comprehensive SVG template
    cat > "$OUTPUT_FILE" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<svg width="4000" height="3000" viewBox="0 0 4000 3000" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <!-- Enhanced gradients for different node types -->
    <linearGradient id="htmlGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#4F46E5;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#7C3AED;stop-opacity:1" />
    </linearGradient>
    
    <linearGradient id="jsGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#F59E0B;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#D97706;stop-opacity:1" />
    </linearGradient>
    
    <linearGradient id="ipcGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#10B981;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#059669;stop-opacity:1" />
    </linearGradient>
    
    <linearGradient id="backendGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#DC2626;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#B91C1C;stop-opacity:1" />
    </linearGradient>
    
    <linearGradient id="criticalGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#EF4444;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#DC2626;stop-opacity:1" />
    </linearGradient>

    <!-- Enhanced arrow markers -->
    <marker id="arrowhead" markerWidth="12" markerHeight="8" refX="11" refY="4" orient="auto">
      <polygon points="0 0, 12 4, 0 8" fill="#374151" />
    </marker>
    
    <marker id="criticalArrow" markerWidth="12" markerHeight="8" refX="11" refY="4" orient="auto">
      <polygon points="0 0, 12 4, 0 8" fill="#DC2626" />
    </marker>
    
    <marker id="missingArrow" markerWidth="12" markerHeight="8" refX="11" refY="4" orient="auto">
      <polygon points="0 0, 12 4, 0 8" fill="#FF0000" stroke="#000" stroke-width="1" />
    </marker>
  </defs>

  <!-- Background with subtle pattern -->
  <rect width="4000" height="3000" fill="#F9FAFB"/>
  <pattern id="grid" width="50" height="50" patternUnits="userSpaceOnUse">
    <path d="M 50 0 L 0 0 0 50" fill="none" stroke="#E5E7EB" stroke-width="0.5"/>
  </pattern>
  <rect width="4000" height="3000" fill="url(#grid)" opacity="0.3"/>
  
  <!-- Enhanced Title Section -->
  <rect x="0" y="0" width="4000" height="100" fill="url(#backendGradient)"/>
  <text x="2000" y="35" text-anchor="middle" font-family="Arial, sans-serif" font-size="28" font-weight="bold" fill="white">
    CODEMAP: Comprehensive Function-Level Dependency Graph
  </text>
  <text x="2000" y="60" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" fill="#E5E7EB">
    Generated by AI-Enforced Analysis Tool - Complete End-to-End Mapping
  </text>
  <text x="2000" y="80" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" fill="#D1D5DB">
    Project: $(basename "$PROJECT_ROOT") | Files Analyzed: $(wc -l < "$TEMP_DIR/all_files.txt") | Generated: $(date)
  </text>

  <!-- Enhanced Legend with Critical Elements -->
  <g transform="translate(50, 120)">
    <rect x="-10" y="-10" width="350" height="200" fill="white" stroke="#374151" stroke-width="2" rx="8" opacity="0.95"/>
    <text x="0" y="10" font-family="Arial, sans-serif" font-size="18" font-weight="bold" fill="#111827">LEGEND - Mandatory Elements</text>
    
    <rect x="0" y="25" width="20" height="15" fill="url(#htmlGradient)" rx="2"/>
    <text x="25" y="37" font-family="Arial, sans-serif" font-size="12" fill="#374151">HTML Elements + Event Handlers</text>
    
    <circle cx="10" cy="55" r="8" fill="url(#jsGradient)"/>
    <text x="25" y="60" font-family="Arial, sans-serif" font-size="12" fill="#374151">JavaScript Functions (with line numbers)</text>
    
    <polygon points="0,75 20,82 0,89" fill="url(#ipcGradient)"/>
    <text x="25" y="83" font-family="Arial, sans-serif" font-size="12" fill="#374151">IPC Handlers + Bridges</text>
    
    <polygon points="0,100 15,94 15,106" fill="url(#backendGradient)"/>
    <text x="25" y="105" font-family="Arial, sans-serif" font-size="12" fill="#374151">Backend Services + Core Functions</text>
    
    <rect x="0" y="115" width="20" height="15" fill="url(#criticalGradient)" rx="2"/>
    <text x="25" y="127" font-family="Arial, sans-serif" font-size="12" fill="#374151">Critical/Missing Connections</text>
    
    <!-- Connection Types -->
    <line x1="0" y1="145" x2="20" y2="145" stroke="#374151" stroke-width="2" marker-end="url(#arrowhead)"/>
    <text x="25" y="149" font-family="Arial, sans-serif" font-size="12" fill="#374151">Function Call Connection</text>
    
    <line x1="0" y1="165" x2="20" y2="165" stroke="#DC2626" stroke-width="3" stroke-dasharray="5,5" marker-end="url(#missingArrow)"/>
    <text x="25" y="169" font-family="Arial, sans-serif" font-size="12" fill="#DC2626">MISSING/BROKEN Connection</text>
  </g>

  <!-- MANDATORY ANALYSIS SECTIONS -->
  
  <!-- LAYER 1: HTML FILES AND ELEMENTS -->
  <g transform="translate(100, 350)">
    <rect x="-20" y="-30" width="800" height="400" fill="rgba(79, 70, 229, 0.1)" stroke="url(#htmlGradient)" stroke-width="3" rx="10"/>
    <text x="0" y="-10" font-family="Arial, sans-serif" font-size="16" font-weight="bold" fill="#4F46E5">
      LAYER 1: HTML FILES + INTERACTIVE ELEMENTS
    </text>
    <text x="0" y="10" font-family="Arial, sans-serif" font-size="12" fill="#6B7280">
      All HTML files with clickable elements, forms, and event handlers
    </text>
  </g>

  <!-- LAYER 2: FRONTEND JAVASCRIPT -->
  <g transform="translate(1000, 350)">
    <rect x="-20" y="-30" width="800" height="400" fill="rgba(245, 158, 11, 0.1)" stroke="url(#jsGradient)" stroke-width="3" rx="10"/>
    <text x="0" y="-10" font-family="Arial, sans-serif" font-size="16" font-weight="bold" fill="#F59E0B">
      LAYER 2: FRONTEND JAVASCRIPT FUNCTIONS
    </text>
    <text x="0" y="10" font-family="Arial, sans-serif" font-size="12" fill="#6B7280">
      All frontend JS functions with line numbers and call chains
    </text>
  </g>

  <!-- LAYER 3: IPC BRIDGE -->  
  <g transform="translate(1900, 350)">
    <rect x="-20" y="-30" width="400" height="400" fill="rgba(16, 185, 129, 0.1)" stroke="url(#ipcGradient)" stroke-width="3" rx="10"/>
    <text x="0" y="-10" font-family="Arial, sans-serif" font-size="16" font-weight="bold" fill="#10B981">
      LAYER 3: IPC COMMUNICATION BRIDGE
    </text>
    <text x="0" y="10" font-family="Arial, sans-serif" font-size="12" fill="#6B7280">
      Preload.js + IPC handlers mapping
    </text>
  </g>

  <!-- LAYER 4: BACKEND SERVICES -->
  <g transform="translate(2400, 350)">
    <rect x="-20" y="-30" width="800" height="400" fill="rgba(220, 38, 38, 0.1)" stroke="url(#backendGradient)" stroke-width="3" rx="10"/>
    <text x="0" y="-10" font-family="Arial, sans-serif" font-size="16" font-weight="bold" fill="#DC2626">
      LAYER 4: BACKEND SERVICES + CORE FUNCTIONS
    </text>
    <text x="0" y="10" font-family="Arial, sans-serif" font-size="12" fill="#6B7280">
      All backend JS functions with dependencies
    </text>
  </g>

  <!-- CRITICAL REQUIREMENTS SECTION -->
  <g transform="translate(100, 800)">
    <rect x="-20" y="-20" width="3800" height="150" fill="rgba(239, 68, 68, 0.1)" stroke="#EF4444" stroke-width="3" rx="10"/>
    <text x="1900" y="0" text-anchor="middle" font-family="Arial, sans-serif" font-size="20" font-weight="bold" fill="#EF4444">
      🚨 CRITICAL ANALYSIS REQUIREMENTS - AI MUST COMPLETE 🚨
    </text>
    <text x="20" y="30" font-family="Arial, sans-serif" font-size="14" fill="#374151">
      1. MAP ALL FUNCTIONS: Every JavaScript function must be mapped with line numbers and connections
    </text>
    <text x="20" y="50" font-family="Arial, sans-serif" font-size="14" fill="#374151">
      2. TRACE ALL PATHS: Complete end-to-end paths from HTML elements to deepest backend functions
    </text>
    <text x="20" y="70" font-family="Arial, sans-serif" font-size="14" fill="#374151">
      3. IDENTIFY MISSING: All broken connections, missing handlers, and orphaned functions must be marked in RED
    </text>
    <text x="20" y="90" font-family="Arial, sans-serif" font-size="14" fill="#374151">
      4. VALIDATE COMPLETENESS: Zero unanswered function calls - every arrow must have valid source and target
    </text>
    <text x="20" y="110" font-family="Arial, sans-serif" font-size="14" fill="#374151">
      5. DOCUMENT RELATIONSHIPS: Every connection must be labeled with relationship type and data flow direction
    </text>
  </g>

  <!-- TEMPLATE NODES - AI MUST REPLACE WITH ACTUAL ANALYSIS -->
  <!-- HTML Elements Section -->
  <g transform="translate(120, 400)">
    <text x="0" y="0" font-family="Arial, sans-serif" font-size="12" font-weight="bold" fill="#4F46E5">
      🔍 AI MUST ANALYZE AND REPLACE THIS SECTION:
    </text>
    <text x="0" y="20" font-family="Arial, sans-serif" font-size="10" fill="#6B7280">
      - Extract ALL HTML elements with IDs from: $html_files
    </text>
    <text x="0" y="35" font-family="Arial, sans-serif" font-size="10" fill="#6B7280">
      - Map ALL onclick, addEventListener, form submissions
    </text>
    <text x="0" y="50" font-family="Arial, sans-serif" font-size="10" fill="#6B7280">
      - Create visual nodes for each interactive element
    </text>
    <text x="0" y="65" font-family="Arial, sans-serif" font-size="10" fill="#6B7280">
      - Connect to corresponding JavaScript functions
    </text>
  </g>

  <!-- JavaScript Functions Section -->
  <g transform="translate(1020, 400)">
    <text x="0" y="0" font-family="Arial, sans-serif" font-size="12" font-weight="bold" fill="#F59E0B">
      🔍 AI MUST ANALYZE AND REPLACE THIS SECTION:
    </text>
    <text x="0" y="20" font-family="Arial, sans-serif" font-size="10" fill="#6B7280">
      - Extract ALL functions from: $js_files
    </text>
    <text x="0" y="35" font-family="Arial, sans-serif" font-size="10" fill="#6B7280">
      - Include line numbers for each function
    </text>
    <text x="0" y="50" font-family="Arial, sans-serif" font-size="10" fill="#6B7280">
      - Map function-to-function call chains
    </text>
    <text x="0" y="65" font-family="Arial, sans-serif" font-size="10" fill="#6B7280">
      - Identify IPC calls and event emissions
    </text>
  </g>

  <!-- VALIDATION CHECKLIST -->
  <g transform="translate(100, 1000)">
    <rect x="-20" y="-20" width="3800" height="100" fill="rgba(34, 197, 94, 0.1)" stroke="#22C55E" stroke-width="2" rx="10"/>
    <text x="1900" y="0" text-anchor="middle" font-family="Arial, sans-serif" font-size="18" font-weight="bold" fill="#16A34A">
      ✅ MANDATORY COMPLETION CHECKLIST - VERIFY BEFORE DECLARING COMPLETE
    </text>
    <g transform="translate(50, 20)">
      <text x="0" y="0" font-family="Arial, sans-serif" font-size="12" fill="#374151">☐ All $(cat "$TEMP_DIR/all_files.txt" | grep "\.js$" | wc -l) JavaScript files analyzed</text>
      <text x="600" y="0" font-family="Arial, sans-serif" font-size="12" fill="#374151">☐ All $(cat "$TEMP_DIR/all_files.txt" | grep "\.html$" | wc -l) HTML files analyzed</text>
      <text x="1200" y="0" font-family="Arial, sans-serif" font-size="12" fill="#374151">☐ All IPC handlers mapped</text>
      <text x="1800" y="0" font-family="Arial, sans-serif" font-size="12" fill="#374151">☐ All missing connections identified</text>
    </g>
    <g transform="translate(50, 40)">
      <text x="0" y="0" font-family="Arial, sans-serif" font-size="12" fill="#374151">☐ Function line numbers included</text>
      <text x="600" y="0" font-family="Arial, sans-serif" font-size="12" fill="#374151">☐ End-to-end paths validated</text>
      <text x="1200" y="0" font-family="Arial, sans-serif" font-size="12" fill="#374151">☐ Connection arrows labeled</text>
      <text x="1800" y="0" font-family="Arial, sans-serif" font-size="12" fill="#374151">☐ Zero unanswered calls confirmed</text>
    </g>
  </g>

  <!-- FOOTER WITH GENERATION INFO -->
  <g transform="translate(100, 2900)">
    <rect x="-20" y="-20" width="3800" height="80" fill="#111827" rx="10"/>
    <text x="1900" y="10" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="bold" fill="white">
      CODEMAP Generation Status: TEMPLATE CREATED - AI ANALYSIS REQUIRED
    </text>
    <text x="1900" y="35" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" fill="#9CA3AF">
      This template must be replaced with comprehensive function-level analysis by AI
    </text>
    <text x="1900" y="55" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" fill="#6B7280">
      Generated: $(date) | Project: $(basename "$PROJECT_ROOT") | Tool Version: 2.0
    </text>
  </g>

</svg>
EOF

    success "Comprehensive SVG template created at: $OUTPUT_FILE"
    log "File size: $(du -h "$OUTPUT_FILE" | cut -f1)"
}

# Create analysis summary
create_summary() {
    cat > "$TEMP_DIR/codemap_summary.md" << EOF
# CODEMAP Tool Execution Summary

## Files Analyzed
- **Total Files**: $(wc -l < "$TEMP_DIR/all_files.txt")
- **JavaScript Files**: $(grep "\.js$" "$TEMP_DIR/all_files.txt" | wc -l)
- **HTML Files**: $(grep "\.html$" "$TEMP_DIR/all_files.txt" | wc -l)  
- **CSS Files**: $(grep "\.css$" "$TEMP_DIR/all_files.txt" | wc -l)
- **JSON Files**: $(grep "\.json$" "$TEMP_DIR/all_files.txt" | wc -l)

## Output Generated
- **SVG File**: $OUTPUT_FILE
- **Analysis Requirements**: $TEMP_DIR/analysis_requirements.md
- **File List**: $TEMP_DIR/all_files.txt

## Next Steps Required
1. **AI MUST ANALYZE**: The generated SVG is a template that REQUIRES comprehensive AI analysis
2. **FUNCTION MAPPING**: Every JavaScript function must be extracted and mapped with line numbers
3. **CONNECTION TRACING**: All function calls, event handlers, and IPC communications must be traced
4. **VALIDATION**: Every connection must be verified and missing handlers identified
5. **COMPLETION**: The template placeholders must be replaced with actual dependency graph

## Critical Requirements
- **Zero Unanswered Calls**: Every function call must have a valid target
- **Complete End-to-End Paths**: HTML → Frontend JS → IPC → Backend JS → Services
- **Line Number Precision**: Every function must include its line number location
- **Visual Clarity**: Color coding, arrows, and legends must be comprehensive
- **Broken Connection Identification**: Missing handlers must be highlighted in RED

Generated by CODEMAP Tool v2.0 at $(date)
EOF

    success "Analysis summary created"
    log "Summary location: $TEMP_DIR/codemap_summary.md"
}

# Main execution using codemap-tool
main() {
    log "Starting CODEMAP Tool - Using codemap-tool from my-web-app"
    log "Project Root: $PROJECT_ROOT"
    
    # Check if codemap-tool exists
    if [[ ! -d "$CODEMAP_TOOL_DIR" ]]; then
        error "Codemap-tool not found at: $CODEMAP_TOOL_DIR"
        error "Please ensure my-web-app project is properly set up"
        exit 1
    fi
    
    # Check if node is available
    if ! command -v node &> /dev/null; then
        error "Node.js is not installed or not in PATH"
        exit 1
    fi
    
    # Run the codemap-tool
    log "Executing codemap-tool..."
    cd "$CODEMAP_TOOL_DIR"
    
    # Install dependencies if needed
    if [[ ! -d "node_modules" ]]; then
        log "Installing codemap-tool dependencies..."
        npm install
    fi
    
    # Run codemap with function-level analysis
    log "Running function-level dependency analysis..."
    node bin/codemap.js \
        --path "$PROJECT_ROOT" \
        --format svg \
        --level function \
        --output "$OUTPUT_FILE" \
        --depth 5 \
        2>&1 | tee -a "$LOG_FILE"
    
    # Check if output was generated
    if [[ -f "$OUTPUT_FILE" ]]; then
        success "CODEMAP generation complete!"
        echo -e "\n${PURPLE}═══════════════════════════════════════${NC}"
        echo -e "${PURPLE}   CODEMAP TOOL EXECUTION COMPLETE     ${NC}"
        echo -e "${PURPLE}═══════════════════════════════════════${NC}"
        echo -e "${CYAN}Output File:${NC} $OUTPUT_FILE"
        echo -e "${CYAN}File Size:${NC} $(du -h "$OUTPUT_FILE" | cut -f1)"
        echo -e "${GREEN}Status:${NC} Function-level dependency graph generated"
        echo -e "${PURPLE}═══════════════════════════════════════${NC}\n"
        
        # Check for actionable reports
        if [[ -f "$CODEMAP_TOOL_DIR/tmp/actionable-report.md" ]]; then
            echo -e "${YELLOW}Actionable Report:${NC} $CODEMAP_TOOL_DIR/tmp/actionable-report.md"
            echo -e "${YELLOW}Agent Input:${NC} $CODEMAP_TOOL_DIR/tmp/agent-input.md"
        fi
    else
        error "Failed to generate codemap output"
        exit 1
    fi
}

# Execute main function
main "$@"