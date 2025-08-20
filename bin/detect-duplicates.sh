#!/bin/bash

# 🗑️ Duplicate/Placeholder Detection and Removal System
# Identifies and removes competing implementations, duplicates, and placeholder code

PROJECT_DIR="${1:-$(pwd)}"

echo "🗑️  DUPLICATE/PLACEHOLDER DETECTION SYSTEM"
echo "📁 Scanning: $PROJECT_DIR"
echo ""

# Function to detect duplicate functions
detect_duplicate_functions() {
    echo "🔍 SCANNING FOR DUPLICATE FUNCTIONS:"
    
    # Find JavaScript files and extract function names
    find "$PROJECT_DIR" -name "*.js" -not -path "*/node_modules/*" -exec grep -l "function\|const.*=\|class\|module.exports" {} \; | while read -r file; do
        echo "   📄 Analyzing: $(basename "$file")"
        
        # Extract function names and their line numbers
        grep -n "function\s\+\w\+\|const\s\+\w\+\s*=\|class\s\+\w\+\|module\.exports\s*=" "$file" | while IFS=':' read -r line_num content; do
            # Extract function name
            func_name=$(echo "$content" | sed -E 's/.*function\s+([a-zA-Z_][a-zA-Z0-9_]*).*/\1/; s/.*const\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*=.*/\1/; s/.*class\s+([a-zA-Z_][a-zA-Z0-9_]*).*/\1/; s/.*module\.exports\s*=.*/module.exports/')
            
            if [[ -n "$func_name" && "$func_name" != "$content" ]]; then
                echo "      • Line $line_num: $func_name"
            fi
        done
        echo ""
    done
}

# Function to detect placeholder code
detect_placeholders() {
    echo "🔍 SCANNING FOR PLACEHOLDER/TEMPLATE CODE:"
    
    # Common placeholder patterns
    PLACEHOLDER_PATTERNS=(
        "TODO"
        "FIXME"
        "PLACEHOLDER"
        "TEMPLATE"
        "EXAMPLE"
        "// Replace this"
        "// Implement"
        "throw new Error.*not.*implement"
        "console\.log.*placeholder"
        "console\.log.*test"
        "// TODO:"
        "// FIXME:"
    )
    
    for pattern in "${PLACEHOLDER_PATTERNS[@]}"; do
        echo "   🔍 Searching for: $pattern"
        find "$PROJECT_DIR" -name "*.js" -not -path "*/node_modules/*" -exec grep -l "$pattern" {} \; | while read -r file; do
            echo "      📄 Found in: $(basename "$file")"
            grep -n "$pattern" "$file" | head -3
        done
    done
    echo ""
}

# Function to detect competing implementations
detect_competing_code() {
    echo "🔍 SCANNING FOR COMPETING IMPLEMENTATIONS:"
    
    # Look for multiple files with similar functions
    echo "   📊 Files with similar function patterns:"
    
    find "$PROJECT_DIR" -name "*.js" -not -path "*/node_modules/*" | while read -r file; do
        basename_file=$(basename "$file")
        
        # Check for similar named files
        find "$PROJECT_DIR" -name "*$(basename "$file" .js)*" -name "*.js" -not -path "*/node_modules/*" | grep -v "^$file$" | while read -r similar_file; do
            echo "      🔄 Potential duplicates:"
            echo "         • $(basename "$file")"
            echo "         • $(basename "$similar_file")"
            
            # Check if they have similar function signatures
            func_count_1=$(grep -c "function\|const.*=\|class" "$file" 2>/dev/null || echo "0")
            func_count_2=$(grep -c "function\|const.*=\|class" "$similar_file" 2>/dev/null || echo "0")
            
            if [[ "$func_count_1" -gt 0 && "$func_count_2" -gt 0 ]]; then
                echo "         📊 Function counts: $func_count_1 vs $func_count_2"
            fi
            echo ""
        done
    done
}

# Function to detect unused imports
detect_unused_imports() {
    echo "🔍 SCANNING FOR UNUSED IMPORTS:"
    
    find "$PROJECT_DIR" -name "*.js" -not -path "*/node_modules/*" | while read -r file; do
        echo "   📄 Analyzing imports in: $(basename "$file")"
        
        # Extract require/import statements
        grep -n "require\|import.*from" "$file" | while IFS=':' read -r line_num content; do
            # Extract variable name from require/import
            var_name=$(echo "$content" | sed -E 's/.*const\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*=.*/\1/; s/.*import\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+from.*/\1/; s/.*{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*}.*/\1/')
            
            if [[ -n "$var_name" && "$var_name" != "$content" ]]; then
                # Check if variable is used elsewhere in file
                usage_count=$(grep -c "$var_name" "$file")
                if [[ "$usage_count" -eq 1 ]]; then
                    echo "      ⚠️  Line $line_num: $var_name (potentially unused)"
                fi
            fi
        done
        echo ""
    done
}

# Main execution
echo "🚨 STARTING COMPREHENSIVE DUPLICATE/PLACEHOLDER SCAN"
echo ""

detect_duplicate_functions
detect_placeholders
detect_competing_code
detect_unused_imports

echo "✅ DUPLICATE/PLACEHOLDER SCAN COMPLETED"
echo ""
echo "📋 AGENT ACTION REQUIRED:"
echo "   1. Review identified duplicates and competing implementations"
echo "   2. Remove placeholder/template code and replace with real implementations"
echo "   3. Clean up unused imports and variables"
echo "   4. Consolidate competing functions into single implementations"
echo "   5. Ensure no functionality is lost during cleanup"
echo ""
echo "⚡ After cleanup, re-run codemap analysis to verify improvements"