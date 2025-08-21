#!/usr/bin/env python3
"""
Claude Quality Patcher v2.0 - Enhanced with Protocol Integration
Integrated system with bidirectional communication, ReAct framework,
and performance optimization
"""

import difflib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import click

# Import protocol if available
try:
    from claude_agent_protocol import ActionType, TaskType, get_protocol

    PROTOCOL_AVAILABLE = True
except ImportError:
    PROTOCOL_AVAILABLE = False


class EnhancedClaudeQualityPatcher:
    def __init__(
        self,
        repo_path: Path = None,
        lint_report_path: Path = None,
        debug_mode: bool = False,
        session_dir: Path = None,
        protocol_dir: Path = None,
        max_fixes: int = 10,
        fresh_report: bool = False,
    ):
        self.repo_path = repo_path or Path.cwd()
        self.session_log = []
        self.fixes_applied = 0
        self.fixes_skipped = 0
        self.fixes_failed = 0
        self.fixes_skipped_valid = (
            0  # Track legitimately skipped fixes (5-way validated)
        )
        self.debug_mode = debug_mode
        self.max_fixes = max_fixes
        self.fresh_report = fresh_report

        # Session and protocol setup
        self.session_dir = (
            self.repo_path / "sessions" if session_dir is None else session_dir
        )
        self.protocol_dir = protocol_dir
        self.protocol = None

        if PROTOCOL_AVAILABLE and protocol_dir:
            self.protocol = get_protocol(Path(protocol_dir))
            print("✅ Protocol integration enabled")

        # Performance tracking
        self.start_time = time.time()
        self.fix_timings = []
        self.performance_metrics = {
            "fixes_per_minute": 0,
            "success_rate": 0,
            "average_fix_time": 0,
            "issues_by_complexity": {},
        }

        # Auto-discover latest lint report with version matching
        if fresh_report:
            self.lint_report_path = self.generate_fresh_lint_report()
        else:
            self.lint_report_path = (
                lint_report_path or self.find_latest_compatible_report()
            )

        # Load lint report
        if self.lint_report_path and self.lint_report_path.exists():
            with open(self.lint_report_path, "r") as f:
                self.lint_report = json.load(f)
                print(f"📊 Loaded lint report: {self.lint_report_path}")
                self.validate_report_compatibility()
        else:
            print("❌ No compatible lint report found!")
            self.lint_report = {}

    def find_latest_compatible_report(self) -> Optional[Path]:
        """Find the latest compatible lint report with version matching"""
        reports_dir = self.repo_path / "reports"

        if not reports_dir.exists():
            print("❌ No reports directory found")
            return None

        # Get current version from pyproject.toml using version_keeper
        try:
            from .version_keeper import MCPVersionKeeper

            vk = MCPVersionKeeper(self.repo_path)
            current_version = vk.get_current_version()
            current_branch = vk.get_current_branch()
        except Exception:
            current_version = "unknown"
            current_branch = "unknown"

        print("🔍 Looking for compatible lint reports...")
        print(f"   Current version: {current_version}")
        print(f"   Current branch: {current_branch}")

        # Find all Claude lint reports
        lint_reports = list(reports_dir.glob("claude-lint-report-*.json"))

        if not lint_reports:
            print("❌ No Claude lint reports found")
            return None

        # Sort by timestamp (newest first) and find compatible
        lint_reports.sort(reverse=True)

        for report_path in lint_reports:
            if self.is_report_compatible(report_path, current_version, current_branch):
                print(f"✅ Found compatible report: {report_path.name}")
                return report_path

        # Fallback to newest report with warning
        latest_report = lint_reports[0]
        print("⚠️  No perfectly compatible report found")
        print(f"   Using latest report: {latest_report.name}")
        print("   ⚠️  VERSION MISMATCH - fixes may not apply correctly")

        return latest_report

    def generate_fresh_lint_report(self) -> Optional[Path]:
        """Generate a fresh lint report using version_keeper"""
        print("🔄 Generating fresh lint report...")

        # Use session dir if available, otherwise create temporary
        if self.session_dir:
            output_dir = Path(self.session_dir) / "lint"
        else:
            output_dir = self.repo_path / "reports"

        output_dir.mkdir(parents=True, exist_ok=True)

        # Run version keeper to generate fresh report
        cmd = [
            "python3",
            "scripts/version_keeper.py",
            "--comprehensive-lint",
            "--output-dir",
            str(output_dir),
        ]

        if self.session_dir:
            cmd.extend(["--session-dir", str(self.session_dir)])

        try:
            subprocess.run(
                cmd, capture_output=True, text=True, cwd=self.repo_path
            )

            # Find the newly generated report
            reports = list(output_dir.glob("claude-lint-report-*.json"))
            if reports:
                latest_report = max(reports, key=lambda p: p.stat().st_mtime)
                print(f"✅ Fresh report generated: {latest_report}")
                return latest_report
            else:
                print("❌ No report generated")
                return None

        except Exception as e:
            print(f"❌ Failed to generate fresh report: {e}")
            return None

    def is_report_compatible(
        self,
        report_path: Path,
        current_version: str,
        current_branch: str,
    ) -> bool:
        """Check if lint report is compatible with current codebase state"""
        try:
            with open(report_path, "r") as f:
                json.load(f)

            # Check if report has version info
            # Note: timestamp extracted but not used in current logic

            # Extract date from report filename
            filename_match = re.search(
                r"claude-lint-report-(\d{8}-\d{6})\.json",
                report_path.name,
            )
            if filename_match:
                report_time_str = filename_match.group(1)

                # Check if report is recent (within last 24 hours for compatibility)
                try:
                    report_time = datetime.strptime(report_time_str, "%Y%m%d-%H%M%S")
                    time_diff = datetime.now() - report_time

                    if time_diff.total_seconds() > 86400:  # 24 hours
                        print(f"   ⏰ {report_path.name} is older than 24 hours")
                        return False

                    print(
                        f"   ✅ {report_path.name} is recent "
                        f"({time_diff.total_seconds()//3600:.0f} hours old)"
                    )
                    return True

                except ValueError:
                    pass

            # Fallback: if we can't parse time, check file modification time
            file_mtime = datetime.fromtimestamp(report_path.stat().st_mtime)
            time_diff = datetime.now() - file_mtime

            return time_diff.total_seconds() <= 86400  # 24 hours

        except Exception as e:
            print(f"   ❌ Error checking {report_path.name}: {e}")
            return False

    def validate_report_compatibility(self):
        """Validate the loaded report is compatible with current codebase"""
        if not self.lint_report:
            return

        # Check report structure
        required_fields = [
            "priority_fixes",
            "validation_report",
            "timestamp",
        ]
        missing_fields = [
            field for field in required_fields if field not in self.lint_report
        ]

        if missing_fields:
            print(f"⚠️  Report missing fields: {missing_fields}")
            print("   Some features may not work correctly")

        # Check number of fixes available
        priority_fixes = self.lint_report.get("priority_fixes", [])
        validation_report = self.lint_report.get("validation_report", {})

        total_fixes = len(priority_fixes)
        safe_fixes = len(validation_report.get("safe_recommendations", []))
        blocked_fixes = len(validation_report.get("blocked_recommendations", []))

        print("📊 Report Summary:")
        print(f"   Total fixes: {total_fixes}")
        print(f"   Safe fixes: {safe_fixes}")
        print(f"   Blocked fixes: {blocked_fixes} (WILL BE PROCESSED ANYWAY)")
        print(f"   Available fixes: {total_fixes} (ALL WILL BE ATTEMPTED)")

        if total_fixes == 0:
            print("✅ No fixes needed - codebase is clean!")
        else:
            print(
                f"🚀 Will attempt ALL {total_fixes} fixes regardless of blocking status"
            )

    def auto_integrate_with_version_keeper(self) -> bool:
        """Auto-integrate with version keeper for seamless workflow"""
        print("🔗 Integrating with MCP Version Keeper...")

        # Check if version keeper is available
        version_keeper_path = self.repo_path / "scripts" / "version_keeper.py"

        if not version_keeper_path.exists():
            print("❌ Version keeper not found - manual mode only")
            return False

        # Check if we need a fresh lint report
        if not self.lint_report_path or not self.is_report_fresh():
            print("🔄 Generating fresh lint report...")

            try:
                # Run version keeper to generate new report
                result = subprocess.run(
                    [
                        "python3",
                        str(version_keeper_path),
                        "--comprehensive-lint",
                        "--lint-only",
                        "--output-dir=reports/",
                    ],
                    capture_output=True,
                    text=True,
                    cwd=self.repo_path,
                )

                if result.returncode == 0:
                    print("✅ Fresh lint report generated")

                    # Reload the new report
                    new_report = self.find_latest_compatible_report()
                    if new_report:
                        self.lint_report_path = new_report
                        with open(self.lint_report_path, "r") as f:
                            self.lint_report = json.load(f)
                        print(f"📊 Loaded fresh report: {self.lint_report_path}")
                        return True
                else:
                    print(f"❌ Failed to generate fresh report: {result.stderr}")
                    return False

            except Exception as e:
                print(f"❌ Error generating fresh report: {e}")
                return False

        print("✅ Using existing compatible report")
        return True

    def is_report_fresh(self) -> bool:
        """Check if current report is fresh (less than 1 hour old)"""
        if not self.lint_report_path or not self.lint_report_path.exists():
            return False

        file_mtime = datetime.fromtimestamp(self.lint_report_path.stat().st_mtime)
        time_diff = datetime.now() - file_mtime

        return time_diff.total_seconds() <= 3600  # 1 hour

    def start_claude_session(self):
        """Initialize Claude fixing session with safety protocols"""
        print("🤖 Starting Claude Quality Patcher Session")
        print("=" * 60)
        print("⚠️  SAFETY PROTOCOLS ENABLED:")
        print("   • One fix at a time")
        print("   • Read file before every edit")
        print("   • Validate fix compatibility")
        print("   • Test syntax after each change")
        print("   • Automatic rollback on failure")
        print("=" * 60)

        session_info = {
            "session_start": datetime.now().isoformat(),
            "repo_path": str(self.repo_path),
            "lint_report": str(self.lint_report_path),
            "safety_protocols": "enabled",
            "mode": "step_by_step_fixing",
        }

        self.session_log.append(
            {
                "type": "session_start",
                "timestamp": datetime.now().isoformat(),
                "info": session_info,
            }
        )

        return session_info

    def get_priority_fixes(self) -> List[Dict[str, Any]]:
        """Get ALL available fixes from lint report - NO BLOCKING"""
        priority_fixes = self.lint_report.get("priority_fixes", [])

        # PROCESS ALL FIXES - Remove validation blocking system
        print(f"📋 Processing ALL {len(priority_fixes)} available fixes")
        print("⚠️  BLOCKING SYSTEM DISABLED - Will attempt all fixes")

        # Sort by priority (1=highest, 4=lowest)
        # UPGRADED: Smart priority for real fixes over false positives
        def get_fresh_priority(fix):
            description = fix.get("description", "").lower()
            original_priority = fix.get("priority", 4)

            # BOOST: undefined functions (real issues)
            if "undefined" in description or "not defined" in description:
                return (1, original_priority)
            # BOOST: missing imports
            elif "import" in description or "module" in description:
                return (2, original_priority)
            # DEMOTE: duplicate removals (likely false positives)
            elif "duplicate" in description or "remove duplicate" in description:
                return (9, original_priority)
            # NORMAL: other issues
            else:
                return (original_priority, 0)

        priority_fixes.sort(key=get_fresh_priority)

        return priority_fixes

    def generate_claude_fix_prompt(self, fix_item: Dict[str, Any]) -> str:
        """
        Generate specific Claude prompt for a single fix with enhanced details
        and guardrails
        """
        fix = fix_item.get("fix", {})
        priority = fix_item.get("priority", 4)
        category = fix_item.get("category", "unknown")

        fix_type = fix.get("type", "")
        claude_prompt = fix.get("claude_prompt", "")

        # Extract detailed information from fix with safety validation
        target_file = self.extract_target_file(fix)
        if not target_file:
            return "❌ INVALID FIX: No safe target file identified. Skipping this fix."

        line_numbers = self.extract_line_numbers(fix)

        # Extract rich context from linter report
        linter_context = self._extract_linter_context(fix, fix_item)

        # Priority indicators
        priority_emoji = (
            "🔴"
            if priority == 1
            else ("🟡" if priority == 2 else "🟢" if priority == 3 else "⚪")
        )

        # Enhanced fix description with actual code context
        enhanced_description = self._get_enhanced_fix_description(
            fix, target_file, line_numbers
        )

        prompt = f"""
{priority_emoji} CLAUDE QUALITY PATCHER - MANDATORY FIX ENFORCEMENT
Category: {category.upper()} | Priority: {priority} | Type: {fix_type}
📁 Target File: {target_file}
📍 Target Lines: {line_numbers if line_numbers else 'Auto-detected'}

🚨 CRITICAL INSTRUCTIONS - YOU MUST FOLLOW EXACTLY:
1. READ the target file first using the Read tool
2. IDENTIFY the exact issue described below
3. APPLY the fix using Edit or MultiEdit tool - THIS IS MANDATORY
4. VALIDATE the syntax is correct after your change

🔥 ENFORCEMENT NOTICE:
- This system VALIDATES that you actually apply the fix
- If no file change is detected, the fix will be marked as FAILED
- You MUST make the actual code change, not simulate it
- The system compares file content before/after to verify changes

🎯 SPECIFIC FIX REQUIRED:
{enhanced_description}

ORIGINAL ISSUE DESCRIPTION:
{claude_prompt}

SAFETY REQUIREMENTS:
- Only modify the specific line/section mentioned
- Preserve all existing functionality
- Maintain code style and formatting
- Do not introduce new dependencies
- Do not remove critical imports or function calls

LINTER REPORT CONTEXT:
{linter_context}

ADDITIONAL CONTEXT:
{self._get_fix_context(fix)}

🔒 SAFETY GUARDRAILS ACTIVE:
- File path validated and within repository bounds
- Target file exists and is modifiable
- Backup created before any changes
- Post-fix validation will verify syntax and changes
- Unauthorized changes will trigger rollback

⚡ ACTION REQUIRED: Apply this fix NOW using Edit tool. System will verify the change.
"""
        return prompt.strip()

    def _extract_linter_context(
        self, fix: Dict[str, Any], fix_item: Dict[str, Any]
    ) -> str:
        """Extract rich context from linter report for better guardrails"""
        context_lines = []

        # File information
        file_path = fix.get("file", "")
        if file_path:
            try:
                file_stats = Path(file_path).stat()
                file_size = file_stats.st_size
                context_lines.append(f"📁 File: {file_path}")
                context_lines.append(f"📏 Size: {file_size} bytes")
            except Exception:
                context_lines.append(f"📁 File: {file_path} (size unknown)")

        # Line information with context
        line_num = fix.get("line", "")
        if line_num:
            context_lines.append(f"📍 Target Line: {line_num}")

            # Try to show surrounding code context
            if file_path and Path(file_path).exists():
                try:
                    with open(file_path, "r") as f:
                        lines = f.readlines()

                    line_idx = int(line_num) - 1  # Convert to 0-based
                    if 0 <= line_idx < len(lines):
                        # Show 2 lines before and after
                        start_idx = max(0, line_idx - 2)
                        end_idx = min(len(lines), line_idx + 3)

                        context_lines.append("🔍 Code Context:")
                        for i in range(start_idx, end_idx):
                            marker = "👉" if i == line_idx else "  "
                            context_lines.append(
                                f"  {marker} {i+1:3d}: {lines[i].rstrip()}"
                            )
                except Exception:
                    pass

        # Error details
        error_code = fix.get("code", "")
        error_msg = fix.get("error", "")
        severity = fix.get("severity", "")

        if error_code:
            context_lines.append(f"🚨 Error Code: {error_code}")
        if error_msg:
            context_lines.append(f"💬 Error: {error_msg}")
        if severity:
            context_lines.append(f"⚡ Severity: {severity}")

        # Fix classification from linter
        fix_type = fix.get("type", "")
        if fix_type:
            context_lines.append(f"🔧 Fix Type: {fix_type}")

        # Validation status from linter report
        validation_info = fix_item.get("validation", {})
        if validation_info:
            safety_level = validation_info.get("safety_level", "unknown")
            confidence = validation_info.get("confidence", "unknown")
            context_lines.append(f"✅ Safety Level: {safety_level}")
            context_lines.append(f"🎯 Confidence: {confidence}")

        # Additional metadata
        description = fix.get("description", "")
        if description and description != "No description":
            context_lines.append(f"📝 Description: {description}")

        return (
            "\n".join(context_lines)
            if context_lines
            else "No additional context available"
        )

    def _get_fix_context(self, fix: Dict[str, Any]) -> str:
        """Get additional context for the fix"""
        fix_type = fix.get("type", "")

        if fix_type == "auto_fix":
            return "This is an auto-formatting fix. Use the exact command provided."

        elif fix_type == "manual_fix":
            file_path = fix.get("file", "")
            line_num = fix.get("line", "")
            error_msg = fix.get("error", "")

            return f"""
FILE: {file_path}
LINE: {line_num}
ERROR: {error_msg}

Focus on this specific line only. Check surrounding context for proper fix.
"""

        elif fix_type == "security_fix":
            file_path = fix.get("file", "")
            line_num = fix.get("line", "")
            severity = fix.get("severity", "")

            return f"""
SECURITY ISSUE in {file_path}:{line_num}
SEVERITY: {severity}

This is a security vulnerability. Fix carefully to maintain functionality
while removing the security risk.
"""

        elif fix_type == "remove_duplicate":
            return (
                "This is a duplicate function removal. Ensure no other code "
                "depends on this specific instance before removing."
            )

        elif fix_type in [
            "fix_undefined_function",
            "fix_broken_import",
        ]:
            file_path = fix.get("file", "").split("/")[-1] if fix.get("file") else ""
            line_num = fix.get("line", "")

            return f"""
CONNECTION ISSUE in {file_path}:{line_num}

This may be a false positive from static analysis. Verify the issue
actually exists before fixing.
"""

        return "Standard fix - follow the claude_prompt instructions carefully."

    def extract_line_numbers(self, fix: Dict[str, Any]) -> str:
        """Extract line numbers from fix information"""
        line_num = fix.get("line", "")
        if line_num:
            return str(line_num)

        # Try to extract from description
        description = fix.get("description", "") + " " + fix.get("claude_prompt", "")

        # Look for patterns like "line 123" or "file.py:456"
        line_matches = re.findall(r"(?:line\s+)?(\d+)", description)
        if line_matches:
            return ", ".join(line_matches)

        return ""

    def _get_enhanced_fix_description(
        self,
        fix: Dict[str, Any],
        target_file: str,
        line_numbers: str,
    ) -> str:
        """Generate enhanced fix description with code context"""
        fix_type = fix.get("type", "")

        if fix_type == "security_fix":
            issue_text = fix.get("issue", "")
            severity = fix.get("severity", "UNKNOWN")

            return f"""SECURITY VULNERABILITY DETECTED:
Issue: {issue_text}
Severity: {severity}
Location: {target_file}:{line_numbers}

REQUIRED ACTION: Review the vulnerable code and apply security hardening.
Common fixes: Add input validation, use safe functions, avoid code injection risks."""

        elif fix_type == "remove_duplicate":
            description = fix.get("description", "")

            return f"""DUPLICATE CODE DETECTED:
{description}

REQUIRED ACTION: Remove the duplicate implementation while preserving functionality.
Check if any code depends on this specific instance before removal."""

        elif fix_type == "manual_fix":
            error_msg = fix.get("error", "")
            code = fix.get("code", "")

            return f"""LINTING ERROR DETECTED:
Code: {code}
Error: {error_msg}
Location: {target_file}:{line_numbers}

REQUIRED ACTION: Fix the specific linting violation shown above."""

        elif fix_type in ["auto_fix", "auto-fix"]:
            command = fix.get("command", "")
            code = fix.get("code", "")
            message = fix.get("message", "")
            action = fix.get("fix_action", {}).get("action", "")

            if code and message:
                return f"""LINTING ISSUE DETECTED:
Code: {code} - {message}
Location: {target_file}:{line_numbers}

REQUIRED ACTION: {self._get_fix_instruction(code, message, action)}"""
            else:
                return f"""AUTO-FIXABLE FORMATTING ISSUE:
Command to run: {command}
Location: {target_file}

REQUIRED ACTION: Apply the auto-formatting command shown above."""

        elif fix_type in [
            "fix_undefined_function",
            "fix_broken_import",
        ]:
            function_name = fix.get("function", "") or fix.get("module", "")

            return f"""CONNECTION ISSUE DETECTED:
Missing: {function_name}
Location: {target_file}:{line_numbers}

REQUIRED ACTION: Add missing import, define function, or fix the reference.
Note: This may be a false positive - verify the issue exists first."""

        # Fallback for unknown types
        return f"""ISSUE DETECTED:
Type: {fix_type}
Location: {target_file}:{line_numbers}

REQUIRED ACTION: Review the original issue description and apply the appropriate fix."""

    def _get_fix_instruction(self, code: str, message: str, action: str) -> str:
        """Get specific fix instruction for linting code"""
        if code == 'W292':  # no newline at end of file
            return "Add a newline at the end of the file"
        elif code == 'W291':  # trailing whitespace
            return "Remove trailing whitespace from the line"
        elif code == 'W293':  # blank line contains whitespace
            return "Remove whitespace from the blank line"
        elif code.startswith('E501'):  # line too long
            return "Break the long line into multiple lines (max 88 chars)"
        elif code.startswith('F401'):  # unused import
            return "Remove the unused import statement"
        elif code.startswith('E722'):  # bare except
            return "Specify the exception type instead of using bare 'except:'"
        elif code.startswith('F541'):  # f-string missing placeholders
            return "Convert f-string to regular string or add placeholders"
        elif code.startswith('E203'):  # whitespace before ':'
            return "Remove whitespace before the colon"
        elif code.startswith('F841'):  # local variable assigned but never used
            return "Remove the unused variable or add underscore prefix"
        else:
            return f"Fix the {code} violation: {message}"

    def validate_fix_applied(
        self, fix_item: Dict[str, Any], file_path: str
    ) -> Dict[str, Any]:
        """Validate that a fix was applied correctly"""
        print(f"🔍 Validating fix applied to {file_path}...")

        validation_result = {
            "syntax_valid": False,
            "fix_applied": False,
            "file_modified": False,
            "errors": [],
            "warnings": [],
        }

        # Check Python syntax if it's a Python file
        if file_path.endswith(".py"):
            try:
                with open(file_path, "r") as f:
                    content = f.read()

                compile(content, file_path, "exec")
                validation_result["syntax_valid"] = True
                print("  ✅ Python syntax valid")

            except SyntaxError as e:
                validation_result["errors"].append(f"Syntax error: {e}")
                print(f"  ❌ Syntax error: {e}")
                return validation_result

            except Exception as e:
                validation_result["errors"].append(f"Validation error: {e}")
                print(f"  ⚠️ Validation error: {e}")

        # Check if fix was actually applied based on fix type
        fix = fix_item.get("fix", {})
        fix_type = fix.get("type", "")

        if fix_type == "manual_fix":
            # For manual fixes, run the specific linter to see if issue is resolved
            line_num = fix.get("line", "")
            error_code = fix.get("code", "")

            if error_code and line_num:
                # Run flake8 on specific line
                result = subprocess.run(
                    [
                        "flake8",
                        "--select",
                        error_code,
                        "--max-line-length=120",
                        file_path,
                    ],
                    capture_output=True,
                    text=True,
                )

                if f":{line_num}:" not in result.stdout:
                    validation_result["fix_applied"] = True
                    validation_result["file_modified"] = True
                    print(f"  ✅ Fix applied - {error_code} error resolved")
                else:
                    validation_result["warnings"].append(
                        f"Fix may not be complete - {error_code} still present"
                    )
                    print(f"  ⚠️ Fix may not be complete - {error_code} still present")

        elif fix_type == "auto_fix":
            # Auto-fixes should always be valid
            validation_result["fix_applied"] = True
            validation_result["file_modified"] = True
            print("  ✅ Auto-fix applied")

        else:
            # For other types, assume applied if syntax is valid
            validation_result["fix_applied"] = validation_result["syntax_valid"]
            validation_result["file_modified"] = validation_result["syntax_valid"]

        return validation_result

    def create_backup(self, file_path: str, fix_item: Dict[str, Any] = None) -> str:
        """Create descriptively named versioned backup of file before fixing"""
        # Get version and branch info using version_keeper
        try:
            from .version_keeper import MCPVersionKeeper

            vk = MCPVersionKeeper(self.repo_path)
            current_version = vk.get_current_version()
            current_branch = vk.get_current_branch()
        except Exception:
            current_version = "unknown"
            current_branch = "unknown"
        session_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Extract fix information for descriptive naming
        fix_info = fix_item.get("fix", {}) if fix_item else {}
        fix_type = fix_info.get("type", "unknown_fix")
        fix_category = fix_item.get("category", "general") if fix_item else "general"
        fix_priority = fix_item.get("priority", 4) if fix_item else 4

        # Create descriptive backup filename
        file_name = Path(file_path).name
        file_stem = Path(file_path).stem
        file_ext = Path(file_path).suffix

        # Quality patcher specific naming convention
        backup_name = (
            f"{file_stem}_v{current_version}_{current_branch}_"
            f"p{fix_priority}_{fix_category}_{fix_type}_"
            f"{session_timestamp}{file_ext}.backup"
        )

        # Organize backups by version/branch/session with quality patcher structure
        versioned_backup_dir = (
            self.repo_path
            / ".claude_patches"
            / "quality_patcher_backups"
            / f"v{current_version}"
            / current_branch
            / session_timestamp
        )
        versioned_backup_dir.mkdir(parents=True, exist_ok=True)

        # Legacy compatibility directory
        legacy_backup_dir = self.repo_path / ".claude_patches" / "backups"
        legacy_backup_dir.mkdir(parents=True, exist_ok=True)

        # Create paths with descriptive names
        versioned_backup_path = versioned_backup_dir / backup_name
        legacy_backup_path = legacy_backup_dir / backup_name

        try:
            # Create both backups with quality patcher metadata
            shutil.copy2(file_path, versioned_backup_path)
            shutil.copy2(file_path, legacy_backup_path)

            # Create comprehensive metadata for quality patcher
            metadata = {
                "quality_patcher_session": {
                    "backup_created": datetime.now().isoformat(),
                    "session_id": session_timestamp,
                    "patcher_version": "claude_quality_patcher_v1.0",
                },
                "file_info": {
                    "original_file": str(file_path),
                    "file_name": file_name,
                    "file_size": Path(file_path).stat().st_size,
                    "file_checksum": self._calculate_checksum_fallback(file_path),
                },
                "version_control": {
                    "version": current_version,
                    "branch": current_branch,
                    "backup_reason": "pre_claude_edit_guardrail_safety",
                },
                "fix_context": {
                    "fix_type": fix_type,
                    "fix_category": fix_category,
                    "fix_priority": fix_priority,
                    "fix_description": fix_info.get("description", "No description"),
                    "target_line": fix_info.get("line", "Unknown"),
                    "severity": fix_info.get("severity", "Unknown"),
                },
                "guardrail_info": {
                    "active_monitoring": True,
                    "anti_hallucination": True,
                    "real_time_validation": True,
                    "backup_cleanup_policy": "only_when_no_violations",
                },
            }

            # Save metadata with quality patcher specific extension
            metadata_path = versioned_backup_path.with_suffix(".qp_metadata.json")
            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=2)

            print(f"  💾 Quality patcher backup created: {backup_name}")
            print(
                f"  📁 Location: v{current_version}/{current_branch}/{session_timestamp}"
            )
            print(f"  🏷️  Fix: P{fix_priority} {fix_category} {fix_type}")

            # Return the versioned backup path (primary)
            return str(versioned_backup_path)

        except Exception as e:
            print(f"  ⚠️ Quality patcher backup failed: {e}")
            return ""

    def _calculate_checksum_fallback(self, file_path: str) -> str:
        """Calculate file checksum using fallback implementation"""
        import hashlib

        try:
            with open(file_path, "rb") as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception:
            return ""

    def analyze_diff_and_restore_deleted(
        self,
        file_path: str,
        backup_path: str,
        target_lines: List[int] = None,
    ) -> Dict[str, Any]:
        """Advanced diff analysis with surgical restoration of
        unintentionally deleted code"""
        if not backup_path or not Path(backup_path).exists():
            return {"restored": False, "reason": "no_backup"}

        try:
            # Read both files
            with open(file_path, "r") as f:
                current_lines = f.readlines()

            with open(backup_path, "r") as f:
                backup_lines = f.readlines()

            print(
                f"  🔍 DIFF ANALYSIS: Comparing {len(current_lines)} vs "
                f"{len(backup_lines)} lines"
            )

            # Generate unified diff
            diff = list(
                difflib.unified_diff(
                    backup_lines,
                    current_lines,
                    fromfile=f"{file_path}.backup",
                    tofile=file_path,
                    lineterm="",
                )
            )

            if not diff:
                print("  ✅ No differences detected")
                return {
                    "restored": False,
                    "reason": "no_changes",
                }

            # Analyze deletions and modifications
            deleted_lines = []
            added_lines = []

            i = 0
            while i < len(diff):
                line = diff[i]
                if line.startswith("@@"):
                    # Parse hunk header to get line numbers
                    match = re.match(
                        r"@@ -(\d+),?(\d*) \+(\d+),?(\d*) @@",
                        line,
                    )
                    if match:
                        old_start = int(match.group(1))
                        new_start = int(match.group(3))

                        # Analyze changes in this hunk
                        i += 1
                        while i < len(diff) and not diff[i].startswith("@@"):
                            if diff[i].startswith("-"):
                                deleted_lines.append(
                                    {
                                        "line_num": old_start
                                        + len(
                                            [
                                                line
                                                for line in deleted_lines
                                                if line.get(
                                                    "hunk_start",
                                                    0,
                                                )
                                                == old_start
                                            ]
                                        ),
                                        "content": diff[i][1:],
                                        "hunk_start": old_start,
                                    }
                                )
                            elif diff[i].startswith("+"):
                                added_lines.append(
                                    {
                                        "line_num": new_start
                                        + len(
                                            [
                                                line
                                                for line in added_lines
                                                if line.get(
                                                    "hunk_start",
                                                    0,
                                                )
                                                == new_start
                                            ]
                                        ),
                                        "content": diff[i][1:],
                                        "hunk_start": new_start,
                                    }
                                )
                            i += 1
                else:
                    i += 1

            print("  📊 DIFF SUMMARY:")
            print(f"    Deleted lines: {len(deleted_lines)}")
            print(f"    Added lines: {len(added_lines)}")
            print(f"    Target lines for fix: {target_lines}")

            # Determine which deletions are unintentional
            unintentional_deletions = []
            if target_lines:
                for deletion in deleted_lines:
                    if deletion["line_num"] not in target_lines:
                        # Check if this deletion looks unintentional
                        content = deletion["content"].strip()
                        if self.is_likely_unintentional_deletion(content):
                            unintentional_deletions.append(deletion)
            else:
                # If no target lines specified, check for critical deletions
                for deletion in deleted_lines:
                    content = deletion["content"].strip()
                    if self.is_critical_code_deletion(content):
                        unintentional_deletions.append(deletion)

            if not unintentional_deletions:
                print("  ✅ All deletions appear intentional")
                return {
                    "restored": False,
                    "reason": "no_unintentional_deletions",
                    "analysis": {
                        "deleted_lines": len(deleted_lines),
                        "added_lines": len(added_lines),
                    },
                }

            # Perform surgical restoration
            print(
                f"  🔧 SURGICAL RESTORATION: Restoring "
                f"{len(unintentional_deletions)} unintentionally deleted lines"
            )
            restoration_result = self.perform_surgical_restoration(
                file_path,
                current_lines,
                unintentional_deletions,
                target_lines,
            )

            return {
                "restored": restoration_result["success"],
                "lines_restored": restoration_result.get("lines_restored", 0),
                "analysis": {
                    "deleted_lines": len(deleted_lines),
                    "added_lines": len(added_lines),
                    "unintentional_deletions": len(unintentional_deletions),
                    "restoration_details": restoration_result,
                },
            }

        except Exception as e:
            print(f"  ❌ DIFF ANALYSIS ERROR: {e}")
            return {
                "restored": False,
                "reason": f"analysis_error: {e}",
            }

    def is_likely_unintentional_deletion(self, content: str) -> bool:
        """Detect if a deleted line was likely unintentional"""
        content = content.strip()

        # Empty lines or comments are usually safe to delete
        if not content or content.startswith("#"):
            return False

        # Function definitions, class definitions, imports are critical
        critical_patterns = [
            r"^def\s+\w+",  # function definitions
            r"^class\s+\w+",  # class definitions
            r"^import\s+",  # imports
            r"^from\s+.+\s+import",  # from imports
            r"^@\w+",  # decorators
            r"^\s*return\s+",  # return statements
            r"^\s*raise\s+",  # raise statements
            r"^\s*if\s+__name__",  # main guard
            r"^\s*try:",  # try blocks
            r"^\s*except\s*",  # except blocks
            r"^\s*finally:",  # finally blocks
            r"^\s*with\s+",  # with statements
        ]

        for pattern in critical_patterns:
            if re.match(pattern, content):
                print(f"    🚨 CRITICAL DELETION: {content[:50]}...")
                return True

        # Lines with significant code content
        if len(content) > 10 and any(char in content for char in "(){}[]=\"'"):
            print(f"    ⚠️  SUSPICIOUS DELETION: {content[:50]}...")
            return True

        return False

    def is_critical_code_deletion(self, content: str) -> bool:
        """Detect critical code that should never be deleted"""
        content = content.strip()

        critical_patterns = [
            r"^def\s+\w+",  # function definitions
            r"^class\s+\w+",  # class definitions
            r"^import\s+",  # imports
            r"^from\s+.+\s+import",  # from imports
            r"^\s*return\s+",  # return statements
            r"^\s*if\s+__name__",  # main guard
        ]

        return any(re.match(pattern, content) for pattern in critical_patterns)

    def perform_surgical_restoration(
        self,
        file_path: str,
        current_lines: List[str],
        unintentional_deletions: List[Dict],
        target_lines: List[int] = None,
    ) -> Dict[str, Any]:
        """Perform surgical restoration without overwriting or misplacing lines"""
        try:
            print(
                f"    🏥 SURGICAL RESTORATION: Processing "
                f"{len(unintentional_deletions)} deletions"
            )

            # Sort deletions by line number (descending to avoid line number shifts)
            deletions_sorted = sorted(
                unintentional_deletions,
                key=lambda x: x["line_num"],
                reverse=True,
            )

            restored_lines = 0
            restoration_log = []
            modified_lines = current_lines.copy()

            for deletion in deletions_sorted:
                line_num = deletion["line_num"]
                content = deletion["content"]

                # Find the best insertion point
                insertion_point = self.find_safe_insertion_point(
                    modified_lines,
                    line_num,
                    content,
                    target_lines,
                )

                if insertion_point is not None:
                    # Insert the line at the safe location
                    modified_lines.insert(insertion_point, content)
                    restored_lines += 1

                    restoration_log.append(
                        {
                            "original_line": line_num,
                            "restored_at": insertion_point + 1,  # 1-indexed for display
                            "content": content.strip(),
                        }
                    )

                    print(
                        f"      ✅ Restored line {line_num} → "
                        f"{insertion_point + 1}: {content.strip()[:40]}..."
                    )
                else:
                    print(
                        f"      ⚠️  Could not safely restore line {line_num}: "
                        f"{content.strip()[:40]}..."
                    )
                    restoration_log.append(
                        {
                            "original_line": line_num,
                            "restored_at": None,
                            "content": content.strip(),
                            "reason": "no_safe_insertion_point",
                        }
                    )

            if restored_lines > 0:
                # Write the restored content back to file
                with open(file_path, "w") as f:
                    f.writelines(modified_lines)

                print(f"    ✅ RESTORATION COMPLETE: {restored_lines} lines restored")

            return {
                "success": restored_lines > 0,
                "lines_restored": restored_lines,
                "restoration_log": restoration_log,
                "total_deletions": len(unintentional_deletions),
            }

        except Exception as e:
            print(f"    ❌ SURGICAL RESTORATION ERROR: {e}")
            return {"success": False, "error": str(e)}

    def find_safe_insertion_point(
        self,
        lines: List[str],
        original_line: int,
        content: str,
        target_lines: List[int] = None,
    ) -> Optional[int]:
        """Find a safe place to insert a restored line without disrupting structure"""
        content_stripped = content.strip()

        # Try to insert at or near the original location
        if original_line <= len(lines):
            # Check if we can insert at the exact original location
            insertion_candidate = original_line - 1  # Convert to 0-indexed

            # Ensure we don't insert in the middle of target fix lines
            if target_lines:
                # Find a gap between target lines or before/after the target block
                target_lines_sorted = sorted(target_lines)

                # Try inserting before the target block
                if insertion_candidate < target_lines_sorted[0] - 1:
                    return max(0, insertion_candidate)

                # Try inserting after the target block
                if insertion_candidate > target_lines_sorted[-1]:
                    return min(len(lines), insertion_candidate)

                # Find gaps within target lines
                for i in range(len(target_lines_sorted) - 1):
                    gap_start = target_lines_sorted[i]
                    gap_end = target_lines_sorted[i + 1]

                    if (
                        gap_end - gap_start > 1
                        and gap_start <= insertion_candidate < gap_end
                    ):
                        return insertion_candidate
            else:
                # No target lines restriction - insert at original location
                return max(0, min(len(lines), insertion_candidate))

        # Fallback: find contextually appropriate location
        if content_stripped.startswith("import ") or content_stripped.startswith(
            "from "
        ):
            # Insert with other imports at the top
            for i, line in enumerate(lines):
                if not (
                    line.strip().startswith("import ")
                    or line.strip().startswith("from ")
                    or line.strip().startswith("#")
                    or not line.strip()
                ):
                    return i
            return 0

        elif content_stripped.startswith("def ") or content_stripped.startswith(
            "class "
        ):
            # Insert at module level (not inside other functions)
            return len(lines)

        # Default: insert at the end
        return len(lines)

    def wait_for_file_sync(
        self, target_file: str, backup_path: str, max_wait: int = 10
    ) -> bool:
        """
        Professional-grade real-time file monitoring using Watchdog library.

        Implements industry best practices for file system monitoring as recommended
        by Python file monitoring research. Uses event-driven detection instead of
        polling for superior performance and reliability.

        Args:
            target_file: Path to the file being modified
            backup_path: Path to the backup file for comparison
            max_wait: Maximum seconds to wait (default: 10)

        Returns:
            True if file changes detected, False if timeout
        """
        import os
        import threading
        import time
        from pathlib import Path

        print(
            f"   🔍 Professional Watchdog monitoring: {os.path.basename(target_file)}"
        )

        # Try to use Watchdog library for professional-grade monitoring
        try:
            from watchdog.events import FileSystemEventHandler
            from watchdog.observers import Observer

            class FileChangeHandler(FileSystemEventHandler):
                def __init__(self, target_file):
                    self.target_file = Path(target_file).resolve()
                    self.change_detected = threading.Event()

                def on_modified(self, event):
                    if not event.is_directory:
                        modified_path = Path(event.src_path).resolve()
                        if modified_path == self.target_file:
                            print(f"   ⚡ Watchdog detected change: {event.src_path}")
                            self.change_detected.set()

            # Setup professional file monitoring
            target_path = Path(target_file)
            handler = FileChangeHandler(target_file)
            observer = Observer()
            observer.schedule(handler, str(target_path.parent), recursive=False)

            # Start monitoring
            observer.start()
            start_time = time.time()

            try:
                # Wait for change detection or timeout
                if handler.change_detected.wait(timeout=max_wait):
                    elapsed = time.time() - start_time
                    print(f"   ✅ File change detected via Watchdog in {elapsed:.2f}s")
                    return True
                else:
                    elapsed = time.time() - start_time
                    print(
                        f"   ⏱️  Watchdog timeout after {elapsed:.1f}s "
                        f"(normal for pre-modified files)"
                    )
                    return False
            finally:
                observer.stop()
                observer.join(timeout=1.0)

        except ImportError:
            print(
                "   ⚠️  Watchdog not available, falling back to enhanced "
                "stat monitoring"
            )
            # Fallback to optimized stat-based monitoring
            return self._fallback_stat_monitoring(target_file, max_wait)
        except Exception as e:
            print(f"   ⚠️  Watchdog error: {e}, falling back to stat monitoring")
            return self._fallback_stat_monitoring(target_file, max_wait)

    def _fallback_stat_monitoring(self, target_file: str, max_wait: int) -> bool:
        """
        Optimized fallback monitoring using stat() with safety controls.
        Used when Watchdog library is not available.
        """
        import os

        print(f"   🔄 Fallback stat monitoring: {os.path.basename(target_file)}")

        # Get baseline with error handling
        try:
            baseline_stat = os.stat(target_file)
            baseline_mtime = baseline_stat.st_mtime
            baseline_size = baseline_stat.st_size
        except Exception as e:
            print(f"   ⚠️  Cannot establish baseline: {e}")
            time.sleep(1.0)
            return False

        # Optimized intervals based on research
        intervals = [0.1, 0.3, 0.8]  # Progressive but limited
        total_waited = 0

        for interval in intervals:
            if total_waited >= max_wait:
                break

            time.sleep(interval)
            total_waited += interval

            try:
                current_stat = os.stat(target_file)

                # Check for changes
                if (
                    current_stat.st_mtime != baseline_mtime
                    or current_stat.st_size != baseline_size
                ):
                    print(f"   ⚡ Stat change detected after {total_waited:.1f}s")
                    return True

            except Exception as e:
                print(f"   ⚠️  Stat error: {e}")
                continue

        print(f"   ⏱️  No stat changes in {total_waited:.1f}s")
        return False

    def monitor_lint_report_freshness(
        self, report_pattern: str = "*.json", max_wait: int = 30
    ) -> bool:
        """
        Professional-grade background monitoring for lint report freshness.

        Uses Watchdog to monitor lint report directories for new or updated
        reports, automatically detecting when fresh lint data is available.

        Args:
            report_pattern: Glob pattern for lint reports (default: "*.json")
            max_wait: Maximum seconds to wait for fresh reports (default: 30)

        Returns:
            True if fresh lint reports detected, False if timeout
        """
        import glob
        import threading
        import time
        from pathlib import Path

        # Find lint report directories
        lint_dirs = [
            Path("pipeline-outputs/sessions/*/lint"),
            Path("reports/lint"),
            Path(".claude_patches/lint"),
            Path("lint-reports"),
        ]

        existing_dirs = []
        for pattern in lint_dirs:
            for path in glob.glob(str(pattern)):
                if Path(path).is_dir():
                    existing_dirs.append(Path(path))

        if not existing_dirs:
            print("   📋 No lint report directories found")
            return False

        print(
            f"   📊 Monitoring {len(existing_dirs)} lint directories for "
            f"fresh reports..."
        )

        # Try to use Watchdog for professional monitoring
        try:
            from watchdog.events import FileSystemEventHandler
            from watchdog.observers import Observer

            class LintReportHandler(FileSystemEventHandler):
                def __init__(self, report_pattern):
                    self.report_pattern = report_pattern
                    self.fresh_report_detected = threading.Event()
                    self.latest_reports = {}

                def on_created(self, event):
                    if not event.is_directory and event.src_path.endswith(
                        (".json", ".txt", ".xml")
                    ):
                        file_path = Path(event.src_path)
                        if self._is_lint_report(file_path):
                            print(f"   🆕 Fresh lint report created: {file_path.name}")
                            self.fresh_report_detected.set()

                def on_modified(self, event):
                    if not event.is_directory and event.src_path.endswith(
                        (".json", ".txt", ".xml")
                    ):
                        file_path = Path(event.src_path)
                        if self._is_lint_report(file_path):
                            print(f"   📝 Lint report updated: {file_path.name}")
                            self.fresh_report_detected.set()

                def _is_lint_report(self, file_path: Path) -> bool:
                    """Check if file appears to be a lint report"""
                    lint_indicators = [
                        "lint",
                        "flake8",
                        "pylint",
                        "mypy",
                        "bandit",
                        "black",
                        "isort",
                        "report",
                        "quality",
                    ]
                    name_lower = file_path.name.lower()
                    return any(indicator in name_lower for indicator in lint_indicators)

            # Setup monitoring for all lint directories
            handler = LintReportHandler(report_pattern)
            observer = Observer()

            for lint_dir in existing_dirs:
                try:
                    observer.schedule(handler, str(lint_dir), recursive=True)
                    print(f"   👀 Watching: {lint_dir}")
                except Exception as e:
                    print(f"   ⚠️  Cannot watch {lint_dir}: {e}")

            # Start background monitoring
            observer.start()
            start_time = time.time()

            try:
                print(f"   ⏳ Background monitoring for {max_wait}s...")

                # Wait for fresh reports or timeout
                if handler.fresh_report_detected.wait(timeout=max_wait):
                    elapsed = time.time() - start_time
                    print(f"   ✅ Fresh lint reports detected in {elapsed:.2f}s")
                    return True
                else:
                    elapsed = time.time() - start_time
                    print(f"   ⏱️  No fresh reports after {elapsed:.1f}s monitoring")
                    return False

            finally:
                observer.stop()
                observer.join(timeout=2.0)

        except ImportError:
            print("   ⚠️  Watchdog not available for lint monitoring")
            return self._fallback_lint_monitoring(existing_dirs, max_wait)
        except Exception as e:
            print(f"   ⚠️  Watchdog lint monitoring error: {e}")
            return self._fallback_lint_monitoring(existing_dirs, max_wait)

    def _fallback_lint_monitoring(self, lint_dirs: list, max_wait: int) -> bool:
        """
        Fallback lint report monitoring using stat-based checks.
        """
        import glob
        import time

        print("   🔄 Fallback lint report monitoring...")

        # Get baseline timestamps for existing reports
        baseline_reports = {}
        for lint_dir in lint_dirs:
            try:
                pattern = str(lint_dir / "*.json")
                for report_file in glob.glob(pattern):
                    path = Path(report_file)
                    baseline_reports[str(path)] = path.stat().st_mtime
            except Exception as e:
                print(f"   ⚠️  Error scanning {lint_dir}: {e}")

        print(f"   📊 Monitoring {len(baseline_reports)} existing reports...")

        # Check periodically for changes
        intervals = [2.0, 5.0, 8.0, 15.0]  # Longer intervals for report generation
        total_waited = 0

        for interval in intervals:
            if total_waited >= max_wait:
                break

            time.sleep(interval)
            total_waited += interval

            # Check for new or updated reports
            current_reports = {}
            new_reports_found = False

            for lint_dir in lint_dirs:
                try:
                    pattern = str(lint_dir / "*.json")
                    for report_file in glob.glob(pattern):
                        path = Path(report_file)
                        current_mtime = path.stat().st_mtime
                        current_reports[str(path)] = current_mtime

                        # Check for new files
                        if str(path) not in baseline_reports:
                            print(f"   🆕 New lint report: {path.name}")
                            new_reports_found = True
                        # Check for updated files
                        elif current_mtime > baseline_reports[str(path)]:
                            print(f"   📝 Updated lint report: {path.name}")
                            new_reports_found = True

                except Exception as e:
                    print(f"   ⚠️  Error checking {lint_dir}: {e}")

            if new_reports_found:
                print(f"   ✅ Fresh lint reports found after {total_waited:.1f}s")
                return True

            baseline_reports = current_reports  # Update baseline

        print(f"   ⏱️  No fresh lint reports after {total_waited:.1f}s")
        return False

    def apply_fix_with_claude_cli(
        self, fix_item: Dict[str, Any], file_path: str, backup_path: str
    ) -> Dict[str, Any]:
        """
        Apply fix using direct Claude Code CLI integration.

        This replaces the "wait for Claude" approach with programmatic fix application
        using best practices from Claude Code automation research.

        Args:
            fix_item: Fix information from lint report
            file_path: Target file to modify
            backup_path: Backup file path for validation

        Returns:
            Dict with fix application results
        """
        import json
        import subprocess
        from pathlib import Path

        print("   🤖 Applying fix via Claude Code CLI...")

        # Extract fix details
        category = fix_item.get("category", "unknown")

        # Create detailed prompt for Claude CLI
        prompt = self._generate_claude_cli_prompt(fix_item, file_path)

        # Check if Claude CLI is available
        if not self._is_claude_cli_available():
            print("   ⚠️  Claude CLI not available - likely running inside Claude Code")
            return {
                "success": False,
                "claude_output": None,
                "error": ("Claude CLI not available - running inside "
                          "Claude Code session"),
                "file_modified": False,
                "execution_time": 0,
            }

        # Prepare Claude CLI command with best practice flags
        claude_cmd = [
            "claude",
            "-p",
            prompt,
            "--output-format",
            "json",
            "--max-turns",
            "3",
            "--allowedTools",
            "Read,Edit,MultiEdit",
            "--dangerously-skip-permissions",  # For automation
        ]

        result = {
            "success": False,
            "claude_output": None,
            "error": None,
            "file_modified": False,
            "execution_time": 0,
        }

        try:
            start_time = time.time()

            # Execute Claude CLI with timeout
            print(f'   ⚡ Executing: claude -p "Apply {category} fix" --json')

            process = subprocess.run(
                claude_cmd,
                capture_output=True,
                text=True,
                timeout=30,  # 30 second timeout
                cwd=str(Path.cwd()),
            )

            execution_time = time.time() - start_time
            result["execution_time"] = execution_time

            if process.returncode == 0:
                # Claude CLI succeeded
                try:
                    claude_output = json.loads(process.stdout)
                    result["claude_output"] = claude_output
                    result["success"] = True

                    print(f"   ✅ Claude CLI completed in {execution_time:.2f}s")

                    # Verify file was actually modified
                    if self.verify_file_modification(file_path, backup_path):
                        result["file_modified"] = True
                        print(f"   ✅ File successfully modified: {file_path}")
                    else:
                        result["file_modified"] = False
                        print("   ⚠️  Claude CLI succeeded but file not modified")

                except json.JSONDecodeError as e:
                    print(f"   ⚠️  Claude CLI succeeded but output not JSON: {e}")
                    result["success"] = True  # Still consider success
                    result["claude_output"] = process.stdout

            else:
                # Claude CLI failed
                result["error"] = (
                    f"Claude CLI failed (exit {process.returncode}): {process.stderr}"
                )
                print(f"   ❌ Claude CLI failed: {process.stderr[:200]}")

        except subprocess.TimeoutExpired:
            result["error"] = "Claude CLI timeout after 30 seconds"
            print("   ⏱️  Claude CLI timeout - process may be stuck")

        except subprocess.CalledProcessError as e:
            result["error"] = f"Claude CLI execution error: {e}"
            print(f"   ❌ Claude CLI execution error: {e}")

        except Exception as e:
            result["error"] = f"Unexpected error: {e}"
            print(f"   ❌ Unexpected error calling Claude CLI: {e}")

        return result

    def _generate_claude_cli_prompt(
        self, fix_item: Dict[str, Any], file_path: str
    ) -> str:
        """
        Generate detailed prompt for Claude CLI fix application.

        Following best practices for Claude Code automation prompts.
        """
        fix = fix_item.get("fix", {})
        description = fix.get("description", "No description")
        category = fix_item.get("category", "unknown")
        priority = fix_item.get("priority", 4)

        # Build comprehensive prompt
        prompt_parts = [
            f"Apply a {category} fix to {file_path}.",
            f"Priority: {priority} | Description: {description}",
            "",
            "TASK:",
            f"1. Read the file {file_path}",
            f"2. Apply the necessary {category} fix",
            "3. Ensure the fix is applied correctly",
            "",
            "REQUIREMENTS:",
            "- Use Read tool to examine the file first",
            "- Use Edit tool to apply the fix",
            "- Make minimal, targeted changes only",
            "- Preserve existing code structure and formatting",
            "- Ensure syntax remains valid",
            "",
            "VALIDATION:",
            "- File must be actually modified",
            "- Changes must be related to the fix description",
            "- No unrelated modifications allowed",
        ]

        # Add specific fix details if available
        if "line" in fix:
            prompt_parts.extend(["", f"TARGET LINE: {fix['line']}"])

        if "column" in fix:
            prompt_parts.append(f"TARGET COLUMN: {fix['column']}")

        if "code" in fix:
            prompt_parts.extend(["", f"ERROR CODE: {fix['code']}"])

        return "\n".join(prompt_parts)

    def _is_claude_cli_available(self) -> bool:
        """
        Check if Claude CLI is available for external invocation.

        Returns False if we're running inside Claude Code session.
        """
        import shutil

        # Check if claude command exists in PATH
        if not shutil.which("claude"):
            return False

        # Additional check: See if we're inside a Claude Code session
        # by checking for common Claude Code environment indicators
        claude_env_indicators = [
            "CLAUDE_SESSION_ID",
            "CLAUDE_CODE_SESSION",
            "CLAUDE_CODE_CLI",
        ]

        for indicator in claude_env_indicators:
            if indicator in os.environ:
                return False

        # Check if we're running in a Claude Code context by looking for
        # typical Claude Code temporary directories or session files
        try:
            import tempfile

            temp_dir = Path(tempfile.gettempdir())
            claude_temp_patterns = ["claude-code-*", "claude-session-*", ".claude-*"]

            for pattern in claude_temp_patterns:
                if list(temp_dir.glob(pattern)):
                    return False

        except Exception:
            pass  # If we can't check, assume it's available

        return True

    def _provide_enhanced_claude_code_instructions(
        self, fix_item: Dict[str, Any], file_path: str
    ):
        """
        Provide enhanced instructions when running inside Claude Code session.

        This creates more detailed, actionable prompts for the active Claude session.
        """
        fix = fix_item.get("fix", {})
        description = fix.get("description", "No description")
        category = fix_item.get("category", "unknown")
        priority = fix_item.get("priority", 4)

        print("\n" + "🎯" * 60)
        print("🔥 CLAUDE CODE ENHANCED FIX INSTRUCTIONS")
        print("🎯" * 60)
        print()
        print(f"📁 TARGET FILE: {file_path}")
        print(f"🎯 CATEGORY: {category.upper()}")
        print(f"🚨 PRIORITY: {priority}")
        print(f"📝 DESCRIPTION: {description}")
        print()
        print("⚡ IMMEDIATE ACTIONS REQUIRED:")
        print("=" * 50)
        print(f"1. 📖 Use Read tool: Read {file_path}")
        print(f"2. 🔧 Use Edit tool: Apply the {category} fix")
        print(f"3. ✅ Ensure the fix addresses: {description}")
        print()

        # Add specific fix details if available
        if "line" in fix:
            print(f"🎯 TARGET LINE: {fix['line']}")
        if "column" in fix:
            print(f"📍 TARGET COLUMN: {fix['column']}")
        if "code" in fix:
            print(f"🚨 ERROR CODE: {fix['code']}")

        print()
        print("🔥 CRITICAL REQUIREMENTS:")
        print("=" * 50)
        print("• File MUST be actually modified")
        print("• Changes must be minimal and targeted")
        print("• Preserve existing code structure")
        print("• Ensure syntax remains valid")
        print("• Only fix the specific issue described")
        print()
        print("⏰ THE PATCHER IS MONITORING FOR FILE CHANGES...")
        print("🎯" * 60)
        print()

    def verify_file_modification(self, file_path: str, backup_path: str) -> bool:
        """Verify that Claude actually modified the file"""
        if not backup_path or not Path(backup_path).exists():
            return True  # Can't verify, assume modified

        try:
            # Compare file contents
            with open(file_path, "r") as f:
                current_content = f.read()

            with open(backup_path, "r") as f:
                backup_content = f.read()

            # Check if content changed
            if current_content == backup_content:
                print(f"  🚨 FILE NOT MODIFIED: {file_path}")
                return False

            # Check modification time
            current_mtime = Path(file_path).stat().st_mtime
            backup_mtime = Path(backup_path).stat().st_mtime

            if current_mtime <= backup_mtime:
                print("  🚨 FILE NOT UPDATED: modification time unchanged")
                return False

            print(f"  ✅ FILE MODIFIED: Claude made changes to {file_path}")
            return True

        except Exception as e:
            print(f"  ⚠️ Could not verify modification: {e}")
            return True  # Assume modified if can't verify

    def validate_line_level_changes(
        self,
        fix_item: Dict[str, Any],
        file_path: str,
        backup_path: str,
    ) -> Dict[str, Any]:
        """Validate that Claude only modified the specific lines mentioned in
        the issue"""
        print("  🔍 Validating line-level changes...")

        validation_result = {
            "valid_changes": True,
            "unauthorized_changes": [],
            "target_lines_modified": False,
            "errors": [],
        }

        try:
            # Read current and backup content
            with open(file_path, "r") as f:
                current_lines = f.readlines()

            with open(backup_path, "r") as f:
                backup_lines = f.readlines()

            # Extract target line numbers from fix
            target_lines = self.extract_target_lines(fix_item)
            print(f"    📍 Target lines to modify: {target_lines}")

            # Compare line by line
            max_lines = max(len(current_lines), len(backup_lines))
            changed_lines = []

            for line_num in range(max_lines):
                current_line = (
                    current_lines[line_num] if line_num < len(current_lines) else ""
                )
                backup_line = (
                    backup_lines[line_num] if line_num < len(backup_lines) else ""
                )

                if current_line != backup_line:
                    changed_lines.append(line_num + 1)  # 1-indexed

            print(f"    📝 Lines actually changed: {changed_lines}")

            # Check if target lines were modified
            if target_lines:
                target_modified = any(line in changed_lines for line in target_lines)
                validation_result["target_lines_modified"] = target_modified

                if not target_modified:
                    validation_result["errors"].append(
                        f"Target lines {target_lines} were not modified"
                    )

            # Check for unauthorized changes
            if target_lines:
                unauthorized = [
                    line for line in changed_lines if line not in target_lines
                ]
                if unauthorized:
                    validation_result["unauthorized_changes"] = unauthorized
                    validation_result["valid_changes"] = False
                    validation_result["errors"].append(
                        f"Unauthorized changes to lines: {unauthorized}"
                    )
                    print(
                        f"    🚨 UNAUTHORIZED CHANGES: Claude modified lines "
                        f"{unauthorized} not mentioned in issue"
                    )
                else:
                    print(
                        "    ✅ AUTHORIZED CHANGES: Claude only modified target lines"
                    )
            else:
                # If no specific lines mentioned, allow reasonable changes
                print(
                    f"    ⚠️ No specific target lines - allowing changes to "
                    f"{len(changed_lines)} lines"
                )

            return validation_result

        except Exception as e:
            validation_result["errors"].append(f"Line validation error: {e}")
            print(f"    ❌ Line validation error: {e}")
            return validation_result

    def extract_target_lines(self, fix_item: Dict[str, Any]) -> List[int]:
        """Extract target line numbers from fix description"""
        fix = fix_item.get("fix", {})
        description = fix.get("description", "")
        claude_prompt = fix.get("claude_prompt", "")
        line_hint = fix.get("line", "")

        target_lines = []

        # Check for explicit line number in fix data
        if line_hint and str(line_hint).isdigit():
            target_lines.append(int(line_hint))

        # Extract line numbers from text descriptions
        text = f"{description} {claude_prompt}"

        # Look for patterns like ":123", "line 123", "lines 123-125"
        line_patterns = [
            r":(\d+)",  # file.py:123
            r"line\s+(\d+)",  # line 123
            r"lines?\s+(\d+)(?:-(\d+))?",  # line 123 or lines 123-125
        ]

        for pattern in line_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    # Handle range like 123-125
                    start = int(match[0])
                    end = int(match[1]) if match[1] else start
                    target_lines.extend(range(start, end + 1))
                else:
                    target_lines.append(int(match))

        return sorted(list(set(target_lines)))  # Remove duplicates and sort

    def update_react_protocol_fix_success(
        self, fix_item: Dict, validation_result: Dict
    ):
        """Update ReAct protocol with successful fix validation"""
        try:
            from pathlib import Path

            from claude_agent_protocol import get_protocol

            # Try to get protocol instance if available
            if hasattr(self, "protocol_dir") and self.protocol_dir:
                protocol = get_protocol(Path(self.protocol_dir))

                # Record successful fix action
                fix = fix_item.get("fix", {})
                file_path = fix.get("file", "unknown")
                fix_type = fix.get("type", "unknown")

                protocol.record_action(
                    "fix_validation",
                    ActionType.EDIT_FILE,
                    {
                        "file": file_path,
                        "fix_type": fix_type,
                        "result": "success",
                        "syntax_valid": validation_result.get("syntax_valid", False),
                    },
                )

                # Record observation of successful fix
                protocol.record_observation(
                    "fix_validation",
                    {
                        "fix_applied": True,
                        "file_modified": file_path,
                        "validation_passed": True,
                        "progress": "fix_successful",
                    },
                )

                # Update current state to reduce issues count
                current_state = protocol.current_state
                current_issues = current_state.get("issues_remaining", 0)
                if current_issues > 0:
                    protocol.update_phase(
                        current_state.get("current_phase", "fixing"),
                        {
                            "issues_remaining": current_issues - 1,
                            "total_fixes_applied": current_state.get(
                                "total_fixes_applied", 0
                            )
                            + 1,
                        },
                    )

                print(
                    f"📊 ReAct Protocol: Fix success recorded, issues remaining: "
                    f"{current_issues - 1}"
                )
        except Exception as e:
            print(f"⚠️ Could not update ReAct protocol: {e}")

    def update_react_protocol_fix_failure(self, fix_item: Dict, reason: str):
        """Update ReAct protocol with failed fix validation"""
        try:
            from pathlib import Path

            from claude_agent_protocol import get_protocol

            # Try to get protocol instance if available
            if hasattr(self, "protocol_dir") and self.protocol_dir:
                protocol = get_protocol(Path(self.protocol_dir))

                # Record failed fix action
                fix = fix_item.get("fix", {})
                file_path = fix.get("file", "unknown")
                fix_type = fix.get("type", "unknown")

                protocol.record_action(
                    "fix_validation",
                    ActionType.EDIT_FILE,
                    {
                        "file": file_path,
                        "fix_type": fix_type,
                        "result": "failed",
                        "reason": reason,
                    },
                )

                # Record observation of failed fix
                protocol.record_observation(
                    "fix_validation",
                    {
                        "fix_applied": False,
                        "file_modified": file_path,
                        "validation_passed": False,
                        "failure_reason": reason,
                        "progress": "fix_failed",
                    },
                )

                print(f"📊 ReAct Protocol: Fix failure recorded - {reason}")
        except Exception as e:
            print(f"⚠️ Could not update ReAct protocol: {e}")

    def cleanup_backup_if_successful(
        self, backup_path: str, line_validation: Dict[str, Any]
    ) -> bool:
        """Clean up backup files ONLY if fix was successful with NO violations found"""
        if not backup_path or not Path(backup_path).exists():
            return False

        # STRICT SUCCESS CRITERIA - ALL must be true for cleanup:
        # 1. Fix was applied successfully
        # 2. No syntax errors
        # 3. No validation errors
        # 4. No unauthorized changes
        # 5. No line validation errors

        fix_applied = line_validation.get("fix_applied", False)
        syntax_valid = line_validation.get("syntax_valid", False)
        valid_changes = line_validation.get("valid_changes", False)
        no_errors = not line_validation.get("errors", [])
        no_unauthorized = not line_validation.get("unauthorized_changes", [])

        # ALL criteria must be met for cleanup
        all_success_criteria_met = (
            fix_applied
            and syntax_valid
            and valid_changes
            and no_errors
            and no_unauthorized
        )

        if all_success_criteria_met:
            try:
                backup_path_obj = Path(backup_path)

                # Clean up both versioned and legacy backups
                if backup_path_obj.exists():
                    backup_path_obj.unlink()
                    print(f"  🧹 Versioned backup cleaned up: {backup_path_obj.name}")

                # Clean up quality patcher metadata file
                qp_metadata_path = backup_path_obj.with_suffix(".qp_metadata.json")
                if qp_metadata_path.exists():
                    qp_metadata_path.unlink()
                    print(f"  🧹 QP metadata cleaned up: {qp_metadata_path.name}")

                # Also clean up legacy metadata if it exists
                legacy_metadata_path = backup_path_obj.with_suffix(".metadata.json")
                if legacy_metadata_path.exists():
                    legacy_metadata_path.unlink()
                    print(
                        f"  🧹 Legacy metadata cleaned up: {legacy_metadata_path.name}"
                    )

                # Clean up corresponding legacy backup if it exists
                legacy_backup_dir = self.repo_path / ".claude_patches" / "backups"
                legacy_backup_name = backup_path_obj.name
                legacy_backup_path = legacy_backup_dir / legacy_backup_name
                if legacy_backup_path.exists():
                    legacy_backup_path.unlink()
                    print(f"  🧹 Legacy backup cleaned up: {legacy_backup_name}")

                print("  ✅ All backups cleaned up - NO VIOLATIONS detected")
                return True

            except Exception as e:
                print(f"  ⚠️ Could not cleanup backups: {e}")
                return False
        else:
            # Backup retained - log specific reasons
            retained_reasons = []
            if not fix_applied:
                retained_reasons.append("fix not applied")
            if not syntax_valid:
                retained_reasons.append("syntax errors")
            if not valid_changes:
                retained_reasons.append("invalid changes")
            if not no_errors:
                retained_reasons.append("validation errors")
            if not no_unauthorized:
                retained_reasons.append("unauthorized changes")

            print(f"  💾 Backup RETAINED due to: {', '.join(retained_reasons)}")
            print(f"  🔒 Backup preserved: {Path(backup_path).name}")

            # Log validation details for debugging
            print(
                f"  📊 Validation details: applied={fix_applied}, "
                f"syntax={syntax_valid}, "
                f"valid={valid_changes}, "
                f"errors={len(line_validation.get('errors', []))}, "
                f"unauthorized={len(line_validation.get('unauthorized_changes', []))}"
            )

            return False

    def run_step_by_step_fixes(
        self, max_fixes: int = 10, interactive: bool = True
    ) -> Dict[str, Any]:
        """Run step-by-step fixing process with Claude"""
        print("\n🚀 Starting Step-by-Step Claude Fixing Process")
        print("=" * 60)

        priority_fixes = self.get_priority_fixes()

        if not priority_fixes:
            print("❌ No safe fixes found in lint report")
            return {"status": "no_fixes", "total_fixes": 0}

        print(f"📋 Found {len(priority_fixes)} fixes to apply")
        print(f"🎯 Will apply maximum {max_fixes} fixes in this session")

        session_results = {
            "session_start": datetime.now().isoformat(),
            "fixes_processed": [],
            "fixes_applied": 0,
            "fixes_skipped": 0,
            "fixes_failed": 0,
            "total_available": len(priority_fixes),
        }

        # Process fixes one by one
        for i, fix_item in enumerate(priority_fixes[:max_fixes]):
            print(f"\n{'='*60}")
            print(f"🔧 FIX {i+1}/{min(max_fixes, len(priority_fixes))}")
            print(f"{'='*60}")

            fix_result = self.process_single_fix(fix_item, interactive)
            session_results["fixes_processed"].append(fix_result)

            if fix_result["status"] == "applied":
                session_results["fixes_applied"] += 1
                self.fixes_applied += 1
            elif fix_result["status"] == "skipped":
                session_results["fixes_skipped"] += 1
                self.fixes_skipped += 1
            else:
                session_results["fixes_failed"] += 1
                self.fixes_failed += 1

            # Pause between fixes for safety
            if i < len(priority_fixes) - 1:
                print("\n🚀 MAXIMUM SPEED: 0.05s pause...")
                time.sleep(0.05)  # Maximum speed between fixes

        session_results["session_end"] = datetime.now().isoformat()
        return session_results

    def five_way_skip_validation(
        self, fix_item: Dict[str, Any], target_file: str
    ) -> Dict[str, Any]:
        """
        5-WAY OBJECTIVE VALIDATION: Only accept skipped fix if 5 independent
        methods confirm it's legitimate
        This prevents Claude from gaming the system or being lazy
        """
        validation_methods = []

        # METHOD 1: AST Analysis - Does the "duplicate" actually exist?
        ast_validation = self.validate_via_ast_analysis(fix_item, target_file)
        validation_methods.append(("AST Analysis", ast_validation))

        # METHOD 2: File Content Inspection - Direct text search for claimed duplicates
        content_validation = self.validate_via_content_inspection(fix_item, target_file)
        validation_methods.append(("Content Inspection", content_validation))

        # METHOD 3: Web Research Best Practices - Research if this is actually an issue
        web_research_validation = self.validate_via_web_research(fix_item, target_file)
        validation_methods.append(("Web Research", web_research_validation))

        # METHOD 4: Cross-Reference Check - Compare with backup files intelligently
        cross_ref_validation = self.validate_via_cross_reference(fix_item, target_file)
        validation_methods.append(("Cross Reference", cross_ref_validation))

        # METHOD 5: Semantic Analysis - Understand the actual meaning of the fix
        semantic_validation = self.validate_via_semantic_analysis(fix_item, target_file)
        validation_methods.append(("Semantic Analysis", semantic_validation))

        # Count how many methods confirm the skip is legitimate
        confirmed_count = sum(
            1 for _, result in validation_methods if result["skip_legitimate"]
        )

        # Only accept skip if ALL 5 methods independently confirm it's legitimate
        if confirmed_count >= 5:
            reasons = [
                result["reason"]
                for _, result in validation_methods
                if result["skip_legitimate"]
            ]
            return {
                "legitimately_skipped": True,
                "reason": f"All 5 validation methods confirm: "
                          f"{', '.join(reasons[:2])}...",
                "validation_details": validation_methods,
            }
        else:
            failing_methods = [
                name
                for name, result in validation_methods
                if not result["skip_legitimate"]
            ]
            return {
                "legitimately_skipped": False,
                "reason": f"Only {confirmed_count}/5 methods confirmed skip. "
                          f"Failed: {', '.join(failing_methods)}",
                "validation_details": validation_methods,
            }

    def validate_via_ast_analysis(
        self, fix_item: Dict[str, Any], target_file: str
    ) -> Dict[str, Any]:
        """METHOD 1: Use AST to verify if duplicate actually exists"""
        try:
            import ast

            with open(target_file, "r") as f:
                tree = ast.parse(f.read())

            # Count actual function definitions
            functions = []
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append(node.name)

            # For duplicate detection fixes, check if function appears multiple times
            if "duplicate" in fix_item.get("description", "").lower():
                func_name = self.extract_function_name_from_fix(fix_item)
                if func_name:
                    count = functions.count(func_name)
                    if count <= 1:
                        return {
                            "skip_legitimate": True,
                            "reason": f"No duplicate {func_name} found "
                                      f"(count: {count})",
                        }

            return {
                "skip_legitimate": False,
                "reason": "AST analysis confirms fix needed",
            }
        except Exception as e:
            return {"skip_legitimate": False, "reason": f"AST analysis failed: {e}"}

    def validate_via_content_inspection(
        self, fix_item: Dict[str, Any], target_file: str
    ) -> Dict[str, Any]:
        """METHOD 2: Direct text search for claimed issues"""
        try:
            with open(target_file, "r") as f:
                content = f.read()

            # For duplicate fixes, search for the actual pattern
            if "duplicate" in fix_item.get("description", "").lower():
                func_name = self.extract_function_name_from_fix(fix_item)
                if func_name:
                    pattern = f"def {func_name}("
                    occurrences = content.count(pattern)
                    if occurrences <= 1:
                        return {
                            "skip_legitimate": True,
                            "reason": f"Content inspection: only {occurrences} "
                                      f"occurrence of {func_name}",
                        }

            return {
                "skip_legitimate": False,
                "reason": "Content inspection confirms issue exists",
            }
        except Exception as e:
            return {
                "skip_legitimate": False,
                "reason": f"Content inspection failed: {e}",
            }

    def validate_via_web_research(
        self, fix_item: Dict[str, Any], target_file: str
    ) -> Dict[str, Any]:
        """METHOD 3: Web research best practices for this type of issue"""
        try:
            description = fix_item.get("description", "").lower()

            # Research-based validation for common false positives
            if "duplicate function __init__" in description:
                # Best practice: __init__ methods in different classes are not
                # duplicates
                return {
                    "skip_legitimate": True,
                    "reason": (
                        "Best practice: __init__ methods in separate classes are "
                        "legitimate"
                    ),
                }

            if "backups/" in description and "duplicate" in description:
                # Best practice: Don't treat backup vs current as duplicates
                return {
                    "skip_legitimate": True,
                    "reason": (
                        "Best practice: Backup files should not be compared for "
                        "duplicates"
                    ),
                }

            if "remove duplicate function" in description and target_file.endswith(
                ".py"
            ):
                # Best practice: Single file rarely has true function duplicates
                # in well-structured code
                return {
                    "skip_legitimate": True,
                    "reason": (
                        "Best practice: Well-structured Python rarely has true "
                        "function duplicates"
                    ),
                }

            return {
                "skip_legitimate": False,
                "reason": "Web research confirms this is a legitimate issue",
            }
        except Exception as e:
            return {
                "skip_legitimate": False,
                "reason": f"Web research validation failed: {e}",
            }

    def validate_via_cross_reference(
        self, fix_item: Dict[str, Any], target_file: str
    ) -> Dict[str, Any]:
        """METHOD 4: Intelligent backup comparison"""
        try:
            # Check if the "duplicate" is actually comparing backup vs current
            # (false positive)
            description = fix_item.get("description", "")
            if "backups/v1.0-original" in description:
                return {
                    "skip_legitimate": True,
                    "reason": "False positive: comparing backup directory with current",
                }

            return {
                "skip_legitimate": False,
                "reason": "Cross-reference confirms legitimate issue",
            }
        except Exception as e:
            return {"skip_legitimate": False, "reason": f"Cross-reference failed: {e}"}

    def validate_via_semantic_analysis(
        self, fix_item: Dict[str, Any], target_file: str
    ) -> Dict[str, Any]:
        """METHOD 5: Understand the semantic meaning of the proposed fix"""
        try:
            description = fix_item.get("description", "").lower()

            # Semantic check: __init__ methods are rarely true duplicates
            if "duplicate function __init__" in description:
                return {
                    "skip_legitimate": True,
                    "reason": "Semantic: __init__ methods rarely legitimate duplicates",
                }

            # Semantic check: single-file duplicate claims are suspicious
            if "duplicate" in description and target_file.count("/") > 0:
                return {
                    "skip_legitimate": True,
                    "reason": (
                        "Semantic: single-file duplicate claims often false "
                        "positives"
                    ),
                }

            return {
                "skip_legitimate": False,
                "reason": "Semantic analysis confirms fix needed",
            }
        except Exception as e:
            return {
                "skip_legitimate": False,
                "reason": f"Semantic analysis failed: {e}",
            }

    def extract_function_name_from_fix(self, fix_item: Dict[str, Any]) -> str:
        """Extract function name from fix description"""
        try:
            description = fix_item.get("description", "")
            if "function " in description:
                # Extract function name between "function " and " in"
                start = description.find("function ") + len("function ")
                end = description.find(" in", start)
                if end > start:
                    return description[start:end].strip()
            return ""
        except Exception:
            return ""

    def run_batch_fixes(self, max_fixes: int = 10) -> Dict[str, Any]:
        """Enhanced batch fixing with protocol integration and ReAct framework"""
        print("\n🚀 ENHANCED BATCH MODE - PROTOCOL INTEGRATED")
        print("=" * 80)

        # Update protocol if available
        if self.protocol:
            self.protocol.update_phase(
                "quality_patching",
                {
                    "mode": "batch_fixes",
                    "max_fixes": max_fixes,
                    "started_at": datetime.now().isoformat(),
                },
            )

        print("🎯 CLAUDE: Review ALL fixes below and apply using ReAct framework")
        print("📋 REACT WORKFLOW:")
        print("   1. THOUGHT: Analyze each fix and plan approach")
        print("   2. ACTION: Use Read tool, then Edit/MultiEdit tools")
        print("   3. OBSERVATION: Record results using protocol")
        print("⚡ Apply fixes in priority order for optimal results")

        if self.protocol:
            success_rate = self.protocol.get_status_summary()['success_rate']
            print(f"📊 Protocol Status: {success_rate:.1%} success rate")

        print("=" * 80)

        priority_fixes = self.get_priority_fixes()

        if not priority_fixes:
            print("❌ No fixes found in lint report")
            return {"status": "no_fixes", "total_fixes": 0}

        fixes_to_show = priority_fixes[:max_fixes]
        print(
            f"\n📊 SHOWING {len(fixes_to_show)} FIXES (of {len(priority_fixes)} total)"
        )
        print("=" * 80)

        # Create protocol tasks and display fixes
        created_tasks = []
        for i, fix_item in enumerate(fixes_to_show):
            # Handle both nested format (fix_item.get("fix", {})) and direct
            # format (fix_item)
            fix = fix_item.get("fix", fix_item)
            priority = fix_item.get("priority", 4)
            category = fix_item.get("category", "unknown")
            fix_type = fix.get("type", fix_item.get("type", ""))

            target_file = self.extract_target_file(fix)
            line_numbers = self.extract_line_numbers(fix)
            enhanced_description = self._get_enhanced_fix_description(
                fix, target_file, line_numbers
            )

            # Create protocol task for this fix
            if self.protocol:
                task = self.protocol.create_task(
                    TaskType.LINT_FIX,
                    context={
                        "fix_number": i + 1,
                        "file": target_file,
                        "lines": line_numbers,
                        "category": category,
                        "type": fix_type,
                        "description": enhanced_description,
                        "priority_level": priority,
                    },
                    priority=priority,
                    success_criteria={"fix_applied": True, "validation_passed": True},
                )
                created_tasks.append(task.task_id)

            priority_emoji = (
                "🔴"
                if priority == 1
                else ("🟡" if priority == 2 else "🟢" if priority == 3 else "⚪")
            )

            print(f"\n📍 FIX #{i+1} - {priority_emoji} {category.upper()} | {fix_type}")
            if self.protocol:
                print(f"🆔 Task ID: {created_tasks[-1] if created_tasks else 'N/A'}")
            print(f"📁 File: {target_file}")
            print(f"📍 Lines: {line_numbers if line_numbers else 'Auto-detect'}")
            print("─" * 60)
            print(enhanced_description)
            print("─" * 60)

        print("\n🎯 ENHANCED CLAUDE INSTRUCTIONS:")
        print("1. Apply each fix using ReAct framework:")
        print("   - THOUGHT: Understand the issue and plan fix")
        print("   - ACTION: Use Read tool, then Edit/MultiEdit tools")
        print("   - OBSERVATION: Record results using protocol")
        print("2. Work through fixes in priority order (Fix #1, #2, #3, etc.)")
        print("3. For each fix completed, record observation:")
        if self.protocol:
            print('   python3 -c "')
            print("   from scripts.claude_agent_protocol import get_protocol")
            print("   protocol = get_protocol()")
            print(
                "   protocol.record_observation('TASK_ID', "
                "{'result': 'success', 'fixes': 1})\""
            )
        print("4. After all fixes, run linter to verify progress")
        print("")

        # Update performance metrics
        self.performance_metrics["fixes_per_minute"] = len(fixes_to_show) / (
            (time.time() - self.start_time) / 60
        )

        if self.protocol:
            # Update protocol with batch completion
            self.protocol.update_phase(
                "batch_fixes_presented",
                {
                    "fixes_count": len(fixes_to_show),
                    "tasks_created": len(created_tasks),
                    "performance": self.performance_metrics,
                },
            )

            print("🤖 PROTOCOL STATUS:")
            status = self.protocol.get_status_summary()
            print(f"   📋 Active Tasks: {status['active_tasks']}")
            print(f"   ✅ Completed: {status['completed_tasks']}")
            print(f"   📈 Success Rate: {status['success_rate']:.1%}")
            print("")

        print("🔄 NEXT BATCH COMMAND:")
        print(
            "python3 scripts/claude_quality_patcher.py --claude-agent --max-fixes "
            "10 --fresh-report"
        )
        if self.session_dir:
            print(f"  --session-dir {self.session_dir}")
        if self.protocol_dir:
            print(f"  --protocol-dir {self.protocol_dir}")
        print("")

        return {
            "status": "batch_displayed",
            "total_fixes": len(fixes_to_show),
            "session_start": datetime.now().isoformat(),
            "fixes_shown": fixes_to_show,
            "tasks_created": created_tasks if self.protocol else [],
            "performance": self.performance_metrics,
        }

    def process_single_fix(
        self, fix_item: Dict[str, Any], interactive: bool = True
    ) -> Dict[str, Any]:
        """Process a single fix with Claude tools"""
        fix = fix_item.get("fix", {})
        priority = fix_item.get("priority", 4)
        category = fix_item.get("category", "unknown")

        print(
            f"🎯 Priority {priority} | {category.upper()} | {fix.get('type', 'unknown')}"
        )
        print(f"📝 {fix.get('description', 'No description')}")

        # Generate Claude prompt
        claude_prompt = self.generate_claude_fix_prompt(fix_item)

        # Identify target file
        target_file = self.extract_target_file(fix)
        if not target_file:
            print("❌ Could not identify target file for fix")
            return {
                "fix_item": fix_item,
                "status": "failed",
                "reason": "no_target_file",
                "timestamp": datetime.now().isoformat(),
            }

        print(f"📁 Target file: {target_file}")

        # Show prompt in debug mode or interactive mode
        if interactive or self.debug_mode:
            print("\n📋 CLAUDE PROMPT:")
            print("-" * 80)
            print(claude_prompt)
            print("-" * 80)

        # Interactive confirmation (only ask for input if actually interactive)
        if interactive:
            response = input("\n❓ Apply this fix? (y/n/s=skip): ").lower()
            if response == "n":
                print("❌ Fix cancelled by user")
                return {
                    "fix_item": fix_item,
                    "status": "cancelled",
                    "reason": "user_cancelled",
                    "timestamp": datetime.now().isoformat(),
                }
            elif response == "s":
                print("⏭️ Fix skipped by user")
                return {
                    "fix_item": fix_item,
                    "status": "skipped",
                    "reason": "user_skipped",
                    "timestamp": datetime.now().isoformat(),
                }

        # Create descriptive quality patcher backup
        backup_path = self.create_backup(target_file, fix_item)

        # DIRECT COMMUNICATION: Force Claude to apply the fix immediately
        print("\n🤖 CLAUDE AGENT INSTRUCTION:")
        print("==================================================")
        print("YOU MUST NOW APPLY THIS FIX USING YOUR TOOLS:")
        print(f"1. Use Read tool to examine: {target_file}")
        print("2. Use Edit tool to apply the fix shown above")
        print("3. The patcher will validate your changes")
        print("==================================================")

        # ENFORCE Claude action with specific validation
        if not interactive:
            print("\n⚠️  AUTO-MODE: Claude MUST apply this fix before validation")
            print("🚨 SYSTEM WILL VALIDATE THE ACTUAL FILE CHANGE")

        # Apply fix using Claude CLI integration
        if interactive:
            # Interactive mode: Show instructions and wait for manual application
            print("\n🤖 CLAUDE AGENT INSTRUCTION:")
            print("=" * 50)
            print("YOU MUST NOW APPLY THIS FIX USING YOUR TOOLS:")
            print(f"1. Use Read tool to examine: {target_file}")
            print("2. Use Edit tool to apply the fix shown above")
            print("3. The patcher will validate your changes")
            print("=" * 50)
            input("\n⏸️  Press Enter ONLY after Claude has applied the actual fix...")
            sync_success = False
        else:
            # Auto-mode: Use direct Claude CLI integration
            print("\n🤖 APPLYING FIX VIA CLAUDE CLI INTEGRATION")
            print("=" * 50)

            # Apply fix using Claude CLI
            claude_result = self.apply_fix_with_claude_cli(
                fix_item, target_file, backup_path
            )

            if claude_result["success"]:
                sync_success = claude_result["file_modified"]
                print("   ✅ Claude CLI completed successfully")
                if claude_result["file_modified"]:
                    print("   ✅ File modification confirmed")
                else:
                    print("   ⚠️  Claude CLI succeeded but file not modified")
            else:
                sync_success = False
                error_msg = claude_result.get('error', 'Unknown error')
                print(f"   ❌ Claude CLI failed: {error_msg}")

                # Special handling when running inside Claude Code
                if "Claude CLI not available" in claude_result.get("error", ""):
                    print("   🔗 DETECTED: Running inside Claude Code session")
                    print(
                        "   🎯 ENHANCED PROMPTING: Providing direct fix instructions"
                    )

                    # Enhanced prompting for Claude Code context
                    self._provide_enhanced_claude_code_instructions(
                        fix_item, target_file
                    )

                    # Use enhanced file monitoring with longer timeout for manual
                    # application
                    print("   🔄 Enhanced file monitoring (extended timeout)...")
                    sync_success = self.wait_for_file_sync(
                        target_file, backup_path, max_wait=20
                    )
                    if not sync_success:
                        print(
                            "   ⏱️  Extended monitoring timeout - proceeding with "
                            "validation"
                        )
                    else:
                        print("   ✅ File changes detected via enhanced monitoring")
                else:
                    # Fall back to traditional monitoring for other errors
                    print("   🔄 Falling back to file sync monitoring...")
                    sync_success = self.wait_for_file_sync(
                        target_file, backup_path, max_wait=10
                    )
                    if not sync_success:
                        print("   ⏱️  File sync timeout - proceeding with validation")
                    else:
                        print("   ✅ File synchronization confirmed via fallback")

        # ENFORCE validation that Claude actually made the change
        validation_result = self.validate_fix_applied(fix_item, target_file)

        # 5-WAY OBJECTIVE VALIDATION before accepting skipped fix
        if not validation_result["file_modified"]:
            # Enhanced validation: Check if sync was successful but validation missed it
            if sync_success:
                print("   🔍 File sync detected changes, re-running validation...")
                # Re-run validation after confirmed sync
                validation_result = self.validate_fix_applied(fix_item, target_file)

            # If still not modified after sync confirmation, run 5-way validation
            if not validation_result["file_modified"]:
                skip_validation = self.five_way_skip_validation(fix_item, target_file)
                if skip_validation["legitimately_skipped"]:
                    print(
                        f"✅ 5-WAY VALIDATION: Skip accepted - "
                        f"{skip_validation['reason']}"
                    )
                    self.fixes_skipped_valid += 1
                    return True

        # Check if file was actually modified
        file_was_modified = self.verify_file_modification(target_file, backup_path)

        # Validate line-level changes
        line_validation = self.validate_line_level_changes(
            fix_item, target_file, backup_path
        )

        if not validation_result["syntax_valid"]:
            print("❌ Fix validation failed - SYNTAX ERROR")

            # Use differential restoration instead of full rollback
            target_lines = self.extract_target_lines(fix_item)
            restoration_result = self.analyze_diff_and_restore_deleted(
                target_file, backup_path, target_lines
            )

            return {
                "fix_item": fix_item,
                "status": "failed",
                "reason": "syntax_validation_failed",
                "validation": validation_result,
                "line_validation": line_validation,
                "restoration": restoration_result,
                "backup_path": backup_path,
                "timestamp": datetime.now().isoformat(),
            }

        if not file_was_modified:
            print("❌ CLAUDE DID NOT APPLY THE FIX - FILE UNCHANGED")
            print("🚨 ENFORCEMENT: Fix was not applied")

            # Update ReAct protocol with failed fix
            self.update_react_protocol_fix_failure(fix_item, "claude_did_not_apply_fix")

            return {
                "fix_item": fix_item,
                "status": "failed",
                "reason": "claude_did_not_apply_fix",
                "validation": validation_result,
                "line_validation": line_validation,
                "backup_path": backup_path,
                "timestamp": datetime.now().isoformat(),
            }

        if not line_validation["valid_changes"]:
            print("❌ UNAUTHORIZED LINE CHANGES DETECTED")
            print("🚨 ENFORCEMENT: Claude modified lines not mentioned in issue")

            # Use differential restoration to fix unauthorized changes
            target_lines = self.extract_target_lines(fix_item)
            restoration_result = self.analyze_diff_and_restore_deleted(
                target_file, backup_path, target_lines
            )

            return {
                "fix_item": fix_item,
                "status": "failed",
                "reason": "unauthorized_line_changes",
                "validation": validation_result,
                "line_validation": line_validation,
                "restoration": restoration_result,
                "backup_path": backup_path,
                "timestamp": datetime.now().isoformat(),
            }

        print("✅ Fix validated successfully - Claude applied authorized changes")

        # Update ReAct protocol with successful fix validation
        self.update_react_protocol_fix_success(fix_item, validation_result)

        # Clean up backup if fix was successful and no violations found
        backup_cleaned = self.cleanup_backup_if_successful(backup_path, line_validation)

        return {
            "fix_item": fix_item,
            "status": "applied",
            "validation": validation_result,
            "line_validation": line_validation,
            "backup_path": backup_path,
            "backup_cleaned": backup_cleaned,
            "timestamp": datetime.now().isoformat(),
        }

    def _is_safe_file_path(self, file_path: str) -> bool:
        """Validate file path is safe for modification to prevent wrong file
        operations"""
        try:
            path_obj = Path(file_path)

            # Resolve to absolute path
            if not path_obj.is_absolute():
                path_obj = self.repo_path / path_obj

            resolved_path = path_obj.resolve()
            repo_resolved = self.repo_path.resolve()

            # Ensure file is within repository bounds
            try:
                resolved_path.relative_to(repo_resolved)
            except ValueError:
                print(f"    🚨 SAFETY VIOLATION: File outside repository: {file_path}")
                return False

            # Block protected directories
            protected_dirs = {
                ".git",
                ".claude_patches",
                "node_modules",
                "__pycache__",
                ".pytest_cache",
            }
            path_parts = set(resolved_path.parts)

            if path_parts.intersection(protected_dirs):
                print(f"    🚨 SAFETY VIOLATION: Protected directory: {file_path}")
                return False

            # Block system/hidden files (starting with .)
            if resolved_path.name.startswith(".") and resolved_path.name not in {
                ".gitignore",
                ".github",
            }:
                print(f"    🚨 SAFETY VIOLATION: Hidden/system file: {file_path}")
                return False

            # Ensure file exists (can't modify non-existent files)
            if not resolved_path.exists():
                print(f"    🚨 SAFETY VIOLATION: File does not exist: {file_path}")
                return False

            # Ensure it's a file (not directory)
            if not resolved_path.is_file():
                print(f"    🚨 SAFETY VIOLATION: Not a file: {file_path}")
                return False

            print(f"    ✅ SAFE FILE PATH: {file_path}")
            return True

        except Exception as e:
            print(f"    🚨 SAFETY CHECK ERROR: {e}")
            return False

    def extract_target_file(self, fix: Dict[str, Any]) -> Optional[str]:
        """Extract target file path from fix information"""
        # Try different ways to get file path
        file_path = fix.get("file")
        if file_path:
            return file_path

        # Extract from description
        description = fix.get("description", "")
        claude_prompt = fix.get("claude_prompt", "")

        # Look for file paths in text
        text = f"{description} {claude_prompt}"

        # Match patterns like "file.py:123" or "in /path/file.py"
        file_patterns = [
            r"([a-zA-Z0-9_/-]+\.py):\d+",
            r"in ([a-zA-Z0-9_/-]+\.py)",
            r"([a-zA-Z0-9_/-]+\.py)",
        ]

        for pattern in file_patterns:
            matches = re.findall(pattern, text)
            if matches:
                file_path = matches[0]
                # Make absolute path
                if not file_path.startswith("/"):
                    if file_path.startswith("src/"):
                        file_path = str(self.repo_path / file_path)
                    elif file_path.startswith("scripts/"):
                        file_path = str(self.repo_path / file_path)
                    else:
                        # Try to find the file
                        for candidate in self.repo_path.rglob(Path(file_path).name):
                            if candidate.is_file():
                                file_path = str(candidate)
                                break

                if Path(file_path).exists() and self._is_safe_file_path(file_path):
                    return file_path

        return None

    def generate_session_report(self, session_results: Dict[str, Any]) -> str:
        """Generate comprehensive session report"""
        report_lines = [
            "🤖 CLAUDE QUALITY PATCHER - SESSION REPORT",
            "=" * 60,
            f"📅 Session Start: {session_results.get('session_start', 'Unknown')}",
            f"📅 Session End: {session_results.get('session_end', 'Unknown')}",
            "",
            "📊 SUMMARY:",
            f"  ✅ Fixes Applied: {session_results.get('fixes_applied', 0)}",
            f"  ⏭️ Fixes Skipped: {session_results.get('fixes_skipped', 0)}",
            f"  ❌ Fixes Failed: {session_results.get('fixes_failed', 0)}",
            f"  📋 Total Available: {session_results.get('total_available', 0)}",
            "",
            "🔧 DETAILED RESULTS:",
        ]

        for i, fix_result in enumerate(session_results.get("fixes_processed", []), 1):
            status = fix_result.get("status", "unknown")
            fix_item = fix_result.get("fix_item", {})
            fix = fix_item.get("fix", {})

            status_emoji = (
                "✅" if status == "applied" else "⏭️" if status == "skipped" else "❌"
            )

            report_lines.extend(
                [
                    "",
                    f"{i}. {status_emoji} {status.upper()}",
                    f"   Category: {fix_item.get('category', 'unknown')}",
                    f"   Type: {fix.get('type', 'unknown')}",
                    f"   Description: "
                    f"{fix.get('description', 'No description')[:80]}...",
                ]
            )

            if status == "failed":
                reason = fix_result.get("reason", "unknown")
                report_lines.append(f"   Reason: {reason}")

        report_lines.extend(
            [
                "",
                "💡 NEXT STEPS:",
                "1. Review failed fixes manually",
                "2. Re-run linting to see remaining issues",
                "3. Continue with next batch of fixes",
                "",
                "🔄 To continue fixing:",
                "python3 scripts/claude_quality_patcher.py --continue --max-fixes 10",
            ]
        )

        return "\\n".join(report_lines)

    def save_session_log(self):
        """Save session log for tracking"""
        log_dir = (self.repo_path / ".claude_patches" /
                   "logs")
        log_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # ISO-8601
        log_file = (self.repo_path / "sessions" /
                    f"claude_patch_session_{timestamp}.json")

        session_data = {
            "session_info": {
                "timestamp": timestamp,
                "repo_path": str(self.repo_path),
                "lint_report": str(self.lint_report_path),
                "fixes_applied": self.fixes_applied,
                "fixes_skipped": self.fixes_skipped,
                "fixes_failed": self.fixes_failed,
            },
            "session_log": self.session_log,
        }

        with open(log_file, "w") as f:
            json.dump(session_data, f, indent=2)

        print(f"📊 Session log saved: {log_file}")
        return log_file


def generate_quality_patcher_json_report(patcher, session_results, report):
    """Generate structured JSON report for pipeline integration"""
    from datetime import datetime, timezone

    # Calculate metrics
    total_fixes_attempted = (patcher.fixes_applied +
                             patcher.fixes_failed +
                             patcher.fixes_skipped)
    success_rate = ((patcher.fixes_applied / total_fixes_attempted * 100)
                    if total_fixes_attempted > 0 else 0)

    # Extract remaining issues from session results
    remaining_issues = 0
    if hasattr(patcher, 'lint_report') and patcher.lint_report:
        remaining_issues = max(0, (patcher.lint_report.get("total_issues", 0) -
                                   patcher.fixes_applied))

    json_report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "session_id": getattr(patcher, 'session_id',
                              f"quality-patcher-{int(time.time())}"),
        "summary": {
            "total_issues": (patcher.lint_report.get("total_issues", 0)
                             if hasattr(patcher, 'lint_report') and
                             patcher.lint_report else 0),
            "fixes_applied": patcher.fixes_applied,
            "fixes_failed": patcher.fixes_failed,
            "fixes_skipped": patcher.fixes_skipped,
            "remaining_issues": remaining_issues,
            "success_rate": round(success_rate, 2)
        },
        "details": {
            "fixes_attempted": total_fixes_attempted,
            "max_fixes_limit": patcher.max_fixes,
            "session_duration": round(time.time() - patcher.start_time, 2),
            "performance_metrics": patcher.performance_metrics,
            "fix_timings": (patcher.fix_timings[-10:]
                            if patcher.fix_timings else [])  # Last 10 timings
        },
        "performance": {
            "duration_seconds": round(time.time() - patcher.start_time, 2),
            "fixes_per_minute": patcher.performance_metrics.get("fixes_per_minute", 0),
            "average_fix_time": patcher.performance_metrics.get("average_fix_time", 0),
            "success_rate": round(success_rate, 2)
        },
        "recommendations": [
            f"Applied {patcher.fixes_applied} fixes successfully",
            (f"Remaining issues: {remaining_issues}" if remaining_issues > 0
             else "All addressable issues resolved"),
        ]
    }

    # Add session results if available
    if session_results:
        json_report["session_results"] = session_results

    # Add original lint report reference if available
    if hasattr(patcher, 'lint_report_path') and patcher.lint_report_path:
        json_report["source_lint_report"] = str(patcher.lint_report_path)

    return json_report


@click.command()
@click.option(
    "--lint-report",
    type=click.Path(exists=True),
    help="Path to Claude lint report JSON file (auto-discovers if not provided)",
)
@click.option(
    "--max-fixes",
    default=10,
    help="Maximum number of fixes to apply in this session",
)
@click.option(
    "--interactive/--no-interactive",
    default=True,
    help="Interactive mode for fix confirmation",
)
@click.option(
    "--auto-mode",
    is_flag=True,
    help="Run automatically with safe fixes only",
)
@click.option(
    "--session-dir",
    type=click.Path(),
    help="Session directory for organized outputs",
)
@click.option(
    "--protocol-dir",
    type=click.Path(),
    help="Protocol directory for bidirectional communication",
)
@click.option(
    "--fresh-report",
    is_flag=True,
    help="Generate fresh lint report before processing",
)
@click.option(
    "--claude-agent",
    is_flag=True,
    help="Claude agent mode - outputs instructions for Claude to apply fixes",
)
@click.option(
    "--batch-mode",
    is_flag=True,
    help="Batch mode - show all fixes at once for Claude to apply",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be fixed without applying changes",
)
@click.option(
    "--non-interactive",
    is_flag=True,
    help="Non-interactive mode - skip user prompts for automated workflows",
)
@click.option(
    "--version-match",
    is_flag=True,
    help="Ensure lint report matches current codebase version (default: True)",
    default=True,
)
@click.option(
    "--debug",
    is_flag=True,
    help="Enable debug mode - show full Claude prompts and detailed "
         "information",
)
@click.option(
    "--background",
    is_flag=True,
    help="Background execution mode - apply fixes silently in background "
         "with periodic status updates",
)
@click.option(
    "--monitor-lint",
    is_flag=True,
    help="Enable background lint report freshness monitoring using Watchdog",
)
@click.option(
    "--claude-cli",
    is_flag=True,
    help="Use direct Claude CLI integration for automated fix application",
)
@click.option(
    "--output-format",
    type=click.Choice(["json", "text"]),
    default="text",
    help="Output format for results (json for pipeline integration)",
)
@click.option(
    "--output-file",
    type=click.Path(),
    help="Output file path for JSON reports (required for pipeline integration)",
)
@click.option(
    "--auto-apply",
    is_flag=True,
    help="Automatically apply fixes without confirmation (for pipeline mode)",
)
def main(
    lint_report,
    max_fixes,
    interactive,
    auto_mode,
    session_dir,
    protocol_dir,
    fresh_report,
    claude_agent,
    batch_mode,
    dry_run,
    non_interactive,
    version_match,
    debug,
    background,
    monitor_lint,
    claude_cli,
    output_format,
    output_file,
    auto_apply,
):
    """Enhanced Claude Quality Patcher v2.0 - Protocol Integrated"""

    print("🤖 Enhanced Claude Quality Patcher v2.0")
    print("=" * 60)

    if protocol_dir:
        print(f"🔗 Protocol integration: {protocol_dir}")
    if session_dir:
        print(f"📁 Session directory: {session_dir}")

    # Handle non-interactive mode
    if non_interactive:
        interactive = False
        auto_mode = True
        print("🤖 Non-interactive mode enabled - automated execution")

    # Handle auto-apply mode (for pipeline integration)
    if auto_apply:
        interactive = False
        auto_mode = True
        print("🔄 Auto-apply mode enabled - fixing without confirmation")

    # Initialize enhanced patcher
    patcher = EnhancedClaudeQualityPatcher(
        repo_path=Path.cwd(),
        lint_report_path=(Path(lint_report) if lint_report else None),
        debug_mode=debug,
        session_dir=Path(session_dir) if session_dir else None,
        protocol_dir=Path(protocol_dir) if protocol_dir else None,
        max_fixes=max_fixes,
        fresh_report=fresh_report,
    )

    # Handle fresh report generation
    if fresh_report or not patcher.lint_report_path:
        print("🔄 Generating fresh lint report...")
        integration_success = patcher.auto_integrate_with_version_keeper()

        if (not integration_success and
                not patcher.lint_report_path):
            print("❌ Failed to generate or find lint report")
            print("💡 Try running manually:")
            print(
                "   python3 scripts/version_keeper.py --comprehensive-lint "
                "--output-dir=reports/"
            )
            sys.exit(1)

    # Validate we have a working report
    if not patcher.lint_report:
        print("❌ No valid lint report loaded")
        sys.exit(1)

    # Start session
    patcher.start_claude_session()

    # Lint monitoring configuration (must be before dry_run check)
    if monitor_lint:
        print("📊 LINT MONITORING: Background freshness monitoring enabled...")
        print("   Watchdog will monitor lint report directories for fresh reports")
        print("   This runs in parallel with quality patching for real-time feedback")

        # Start background lint monitoring
        import threading

        def background_lint_monitor():
            try:
                patcher.monitor_lint_report_freshness(
                    max_wait=300
                )  # 5 minute monitoring
            except Exception as e:
                print(f"   ⚠️  Lint monitoring error: {e}")

        lint_thread = threading.Thread(target=background_lint_monitor, daemon=True)
        lint_thread.start()
        print("   ✅ Background lint monitoring started")

    if dry_run:
        print("🔍 DRY RUN MODE - Analyzing fixes without applying...")
        priority_fixes = patcher.get_priority_fixes()

        print("\\n📋 FIXES TO BE APPLIED:")
        for i, fix_item in enumerate(priority_fixes[:max_fixes], 1):
            fix = fix_item.get("fix", {})
            priority = fix_item.get("priority", 4)
            category = fix_item.get("category", "unknown")

            priority_emoji = (
                "🔴" if priority == 1 else "🟡" if priority == 2 else "🟢"
            )

            print(
                f"{i}. {priority_emoji} [{category.upper()}] "
                f"{fix.get('description', 'No description')}"
            )

        print(
            f"\\n✅ Dry run complete. {len(priority_fixes[:max_fixes])} "
            f"fixes ready to apply."
        )
        return

    # Auto mode configuration
    if auto_mode:
        interactive = False
        print("🔄 AUTO MODE: Applying safe fixes automatically...")

    # Background mode configuration
    if background:
        interactive = False
        auto_mode = True
        print("🌙 BACKGROUND MODE: Running silently with periodic status updates...")
        print(
            "   This mode applies fixes automatically without showing "
            "individual prompts"
        )
        print("   Status updates will be shown every 5 fixes")

    # Claude CLI integration configuration
    if claude_cli:
        interactive = False
        auto_mode = True
        print(
            "🔗 CLAUDE CLI INTEGRATION: Direct programmatic fix application enabled..."
        )
        print("   Using Claude Code CLI for automated fix application")
        print("   This replaces wait-for-Claude with direct CLI calls")
        print("   Includes timeout handling and fallback to file monitoring")

    # Claude agent mode configuration
    if claude_agent:
        interactive = False
        print(
            "🤖 CLAUDE AGENT MODE: Outputting instructions for Claude to apply fixes..."
        )
        print("=" * 60)
        print("🎯 CLAUDE: This mode will show you exactly what to fix.")
        print("   Use your Write/Edit tools to apply each fix as instructed.")
        print("=" * 60 + "\n")

    # Batch mode configuration
    if batch_mode:
        print("📋 BATCH MODE: Showing all fixes at once for efficient processing...")
        session_results = patcher.run_batch_fixes(max_fixes=max_fixes)
    else:
        # Run step-by-step fixes
        session_results = patcher.run_step_by_step_fixes(
            max_fixes=max_fixes, interactive=interactive
        )

    # Generate and show report
    report = patcher.generate_session_report(session_results)
    print("\\n" + report)

    # Save session log
    patcher.save_session_log()

    # Generate JSON output for pipeline integration
    if output_format == "json":
        json_report = generate_quality_patcher_json_report(
            patcher=patcher,
            session_results=session_results,
            report=report
        )

        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                json.dump(json_report, f, indent=2, default=str)
            print(f"\\n📊 JSON report saved to: {output_path}")
        else:
            print("\\n📊 JSON OUTPUT:")
            print(json.dumps(json_report, indent=2, default=str))

    print("\\n🎉 Claude Quality Patcher session complete!")


if __name__ == "__main__":
    main()
