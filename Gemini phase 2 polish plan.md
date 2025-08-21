# Gemini's Phase 2 Polish Plan

This document outlines a prioritized plan to address critical issues, resolve architectural debt, and polish the codebase in preparation for Phase 2 development. The plan is based on a comprehensive analysis of the test suite results, dependency conflicts, and a full code quality scan.

---

## P0: Critical - Blockers & Core Functionality

*These issues must be resolved first as they block core components from being operational.* 

| Priority | Issue | Analysis | Proposed Fix | Files Affected |
| :--- | :--- | :--- | :--- | :--- |
| **P0.1** | `ImportError` in Server | The `pipeline_mcp_server.py` script fails to start because it tries to import `McpError` and `ErrorCode` from an external library, but the project's documentation specifies its own internal error classes. | 1. Create a new file `src/exceptions.py`. <br> 2. Define the `MCPSystemError` and `ErrorCode` classes in it, as per `docs/API-Reference.md`. <br> 3. Refactor `pipeline_mcp_server.py` to import and use these local classes. | `src/pipeline_mcp_server.py` (Modify)<br>`src/exceptions.py` (New File) |
| **P0.2** | `SyntaxError` in Loop Script | The quality scan could not parse `scripts/claude_code_integration_loop.py`, indicating a fatal syntax error that prevents any quality checks on this file. | Manually inspect the file at the reported line (1269) and fix the underlying Python syntax error. | `scripts/claude_code_integration_loop.py` (Modify) |

---

## P1: High - Architectural Health & Dependency Management

*These issues represent significant technical debt and architectural problems that will impede future development if not addressed.* 

| Priority | Issue | Analysis | Proposed Fix | Files Affected |
| :--- | :--- | :--- | :--- | :--- |
| **P1.1** | Dependency Conflict | The `pip install` log revealed that `pylint 3.1.0` requires a version of `isort` older than v6, but `isort 6.0.1` was installed, which can cause unpredictable linting behavior. | Pin the `isort` version to be compatible with `pylint`. Specifically, change the dependency to `isort>=5.12.0,<6.0` in configuration files. | `requirements.txt`<br>`pyproject.toml` |
| **P1.2** | Duplicate Functions | The scan detected **90 duplicate functions**. This level of code duplication significantly increases maintenance overhead and the risk of bugs. | Review the list of duplicates from the lint report. Abstract shared logic into utility functions and refactor the duplicate implementations to call the single, shared function. | Multiple files across the codebase. |
| **P1.3** | Monolithic `version_keeper.py` | This script is overly complex (2700+ lines) and handles too many responsibilities (linting, duplicate detection, connection checks, versioning), making it difficult to maintain and debug. | Refactor `version_keeper.py` by splitting its core functionalities into smaller, single-purpose modules, such as `scripts/linters.py`, `scripts/detectors.py`, and `scripts/reporting.py`. The main script should become a simple orchestrator. | `scripts/version_keeper.py` (Modify)<br>Multiple new modules (Create) |

---

## P2: Medium - Code Quality & Security

*These are specific, actionable issues identified by the quality scan that should be cleaned up.* 

| Priority | Issue | Analysis | Proposed Fix | Files Affected |
| :--- | :--- | :--- | :--- | :--- |
| **P2.1** | Security Vulnerabilities | The scan identified **3 security issues**. These should be reviewed and patched to maintain a secure codebase. | Inspect the detailed security report (`claude-lint-report-*.json`). Address each vulnerability, which may involve updating dependencies or changing code patterns. | Varies based on report. |
| **P2.2** | Undefined Function Calls | The scan reported **1209 undefined function calls**. While many are likely false positives due to the linter's limitations with complex class structures, this indicates areas where the code is unclear and needs review. | Perform a targeted review of the top reported undefined calls. For any that are genuine bugs, apply the necessary fix. For false positives, consider adding `# noqa` comments or refactoring the code for clarity. | Multiple files, primarily `mcp-file-sync-manager.py`. |
| **P2.3** | Code Formatting | The scan recommended running `black` and `isort` to standardize code formatting. | Execute the recommended auto-fix commands: `black .` and `isort .`. | Potentially all `.py` files. |

---

## P3: Low - Documentation & Final Cleanup

*Final touches to ensure the project is left in a clean and well-documented state.* 

| Priority | Issue | Analysis | Proposed Fix | Files Affected |
| :--- | :--- | :--- | :--- | :--- |
| **P3.1** | Documentation Sync | The project's documentation (e.g., `API-Reference.md`) is out of sync with the code's reality, such as the `McpError` vs. `MCPSystemError` discrepancy. | After all code changes are complete, thoroughly review and update all Markdown documentation to reflect the polished state of the codebase. | `docs/API-Reference.md`<br>Other `.md` files. |
| **P3.2** | Cleanup Temporary Files | The analysis generated a report file that should not be committed to the repository. | Remove the `gemini-polish-analysis.json` file. | `gemini-polish-analysis.json` |
