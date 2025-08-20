# Claude Quality Patcher Guide

## 🤖 Integrated Step-by-Step Code Fixing with Claude

The Claude Quality Patcher is an advanced system that forces Claude to fix lint issues **one-by-one** using Claude's Write/Edit tools with strict compatibility validation.

## 🎯 How It Works

### **Step-by-Step Process:**
1. **Load lint report** from comprehensive linting
2. **Filter to safe fixes** (excludes blocked/dangerous changes)
3. **Present one fix at a time** to Claude with specific instructions
4. **Force Claude to use Read/Edit tools** for each fix
5. **Validate syntax** after every change
6. **Automatic rollback** if validation fails
7. **Track session progress** with detailed logging

## 🚀 Quick Start

### **1. Generate Lint Report First**
```bash
# Generate comprehensive lint report
python3 scripts/version_keeper.py --comprehensive-lint --output-dir=reports/
```

### **2. Run Quality Patcher**
```bash
# Interactive mode (recommended)
python3 scripts/claude_quality_patcher.py --max-fixes 10

# Auto mode for safe fixes only
python3 scripts/claude_quality_patcher.py --auto-mode --max-fixes 20

# Dry run to see what would be fixed
python3 scripts/claude_quality_patcher.py --dry-run --max-fixes 50
```

## 🔧 CLI Options

```bash
python3 scripts/claude_quality_patcher.py [OPTIONS]

Options:
  --lint-report PATH     Path to Claude lint report JSON file
  --max-fixes INTEGER    Maximum fixes to apply in session (default: 10)
  --interactive         Interactive mode for fix confirmation (default)
  --no-interactive      Skip confirmations
  --auto-mode           Run automatically with safe fixes only
  --dry-run             Show fixes without applying changes
  --help                Show help message
```

## 🛡️ Safety Features

### **Strict Compatibility Checking:**
- ✅ **One fix at a time** - No batch changes
- ✅ **Read before edit** - Forces Claude to read target file first
- ✅ **Syntax validation** - Compiles Python after each change
- ✅ **Automatic backup** - Creates timestamped backups
- ✅ **Automatic rollback** - Reverts on validation failure
- ✅ **Dependency checking** - Validates fix won't break code

### **Blocked Fix Prevention:**
```json
{
  "blocked_recommendations": [
    {
      "fix": {
        "description": "Remove duplicate function main in mcp-router.py"
      },
      "reason": "Removing main from mcp-router.py would break dependencies"
    }
  ]
}
```

## 📋 Fix Categories & Priorities

### **Priority 1: 🔴 Security Issues**
- Subprocess security risks
- Hardcoded credentials
- Unsafe imports
- **Action:** Manual review with Claude assistance

### **Priority 2: 🟡 Duplicate Functions**
- AST-detected duplicate implementations
- Safe removal candidates only
- **Action:** Remove with dependency validation

### **Priority 3: 🟢 Connection Issues**
- Undefined function calls
- Broken imports
- **Action:** Fix imports/add missing functions

### **Priority 4: ⚪ Quality Issues**
- Code formatting (black/isort)
- Type errors (mypy)
- Style violations (flake8)
- **Action:** Auto-fix or manual correction

## 🔄 Interactive Workflow

### **Example Session:**
```
🤖 Claude Quality Patcher Session
============================================================
⚠️  SAFETY PROTOCOLS ENABLED:
   • One fix at a time
   • Read file before every edit
   • Validate fix compatibility
   • Test syntax after each change
   • Automatic rollback on failure
============================================================

📋 Found 23 fixes to apply
🎯 Will apply maximum 10 fixes in this session

============================================================
🔧 FIX 1/10
============================================================
🎯 Priority 1 | SECURITY | security_fix
📝 Security issue in src/auto-discovery-system.py:170

📋 CLAUDE PROMPT:
------------------------------------------------------------
🔴 CLAUDE QUALITY PATCHER - SINGLE FIX REQUEST
Category: SECURITY | Priority: 1 | Type: security_fix

INSTRUCTIONS:
1. READ the target file first using the Read tool
2. IDENTIFY the exact issue at line 170
3. APPLY the fix using Edit tool
4. VALIDATE the syntax is correct after your change

FIX DESCRIPTION:
Please review and fix the security issue in src/auto-discovery-system.py:170: 
subprocess call - check for execution of untrusted input.

SAFETY REQUIREMENTS:
- Only modify line 170 and surrounding context if needed
- Preserve all existing functionality
- Maintain code style and formatting
- Do not introduce new dependencies
- Do not remove critical imports or function calls
------------------------------------------------------------

❓ Apply this fix? (y/n/s=skip): y

  💾 Backup created: .claude_patches/backups/auto-discovery-system.py.20250815_133045.backup

🤖 CLAUDE: Please apply the fix now using Read/Edit tools
👆 USE THE PROMPT ABOVE TO MAKE THE EXACT FIX REQUIRED

⏸️  Press Enter after Claude has applied the fix...

🔍 Validating fix applied to src/auto-discovery-system.py...
  ✅ Python syntax valid
  ✅ Fix applied - security issue resolved
✅ Fix validated successfully

⏸️  Pausing 2 seconds between fixes for safety...
```

## 📊 Session Reporting

### **Real-Time Progress:**
```
📊 SUMMARY:
  ✅ Fixes Applied: 8
  ⏭️ Fixes Skipped: 1
  ❌ Fixes Failed: 1
  📋 Total Available: 23
```

### **Detailed Session Log:**
```json
{
  "session_info": {
    "timestamp": "20250815_133045",
    "repo_path": "/Users/user/mcp-system-complete",
    "fixes_applied": 8,
    "fixes_skipped": 1,
    "fixes_failed": 1
  },
  "session_log": [
    {
      "type": "fix_applied",
      "timestamp": "2025-08-15T13:30:45",
      "fix_item": {...},
      "validation": {...},
      "backup_path": "..."
    }
  ]
}
```

## 🎯 Usage Scenarios

### **Scenario 1: Security Fix Session**
```bash
# Focus on security issues only
python3 scripts/claude_quality_patcher.py --max-fixes 5 --interactive
```
- Reviews each security issue individually
- Forces Claude to read code context
- Validates security fix doesn't break functionality

### **Scenario 2: Quick Quality Improvements**
```bash
# Auto-apply safe formatting fixes
python3 scripts/claude_quality_patcher.py --auto-mode --max-fixes 20
```
- Applies black/isort formatting automatically
- Fixes simple type errors
- Skips complex manual fixes

### **Scenario 3: Duplicate Function Cleanup**
```bash
# Review and remove safe duplicates
python3 scripts/claude_quality_patcher.py --max-fixes 15 --interactive
```
- Shows dependency analysis for each duplicate
- Confirms removal won't break imports
- Provides file:line references for verification

## 📁 Generated Files

### **Backups:**
```
.claude_patches/backups/
├── auto-discovery-system.py.20250815_133045.backup
├── mcp-router.py.20250815_133102.backup
└── version_keeper.py.20250815_133158.backup
```

### **Session Logs:**
```
.claude_patches/logs/
├── claude_patch_session_20250815_133045.json
└── claude_patch_session_20250815_134502.json
```

## 🔄 Continue Fixing

### **Resume Previous Session:**
```bash
# Continue with remaining fixes
python3 scripts/claude_quality_patcher.py --max-fixes 10

# Re-run lint to see remaining issues
python3 scripts/version_keeper.py --comprehensive-lint --output-dir=reports/
```

### **Track Progress:**
```bash
# View session logs
ls -la .claude_patches/logs/

# Check remaining issues
python3 scripts/version_keeper.py --claude-lint --lint-only
```

## ⚠️ Important Notes

### **Claude Instructions:**
1. **Always use Read tool first** before making any edit
2. **Only fix the specific issue** mentioned in the prompt
3. **Preserve existing code structure** and formatting
4. **Test your change** by ensuring syntax is valid
5. **Don't add unnecessary dependencies** or imports

### **User Responsibilities:**
1. **Review each fix prompt** before approving
2. **Verify Claude used Read tool** before editing
3. **Check backup was created** for each change
4. **Monitor validation results** for each fix
5. **Stop session if unexpected behavior** occurs

### **Emergency Procedures:**
```bash
# Rollback all changes in session
cd .claude_patches/backups/
for backup in *.backup; do
    original=$(echo $backup | sed 's/\.[0-9_]*\.backup$//')
    cp "$backup" "../../src/$original"
done
```

## 🎉 Success Metrics

- **Safety:** Zero code-breaking changes
- **Accuracy:** Each fix addresses exact issue reported
- **Traceability:** Full session logs and backups
- **Efficiency:** One fix per Claude interaction
- **Validation:** Syntax checking after every change

The Claude Quality Patcher ensures **safe, controlled, step-by-step code improvements** with full traceability and automatic safety measures.