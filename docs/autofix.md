# MCP Autofix Tool - Enhanced with Higher Resolution Logic

Advanced, consolidated autofix tool with **higher resolution capabilities** that delivers precise, surgical code improvements using proven industry-standard tools with comprehensive error handling, detailed reporting, and configurable operation modes.

## ✨ ENHANCED FEATURES:

### 🔬 **Higher Resolution Capabilities (NEW)**
✅ **Granular Classification**: Issues categorized by complexity (critical/high/medium/low/cosmetic)  
✅ **Surgical Fix Precision**: Line-level targeting with minimal disruption  
✅ **Context-Aware Analysis**: Dependency graph analysis for intelligent fixes  
✅ **Advanced Validation**: Multi-level validation (syntax, imports, execution, safety)  
✅ **Precision Metrics**: Detailed impact analysis and confidence scoring  
✅ **Backup Registry**: Comprehensive backup management with metadata tracking  

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
✅ **High-Resolution Insights**: Precision metrics, complexity breakdown, dependency analysis  

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

Create an optional `autofix-config.json` file with enhanced resolution settings:

```json
{
  "black_line_length": 88,
  "target_python_version": "py38",
  "max_line_length": 88,
  "command_timeout": 300,
  "max_cycles": 10,
  "skip_hidden_files": true,
  "backup_enabled": true,
  "tools_required": ["black", "isort", "flake8", "mypy", "bandit"],
  
  "enable_high_resolution": true,
  "granular_classification": true,
  "line_level_precision": true,
  "context_aware_fixes": true,
  "advanced_validation": true,
  "detailed_reporting": true,
  "surgical_fix_mode": true,
  
  "similarity_threshold": 0.85,
  "complexity_threshold": 5,
  "dependency_depth": 3,
  "validation_levels": ["syntax", "imports", "execution", "safety"]
}
```

## 🐍 PYTHON API:

```python
from scripts.autofix import MCPAutofix, AutofixConfig
from pathlib import Path

# Basic usage with higher resolution
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

# Higher resolution specific operations
if autofix.config.enable_high_resolution:
    issues = [{'type': 'whitespace', 'file': 'test.py', 'line': 10}]
    categorized = autofix.analyze_issues_with_high_resolution(issues)
    surgical_success = autofix.apply_surgical_fix(issues[0])
    validation = autofix.validate_fix_with_high_resolution(Path('test.py'), issues[0])
```

## 📁 OUTPUT FILES:

```
autofix-reports/
├── autofix-report-{session_id}.json    # Comprehensive JSON report
├── autofix-summary-{session_id}.txt    # Human-readable summary
├── bandit-report-{session_id}.json     # Security vulnerability report
└── autofix-{session_id}.log            # Detailed execution log

.autofix_surgical_backups/              # Higher resolution backups
├── file1.py.{timestamp}.bak
├── file2.py.{timestamp}.bak
└── ...

# Additional analysis files (as needed)
flake8-report.txt                        # Style and error analysis
mypy-report.txt                          # Type checking results
test-results.txt                         # Test execution output
```

## 🔄 EXECUTION PHASES:

The enhanced autofix process runs in carefully orchestrated phases with higher resolution analysis:

1. **Environment Validation** - Verify Python version, file permissions, repository structure
2. **Tool Installation** - Install and verify required tools (black, isort, flake8, mypy, bandit)
3. **Higher Resolution Analysis** - Build dependency graph, analyze issue complexity
4. **High-Resolution Code Formatting** - Apply Black and isort with surgical precision
5. **Surgical Whitespace Cleanup** - Line-level whitespace fixes with validation
6. **Security Fixes** - Detect and fix security vulnerabilities using Bandit
7. **Function Resolution** - Resolve undefined functions through intelligent analysis
8. **Duplicate Elimination** - Consolidate duplicate code into shared utilities
9. **Type Error Fixes** - Add type annotations and fix type-related issues
10. **Test Failure Repairs** - Analyze and repair test failures
11. **Final Analysis** - Comprehensive security, quality, and test analysis
12. **Enhanced Report Generation** - Create detailed reports with higher resolution insights

## 🎯 HIGHER RESOLUTION FEATURES:

### **🔬 Granular Issue Classification**
- **Critical**: Complex security issues, core system changes
- **High**: Important functional changes, class modifications  
- **Medium**: Standard fixes, moderate complexity
- **Low**: Simple changes, basic improvements
- **Cosmetic**: Formatting, whitespace, style adjustments

### **⚡ Surgical Fix Precision**
- Line-level targeting with context validation
- Minimal disruption to surrounding code
- Fuzzy matching for content verification (80% similarity threshold)
- Automatic backup creation with metadata tracking

### **🧠 Context-Aware Analysis**
- Dependency graph construction for all Python files
- Impact analysis considering file importance
- Risk assessment based on change scope
- Confidence scoring for fix reliability

### **🛡️ Advanced Multi-Level Validation**
1. **Syntax Validation**: AST parsing verification
2. **Import Validation**: Import structure integrity  
3. **Execution Safety**: Dangerous pattern detection
4. **Safety Checks**: File size change monitoring, issue resolution verification

## 📈 SUCCESS METRICS:

After running enhanced autofix, expect:
- **Consistent formatting** across all Python files with surgical precision
- **Reduced security vulnerabilities** with specific fixes applied and validated
- **Improved code quality** through automated cleanup with minimal disruption
- **Better type safety** with enhanced annotations and context awareness
- **Consolidated code** with eliminated duplicates using intelligent analysis
- **Comprehensive documentation** of all changes with higher resolution insights
- **Precision metrics** showing surgical fix ratios and validation success rates

## 🔧 INTEGRATION:

This enhanced tool integrates seamlessly with:
- **MCP Pipeline System** - Part of the larger MCP ecosystem with higher resolution reporting
- **CI/CD Workflows** - Can be run in automated pipelines with precision metrics
- **Pre-commit Hooks** - Use for automatic code quality enforcement with surgical fixes
- **Development Workflows** - Regular maintenance and cleanup with minimal disruption

## 🚨 SAFETY GUARANTEES:

- **Syntax Validation**: All changes are AST-validated before writing
- **Surgical Backup Creation**: Original files preserved with metadata and timestamps
- **Error Isolation**: Failed phases don't affect successful ones
- **Dry Run Mode**: Always test with `--dry-run` first
- **Detailed Logging**: Complete audit trail of all operations
- **Graceful Degradation**: Continues operation even if some tools fail
- **Higher Resolution Validation**: Multi-level validation ensures fix quality
- **Impact Analysis**: Risk assessment prevents dangerous changes

This enhanced autofix tool with **higher resolution logic** represents a significant advancement in automated code maintenance, providing enterprise-grade reliability, surgical precision, and comprehensive coverage of code quality issues with minimal disruption to existing codebases.
