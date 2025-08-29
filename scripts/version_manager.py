from utils.functions import main
#!/usr/bin/env python3
from analyze_functions import project_root
from utils.functions import __file__
from utils.functions import f
from sys import version
from .autofix import line
from utils.functions import e
"""
Version Manager for MCP System
Handles semantic versioning and automated version bumps.
"""
import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
import toml
from packaging.version import Version
class VersionManager:
    """Manages version bumping and release preparation"""
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path(__file__).parent.parent
        self.pyproject_path = self.project_root / "pyproject.toml"
        self.init_path = self.project_root / "src" / "__init__.py"
    def get_current_version(self) -> str:
        """Get current version from pyproject.toml"""
        if not self.pyproject_path.exists():
            raise FileNotFoundError("pyproject.toml not found")
        with open(self.pyproject_path, "r") as f:
            data = toml.load(f)
        return data["project"]["version"]
    def bump_version(self, version_type: str, custom_version: str = None) -> str:
        """Bump version based on type (patch/minor/major) or use custom version"""
        current = Version(self.get_current_version())
        if custom_version:
            new_version = Version(custom_version)
        elif version_type == "major":
            new_version = Version(f"{current.major + 1}.0.0")
        elif version_type == "minor":
            new_version = Version(f"{current.major}.{current.minor + 1}.0")
        elif version_type == "patch":
            new_version = Version(
                f"{current.major}.{current.minor}.{current.micro + 1}"
            )
        else:
            raise ValueError(f"Invalid version type: {version_type}")
        return str(new_version)
    def update_version_files(self, new_version: str) -> bool:
        """Update version in pyproject.toml and __init__.py"""
        try:
            # Update pyproject.toml
            with open(self.pyproject_path, "r") as f:
                data = toml.load(f)
            data["project"]["version"] = new_version
            with open(self.pyproject_path, "w") as f:
                toml.dump(data, f)
            print(f"✅ Updated pyproject.toml version to {new_version}")
            # Update __init__.py if it exists
            if self.init_path.exists():
                with open(self.init_path, "r") as f:
                    content = f.read()
                # Replace __version__ line
                updated_content = []
                for line in content.split("\n"):
                    if line.strip().startswith("__version__"):
                        updated_content.append(f'__version__ = "{new_version}"')
                    else:
                        updated_content.append(line)
                with open(self.init_path, "w") as f:
                    f.write("\n".join(updated_content))
                print(f"✅ Updated __init__.py version to {new_version}")
            return True
        except Exception as e:
            print(f"❌ Failed to update version files: {e}")
            return False
    def create_version_branch(self, version: str) -> bool:
        """Create a version branch and commit changes"""
        branch_name = f"version-{version}"
        try:
            # Check if we're in a git repository
            subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                check=True,
                capture_output=True,
                cwd=self.project_root,
            )
            # Create and switch to version branch
            subprocess.run(
                ["git", "checkout", "-b", branch_name],
                check=True,
                cwd=self.project_root,
            )
            # Add changed files
            files_to_add = ["pyproject.toml"]
            if self.init_path.exists():
                files_to_add.append("src/__init__.py")
            subprocess.run(
                ["git", "add"] + files_to_add, check=True, cwd=self.project_root
            )
            # Commit changes
            commit_message = f"""🚀 Bump version to {version}
- Version bump automated by version_manager.py
- Updated pyproject.toml and __init__.py
- Ready for release
🤖 Generated with [Claude Code](https://claude.ai/code)
Co-Authored-By: Claude <noreply@anthropic.com>"""
            subprocess.run(
                ["git", "commit", "-m", commit_message],
                check=True,
                cwd=self.project_root,
            )
            print(f"✅ Created version branch: {branch_name}")
            print(f"✅ Committed version changes")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Git operation failed: {e}")
            return False
    def push_version_branch(self, version: str) -> bool:
        """Push version branch to remote"""
        branch_name = f"version-{version}"
        try:
            subprocess.run(
                ["git", "push", "origin", branch_name],
                check=True,
                cwd=self.project_root,
            )
            print(f"✅ Pushed version branch: {branch_name}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to push version branch: {e}")
            return False
    def create_tag(self, version: str) -> bool:
        """Create and push a git tag for the version"""
        tag_name = f"v{version}"
        try:
            # Create annotated tag
            tag_message = f"""Release {tag_name}
📦 Version {version} release
📅 Release date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}
🤖 Generated with [Claude Code](https://claude.ai/code)"""
            subprocess.run(
                ["git", "tag", "-a", tag_name, "-m", tag_message],
                check=True,
                cwd=self.project_root,
            )
            # Push tag
            subprocess.run(
                ["git", "push", "origin", tag_name], check=True, cwd=self.project_root
            )
            print(f"✅ Created and pushed tag: {tag_name}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create/push tag: {e}")
            return False
    def analyze_commits_for_version_type(self) -> str:
        """Analyze recent commits to suggest version bump type"""
        try:
            # Get commits since last tag
            result = subprocess.run(
                ["git", "describe", "--tags", "--abbrev=0"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )
            if result.returncode == 0:
                last_tag = result.stdout.strip()
                commit_range = f"{last_tag}..HEAD"
            else:
                # No tags yet, check all commits
                commit_range = "HEAD"
            # Get commit messages
            result = subprocess.run(
                ["git", "log", "--pretty=format:%s", commit_range],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )
            if result.returncode != 0:
                return "patch"  # Default fallback
            commits = result.stdout.strip().split("\n")
            commits = [c for c in commits if c.strip()]  # Filter empty lines
            if not commits:
                return "patch"
            # Analyze commit messages for version type
            has_breaking = any(
                any(keyword in commit.lower() for keyword in ["breaking", "major:"])
                for commit in commits
            )
            has_feature = any(
                any(
                    keyword in commit.lower()
                    for keyword in ["feat:", "feature:", "minor:"]
                )
                for commit in commits
            )
            has_fix = any(
                any(
                    keyword in commit.lower()
                    for keyword in ["fix:", "patch:", "security:"]
                )
                for commit in commits
            )
            if has_breaking:
                return "major"
            elif has_feature:
                return "minor"
            elif has_fix:
                return "patch"
            else:
                # If many commits, suggest patch
                return "patch" if len(commits) > 5 else "none"
        except Exception:
            return "patch"  # Safe default
    def get_version_info(self) -> dict:
        """Get comprehensive version information"""
        current_version = self.get_current_version()
        suggested_type = self.analyze_commits_for_version_type()
        info = {
            "current_version": current_version,
            "suggested_bump": suggested_type,
            "next_versions": {
                "patch": self.bump_version("patch"),
                "minor": self.bump_version("minor"),
                "major": self.bump_version("major"),
            },
        }
        return info
if __name__ == "__main__":
    main()