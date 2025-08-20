# /prep Command - MANDATORY PREPARATION PROTOCOL WITH HOOK ENFORCEMENT

## Command: `/prep`

## Description:
Executes mandatory preparation protocol before ANY chrome-container-app code changes. Creates timestamped trace snowball report, runs all required verification checks, and configures hooks to enforce trace documentation for ALL file operations.

## Execution Sequence:

### 1. **READ MANDATORY FILES** (In Order)
```bash
# Files to read immediately:
1. /Users/dezmondhollins/my-web-app/CLAUDE.md
2. /Users/dezmondhollins/my-web-app/DOM-EXPECTED-FUNCTIONS-COMPLETE.md  
3. /Users/dezmondhollins/my-web-app/my-web-app-architecture.md
4. /Users/dezmondhollins/my-web-app/CHROME-CONTAINER-DEVELOPMENT-SOP.md
5. /Users/dezmondhollins/my-web-app/apps/chrome-container/chrome-container-app/PRETTIER-LANGEXTRACT-SOP.md
6. /Users/dezmondhollins/my-web-app/MANDATORY-PREP-TEMPLATE.md
```

### 2. **CREATE TIMESTAMPED REPORT**
```bash
# Generate Chicago timestamp
TIMESTAMP=$(TZ=America/Chicago date '+%Y%m%d-%H%M%S-CST')
REPORT_FILE="TRACE-${TIMESTAMP}-[FEATURE].md"

# Create report with mandatory template
cp MANDATORY-PREP-TEMPLATE.md $REPORT_FILE
```

### 3. **RUN MANDATORY GREP VERIFICATION**
```bash
# Check for violations BEFORE starting
grep -rn "TODO\|FIXME\|PLACEHOLDER" apps/chrome-container/chrome-container-app/
grep -rn "console\.log" apps/chrome-container/chrome-container-app/ | grep -v "traceDebug"
grep -rn "execute_script" apps/chrome-container/chrome-container-app/

# Check for duplicates
grep -rn "function.*same.*name" apps/chrome-container/chrome-container-app/ --include="*.js"

# Verify trace coverage
grep -c "traceDebug" apps/chrome-container/chrome-container-app/renderer/app.js

# Check prettier compliance
npx prettier --check apps/chrome-container/chrome-container-app/
```

### 4. **POPULATE TEMPLATE WITH RESULTS**
- Fill in actual grep outputs (no placeholders)
- Add Chicago timestamps to all sections
- Create mermaid diagram for directory trace
- Define snowball action chain with trace points

### 5. **VERIFICATION GATES**
```bash
# GATE 1: No violations found
if [ violations_found ]; then
    echo "🚨 VIOLATIONS DETECTED - TASK BLOCKED"
    echo "Fix violations before proceeding"
    exit 1
fi

# GATE 2: Dependencies verified
if [ ! -f "package.json" ]; then
    echo "🚨 MISSING DEPENDENCIES - TASK BLOCKED"
    exit 1
fi

# GATE 3: Chrome container scope confirmed
if [ touching_website_files ]; then
    echo "🚨 SCOPE VIOLATION - Chrome Container ONLY"
    exit 1
fi
```

### 6. **CONFIGURE ENFORCEMENT HOOKS**
```bash
# Create/update hooks in ~/.claude/settings.json
# These hooks ENFORCE trace snowball documentation for EVERY operation
```

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "if [ ! -f TRACE-*-CST-*.md ] || ! grep -q 'MANDATORY GREP' TRACE-*-CST-*.md 2>/dev/null; then echo '🚨 BLOCKED: No trace snowball documentation found! Run /prep first'; cat /Users/dezmondhollins/my-web-app/CLAUDE.md | head -50; exit 2; fi",
            "timeout": 10
          },
          {
            "type": "command",
            "command": "echo '📋 Verifying trace documentation...' && grep -c 'ACTUAL RESULT' TRACE-*-CST-*.md 2>/dev/null || (echo '❌ Missing grep results in trace'; exit 2)",
            "timeout": 5
          }
        ]
      },
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "echo '$1' | grep -E 'rm |rm -|delete|remove' && ([ -f TRACE-*-CST-*.md ] || (echo '🚨 BLOCKED: rm/delete requires trace documentation'; exit 2))",
            "timeout": 5
          }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "echo '📖 Loading mandatory rules...' && head -20 /Users/dezmondhollins/my-web-app/CLAUDE.md && head -20 /Users/dezmondhollins/my-web-app/CHROME-CONTAINER-DEVELOPMENT-SOP.md",
            "timeout": 5
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Write|Edit|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "echo '✅ Updating trace report...' && echo '## Change Applied: '$(date '+%Y-%m-%d %H:%M:%S CST') >> TRACE-*-CST-*.md 2>/dev/null",
            "timeout": 5
          },
          {
            "type": "command",
            "command": "npx prettier --check . 2>/dev/null || echo '⚠️ Prettier violations detected'",
            "timeout": 30
          },
          {
            "type": "command",
            "command": "grep -rn 'TODO\|FIXME\|PLACEHOLDER' apps/chrome-container/chrome-container-app/ 2>/dev/null && echo '🚨 PLACEHOLDERS FOUND - VIOLATION'",
            "timeout": 10
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "echo '📊 Final compliance check...' && grep -c 'traceDebug' apps/chrome-container/chrome-container-app/renderer/app.js 2>/dev/null || echo 'Warning: Low trace coverage'",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

### 7. **FINAL PREP OUTPUT**
```markdown
## ✅ PREP PROTOCOL COMPLETE

**Report Created:** TRACE-[TIMESTAMP]-[FEATURE].md
**Violations Found:** 0
**Ready for Implementation:** YES

### Next Steps:
1. Review the populated trace report
2. Confirm all grep results are acceptable
3. Begin implementation following snowball chain
4. Update trace report as you progress
5. Run verification after each step
```

## Usage Example:

```
User: /prep
Claude: 
🎯 EXECUTING MANDATORY PREP PROTOCOL WITH HOOK ENFORCEMENT
📅 Timestamp: 2025-08-09 00:45:00 CST

📖 Reading mandatory files...
✅ CLAUDE.md loaded (anti-optimism protocol - 1,122 file disaster prevention)
✅ DOM-EXPECTED-FUNCTIONS-COMPLETE.md loaded (element templates)
✅ my-web-app-architecture.md loaded (file placement rules)
✅ CHROME-CONTAINER-DEVELOPMENT-SOP.md loaded (development protocol)
✅ PRETTIER-LANGEXTRACT-SOP.md loaded (code quality enforcement)
✅ MANDATORY-PREP-TEMPLATE.md loaded (trace template)

📝 Creating trace report: TRACE-20250809-004500-CST-PENDING.md

🔍 Running mandatory grep verification...
- Checking for violations... NONE FOUND ✅
- Checking for duplicates... NONE FOUND ✅
- Verifying trace coverage... 85% (ACCEPTABLE) ✅
- Checking prettier compliance... FORMATTED ✅
- Checking string usage... REVIEWED ✅

🔧 Configuring enforcement hooks...
✅ PreToolUse hooks: Block Write/Edit without trace documentation
✅ PreToolUse hooks: Block rm/delete without trace documentation
✅ UserPromptSubmit hooks: Auto-load CLAUDE.md and SOP rules
✅ PostToolUse hooks: Auto-update trace reports
✅ Stop hooks: Final compliance verification

⚡ HOOK ENFORCEMENT ACTIVE:
- Any Write/Edit/MultiEdit will be BLOCKED without trace report
- Any rm/delete commands will be BLOCKED without documentation
- CLAUDE.md and SOP rules will be loaded on every prompt
- Violations will trigger immediate task termination

✅ PREP COMPLETE - Ready for implementation
📋 Trace report created: TRACE-20250809-004500-CST-PENDING.md
🔒 Hook protection enabled: All operations require trace documentation

Please specify the feature/bug to work on.
```

## Error Handling:

### If violations found:
```
🚨 PREP FAILED - VIOLATIONS DETECTED

Found 3 TODO placeholders:
- renderer/app.js:142 // TODO: implement this
- renderer/app.js:256 // TODO: fix later
- src/ipc/handlers.js:89 // FIXME: temporary

❌ TASK BLOCKED - Remove all placeholders before proceeding
```

### If duplicates found:
```
🚨 PREP FAILED - DUPLICATES DETECTED

Found duplicate functions:
- processData() in app.js:45 and app.js:189
- validateInput() in utils.js:12 and helpers.js:34

❌ TASK BLOCKED - Remove duplicates before proceeding
```

### If scope violation:
```
🚨 PREP FAILED - SCOPE VIOLATION

Attempting to modify website files:
- public/index.html (FORBIDDEN - website file)
- public/js/theme.js (FORBIDDEN - not chrome container)

❌ TASK BLOCKED - Chrome Container scope ONLY
```

## Mandatory Rules Enforced Through Hooks:

### **PreToolUse Hooks (BLOCKING):**
1. **Write/Edit/MultiEdit BLOCKED** without trace snowball documentation
2. **rm/delete commands BLOCKED** without trace documentation
3. **Missing grep results BLOCKS** all file operations
4. **No TRACE-*-CST-*.md file BLOCKS** all changes

### **UserPromptSubmit Hooks (CONTEXT):**
5. **Auto-loads CLAUDE.md** rules on every prompt
6. **Auto-loads CHROME-CONTAINER-DEVELOPMENT-SOP.md** on every prompt
7. **Reminds of 1,122 file disaster** and 472 violations

### **PostToolUse Hooks (VERIFICATION):**
8. **Auto-checks prettier compliance** after every edit
9. **Auto-scans for placeholders** (TODO, FIXME, PLACEHOLDER)
10. **Auto-updates trace report** with timestamps

### **Stop Hooks (FINAL CHECK):**
11. **Verifies trace coverage** in app.js
12. **Final compliance report** generated

### **Core Mandates:**
- **NO new file creation** (edit existing only)
- **NO placeholders** (TODO, FIXME, PLACEHOLDER)
- **REVIEW string usage** (ensure appropriate handling)
- **NO console.log** without traceDebug
- **NO execute_script()** usage
- **NO website integration** (chrome-container only)
- **MANDATORY grep verification** before starting
- **MANDATORY Chicago timestamps** throughout
- **MANDATORY trace debugging** for all interactions
- **MANDATORY prettier** compliance

## Success Criteria:

The /prep command succeeds when:
- ✅ All mandatory files read
- ✅ Trace report created with timestamp
- ✅ Zero violations found in grep checks
- ✅ Template populated with actual results
- ✅ All verification gates passed
- ✅ Ready for implementation confirmed

## Command Aliases:
- `/prep` - Full preparation protocol
- `/prepare` - Same as /prep
- `/pre` - Same as /prep

## Related Commands:
- `/verify` - Run verification checks only
- `/trace` - Create trace report only
- `/validate` - Final validation after implementation
- `/hooks` - View currently active hooks

## Hook Management:

### To Enable Hooks:
```bash
# The /prep command automatically configures hooks
# Hooks persist across sessions until disabled
```

### To Verify Hooks Are Active:
```bash
/hooks
# Should show PreToolUse, PostToolUse, UserPromptSubmit, and Stop hooks
```

### To Temporarily Disable (NOT RECOMMENDED):
```bash
# Edit ~/.claude/settings.json and remove hooks section
# WARNING: This removes protection against violations
```

## Trace Snowball Documentation Requirements:

Every file operation MUST have a corresponding trace report with:
1. **Timestamp**: [YYYY-MM-DD HH:MM:SS CST] format
2. **Grep Evidence**: ACTUAL command outputs (no placeholders)
3. **Mermaid Diagram**: Directory trace showing file flow
4. **Snowball Chain**: Step-by-step actions with trace points
5. **Compliance Checks**: Architecture and CLAUDE.md rules verified
6. **Screenshots**: Before/after evidence
7. **Function Tracing**: End-to-end verification

## Why Hooks Are Mandatory:

Based on ACTUAL FAILURES documented in CLAUDE.md:
- **1,122 unnecessary files created** → Hooks prevent file creation
- **472 security violations** → Hooks enforce security checks
- **91% audit failure rate** → Hooks ensure compliance
- **SNAPE false success claims** → Hooks require evidence
- **Systematic rule violations** → Hooks block violations

These hooks are NOT optional - they prevent catastrophic failures.