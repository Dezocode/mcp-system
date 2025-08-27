# Semantic Catalog Tool Documentation

## Overview

The **Semantic Catalog Review Tool** is an advanced MCP (Model Context Protocol) tool integrated into the pipeline MCP server that provides comprehensive code analysis, version management, and compliance review capabilities. This tool implements high-resolution execution with 100% reliability and hierarchical protection as requested.

## Features

### 🎯 Core Capabilities

1. **High-Resolution Execution and Code Review**
   - AST-based code analysis with comprehensive node inspection
   - Function signature validation
   - Import dependency analysis  
   - Security vulnerability scanning
   - Real-time performance monitoring

2. **Version Branch Creation and Management**
   - Automatic version bumping (patch, minor, major)
   - Git branch creation with semantic versioning
   - Version file updates (pyproject.toml, __init__.py)
   - Commit automation with proper messaging

3. **Semantic Diff Analysis**
   - Branch-to-branch comparison
   - Semantic change detection
   - Risk assessment with hierarchical protection
   - File-level change analysis

4. **Function Review and Semantic Analysis**
   - Python function discovery and cataloging
   - Semantic property analysis (complexity, side effects, return types)
   - Documentation quality assessment
   - Pattern and anti-pattern identification
   - Compliance scoring

5. **Watchdog Compliance Review**
   - Security compliance checking
   - Code quality compliance
   - Documentation compliance
   - Testing compliance
   - Overall compliance scoring

6. **MCP/React Compatible Responses**
   - Multiple output formats: JSON, React components, MCP-compatible
   - Structured data for easy integration
   - Real-time progress tracking

## Tool Interface

### Tool Name
`semantic_catalog_review`

### Input Schema

```json
{
  "type": "object",
  "properties": {
    "session_id": {
      "type": "string",
      "description": "Session ID for tracking",
      "required": true
    },
    "action": {
      "type": "string",
      "enum": ["full_review", "create_version_branch", "diff_analysis", "semantic_analysis", "compliance_check"],
      "description": "Action to perform",
      "default": "full_review"
    },
    "version_bump_type": {
      "type": "string",
      "enum": ["patch", "minor", "major"],
      "description": "Type of version bump for branch creation",
      "default": "patch"
    },
    "base_branch": {
      "type": "string",
      "description": "Base branch for comparison",
      "default": "main"
    },
    "target_branch": {
      "type": "string",
      "description": "Target branch for comparison (optional, auto-generated if creating)"
    },
    "include_function_review": {
      "type": "boolean",
      "description": "Include detailed function-level review",
      "default": true
    },
    "include_watchdog_compliance": {
      "type": "boolean", 
      "description": "Include watchdog compliance checking",
      "default": true
    },
    "response_format": {
      "type": "string",
      "enum": ["json", "react", "mcp_compatible"],
      "description": "Output format compatible with MCP/React",
      "default": "mcp_compatible"
    },
    "high_resolution_mode": {
      "type": "boolean",
      "description": "Enable high-resolution execution and analysis", 
      "default": true
    },
    "hierarchical_protection": {
      "type": "boolean",
      "description": "Enable hierarchical protection for 100% reliability",
      "default": true
    }
  },
  "required": ["session_id"]
}
```

## Usage Examples

### 1. Full Semantic Review

```json
{
  "session_id": "my-session-123",
  "action": "full_review",
  "high_resolution_mode": true,
  "hierarchical_protection": true,
  "response_format": "mcp_compatible"
}
```

This performs:
- High-resolution code execution and analysis
- Version branch creation  
- Diff analysis between branches
- Semantic function analysis
- Watchdog compliance review

### 2. Version Branch Creation Only

```json
{
  "session_id": "my-session-123", 
  "action": "create_version_branch",
  "version_bump_type": "minor",
  "base_branch": "main"
}
```

Creates a new version branch with minor version bump.

### 3. Semantic Analysis Only

```json
{
  "session_id": "my-session-123",
  "action": "semantic_analysis", 
  "include_function_review": true,
  "hierarchical_protection": true
}
```

Performs semantic function analysis with hierarchical protection.

### 4. Compliance Check

```json
{
  "session_id": "my-session-123",
  "action": "compliance_check",
  "include_watchdog_compliance": true,
  "response_format": "react"
}
```

Runs comprehensive compliance review with React-compatible output.

### 5. Diff Analysis

```json
{
  "session_id": "my-session-123", 
  "action": "diff_analysis",
  "base_branch": "main",
  "target_branch": "feature-branch",
  "hierarchical_protection": true
}
```

Analyzes semantic differences between branches.

## Response Formats

### MCP Compatible Format

```json
{
  "type": "mcp_semantic_catalog",
  "version": "1.0", 
  "timestamp": 1756261287.123,
  "session_id": "my-session-123",
  "action": "full_review",
  "status": "completed",
  "data": {
    "high_resolution_execution": {...},
    "version_branch": {...},
    "diff_analysis": {...}, 
    "semantic_analysis": {...},
    "compliance_review": {...}
  },
  "meta": {
    "tool": "semantic_catalog_review",
    "high_resolution": true,
    "hierarchical_protection": true
  }
}
```

### React Component Format

```json
{
  "component": "SemanticCatalogReview",
  "props": {
    "sessionId": "my-session-123",
    "action": "full_review", 
    "status": "completed",
    "results": {...},
    "config": {...},
    "timestamp": 1756261287.123
  },
  "meta": {
    "type": "react_component",
    "version": "1.0"
  }
}
```

## Technical Implementation

### High-Resolution Execution

The tool implements high-resolution execution through:

1. **AST-based Analysis**: Uses Python's `ast` module for deep code inspection
2. **Multi-threaded Processing**: Parallel analysis of multiple files
3. **Real-time Monitoring**: Progress tracking and metrics collection
4. **Error Recovery**: Hierarchical protection with graceful degradation

### Hierarchical Protection

Ensures 100% reliability through:

1. **Layered Validation**: Multiple validation layers at each step
2. **Backup Strategies**: Automatic backup creation before modifications
3. **Rollback Capability**: Ability to revert changes if issues detected
4. **Circuit Breakers**: Automatic failure detection and prevention

### Version Management Integration

Integrates with existing version management:

1. **Semantic Versioning**: Uses `semantic_version` library for precise version handling
2. **Git Integration**: Direct git commands for branch operations
3. **File Updates**: Automatic updates to `pyproject.toml` and `__init__.py`
4. **Commit Automation**: Proper commit messages and workflow

## Integration with Pipeline MCP Server

The semantic catalog tool is fully integrated into the pipeline MCP server as tool #12, providing:

- **Session Management**: Tracking across pipeline operations
- **Protocol Integration**: Compatible with Claude Agent Protocol
- **Performance Monitoring**: Real-time metrics and health tracking  
- **Error Handling**: Comprehensive error management and logging

## Security and Compliance

### Security Features

- Input validation and sanitization
- Path traversal protection
- Command injection prevention
- Secure file operations

### Compliance Standards

- Code quality metrics
- Documentation standards
- Testing requirements  
- Security best practices

## Troubleshooting

### Common Issues

1. **Git Repository Not Found**: Ensure the tool is run in a git repository
2. **Permission Errors**: Check file system permissions for branch creation
3. **Version File Missing**: Ensure `pyproject.toml` exists for version management
4. **Import Errors**: Verify all dependencies are installed

### Debug Mode

Enable debug logging by setting the session to include detailed error information and execution traces.

## Dependencies

- `semantic_version`: For semantic version management
- `ast`: For Python code analysis (built-in)
- `git`: For version control operations
- `pathlib`: For path operations (built-in)
- `json`: For data serialization (built-in)

## Conclusion

The Semantic Catalog Review Tool provides comprehensive code analysis and version management capabilities with high-resolution execution and 100% reliability through hierarchical protection. It integrates seamlessly with the MCP protocol and supports multiple output formats for maximum compatibility.