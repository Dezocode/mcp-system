#!/usr/bin/env python3
"""
MCP System Version Keeper - Enhanced with Protocol Integration
Manages versions, packaging, linting, and compatibility validation
"""

import ast
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import click
import semantic_version

# Import protocol if available
try:
    from claude_agent_protocol import TaskType, get_protocol

    PROTOCOL_AVAILABLE = True
except ImportError:
    PROTOCOL_AVAILABLE = False


class MCPVersionKeeper:
    def __init__(self, repo_path: Path = None, session_dir: Path = None):
        self.repo_path = repo_path or Path.cwd()
        self.version_file = self.repo_path / "pyproject.toml"
        self.changelog_file = self.repo_path / "CHANGELOG.md"
        self.package_dir = self.repo_path / "src"
        self.docs_dir = self.repo_path / "docs"

        self.current_version = self.get_current_version()
        self.git_branch = self.get_current_branch()
        # Protocol integration
        self.protocol = None
        self.session_dir = session_dir
        if PROTOCOL_AVAILABLE and session_dir:
            claude_session = session_dir / ".claude-session"
            if claude_session.exists():
                self.protocol = get_protocol(claude_session)
                print("✅ Protocol integration enabled")
        # Performance tracking
        self.lint_start_time = None
        self.issues_found = 0
        self.files_scanned = 0

    def get_current_version(self) -> str:
        """Get current version from pyproject.toml"""
        try:
            with open(self.version_file, "r") as f:
                content = f.read()
                match = re.search(
                    r'version\s*=\s*"([^"]+)"',
                    content,
                )
                if match:
                    return match.group(1)
        except FileNotFoundError:
            pass
        return "0.0.0"

    def get_current_branch(self) -> str:
        """Get current git branch"""
        try:
            result = subprocess.run(
                [
                    "git",
                    "branch",
                    "--show-current",
                ],
                capture_output=True,
                text=True,
                cwd=self.repo_path,
            )
            return result.stdout.strip()
        except subprocess.SubprocessError:
            return "unknown"

    def bump_version(self, bump_type: str = "patch") -> str:
        """Bump version based on type (major, minor, patch)"""
        current = semantic_version.Version(self.current_version)

        if bump_type == "major":
            new_version = current.next_major()
        elif bump_type == "minor":
            new_version = current.next_minor()
        elif bump_type == "patch":
            new_version = current.next_patch()
        else:
            raise ValueError(f"Invalid bump type: {bump_type}")

        return str(new_version)

    def update_version_files(self, new_version: str):
        """Update version in all relevant files"""
        print(f"📝 Updating version from {self.current_version} to {new_version}")

        # Update pyproject.toml
        with open(self.version_file, "r") as f:
            content = f.read()

        content = re.sub(
            r'version\s*=\s*"[^"]+"',
            f'version = "{new_version}"',
            content,
        )

        with open(self.version_file, "w") as f:
            f.write(content)

        # Update other version references
        version_files = [
            self.repo_path / "src" / "install-mcp-system.py",
            self.repo_path / "README.md",
            self.docs_dir / "INSTALLATION.md",
        ]

        for file_path in version_files:
            if file_path.exists():
                self.update_version_in_file(file_path, new_version)

    def update_version_in_file(
        self,
        file_path: Path,
        new_version: str,
    ):
        """Update version strings in a specific file"""
        try:
            with open(file_path, "r") as f:
                content = f.read()

            # Common version patterns
            patterns = [
                (
                    r'version\s*=\s*"[^"]+"',
                    f'version = "{new_version}"',
                ),
                (
                    r'__version__\s*=\s*"[^"]+"',
                    f'__version__ = "{new_version}"',
                ),
                (
                    r"v\d+\.\d+\.\d+",
                    f"v{new_version}",
                ),
                (
                    r"Version \d+\.\d+\.\d+",
                    f"Version {new_version}",
                ),
                (
                    r"MCP System v\d+\.\d+\.\d+",
                    f"MCP System v{new_version}",
                ),
            ]

            updated = False
            for (
                pattern,
                replacement,
            ) in patterns:
                if re.search(pattern, content):
                    content = re.sub(
                        pattern,
                        replacement,
                        content,
                    )
                    updated = True

            if updated:
                with open(file_path, "w") as f:
                    f.write(content)
                print(f"  ✅ Updated {file_path.name}")

        except Exception as e:
            print(f"  ⚠️  Failed to update {file_path}: {e}")

    def run_quality_checks(self, output_dir: str = None) -> Dict[str, bool]:
        """Run comprehensive quality checks"""
        print("🔍 Running quality checks...")

        checks = {}

        # Code formatting
        print("  📝 Checking code formatting...")
        checks["black"] = self.run_command(
            [
                "black",
                "--check",
                "core/",
                "scripts/",
                "guardrails/",
                "tests/",
                "utils/",
            ]
        )
        checks["isort"] = self.run_command(
            [
                "isort",
                "--check-only",
                "core/",
                "scripts/",
                "guardrails/",
                "tests/",
                "utils/",
            ]
        )

        # Type checking
        print("  🔍 Type checking...")
        checks["mypy"] = self.run_command(["mypy", "scripts/", "core/"])

        # Linting
        print("  🧹 Linting...")
        checks["pylint"] = self.run_command(
            [
                "pylint",
                "scripts/",
                "core/",
                "--exit-zero",
            ]
        )
        checks["flake8"] = self.run_command(
            [
                "flake8",
                "scripts/",
                "core/",
                "guardrails/",
            ]
        )

        # Security scanning
        print("  🔒 Security scanning...")
        if output_dir:
            checks["bandit"] = self.run_command(
                [
                    "bandit",
                    "-r",
                    "scripts/",
                    "core/",
                    "guardrails/",
                    "-f",
                    "json",
                    "-o",
                    f"{output_dir}/bandit-report.json",
                ]
            )
            checks["safety"] = self.run_command(
                [
                    "safety",
                    "check",
                    "--json",
                    "--output",
                    f"{output_dir}/safety-report.json",
                ]
            )
        else:
            checks["bandit"] = self.run_command(
                [
                    "bandit",
                    "-r",
                    "scripts/",
                    "core/",
                    "guardrails/",
                    "-f",
                    "json",
                    "-o",
                    "bandit-report.json",
                ]
            )
            checks["safety"] = self.run_command(
                [
                    "safety",
                    "check",
                    "--json",
                    "--output",
                    "safety-report.json",
                ]
            )

        # Dependency validation
        print("  📦 Dependency validation...")
        if output_dir:
            checks["pip_audit"] = self.run_command(
                [
                    "pip-audit",
                    "--format=json",
                    f"--output={output_dir}/pip-audit-report.json",
                ]
            )
        else:
            checks["pip_audit"] = self.run_command(
                [
                    "pip-audit",
                    "--format=json",
                    "--output=pip-audit-report.json",
                ]
            )

        return checks

    def run_tests(self) -> Dict[str, bool]:
        """Run comprehensive test suite"""
        print("🧪 Running test suite...")

        test_results = {}

        # Unit tests
        print("  🔬 Unit tests...")
        test_results["unit"] = self.run_command(
            [
                "pytest",
                "tests/",
                "--cov=src",
                "--cov-report=xml",
                "--cov-report=html",
                "--junit-xml=test-results.xml",
            ]
        )

        # Integration tests
        print("  🔗 Integration tests...")
        test_results["integration"] = self.run_command(
            [
                "python",
                "scripts/test_installation.py",
            ]
        )

        # Template validation
        print("  📋 Template validation...")
        test_results["templates"] = self.run_command(
            [
                "python",
                "scripts/validate_templates.py",
                "--all",
            ]
        )

        # Upgrade module validation
        print("  ⚡ Upgrade module validation...")
        test_results["upgrades"] = self.run_command(
            [
                "python",
                "scripts/validate_upgrade_modules.py",
                "--all",
            ]
        )

        # Documentation tests
        print("  📚 Documentation tests...")
        test_results["docs"] = self.run_command(
            [
                "python",
                "scripts/test_documentation_examples.py",
            ]
        )

        return test_results

    def validate_compatibility(self, base_branch: str = "main") -> Dict[str, Any]:
        """Validate compatibility with base branch"""
        print(f"🔄 Validating compatibility with {base_branch}...")

        compatibility = {
            "breaking_changes": [],
            "api_changes": [],
            "template_changes": [],
            "upgrade_module_changes": [],
            "compatible": True,
        }

        try:
            # Get diff with base branch
            result = subprocess.run(
                [
                    "git",
                    "diff",
                    f"origin/{base_branch}...HEAD",
                    "--name-only",
                ],
                capture_output=True,
                text=True,
                cwd=self.repo_path,
            )

            changed_files = result.stdout.strip().split("\n")

            # Analyze changes
            for file_path in changed_files:
                if not file_path:
                    continue

                file_path = Path(file_path)

                # Check for potential breaking changes
                if self.is_critical_file(file_path):
                    compatibility["breaking_changes"].append(str(file_path))

                # Check API changes
                if file_path.suffix == ".py" and any(
                    dir in str(file_path)
                    for dir in [
                        "scripts/",
                        "core/",
                        "guardrails/",
                    ]
                ):
                    api_changes = self.detect_api_changes(
                        file_path,
                        base_branch,
                    )
                    if api_changes:
                        compatibility["api_changes"].extend(api_changes)

                # Check template changes
                if "templates/" in str(file_path):
                    compatibility["template_changes"].append(str(file_path))

                # Check upgrade module changes
                if "upgrade" in str(file_path).lower():
                    compatibility["upgrade_module_changes"].append(str(file_path))

            # Determine overall compatibility
            compatibility["compatible"] = (
                len(compatibility["breaking_changes"]) == 0
                and len(compatibility["api_changes"]) == 0
            )

        except subprocess.SubprocessError as e:
            print(f"  ❌ Failed to validate compatibility: {e}")
            compatibility["compatible"] = False

        return compatibility

    def is_critical_file(self, file_path: Path) -> bool:
        """Check if file is critical for compatibility"""
        critical_patterns = [
            "install-mcp-system.py",
            "claude-code-mcp-bridge.py",
            "auto-discovery-system.py",
            "mcp-upgrader.py",
            "pyproject.toml",
            "requirements.txt",
        ]

        return any(pattern in str(file_path) for pattern in critical_patterns)

    def detect_api_changes(
        self,
        file_path: Path,
        base_branch: str,
    ) -> List[str]:
        """Detect API changes in a Python file"""
        try:
            # Get file content from base branch
            result = subprocess.run(
                [
                    "git",
                    "show",
                    f"origin/{base_branch}:{file_path}",
                ],
                capture_output=True,
                text=True,
                cwd=self.repo_path,
            )

            if result.returncode != 0:
                return []  # File might be new

            base_content = result.stdout
            current_content = (self.repo_path / file_path).read_text()

            # Simple API change detection
            changes = []

            # Check for removed functions/classes
            base_functions = re.findall(r"def\s+(\w+)", base_content)
            current_functions = re.findall(
                r"def\s+(\w+)",
                current_content,
            )

            removed_functions = set(base_functions) - set(current_functions)
            if removed_functions:
                changes.extend(
                    [f"Removed function: {func}" for func in removed_functions]
                )

            base_classes = re.findall(
                r"class\s+(\w+)",
                base_content,
            )
            current_classes = re.findall(
                r"class\s+(\w+)",
                current_content,
            )

            removed_classes = set(base_classes) - set(current_classes)
            if removed_classes:
                changes.extend([f"Removed class: {cls}" for cls in removed_classes])

            return changes

        except Exception:
            return []

    def build_package(self) -> bool:
        """Build distribution package"""
        print("📦 Building package...")

        # Clean previous builds
        build_dirs = [
            self.repo_path / "build",
            self.repo_path / "dist",
            self.repo_path / "src" / "*.egg-info",
        ]

        for build_dir in build_dirs:
            if build_dir.exists():
                shutil.rmtree(
                    build_dir,
                    ignore_errors=True,
                )

        # Build package
        success = self.run_command(["python", "-m", "build"])

        if success:
            print("  ✅ Package built successfully")

            # Validate package
            dist_files = list((self.repo_path / "dist").glob("*"))
            print(f"  📦 Built {len(dist_files)} distribution files:")
            for dist_file in dist_files:
                print(f"    - {dist_file.name}")

            # Test package installation
            return self.test_package_installation()

        return False

    def test_package_installation(
        self,
    ) -> bool:
        """Test package installation in isolated environment"""
        print("  🧪 Testing package installation...")

        with tempfile.TemporaryDirectory() as temp_dir:
            venv_path = Path(temp_dir) / "test_venv"

            # Create virtual environment
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "venv",
                    str(venv_path),
                ]
            )

            # Install package
            pip_path = venv_path / "bin" / "pip"
            if not pip_path.exists():
                pip_path = venv_path / "Scripts" / "pip.exe"

            dist_files = list((self.repo_path / "dist").glob("*.whl"))
            if dist_files:
                result = subprocess.run(
                    [
                        str(pip_path),
                        "install",
                        str(dist_files[0]),
                    ],
                    capture_output=True,
                    text=True,
                )

                if result.returncode == 0:
                    print("    ✅ Package installation successful")
                    return True
                else:
                    print(f"    ❌ Package installation failed: {result.stderr}")

        return False

    def update_changelog(
        self,
        new_version: str,
        changes: List[str],
    ):
        """Update changelog with new version"""
        print(f"📝 Updating changelog for v{new_version}...")

        if not self.changelog_file.exists():
            self.create_initial_changelog()

        with open(self.changelog_file, "r") as f:
            content = f.read()

        # Create new entry
        date_str = datetime.now().strftime("%Y-%m-%d")
        new_entry = f"""
## [{new_version}] - {date_str}

### Changed
"""

        for change in changes:
            new_entry += f"- {change}\n"

        # Insert after the first header
        lines = content.split("\n")
        insert_index = 0
        for i, line in enumerate(lines):
            if line.startswith("## [") and "Unreleased" not in line:
                insert_index = i
                break

        lines.insert(insert_index, new_entry)

        with open(self.changelog_file, "w") as f:
            f.write("\n".join(lines))

        print("  ✅ Changelog updated")

    def create_initial_changelog(self):
        """Create initial changelog if it doesn't exist"""
        initial_content = """# Changelog

All notable changes to MCP System will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

"""
        self.changelog_file.write_text(initial_content)

    def run_command(self, cmd: List[str]) -> bool:
        """Run command and return success status"""
        try:
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
            )
            return result.returncode == 0
        except Exception:
            return False

    def run_command_with_output(self, cmd: List[str]) -> Tuple[bool, str, str]:
        """Run command and return success status, stdout, stderr"""
        try:
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
            )
            return (
                result.returncode == 0,
                result.stdout,
                result.stderr,
            )
        except Exception as e:
            return False, "", str(e)

    def detect_duplicate_implementations(
        self,
    ) -> Dict[str, Any]:
        """Detect duplicate/competing implementations across all MCP-System modules"""
        print("🔍 Scanning for duplicate/competing implementations...")

        duplicates = {
            "duplicate_functions": [],
            "competing_implementations": [],
            "similar_classes": [],
            "redundant_files": [],
            "recommendations": [],
        }

        # Scan all Python files
        python_files = list(self.repo_path.rglob("*.py"))
        functions_map = {}
        classes_map = {}
        file_hashes = {}

        for py_file in python_files:
            if self.should_skip_file(py_file):
                continue

            try:
                content = py_file.read_text()
                file_hash = hashlib.md5(content.encode()).hexdigest()

                # Check for duplicate file content
                if file_hash in file_hashes:
                    duplicates["redundant_files"].append(
                        {
                            "file1": str(file_hashes[file_hash]),
                            "file2": str(py_file),
                            "hash": file_hash,
                        }
                    )
                else:
                    file_hashes[file_hash] = py_file

                # Parse AST to find functions and classes
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        func_signature = self.get_function_signature(node)
                        if func_signature in functions_map:
                            duplicates["duplicate_functions"].append(
                                {
                                    "function": node.name,
                                    "signature": func_signature,
                                    "file1": str(functions_map[func_signature]),
                                    "file2": str(py_file),
                                    "line1": functions_map[func_signature].get(
                                        "line",
                                        "unknown",
                                    ),
                                    "line2": node.lineno,
                                }
                            )
                        else:
                            functions_map[func_signature] = {
                                "file": py_file,
                                "line": node.lineno,
                                "name": node.name,
                            }

                    elif isinstance(node, ast.ClassDef):
                        class_signature = self.get_class_signature(node)
                        if class_signature in classes_map:
                            duplicates["similar_classes"].append(
                                {
                                    "class": node.name,
                                    "signature": class_signature,
                                    "file1": str(classes_map[class_signature]),
                                    "file2": str(py_file),
                                    "line1": classes_map[class_signature].get(
                                        "line",
                                        "unknown",
                                    ),
                                    "line2": node.lineno,
                                }
                            )
                        else:
                            classes_map[class_signature] = {
                                "file": py_file,
                                "line": node.lineno,
                                "name": node.name,
                            }

            except Exception as e:
                print(f"  ⚠️ Error parsing {py_file}: {e}")

        # Detect competing implementations
        duplicates["competing_implementations"] = (
            self.detect_competing_implementations()
        )

        # Generate recommendations
        if duplicates["duplicate_functions"]:
            duplicates["recommendations"].append(
                "Remove duplicate function implementations"
            )
        if duplicates["competing_implementations"]:
            duplicates["recommendations"].append(
                "Consolidate competing implementations into single modules"
            )
        if duplicates["similar_classes"]:
            duplicates["recommendations"].append(
                "Consider merging similar class implementations"
            )
        if duplicates["redundant_files"]:
            duplicates["recommendations"].append("Remove redundant file copies")

        return duplicates

    def should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped during duplicate detection"""
        skip_patterns = [
            "__pycache__",
            ".git",
            "venv",
            "env",
            ".pytest_cache",
            "node_modules",
            "dist",
            "build",
        ]

        for pattern in skip_patterns:
            if pattern in str(file_path):
                return True
        return False

    def get_function_signature(self, node: ast.FunctionDef) -> str:
        """Generate function signature for comparison"""
        args = []
        for arg in node.args.args:
            args.append(arg.arg)

        return f"{node.name}({','.join(args)})"

    def get_class_signature(self, node: ast.ClassDef) -> str:
        """Generate class signature for comparison"""
        methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                methods.append(item.name)

        return f"{node.name}::{','.join(sorted(methods))}"

    def detect_competing_implementations(
        self,
    ) -> List[Dict[str, Any]]:
        """Detect competing implementations (similar functionality in
        different files)"""
        competing = []

        # Define known competing patterns
        competing_patterns = [
            {
                "pattern": "server.*management",
                "files": [
                    "mcp-universal",
                    "mcp-router",
                    "auto-discovery",
                ],
                "description": "Multiple server management implementations",
            },
            {
                "pattern": "template.*creation",
                "files": [
                    "mcp-create-server",
                    "template",
                ],
                "description": "Multiple template creation systems",
            },
            {
                "pattern": "validation.*system",
                "files": [
                    "validate_templates",
                    "validate_upgrade_modules",
                    "version_keeper",
                ],
                "description": "Multiple validation frameworks",
            },
            {
                "pattern": "upgrade.*module",
                "files": [
                    "mcp-upgrader",
                    "claude-upgrade",
                ],
                "description": "Multiple upgrade systems",
            },
        ]

        for pattern_info in competing_patterns:
            pattern = pattern_info["pattern"]
            found_files = []

            for py_file in self.repo_path.rglob("*.py"):
                if re.search(
                    pattern,
                    py_file.name,
                    re.IGNORECASE,
                ):
                    found_files.append(str(py_file))

            if len(found_files) > 1:
                competing.append(
                    {
                        "pattern": pattern,
                        "description": pattern_info["description"],
                        "files": found_files,
                        "recommendation": (
                            f"Consolidate {len(found_files)} "
                            f"implementations into single module"
                        ),
                    }
                )

        return competing

    def run_claude_integrated_linting(
        self, output_dir: Path = None, session_id: str = None, quick_check: bool = False
    ) -> Dict[str, Any]:
        """Enhanced comprehensive linting with protocol integration"""
        self.lint_start_time = time.time()
        print(
            f"🔍 Running {'quick' if quick_check else 'comprehensive'} "
            f"Claude-integrated linting..."
        )

        # Update protocol if available
        if self.protocol:
            self.protocol.update_phase(
                "linting",
                {
                    "lint_type": "quick" if quick_check else "comprehensive",
                    "started_at": datetime.now().isoformat(),
                },
            )

        lint_report = {
            "version": self.current_version,
            "branch": self.git_branch,
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id,
            "total_issues": 0,
            "critical_issues": 0,
            "error_issues": 0,
            "warning_issues": 0,
            "info_issues": 0,
            "files_analyzed": 0,
            "linters_used": [],
            "issues": [],
            "quality_issues": {},
            "security_issues": {},
            "compatibility_issues": {},
            "duplicate_issues": {},
            "claude_recommendations": [],
            "fix_commands": [],
            "priority_fixes": [],
            "performance": {},
        }

        # Run quality checks with detailed output
        quality_tools = [
            "black",
            "isort",
            "mypy",
            "flake8",
            "pylint",
        ]
        for tool in quality_tools:
            success, stdout, stderr = self.run_quality_check_with_details(tool)
            lint_report["quality_issues"][tool] = {
                "passed": success,
                "stdout": stdout,
                "stderr": stderr,
                "fixes": self.generate_tool_fixes(tool, stdout, stderr),
            }

        # Run security checks with detailed output
        security_tools = ["bandit", "safety"]
        for tool in security_tools:
            success, stdout, stderr = self.run_security_check_with_details(tool)
            lint_report["security_issues"][tool] = {
                "passed": success,
                "stdout": stdout,
                "stderr": stderr,
                "fixes": self.generate_security_fixes(tool, stdout, stderr),
            }

        # Run duplicate detection
        lint_report["duplicate_issues"] = self.detect_duplicate_implementations()

        # Run connections linting
        lint_report["connection_issues"] = self.run_connections_linter()

        # Generate Claude-specific recommendations
        lint_report["claude_recommendations"] = self.generate_claude_recommendations(
            lint_report
        )

        # Generate automated fix commands
        lint_report["fix_commands"] = self.generate_fix_commands(lint_report)

        # Prioritize fixes
        lint_report["priority_fixes"] = self.prioritize_fixes(lint_report)

        # Validate recommendations for safety
        lint_report["validation_report"] = self.validate_lint_recommendations(
            lint_report
        )

        # Calculate totals and performance metrics
        total_issues = sum(
            [
                len(tool_data.get("fixes", []))
                for tool_data in lint_report["quality_issues"].values()
            ]
        ) + sum(
            [
                len(tool_data.get("fixes", []))
                for tool_data in lint_report["security_issues"].values()
            ]
        )
        lint_report["total_issues"] = total_issues
        lint_report["files_analyzed"] = self.files_scanned
        # Performance metrics
        if self.lint_start_time:
            lint_duration = time.time() - self.lint_start_time
            lint_report["performance"] = {
                "duration_seconds": lint_duration,
                "issues_per_second": (
                    total_issues / lint_duration if lint_duration > 0 else 0
                ),
                "files_per_second": (
                    self.files_scanned / lint_duration if lint_duration > 0 else 0
                ),
            }

        # Save detailed report
        if output_dir:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            report_file = output_dir / f"claude-lint-report-{timestamp}.json"
            with open(report_file, "w") as f:
                json.dump(lint_report, f, indent=2)
            print(f"📊 Lint report saved to: {report_file}")
            lint_report["report_file"] = str(report_file)

        # Protocol integration - update state and create tasks
        if self.protocol:
            self.protocol.update_phase(
                "linting_complete",
                {
                    "issues_remaining": total_issues,
                    "lint_report": lint_report.get("report_file", ""),
                    "performance": lint_report["performance"],
                },
            )

            # Create fixing tasks for critical issues
            critical_fixes = []
            for tool, data in lint_report["quality_issues"].items():
                for fix in data.get("fixes", []):
                    if fix.get("type") == "auto_fix":
                        critical_fixes.append(
                            {
                                "tool": tool,
                                "command": fix["command"],
                                "description": fix["description"],
                                "severity": "error",
                            }
                        )

            # Create tasks for the most critical fixes
            for fix in critical_fixes[:5]:
                self.protocol.create_task(
                    TaskType.LINT_FIX,
                    context=fix,
                    priority=1,
                    success_criteria={"fix_applied": True},
                )

            print(
                f"📋 Created {len(critical_fixes[:5])} priority fixing "
                f"tasks in protocol"
            )

        return lint_report

    def run_quality_check_with_details(self, tool: str) -> Tuple[bool, str, str]:
        """Run quality check tool with detailed output"""
        commands = {
            "black": [
                "black",
                "--check",
                "--diff",
                "scripts/",
                "core/",
                "guardrails/",
            ],
            "isort": [
                "isort",
                "--check-only",
                "--diff",
                "scripts/",
                "core/",
                "guardrails/",
            ],
            "mypy": [
                "mypy",
                "scripts/",
                "core/",
                "--show-error-codes",
            ],
            "flake8": [
                "flake8",
                "scripts/",
                "core/",
                "guardrails/",
                "--format=%(path)s:%(row)d:%(col)d: %(code)s %(text)s",
            ],
            "pylint": [
                "pylint",
                "scripts/",
                "core/",
                "--output-format=text",
            ],
        }

        if tool in commands:
            return self.run_command_with_output(commands[tool])
        return (
            False,
            "",
            f"Unknown tool: {tool}",
        )

    def run_security_check_with_details(self, tool: str) -> Tuple[bool, str, str]:
        """Run security check tool with detailed output"""
        commands = {
            "bandit": [
                "bandit",
                "-r",
                "scripts/",
                "core/",
                "guardrails/",
                "-f",
                "json",
            ],
            "safety": [
                "safety",
                "check",
                "--json",
            ],
        }

        if tool in commands:
            return self.run_command_with_output(commands[tool])
        return (
            False,
            "",
            f"Unknown security tool: {tool}",
        )

    def generate_tool_fixes(
        self,
        tool: str,
        stdout: str,
        stderr: str,
    ) -> List[Dict[str, str]]:
        """Generate specific fix recommendations for each tool"""
        fixes = []

        if tool == "black":
            if "would reformat" in stdout:
                fixes.append(
                    {
                        "type": "auto_fix",
                        "command": "black scripts/ core/ guardrails/",
                        "description": "Auto-format code with Black",
                        "claude_prompt": "Please run 'black scripts/ core/ "
                        "guardrails/' to auto-format the code "
                        "according to PEP 8 standards.",
                    }
                )

        elif tool == "isort":
            if "ERROR" in stderr or "Skipped" in stdout:
                fixes.append(
                    {
                        "type": "auto_fix",
                        "command": "isort scripts/ core/ guardrails/",
                        "description": "Sort imports with isort",
                        "claude_prompt": "Please run 'isort scripts/ core/ "
                        "guardrails/' to organize import statements.",
                    }
                )

        elif tool == "mypy":
            if "error:" in stdout:
                # Parse mypy errors for specific fixes
                errors = re.findall(
                    r"(.+?):(\d+):.*?error: (.+)",
                    stdout,
                )
                for (
                    file_path,
                    line_num,
                    error_msg,
                ) in errors[
                    :5
                ]:  # Limit to 5 errors
                    fixes.append(
                        {
                            "type": "manual_fix",
                            "file": file_path,
                            "line": line_num,
                            "error": error_msg,
                            "claude_prompt": (
                                f"Please fix the type error in "
                                f"{file_path}:{line_num}: {error_msg}"
                            ),
                        }
                    )

        elif tool == "flake8":
            if stdout:
                # Parse flake8 errors
                errors = re.findall(
                    r"(.+?):(\d+):(\d+): (.+?) (.+)",
                    stdout,
                )
                for (
                    file_path,
                    line_num,
                    col_num,
                    code,
                    msg,
                ) in errors[:5]:
                    fixes.append(
                        {
                            "type": "manual_fix",
                            "file": file_path,
                            "line": line_num,
                            "column": col_num,
                            "code": code,
                            "message": msg,
                            "claude_prompt": (
                                f"Please fix the linting issue in "
                                f"{file_path}:{line_num}:{col_num}: "
                                f"{code} {msg}"
                            ),
                        }
                    )

        return fixes

    def generate_security_fixes(
        self,
        tool: str,
        stdout: str,
        stderr: str,
    ) -> List[Dict[str, str]]:
        """Generate security fix recommendations"""
        fixes = []

        if tool == "bandit":
            try:
                if stdout:
                    bandit_data = json.loads(stdout)
                    for result in bandit_data.get("results", [])[
                        :3
                    ]:  # Limit to 3 issues
                        fixes.append(
                            {
                                "type": "security_fix",
                                "file": result.get("filename"),
                                "line": result.get("line_number"),
                                "severity": result.get("issue_severity"),
                                "confidence": result.get("issue_confidence"),
                                "issue": result.get("issue_text"),
                                "claude_prompt": (
                                    f"Please review and fix the security issue in "
                                    f"{result.get('filename')}:"
                                    f"{result.get('line_number')}: "
                                    f"{result.get('issue_text')}"
                                ),
                            }
                        )
            except json.JSONDecodeError:
                pass

        elif tool == "safety":
            try:
                if stdout:
                    safety_data = json.loads(stdout)
                    for vuln in safety_data[:3]:  # Limit to 3 vulnerabilities
                        fixes.append(
                            {
                                "type": "dependency_fix",
                                "package": vuln.get("package_name"),
                                "version": vuln.get("installed_version"),
                                "vulnerability": vuln.get("vulnerability_id"),
                                "recommendation": vuln.get("more_info_url"),
                                "claude_prompt": (
                                    f"Please update {vuln.get('package_name')} "
                                    f"from {vuln.get('installed_version')} to fix "
                                    f"vulnerability {vuln.get('vulnerability_id')}"
                                ),
                            }
                        )
            except json.JSONDecodeError:
                pass

        return fixes

    def generate_claude_recommendations(self, lint_report: Dict[str, Any]) -> List[str]:
        """Generate Claude-specific recommendations based on lint results"""
        recommendations = []

        # Quality issues
        failed_quality = [
            tool
            for tool, result in lint_report["quality_issues"].items()
            if not result["passed"]
        ]
        if failed_quality:
            recommendations.append(
                f"🔧 Run quality fixes for: {', '.join(failed_quality)}"
            )

        # Security issues
        security_count = sum(
            len(result.get("fixes", []))
            for result in lint_report["security_issues"].values()
        )
        if security_count > 0:
            recommendations.append(f"🔒 Address {security_count} security issues found")

        # Duplicate issues
        duplicates = lint_report["duplicate_issues"]
        if duplicates["duplicate_functions"]:
            recommendations.append(
                f"🔄 Remove {len(duplicates['duplicate_functions'])} duplicate functions"
            )
        if duplicates["competing_implementations"]:
            recommendations.append(
                f"⚡ Consolidate {len(duplicates['competing_implementations'])} "
                f"competing implementations"
            )

        # Connection issues
        connections = lint_report.get("connection_issues", {})
        if connections.get("undefined_functions"):
            recommendations.append(
                f"🔗 Fix {len(connections['undefined_functions'])} "
                f"undefined function calls"
            )
        if connections.get("broken_imports"):
            recommendations.append(
                f"📦 Fix {len(connections['broken_imports'])} broken imports"
            )

        return recommendations

    def generate_fix_commands(self, lint_report: Dict[str, Any]) -> List[str]:
        """Generate automated fix commands"""
        commands = []

        # Auto-fixable quality issues
        if not lint_report["quality_issues"].get("black", {}).get("passed", True):
            commands.append("black scripts/ core/ guardrails/")
        if not lint_report["quality_issues"].get("isort", {}).get("passed", True):
            commands.append("isort scripts/ core/ guardrails/")

        return commands

    def prioritize_fixes(self, lint_report: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Prioritize fixes by importance"""
        priority_fixes = []

        # Priority 1: Security issues
        for tool, result in lint_report["security_issues"].items():
            for fix in result.get("fixes", []):
                priority_fixes.append(
                    {
                        "priority": 1,
                        "category": "security",
                        "fix": fix,
                    }
                )

        # Priority 2: Duplicate implementations
        duplicates = lint_report["duplicate_issues"]
        for dup in duplicates["duplicate_functions"]:
            priority_fixes.append(
                {
                    "priority": 2,
                    "category": "duplicates",
                    "fix": {
                        "type": "remove_duplicate",
                        "description": f"Remove duplicate function "
                        f"{dup['function']} in {dup['file2']}",
                        "claude_prompt": (
                            f"Please remove the duplicate function "
                            f"'{dup['function']}' from {dup['file2']}:{dup['line2']} "
                            f"as it already exists in "
                            f"{dup['file1']}:{dup['line1']}"
                        ),
                    },
                }
            )

        # Priority 3: Connection issues
        connections = lint_report.get("connection_issues", {})
        for func in connections.get("undefined_functions", []):
            priority_fixes.append(
                {
                    "priority": 3,
                    "category": "connections",
                    "fix": {
                        "type": "fix_undefined_function",
                        "description": (
                            f"Fix undefined function call {func['function']} "
                            f"in {func['file']}:{func['line']}"
                        ),
                        "claude_prompt": (
                            f"Please fix the undefined function call "
                            f"'{func['function']}' in {func['file']}:{func['line']} "
                            f"by either importing it, defining it, or correcting "
                            f"the function name"
                        ),
                    },
                }
            )

        for imp in connections.get("broken_imports", []):
            priority_fixes.append(
                {
                    "priority": 3,
                    "category": "connections",
                    "fix": {
                        "type": "fix_broken_import",
                        "description": (
                            f"Fix broken import {imp['module']} "
                            f"in {imp['file']}:{imp['line']}"
                        ),
                        "claude_prompt": (
                            f"Please fix the broken import '{imp['module']}' "
                            f"in {imp['file']}:{imp['line']} by either installing "
                            f"the module, correcting the import path, or removing "
                            f"the unused import"
                        ),
                    },
                }
            )

        # Priority 4: Quality issues
        for tool, result in lint_report["quality_issues"].items():
            for fix in result.get("fixes", []):
                priority_fixes.append(
                    {
                        "priority": 4,
                        "category": "quality",
                        "fix": fix,
                    }
                )

        return sorted(
            priority_fixes,
            key=lambda x: x["priority"],
        )

    def run_connections_linter(
        self,
    ) -> Dict[str, Any]:
        """Lint for broken function calls and connections across MCP-System"""
        print("🔗 Running connections linter for broken function calls...")

        connections_report = {
            "broken_imports": [],
            "undefined_functions": [],
            "missing_dependencies": [],
            "circular_imports": [],
            "unused_imports": [],
            "connection_errors": [],
            "recommendations": [],
        }

        # Build function registry from all Python files
        function_registry = {}
        import_registry = {}

        python_files = [
            f for f in self.repo_path.rglob("*.py") if not self.should_skip_file(f)
        ]

        # First pass: collect all functions and imports
        for py_file in python_files:
            try:
                content = py_file.read_text()
                tree = ast.parse(content)

                # Collect function definitions
                file_functions = []
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        file_functions.append(node.name)
                    elif isinstance(node, ast.ClassDef):
                        # Collect class methods
                        for item in node.body:
                            if isinstance(
                                item,
                                ast.FunctionDef,
                            ):
                                file_functions.append(f"{node.name}.{item.name}")

                function_registry[str(py_file)] = file_functions

                # Collect imports
                file_imports = []
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            file_imports.append(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            for alias in node.names:
                                file_imports.append(f"{node.module}.{alias.name}")

                import_registry[str(py_file)] = file_imports

            except Exception as e:
                connections_report["connection_errors"].append(
                    {
                        "file": str(py_file),
                        "error": f"Failed to parse: {e}",
                        "type": "parse_error",
                    }
                )

        # Second pass: check for broken connections
        for py_file in python_files:
            try:
                content = py_file.read_text()
                tree = ast.parse(content)

                # Check function calls
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call):
                        if isinstance(
                            node.func,
                            ast.Name,
                        ):
                            func_name = node.func.id
                            if not self.is_function_defined(
                                func_name,
                                py_file,
                                function_registry,
                                import_registry,
                            ):
                                connections_report["undefined_functions"].append(
                                    {
                                        "file": str(py_file),
                                        "line": node.lineno,
                                        "function": func_name,
                                        "type": "undefined_function_call",
                                    }
                                )

                        elif isinstance(
                            node.func,
                            ast.Attribute,
                        ):
                            # Handle method calls like obj.method()
                            attr_name = node.func.attr
                            if isinstance(
                                node.func.value,
                                ast.Name,
                            ):
                                obj_name = node.func.value.id
                                full_call = f"{obj_name}.{attr_name}"
                                if not self.is_method_defined(
                                    full_call,
                                    py_file,
                                    function_registry,
                                    import_registry,
                                ):
                                    connections_report["undefined_functions"].append(
                                        {
                                            "file": str(py_file),
                                            "line": node.lineno,
                                            "function": full_call,
                                            "type": "undefined_method_call",
                                        }
                                    )

                # Check imports
                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom):
                        if node.module:
                            module_path = self.resolve_module_path(
                                node.module,
                                py_file,
                            )
                            if module_path and not module_path.exists():
                                connections_report["broken_imports"].append(
                                    {
                                        "file": str(py_file),
                                        "line": node.lineno,
                                        "module": node.module,
                                        "type": "missing_module",
                                    }
                                )

            except Exception as e:
                connections_report["connection_errors"].append(
                    {
                        "file": str(py_file),
                        "error": f"Failed to analyze connections: {e}",
                        "type": "analysis_error",
                    }
                )

        # Generate recommendations
        if connections_report["undefined_functions"]:
            connections_report["recommendations"].append(
                f"Fix {len(connections_report['undefined_functions'])} "
                f"undefined function calls"
            )
        if connections_report["broken_imports"]:
            connections_report["recommendations"].append(
                f"Fix {len(connections_report['broken_imports'])} broken imports"
            )
        if connections_report["connection_errors"]:
            connections_report["recommendations"].append(
                f"Investigate {len(connections_report['connection_errors'])} "
                f"connection analysis errors"
            )

        return connections_report

    def is_function_defined(
        self,
        func_name: str,
        current_file: Path,
        function_registry: Dict,
        import_registry: Dict,
    ) -> bool:
        """Check if function is defined locally or imported"""
        current_file_str = str(current_file)

        # Check if defined in current file
        if current_file_str in function_registry:
            if func_name in function_registry[current_file_str]:
                return True

        # Check if it's a built-in function
        builtins = [
            "print",
            "len",
            "str",
            "int",
            "float",
            "list",
            "dict",
            "set",
            "tuple",
            "open",
            "range",
            "enumerate",
            "zip",
            "map",
            "filter",
            "sorted",
            "sum",
            "min",
            "max",
            "abs",
            "all",
            "any",
            "bool",
            "bytes",
            "callable",
            "chr",
            "compile",
            "dir",
            "eval",
            "exec",
            "format",
            "getattr",
            "hasattr",
            "hash",
            "hex",
            "id",
            "input",
            "isinstance",
            "issubclass",
            "iter",
            "next",
            "oct",
            "ord",
            "pow",
            "repr",
            "round",
            "setattr",
            "slice",
            "super",
            "type",
            "vars",
        ]

        if func_name in builtins:
            return True

        # Check if imported (simplified check)
        if current_file_str in import_registry:
            imports = import_registry[current_file_str]
            for imp in imports:
                if func_name in imp or imp.endswith(func_name):
                    return True

        return False

    def is_method_defined(
        self,
        method_call: str,
        current_file: Path,
        function_registry: Dict,
        import_registry: Dict,
    ) -> bool:
        """Check if method call is valid"""
        # This is a simplified check - in a real implementation you'd need more
        # sophisticated analysis
        # For now, assume imported modules have valid methods
        current_file_str = str(current_file)

        if current_file_str in import_registry:
            imports = import_registry[current_file_str]
            for imp in imports:
                # If the object is imported, assume its methods are valid
                if any(part in imp for part in method_call.split(".")):
                    return True

        # Check if it's a standard library method
        std_objects = [
            "json",
            "os",
            "sys",
            "subprocess",
            "pathlib",
            "datetime",
            "re",
            "ast",
        ]
        for obj in std_objects:
            if method_call.startswith(obj + "."):
                return True

        return False

    def resolve_module_path(
        self,
        module_name: str,
        current_file: Path,
    ) -> Optional[Path]:
        """Resolve relative module import to file path"""
        try:
            if module_name.startswith("."):
                # Relative import
                current_dir = current_file.parent
                parts = module_name.split(".")

                # Count leading dots for relative level
                level = 0
                for part in parts:
                    if part == "":
                        level += 1
                    else:
                        break

                # Go up directories based on level
                target_dir = current_dir
                for _ in range(level):
                    target_dir = target_dir.parent

                # Add remaining path parts
                remaining_parts = [p for p in parts if p]
                for part in remaining_parts:
                    target_dir = target_dir / part

                # Check for .py file or __init__.py in directory
                if target_dir.with_suffix(".py").exists():
                    return target_dir.with_suffix(".py")
                elif (target_dir / "__init__.py").exists():
                    return target_dir / "__init__.py"

            else:
                # Absolute import - check if it's a local module
                parts = module_name.split(".")
                base_path = self.repo_path / "src"

                for part in parts:
                    base_path = base_path / part

                if base_path.with_suffix(".py").exists():
                    return base_path.with_suffix(".py")
                elif (base_path / "__init__.py").exists():
                    return base_path / "__init__.py"

        except Exception:
            pass

        return None

    def validate_lint_recommendations(
        self, lint_report: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate that lint recommendations won't break code"""
        print("🛡️ Validating lint recommendations for safety...")

        validation_report = {
            "safe_recommendations": [],
            "risky_recommendations": [],
            "blocked_recommendations": [],
            "validation_errors": [],
        }

        # Check each priority fix for safety
        for pfix in lint_report.get("priority_fixes", []):
            fix = pfix.get("fix", {})
            fix_type = fix.get("type", "")

            try:
                if fix_type == "auto_fix":
                    # Auto-fixes like black/isort are generally safe
                    validation_report["safe_recommendations"].append(
                        {
                            "fix": fix,
                            "reason": "Auto-formatting tools are safe",
                        }
                    )

                elif fix_type == "remove_duplicate":
                    # Check if removing duplicate would break imports/calls
                    file_path = fix.get("description", "").split(" in ")[-1]
                    function_name = (
                        fix.get("description", "")
                        .split("function ")[-1]
                        .split(" in")[0]
                    )

                    if self.would_break_dependencies(
                        file_path,
                        function_name,
                    ):
                        validation_report["blocked_recommendations"].append(
                            {
                                "fix": fix,
                                "reason": (
                                    f"Removing {function_name} from {file_path} "
                                    f"would break dependencies"
                                ),
                            }
                        )
                    else:
                        validation_report["safe_recommendations"].append(
                            {
                                "fix": fix,
                                "reason": "Duplicate removal is safe",
                            }
                        )

                elif fix_type == "manual_fix":
                    # Manual fixes need human review
                    validation_report["risky_recommendations"].append(
                        {
                            "fix": fix,
                            "reason": "Manual fixes require human validation",
                        }
                    )

                elif fix_type == "security_fix":
                    # Security fixes are high priority but need careful
                    # review
                    validation_report["risky_recommendations"].append(
                        {
                            "fix": fix,
                            "reason": (
                                "Security fixes require careful review to avoid "
                                "breaking functionality"
                            ),
                        }
                    )

                else:
                    validation_report["risky_recommendations"].append(
                        {
                            "fix": fix,
                            "reason": f"Unknown fix type: {fix_type}",
                        }
                    )

            except Exception as e:
                validation_report["validation_errors"].append(
                    {
                        "fix": fix,
                        "error": str(e),
                    }
                )

        return validation_report

    def would_break_dependencies(
        self,
        file_path: str,
        function_name: str,
    ) -> bool:
        """Check if removing a function would break dependencies"""
        try:
            # Simple check: search for function calls across all files
            for py_file in self.repo_path.rglob("*.py"):
                if self.should_skip_file(py_file) or str(py_file) == file_path:
                    continue

                try:
                    content = py_file.read_text()
                    # Look for function calls, imports, or references
                    if (
                        f"{function_name}(" in content
                        or f"from {file_path} import" in content
                        or f"import {file_path}" in content
                    ):
                        return True
                except Exception:
                    continue

        except Exception:
            pass

        return False

    def generate_release_report(
        self,
        version: str,
        checks: Dict[str, bool],
        tests: Dict[str, bool],
        compatibility: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate comprehensive release report"""
        report = {
            "version": version,
            "timestamp": datetime.now().isoformat(),
            "branch": self.git_branch,
            "quality_checks": checks,
            "test_results": tests,
            "compatibility": compatibility,
            "overall_status": (
                "PASS"
                if self.all_checks_passed(
                    checks,
                    tests,
                    compatibility,
                )
                else "FAIL"
            ),
            "recommendations": [],
        }

        # Add recommendations
        if not all(checks.values()):
            report["recommendations"].append("Fix code quality issues before release")

        if not all(tests.values()):
            report["recommendations"].append("Fix failing tests before release")

        if not compatibility["compatible"]:
            report["recommendations"].append(
                "Review breaking changes and update documentation"
            )

        if len(compatibility["api_changes"]) > 0:
            report["recommendations"].append(
                "Consider bumping major version for API changes"
            )

        return report

    def all_checks_passed(
        self,
        checks: Dict[str, bool],
        tests: Dict[str, bool],
        compatibility: Dict[str, Any],
    ) -> bool:
        """Check if all validation passes"""
        return (
            all(checks.values()) and all(tests.values()) and compatibility["compatible"]
        )

    def save_report(
        self,
        report: Dict[str, Any],
        output_path: Path = None,
    ):
        """Save release report to file"""
        if output_path is None:
            output_path = self.repo_path / f"release-report-{report['version']}.json"

        with open(output_path, "w") as f:
            json.dump(report, f, indent=2)

        print(f"📊 Release report saved: {output_path}")


@click.command()
@click.option(
    "--bump-type",
    default="patch",
    type=click.Choice(["major", "minor", "patch"]),
    help="Version bump type",
)
@click.option(
    "--base-branch",
    default="main",
    help="Base branch for compatibility check",
)
@click.option(
    "--skip-tests",
    is_flag=True,
    help="Skip test execution",
)
@click.option(
    "--skip-build",
    is_flag=True,
    help="Skip package build",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Perform dry run without changes",
)
@click.option(
    "--output-dir",
    type=click.Path(),
    help="Output directory for reports",
)
@click.option(
    "--claude-lint",
    is_flag=True,
    help="Run Claude-integrated linting with fix recommendations",
)
@click.option(
    "--detect-duplicates",
    is_flag=True,
    help="Run duplicate/competing implementation detector",
)
@click.option(
    "--check-connections",
    is_flag=True,
    help="Run connections linter for broken function calls",
)
@click.option(
    "--lint-only",
    is_flag=True,
    help="Only run linting checks, skip version operations",
)
@click.option(
    "--comprehensive-lint",
    is_flag=True,
    help="Run all linting checks (claude-lint + duplicates + connections)",
)
@click.option(
    "--session-id",
    help="Session ID for tracking and protocol integration",
)
@click.option(
    "--session-dir",
    type=click.Path(),
    help="Session directory for protocol integration",
)
@click.option(
    "--quick-check",
    is_flag=True,
    help="Quick lint check (faster, fewer linters)",
)
def main(
    bump_type,
    base_branch,
    skip_tests,
    skip_build,
    dry_run,
    output_dir,
    claude_lint,
    detect_duplicates,
    check_connections,
    lint_only,
    comprehensive_lint,
    session_id,
    session_dir,
    quick_check,
):
    """MCP System Version Keeper - Enhanced with Protocol Integration"""

    print("🚀 MCP System Version Keeper v2.0")
    print("=" * 50)

    # Initialize with protocol support
    session_path = Path(session_dir) if session_dir else None
    keeper = MCPVersionKeeper(session_dir=session_path)

    print(f"📍 Current version: {keeper.current_version}")
    print(f"🌿 Current branch: {keeper.git_branch}")

    # Handle comprehensive lint mode
    if comprehensive_lint:
        claude_lint = True
        detect_duplicates = True
        check_connections = True
        lint_only = True

    # Handle lint-only mode
    if lint_only or claude_lint or detect_duplicates or check_connections:
        if detect_duplicates:
            print("\n🔍 Running duplicate/competing implementation detection...")
            duplicates = keeper.detect_duplicate_implementations()

            print("\n📊 DUPLICATE DETECTION RESULTS")
            print("=" * 50)
            print(f"🔄 Duplicate functions: {len(duplicates['duplicate_functions'])}")
            print(
                f"⚡ Competing implementations: "
                f"{len(duplicates['competing_implementations'])}"
            )
            print(f"🏗️ Similar classes: {len(duplicates['similar_classes'])}")
            print(f"📁 Redundant files: {len(duplicates['redundant_files'])}")

            if duplicates["duplicate_functions"]:
                print("\n🔄 DUPLICATE FUNCTIONS:")
                for dup in duplicates["duplicate_functions"]:
                    print(
                        f"  • {dup['function']} in {dup['file1']}:{dup['line1']} "
                        f"and {dup['file2']}:{dup['line2']}"
                    )

            if duplicates["competing_implementations"]:
                print("\n⚡ COMPETING IMPLEMENTATIONS:")
                for comp in duplicates["competing_implementations"]:
                    print(
                        f"  • {comp['description']}: "
                        f"{len(comp['files'])} implementations"
                    )
                    for file in comp["files"]:
                        print(f"    - {file}")

            if duplicates["recommendations"]:
                print("\n💡 RECOMMENDATIONS:")
                for rec in duplicates["recommendations"]:
                    print(f"  • {rec}")

        if check_connections:
            print("\n🔗 Running connections linter...")
            connections = keeper.run_connections_linter()

            print("\n📊 CONNECTION ANALYSIS RESULTS")
            print("=" * 50)
            print(f"🔗 Undefined functions: {len(connections['undefined_functions'])}")
            print(f"📦 Broken imports: {len(connections['broken_imports'])}")
            print(f"⚠️  Connection errors: {len(connections['connection_errors'])}")

            if connections["undefined_functions"]:
                print("\n🔗 UNDEFINED FUNCTIONS:")
                for func in connections["undefined_functions"][:10]:  # Show first 10
                    print(
                        f"  • {func['function']} in {func['file']}:{func['line']} "
                        f"({func['type']})"
                    )
                if len(connections["undefined_functions"]) > 10:
                    print(
                        f"  ... and {len(connections['undefined_functions']) - 10} more"
                    )

            if connections["broken_imports"]:
                print("\n📦 BROKEN IMPORTS:")
                for imp in connections["broken_imports"][:10]:  # Show first 10
                    print(f"  • {imp['module']} in {imp['file']}:{imp['line']}")
                if len(connections["broken_imports"]) > 10:
                    print(f"  ... and {len(connections['broken_imports']) - 10} more")

            if connections["recommendations"]:
                print("\n💡 CONNECTION RECOMMENDATIONS:")
                for rec in connections["recommendations"]:
                    print(f"  • {rec}")

        if claude_lint:
            print(
                f"\n🤖 Running {'quick' if quick_check else 'comprehensive'} "
                f"Claude-integrated linting..."
            )
            lint_report = keeper.run_claude_integrated_linting(
                output_dir=Path(output_dir) if output_dir else None,
                session_id=session_id,
                quick_check=quick_check,
            )

            print("\n📊 CLAUDE LINT REPORT")
            print("=" * 50)

            # Show priority fixes
            if lint_report["priority_fixes"]:
                print(
                    f"\n🚨 PRIORITY FIXES ({len(lint_report['priority_fixes'])} total):"
                )
                for i, pfix in enumerate(
                    lint_report["priority_fixes"][:10],
                    1,
                ):  # Show top 10
                    priority_icon = (
                        "🔴"
                        if pfix["priority"] == 1
                        else ("🟡" if pfix["priority"] == 2 else "🟢")
                    )
                    print(
                        f"  {i}. {priority_icon} [{pfix['category'].upper()}] "
                        f"{pfix['fix'].get('description', 'No description')}"
                    )

            # Show Claude recommendations
            if lint_report["claude_recommendations"]:
                print("\n🤖 CLAUDE RECOMMENDATIONS:")
                for rec in lint_report["claude_recommendations"]:
                    print(f"  • {rec}")

            # Show automated fix commands
            if lint_report["fix_commands"]:
                print("\n⚡ AUTO-FIX COMMANDS:")
                for cmd in lint_report["fix_commands"]:
                    print(f"  • {cmd}")

            # Save detailed report
            if output_dir:
                timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                report_file = Path(output_dir) / f"claude-lint-report-{timestamp}.json"
            else:
                # Save in reports/lint directory for pipeline coordination
                reports_dir = keeper.repo_path / "reports" / "lint"
                reports_dir.mkdir(
                    parents=True,
                    exist_ok=True,
                )
                timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                report_file = reports_dir / f"claude-lint-report-{timestamp}.json"

            with open(report_file, "w") as f:
                json.dump(
                    lint_report,
                    f,
                    indent=2,
                    default=str,
                )
            print(f"\n📊 Detailed Claude lint report saved: {report_file}")
            print("\n🚨 FRESH REPORT READY 🚨")
            print("Claude: New lint report generated and ready for quality patcher!")

        if lint_only:
            print("\n✅ Lint-only mode complete")
            return

    # Calculate new version
    new_version = keeper.bump_version(bump_type)
    print(f"🎯 Target version: {new_version}")

    if dry_run:
        print("🔍 DRY RUN MODE - No changes will be made")

    # Run quality checks (enhanced with Claude integration if requested)
    if claude_lint:
        lint_report = keeper.run_claude_integrated_linting(
            output_dir=Path(output_dir) if output_dir else None,
            session_id=session_id,
            quick_check=quick_check,
        )
        checks = {
            tool: result["passed"]
            for tool, result in lint_report["quality_issues"].items()
        }
    else:
        checks = keeper.run_quality_checks(output_dir)

    # Run tests (unless skipped)
    if not skip_tests:
        tests = keeper.run_tests()
    else:
        tests = {"skipped": True}

    # Validate compatibility
    compatibility = keeper.validate_compatibility(base_branch)

    # Generate report
    report = keeper.generate_release_report(
        new_version,
        checks,
        tests,
        compatibility,
    )

    # Save report
    if output_dir:
        output_path = Path(output_dir) / f"release-report-{new_version}.json"
    else:
        output_path = None

    keeper.save_report(report, output_path)

    # Show summary
    print("\n" + "=" * 50)
    print("📊 RELEASE VALIDATION SUMMARY")
    print("=" * 50)

    status_icon = "✅" if report["overall_status"] == "PASS" else "❌"
    print(f"{status_icon} Overall Status: {report['overall_status']}")

    print("\n🔍 Quality Checks:")
    for check, result in checks.items():
        icon = "✅" if result else "❌"
        print(f"  {icon} {check}")

    if not skip_tests:
        print("\n🧪 Tests:")
        for test, result in tests.items():
            icon = "✅" if result else "❌"
            print(f"  {icon} {test}")

    print("\n🔄 Compatibility:")
    icon = "✅" if compatibility["compatible"] else "❌"
    print(f"  {icon} Compatible with {base_branch}")

    if compatibility["breaking_changes"]:
        print(f"  ⚠️  Breaking changes: {len(compatibility['breaking_changes'])}")

    if compatibility["api_changes"]:
        print(f"  ⚠️  API changes: {len(compatibility['api_changes'])}")

    # Recommendations
    if report["recommendations"]:
        print("\n💡 Recommendations:")
        for rec in report["recommendations"]:
            print(f"  • {rec}")

    # Apply changes if validation passes and not dry run
    if report["overall_status"] == "PASS" and not dry_run:
        print(f"\n🚀 Applying version update to {new_version}...")

        # Update version files
        keeper.update_version_files(new_version)

        # Update changelog
        changes = [f"Version bump to {new_version}"]
        if compatibility["api_changes"]:
            changes.extend(compatibility["api_changes"])

        keeper.update_changelog(new_version, changes)

        # Build package (unless skipped)
        if not skip_build:
            keeper.build_package()

        print("✅ Version update complete!")
        print("\n📋 Next steps:")
        print("  1. Review changes: git diff")
        print(
            f"  2. Commit changes: git add -A && "
            f"git commit -m 'Bump version to {new_version}'"
        )
        print(
            f"  3. Create release: git tag v{new_version} && "
            f"git push origin v{new_version}"
        )

    elif report["overall_status"] == "FAIL":
        print("\n❌ Validation failed - version update aborted")
        print("Please fix issues and run again")
        sys.exit(1)

    elif dry_run:
        print("\n🔍 Dry run complete - no changes applied")


if __name__ == "__main__":
    main()
