#!/usr/bin/env bash
# GTST REAL TIMESTAMPING TOOL
# Generated: 2025-08-14 16:44:00 CST (Chicago Time MANDATORY)
# Enforces Chicago timestamps on ALL documents in ALL processes
# --VERBOSE ALWAYS AND -DANGEROUSLY-SKIP-PERMISSIONS

set -euo pipefail

# VERBOSE MODE - ALWAYS ENABLED
export GTST_VERBOSE=1
export GTST_DANGEROUS_SKIP_PERMISSIONS=1

# Real Chicago Time Function with Multiple Formats
chicago_time() {
    TZ=America/Chicago date '+%Y-%m-%d %H:%M:%S CST'
}

chicago_time_filename() {
    TZ=America/Chicago date '+%Y%m%d-%H%M%S'
}

chicago_time_iso() {
    TZ=America/Chicago date '+%Y-%m-%dT%H:%M:%S-06:00'
}

chicago_time_trace() {
    TZ=America/Chicago date '+[%H:%M:%S CST]'
}

# Verbose logging function
verbose_log() {
    if [[ "${GTST_VERBOSE:-1}" == "1" ]]; then
        echo "🔍 GTST-TIMESTAMPING: $1 - $(chicago_time)" >&2
    fi
}

# Main timestamping enforcement function
enforce_timestamps() {
    local target_dir="${1:-$(pwd)}"
    local operation="${2:-add}"
    
    verbose_log "Starting timestamp enforcement on $target_dir"
    verbose_log "Operation mode: $operation"
    verbose_log "Dangerous skip permissions: ${GTST_DANGEROUS_SKIP_PERMISSIONS:-0}"
    
    case "$operation" in
        "add"|"enforce")
            add_timestamps_to_documents "$target_dir"
            ;;
        "verify")
            verify_timestamps_in_documents "$target_dir"
            ;;
        "fix")
            fix_missing_timestamps "$target_dir"
            ;;
        "report")
            generate_timestamp_report "$target_dir"
            ;;
        *)
            echo "🚨 GTST TIMESTAMPING USAGE:"
            echo "  $0 [directory] [add|verify|fix|report]"
            echo "  Default: add timestamps to all documents"
            exit 1
            ;;
    esac
}

# Add timestamps to all documents
add_timestamps_to_documents() {
    local target_dir="$1"
    local timestamp=$(chicago_time)
    local count=0
    
    verbose_log "Adding timestamps to documents in $target_dir"
    
    # Find all markdown and text documents
    while IFS= read -r -d '' file; do
        if [[ -f "$file" ]] && [[ "${GTST_DANGEROUS_SKIP_PERMISSIONS:-0}" == "1" || -w "$file" ]]; then
            verbose_log "Processing: $(basename "$file")"
            
            # Check if file already has Chicago timestamp
            if ! grep -q "CST\|Chicago Time" "$file" 2>/dev/null; then
                # Add timestamp header
                local temp_file=$(mktemp)
                {
                    echo "# GTST TIMESTAMPED DOCUMENT"
                    echo "Generated: $timestamp"
                    echo "Chicago Time: MANDATORY"
                    echo ""
                    cat "$file"
                } > "$temp_file"
                
                if [[ "${GTST_DANGEROUS_SKIP_PERMISSIONS:-0}" == "1" ]]; then
                    chmod 666 "$file" 2>/dev/null || true
                fi
                
                mv "$temp_file" "$file"
                count=$((count + 1))
                verbose_log "✅ Added timestamp to $(basename "$file")"
            else
                verbose_log "⚠️  $(basename "$file") already has Chicago timestamp"
            fi
        else
            verbose_log "❌ Cannot write to $(basename "$file") - permissions denied"
        fi
    done < <(find "$target_dir" -type f \( -name "*.md" -o -name "*.txt" -o -name "*.log" \) -print0 2>/dev/null)
    
    echo "📊 TIMESTAMP ENFORCEMENT COMPLETE: $count files processed"
}

# Verify timestamps in documents
verify_timestamps_in_documents() {
    local target_dir="$1"
    local with_cst=0
    local without_cst=0
    local total=0
    
    verbose_log "Verifying timestamps in $target_dir"
    
    while IFS= read -r -d '' file; do
        if [[ -f "$file" ]]; then
            total=$((total + 1))
            if grep -q "CST\|Chicago Time" "$file" 2>/dev/null; then
                with_cst=$((with_cst + 1))
                verbose_log "✅ $(basename "$file") has Chicago timestamp"
            else
                without_cst=$((without_cst + 1))
                verbose_log "❌ $(basename "$file") missing Chicago timestamp"
            fi
        fi
    done < <(find "$target_dir" -type f \( -name "*.md" -o -name "*.txt" -o -name "*.log" \) -print0 2>/dev/null)
    
    echo "📊 TIMESTAMP VERIFICATION REPORT:"
    echo "   📋 Total documents: $total"
    echo "   ✅ With Chicago timestamps: $with_cst"
    echo "   ❌ Missing timestamps: $without_cst"
    echo "   📊 Compliance rate: $(( with_cst * 100 / total ))%"
}

# Fix missing timestamps
fix_missing_timestamps() {
    local target_dir="$1"
    
    verbose_log "Fixing missing timestamps in $target_dir"
    
    # First verify to get current state
    verify_timestamps_in_documents "$target_dir"
    
    # Then add timestamps where missing
    add_timestamps_to_documents "$target_dir"
    
    echo "🔧 TIMESTAMP FIX COMPLETE"
}

# Generate comprehensive timestamp report
generate_timestamp_report() {
    local target_dir="$1"
    local report_file="$target_dir/GTST-TIMESTAMP-REPORT-$(chicago_time_filename)-CST.md"
    
    verbose_log "Generating timestamp report: $report_file"
    
    cat > "$report_file" << EOF
# GTST TIMESTAMP COMPLIANCE REPORT
Generated: $(chicago_time)

## SCAN SUMMARY
Target Directory: $target_dir
Scan Time: $(chicago_time)
Enforcement Mode: ${GTST_DANGEROUS_SKIP_PERMISSIONS:-0}

## DOCUMENT ANALYSIS
EOF
    
    local total=0
    local compliant=0
    
    while IFS= read -r -d '' file; do
        if [[ -f "$file" ]]; then
            total=$((total + 1))
            local relative_path="${file#$target_dir/}"
            local status="❌ MISSING"
            
            if grep -q "CST\|Chicago Time" "$file" 2>/dev/null; then
                compliant=$((compliant + 1))
                status="✅ COMPLIANT"
                local timestamp_line=$(grep -m1 "CST\|Chicago Time" "$file" 2>/dev/null || echo "Unknown")
                echo "| $relative_path | $status | $timestamp_line |" >> "$report_file"
            else
                echo "| $relative_path | $status | No timestamp found |" >> "$report_file"
            fi
        fi
    done < <(find "$target_dir" -type f \( -name "*.md" -o -name "*.txt" -o -name "*.log" \) -print0 2>/dev/null)
    
    cat >> "$report_file" << EOF

## COMPLIANCE METRICS
- **Total Documents:** $total
- **Compliant:** $compliant
- **Non-Compliant:** $((total - compliant))
- **Compliance Rate:** $(( compliant * 100 / total ))%

## RECOMMENDATIONS
EOF
    
    if [[ $((compliant * 100 / total)) -lt 100 ]]; then
        cat >> "$report_file" << EOF
1. 🚨 **CRITICAL:** $((total - compliant)) documents missing Chicago timestamps
2. 🔧 **ACTION:** Run \`$0 "$target_dir" fix\` to add missing timestamps
3. 📋 **VERIFY:** Run \`$0 "$target_dir" verify\` after fixes
EOF
    else
        cat >> "$report_file" << EOF
1. ✅ **EXCELLENT:** All documents have Chicago timestamps
2. 📊 **MAINTAIN:** Continue enforcing timestamp requirements
3. 🎯 **MONITOR:** Regular compliance checks recommended
EOF
    fi
    
    echo "📄 Report generated: $report_file"
}

# Parse command line arguments
if [[ $# -eq 0 ]]; then
    # Default: enforce timestamps in current directory
    enforce_timestamps "$(pwd)" "add"
elif [[ $# -eq 1 ]]; then
    if [[ -d "$1" ]]; then
        # Directory provided, default operation
        enforce_timestamps "$1" "add"
    else
        # Operation provided, use current directory
        enforce_timestamps "$(pwd)" "$1"
    fi
else
    # Both directory and operation provided
    enforce_timestamps "$1" "$2"
fi

verbose_log "GTST timestamping tool execution complete"