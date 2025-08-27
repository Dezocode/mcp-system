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
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import click
import semantic_version

# Import protocol if available
try:
    from claude_agent_protocol import TaskStatus, TaskType, get_protocol

    PROTOCOL_AVAILABLE = True
except ImportError:
    PROTOCOL_AVAILABLE = False


class MCPVersionKeeper:
    def __init__(self, repo_path: Path = None, session_dir: Path = None, config_path: Path = None):
        self.repo_path = repo_path or Path.cwd()
        self.version_file = self.repo_path / "pyproject.toml"
        self.changelog_file = self.repo_path / "CHANGELOG.md"
        self.package_dir = self.repo_path / "src"
        self.docs_dir = self.repo_path / "docs"
        
        # Load configuration
        self.config = self.load_config(config_path)

        self.current_version = self.get_current_version()
        self.protocol = None  # Enhanced with sync monitoring
        self.git_branch = self.get_current_branch()

        # Protocol integration
        self.protocol = None  # Enhanced with sync monitoring and real-time validation
        self.session_dir = session_dir
        if PROTOCOL_AVAILABLE and session_dir:
            claude_session = session_dir / ".claude-session"
            if claude_session.exists():
                self.protocol = get_protocol(claude_session)
                print(f"✅ Protocol integration enabled")
                
    def load_config(self, config_path: Path = None) -> Dict[str, Any]:
        """Load configuration from file with defaults"""
        default_config = {
            "timeout": {
                "subprocess": 120,
                "build": 300,
                "test": 600
            },
            "linting": {
                "tools": ["black", "isort", "mypy", "flake8", "pylint"],
                "max_issues": 1000,
                "exclude_patterns": ["*.backup.py", "*_old.py"]
            },
            "output": {
                "progress_bars": True,
                "verbose": False
            }
        }
        
        # Try to load from various locations
        config_locations = []
        if config_path:
            config_locations.append(config_path)
        config_locations.extend([
            self.repo_path / ".mcp-version-keeper.json",
            self.repo_path / "configs" / "version-keeper.json",
            Path.home() / ".mcp" / "version-keeper.json"
        ])
        
        for config_file in config_locations:
            if config_file.exists():
                try:
                    with open(config_file, 'r') as f:
                        user_config = json.load(f)
                    # Deep merge with defaults
                    self._deep_update(default_config, user_config)
                    print(f"📝 Loaded config from: {config_file}")
                    break
                except Exception as e:
                    print(f"⚠️ Failed to load config from {config_file}: {e}")
                    
        return default_config
    
    def _deep_update(self, base_dict: Dict, update_dict: Dict) -> None:
        """Deep update dictionary"""
        for key, value in update_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                self._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value

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
            f"📝 Updating version from {self.current_version} to {new_version}"
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
                    f"{output_dir}/bandit-report.json",
                    f"configs/bandit-report.json",
                    "-f",
                    "json",
                    "-o",
                    f"reports/bandit-report.json",
                ]
            )
            checks["safety"] = self.run_command(
                [
                    "safety",
                    f"{output_dir}/safety-report.json",
                    "check",
                    "--json",
                    "--output",
                    f"configs/safety-report.json",
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
                    f"--output={output_dir}/pip-audit-report.json",
                [
                    "pip-audit",
                    "--format=json",
                    f"--output=configs/pip-audit-report.json",
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
            "installers/install-mcp-system.py",
            "core/claude-code-mcp-bridge.py",
            "core/auto-discovery-system.py",
            "core/mcp-upgrader.py",
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
            removed_functions = set(base_functions) - set(current_functions)
            current_classes = re.findall(
                r"class\s+(\w+)",
                current_content,
            )
            if removed_functions:
                changes.extend([f"Removed function: {func}" for func in removed_functions])

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
            try:
                result = subprocess.run(
                    [
                        sys.executable,
                        "-m",
                        "venv",
                        str(venv_path),
                    ],
                    timeout=120,  # 2 minutes timeout
                    capture_output=True,
                    text=True,
                    check=True
                )
            except subprocess.TimeoutExpired:
                print(f"⚠️ Virtual environment creation timed out after 2 minutes")
                return {"passed": False, "error": "Timeout creating virtual environment"}
            except subprocess.CalledProcessError as e:
                print(f"⚠️ Failed to create virtual environment: {e.stderr}")
                return {"passed": False, "error": f"venv creation failed: {e.stderr}"}
            except Exception as e:
                print(f"⚠️ Unexpected error creating virtual environment: {e}")
                return {"passed": False, "error": f"Unexpected error: {e}"}

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
        self, exclude_backups: bool = False, exclude_duplicates: bool = False
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
            if self.should_skip_file(py_file, exclude_backups):
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

                # Skip files that contain template content (Jinja2, etc.) that would break AST parsing
                if any(template_marker in content for template_marker in ['{%', '{{', '%}', '}}']):
                    print(f"  ⏭️ Skipping template file {py_file.name} (contains Jinja2 syntax)")
                    continue

                # Parse AST to find functions and classes with proper context
                tree = ast.parse(content)

                def walk_with_class_context(node, class_name=None):
                    """Walk AST nodes while maintaining class context"""
                    if isinstance(node, ast.ClassDef):
                        # Process class-level methods
                        for child in node.body:
                            if isinstance(child, ast.FunctionDef):
                                func_signature = self.get_function_signature(
                                    child, node.name
                                )
                                if func_signature in functions_map:
                                    # Only flag as duplicate if it's truly the same function in different files
                                    # Skip if same file (could be legitimate overloads)
                                    if str(py_file) != str(functions_map[func_signature]["file"]):
                                        # Check if this is a legitimate duplicate vs legacy code
                                        func1_info = {
                                            "function": child.name,
                                            "file": str(functions_map[func_signature]["file"]),
                                            "line": functions_map[func_signature]["line"]
                                        }
                                        func2_info = {
                                            "function": child.name,
                                            "file": str(py_file),
                                            "line": child.lineno
                                        }
                                        
                                        # Only add to duplicates if it's legacy code, not legitimate different classes
                                        if not self.is_legitimate_duplicate_vs_legacy(func1_info, func2_info):
                                            duplicates["duplicate_functions"].append(
                                                {
                                                    "function": child.name,
                                                    "signature": func_signature,
                                                    "file1": str(functions_map[func_signature]["file"]),
                                                    "file2": str(py_file),
                                                    "line1": functions_map[func_signature]["line"],
                                                    "line2": child.lineno,
                                                }
                                            )
                                else:
                                    functions_map[func_signature] = {
                                        "file": py_file,
                                        "line": child.lineno,
                                        "name": child.name,
                                    }

                        # Process class itself for class duplicates
                        class_signature = self.get_class_signature(node)
                        if class_signature in classes_map:
                            duplicates["similar_classes"].append(
                                {
                                    "class": node.name,
                                    "signature": class_signature,
                                    "file1": str(classes_map[class_signature]["file"]),
                                    "file2": str(py_file),
                                    "line1": classes_map[class_signature]["line"],
                                    "line2": node.lineno,
                                }
                            )
                        else:
                            classes_map[class_signature] = {
                                "file": py_file,
                                "line": node.lineno,
                                "name": node.name,
                            }

                    elif isinstance(node, ast.FunctionDef) and class_name is None:
                        # Module-level function
                        func_signature = self.get_function_signature(node)
                        if func_signature in functions_map:
                            if str(py_file) != str(
                                functions_map[func_signature]["file"]
                            ):
                                # Apply the same filtering logic for module-level functions
                                func1_info = {
                                    "function": node.name,
                                    "file": str(functions_map[func_signature]["file"]),
                                    "line": functions_map[func_signature]["line"]
                                }
                                func2_info = {
                                    "function": node.name,
                                    "file": str(py_file),
                                    "line": node.lineno
                                }
                                
                                # Only add to duplicates if it's legacy code, not legitimate different implementations
                                if not self.is_legitimate_duplicate_vs_legacy(func1_info, func2_info):
                                    duplicates["duplicate_functions"].append(
                                        {
                                            "function": node.name,
                                            "signature": func_signature,
                                            "file1": str(
                                                functions_map[func_signature]["file"]
                                            ),
                                            "file2": str(py_file),
                                            "line1": functions_map[func_signature]["line"],
                                            "line2": node.lineno,
                                        }
                                    )
                        else:
                            functions_map[func_signature] = {
                                "file": py_file,
                                "line": node.lineno,
                                "name": node.name,
                            }

                    # Recursively process child nodes
                    for child in ast.iter_child_nodes(node):
                        walk_with_class_context(child, class_name)

                # Process the entire tree
                for node in tree.body:
                    walk_with_class_context(node)

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
    def should_skip_file(self, file_path: Path, exclude_backups: bool = False) -> bool:
        """Check if file should be skipped during duplicate detection"""
        
        # ALWAYS skip these patterns (including backup files by default)
        skip_patterns = [
            "__pycache__",
            ".git", 
            "venv",
            "env",
            ".pytest_cache",
            "node_modules",
            "dist",
            "build",
            # BACKUP/LEGACY PATTERNS - Always skip these
            "backups/",
            ".claude_patches/", 
            ".backup",
            "_backup",
            "-backup",
            ".bak",
            "-enhanced",  # Skip old enhanced files
            "_enhanced",
            ".orig",
            ".old", 
            "v1.0-original/",
            "-v1", "-v2", "_v1", "_v2",  # Versioned files
            "_original", "_updated",
            "legacy/", "-legacy", "_legacy",
        ]
        
        for pattern in skip_patterns:
            if pattern in str(file_path):
                return True
        
        return False

    def is_likely_false_positive(self, func_name: str, file_path: Path) -> bool:
        """Detect likely false positives vs REAL connection issues"""

        # REAL ISSUES: Don't filter these - they indicate actual problems
        real_connection_issues = [
            # Functions that should exist but don't
            "MCPRouter",  # Class that should be defined
            "get_protocol",  # Function that should exist
            "analyze_prompt",  # Method that should be implemented
            "start_required_servers",  # Method that should exist
        ]

        # If this is a function that SHOULD exist, it's a REAL issue
        if func_name in real_connection_issues:
            return False  # Don't filter - this is a genuine problem

        # FALSE POSITIVES: These are usually scope/import issues, not real problems
        false_positive_patterns = [
            # Standard library method calls that are usually correct
            ("parser", ["add_argument", "parse_args"]),  # argparse correctly used
            ("args", ["analyze", "route", "interactive"]),  # argparse args attributes
            ("self", ["protocol", "method"]),  # Class method calls
            ("super", ["__init__"]),  # Super calls
        ]

        # Check for obvious false positives
        for obj_name, methods in false_positive_patterns:
            if func_name in methods:
                return True  # More aggressive filtering of known methods

        # Standard library method calls - usually not real issues
        stdlib_methods = [
            "add_argument",
            "parse_args",  # argparse
            "lower",
            "upper",
            "strip",
            "split",
            "join",  # string methods
            "append",
            "extend",
            "add_argument", "parse_args",  # argparse
            "remove",
            "lower", "upper", "strip", "split", "join",  # string methods
            "pop",  # list methods
            "append", "extend", "remove", "pop",  # list methods
            "get",
            "get", "keys", "values", "items", "update",  # dict methods
            "keys",
            "read", "write", "close", "exists", "mkdir",  # file/path methods
            "values",
            "items",
            "update",  # dict methods
            "read",
            "write",
            "close",
            "exists",
            "mkdir",  # file/path methods
        ]
        if func_name in stdlib_methods:
            return True

        # DUPLICATE CODE ISSUES: Check if this might be calling an old/renamed function
        if self.is_duplicate_reference_issue(func_name, file_path):
            return False  # Don't filter - this is a real duplicate code issue

        return False  # Default to reporting as real issue

    def is_duplicate_reference_issue(self, func_name: str, file_path: Path) -> bool:
        """Check if undefined function might be calling old/duplicate code"""

        # Common patterns of duplicate code calling old functions
        duplicate_patterns = [
            # Old/new function naming patterns
            ("_v1", "_v2"),  # versioned functions
            ("_old", "_new"),  # old/new variants
            ("_enhanced", ""),  # enhanced vs original
            ("_original", "_updated"),  # original vs updated
        ]

        # Check if there are similar function names with these patterns
        try:
            # Quick scan for similar function names in the same file
            content = file_path.read_text()
            for old_suffix, new_suffix in duplicate_patterns:
                # Check if there's a pattern like func_name_old vs func_name_new
                old_variant = func_name + old_suffix
                new_variant = func_name + new_suffix
                if old_variant in content or new_variant in content:
                    return True

            # Check for common duplicate code scenarios
            if any(pattern in str(file_path) for pattern in ["enhanced", "v2", "backup", "original"]):
                # In enhanced/versioned files, undefined functions might be calling old code
                return True

        except Exception:
            pass

        return False

    def get_function_signature(self, node: ast.FunctionDef, class_name: str = None) -> str:
        """Generate unique signature for function node"""
        args = [arg.arg for arg in node.args.args]
        signature = f"{node.name}({', '.join(args)})"
        if class_name:
            signature = f"{class_name}.{signature}"
        return signature

    def is_legitimate_duplicate_vs_legacy(self, func1_info: dict, func2_info: dict) -> bool:
        """
        Determine if detected duplicate is legitimate (different valid implementations)
        vs legacy code that should be removed.
        
        Returns True if this is a legitimate duplicate (keep both)
        Returns False if this is legacy code (one should be removed)
        """
        file1 = Path(func1_info["file"])
        file2 = Path(func2_info["file"])
        func_name = func1_info["function"]
        
        # ALWAYS LEGITIMATE: Common method names that appear across different classes/modules
        if func_name in ["__init__", "__str__", "__repr__", "__enter__", "__exit__", 
                        "run", "execute", "process", "main", "start", "stop", 
                        "setup", "cleanup", "init", "handle", "validate"]:
            # These are legitimate different implementations
            return True
            
        # ALWAYS LEGITIMATE: Different top-level directories (different modules)
        if len(file1.parts) > 1 and len(file2.parts) > 1:
            # Check if in completely different top-level modules
            if file1.parts[0] != file2.parts[0]:
                return True
                
        # LEGACY PATTERNS: Clear indicators of old/backup code
        legacy_indicators = [
            "_backup", "_old", "_legacy", "_v1", "_v2", "_copy", 
            "_original", "_working", "_1", "_2", "backup/", "old/"
        ]
        
        file1_str = str(file1).lower()
        file2_str = str(file2).lower()
        
        for indicator in legacy_indicators:
            if indicator in file1_str or indicator in file2_str:
                # One file is clearly a backup/old version
                return False
                
        # SPECIFIC PATTERNS: Check for version keeper duplicates
        if func_name == "detect_duplicate_implementations":
            # Multiple version keeper files - check which is the main one
            if "version_keeper_1.py" in file1_str or "version_keeper_1.py" in file2_str:
                return False  # version_keeper_1.py is legacy
                
        # Same directory with similar function names = likely legacy
        if file1.parent == file2.parent:
            # Check if one file is clearly newer/enhanced version
            enhanced_indicators = ["enhanced", "improved", "new", "updated"]
            for indicator in enhanced_indicators:
                if indicator in file1_str and indicator not in file2_str:
                    return False  # file2 is legacy
                if indicator in file2_str and indicator not in file1_str:
                    return False  # file1 is legacy
            
            # Same directory, same function name, no clear enhancement pattern
            # This is likely a real duplicate that needs attention
            return False
            
        # Different directories, different purposes = legitimate
        return True

    def get_function_signature(
        self, node: ast.FunctionDef, class_name: str = None
    ) -> str:
        """Generate function signature for comparison with class context"""
        args = []
        for arg in node.args.args:
            args.append(arg.arg)

        # Include class context to avoid false positives for methods like __init__
        if class_name:
            return f"{class_name}.{node.name}({','.join(args)})"
        else:
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
        """Detect competing implementations (similar functionality in different files)"""
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

        # Import tqdm for progress indicators
        try:
            from tqdm import tqdm
            use_progress = True
        except ImportError:
            use_progress = False
            
        for pattern_info in competing_patterns:
            pattern = pattern_info["pattern"]
            found_files = []

            # Get all Python files first for progress tracking
            python_files = list(self.repo_path.rglob("*.py"))
            
            if use_progress and len(python_files) > 100:
                file_iterator = tqdm(python_files, desc=f"Scanning for {pattern}", leave=False)
            else:
                file_iterator = python_files
                
            for py_file in file_iterator:
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
                        "recommendation": f"Consolidate {len(found_files)} implementations into single module",
                    }
                )

        return competing

    def run_claude_integrated_linting(
        self, output_dir: Path = None, session_id: str = None, quick_check: bool = False
    ) -> Dict[str, Any]:
        """Enhanced comprehensive linting with protocol integration"""
        self.lint_start_time = time.time()

        print(
            f"🔍 Running {'quick' if quick_check else 'comprehensive'} Claude-integrated linting..."
        )

        # Update protocol if available
        if self.protocol:
            self.protocol.update_phase("linting", {
                "lint_type": "quick" if quick_check else "comprehensive",
                "started_at": datetime.now().isoformat()
            })

        lint_report = {
            "version": self.current_version,
            "performance": {},
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
        
        lint_report["fix_commands"] = self.generate_fix_commands(lint_report)
        lint_report["validation_report"] = self.validate_lint_recommendations(lint_report)

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
        
        # Calculate total issues
        total_issues = sum([
            len(tool_data.get("fixes", [])) 
            for tool_data in lint_report["quality_issues"].values()
        ]) + sum([
            len(tool_data.get("fixes", [])) 
            for tool_data in lint_report["security_issues"].values()
        ])

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
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        if output_dir:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")  # ISO-8601 compatible
            report_file = output_dir / f"claude-lint-report-{timestamp}.json"
            
            if self.protocol:
                self.protocol.update_phase("linting_complete", {
                    "issues_remaining": total_issues,
                    "lint_report": str(report_file),
                })
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
                        critical_fixes.append({
                            "tool": tool,
                            "command": fix.get("command", ""),
                            "description": fix.get("description", ""),
                            "severity": "error"
                        })

            # Create tasks for the most critical fixes
            for fix in critical_fixes[:5]:
                self.protocol.create_task(
                    task_type="fix_quality_issue",
                    description=fix["description"],
                    priority="high",
                    success_criteria={"fix_applied": True}
                )
            
            print(f"📋 Created {len(critical_fixes[:5])} priority fixing tasks in protocol")

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
                        "claude_prompt": "Please run 'black scripts/ core/ guardrails/' to auto-format the code according to PEP 8 standards.",
                    }
                )

        elif tool == "isort":
            if "ERROR" in stderr or "Skipped" in stdout:
                fixes.append(
                    {
                        "type": "auto_fix",
                        "command": "isort scripts/ core/ guardrails/",
                        "description": "Sort imports with isort",
                        "claude_prompt": "Please run 'isort scripts/ core/ guardrails/' to organize import statements.",
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
                            "claude_prompt": f"Please fix the type error in {file_path}:{line_num}: {error_msg}",
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
                            "claude_prompt": f"Please fix the linting issue in {file_path}:{line_num}:{col_num}: {code} {msg}",
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
                                "claude_prompt": f"Please review and fix the security issue in {result.get('filename')}:{result.get('line_number')}: {result.get('issue_text')}",
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
                                "claude_prompt": f"Please update {vuln.get('package_name')} from {vuln.get('installed_version')} to fix vulnerability {vuln.get('vulnerability_id')}",
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
            recommendations.append(
                f"🔒 Address {security_count} security issues found"
            )

        # Duplicate issues
        duplicates = lint_report["duplicate_issues"]
        if duplicates["duplicate_functions"]:
            recommendations.append(
                f"🔄 Remove {len(duplicates['duplicate_functions'])} duplicate functions"
            )
        if duplicates["competing_implementations"]:
            recommendations.append(
                f"⚡ Consolidate {len(duplicates['competing_implementations'])} competing implementations"
            )

        # Connection issues
        connections = lint_report.get("connection_issues", {})
        if connections.get("undefined_functions"):
            recommendations.append(
                f"🔗 Fix {len(connections['undefined_functions'])} undefined function calls"
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
        quality_issues = lint_report.get("quality_issues", {})
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
                        "description": f"Remove duplicate function {dup['function']} in {dup['file2']}",
                        "claude_prompt": f"Please remove the duplicate function '{dup['function']}' from {dup['file2']}:{dup['line2']} as it already exists in {dup['file1']}:{dup['line1']}",
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
                        "description": f"Fix undefined function call {func['function']} in {func['file']}:{func['line']}",
                        "claude_prompt": f"Please fix the undefined function call '{func['function']}' in {func['file']}:{func['line']} by either importing it, defining it, or correcting the function name",
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
                        "description": f"Fix broken import {imp['module']} in {imp['file']}:{imp['line']}",
                        "claude_prompt": f"Please fix the broken import '{imp['module']}' in {imp['file']}:{imp['line']} by either installing the module, correcting the import path, or removing the unused import",
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
        self, exclude_backups: bool = False, real_issues_only: bool = False
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
            f
            for f in self.repo_path.rglob("*.py")
            if not self.should_skip_file(f, exclude_backups)
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
                                # Smart filtering for real issues only
                                if real_issues_only and self.is_likely_false_positive(
                                    func_name, py_file
                                ):
                                    continue

                                connections_report["undefined_functions"].append(
                                    {
                                        "file": str(py_file),
                                        "line": node.lineno,
                                        "function": func_name,
                                        "type": "undefined_function_call",
                                    }
                                )

                        elif isinstance(node.func, ast.Attribute):
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
                                py_file
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
                f"Fix {len(connections_report['undefined_functions'])} undefined function calls"
            )
        if connections_report["broken_imports"]:
            connections_report["recommendations"].append(
                f"Fix {len(connections_report['broken_imports'])} broken imports"
            )
        if connections_report["connection_errors"]:
            connections_report["recommendations"].append(
                f"Investigate {len(connections_report['connection_errors'])} connection analysis errors"
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
        # This is a simplified check - in a real implementation you'd need more sophisticated analysis
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
                                "reason": f"Removing {function_name} from {file_path} would break dependencies",
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
                    # Security fixes are high priority but need careful review
                    validation_report["risky_recommendations"].append(
                        {
                            "fix": fix,
                            "reason": "Security fixes require careful review to avoid breaking functionality",
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
    ) -> Path:
        """Save release report to file"""
        if output_path is None:
            output_path = self.repo_path / f"release-report-{report['version']}.json"

        with open(output_path, "w") as f:
            json.dump(report, f, indent=2)

        print(f"📊 Release report saved: {output_path}")


def generate_json_report(keeper, session_id=None, claude_lint_report=None, duplicates=None, connections=None):
    """Generate structured JSON report for pipeline integration"""
    
    # Calculate total issues across all categories
    total_issues = 0
    
    # Count Claude lint issues
    if claude_lint_report:
        total_issues += claude_lint_report.get("total_issues", 0)
    
    # Count duplicate issues
    if duplicates:
        total_issues += len(duplicates.get("duplicate_functions", []))
        total_issues += len(duplicates.get("competing_implementations", [])) * 2  # Weight competing implementations higher
    
    # Count connection issues
    if connections:
        total_issues += len(connections.get("undefined_functions", []))
        total_issues += len(connections.get("broken_imports", []))
    
    # Generate structured report
    json_report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "session_id": session_id or f"version-keeper-{int(time.time())}",
        "version": keeper.current_version,
        "branch": keeper.git_branch,
        "summary": {
            "total_issues": total_issues,
            "fixes_applied": 0,  # This will be updated by quality patcher
            "remaining_issues": total_issues,  # Initially all issues remain
            "success_rate": 0.0 if total_issues > 0 else 100.0
        },
        "details": {
            "quality_issues": claude_lint_report.get("quality_issues", {}) if claude_lint_report else {},
            "security_issues": claude_lint_report.get("security_issues", {}) if claude_lint_report else {},
            "duplicate_issues": duplicates if duplicates else {},
            "connection_issues": connections if connections else {}
        },
        "performance": {
            "duration_seconds": claude_lint_report.get("performance", {}).get("duration_seconds", 0) if claude_lint_report else 0,
            "files_analyzed": claude_lint_report.get("files_analyzed", 0) if claude_lint_report else 0,
            "issues_per_second": claude_lint_report.get("performance", {}).get("issues_per_second", 0) if claude_lint_report else 0
        },
        "recommendations": []
    }
    
    # Add recommendations from each component
    if claude_lint_report and claude_lint_report.get("claude_recommendations"):
        json_report["recommendations"].extend(claude_lint_report["claude_recommendations"])
    
    if duplicates and duplicates.get("recommendations"):
        json_report["recommendations"].extend(duplicates["recommendations"])
    
    if connections and connections.get("recommendations"):
        json_report["recommendations"].extend(connections["recommendations"])
    
    # Add priority fixes from Claude lint if available
    if claude_lint_report and claude_lint_report.get("priority_fixes"):
        json_report["priority_fixes"] = claude_lint_report["priority_fixes"][:10]  # Top 10 priority fixes
    
    return json_report


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
@click.option(
    "--exclude-backups",
    is_flag=True,
    help="Exclude backup directories from analysis",
)
@click.option(
    "--exclude-duplicates",
    is_flag=True,
    help="Skip duplicate detection for backup files",
)
@click.option(
    "--real-issues-only",
    is_flag=True,
    help="Filter out false positives and focus on genuine issues",
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
    "--debug",
    is_flag=True,
    help="Enable debug mode - show detailed information and verbose output",
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
    exclude_backups,
    exclude_duplicates,
    real_issues_only,
    output_format,
    output_file,
    debug,
):
    """
    MCP System Version Keeper - Enhanced with Protocol Integration
    
    Manages versions, packaging, linting, and compatibility validation for MCP systems.
    
    Examples:
        # Run comprehensive linting with debug output
        python scripts/version_keeper.py --comprehensive-lint --debug
        
        # Generate JSON report for pipeline integration
        python scripts/version_keeper.py --claude-lint --output-format=json --output-file=report.json
        
        # Quick lint check excluding false positives
        python scripts/version_keeper.py --quick-check --real-issues-only
        
        # Version bump with validation
        python scripts/version_keeper.py --bump-type=patch --skip-tests
    """
    
    # Configure logging based on debug mode
    import logging
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logger = logging.getLogger(__name__)
    
    if debug:
        logger.debug("Debug mode enabled - verbose output will be shown")
        logger.debug(f"CLI Arguments: bump_type={bump_type}, output_format={output_format}")

    try:
        print("🚀 MCP System Version Keeper v2.0")
        print("=" * 50)

        # Initialize with protocol support
        session_path = Path(session_dir) if session_dir else None
        keeper = MCPVersionKeeper(session_dir=session_path)

        print(f"📍 Current version: {keeper.current_version}")
        print(f"🌿 Current branch: {keeper.git_branch}")
        
        if debug:
            logger.debug(f"Repository path: {keeper.repo_path}")
            logger.debug(f"Session directory: {session_path}")

    except Exception as e:
        logger.error(f"Failed to initialize Version Keeper: {e}")
        if debug:
            logger.exception("Full traceback:")
        sys.exit(1)

    # Input validation
    try:
        if output_file:
            output_file_path = Path(output_file)
            if not output_file_path.parent.exists():
                logger.error(f"Output directory does not exist: {output_file_path.parent}")
                sys.exit(1)
                
        if session_dir:
            session_dir_path = Path(session_dir)
            if not session_dir_path.exists():
                logger.warning(f"Session directory does not exist, creating: {session_dir_path}")
                session_dir_path.mkdir(parents=True, exist_ok=True)
                
        if output_format == "json" and not output_file:
            logger.warning("JSON output format specified but no output file provided")
            
        # Validate bump type
        if bump_type not in ["major", "minor", "patch"]:
            logger.error(f"Invalid bump type: {bump_type}")
            sys.exit(1)
            
        if debug:
            logger.debug("Input validation completed successfully")
            
    except Exception as e:
        logger.error(f"Input validation failed: {e}")
        if debug:
            logger.exception("Full traceback:")
        sys.exit(1)

    # Handle comprehensive lint mode - UPGRADED for freshness
    if comprehensive_lint:
        claude_lint = True
        detect_duplicates = False  # Skip false positives, focus on real issues
        check_connections = True  # Priority: undefined functions
        lint_only = True

    # Smart filtering for real issues
    if real_issues_only:
        print(
            "🎯 INTELLIGENT FILTERING: Focusing on real issues, excluding false positives"
        )
        exclude_backups = True
        exclude_duplicates = True

    # Handle lint-only mode
    if lint_only or claude_lint or detect_duplicates or check_connections:
        if detect_duplicates and not exclude_duplicates:
            print("\n🔍 Running duplicate/competing implementation detection...")
            duplicates = keeper.detect_duplicate_implementations(
                exclude_backups, exclude_duplicates
            )
        elif detect_duplicates and exclude_duplicates:
            print(
                "\n⏭️ Skipping duplicate detection (excluded by real-issues-only filter)"
            )
            duplicates = {
                "duplicate_functions": [],
                "competing_implementations": [],
                "similar_classes": [],
                "redundant_files": [],
                "recommendations": [],
            }

        if detect_duplicates:
            print("\n📊 DUPLICATE DETECTION RESULTS")
            print("=" * 50)
            print(f"🔄 Duplicate functions: {len(duplicates['duplicate_functions'])}")
            print(f"⚡ Competing implementations: {len(duplicates['competing_implementations'])}")
            
        print("🎯 INTELLIGENT FILTERING: Focusing on real issues, excluding false positives")
        
        if real_issues_only:
            print("\n⏭️ Skipping duplicate detection (excluded by real-issues-only filter)")
            duplicates = {"duplicate_functions": [], "competing_implementations": [], "similar_classes": [], "redundant_files": [], "recommendations": []}

        else:
            # Run duplicate detection normally
            duplicates = keeper.detect_duplicate_implementations(exclude_backups, exclude_duplicates)

            if duplicates["recommendations"]:
                print("\n💡 RECOMMENDATIONS:")
                for rec in duplicates["recommendations"]:
                    print(f"  • {rec}")

        if check_connections:
            print("\n🔗 Running connections linter...")
            connections = keeper.run_connections_linter(
                exclude_backups, real_issues_only
            )

            print("\n📊 CONNECTION ANALYSIS RESULTS")
            print("=" * 50)
            print(f"🔗 Undefined functions: {len(connections['undefined_functions'])}")
            print(f"📦 Broken imports: {len(connections['broken_imports'])}")
            print(f"⚠️  Connection errors: {len(connections['connection_errors'])}")

            if connections["undefined_functions"]:
                print("\n🔗 UNDEFINED FUNCTIONS:")
                for func in connections["undefined_functions"][:10]:  # Show first 10
                    print(
                        f"  • {func['function']} in {func['file']}:{func['line']} ({func['type']})"
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

        # Run connections check
        if check_connections:
            print("\n🔍 Running connection analysis...")
            connections = keeper.run_connections_linter(exclude_backups, real_issues_only)
            
            if connections["recommendations"]:
                print("\n💡 CONNECTION RECOMMENDATIONS:")
                for rec in connections["recommendations"]:
                    print(f"  • {rec}")

        # Run Claude integrated linting
        if claude_lint:
            print(f"\n🤖 Running {'quick' if quick_check else 'comprehensive'} Claude-integrated linting...")
            lint_report = keeper.run_claude_integrated_linting(
                output_dir=Path(output_dir) if output_dir else None,
                session_id=session_id,
                quick_check=quick_check,
            )
            
            # Process undefined functions
            for func in connections["undefined_functions"][:10]:  # Show first 10
                print(f"  • {func['function']} in {func['file']}:{func['line']}")

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
                    
            # Process broken imports
            for imp in connections["broken_imports"][:10]:  # Show first 10
                print(f"  • {imp['module']} in {imp['file']}:{imp['line']}")

            # Show additional imports if applicable
            if len(connections['broken_imports']) > 10:
                print(f"  ... and {len(connections['broken_imports']) - 10} more")
                
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
                report_file = (
                    Path(output_dir)
                    / f"claude-lint-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
                )
            else:
                # Save in reports directory for pipeline coordination
                reports_dir = keeper.repo_path / "reports"
                reports_dir.mkdir(
                    parents=True,
                    exist_ok=True,
                )
                report_file = (
                    reports_dir
                    / f"claude-lint-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
                )

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
            # Generate JSON output for pipeline integration
            if output_format == "json":
                json_report = generate_json_report(
                    keeper=keeper,
                    session_id=session_id,
                    claude_lint_report=lint_report if claude_lint else None,
                    duplicates=duplicates if detect_duplicates and not exclude_duplicates else None,
                    connections=connections if check_connections else None
                )
                
                if output_file:
                    output_path = Path(output_file)
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(output_path, 'w') as f:
                        json.dump(json_report, f, indent=2, default=str)
                    print(f"\n📊 JSON report saved to: {output_path}")
                else:
                    print("\n📊 JSON OUTPUT:")
                    print(json.dumps(json_report, indent=2, default=str))
                    
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
            f"  2. Commit changes: git add -A && git commit -m 'Bump version to {new_version}'"
        )
        print(
            f"  3. Create release: git tag v{new_version} && git push origin v{new_version}"
        )

    elif report["overall_status"] == "FAIL":
        print("\n❌ Validation failed - version update aborted")
        print("Please fix issues and run again")
        sys.exit(1)

    elif dry_run:
        print("\n🔍 Dry run complete - no changes applied")


if __name__ == "__main__":
    main()
