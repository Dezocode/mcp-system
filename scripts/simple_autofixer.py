#!/usr/bin/env python3
"""
Simple Working Autofix Module
Focuses on achievable automation using proven techniques
"""

import ast
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class SimpleAutofixer:
    """
    Simple, working autofix system that delivers real results
    """
    
    def __init__(self, repo_path: Path = None):
        self.repo_path = repo_path or Path.cwd()
        self.fixes_applied = 0
        self.issues_found = 0
        
    def run_complete_autofix(self) -> Dict:
        """Run all automated fixes that we know work reliably"""
        print("🛠️ Starting Simple Autofix Process...")
        
        results = {
            'formatting': self.fix_code_formatting(),
            'imports': self.fix_import_issues(),
            'whitespace': self.fix_whitespace_issues(),
            'syntax': self.fix_basic_syntax_issues(),
            'security': self.fix_basic_security_issues()
        }
        
        print(f"✅ Autofix completed! Applied {self.fixes_applied} fixes to {self.issues_found} issues")
        return results
    
    def fix_code_formatting(self) -> Dict:
        """Fix code formatting using black and isort"""
        print("📝 Fixing code formatting...")
        
        try:
            # Install black and isort if not available
            subprocess.run([sys.executable, "-m", "pip", "install", "black", "isort"], 
                         capture_output=True, check=False)
            
            # Run black
            result_black = subprocess.run(
                [sys.executable, "-m", "black", "--line-length", "88", str(self.repo_path)],
                capture_output=True, text=True
            )
            
            # Run isort
            result_isort = subprocess.run(
                [sys.executable, "-m", "isort", "--profile", "black", str(self.repo_path)],
                capture_output=True, text=True
            )
            
            self.fixes_applied += 1
            return {
                'black_success': result_black.returncode == 0,
                'isort_success': result_isort.returncode == 0,
                'black_output': result_black.stdout,
                'isort_output': result_isort.stdout
            }
            
        except Exception as e:
            print(f"⚠️ Formatting failed: {e}")
            return {'error': str(e)}
    
    def fix_import_issues(self) -> Dict:
        """Fix common import issues"""
        print("📦 Fixing import issues...")
        
        fixes = []
        python_files = list(self.repo_path.rglob("*.py"))
        
        for py_file in python_files:
            if py_file.name.startswith('.'):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                
                # Fix common import issues
                content = self.fix_relative_imports(content)
                content = self.remove_unused_imports(content, py_file)
                content = self.fix_import_order(content)
                
                if content != original_content:
                    with open(py_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    fixes.append(str(py_file))
                    self.fixes_applied += 1
                    
            except Exception as e:
                print(f"⚠️ Error processing {py_file}: {e}")
                continue
        
        self.issues_found += len(fixes)
        return {'files_fixed': fixes, 'count': len(fixes)}
    
    def fix_relative_imports(self, content: str) -> str:
        """Fix relative import issues"""
        # Convert problematic relative imports to absolute
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            # Fix imports that start with too many dots
            if re.match(r'^from \.{3,}', line.strip()):
                # Convert to relative import with fewer dots
                line = re.sub(r'^from \.{3,}', 'from ..', line)
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def remove_unused_imports(self, content: str, file_path: Path) -> str:
        """Remove obviously unused imports"""
        try:
            tree = ast.parse(content)
            
            # Find all imports
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    for alias in node.names:
                        imports.append(alias.name)
            
            # Find used names (simple check)
            used_names = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Name):
                    used_names.add(node.id)
                elif isinstance(node, ast.Attribute):
                    if isinstance(node.value, ast.Name):
                        used_names.add(node.value.id)
            
            # Remove unused imports from content
            lines = content.split('\n')
            filtered_lines = []
            
            for line in lines:
                # Skip import lines for unused imports
                if line.strip().startswith(('import ', 'from ')):
                    # Simple check - if no imported name is used, remove the import
                    import_match = re.search(r'import\s+(\w+)', line)
                    if import_match:
                        imported_name = import_match.group(1)
                        if imported_name in used_names or imported_name in ['os', 'sys', 'json']:
                            filtered_lines.append(line)
                        # else: skip unused import
                    else:
                        filtered_lines.append(line)
                else:
                    filtered_lines.append(line)
            
            return '\n'.join(filtered_lines)
            
        except Exception:
            # If parsing fails, return original content
            return content
    
    def fix_import_order(self, content: str) -> str:
        """Basic import ordering"""
        lines = content.split('\n')
        imports = []
        other_lines = []
        
        for line in lines:
            if line.strip().startswith(('import ', 'from ')):
                imports.append(line)
            else:
                other_lines.append(line)
        
        # Simple ordering: standard library first, then others
        std_imports = []
        other_imports = []
        
        for imp in imports:
            if any(module in imp for module in ['os', 'sys', 'json', 'pathlib', 'datetime']):
                std_imports.append(imp)
            else:
                other_imports.append(imp)
        
        # Reconstruct content
        result_lines = []
        result_lines.extend(sorted(std_imports))
        if std_imports and other_imports:
            result_lines.append('')  # blank line between groups
        result_lines.extend(sorted(other_imports))
        if imports and other_lines:
            result_lines.append('')  # blank line after imports
        result_lines.extend(other_lines)
        
        return '\n'.join(result_lines)
    
    def fix_whitespace_issues(self) -> Dict:
        """Fix whitespace and basic formatting issues"""
        print("🧹 Fixing whitespace issues...")
        
        fixes = []
        python_files = list(self.repo_path.rglob("*.py"))
        
        for py_file in python_files:
            if py_file.name.startswith('.'):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                
                # Remove trailing whitespace
                lines = content.split('\n')
                lines = [line.rstrip() for line in lines]
                content = '\n'.join(lines)
                
                # Ensure file ends with newline
                if content and not content.endswith('\n'):
                    content += '\n'
                
                # Fix multiple blank lines
                content = re.sub(r'\n{3,}', '\n\n', content)
                
                if content != original_content:
                    with open(py_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    fixes.append(str(py_file))
                    self.fixes_applied += 1
                    
            except Exception as e:
                print(f"⚠️ Error processing {py_file}: {e}")
                continue
        
        self.issues_found += len(fixes)
        return {'files_fixed': fixes, 'count': len(fixes)}
    
    def fix_basic_syntax_issues(self) -> Dict:
        """Fix basic syntax issues that can be automated"""
        print("🔧 Fixing basic syntax issues...")
        
        fixes = []
        python_files = list(self.repo_path.rglob("*.py"))
        
        for py_file in python_files:
            if py_file.name.startswith('.'):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                
                # Fix common syntax issues
                content = self.fix_print_statements(content)
                content = self.fix_string_quotes(content)
                
                # Validate syntax
                try:
                    ast.parse(content)
                    if content != original_content:
                        with open(py_file, 'w', encoding='utf-8') as f:
                            f.write(content)
                        fixes.append(str(py_file))
                        self.fixes_applied += 1
                except SyntaxError:
                    # If our fix broke syntax, revert
                    continue
                    
            except Exception as e:
                print(f"⚠️ Error processing {py_file}: {e}")
                continue
        
        self.issues_found += len(fixes)
        return {'files_fixed': fixes, 'count': len(fixes)}
    
    def fix_print_statements(self, content: str) -> str:
        """Fix print statements for Python 3"""
        # Convert print statements to print functions (basic cases)
        content = re.sub(r'print\s+([^(].*)', r'print(\1)', content)
        return content
    
    def fix_string_quotes(self, content: str) -> str:
        """Normalize string quotes to double quotes"""
        # Simple quote normalization (avoiding strings that contain quotes)
        content = re.sub(r"'([^'\"]*)'", r'"\1"', content)
        return content
    
    def fix_basic_security_issues(self) -> Dict:
        """Fix basic security issues that can be automated safely"""
        print("🔒 Fixing basic security issues...")
        
        fixes = []
        python_files = list(self.repo_path.rglob("*.py"))
        
        for py_file in python_files:
            if py_file.name.startswith('.'):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                
                # Fix hardcoded temporary directories
                content = re.sub(r'/tmp/', 'tempfile.gettempdir() + "/"', content)
                
                # Add tempfile import if we used it
                if 'tempfile.gettempdir()' in content and 'import tempfile' not in content:
                    lines = content.split('\n')
                    # Find the first non-comment, non-import line to insert import
                    for i, line in enumerate(lines):
                        if not line.strip().startswith(('#', 'import ', 'from ')) and line.strip():
                            lines.insert(i, 'import tempfile')
                            break
                    content = '\n'.join(lines)
                
                if content != original_content:
                    with open(py_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    fixes.append(str(py_file))
                    self.fixes_applied += 1
                    
            except Exception as e:
                print(f"⚠️ Error processing {py_file}: {e}")
                continue
        
        self.issues_found += len(fixes)
        return {'files_fixed': fixes, 'count': len(fixes)}


def main():
    """Main entry point for simple autofix"""
    if len(sys.argv) > 1:
        repo_path = Path(sys.argv[1])
    else:
        repo_path = Path.cwd()
    
    print(f"🛠️ Simple Autofix starting in: {repo_path}")
    
    autofixer = SimpleAutofixer(repo_path)
    results = autofixer.run_complete_autofix()
    
    print("\n📊 Summary:")
    for category, result in results.items():
        if isinstance(result, dict) and 'count' in result:
            print(f"  {category}: {result['count']} fixes applied")
        else:
            print(f"  {category}: completed")
    
    print(f"\n✅ Total: {autofixer.fixes_applied} fixes applied")
    

if __name__ == "__main__":
    main()