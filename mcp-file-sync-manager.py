#!/usr/bin/env python3
"""
MCP File Sync Manager - Automated File Organization with Watchdog
Keeps files in their correct directories with real-time monitoring
"""

import json
import shutil
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class MCPFileSyncManager(FileSystemEventHandler):
    """Real-time file synchronization and directory organization manager"""

    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.config_file = self.project_root / ".mcp-sync-config.json"
        self.backup_dir = self.project_root / ".mcp-system-backups-disconnected"
        self.trash_dir = self.project_root / ".mcp-system-trash-internal"

        # Directory organization rules with hierarchical prioritization
        self.directory_rules = {
            # CORE DIRECTORY - Core MCP system files (HIGHEST PRIORITY)
            "core/": {
                "patterns": [
                    "mcp-*.py", "claude-*.py", "auto-discovery-system.py",
                    "direct-mem0-usage.py"
                ],
                "exclude_patterns": [
                    "mcp-file-sync-manager.py"  # This stays in root as utility
                ],
                "description": "Core MCP system files",
                "priority": 2
            },
            # Core system scripts (SECOND PRIORITY)
            "scripts/": {
                "patterns": [
                    "*_keeper.py", "*_agent*.py", "*_loop.py", "claude_*.py",
                    "*quality_patcher.py", "*version_keeper.py"
                ],
                "description": "Core system scripts and agents",
                "priority": 2
            },
            "installers/": {
                "patterns": ["install*.py", "setup*.py", "*installer*.py"],
                "description": "Installation and setup scripts",
                "priority": 3
            },
            # BIN - Only shell scripts and executables (NOT Python files)
            "bin/": {
                "patterns": ["run-*", "*.sh", "quick-*"],
                "exclude_patterns": ["*.py"],  # NO Python files in bin/
                "description": "Shell scripts and executable binaries only",
                "priority": 4
            },
            "configs/": {
                "patterns": [
                    ".gitignore", ".flake8", "pyproject.toml", "settings.json",
                    "installation-manifest.json", "trace-enforcement.json",
                    "versions.json", "claude_desktop_config.json"
                ],
                "exclude_patterns": [],  # NO EXCLUSIONS - ONLY EXACT MATCHES ALLOWED
                "description": "Core configuration files only - EXACT MATCHES ONLY",
                "priority": 9  # LOWEST PRIORITY - sessions should get files first
            },
            "reports/": {
                "patterns": [
                    "*report*.json", "*lint*.json", "*audit*.json",
                    "bandit-*.json", "safety-*.json"
                ],
                "description": "Generated reports and analysis files",
                "priority": 6
            },
            "sessions/": {
                "patterns": [
                    "*session*.json", "*patch*.json", "*state*.json",
                    "*checkpoint*.json", "*agent*.json", "*-agent-*.json",
                    "*metadata*.json", "claude_patch_*.json"
                ],
                "description": (
                    "Session and pipeline state files, agent states, and metadata"
                ),
                "priority": 1  # HIGHEST PRIORITY - get agent/metadata files FIRST
            },
            "docs/": {
                "patterns": ["*.md", "README*", "*guide*", "*documentation*"],
                "exclude_patterns": ["CLAUDE.md"],
                "description": "Documentation files",
                "priority": 8
            },
            "utils/": {
                "patterns": ["*util*.py", "*helper*.py", "*tool*.py"],
                "description": "Utility and helper scripts",
                "priority": 9
            },
            "tests/": {
                "patterns": ["test_*.py", "*_test.py", "conftest.py"],
                "description": "Test files",
                "priority": 10
            },
            ".mcp-system-backups-disconnected/": {
                "patterns": [
                    "*.backup", "*_backup*", "*-backup*", "*.bak", "*.orig", "*.old",
                    "*-enhanced*", "*_enhanced*", "*-v[0-9]*", "*_v[0-9]*",
                    "*_original*", "*_updated*", "*legacy*"
                ],
                "description": "Backup and legacy files"
            },
            ".mcp-system-trash-internal/auto-removed/system/": {
                "patterns": [
                    ".DS_Store", "Thumbs.db", ".gitkeep", "*.tmp", "*.temp",
                    "*.swp", "*.swo", "*~", ".#*"
                ],
                "description": "System generated and temporary files"
            },
            ".mcp-system-trash-internal/auto-removed/cache/": {
                "patterns": [
                    "*.pyc", "*.pyo", "*.egg-info", ".pytest_cache", "__pycache__",
                    "*.cache", ".coverage", "node_modules"
                ],
                "description": "Cache and compiled files"
            },
            ".mcp-system-trash-internal/auto-removed/logs/": {
                "patterns": [
                    "*.log", "*.trace", "*.debug", "pipeline-daemon-*.log",
                    ".pipeline-*.log", "audit-*.log", "error-*.log"
                ],
                "description": "Log and debug files"
            },
            ".mcp-system-trash-internal/auto-removed/temp/": {
                "patterns": [
                    "*.pid", "*.lock", "*.socket", "*.monitor.pid", ".running"
                ],
                "description": "Lock and process files"
            }
        }

        # File type rules
        self.file_type_rules = {
            ".py": {"priority": "high", "organize": True},
            ".json": {"priority": "medium", "organize": True},
            ".md": {"priority": "low", "organize": True},
            ".sh": {"priority": "medium", "organize": True},
            ".yaml": {"priority": "medium", "organize": True},
            ".yml": {"priority": "medium", "organize": True},
            ".toml": {"priority": "medium", "organize": True},
        }

        # CRITICAL: Never move these essential files
        self.protected_files = {
            # Core system files
            "pyproject.toml", "package.json", "package-lock.json", "requirements.txt",
            "setup.py", "setup.cfg", "Cargo.toml", "go.mod", "pom.xml",
            # Configuration files
            "CLAUDE.md", ".claude-instructions.md", ".mcp-sync-config.json",
            ".mcp-pipeline-state.json", ".claude-fixes.json",
            # Git and version control
            ".gitignore", ".gitattributes", ".gitmodules",
            # CI/CD
            ".github", "Dockerfile", "docker-compose.yml",
            # Essential scripts
            "run-pipeline", "run-direct-pipeline", "run-pipeline-claude-interactive"
        }

        # CRITICAL: Never move files in these directories
        self.protected_directories = {
            ".git", "venv", "env", ".venv",
            "src", "lib", "core", "scripts", "bin", "docs", "tests",
            ".github", ".claude", "configs"
        }

        self.observer = Observer()
        self.sync_log = []
        self.load_config()
        self._ensure_trash_structure()

    def load_config(self):
        """Load sync configuration"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                self.directory_rules.update(config.get("directory_rules", {}))
                self.file_type_rules.update(config.get("file_type_rules", {}))

    def save_config(self):
        """Save sync configuration"""
        config = {
            "directory_rules": self.directory_rules,
            "file_type_rules": self.file_type_rules,
            "last_updated": time.time()
        }
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)

    def is_protected_file(self, file_path: Path) -> bool:
        """Check if file is protected from being moved"""
        file_name = file_path.name
        relative_path = file_path.relative_to(self.project_root)

        # Check protected filenames
        if file_name in self.protected_files:
            return True

        # Check protected directories
        path_parts = relative_path.parts
        for protected_dir in self.protected_directories:
            if protected_dir in path_parts:
                return True

        # Additional safety checks
        if file_name.startswith('.env'):  # Environment files
            return True
        if file_name.endswith('.key') or file_name.endswith('.pem'):  # Security keys
            return True
        if ('config' in file_name.lower() and
                file_path.suffix in ['.json', '.yaml', '.yml', '.toml']):
            return True

        return False

    def should_move_file(self, file_path: Path) -> Optional[Path]:
        """Determine if file should be moved and where"""
        if not file_path.is_file():
            return None

        # CRITICAL SAFETY CHECK: Never move protected files
        if self.is_protected_file(file_path):
            return None

        file_name = file_path.name
        relative_path = file_path.relative_to(self.project_root)

        # Skip files already in correct directories
        current_dir = str(relative_path.parent)

        # Check backup patterns first (highest priority)
        backup_patterns = (
            self.directory_rules[".mcp-system-backups-disconnected/"]["patterns"]
        )
        for pattern in backup_patterns:
            if self._matches_pattern(file_name, pattern):
                target_dir = self.backup_dir
                if current_dir != str(target_dir.relative_to(self.project_root)):
                    return target_dir / file_name
                return None

        # Check directory rules in priority order (lowest number = highest priority)
        sorted_rules = sorted(
            self.directory_rules.items(), key=lambda x: x[1].get("priority", 999)
        )

        for target_dir, rules in sorted_rules:
            if target_dir.endswith("backups-disconnected/"):
                continue  # Already handled above

            # Check if file matches patterns for this directory
            patterns = rules.get("patterns", [])
            exclude_patterns = rules.get("exclude_patterns", [])

            # Skip this directory if file matches exclude patterns for THIS directory
            if exclude_patterns and any(
                self._matches_pattern(file_name, pattern)
                for pattern in exclude_patterns
            ):
                continue

            # Special hardcoded protection for configs directory
            if target_dir == "configs/" and (
                file_name.endswith("agent.json") or
                "-agent-" in file_name or
                "metadata" in file_name or
                "patch" in file_name or
                "session" in file_name or
                "state" in file_name
            ):
                continue

            # Check if file matches include patterns
            if any(self._matches_pattern(file_name, pattern) for pattern in patterns):
                target_path = self.project_root / target_dir

                current_normalized = current_dir if current_dir != "." else ""
                target_normalized = target_dir.rstrip('/')

                if current_normalized != target_normalized:
                    return target_path / file_name

        return None

    def _matches_pattern(self, filename: str, pattern: str) -> bool:
        """Check if filename matches pattern (supports wildcards)"""
        import fnmatch
        return fnmatch.fnmatch(filename, pattern)

    def extract_timestamp_from_filename(self, filename: str) -> Optional[Dict]:
        """Extract creation time from filename using standard patterns"""
        import re

        patterns = {
            "compact_iso": r"(\d{8}-\d{6})",  # 20240820-143045
            "underscore_iso": r"(\d{8}_\d{6})",  # 20240820_143045
            "full_iso": r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})",  # 2024-08-20T14:30:45
            "readable": r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})",  # 2024-08-20 14:30:45
        }

        for pattern_name, regex in patterns.items():
            match = re.search(regex, filename)
            if match:
                timestamp_str = match.group(1)
                try:
                    if pattern_name == "compact_iso":
                        dt = datetime.strptime(timestamp_str, "%Y%m%d-%H%M%S")
                    elif pattern_name == "underscore_iso":
                        dt = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                    elif pattern_name == "full_iso":
                        dt = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S")
                    elif pattern_name == "readable":
                        dt = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")

                    return {
                        "extracted": timestamp_str,
                        "format": pattern_name,
                        "datetime": dt,
                        "timestamp": dt.timestamp(),
                        "iso": dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
                        "readable": dt.strftime("%Y-%m-%d %H:%M:%S")
                    }
                except ValueError:
                    continue

        return None

    def move_file(self, source: Path, target: Path) -> bool:
        """Safely move file to target location"""
        try:
            # Create target directory if it doesn't exist
            target.parent.mkdir(parents=True, exist_ok=True)

            # Handle name conflicts
            if target.exists():
                counter = 1
                stem = target.stem
                suffix = target.suffix
                while target.exists():
                    target = target.parent / f"{stem}_{counter}{suffix}"
                    counter += 1

            # Move file
            shutil.move(str(source), str(target))

            # Log the move with proper timestamp notation
            now = datetime.now()
            log_entry = {
                "timestamp": time.time(),
                "timestamp_iso": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "timestamp_readable": now.strftime("%Y-%m-%d %H:%M:%S"),
                "action": "moved",
                "source": str(source),
                "target": str(target),
                "reason": "directory_organization"
            }
            self.sync_log.append(log_entry)

            print(
                f"📁 Moved: {source.relative_to(self.project_root)} → "
                f"{target.relative_to(self.project_root)}"
            )
            return True

        except Exception as e:
            print(f"❌ Failed to move {source}: {e}")
            return False

    def scan_and_organize(self):
        """Scan entire project and organize files"""
        print("🔍 Scanning project for file organization...")

        moved_count = 0
        for file_path in self.project_root.rglob("*"):
            if file_path.is_file():
                target = self.should_move_file(file_path)
                if target:
                    if self.move_file(file_path, target):
                        moved_count += 1

        print(f"✅ Organization complete: {moved_count} files moved")
        return moved_count

    def on_created(self, event):
        """Handle file creation events"""
        if not event.is_directory:
            file_path = Path(event.src_path)
            target = self.should_move_file(file_path)
            if target:
                # Small delay to ensure file is fully written
                time.sleep(0.1)
                self.move_file(file_path, target)

    def on_moved(self, event):
        """Handle file move events"""
        if not event.is_directory:
            file_path = Path(event.dest_path)
            target = self.should_move_file(file_path)
            if target:
                self.move_file(file_path, target)

    def start_monitoring(self):
        """Start real-time file system monitoring"""
        print(f"👀 Starting file sync monitoring on {self.project_root}")

        self.observer.schedule(self, str(self.project_root), recursive=True)
        self.observer.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.observer.stop()
            print("\n🛑 File sync monitoring stopped")

        self.observer.join()

    def generate_sync_report(self) -> str:
        """Generate sync activity report"""
        if not self.sync_log:
            return "No sync activity recorded"

        report = f"""
# MCP File Sync Report
Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}

## Sync Activity Summary
Total file moves: {len(self.sync_log)}

## Recent Activity (Last 10)
"""

        for entry in self.sync_log[-10:]:
            timestamp = entry.get(
                'timestamp_readable',
                time.strftime('%H:%M:%S', time.localtime(entry['timestamp']))
            )
            source = Path(entry['source']).name
            target_dir = Path(entry['target']).parent.name
            report += f"- {timestamp}: {source} → {target_dir}/\n"

        return report

    def add_directory_rule(
        self, directory: str, patterns: List[str], description: str = ""
    ):
        """Add new directory organization rule"""
        self.directory_rules[directory] = {
            "patterns": patterns,
            "description": description
        }
        self.save_config()
        print(f"✅ Added rule for {directory}: {patterns}")

    def list_rules(self):
        """Display current organization rules"""
        print("📋 Current Directory Organization Rules:")
        print("=" * 50)

        for directory, rules in self.directory_rules.items():
            print(f"\n📁 {directory}")
            print(f"   Description: {rules.get('description', 'No description')}")
            print(f"   Patterns: {rules.get('patterns', [])}")
            if 'exclude_patterns' in rules:
                print(f"   Excludes: {rules['exclude_patterns']}")

    def _ensure_trash_structure(self):
        """Create trash directory structure"""
        trash_dirs = [
            self.trash_dir / "auto-removed" / "system",
            self.trash_dir / "auto-removed" / "cache",
            self.trash_dir / "auto-removed" / "logs",
            self.trash_dir / "auto-removed" / "temp",
            self.trash_dir / "conditional" / "databases",
            self.trash_dir / "conditional" / "binaries",
            self.trash_dir / "conditional" / "unknown",
            self.trash_dir / "metadata"
        ]

        for dir_path in trash_dirs:
            dir_path.mkdir(parents=True, exist_ok=True)

        # Create metadata files
        metadata_dir = self.trash_dir / "metadata"
        moved_files_log = metadata_dir / "moved-files.json"
        restore_guide = metadata_dir / "restore.md"

        if not moved_files_log.exists():
            moved_files_log.write_text(
                '{"moved_files": [], "created_at": "' +
                datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '"}'
            )

        if not restore_guide.exists():
            restore_guide.write_text("""# File Restoration Guide

## How to Restore Files

1. **Find the file**: Check `moved-files.json` for the original location
2. **Verify safety**: Ensure the file is still needed
3. **Move back**: Copy from trash to original location
4. **Update log**: Mark as restored in moved-files.json

## Trash Directory Structure

- `auto-removed/`: Automatically moved files (usually safe to delete)
- `conditional/`: Files requiring manual review
- `metadata/`: Tracking and restoration information

## Safety

- Never delete files from `conditional/` without review
- Files older than 30 days in `auto-removed/` can be safely deleted
- Always check `moved-files.json` before permanent deletion
""")

    def clean_non_functional_files(self):
        """Clean up non-functional files by moving to trash"""
        print("🧹 Cleaning non-functional files...")

        moved_count = 0
        protected_count = 0

        for file_path in self.project_root.rglob("*"):
            if file_path.is_file():
                # Check if protected
                if self.is_protected_file(file_path):
                    protected_count += 1
                    continue

                # Check if it's a trash/cleanup file
                target = self._get_trash_target(file_path)
                if target:
                    if self.move_file(file_path, target):
                        moved_count += 1

        print(
            f"✅ Cleanup complete: {moved_count} files moved to trash, "
            f"{protected_count} protected files skipped"
        )
        return moved_count

    def _get_trash_target(self, file_path: Path) -> Optional[Path]:
        """Determine if file should go to trash and where"""
        file_name = file_path.name

        # Check trash patterns
        for target_dir, rules in self.directory_rules.items():
            if not target_dir.startswith(".mcp-system-trash-internal/"):
                continue

            patterns = rules.get("patterns", [])
            for pattern in patterns:
                if self._matches_pattern(file_name, pattern):
                    return self.project_root / target_dir / file_name

        return None


def main():
    """Main CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="MCP File Sync Manager")
    parser.add_argument("action", choices=[
        "scan", "monitor", "report", "rules", "add-rule", "clean"
    ], help="Action to perform")
    parser.add_argument("--directory", help="Directory for add-rule action")
    parser.add_argument(
        "--patterns", nargs="+", help="File patterns for add-rule action"
    )
    parser.add_argument("--description", help="Description for add-rule action")

    args = parser.parse_args()

    sync_manager = MCPFileSyncManager()

    if args.action == "scan":
        sync_manager.scan_and_organize()
    elif args.action == "monitor":
        sync_manager.start_monitoring()
    elif args.action == "report":
        print(sync_manager.generate_sync_report())
    elif args.action == "rules":
        sync_manager.list_rules()
    elif args.action == "add-rule":
        if not all([args.directory, args.patterns]):
            print("❌ --directory and --patterns required for add-rule")
            return
        sync_manager.add_directory_rule(
            args.directory,
            args.patterns,
            args.description or ""
        )
    elif args.action == "clean":
        sync_manager.clean_non_functional_files()

    # Save any config changes
    sync_manager.save_config()


if __name__ == "__main__":
    main()
