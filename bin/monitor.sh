#!/usr/bin/env bash
# Pipeline File Monitor - Detects unauthorized changes/deletions

SECURITY_DIR=".pipeline-security"
PIPELINE_FILES=("run-pipeline" "run-direct-pipeline" "mcp-claude-pipeline.py")
HASH_FILE="${SECURITY_DIR}/file-hashes.txt"

check_integrity() {
    echo "🔍 Checking pipeline file integrity..."
    
    while IFS=':' read -r file original_hash backup_path; do
        if [[ -f "$file" ]]; then
            current_hash=$(shasum -a 256 "$file" | cut -d' ' -f1)
            if [[ "$current_hash" != "$original_hash" ]]; then
                echo "⚠️  WARNING: $file has been modified!"
                echo "   Original hash: $original_hash"
                echo "   Current hash:  $current_hash"
                echo "   Backup available: $backup_path"
            fi
        else
            echo "🚨 CRITICAL: $file is missing!"
            echo "   Backup available: $backup_path"
            echo "   Run './pipeline-security.sh restore' to recover"
        fi
    done < "$HASH_FILE"
}

# Run integrity check
check_integrity
