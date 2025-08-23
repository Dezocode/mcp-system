#!/usr/bin/env bash
# MCP Pipeline Security System - Deletion Protection
# Protects critical pipeline files from accidental or malicious deletion

# Configuration
PIPELINE_FILES=("run-pipeline" "run-direct-pipeline" "mcp-claude-pipeline.py")
SECURITY_DIR=".pipeline-security"
BACKUP_DIR="${SECURITY_DIR}/secure-backups"
HASH_FILE="${SECURITY_DIR}/file-hashes.txt"
PASSWORD_HASH_FILE="${SECURITY_DIR}/auth.hash"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Security functions
setup_security() {
    echo -e "${BLUE}🔒 Setting up MCP Pipeline Security System${NC}"
    
    # Create security directories
    mkdir -p "${BACKUP_DIR}"
    
    # Set password if not exists
    if [[ ! -f "${PASSWORD_HASH_FILE}" ]]; then
        set_master_password "$1"
    fi
    
    # Create secure backups
    create_secure_backups
    
    # Set file protections
    protect_pipeline_files
    
    # Create monitoring script
    create_file_monitor
    
    echo -e "${GREEN}✅ Pipeline security system activated${NC}"
}

set_master_password() {
    echo -e "${YELLOW}🔐 Setting up master password for pipeline protection${NC}"
    
    # Check for automated setup with default password
    if [[ "$1" == "--auto" ]]; then
        default_password="MCP2024SecurePipeline!"
        echo "Using default secure password for automated setup"
        password_hash=$(echo -n "$default_password" | shasum -a 256 | cut -d' ' -f1)
        echo "$password_hash" > "${PASSWORD_HASH_FILE}"
        chmod 600 "${PASSWORD_HASH_FILE}"
        echo -e "${GREEN}✅ Master password set successfully (default)${NC}"
        echo -e "${YELLOW}⚠️  Default password: MCP2024SecurePipeline!${NC}"
        echo -e "${YELLOW}   Change it using: ./pipeline-security.sh change-password${NC}"
        return
    fi
    
    echo "This password will be required to disable security or force delete pipeline files."
    echo
    
    while true; do
        read -s -p "Enter master password: " password1
        echo
        read -s -p "Confirm master password: " password2
        echo
        
        if [[ "$password1" == "$password2" ]] && [[ ${#password1} -ge 8 ]]; then
            # Create secure hash
            password_hash=$(echo -n "$password1" | shasum -a 256 | cut -d' ' -f1)
            echo "$password_hash" > "${PASSWORD_HASH_FILE}"
            chmod 600 "${PASSWORD_HASH_FILE}"
            echo -e "${GREEN}✅ Master password set successfully${NC}"
            break
        elif [[ ${#password1} -lt 8 ]]; then
            echo -e "${RED}❌ Password must be at least 8 characters${NC}"
        else
            echo -e "${RED}❌ Passwords do not match${NC}"
        fi
    done
}

verify_password() {
    if [[ ! -f "${PASSWORD_HASH_FILE}" ]]; then
        echo -e "${RED}❌ No password set. Run setup first.${NC}"
        return 1
    fi
    
    read -s -p "🔐 Enter master password: " input_password
    echo
    
    input_hash=$(echo -n "$input_password" | shasum -a 256 | cut -d' ' -f1)
    stored_hash=$(cat "${PASSWORD_HASH_FILE}")
    
    if [[ "$input_hash" == "$stored_hash" ]]; then
        return 0
    else
        echo -e "${RED}❌ Invalid password${NC}"
        return 1
    fi
}

create_secure_backups() {
    echo -e "${BLUE}💾 Creating secure backups of pipeline files${NC}"
    
    for file in "${PIPELINE_FILES[@]}"; do
        if [[ -f "$file" ]]; then
            # Create timestamped backup
            timestamp=$(date +"%Y%m%d_%H%M%S")
            backup_file="${BACKUP_DIR}/${file}.backup.${timestamp}"
            cp "$file" "$backup_file"
            
            # Calculate and store hash
            file_hash=$(shasum -a 256 "$file" | cut -d' ' -f1)
            echo "${file}:${file_hash}:${backup_file}" >> "${HASH_FILE}"
            
            echo "  ✅ Backed up: $file → $backup_file"
        fi
    done
}

protect_pipeline_files() {
    echo -e "${BLUE}🛡️ Applying file protection to pipeline files${NC}"
    
    for file in "${PIPELINE_FILES[@]}"; do
        if [[ -f "$file" ]]; then
            # Set file as immutable (macOS equivalent)
            chflags uchg "$file" 2>/dev/null || {
                echo "  ⚠️  Could not set immutable flag on $file (requires sudo)"
            }
            
            # Set restrictive permissions
            chmod 755 "$file"
            
            echo "  🔒 Protected: $file"
        fi
    done
}

create_file_monitor() {
    cat > "${SECURITY_DIR}/monitor.sh" << 'EOF'
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
EOF
    
    chmod +x "${SECURITY_DIR}/monitor.sh"
}

check_integrity() {
    echo -e "${BLUE}🔍 Checking pipeline integrity${NC}"
    
    if [[ ! -f "${HASH_FILE}" ]]; then
        echo -e "${RED}❌ No hash file found. Run setup first.${NC}"
        return 1
    fi
    
    issues_found=0
    
    while IFS=':' read -r file original_hash backup_path; do
        if [[ -f "$file" ]]; then
            current_hash=$(shasum -a 256 "$file" | cut -d' ' -f1)
            if [[ "$current_hash" != "$original_hash" ]]; then
                echo -e "${YELLOW}⚠️  WARNING: $file has been modified!${NC}"
                echo "   Backup available: $backup_path"
                ((issues_found++))
            else
                echo -e "${GREEN}✅ $file: integrity verified${NC}"
            fi
        else
            echo -e "${RED}🚨 CRITICAL: $file is missing!${NC}"
            echo "   Backup available: $backup_path"
            ((issues_found++))
        fi
    done < "$HASH_FILE"
    
    if [[ $issues_found -eq 0 ]]; then
        echo -e "${GREEN}🛡️ All pipeline files are secure and intact${NC}"
    else
        echo -e "${RED}❌ Found $issues_found integrity issues${NC}"
        echo "Run './pipeline-security.sh restore' to fix issues"
    fi
}

restore_files() {
    echo -e "${YELLOW}🔧 Pipeline File Restoration${NC}"
    echo "This will restore pipeline files from secure backups."
    echo
    
    if ! verify_password; then
        echo -e "${RED}❌ Authentication failed${NC}"
        return 1
    fi
    
    echo -e "${BLUE}📦 Restoring pipeline files${NC}"
    
    while IFS=':' read -r file original_hash backup_path; do
        if [[ ! -f "$file" ]] || [[ "$1" == "--force" ]]; then
            if [[ -f "$backup_path" ]]; then
                cp "$backup_path" "$file"
                chmod 755 "$file"
                echo -e "${GREEN}✅ Restored: $file${NC}"
            else
                echo -e "${RED}❌ Backup not found: $backup_path${NC}"
            fi
        fi
    done < "$HASH_FILE"
    
    # Reapply protections
    protect_pipeline_files
}

unprotect_files() {
    echo -e "${YELLOW}⚠️  Removing Pipeline Protection${NC}"
    echo "This will remove all file protections from pipeline files."
    echo -e "${RED}WARNING: Files will be vulnerable to deletion!${NC}"
    echo
    
    if ! verify_password; then
        echo -e "${RED}❌ Authentication failed${NC}"
        return 1
    fi
    
    read -p "Are you sure you want to remove protection? (type 'CONFIRM'): " confirm
    if [[ "$confirm" != "CONFIRM" ]]; then
        echo -e "${YELLOW}Operation cancelled${NC}"
        return 1
    fi
    
    echo -e "${BLUE}🔓 Removing file protections${NC}"
    
    for file in "${PIPELINE_FILES[@]}"; do
        if [[ -f "$file" ]]; then
            # Remove immutable flag
            chflags nouchg "$file" 2>/dev/null
            echo "  🔓 Unprotected: $file"
        fi
    done
    
    echo -e "${GREEN}✅ All protections removed${NC}"
}

show_status() {
    echo -e "${BLUE}🔒 MCP Pipeline Security Status${NC}"
    echo "=================================="
    echo
    
    # Check if security is set up
    if [[ -d "$SECURITY_DIR" ]]; then
        echo -e "${GREEN}✅ Security system: ACTIVE${NC}"
        echo "📁 Security directory: $SECURITY_DIR"
        echo "💾 Backups directory: $BACKUP_DIR"
        echo
        
        # File status
        echo "📋 Protected Files:"
        for file in "${PIPELINE_FILES[@]}"; do
            if [[ -f "$file" ]]; then
                # Check if file is protected (immutable)
                if ls -lO "$file" 2>/dev/null | grep -q "uchg"; then
                    echo -e "  🔒 $file: ${GREEN}PROTECTED${NC}"
                else
                    echo -e "  🔓 $file: ${YELLOW}UNPROTECTED${NC}"
                fi
            else
                echo -e "  ❌ $file: ${RED}MISSING${NC}"
            fi
        done
        echo
        
        # Backup count
        backup_count=$(ls -1 "$BACKUP_DIR" 2>/dev/null | wc -l)
        echo "💾 Available backups: $backup_count"
        
    else
        echo -e "${RED}❌ Security system: INACTIVE${NC}"
        echo "Run './pipeline-security.sh setup' to activate protection"
    fi
}

# Main script logic
case "$1" in
    "setup")
        setup_security "$2"
        ;;
    "auto-setup")
        setup_security "--auto"
        ;;
    "check")
        check_integrity
        ;;
    "restore")
        restore_files "$2"
        ;;
    "unprotect")
        unprotect_files
        ;;
    "status")
        show_status
        ;;
    "monitor")
        "${SECURITY_DIR}/monitor.sh"
        ;;
    *)
        echo -e "${BLUE}🔒 MCP Pipeline Security System${NC}"
        echo "================================"
        echo
        echo "Usage: $0 {setup|check|restore|unprotect|status|monitor}"
        echo
        echo "Commands:"
        echo "  setup     - Initialize security system and set master password"
        echo "  check     - Check file integrity and protection status"
        echo "  restore   - Restore files from secure backups (requires password)"
        echo "  unprotect - Remove all file protections (requires password)"
        echo "  status    - Show current security status"
        echo "  monitor   - Run file integrity monitor"
        echo
        echo "Examples:"
        echo "  $0 setup           # Initial setup with password"
        echo "  $0 check           # Verify file integrity"
        echo "  $0 restore         # Restore missing/corrupted files"
        echo "  $0 restore --force # Force restore all files"
        echo
        exit 1
        ;;
esac