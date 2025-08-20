# 🎯 CODEMAP TOOL - Comprehensive Function-Level Dependency Analysis System

## Overview

The **CODEMAP Tool** is an advanced AI-enforced system that generates comprehensive function-level dependency graphs at or above the quality level of `chrome-container-dependency-graph.svg`. It forces AI assistants to perform detailed end-to-end code analysis through automated hook triggers.

## 🚀 Features

### Core Capabilities
- **Comprehensive Function Mapping**: Every JavaScript function with line numbers
- **End-to-End Connection Tracing**: HTML elements → Frontend JS → IPC → Backend JS → Services  
- **Missing Handler Detection**: Identifies broken connections and orphaned functions
- **Visual Excellence**: 4000x3000px SVG with color-coded layers and relationship arrows
- **Automated AI Enforcement**: Hook system forces thorough analysis

### Visual Elements
- **Multi-layer Architecture**: HTML, Frontend JS, IPC Bridge, Backend Services
- **Color-Coded Components**: Different gradients for file types and connection states
- **Relationship Arrows**: Labeled connections showing data flow and call chains
- **Critical Issue Highlighting**: RED markers for missing/broken connections
- **Comprehensive Legend**: Explains all visual elements and connection types

## 🔧 Installation & Configuration

### Hook System (Already Configured)
The tool is automatically activated through Claude Code hooks in `~/.claude/settings.json`:

```json
{
  "hooks": {
    "UserPromptSubmit": "Activates on dependency analysis requests",
    "PostToolUse": "Triggers after Task tool usage or code file reading", 
    "Stop": "Validates completion and checks template status",
    "PreToolUse": "Monitors CODEMAP SVG modifications",
    "SessionStart": "Displays tool availability and status"
  }
}
```

### Scripts Location
- **Main Tool**: `~/.claude/scripts/code-map.sh`
- **Validator**: `~/.claude/scripts/validate-codemap.sh` 
- **Documentation**: `~/.claude/CODEMAP-README.md`

## 🎯 Usage

### Automatic Activation
The tool automatically activates when you use keywords like:
- "code map" or "dependency graph"
- "analyze code" or "function map" 
- "comprehensive analysis"
- After using Task tool in projects with code files
- When reading JavaScript/HTML/CSS files

### Manual Activation
```bash
# Direct execution
~/.claude/scripts/code-map.sh

# With validation
~/.claude/scripts/code-map.sh && ~/.claude/scripts/validate-codemap.sh
```

### Example Commands
- "Generate a comprehensive code map"
- "Create dependency graph for this project"
- "Analyze all functions with line numbers"
- "Map end-to-end connections"

## 📊 Output Structure

### File Output
- **Location**: `CODEMAP-DEPENDENCY-GRAPH.svg` in project root
- **Size**: 4000x3000px minimum
- **Format**: Valid XML/SVG with embedded CSS

### Required Sections
1. **Layer 1**: HTML files and interactive elements
2. **Layer 2**: Frontend JavaScript functions
3. **Layer 3**: IPC communication bridge
4. **Layer 4**: Backend services and core functions
5. **Critical Requirements**: Analysis mandate section
6. **Validation Checklist**: Completion verification
7. **Legend**: Comprehensive visual guide

### Visual Standards
- **Function Nodes**: Circle/rectangle shapes with line numbers
- **Connection Arrows**: Labeled with relationship types
- **Color Coding**: Gradients for HTML, JS, IPC, Backend, Critical
- **Missing Handlers**: RED highlighting for broken connections
- **Layer Separation**: Clear visual boundaries between architecture layers

## ⚠️ AI Requirements

### Mandatory Analysis Elements
The AI **MUST** replace template sections with:

1. **All JavaScript Functions**
   - Extract every function from all `.js` files
   - Include accurate line numbers (`functionName() L:123`)
   - Map function-to-function call chains
   - Identify async/await patterns and callbacks

2. **HTML Element Mapping**
   - All elements with IDs and event handlers
   - onclick, addEventListener, form submissions
   - Button clicks and user interactions
   - Connection to corresponding JavaScript functions

3. **IPC Communication Paths**
   - preload.js electronAPI bridges
   - ipcMain.handle and ipcRenderer.invoke calls
   - Missing handler identification
   - Request/response flow mapping

4. **Backend Service Integration**
   - Core application services and utilities
   - File system operations and external API calls
   - Chrome browser control functions
   - Terminal/PTY manager operations

5. **Dependency Chain Validation**
   - Complete end-to-end path verification
   - Broken connection identification (RED markers)
   - Orphaned function detection
   - Import/require resolution validation

### Completion Criteria
The analysis is complete only when:
- ✅ All template placeholders are replaced with actual data
- ✅ Every JavaScript function includes line numbers
- ✅ All connection arrows have valid source and target
- ✅ Missing handlers are identified and marked in RED
- ✅ End-to-end paths are fully traceable
- ✅ Validation checklist shows 90%+ completion

## 🔍 Validation System

### Automatic Validation
The `validate-codemap.sh` script checks:
- Function line number presence
- Layer structure completeness
- Connection arrow implementation
- JavaScript function mapping
- HTML element integration
- IPC handler coverage
- Backend service mapping
- Missing connection identification
- Color coding implementation
- Legend comprehensiveness

### Scoring System
- **90-100%**: Excellent - Meets comprehensive standards
- **70-89%**: Good - Mostly complete, minor improvements needed
- **50-69%**: Poor - Significant improvement required
- **Below 50%**: Failed - Comprehensive AI analysis required

### Status Messages
- ✅ **Complete Analysis**: All requirements met
- ⚠️ **Template Detected**: AI analysis still required
- ❌ **Validation Failed**: Major issues found

## 🎨 Quality Standards

### Reference Level
The output must meet or exceed the quality of:
`chrome-container-dependency-graph.svg`

### Required Features
- **Professional Appearance**: Clean, organized layout
- **Comprehensive Coverage**: No missing functions or connections
- **Clear Relationships**: Obvious connection paths and data flow
- **Error Identification**: Broken connections clearly marked
- **Documentation**: Self-explanatory with comprehensive legend

### Technical Requirements
- Valid XML/SVG structure
- Embedded CSS for styling
- Proper viewBox and dimensions
- Accessible color schemes
- Scalable vector graphics

## 🚨 Common Issues & Solutions

### Issue: Template Not Replaced
**Problem**: AI generates template without actual analysis
**Solution**: Explicitly request "comprehensive function analysis" and reference specific files

### Issue: Missing Function Line Numbers
**Problem**: Functions mapped without line numbers
**Solution**: Request "include line numbers for all functions"

### Issue: Incomplete Connection Mapping
**Problem**: Arrows without valid source/target
**Solution**: Demand "end-to-end path verification" and "complete connection validation"

### Issue: No Missing Handler Identification
**Problem**: Broken connections not highlighted
**Solution**: Request "identify all missing IPC handlers in RED"

## 📈 Best Practices

### For Users
1. **Be Specific**: Request "comprehensive function-level analysis"
2. **Demand Completeness**: Ask for "every JavaScript function with line numbers"
3. **Require Validation**: Request "end-to-end connection verification"
4. **Check Output**: Verify template sections are replaced with actual data

### For AI Implementation
1. **Read All Code Files**: Analyze every `.js`, `.html`, `.css` file
2. **Extract Every Function**: Include line numbers and call chains
3. **Map All Connections**: HTML → JS → IPC → Backend
4. **Identify Gaps**: Mark missing handlers in RED
5. **Validate Completeness**: Ensure 90%+ validation score

## 🔄 Hook Trigger Details

### UserPromptSubmit Hook
Activates when prompt contains dependency analysis keywords

### PostToolUse Hooks
- **Task Tool**: Triggers after agent usage in projects with code files
- **Read/Grep/Glob**: Activates when analyzing code files

### Stop Hook
Validates CODEMAP status and provides guidance for incomplete analysis

### PreToolUse Hook
Monitors CODEMAP SVG modifications to ensure quality

### SessionStart Hook
Displays tool availability and status on session initialization

## 🎯 Success Metrics

### Quantitative Measures
- **Function Coverage**: 100% of JavaScript functions mapped
- **Connection Accuracy**: All arrows have valid endpoints
- **Line Number Precision**: Every function includes exact location
- **Missing Handler Count**: All broken connections identified

### Qualitative Assessment
- **Visual Clarity**: Professional, organized appearance
- **Comprehensive Coverage**: No significant gaps in analysis
- **Actionable Insights**: Clear identification of issues
- **Documentation Quality**: Self-explanatory with detailed legend

## 🛠️ Troubleshooting

### Hook Not Triggering
1. Verify settings.json syntax with `claude --validate-hooks`
2. Restart Claude Code to reload hook configuration
3. Use explicit trigger phrases in prompts

### Script Execution Errors
1. Check script permissions: `chmod +x ~/.claude/scripts/code-map.sh`
2. Verify PROJECT_ROOT environment variable
3. Review error logs in `/tmp/codemap-*/codemap.log`

### Incomplete Analysis
1. Request specific function mapping
2. Demand line number inclusion
3. Require missing handler identification
4. Validate with `~/.claude/scripts/validate-codemap.sh`

## 📞 Support

### Tool Location
- **Scripts**: `~/.claude/scripts/`
- **Configuration**: `~/.claude/settings.json`
- **Documentation**: `~/.claude/CODEMAP-README.md`
- **Output**: `$PROJECT_ROOT/CODEMAP-DEPENDENCY-GRAPH.svg`

### Validation Commands
```bash
# Check hook status
claude --hooks

# Validate CODEMAP output
~/.claude/scripts/validate-codemap.sh

# Manual tool execution
~/.claude/scripts/code-map.sh
```

---

**Generated by CODEMAP Tool v2.0** - AI-Enforced Comprehensive Function-Level Dependency Analysis System