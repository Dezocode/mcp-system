#!/usr/bin/env python3
"""
Simple Version Keeper - Test Implementation
Creates JSON linting reports for testing pipeline integration
"""

import json
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path


def create_test_lint_report():
    """Create a test lint report with required JSON structure"""

    # Ensure output directory exists
    output_dir = Path("test-output")
    output_dir.mkdir(exist_ok=True)

    # Generate session ID and timestamp
    session_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now(timezone.utc).isoformat()

    # Create mock lint report with required structure
    lint_report = {
        "timestamp": timestamp,
        "session_id": session_id,
        "version": "1.0.0",
        "branch": "main",
        "summary": {
            "total_issues": 15,
            "fixes_applied": 0,  # Lint scan doesn't apply fixes
            "remaining_issues": 15,
            "success_rate": 0.0,
        },
        "details": {
            "issues": [
                {
                    "file": "src/example.py",
                    "line": 42,
                    "severity": "warning",
                    "code": "E302",
                    "message": "expected 2 blank lines, found 1",
                    "rule": "pep8",
                },
                {
                    "file": "src/main.py",
                    "line": 15,
                    "severity": "error",
                    "code": "F401",
                    "message": "unused import",
                    "rule": "pyflakes",
                },
                {
                    "file": "tests/test_example.py",
                    "line": 23,
                    "severity": "info",
                    "code": "I001",
                    "message": "import order suggestion",
                    "rule": "isort",
                },
            ],
            "files_scanned": 25,
            "rules_applied": ["pep8", "pyflakes", "isort", "mypy"],
            "scan_duration": 2.34,
        },
        "performance": {
            "duration_seconds": 2.34,
            "files_per_second": 10.68,
            "issues_per_file": 0.6,
            "memory_usage_mb": 45.2,
        },
        "recommendations": [
            "Fix PEP8 formatting issues",
            "Remove unused imports",
            "Organize import statements",
            "Add type annotations where missing",
        ],
    }

    # Write JSON report
    output_file = output_dir / "test-lint.json"
    with open(output_file, "w") as f:
        json.dump(lint_report, f, indent=2)

    print(f"✅ Created test lint report: {output_file}")
    print(f"📊 Generated {lint_report['summary']['total_issues']} test issues")
    print(f"🔍 Session ID: {session_id}")

    return lint_report


if __name__ == "__main__":
    try:
        report = create_test_lint_report()
        print("🎉 Simple version keeper test completed successfully")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error creating test lint report: {e}")
        sys.exit(1)
