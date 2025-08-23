# CLAUDE.md - MCP Pipeline Integration Expert Configuration

## 🚨 CRITICAL PIPELINE CONSTRAINTS

### LINE-LEVEL EDITING MANDATE
- **NEVER** make changes without using Read tool first
- **ALWAYS** use Edit/MultiEdit tools for precise line-level changes
- **PRESERVE** exact indentation, whitespace, and formatting
- **VALIDATE** syntax after every edit
- **BACKUP** awareness - system creates automatic backups

### REACT FRAMEWORK INTEGRATION
- React components in `/utils/paste-to-claude.js` and `/utils/claude-userscript.js`
- Use `nativeInputValueSetter` pattern for React state updates
- Dispatch both 'input' and 'change' events for React compatibility
- Handle contentEditable elements with ProseMirror awareness

## 🔄 AUTO-CYCLING PIPELINE VALIDATION

### Pipeline Entry Points
```bash
./run-pipeline                    # Master orchestrator
python3 scripts/version_keeper.py --claude-lint
python3 scripts/claude_quality_patcher.py --continuous-rerun
```

### Validation Cycle Requirements
1. **Read target file** using Read tool
2. **Identify exact issue** at specified line number
3. **Apply minimal fix** using Edit/MultiEdit tool
4. **Verify syntax** - system validates automatically
5. **Confirm completion** - pipeline advances to next fix

### Auto-Cycling Until Clean
- Target: **0 issues remaining** across all categories
- Categories: Security, Quality, Duplicates, Connections, Style
- Max cycles: 999 or until complete
- Pipeline publishes development branch when clean

## 🛡️ SECURITY & QUALITY CONSTRAINTS

### Security Fixes (Priority 1)
- Subprocess hardening: Use absolute paths, validated args, timeouts
- Input validation: Sanitize all user inputs
- Shell command safety: Always use `shell=False`
- Error handling: Proper exception management

### Quality Fixes (Priority 2-4)
- Remove duplicate functions across files
- Fix broken imports and references
- Standardize code style and documentation
- Performance optimizations

## 🎯 PIPELINE OPERATION MODES

### Mode 1: Version Keeper Linting
```python
# Command pattern
python3 scripts/version_keeper.py --claude-lint --detect-duplicates --check-connections --output-format=json
```

### Mode 2: Quality Patcher Continuous
```python
# Command pattern  
python3 scripts/claude_quality_patcher.py --continuous-rerun --publish-pipeline --auto-apply
```

### Mode 3: Integration Loop
```python
# Command pattern
python3 scripts/claude_code_integration_loop.py --max-cycles=999 --process-all-fixes
```

## 🔧 EXPERT EDITING PATTERNS

### MultiEdit for Complex Changes
```python
# Use when making multiple changes to same file
MultiEdit(
    file_path="/absolute/path/to/file.py",
    edits=[
        {"old_string": "exact_text_to_replace", "new_string": "fixed_text"},
        {"old_string": "another_exact_match", "new_string": "another_fix"}
    ]
)
```

### Edit for Single Changes
```python
# Use for single line/section changes
Edit(
    file_path="/absolute/path/to/file.py", 
    old_string="def vulnerable_function():",
    new_string="def secure_function():"
)
```

## 📊 STATE MANAGEMENT INTEGRATION

### Pipeline State Files
- `.mcp-pipeline-state.json` - Current execution state
- `pipeline-sessions/` - Session-specific data
- `configs/pipeline-state.json` - Configuration state

### JSON Output Format
```json
{
  "timestamp": "2025-01-21T12:00:00Z",
  "session_id": "session-12345", 
  "summary": {
    "total_issues": 0,
    "fixes_applied": 875,
    "remaining_issues": 0,
    "success_rate": 100.0
  },
  "performance": {
    "execution_time": 3600,
    "files_processed": 45,
    "cycles_completed": 3
  }
}
```

## 🚀 DEVELOPMENT BRANCH PUBLISHING

### Automatic Triggers
- Activated when **all issues = 0**
- Creates timestamped development branch
- Applies comprehensive commit message
- Pushes to remote repository
- Updates version numbers and tags

### Success Criteria
```bash
✅ Security Issues: 0
✅ Critical Errors: 0  
✅ Quality Issues: 0
✅ Code Duplicates: 0
✅ Connection Issues: 0
✅ Development branch: published
✅ Version: bumped and tagged
```

## 🔄 CONTINUOUS MONITORING

### Real-Time Validation
- File change detection every 30 seconds
- Memory and disk usage tracking  
- Process monitoring with timeout management
- Automatic error detection and recovery

### Guardrail System
- Quality patcher monitors ALL file changes
- Backup creation before each fix attempt
- Syntax validation after modifications
- Pipeline resumption after successful fixes

## 💡 BEST PRACTICES

### Before Making Changes
1. Use Read tool to understand current state
2. Identify exact line numbers and text to change
3. Plan minimal, surgical modifications
4. Consider impact on surrounding code

### During Editing
1. Preserve existing functionality
2. Maintain code style consistency
3. Follow security best practices
4. Keep changes focused and minimal

### After Changes
1. Verify syntax is valid
2. Check that fix addresses specific issue
3. Allow pipeline to validate automatically
4. Monitor for successful advancement

## ⚡ CRITICAL SUCCESS FACTORS

### Line-Level Precision
- Match exact whitespace and indentation
- Use absolute file paths only
- Preserve comment formatting
- Maintain import order and structure

### Pipeline Cooperation
- Trust the guardrail system
- Allow automatic backup creation
- Let pipeline validate changes
- Follow fix prioritization order

### Auto-Cycling Discipline  
- Process one fix at a time
- Complete each fix fully before advancing
- Use tools correctly (Read then Edit)
- Maintain focus on zero remaining issues

---

**REMEMBER**: You are the active worker in a sophisticated pipeline. The system coordinates, validates, and advances - you apply the precise fixes using proper tools with line-level accuracy until all issues are resolved and the development branch is automatically published.