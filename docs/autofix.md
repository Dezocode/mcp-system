# MCP Autofix Tool - Consolidated Automated Fixing System

Advanced, consolidated autofix tool that delivers reliable code improvements using proven industry-standard tools with comprehensive error handling, detailed reporting, and configurable operation modes.

## ✨ ENHANCED FEATURES:

### 🎯 **Core Capabilities**
✅ **Code Formatting**: Uses `black` and `isort` for consistent formatting  
✅ **Security Analysis**: Uses `bandit` for vulnerability detection and automated fixes  
✅ **Quality Analysis**: Uses `flake8` and `mypy` for style and type checking  
✅ **Whitespace Cleanup**: Automated whitespace and formatting fixes with backup creation  
✅ **Function Resolution**: Intelligent undefined function detection and resolution  
✅ **Duplicate Elimination**: Smart duplicate code detection and consolidation  
✅ **Type Error Fixes**: Automated type annotation and error corrections  
✅ **Test Integration**: Runs existing pytest or unittest tests with failure analysis  
✅ **Comprehensive Reporting**: Detailed JSON reports and human-readable summaries  

### 🛡️ **Safety & Reliability**
✅ **AST Validation**: All Python code changes are syntax-validated before writing  
✅ **Backup Creation**: Automatic backup files with session IDs  
✅ **Error Recovery**: Graceful error handling with detailed logging  
✅ **Dry Run Mode**: Preview all changes before applying  
✅ **Phase Isolation**: Each fix phase runs independently with error isolation  
✅ **Timeout Protection**: Built-in command timeouts and resource management  

### 📊 **Advanced Reporting**
✅ **Session Tracking**: Unique session IDs for each autofix run  
✅ **Execution Analytics**: Detailed timing and performance metrics  
✅ **Issue Categorization**: Security, quality, type, and test issue classification  
✅ **Recommendations**: Smart recommendations based on findings  
✅ **Multiple Formats**: JSON reports + human-readable summaries  

## 🚀 COMMAND USAGE:

```bash
# Basic usage
./run-autofix

# Preview changes without applying (recommended first run)
./run-autofix --dry-run --verbose

# Use custom configuration
./run-autofix --config-file autofix-config.json

# Specific operations
./run-autofix --format-only          # Only code formatting
./run-autofix --security-only        # Only security analysis and fixes  
./run-autofix --scan-only            # Analysis only, no fixes applied

# Advanced options
./run-autofix --no-backup            # Disable backup file creation
./run-autofix --session-id my-fix    # Custom session identifier
```

## ⚙️ CONFIGURATION:

Create an optional `autofix-config.json` file:

```json
{
  "black_line_length": 88,
  "target_python_version": "py38",
  "max_line_length": 88,
  "command_timeout": 300,
  "max_cycles": 10,
  "skip_hidden_files": true,
  "backup_enabled": true,
  "tools_required": ["black", "isort", "flake8", "mypy", "bandit"]
}
```

## 🐍 PYTHON API:

```python
from scripts.autofix import MCPAutofix, AutofixConfig
from pathlib import Path

# Basic usage
autofix = MCPAutofix(dry_run=False, verbose=True)
results = autofix.run_complete_autofix()
print(f"Applied {autofix.fixes_applied} fixes")

# With custom configuration
config_file = Path("autofix-config.json")
autofix = MCPAutofix(
    repo_path=Path("/path/to/repo"),
    config_file=config_file,
    dry_run=True
)
results = autofix.run_complete_autofix()

# Specific operations
autofix.fix_code_formatting()           # Format code only
autofix.run_security_scan()             # Security scan only
autofix.fix_security_issues()           # Security fixes only
```

## 📁 OUTPUT FILES:

```
autofix-reports/
├── autofix-report-{session_id}.json    # Comprehensive JSON report
├── autofix-summary-{session_id}.txt    # Human-readable summary
├── bandit-report-{session_id}.json     # Security vulnerability report
└── autofix-{session_id}.log            # Detailed execution log

# Additional analysis files (as needed)
flake8-report.txt                        # Style and error analysis
mypy-report.txt                          # Type checking results
test-results.txt                         # Test execution output
```

## 🔄 EXECUTION PHASES:

The autofix process runs in carefully orchestrated phases:

1. **Environment Validation** - Verify Python version, file permissions, repository structure
2. **Tool Installation** - Install and verify required tools (black, isort, flake8, mypy, bandit)
3. **Code Formatting** - Apply Black and isort formatting with validation
4. **Whitespace Cleanup** - Fix whitespace issues with encoding detection and backups
5. **Security Fixes** - Detect and fix security vulnerabilities using Bandit
6. **Function Resolution** - Resolve undefined functions through intelligent analysis
7. **Duplicate Elimination** - Consolidate duplicate code into shared utilities
8. **Type Error Fixes** - Add type annotations and fix type-related issues
9. **Test Failure Repairs** - Analyze and repair test failures
10. **Final Analysis** - Comprehensive security, quality, and test analysis
11. **Report Generation** - Create detailed reports with recommendations

## 🎯 INTELLIGENT FEATURES:

### **Smart Function Resolution**
- Typo detection using Levenshtein distance
- Missing import detection from standard library
- Stub generation for missing functions with TODO markers

### **Advanced Security Fixes**
- Subprocess shell=True to shell=False conversion
- Hardcoded password to environment variable migration
- YAML safe_load() implementation
- Comprehensive vulnerability pattern matching

### **Code Quality Improvements**
- AST-based duplicate function detection
- Intelligent consolidation to shared modules
- Type annotation inference and addition
- Import organization and cleanup

## 📈 SUCCESS METRICS:

After running autofix, expect:
- **Consistent formatting** across all Python files
- **Reduced security vulnerabilities** with specific fixes applied
- **Improved code quality** through automated cleanup
- **Better type safety** with enhanced annotations
- **Consolidated code** with eliminated duplicates
- **Comprehensive documentation** of all changes made

## 🔧 INTEGRATION:

This tool integrates seamlessly with:
- **MCP Pipeline System** - Part of the larger MCP ecosystem
- **CI/CD Workflows** - Can be run in automated pipelines
- **Pre-commit Hooks** - Use for automatic code quality enforcement
- **Development Workflows** - Regular maintenance and cleanup

## 🚨 SAFETY GUARANTEES:

- **Syntax Validation**: All changes are AST-validated before writing
- **Backup Creation**: Original files are preserved with session tracking
- **Error Isolation**: Failed phases don't affect successful ones
- **Dry Run Mode**: Always test with `--dry-run` first
- **Detailed Logging**: Complete audit trail of all operations
- **Graceful Degradation**: Continues operation even if some tools fail

This enhanced autofix tool represents a significant improvement in automated code maintenance, providing enterprise-grade reliability and comprehensive coverage of code quality issues.
