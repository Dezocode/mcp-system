# 🔧 AUTOFIX ACTION PLAN - Safe Path to Clean Codebase
**Generated**: 2025-01-29  
**Execution Time**: ~30-45 minutes  
**Risk Level After Completion**: LOW (2/10)  

---

## 📊 Pre-Execution Checklist

- [ ] Full backup created
- [ ] Working in version-0.3 branch (not main)
- [ ] No critical processes running
- [ ] 45 minutes available for fixes
- [ ] Terminal access ready

---

## PHASE 1: CRITICAL SYNTAX FIXES
**Time**: 10 minutes  
**Risk**: LOW  
**Priority**: MANDATORY  

### Step 1.1: Identify All Hyphenated Module Files

```bash
# List all Python files with hyphens in their names
echo "=== Checking for hyphenated Python files ==="
find . -name "*-*.py" -type f | grep -v ".autofix_backups" | sort
```

**Expected Output**:
```
./bin/mcp-crafter
./core/auto-discovery-system.py
./core/claude-code-mcp-bridge.py
./core/mcp-create-server.py
./core/mcp-manager.py
./core/mcp-mem0-client.py
./core/mcp-mem0-simple.py
./core/mcp-router.py
./core/mcp-test-framework.py
./core/mcp-upgrader.py
./mcp-claude-pipeline-enhanced.py
./mcp-docker-orchestration-integration.py
./mcp-file-sync-manager.py
```

**Reasoning**: 
- Python modules CANNOT contain hyphens (PEP 8)
- Hyphens are interpreted as minus operators
- This is the ROOT CAUSE of syntax errors

### Step 1.2: Batch Rename All Hyphenated Files

```bash
#!/bin/bash
# Save as: fix_module_names.sh

echo "=== Renaming hyphenated Python files ==="

# Create rename mapping for verification
declare -A renames=(
    ["core/auto-discovery-system.py"]="core/auto_discovery_system.py"
    ["core/claude-code-mcp-bridge.py"]="core/claude_code_mcp_bridge.py"
    ["core/mcp-create-server.py"]="core/mcp_create_server.py"
    ["core/mcp-manager.py"]="core/mcp_manager.py"
    ["core/mcp-mem0-client.py"]="core/mcp_mem0_client.py"
    ["core/mcp-mem0-simple.py"]="core/mcp_mem0_simple.py"
    ["core/mcp-router.py"]="core/mcp_router.py"
    ["core/mcp-test-framework.py"]="core/mcp_test_framework.py"
    ["core/mcp-upgrader.py"]="core/mcp_upgrader.py"
    ["mcp-claude-pipeline-enhanced.py"]="mcp_claude_pipeline_enhanced.py"
    ["mcp-docker-orchestration-integration.py"]="mcp_docker_orchestration_integration.py"
    ["mcp-file-sync-manager.py"]="mcp_file_sync_manager.py"
)

# Perform renames
for old_name in "${!renames[@]}"; do
    new_name="${renames[$old_name]}"
    if [ -f "$old_name" ]; then
        echo "  Renaming: $old_name -> $new_name"
        mv "$old_name" "$new_name"
    else
        echo "  Skipped: $old_name (not found)"
    fi
done

echo "=== Rename complete ==="
```

**Validation Command**:
```bash
# Verify no hyphenated Python files remain
find . -name "*-*.py" -type f | grep -v ".autofix_backups" | wc -l
# Should output: 0
```

**Reasoning**:
- Atomic operation that fixes the fundamental issue
- No code changes, just filesystem operations
- Immediately resolves syntax errors from imports

### Step 1.3: Fix All Import Statements

```bash
#!/bin/bash
# Save as: fix_imports.sh

echo "=== Fixing import statements ==="

# Count files before fixing
total_files=$(find . -name "*.py" -type f | grep -v ".autofix_backups" | wc -l)
echo "Processing $total_files Python files..."

# Create comprehensive sed script for all import fixes
cat > /tmp/fix_imports.sed << 'EOF'
# Core module imports
s/from core\.auto-discovery-system/from core.auto_discovery_system/g
s/from core\.claude-code-mcp-bridge/from core.claude_code_mcp_bridge/g
s/from core\.mcp-create-server/from core.mcp_create_server/g
s/from core\.mcp-manager/from core.mcp_manager/g
s/from core\.mcp-mem0-client/from core.mcp_mem0_client/g
s/from core\.mcp-mem0-simple/from core.mcp_mem0_simple/g
s/from core\.mcp-router/from core.mcp_router/g
s/from core\.mcp-test-framework/from core.mcp_test_framework/g
s/from core\.mcp-upgrader/from core.mcp_upgrader/g

# Root module imports (absolute)
s/from mcp-claude-pipeline-enhanced/from mcp_claude_pipeline_enhanced/g
s/from mcp-docker-orchestration-integration/from mcp_docker_orchestration_integration/g
s/from mcp-file-sync-manager/from mcp_file_sync_manager/g

# Root module imports (relative)
s/from \.mcp-claude-pipeline-enhanced/from .mcp_claude_pipeline_enhanced/g
s/from \.mcp-docker-orchestration-integration/from .mcp_docker_orchestration_integration/g
s/from \.mcp-file-sync-manager/from .mcp_file_sync_manager/g

# Import statements (import X)
s/import mcp-/import mcp_/g
s/import core\.mcp-/import core.mcp_/g
EOF

# Apply fixes to all Python files
fixed_count=0
find . -name "*.py" -type f | while read -r file; do
    # Skip backup directories
    if [[ "$file" == *".autofix_backups"* ]]; then
        continue
    fi
    
    # Check if file needs fixing
    if grep -q "mcp-\|auto-discovery-system\|claude-code-mcp-bridge" "$file" 2>/dev/null; then
        echo "  Fixing: $file"
        sed -i.bak -f /tmp/fix_imports.sed "$file"
        rm -f "${file}.bak"
        ((fixed_count++))
    fi
done

echo "=== Fixed imports in $fixed_count files ==="
```

**Validation**:
```bash
# Test that imports are fixed
grep -r "from.*mcp-" --include="*.py" . 2>/dev/null | grep -v ".autofix_backups" | wc -l
# Should output: 0
```

**Reasoning**:
- Systematic replacement ensures no imports are missed
- Uses sed for reliable text replacement
- Creates backups that are immediately removed after success

---

## PHASE 2: FIX TEMPLATE STRING ISSUE
**Time**: 5 minutes  
**Risk**: MEDIUM  
**Priority**: MANDATORY  

### Step 2.1: Diagnose the Template Issue

```bash
# Examine the problematic section
echo "=== Checking template issue in mcp_crafter.py ==="
python3 -c "
with open('src/mcp_crafter.py', 'r') as f:
    lines = f.readlines()
    print('Lines 2305-2320:')
    for i in range(2304, min(2320, len(lines))):
        print(f'{i+1:4d}: {lines[i]}', end='')
"
```

**Expected Issue**:
```python
2309:       interval: 10s    # Unquoted YAML value
2310:       timeout: 5s      # Unquoted YAML value
```

### Step 2.2: Apply Template String Fix

```python
#!/usr/bin/env python3
# Save as: fix_template.py

import re
import sys

print("=== Fixing template strings in mcp_crafter.py ===")

try:
    with open('src/mcp_crafter.py', 'r') as f:
        content = f.read()
    
    # Fix pattern 1: Unquoted time values in YAML
    fixes_applied = 0
    
    # Fix intervals and timeouts
    patterns = [
        (r'interval:\s*(\d+)s', r'interval: "\1s"'),
        (r'timeout:\s*(\d+)s', r'timeout: "\1s"'),
        (r'delay:\s*(\d+)s', r'delay: "\1s"'),
        (r'period:\s*(\d+)s', r'period: "\1s"'),
    ]
    
    for pattern, replacement in patterns:
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            fixes_applied += 1
            print(f"  Fixed: {pattern} -> {replacement}")
    
    # Write back
    with open('src/mcp_crafter.py', 'w') as f:
        f.write(content)
    
    print(f"=== Applied {fixes_applied} template fixes ===")
    
    # Validate syntax
    compile(content, 'src/mcp_crafter.py', 'exec')
    print("✓ Syntax validation passed!")
    
except SyntaxError as e:
    print(f"✗ Syntax error remains: {e}")
    print("  Manual intervention required")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)
```

**Run Fix**:
```bash
python3 fix_template.py
```

**Validation**:
```bash
# Test syntax is fixed
python3 -m py_compile src/mcp_crafter.py && echo "✓ mcp_crafter.py syntax valid" || echo "✗ Still has syntax errors"
```

**Reasoning**:
- YAML values with units (10s, 5s) must be quoted in Python strings
- Regex ensures we only fix the specific pattern
- Compile check validates the fix worked

---

## PHASE 3: REMOVE BROKEN utils/functions.py
**Time**: 5 minutes  
**Risk**: HIGH (but necessary)  
**Priority**: MANDATORY  

### Step 3.1: Backup and Assessment

```bash
# Create safety backup
echo "=== Backing up utils/functions.py ==="
cp utils/functions.py utils/functions.py.broken_backup_$(date +%Y%m%d_%H%M%S)

# Analyze what's actually in the file
echo "=== Analyzing utils/functions.py content ==="
python3 -c "
import ast
try:
    with open('utils/functions.py', 'r') as f:
        content = f.read()
    tree = ast.parse(content)
    
    functions = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
    classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
    
    print(f'Functions found: {len(functions)}')
    print(f'Classes found: {len(classes)}')
    print(f'First 10 functions: {functions[:10]}')
    
    # Check for orphaned methods
    orphaned = [f for f in functions if f in ['__init__', '__post_init__', 'on_created', 'on_modified']]
    print(f'Orphaned methods: {orphaned}')
    
except SyntaxError as e:
    print(f'File has syntax errors: {e}')
"
```

### Step 3.2: Fix Files Using utils.functions

```python
#!/usr/bin/env python3
# Save as: fix_utils_imports.py

import os
import re

print("=== Fixing imports from utils.functions ===")

# Files that incorrectly import from utils.functions
files_to_fix = [
    'rapid_fix.py',
    'installers/install-mcp-system.py',
    'scripts/simple_quality_patcher.py',
    'scripts/version_manager.py',
    'scripts/simple_version_keeper.py',
    'scripts/docker-health-check.py',
    'demo_enhanced_orchestrator.py'
]

# Standard library mappings
correct_imports = {
    'Any': 'from typing import Any',
    'Dict': 'from typing import Dict',
    'List': 'from typing import List',
    'Optional': 'from typing import Optional',
    'Path': 'from pathlib import Path',
    'asyncio': 'import asyncio',
    'json': 'import json',
    'os': 'import os',
    'sys': 'import sys',
    'time': 'import time',
    'subprocess': 'import subprocess',
    're': 'import re',
}

for file_path in files_to_fix:
    if not os.path.exists(file_path):
        print(f"  Skipped: {file_path} (not found)")
        continue
    
    print(f"  Processing: {file_path}")
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Remove all utils.functions imports
    original_content = content
    content = re.sub(r'from utils\.functions import.*?\n(?:.*?,\n)*.*?\)', '', content, flags=re.MULTILINE)
    content = re.sub(r'from utils\.functions import.*?\n', '', content)
    
    # Identify what needs to be imported based on usage
    needed_imports = set()
    
    # Check for common patterns
    if 'Path(' in content or 'Path.' in content:
        needed_imports.add('from pathlib import Path')
    if 'asyncio.' in content or 'async def' in content:
        needed_imports.add('import asyncio')
    if 'json.' in content:
        needed_imports.add('import json')
    if 'os.' in content or 'os.path' in content:
        needed_imports.add('import os')
    if 'sys.' in content or 'sys.path' in content:
        needed_imports.add('import sys')
    if 'Dict[' in content:
        needed_imports.add('from typing import Dict')
    if 'List[' in content:
        needed_imports.add('from typing import List')
    if 'Any' in content:
        needed_imports.add('from typing import Any')
    if 'Optional[' in content:
        needed_imports.add('from typing import Optional')
    if 'subprocess.' in content:
        needed_imports.add('import subprocess')
    if re.search(r'\btime\.\w+', content):
        needed_imports.add('import time')
    if re.search(r'\bre\.\w+', content):
        needed_imports.add('import re')
    
    # Find insertion point (after shebang and docstring)
    lines = content.split('\n')
    insert_pos = 0
    
    for i, line in enumerate(lines):
        if line.startswith('#!'):
            insert_pos = i + 1
        elif line.strip().startswith('"""'):
            # Find end of docstring
            for j in range(i + 1, len(lines)):
                if '"""' in lines[j]:
                    insert_pos = j + 1
                    break
            break
        elif line.strip() and not line.startswith('#'):
            insert_pos = i
            break
    
    # Insert the needed imports
    if needed_imports:
        import_block = '\n'.join(sorted(needed_imports))
        lines.insert(insert_pos, import_block)
        lines.insert(insert_pos + 1, '')  # Empty line after imports
    
    # Write back
    new_content = '\n'.join(lines)
    
    # Only write if content changed
    if new_content != original_content:
        with open(file_path, 'w') as f:
            f.write(new_content)
        print(f"    ✓ Fixed imports")
    else:
        print(f"    - No changes needed")

print("=== Import fixes complete ===")
```

**Run Fix**:
```bash
python3 fix_utils_imports.py
```

### Step 3.3: Replace utils/functions.py

```bash
# Create a minimal, valid replacement
cat > utils/functions.py << 'EOF'
"""Utility functions module

This module was rebuilt after autofix corruption.
Original backed up as functions.py.broken_backup_*
"""

# Placeholder for future utility functions
# Add common utility functions here as needed

def safe_import(module_name: str):
    """Safely import a module with error handling"""
    try:
        return __import__(module_name)
    except ImportError as e:
        print(f"Warning: Could not import {module_name}: {e}")
        return None

# Add more utility functions as needed
EOF

echo "✓ Created clean utils/functions.py"
```

**Reasoning**:
- The original file is completely corrupted with orphaned methods
- Files importing from it are importing Python built-ins incorrectly
- Clean slate with proper imports is safer than trying to salvage

---

## PHASE 4: VALIDATION
**Time**: 5 minutes  
**Risk**: NONE  
**Priority**: MANDATORY  

### Step 4.1: Comprehensive Syntax Check

```bash
#!/bin/bash
# Save as: validate_syntax.sh

echo "=== Running comprehensive syntax validation ==="

# Check all Python files
error_count=0
success_count=0

find . -name "*.py" -type f | while read -r file; do
    # Skip backups
    if [[ "$file" == *".backup"* ]] || [[ "$file" == *".autofix_backups"* ]]; then
        continue
    fi
    
    # Try to compile
    if python3 -m py_compile "$file" 2>/dev/null; then
        ((success_count++))
        echo -n "."
    else
        echo ""
        echo "✗ Syntax error in: $file"
        python3 -m py_compile "$file" 2>&1 | head -2
        ((error_count++))
    fi
done

echo ""
echo "=== Validation Results ==="
echo "✓ Valid files: $success_count"
echo "✗ Files with errors: $error_count"

if [ $error_count -eq 0 ]; then
    echo "🎉 ALL FILES HAVE VALID SYNTAX!"
    exit 0
else
    echo "⚠️ Some files still have syntax errors"
    exit 1
fi
```

**Run Validation**:
```bash
chmod +x validate_syntax.sh
./validate_syntax.sh
```

### Step 4.2: Import Resolution Check

```python
#!/usr/bin/env python3
# Save as: validate_imports.py

import ast
import os
import sys

print("=== Validating import resolution ===")

def check_imports(file_path):
    """Check if imports in a file can be resolved"""
    issues = []
    
    try:
        with open(file_path, 'r') as f:
            tree = ast.parse(f.read())
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module_name = alias.name
                    # Check for hyphenated modules
                    if '-' in module_name:
                        issues.append(f"Invalid module name: {module_name}")
            
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                if '-' in module:
                    issues.append(f"Invalid module name: {module}")
                
                # Check for utils.functions imports
                if module == 'utils.functions':
                    imported_names = [alias.name for alias in node.names]
                    issues.append(f"Still importing from utils.functions: {imported_names}")
    
    except SyntaxError as e:
        issues.append(f"Syntax error: {e}")
    
    return issues

# Check all Python files
total_files = 0
problematic_files = []

for root, dirs, files in os.walk('.'):
    # Skip backup directories
    dirs[:] = [d for d in dirs if '.backup' not in d and '.autofix' not in d]
    
    for file in files:
        if file.endswith('.py'):
            file_path = os.path.join(root, file)
            total_files += 1
            
            issues = check_imports(file_path)
            if issues:
                problematic_files.append((file_path, issues))

print(f"Checked {total_files} Python files")

if problematic_files:
    print(f"\n⚠️ Found issues in {len(problematic_files)} files:")
    for file_path, issues in problematic_files[:10]:  # Show first 10
        print(f"\n{file_path}:")
        for issue in issues:
            print(f"  - {issue}")
else:
    print("✓ All imports look valid!")
```

**Run Import Check**:
```bash
python3 validate_imports.py
```

---

## PHASE 5: SAFE AUTOFIX EXECUTION
**Time**: 10 minutes  
**Risk**: LOW (after above fixes)  
**Priority**: RECOMMENDED  

### Step 5.1: Create Full Backup

```bash
# Create comprehensive backup
backup_dir="backups/pre-autofix-$(date +%Y%m%d-%H%M%S)"
echo "=== Creating backup in $backup_dir ==="

mkdir -p "$backup_dir"

# Use rsync for efficient copying
rsync -av \
    --exclude='.git' \
    --exclude='backups/' \
    --exclude='*.pyc' \
    --exclude='__pycache__' \
    --exclude='.autofix_backups' \
    . "$backup_dir/"

echo "✓ Backup created: $backup_dir"
echo "  Size: $(du -sh "$backup_dir" | cut -f1)"
echo "  Files: $(find "$backup_dir" -type f | wc -l)"
```

### Step 5.2: Autofix Dry Run

```bash
# Test what autofix would do
echo "=== Running autofix dry run ==="
python3 scripts/autofix.py --dry-run --verbose 2>&1 | tee autofix-dryrun-$(date +%Y%m%d-%H%M%S).log

# Check for critical errors
if grep -q "SyntaxError\|invalid syntax\|parsing AST" autofix-dryrun-*.log; then
    echo "⚠️ Dry run shows syntax errors remain!"
    echo "Do not proceed with autofix"
    exit 1
else
    echo "✓ Dry run completed without syntax errors"
fi
```

### Step 5.3: Progressive Autofix

```bash
# Stage 1: Format only (safest)
echo "=== Stage 1: Format-only autofix ==="
python3 scripts/autofix.py --format-only

# Validate
python3 -m py_compile src/mcp_crafter.py demo_enhanced_orchestrator.py

# Stage 2: Security scan only
echo "=== Stage 2: Security-only autofix ==="
python3 scripts/autofix.py --security-only

# Stage 3: Full autofix (if above succeeded)
echo "=== Stage 3: Full autofix ==="
python3 scripts/autofix.py --verbose
```

---

## PHASE 6: POST-FIX VERIFICATION
**Time**: 5 minutes  
**Risk**: NONE  
**Priority**: MANDATORY  

### Step 6.1: Final Validation Suite

```python
#!/usr/bin/env python3
# Save as: final_validation.py

import subprocess
import json
import sys
from pathlib import Path

print("=" * 60)
print("FINAL VALIDATION REPORT")
print("=" * 60)

results = {
    'syntax_check': False,
    'import_check': False,
    'security_scan': False,
    'no_hyphenated_modules': False,
    'utils_functions_clean': False,
    'critical_files_valid': False
}

# 1. Syntax Check
print("\n1. Syntax Validation...")
try:
    subprocess.run(['python3', 'validate_syntax.sh'], check=True, capture_output=True)
    results['syntax_check'] = True
    print("   ✓ All files have valid syntax")
except:
    print("   ✗ Some files have syntax errors")

# 2. Import Check
print("\n2. Import Resolution...")
try:
    output = subprocess.run(['python3', 'validate_imports.py'], 
                          capture_output=True, text=True, check=True)
    if 'All imports look valid' in output.stdout:
        results['import_check'] = True
        print("   ✓ All imports resolved")
    else:
        print("   ✗ Import issues remain")
except:
    print("   ✗ Import validation failed")

# 3. No Hyphenated Modules
print("\n3. Module Naming...")
hyphenated = list(Path('.').rglob('*-*.py'))
hyphenated = [f for f in hyphenated if '.backup' not in str(f)]
if not hyphenated:
    results['no_hyphenated_modules'] = True
    print("   ✓ No hyphenated module names")
else:
    print(f"   ✗ Still have {len(hyphenated)} hyphenated files")

# 4. Utils Functions Check
print("\n4. utils/functions.py Status...")
utils_file = Path('utils/functions.py')
if utils_file.exists():
    content = utils_file.read_text()
    if 'def __init__(' not in content and len(content.split('\n')) < 100:
        results['utils_functions_clean'] = True
        print("   ✓ utils/functions.py is clean")
    else:
        print("   ✗ utils/functions.py still has issues")

# 5. Critical Files Valid
print("\n5. Critical Files...")
critical_files = [
    'src/mcp_crafter.py',
    'demo_enhanced_orchestrator.py',
    'installers/install-mcp-system.py'
]
all_valid = True
for file_path in critical_files:
    try:
        compile(open(file_path).read(), file_path, 'exec')
        print(f"   ✓ {file_path}")
    except SyntaxError:
        print(f"   ✗ {file_path}")
        all_valid = False
results['critical_files_valid'] = all_valid

# Summary
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)

passed = sum(1 for v in results.values() if v)
total = len(results)

for check, passed in results.items():
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"{check:.<30} {status}")

print(f"\nOverall: {passed}/{total} checks passed")

if passed == total:
    print("\n🎉 SUCCESS! Codebase is ready for autofix tool!")
    sys.exit(0)
else:
    print("\n⚠️ WARNING: Some issues remain. Manual review recommended.")
    sys.exit(1)
```

### Step 6.2: Rollback Procedure (If Needed)

```bash
#!/bin/bash
# Save as: rollback.sh

if [ -z "$1" ]; then
    echo "Usage: ./rollback.sh <backup-directory>"
    echo "Available backups:"
    ls -la backups/
    exit 1
fi

backup_dir="$1"

if [ ! -d "$backup_dir" ]; then
    echo "Error: Backup directory not found: $backup_dir"
    exit 1
fi

echo "=== Rolling back from $backup_dir ==="
echo "This will overwrite current files. Continue? (y/n)"
read -r response

if [ "$response" = "y" ]; then
    rsync -av --delete \
        --exclude='.git' \
        --exclude='backups/' \
        "$backup_dir/" ./
    
    echo "✓ Rollback complete"
else
    echo "Rollback cancelled"
fi
```

---

## 📊 Success Criteria

### Must Pass Before Autofix
- [ ] Zero files with hyphenated names
- [ ] Zero syntax errors in Python files
- [ ] Zero imports from utils.functions
- [ ] All critical files compile successfully
- [ ] Backup created and verified

### Expected After Manual Fixes
```yaml
Syntax Errors: 0
Invalid Module Names: 0
Broken Imports: 0
Template Issues: 0
Orphaned Methods: 0
Risk Level: LOW (2/10)
Safe for Autofix: YES
```

### Time Breakdown
```yaml
Phase 1 (Module Renames): 10 minutes
Phase 2 (Template Fix): 5 minutes
Phase 3 (Utils Cleanup): 5 minutes
Phase 4 (Validation): 5 minutes
Phase 5 (Autofix): 10 minutes
Phase 6 (Verification): 5 minutes
Buffer Time: 5 minutes
Total: 45 minutes
```

---

## 🚨 Emergency Commands

If something goes wrong:

```bash
# Quick syntax check
find . -name "*.py" -exec python3 -m py_compile {} \; 2>&1 | grep -c "SyntaxError"

# Find what's broken
python3 -c "
import os, sys
for root, dirs, files in os.walk('.'):
    for f in files:
        if f.endswith('.py'):
            path = os.path.join(root, f)
            try:
                compile(open(path).read(), path, 'exec')
            except SyntaxError as e:
                print(f'{path}: {e.msg} at line {e.lineno}')
"

# Emergency rollback
rsync -av backups/pre-autofix-*/ ./ --exclude=backups/

# Reset git changes (nuclear option)
git checkout -- .
```

---

*End of Verbose Action Plan*