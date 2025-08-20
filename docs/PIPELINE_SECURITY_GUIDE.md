# 🔒 MCP Pipeline Security System

## Overview

The MCP Pipeline Security System provides robust deletion protection for critical pipeline files. This system prevents accidental or malicious deletion of essential pipeline components.

## Protected Files

- `run-pipeline` - Main pipeline execution script
- `run-direct-pipeline` - Direct pipeline execution script  
- `mcp-claude-pipeline.py` - Master orchestrator

## Quick Start

### 1. Initialize Security System
```bash
./pipeline-security.sh setup
```
This will:
- Prompt you to set a master password (minimum 8 characters)
- Create secure backups of all pipeline files
- Apply file-level protections
- Set up integrity monitoring

### 2. Check Security Status
```bash
./pipeline-security.sh status
```

### 3. Verify File Integrity
```bash
./pipeline-security.sh check
```

## Security Features

### ✅ Deletion Protection
- Built-in detection of deletion attempts
- Password-protected file management
- Immutable file flags (when possible)
- Clear error messages for unauthorized access

### ✅ Integrity Monitoring
- SHA-256 hash verification
- Automatic corruption detection
- Real-time file monitoring
- Backup validation

### ✅ Secure Backup System
- Timestamped backup creation
- Multiple backup retention
- Hash-verified integrity
- One-click restoration

### ✅ Password Authentication
- Secure password hashing (SHA-256)
- Master password requirement for sensitive operations
- Authentication required for:
  - Removing file protections
  - Restoring from backups
  - System configuration changes

## Command Reference

| Command | Description | Password Required |
|---------|-------------|-------------------|
| `setup` | Initialize security system | Yes (set password) |
| `status` | Show current security status | No |
| `check` | Verify file integrity | No |
| `restore` | Restore files from backup | Yes |
| `unprotect` | Remove all protections | Yes |
| `monitor` | Run integrity check | No |

## Common Scenarios

### Accidental Deletion Attempt
If someone tries to delete a protected file:
```bash
rm run-pipeline
# Output: 🚨 DELETION PROTECTION ACTIVATED
#         ❌ Attempting to delete protected pipeline file: run-pipeline
#         🔒 This file is critical to the MCP system operation
#         🛡️ Deletion blocked for security
```

### File Corruption Recovery
```bash
./pipeline-security.sh check
# If corruption detected:
./pipeline-security.sh restore
# Enter master password when prompted
```

### Temporary Protection Removal
```bash
./pipeline-security.sh unprotect
# Enter master password and type 'CONFIRM'
# Make your changes
./pipeline-security.sh setup  # Re-enable protection
```

## Security Architecture

### Protection Layers
1. **Script-Level Protection**: Built-in deletion detection in pipeline files
2. **File-System Protection**: Immutable flags and permission restrictions
3. **Backup System**: Secure, hash-verified backups with restoration
4. **Authentication**: Password-protected administrative operations
5. **Monitoring**: Continuous integrity verification

### Security Directory Structure
```
.pipeline-security/
├── secure-backups/           # Timestamped file backups
│   ├── run-pipeline.backup.20250815_223045
│   ├── run-direct-pipeline.backup.20250815_223045
│   └── mcp-claude-pipeline.py.backup.20250815_223045
├── file-hashes.txt          # SHA-256 hashes for integrity verification
├── auth.hash                # Secure password hash
└── monitor.sh               # Automated integrity monitoring script
```

## Troubleshooting

### Q: I forgot my master password
**A:** You'll need to remove the `.pipeline-security` directory and run `setup` again. This will create new backups and require setting a new password.

### Q: The system says files are "unprotected"
**A:** Run `./pipeline-security.sh setup` to reapply protections, or check if you have sufficient permissions.

### Q: File integrity check fails
**A:** This indicates file modification or corruption. Run `./pipeline-security.sh restore` to restore from verified backups.

### Q: Can't execute pipeline-security.sh
**A:** Ensure the script is executable: `chmod +x pipeline-security.sh`

## Best Practices

1. **Set a Strong Password**: Use at least 8 characters with mixed case, numbers, and symbols
2. **Regular Integrity Checks**: Run `check` command periodically
3. **Keep Backups Current**: Re-run `setup` after making legitimate changes to pipeline files
4. **Document Password**: Store master password securely (password manager recommended)
5. **Monitor System**: Check status regularly to ensure protections remain active

## Integration with MCP Pipeline

The security system is designed to work seamlessly with the MCP pipeline:

- **Zero Impact**: Security checks add minimal overhead to pipeline execution
- **Automatic Monitoring**: Built-in integrity verification on each pipeline run
- **Transparent Operation**: Security works behind the scenes
- **Emergency Recovery**: Quick restoration capabilities for business continuity

## Emergency Procedures

### Complete System Recovery
If all pipeline files are lost or corrupted:
```bash
./pipeline-security.sh restore --force
# Enter master password
# All files will be restored from secure backups
```

### Security System Reset
If security system is compromised:
```bash
rm -rf .pipeline-security
./pipeline-security.sh setup
# Set new master password
# New secure backups will be created
```

---

🔒 **Remember**: The security system is only as strong as your master password. Choose wisely and store securely!