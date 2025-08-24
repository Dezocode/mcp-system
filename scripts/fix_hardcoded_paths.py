#!/usr/bin/env python3
"""
Automated Path Migration Script
Finds and replaces all hardcoded paths with cross-platform alternatives
"""

import re
import sys
import json
from pathlib import Path
from typing import Dict, List, Tuple
import argparse
import shutil
from datetime import datetime

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from mcp_tools.installation.config.cross_platform import CrossPlatformResolver


class PathMigrator:
    """Migrate hardcoded paths to cross-platform code"""
    
    def __init__(self, dry_run=False, backup=True):
        self.dry_run = dry_run
        self.backup = backup
        self.resolver = CrossPlatformResolver()
        self.changes = []
        self.files_modified = 0
        
        # Define replacement patterns
        self.patterns = [
            # macOS specific paths
            (r'cross_platform.get_path("home") / ', 'cross_platform.get_path("home") / '),
            (r'/Users/\w+/', 'cross_platform.get_path("home") / '),
            
            # Windows paths
            (r'C:\\Users\\\w+\\', 'cross_platform.get_path("home") / '),
            (r'C:\\\\Users\\\\\w+\\\\', 'cross_platform.get_path("home") / '),
            
            # Linux home paths
            (r'cross_platform.get_path("mcp_home") / ', 'cross_platform.get_path("mcp_home") / '),
            (r'/home/\w+/', 'cross_platform.get_path("home") / '),
            
            # Hardcoded command paths
            (r'"cross_platform.get_path("home") / mcp"', 'cross_platform.get_command("mcp")'),
            (r'f"{cross_platform.get_command(\"python\")} "', 'f"{cross_platform.get_command(\\"python\\")} "'),
            (r'f"{cross_platform.get_command(\"pip\")} "', 'f"{cross_platform.get_command(\\"pip\\")} "'),
            
            # Path separators
            (r'os\.path\.sep', 'cross_platform.get_file_separator()'),
            
            # Shell-specific
            (r'#!/usr/bin/env bash', '#!/usr/bin/env bash'),
            (r'#!/usr/bin/env python3', '#!/usr/bin/env python3'),
        ]
        
        # File-specific replacements
        self.file_specific = {
            'mcp-router.py': [
                (r'cmd = f"cross_platform.get_path("home") / mcp {server} \w+"',
                 'cmd = f"{cross_platform.get_command(\\"mcp\\")} {server} {action}"')
            ],
            'Dockerfile': [
                (r'WORKDIR /app', '# Platform-agnostic workdir set by build args\nWORKDIR ${WORKDIR:-/app}'),
                (r'/home/mcpuser', '${MCP_HOME}')
            ]
        }
    
    def scan_file(self, filepath: Path) -> List[Tuple[int, str, str]]:
        """Scan a file for hardcoded paths"""
        if not filepath.exists() or filepath.is_dir():
            return []
        
        issues = []
        try:
            content = filepath.read_text(encoding='utf-8', errors='ignore')
            lines = content.splitlines()
            
            for i, line in enumerate(lines, 1):
                # Check general patterns
                for pattern, _ in self.patterns:
                    if re.search(pattern, line):
                        issues.append((i, line.strip(), pattern))
                
                # Check file-specific patterns
                if filepath.name in self.file_specific:
                    for pattern, _ in self.file_specific[filepath.name]:
                        if re.search(pattern, line):
                            issues.append((i, line.strip(), pattern))
        except Exception as e:
            print(f"Error scanning {filepath}: {e}")
        
        return issues
    
    def fix_file(self, filepath: Path) -> bool:
        """Fix hardcoded paths in a file"""
        if not filepath.exists() or filepath.is_dir():
            return False
        
        try:
            content = filepath.read_text(encoding='utf-8', errors='ignore')
            original_content = content
            
            # Apply general replacements
            for pattern, replacement in self.patterns:
                content = re.sub(pattern, replacement, content)
            
            # Apply file-specific replacements
            if filepath.name in self.file_specific:
                for pattern, replacement in self.file_specific[filepath.name]:
                    content = re.sub(pattern, replacement, content)
            
            # Add import if needed (for Python files)
            if filepath.suffix == '.py' and 'cross_platform' in content and 'from mcp_tools.installation.config.cross_platform import' not in content:
                lines = content.splitlines()
                import_added = False
                
                for i, line in enumerate(lines):
                    if line.startswith('import ') or line.startswith('from '):
                        # Add after other imports
                        lines.insert(i + 1, 'from mcp_tools.installation.config.cross_platform import cross_platform')
                        import_added = True
                        break
                
                if not import_added:
                    # Add at the beginning after shebang and docstring
                    insert_pos = 0
                    if lines and lines[0].startswith('#!'):
                        insert_pos = 1
                    if len(lines) > insert_pos and lines[insert_pos].startswith('"""'):
                        # Find end of docstring
                        for j in range(insert_pos + 1, len(lines)):
                            if '"""' in lines[j]:
                                insert_pos = j + 1
                                break
                    
                    lines.insert(insert_pos, '\nfrom mcp_tools.installation.config.cross_platform import cross_platform\n')
                
                content = '\n'.join(lines)
            
            if content != original_content:
                if self.backup:
                    # Create backup
                    backup_path = filepath.with_suffix(filepath.suffix + '.backup')
                    shutil.copy2(filepath, backup_path)
                
                if not self.dry_run:
                    filepath.write_text(content, encoding='utf-8')
                
                self.files_modified += 1
                self.changes.append({
                    'file': str(filepath),
                    'changes': len(re.findall(r'cross_platform', content)) - len(re.findall(r'cross_platform', original_content))
                })
                return True
        
        except Exception as e:
            print(f"Error fixing {filepath}: {e}")
        
        return False
    
    def scan_directory(self, directory: Path) -> Dict[str, List]:
        """Scan entire directory for issues"""
        issues = {}
        
        # Define file patterns to check
        patterns = ['*.py', '*.sh', '*.yml', '*.yaml', '*.json', 'Dockerfile*']
        
        for pattern in patterns:
            for filepath in directory.rglob(pattern):
                # Skip certain directories
                if any(skip in str(filepath) for skip in ['.git', '__pycache__', 'venv', '.backup']):
                    continue
                
                file_issues = self.scan_file(filepath)
                if file_issues:
                    issues[str(filepath)] = file_issues
        
        return issues
    
    def fix_directory(self, directory: Path):
        """Fix all files in directory"""
        print(f"{'DRY RUN: ' if self.dry_run else ''}Fixing hardcoded paths in {directory}")
        
        # First scan for issues
        issues = self.scan_directory(directory)
        
        if not issues:
            print("✅ No hardcoded paths found!")
            return
        
        print(f"Found hardcoded paths in {len(issues)} files")
        
        # Fix each file
        for filepath in issues:
            print(f"  Fixing {filepath}...")
            self.fix_file(Path(filepath))
        
        print(f"\n{'Would modify' if self.dry_run else 'Modified'} {self.files_modified} files")
        
        # Save report
        self.save_report()
    
    def save_report(self):
        """Save migration report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'dry_run': self.dry_run,
            'files_modified': self.files_modified,
            'changes': self.changes,
            'platform': self.resolver.platform_info
        }
        
        report_path = Path('migration_report.json')
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📊 Report saved to {report_path}")


def main():
    parser = argparse.ArgumentParser(description='Fix hardcoded paths for cross-platform compatibility')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without modifying files')
    parser.add_argument('--no-backup', action='store_true', help='Do not create backup files')
    parser.add_argument('--directory', type=Path, default=Path.cwd(), help='Directory to process')
    parser.add_argument('--scan-only', action='store_true', help='Only scan for issues, do not fix')
    
    args = parser.parse_args()
    
    migrator = PathMigrator(dry_run=args.dry_run or args.scan_only, backup=not args.no_backup)
    
    if args.scan_only:
        print("Scanning for hardcoded paths...")
        issues = migrator.scan_directory(args.directory)
        
        if issues:
            print(f"\n⚠️  Found hardcoded paths in {len(issues)} files:\n")
            for filepath, file_issues in issues.items():
                print(f"\n{filepath}:")
                for line_num, line, pattern in file_issues[:3]:  # Show first 3 issues
                    print(f"  Line {line_num}: {line[:80]}...")
                if len(file_issues) > 3:
                    print(f"  ... and {len(file_issues) - 3} more issues")
        else:
            print("✅ No hardcoded paths found!")
    else:
        migrator.fix_directory(args.directory)


if __name__ == '__main__':
    main()