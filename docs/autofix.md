# MCP Autofix Tool - Consolidated Automated Fixing System

Single, consolidated autofix tool that delivers reliable code improvements using proven industry-standard tools.

## COMMAND USAGE:
```bash
./run-autofix [OPTIONS]
```

## FEATURES:
✅ **Code Formatting**: Uses `black` and `isort` for consistent formatting  
✅ **Security Analysis**: Uses `bandit` for security vulnerability detection  
✅ **Quality Analysis**: Uses `flake8` and `mypy` for style and type checking  
✅ **Whitespace Cleanup**: Automated whitespace and basic formatting fixes  
✅ **Test Integration**: Runs existing pytest or unittest tests  
✅ **Comprehensive Reporting**: Detailed JSON and text reports  

## OPTIONS:
- `--repo-path PATH`: Repository path (default: current directory)
- `--dry-run`: Show what would be fixed without applying changes
- `--verbose`: Show detailed output
- `--format-only`: Only run code formatting
- `--scan-only`: Only run analysis without fixes

## USAGE EXAMPLES:
```bash
# Run complete autofix
./run-autofix

# Dry run to preview changes
./run-autofix --dry-run --verbose

# Format code only
./run-autofix --format-only

# Analysis only (no fixes)
./run-autofix --scan-only
```

## PYTHON API:
```python
from scripts.autofix import MCPAutofix

autofix = MCPAutofix(dry_run=False, verbose=True)
results = autofix.run_complete_autofix()
print(f"Applied {autofix.fixes_applied} fixes")
```

## OUTPUT FILES:
- `autofix-report.json`: Comprehensive results summary
- `bandit-report.json`: Security vulnerability report  
- `flake8-report.txt`: Style and error analysis
- `mypy-report.txt`: Type checking results
- `test-results.txt`: Test execution output

## SAFETY FEATURES:
- **AST Validation**: All Python code changes are syntax-validated
- **Dry Run Mode**: Preview changes before applying
- **Timeout Protection**: Commands have built-in timeouts
- **Error Handling**: Graceful degradation on tool failures

This tool consolidates all autofix functionality into a single, reliable system that integrates seamlessly with the existing MCP pipeline.
