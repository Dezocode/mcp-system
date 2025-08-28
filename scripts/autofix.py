#!/usr/bin/env python3
"""
MCP Autofix Tool - Consolidated automated fixing system
Integrates proven tools: black, isort, flake8, mypy, bandit
"""

import ast
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import click


class MCPAutofix:
    """
    Consolidated autofix system that delivers real results using proven tools
    """
    
    def __init__(self, repo_path: Path = None, dry_run: bool = False, verbose: bool = False):
        self.repo_path = repo_path or Path.cwd()
        self.dry_run = dry_run
        self.verbose = verbose
        self.fixes_applied = 0
        self.issues_found = 0
        self.results = {}
        
    def log(self, message: str, level: str = "info"):
        """Log message with optional verbosity control"""
        if level == "verbose" and not self.verbose:
            return
        
        prefixes = {
            "info": "ℹ️",
            "success": "✅", 
            "warning": "⚠️",
            "error": "❌",
            "verbose": "🔍"
        }
        prefix = prefixes.get(level, "•")
        print(f"{prefix} {message}")
    
    def run_command(self, cmd: List[str], description: str = "") -> Tuple[bool, str, str]:
        """Run command and return success, stdout, stderr"""
        if self.dry_run:
            self.log(f"[DRY RUN] Would run: {' '.join(cmd)}", "verbose")
            return True, "", ""
        
        try:
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                cwd=self.repo_path,
                timeout=300  # 5 minute timeout
            )
            
            success = result.returncode == 0
            if not success and self.verbose:
                self.log(f"Command failed: {' '.join(cmd)}", "error")
                self.log(f"Error: {result.stderr}", "verbose")
            
            return success, result.stdout, result.stderr
            
        except subprocess.TimeoutExpired:
            self.log(f"Command timed out: {' '.join(cmd)}", "error")
            return False, "", "Command timed out"
        except Exception as e:
            self.log(f"Command error: {e}", "error")
            return False, "", str(e)
    
    def install_tools(self) -> bool:
        """Install required tools if not available"""
        tools = ['black', 'isort', 'flake8', 'mypy', 'bandit']
        missing_tools = []
        
        for tool in tools:
            success, _, _ = self.run_command(['python3', '-m', tool, '--version'])
            if not success:
                missing_tools.append(tool)
        
        if missing_tools:
            self.log(f"Installing tools: {', '.join(missing_tools)}")
            success, stdout, stderr = self.run_command([
                sys.executable, '-m', 'pip', 'install'
            ] + missing_tools)
            
            if not success:
                self.log(f"Failed to install tools: {stderr}", "error")
                return False
        
        return True
    
    def fix_code_formatting(self) -> Dict:
        """Fix code formatting using black and isort"""
        self.log("Fixing code formatting...")
        
        results = {'black': False, 'isort': False}
        
        # Run black
        success, stdout, stderr = self.run_command([
            sys.executable, '-m', 'black', 
            '--line-length', '88',
            '--target-version', 'py38',
            str(self.repo_path)
        ])
        results['black'] = success
        
        if success:
            self.fixes_applied += 1
            self.log("Code formatted with black", "success")
        else:
            self.log(f"Black formatting failed: {stderr}", "error")
        
        # Run isort
        success, stdout, stderr = self.run_command([
            sys.executable, '-m', 'isort',
            '--profile', 'black',
            '--line-length', '88',
            str(self.repo_path)
        ])
        results['isort'] = success
        
        if success:
            self.fixes_applied += 1
            self.log("Imports sorted with isort", "success")
        else:
            self.log(f"Import sorting failed: {stderr}", "error")
        
        return results
    
    def fix_whitespace_issues(self) -> Dict:
        """Fix whitespace and basic formatting issues"""
        self.log("Fixing whitespace issues...")
        
        if self.dry_run:
            self.log("[DRY RUN] Would fix whitespace issues", "verbose")
            return {'files_processed': 0}
        
        files_fixed = 0
        python_files = list(self.repo_path.rglob("*.py"))
        
        for py_file in python_files:
            if any(part.startswith('.') for part in py_file.parts):
                continue  # Skip hidden files/directories
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                
                # Remove trailing whitespace
                content = re.sub(r'[ \t]+$', '', content, flags=re.MULTILINE)
                
                # Ensure single newline at end of file
                content = content.rstrip() + '\n'
                
                # Fix multiple consecutive blank lines (max 2)
                content = re.sub(r'\n{4,}', '\n\n\n', content)
                
                if content != original_content:
                    # Validate syntax before writing
                    try:
                        ast.parse(content)
                        with open(py_file, 'w', encoding='utf-8') as f:
                            f.write(content)
                        files_fixed += 1
                        self.log(f"Fixed whitespace in {py_file}", "verbose")
                    except SyntaxError:
                        self.log(f"Skipped {py_file} - syntax error after fix", "warning")
                        
            except Exception as e:
                self.log(f"Error processing {py_file}: {e}", "error")
        
        if files_fixed > 0:
            self.fixes_applied += files_fixed
            self.log(f"Fixed whitespace in {files_fixed} files", "success")
        
        return {'files_processed': files_fixed}
    
    def run_security_scan(self) -> Dict:
        """Run security analysis with bandit"""
        self.log("Running security scan...")
        
        output_file = self.repo_path / "bandit-report.json"
        
        success, stdout, stderr = self.run_command([
            sys.executable, '-m', 'bandit',
            '-r', str(self.repo_path),
            '-f', 'json',
            '-o', str(output_file)
        ])
        
        results = {'scan_completed': success, 'report_file': str(output_file)}
        
        if success:
            self.log(f"Security scan completed: {output_file}", "success")
            
            # Parse results if available
            try:
                with open(output_file, 'r') as f:
                    report = json.load(f)
                    issues = len(report.get('results', []))
                    results['issues_found'] = issues
                    if issues > 0:
                        self.log(f"Found {issues} security issues", "warning")
                    else:
                        self.log("No security issues found", "success")
            except Exception as e:
                self.log(f"Could not parse security report: {e}", "error")
        else:
            self.log(f"Security scan failed: {stderr}", "error")
        
        return results
    
    def run_quality_analysis(self) -> Dict:
        """Run quality analysis with flake8 and mypy"""
        self.log("Running quality analysis...")
        
        results = {'flake8': False, 'mypy': False}
        
        # Run flake8
        flake8_output = self.repo_path / "flake8-report.txt"
        success, stdout, stderr = self.run_command([
            sys.executable, '-m', 'flake8',
            '--max-line-length=88',
            '--extend-ignore=E203,W503',
            '--output-file', str(flake8_output),
            str(self.repo_path)
        ])
        
        results['flake8'] = success
        results['flake8_report'] = str(flake8_output)
        
        if success:
            self.log("Flake8 analysis completed", "success")
        else:
            self.log("Flake8 found style issues", "warning")
        
        # Run mypy  
        mypy_output = self.repo_path / "mypy-report.txt"
        with open(mypy_output, 'w') as f:
            success, stdout, stderr = self.run_command([
                sys.executable, '-m', 'mypy',
                '--ignore-missing-imports',
                '--no-error-summary',
                str(self.repo_path)
            ])
            f.write(stdout)
            f.write(stderr)
        
        results['mypy'] = success
        results['mypy_report'] = str(mypy_output)
        
        if success:
            self.log("MyPy analysis completed", "success")
        else:
            self.log("MyPy found type issues", "warning")
        
        return results
    
    def run_tests(self) -> Dict:
        """Run available tests"""
        self.log("Running tests...")
        
        test_results = {'ran_tests': False, 'test_framework': None}
        
        # Check for pytest
        if (self.repo_path / "pytest.ini").exists() or \
           (self.repo_path / "pyproject.toml").exists():
            
            success, stdout, stderr = self.run_command([
                sys.executable, '-m', 'pytest', '--tb=short', '-v'
            ])
            
            test_results['ran_tests'] = True
            test_results['test_framework'] = 'pytest'
            test_results['success'] = success
            
            # Save test output
            test_output = self.repo_path / "test-results.txt"
            with open(test_output, 'w') as f:
                f.write(stdout)
                f.write(stderr)
            test_results['output_file'] = str(test_output)
            
            if success:
                self.log("Tests passed", "success")
            else:
                self.log("Some tests failed", "warning")
        
        # Fallback to unittest
        elif (self.repo_path / "tests").exists():
            success, stdout, stderr = self.run_command([
                sys.executable, '-m', 'unittest', 'discover', '-v'
            ])
            
            test_results['ran_tests'] = True
            test_results['test_framework'] = 'unittest'
            test_results['success'] = success
            
            if success:
                self.log("Tests passed", "success")
            else:
                self.log("Some tests failed", "warning")
        else:
            self.log("No test framework detected", "warning")
        
        return test_results
    
    def generate_report(self) -> Dict:
        """Generate comprehensive autofix report"""
        self.log("Generating autofix report...")
        
        report = {
            'timestamp': str(Path.cwd()),
            'summary': {
                'fixes_applied': self.fixes_applied,
                'issues_found': self.issues_found,
                'dry_run': self.dry_run
            },
            'results': self.results
        }
        
        # Save report
        report_file = self.repo_path / "autofix-report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.log(f"Report saved: {report_file}", "success")
        return report
    
    def run_complete_autofix(self) -> Dict:
        """Run complete autofix process"""
        self.log("🛠️ Starting MCP Autofix Process...")
        
        # Install tools first
        if not self.install_tools():
            self.log("Failed to install required tools", "error")
            return {'error': 'tool_installation_failed'}
        
        # Phase 1: Code formatting
        self.results['formatting'] = self.fix_code_formatting()
        
        # Phase 2: Whitespace cleanup  
        self.results['whitespace'] = self.fix_whitespace_issues()
        
        # Phase 3: Security scan
        self.results['security'] = self.run_security_scan()
        
        # Phase 4: Quality analysis
        self.results['quality'] = self.run_quality_analysis()
        
        # Phase 5: Run tests
        self.results['tests'] = self.run_tests()
        
        # Generate final report
        report = self.generate_report()
        
        self.log(f"🎉 Autofix completed! Applied {self.fixes_applied} fixes", "success")
        self.log("📊 Check autofix-report.json for detailed results")
        
        return report


@click.command()
@click.option('--repo-path', type=click.Path(exists=True), help='Repository path')
@click.option('--dry-run', is_flag=True, help='Show what would be fixed without applying changes')
@click.option('--verbose', is_flag=True, help='Show detailed output')
@click.option('--format-only', is_flag=True, help='Only run code formatting')
@click.option('--scan-only', is_flag=True, help='Only run analysis without fixes')
def main(repo_path, dry_run, verbose, format_only, scan_only):
    """MCP Autofix Tool - Consolidated automated fixing system"""
    
    autofix = MCPAutofix(
        repo_path=Path(repo_path) if repo_path else None,
        dry_run=dry_run,
        verbose=verbose
    )
    
    if format_only:
        # Only run formatting
        autofix.log("🎨 Running code formatting only...")
        results = autofix.fix_code_formatting()
        autofix.log(f"Formatting completed: {results}")
        
    elif scan_only:
        # Only run analysis
        autofix.log("🔍 Running analysis only...")
        security_results = autofix.run_security_scan()
        quality_results = autofix.run_quality_analysis()
        autofix.log(f"Analysis completed - Security: {security_results}, Quality: {quality_results}")
        
    else:
        # Run complete autofix
        results = autofix.run_complete_autofix()
        
        if 'error' in results:
            sys.exit(1)


if __name__ == '__main__':
    main()