#!/usr/bin/env python3
"""
Enhanced Autofix Engine v3.0 - Higher Resolution Logic & Watchdog Integration

This module provides the next-generation autofix capabilities with:
- High-resolution issue analysis and classification
- Proactive prevention through integrated watchdog monitoring
- Self-healing capabilities with automatic regression detection
- Learning system to analyze patterns and prevent similar issues
- Unified control system coordinating all autofix components
"""

import ast
import asyncio
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from concurrent.futures import ThreadPoolExecutor

# Import existing components (with error handling for missing modules)
try:
    from .claude_quality_patcher import EnhancedClaudeQualityPatcher
except ImportError:
    try:
        from claude_quality_patcher import EnhancedClaudeQualityPatcher
    except ImportError:
        EnhancedClaudeQualityPatcher = None

try:
    from .mcp_tools_monitor import MCPToolsStandardizer, MCPToolsEventHandler
except ImportError:
    try:
        from mcp_tools_monitor import MCPToolsStandardizer, MCPToolsEventHandler
    except ImportError:
        MCPToolsStandardizer = None
        MCPToolsEventHandler = None

try:
    from .version_keeper import MCPVersionKeeper
except ImportError:
    try:
        from version_keeper import MCPVersionKeeper
    except ImportError:
        MCPVersionKeeper = None

try:
    from watchdog.events import FileSystemEventHandler
    from watchdog.observers import Observer
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    print("⚠️ Watchdog not available - install with: pip install watchdog")


class IssueCategory(Enum):
    """Enhanced issue categorization for higher resolution analysis"""
    CRITICAL_SYNTAX = "critical_syntax"          # Prevents execution
    CRITICAL_IMPORT = "critical_import"          # Breaks module loading
    CRITICAL_SECURITY = "critical_security"     # Security vulnerabilities
    HIGH_LOGIC = "high_logic"                   # Logic errors, undefined functions
    HIGH_QUALITY = "high_quality"               # Code quality issues
    MEDIUM_STYLE = "medium_style"               # Style and formatting
    MEDIUM_OPTIMIZATION = "medium_optimization" # Performance optimizations
    LOW_COSMETIC = "low_cosmetic"               # Cosmetic improvements
    PREVENTABLE_REGRESSION = "preventable_regression"  # Issues that could be prevented


class IssueSeverity(Enum):
    """Issue severity levels for prioritization"""
    BLOCKER = 1      # Prevents any execution
    CRITICAL = 2     # Breaks major functionality
    HIGH = 3         # Significant issues
    MEDIUM = 4       # Moderate issues
    LOW = 5          # Minor issues
    COSMETIC = 6     # Cosmetic only


@dataclass
class EnhancedIssue:
    """Enhanced issue representation with detailed metadata"""
    id: str
    category: IssueCategory
    severity: IssueSeverity
    file_path: Path
    line_number: int
    column: Optional[int] = None
    description: str = ""
    context: Dict[str, Any] = field(default_factory=dict)
    suggested_fix: Optional[str] = None
    prevention_strategy: Optional[str] = None
    confidence: float = 1.0  # 0.0 to 1.0
    fix_history: List[Dict] = field(default_factory=list)
    dependencies: Set[str] = field(default_factory=set)
    impact_scope: Set[Path] = field(default_factory=set)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'id': self.id,
            'category': self.category.value,
            'severity': self.severity.value,
            'file_path': str(self.file_path),
            'line_number': self.line_number,
            'column': self.column,
            'description': self.description,
            'context': self.context,
            'suggested_fix': self.suggested_fix,
            'prevention_strategy': self.prevention_strategy,
            'confidence': self.confidence,
            'fix_history': self.fix_history,
            'dependencies': list(self.dependencies),
            'impact_scope': [str(p) for p in self.impact_scope]
        }


class HighResolutionAnalyzer:
    """Advanced analyzer for high-resolution issue detection and classification"""
    
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.logger = logging.getLogger(__name__)
        self.ast_cache = {}
        self.import_graph = {}
        self.function_registry = {}
        self.class_registry = {}
        self.dependency_map = {}
        
    def analyze_codebase(self) -> List[EnhancedIssue]:
        """Perform comprehensive high-resolution analysis"""
        self.logger.info("🔬 Starting high-resolution codebase analysis...")
        
        # Build comprehensive maps
        self._build_codebase_maps()
        
        issues = []
        
        # Multi-layer analysis
        issues.extend(self._analyze_syntax_issues())
        issues.extend(self._analyze_import_issues())
        issues.extend(self._analyze_security_issues())
        issues.extend(self._analyze_logic_issues())
        issues.extend(self._analyze_quality_issues())
        issues.extend(self._analyze_potential_regressions())
        
        # Enhance issues with dependency and impact analysis
        self._enhance_issues_with_impact_analysis(issues)
        
        # Sort by priority
        issues.sort(key=lambda x: (x.severity.value, -x.confidence))
        
        self.logger.info(f"✅ Analysis complete: {len(issues)} issues found")
        return issues
    
    def _build_codebase_maps(self):
        """Build comprehensive maps of the codebase structure"""
        self.logger.info("🗺️ Building codebase maps...")
        
        for py_file in self.repo_path.rglob("*.py"):
            if self._should_skip_file(py_file):
                continue
                
            try:
                content = py_file.read_text(encoding='utf-8')
                tree = ast.parse(content, filename=str(py_file))
                self.ast_cache[py_file] = tree
                
                # Extract definitions
                self._extract_definitions(tree, py_file)
                self._extract_imports(tree, py_file)
                
            except (SyntaxError, UnicodeDecodeError) as e:
                self.logger.warning(f"⚠️ Could not parse {py_file}: {e}")
    
    def _extract_definitions(self, tree: ast.AST, file_path: Path):
        """Extract function and class definitions from AST"""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if str(file_path) not in self.function_registry:
                    self.function_registry[str(file_path)] = []
                self.function_registry[str(file_path)].append({
                    'name': node.name,
                    'line': node.lineno,
                    'args': [arg.arg for arg in node.args.args],
                    'is_method': self._is_method_in_class(node, tree)
                })
            elif isinstance(node, ast.ClassDef):
                if str(file_path) not in self.class_registry:
                    self.class_registry[str(file_path)] = []
                self.class_registry[str(file_path)].append({
                    'name': node.name,
                    'line': node.lineno,
                    'methods': [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                })
    
    def _extract_imports(self, tree: ast.AST, file_path: Path):
        """Extract import statements from AST"""
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append({
                        'type': 'import',
                        'module': alias.name,
                        'name': alias.asname or alias.name,
                        'line': node.lineno
                    })
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for alias in node.names:
                    imports.append({
                        'type': 'from_import',
                        'module': module,
                        'name': alias.name,
                        'asname': alias.asname,
                        'line': node.lineno
                    })
        
        self.import_graph[str(file_path)] = imports
    
    def _is_method_in_class(self, func_node: ast.FunctionDef, tree: ast.AST) -> bool:
        """Check if function is defined inside a class"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if func_node in node.body:
                    return True
        return False
    
    def _analyze_syntax_issues(self) -> List[EnhancedIssue]:
        """Detect and classify syntax issues with high precision"""
        issues = []
        
        for py_file in self.repo_path.rglob("*.py"):
            if self._should_skip_file(py_file):
                continue
                
            try:
                content = py_file.read_text(encoding='utf-8')
                # Try to parse - if it fails, it's a syntax issue
                ast.parse(content, filename=str(py_file))
                
                # Additional syntax checks
                issues.extend(self._check_advanced_syntax_issues(py_file, content))
                
            except SyntaxError as e:
                issue = EnhancedIssue(
                    id=f"syntax_{py_file.stem}_{e.lineno}",
                    category=IssueCategory.CRITICAL_SYNTAX,
                    severity=IssueSeverity.BLOCKER,
                    file_path=py_file,
                    line_number=e.lineno or 0,
                    column=e.offset,
                    description=f"Syntax error: {e.msg}",
                    context={'error_text': e.text, 'error_type': type(e).__name__},
                    suggested_fix=self._suggest_syntax_fix(e),
                    prevention_strategy="Use pre-commit hooks with syntax validation",
                    confidence=1.0
                )
                issues.append(issue)
        
        return issues
    
    def _analyze_import_issues(self) -> List[EnhancedIssue]:
        """Advanced import analysis with dependency tracking"""
        issues = []
        
        for py_file, tree in self.ast_cache.items():
            # Check for problematic import patterns
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    issue = self._analyze_import_node(node, py_file, tree)
                    if issue:
                        issues.append(issue)
        
        # Check for circular imports
        circular_imports = self._detect_circular_imports()
        for cycle in circular_imports:
            issue = EnhancedIssue(
                id=f"circular_import_{hash(tuple(cycle))}",
                category=IssueCategory.CRITICAL_IMPORT,
                severity=IssueSeverity.CRITICAL,
                file_path=Path(cycle[0]),
                line_number=1,
                description=f"Circular import detected: {' -> '.join(cycle)}",
                context={'cycle': cycle},
                suggested_fix="Refactor to eliminate circular dependency",
                prevention_strategy="Use import dependency analysis in CI/CD",
                confidence=0.9
            )
            issues.append(issue)
        
        return issues
    
    def _analyze_security_issues(self) -> List[EnhancedIssue]:
        """Enhanced security analysis with context awareness"""
        issues = []
        
        # Run bandit for baseline security analysis
        try:
            result = subprocess.run([
                'python3', '-m', 'bandit', '-r', str(self.repo_path),
                '-f', 'json', '--skip', 'B101'  # Skip assert usage
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                bandit_data = json.loads(result.stdout)
                for issue_data in bandit_data.get('results', []):
                    issue = self._create_security_issue(issue_data)
                    if issue:
                        issues.append(issue)
        
        except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
            self.logger.warning("⚠️ Could not run bandit security analysis")
        
        # Additional custom security checks
        issues.extend(self._custom_security_analysis())
        
        return issues
    
    def _analyze_logic_issues(self) -> List[EnhancedIssue]:
        """Detect logic issues and undefined functions with context"""
        issues = []
        
        for py_file, tree in self.ast_cache.items():
            # Find undefined function calls
            undefined_calls = self._find_undefined_calls(tree, py_file)
            for call in undefined_calls:
                issue = EnhancedIssue(
                    id=f"undefined_{py_file.stem}_{call['name']}_{call['line']}",
                    category=IssueCategory.HIGH_LOGIC,
                    severity=IssueSeverity.HIGH,
                    file_path=py_file,
                    line_number=call['line'],
                    description=f"Undefined function call: {call['name']}",
                    context=call,
                    suggested_fix=self._suggest_function_fix(call, py_file),
                    prevention_strategy="Use static analysis tools and type hints",
                    confidence=call.get('confidence', 0.8)
                )
                issues.append(issue)
        
        return issues
    
    def _analyze_quality_issues(self) -> List[EnhancedIssue]:
        """Quality analysis with intelligent prioritization"""
        issues = []
        
        # Code complexity analysis
        for py_file, tree in self.ast_cache.items():
            complexity_issues = self._analyze_complexity(tree, py_file)
            issues.extend(complexity_issues)
            
            # Duplicate code detection
            duplicate_issues = self._find_smart_duplicates(tree, py_file)
            issues.extend(duplicate_issues)
        
        return issues
    
    def _analyze_potential_regressions(self) -> List[EnhancedIssue]:
        """Detect patterns that could lead to future regressions"""
        issues = []
        
        # Analyze code patterns that commonly break
        for py_file, tree in self.ast_cache.items():
            # Check for fragile patterns
            fragile_patterns = self._detect_fragile_patterns(tree, py_file)
            issues.extend(fragile_patterns)
        
        return issues
    
    def _check_advanced_syntax_issues(self, py_file: Path, content: str) -> List[EnhancedIssue]:
        """Check for advanced syntax issues beyond basic parsing"""
        issues = []
        
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            # Check for common problematic patterns
            if re.search(r'\w+:\s*\d+[a-zA-Z]', line) and 'def ' not in line:
                # Potential template syntax issue
                issue = EnhancedIssue(
                    id=f"template_syntax_{py_file.stem}_{i}",
                    category=IssueCategory.CRITICAL_SYNTAX,
                    severity=IssueSeverity.HIGH,
                    file_path=py_file,
                    line_number=i,
                    description="Potential template syntax issue: unquoted value with units",
                    context={'line_content': line.strip()},
                    suggested_fix="Quote the value with units",
                    confidence=0.8
                )
                issues.append(issue)
        
        return issues
    
    def _analyze_import_node(self, node: Union[ast.Import, ast.ImportFrom], py_file: Path, tree: ast.AST) -> Optional[EnhancedIssue]:
        """Analyze a single import node for issues"""
        if isinstance(node, ast.ImportFrom) and node.module:
            # Check for hyphenated module names
            if '-' in node.module:
                return EnhancedIssue(
                    id=f"hyphen_import_{py_file.stem}_{node.lineno}",
                    category=IssueCategory.CRITICAL_IMPORT,
                    severity=IssueSeverity.CRITICAL,
                    file_path=py_file,
                    line_number=node.lineno,
                    description=f"Hyphenated module import: {node.module}",
                    context={'module': node.module, 'import_type': 'from_import'},
                    suggested_fix=f"Replace with: {node.module.replace('-', '_')}",
                    prevention_strategy="Use pre-commit hooks to validate module names",
                    confidence=1.0
                )
            
            # Check for imports from utils.functions
            if node.module == 'utils.functions':
                imported_names = [alias.name for alias in node.names]
                return EnhancedIssue(
                    id=f"utils_functions_import_{py_file.stem}_{node.lineno}",
                    category=IssueCategory.CRITICAL_IMPORT,
                    severity=IssueSeverity.HIGH,
                    file_path=py_file,
                    line_number=node.lineno,
                    description=f"Import from broken utils.functions: {imported_names}",
                    context={'imported_names': imported_names},
                    suggested_fix="Use standard library imports instead",
                    confidence=0.9
                )
        
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if '-' in alias.name:
                    return EnhancedIssue(
                        id=f"hyphen_import_{py_file.stem}_{node.lineno}",
                        category=IssueCategory.CRITICAL_IMPORT,
                        severity=IssueSeverity.CRITICAL,
                        file_path=py_file,
                        line_number=node.lineno,
                        description=f"Hyphenated module import: {alias.name}",
                        context={'module': alias.name, 'import_type': 'import'},
                        suggested_fix=f"Replace with: {alias.name.replace('-', '_')}",
                        confidence=1.0
                    )
        
        return None
    
    def _detect_circular_imports(self) -> List[List[str]]:
        """Detect circular imports using graph analysis"""
        # Simple circular import detection
        cycles = []
        
        # Build dependency graph
        graph = {}
        for file_path, imports in self.import_graph.items():
            graph[file_path] = []
            for imp in imports:
                if imp['type'] == 'from_import' and imp['module']:
                    # Try to resolve module to file path
                    potential_path = self._resolve_module_path(imp['module'])
                    if potential_path:
                        graph[file_path].append(str(potential_path))
        
        # Simple cycle detection (would need more sophisticated algorithm for production)
        visited = set()
        rec_stack = set()
        
        def has_cycle(node, path):
            if node in rec_stack:
                # Found cycle
                cycle_start = path.index(node)
                cycles.append(path[cycle_start:] + [node])
                return True
            
            if node in visited:
                return False
            
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in graph.get(node, []):
                if has_cycle(neighbor, path + [node]):
                    return True
            
            rec_stack.remove(node)
            return False
        
        for node in graph:
            if node not in visited:
                has_cycle(node, [])
        
        return cycles
    
    def _resolve_module_path(self, module_name: str) -> Optional[Path]:
        """Resolve module name to file path"""
        # Simple resolution - could be enhanced
        parts = module_name.split('.')
        
        # Check in repo
        potential_path = self.repo_path
        for part in parts:
            potential_path = potential_path / part
        
        if (potential_path.with_suffix('.py')).exists():
            return potential_path.with_suffix('.py')
        
        if (potential_path / '__init__.py').exists():
            return potential_path / '__init__.py'
        
        return None
    
    def _create_security_issue(self, bandit_data: Dict[str, Any]) -> Optional[EnhancedIssue]:
        """Create security issue from bandit data"""
        try:
            return EnhancedIssue(
                id=f"security_{bandit_data.get('test_id', 'unknown')}_{bandit_data.get('line_number', 0)}",
                category=IssueCategory.CRITICAL_SECURITY,
                severity=self._map_bandit_severity(bandit_data.get('issue_severity', 'MEDIUM')),
                file_path=Path(bandit_data.get('filename', '')),
                line_number=bandit_data.get('line_number', 0),
                description=bandit_data.get('issue_text', 'Security vulnerability'),
                context=bandit_data,
                suggested_fix=self._suggest_security_fix(bandit_data),
                prevention_strategy="Use security linting in CI/CD pipeline",
                confidence=self._parse_confidence(bandit_data.get('issue_confidence', 'MEDIUM'))
            )
        except Exception:
            return None
    
    def _parse_confidence(self, confidence_str: str) -> float:
        """Parse confidence string to float"""
        if not confidence_str:
            return 0.5
        
        confidence_map = {
            'high': 0.9,
            'medium': 0.7,
            'low': 0.5
        }
        
        return confidence_map.get(confidence_str.lower(), 0.5)
    
    def _map_bandit_severity(self, bandit_severity: str) -> IssueSeverity:
        """Map bandit severity to our severity enum"""
        mapping = {
            'HIGH': IssueSeverity.CRITICAL,
            'MEDIUM': IssueSeverity.HIGH,
            'LOW': IssueSeverity.MEDIUM
        }
        return mapping.get(bandit_severity.upper(), IssueSeverity.MEDIUM)
    
    def _suggest_security_fix(self, bandit_data: Dict[str, Any]) -> str:
        """Suggest fix for security issue"""
        test_id = bandit_data.get('test_id', '')
        
        suggestions = {
            'B602': 'Use shell=False and pass command as list',
            'B506': 'Use yaml.safe_load() instead of yaml.load()',
            'B105': 'Move password to environment variable',
            'B101': 'Remove assert statements or use proper validation'
        }
        
        return suggestions.get(test_id, 'Review security documentation for this issue type')
    
    def _custom_security_analysis(self) -> List[EnhancedIssue]:
        """Custom security analysis beyond bandit"""
        issues = []
        
        for py_file, tree in self.ast_cache.items():
            # Check for potential password patterns
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and 'password' in target.id.lower():
                            if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                                issue = EnhancedIssue(
                                    id=f"hardcoded_password_{py_file.stem}_{node.lineno}",
                                    category=IssueCategory.CRITICAL_SECURITY,
                                    severity=IssueSeverity.CRITICAL,
                                    file_path=py_file,
                                    line_number=node.lineno,
                                    description="Hardcoded password detected",
                                    context={'variable_name': target.id},
                                    suggested_fix="Use environment variable or secure configuration",
                                    confidence=0.8
                                )
                                issues.append(issue)
        
        return issues
    
    def _find_undefined_calls(self, tree: ast.AST, py_file: Path) -> List[Dict[str, Any]]:
        """Find undefined function calls"""
        undefined_calls = []
        
        # Get all function calls
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func_name = None
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    func_name = node.func.attr
                
                if func_name and not self._is_function_defined(func_name, py_file):
                    undefined_calls.append({
                        'name': func_name,
                        'line': node.lineno,
                        'confidence': 0.7,
                        'context': 'function_call'
                    })
        
        return undefined_calls
    
    def _is_function_defined(self, func_name: str, py_file: Path) -> bool:
        """Check if function is defined (simplified version)"""
        # Check built-ins
        builtins = ['print', 'len', 'str', 'int', 'float', 'list', 'dict', 'open', 'range']
        if func_name in builtins:
            return True
        
        # Check in current file
        file_functions = self.function_registry.get(str(py_file), [])
        if any(f['name'] == func_name for f in file_functions):
            return True
        
        # Check imports (simplified)
        imports = self.import_graph.get(str(py_file), [])
        for imp in imports:
            if func_name in imp['name']:
                return True
        
        return False
    
    def _suggest_function_fix(self, call: Dict[str, Any], py_file: Path) -> str:
        """Suggest fix for undefined function call"""
        func_name = call['name']
        
        # Common suggestions
        if func_name.lower() in ['path', 'pathlib']:
            return "Add: from pathlib import Path"
        elif func_name in ['json', 'os', 'sys', 'time']:
            return f"Add: import {func_name}"
        elif func_name in ['Any', 'Dict', 'List', 'Optional']:
            return f"Add: from typing import {func_name}"
        
        return f"Define function {func_name} or add appropriate import"
    
    def _analyze_complexity(self, tree: ast.AST, py_file: Path) -> List[EnhancedIssue]:
        """Analyze code complexity"""
        issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Simple complexity metric
                complexity = self._calculate_complexity(node)
                if complexity > 10:  # Threshold
                    issue = EnhancedIssue(
                        id=f"complexity_{py_file.stem}_{node.name}_{node.lineno}",
                        category=IssueCategory.HIGH_QUALITY,
                        severity=IssueSeverity.MEDIUM,
                        file_path=py_file,
                        line_number=node.lineno,
                        description=f"High complexity function: {node.name} (complexity: {complexity})",
                        context={'function_name': node.name, 'complexity': complexity},
                        suggested_fix="Consider breaking into smaller functions",
                        confidence=0.8
                    )
                    issues.append(issue)
        
        return issues
    
    def _calculate_complexity(self, func_node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity (simplified)"""
        complexity = 1  # Base complexity
        
        for node in ast.walk(func_node):
            if isinstance(node, (ast.If, ast.While, ast.For)):
                complexity += 1
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1
        
        return complexity
    
    def _find_smart_duplicates(self, tree: ast.AST, py_file: Path) -> List[EnhancedIssue]:
        """Find duplicate code with intelligent analysis"""
        issues = []
        
        # This would be enhanced with AST fingerprinting
        # For now, simple function name checking
        functions = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
        func_names = [f.name for f in functions]
        
        # Check for duplicate function names (simple check)
        seen = set()
        for func in functions:
            if func.name in seen and func.name != '__init__':
                issue = EnhancedIssue(
                    id=f"duplicate_func_{py_file.stem}_{func.name}_{func.lineno}",
                    category=IssueCategory.HIGH_QUALITY,
                    severity=IssueSeverity.MEDIUM,
                    file_path=py_file,
                    line_number=func.lineno,
                    description=f"Duplicate function name: {func.name}",
                    context={'function_name': func.name},
                    suggested_fix="Rename function or consolidate implementations",
                    confidence=0.6
                )
                issues.append(issue)
            seen.add(func.name)
        
        return issues
    
    def _detect_fragile_patterns(self, tree: ast.AST, py_file: Path) -> List[EnhancedIssue]:
        """Detect patterns that commonly lead to regressions"""
        issues = []
        
        for node in ast.walk(tree):
            # Check for bare except clauses
            if isinstance(node, ast.ExceptHandler) and node.type is None:
                issue = EnhancedIssue(
                    id=f"bare_except_{py_file.stem}_{node.lineno}",
                    category=IssueCategory.PREVENTABLE_REGRESSION,
                    severity=IssueSeverity.MEDIUM,
                    file_path=py_file,
                    line_number=node.lineno,
                    description="Bare except clause can hide errors",
                    context={'type': 'bare_except'},
                    suggested_fix="Specify exception types to catch",
                    prevention_strategy="Use specific exception handling",
                    confidence=0.9
                )
                issues.append(issue)
        
        return issues
    
    def _enhance_issues_with_impact_analysis(self, issues: List[EnhancedIssue]):
        """Enhance issues with dependency and impact analysis"""
        for issue in issues:
            # Add dependency information
            issue.dependencies = self._find_issue_dependencies(issue)
            
            # Add impact scope
            issue.impact_scope = self._calculate_impact_scope(issue)
    
    def _find_issue_dependencies(self, issue: EnhancedIssue) -> Set[str]:
        """Find dependencies for an issue"""
        dependencies = set()
        
        if issue.category == IssueCategory.CRITICAL_IMPORT:
            # Import issues may affect other files
            file_imports = self.import_graph.get(str(issue.file_path), [])
            for imp in file_imports:
                if issue.context.get('module') in imp.get('module', ''):
                    dependencies.add(f"import_{imp['module']}")
        
        return dependencies
    
    def _calculate_impact_scope(self, issue: EnhancedIssue) -> Set[Path]:
        """Calculate which files might be impacted by this issue"""
        impact_scope = {issue.file_path}
        
        if issue.category in [IssueCategory.CRITICAL_IMPORT, IssueCategory.CRITICAL_SYNTAX]:
            # Check which files import this one
            issue_file_str = str(issue.file_path)
            for file_path, imports in self.import_graph.items():
                for imp in imports:
                    if issue_file_str in imp.get('module', ''):
                        impact_scope.add(Path(file_path))
        
        return impact_scope
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """Determine if file should be skipped in analysis"""
        skip_patterns = [
            '.git', '__pycache__', '.pytest_cache', 'node_modules',
            '.autofix_backups', 'backups', '.tmp', 'venv', '.venv'
        ]
        
        return any(pattern in str(file_path) for pattern in skip_patterns)
    
    def _suggest_syntax_fix(self, syntax_error: SyntaxError) -> Optional[str]:
        """Suggest fixes for common syntax errors"""
        error_msg = syntax_error.msg.lower()
        
        if 'invalid decimal literal' in error_msg:
            return "Quote the value in string literals (e.g., '10s' instead of 10s)"
        elif 'invalid syntax' in error_msg and syntax_error.text:
            if '-' in syntax_error.text and 'import' in syntax_error.text:
                return "Replace hyphens with underscores in module names"
        
        return "Fix syntax error according to Python grammar rules"


class IntegratedWatchdog:
    """Integrated watchdog system for proactive issue prevention"""
    
    def __init__(self, repo_path: Path, autofix_engine: 'EnhancedAutofixEngine'):
        self.repo_path = repo_path
        self.autofix_engine = autofix_engine
        self.logger = logging.getLogger(__name__)
        self.observer = None
        self.is_monitoring = False
        self.prevention_rules = self._load_prevention_rules()
        
    def start_monitoring(self):
        """Start proactive file system monitoring"""
        if not WATCHDOG_AVAILABLE:
            self.logger.warning("⚠️ Watchdog not available - monitoring disabled")
            return
        
        self.logger.info("👁️ Starting integrated watchdog monitoring...")
        
        self.observer = Observer()
        event_handler = AutofixWatchdogHandler(self)
        self.observer.schedule(event_handler, str(self.repo_path), recursive=True)
        
        self.observer.start()
        self.is_monitoring = True
        self.logger.info("✅ Watchdog monitoring active")
    
    def stop_monitoring(self):
        """Stop monitoring"""
        if self.observer and self.is_monitoring:
            self.observer.stop()
            self.observer.join()
            self.is_monitoring = False
            self.logger.info("🛑 Watchdog monitoring stopped")
    
    def _load_prevention_rules(self) -> Dict[str, Any]:
        """Load prevention rules configuration"""
        rules_file = self.repo_path / "configs" / "prevention_rules.json"
        
        default_rules = {
            "auto_fix_on_save": True,
            "prevent_syntax_errors": True,
            "prevent_import_errors": True,
            "prevent_security_issues": True,
            "immediate_validation": True,
            "rollback_on_failure": True,
            "file_patterns": {
                "python": ["*.py"],
                "config": ["*.json", "*.yaml", "*.yml"],
                "docs": ["*.md", "*.txt"]
            },
            "exclude_patterns": [
                ".git/*", "__pycache__/*", "*.pyc", ".tmp/*"
            ]
        }
        
        if rules_file.exists():
            try:
                with open(rules_file, 'r') as f:
                    user_rules = json.load(f)
                    default_rules.update(user_rules)
            except Exception as e:
                self.logger.warning(f"⚠️ Could not load prevention rules: {e}")
        
        return default_rules
    
    def handle_file_change(self, file_path: Path, event_type: str):
        """Handle file change events with immediate prevention"""
        if not self._should_monitor_file(file_path):
            return
        
        self.logger.debug(f"📝 File {event_type}: {file_path}")
        
        if self.prevention_rules.get("immediate_validation", True):
            # Immediate validation and fixing
            threading.Thread(
                target=self._immediate_validation,
                args=(file_path,),
                daemon=True
            ).start()
    
    def _immediate_validation(self, file_path: Path):
        """Perform immediate validation and fixing"""
        try:
            # Quick syntax check for Python files
            if file_path.suffix == '.py':
                content = file_path.read_text(encoding='utf-8')
                
                try:
                    ast.parse(content, filename=str(file_path))
                except SyntaxError as e:
                    self.logger.warning(f"⚠️ Syntax error detected in {file_path}: {e}")
                    
                    if self.prevention_rules.get("auto_fix_on_save", True):
                        # Attempt immediate fix
                        self.autofix_engine.fix_file_immediately(file_path, e)
            
            # Validate imports
            if self.prevention_rules.get("prevent_import_errors", True):
                self._validate_imports(file_path)
        
        except Exception as e:
            self.logger.error(f"❌ Error in immediate validation: {e}")
    
    def _should_monitor_file(self, file_path: Path) -> bool:
        """Determine if file should be monitored"""
        file_str = str(file_path)
        
        # Check exclude patterns
        for pattern in self.prevention_rules.get("exclude_patterns", []):
            if pattern.replace('*', '') in file_str:
                return False
        
        # Check include patterns
        include_patterns = []
        for patterns in self.prevention_rules.get("file_patterns", {}).values():
            include_patterns.extend(patterns)
        
        if include_patterns:
            return any(file_path.match(pattern) for pattern in include_patterns)
        
        return True
    
    def _validate_imports(self, file_path: Path):
        """Validate imports in the file"""
        if file_path.suffix != '.py':
            return
        
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content, filename=str(file_path))
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    if node.module and '-' in node.module:
                        self.logger.warning(f"⚠️ Hyphenated import detected: {node.module}")
                        
                        if self.prevention_rules.get("auto_fix_on_save", True):
                            # Fix hyphenated import
                            fixed_module = node.module.replace('-', '_')
                            new_content = content.replace(
                                f"from {node.module}",
                                f"from {fixed_module}"
                            )
                            file_path.write_text(new_content, encoding='utf-8')
                            self.logger.info(f"✅ Fixed hyphenated import: {node.module} -> {fixed_module}")
        
        except Exception as e:
            self.logger.error(f"❌ Error validating imports in {file_path}: {e}")


class AutofixWatchdogHandler(FileSystemEventHandler):
    """File system event handler for autofix integration"""
    
    def __init__(self, watchdog: IntegratedWatchdog):
        super().__init__()
        self.watchdog = watchdog
    
    def on_modified(self, event):
        if not event.is_directory:
            self.watchdog.handle_file_change(Path(event.src_path), "modified")
    
    def on_created(self, event):
        if not event.is_directory:
            self.watchdog.handle_file_change(Path(event.src_path), "created")


class SelfHealingSystem:
    """Self-healing system that learns from fixes and prevents regressions"""
    
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.logger = logging.getLogger(__name__)
        self.healing_history = self._load_healing_history()
        self.pattern_database = self._load_pattern_database()
    
    def learn_from_fix(self, issue: EnhancedIssue, fix_result: Dict[str, Any]):
        """Learn from a successful fix to prevent similar issues"""
        pattern = self._extract_pattern(issue, fix_result)
        
        if pattern:
            self.pattern_database[pattern['signature']] = pattern
            self._save_pattern_database()
            self.logger.info(f"🧠 Learned new pattern: {pattern['signature']}")
    
    def predict_issues(self, file_path: Path) -> List[EnhancedIssue]:
        """Predict potential issues based on learned patterns"""
        predicted_issues = []
        
        try:
            content = file_path.read_text(encoding='utf-8')
            
            for signature, pattern in self.pattern_database.items():
                if self._matches_pattern(content, pattern):
                    issue = EnhancedIssue(
                        id=f"predicted_{file_path.stem}_{signature}",
                        category=IssueCategory.PREVENTABLE_REGRESSION,
                        severity=IssueSeverity.MEDIUM,
                        file_path=file_path,
                        line_number=pattern.get('typical_line', 1),
                        description=f"Predicted issue based on pattern: {pattern['description']}",
                        context=pattern,
                        suggested_fix=pattern.get('prevention_fix'),
                        prevention_strategy=pattern.get('prevention_strategy'),
                        confidence=pattern.get('confidence', 0.7)
                    )
                    predicted_issues.append(issue)
        
        except Exception as e:
            self.logger.error(f"❌ Error predicting issues for {file_path}: {e}")
        
        return predicted_issues
    
    def _load_healing_history(self) -> Dict[str, Any]:
        """Load healing history from disk"""
        history_file = self.repo_path / ".autofix" / "healing_history.json"
        
        if history_file.exists():
            try:
                with open(history_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        
        return {"fixes": [], "patterns": {}, "statistics": {}}
    
    def _load_pattern_database(self) -> Dict[str, Any]:
        """Load pattern database"""
        pattern_file = self.repo_path / ".autofix" / "patterns.json"
        
        if pattern_file.exists():
            try:
                with open(pattern_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        
        return {}
    
    def _save_pattern_database(self):
        """Save pattern database to disk"""
        pattern_file = self.repo_path / ".autofix" / "patterns.json"
        pattern_file.parent.mkdir(exist_ok=True)
        
        with open(pattern_file, 'w') as f:
            json.dump(self.pattern_database, f, indent=2)
    
    def _extract_pattern(self, issue: EnhancedIssue, fix_result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract a pattern from a successful fix"""
        if not fix_result.get('success', False):
            return None
        
        return {
            'signature': f"{issue.category.value}_{issue.description[:50]}",
            'description': issue.description,
            'fix_type': fix_result.get('fix_type'),
            'prevention_fix': fix_result.get('prevention_fix'),
            'prevention_strategy': issue.prevention_strategy,
            'confidence': issue.confidence,
            'typical_line': issue.line_number,
            'context_pattern': self._generalize_context(issue.context)
        }
    
    def _matches_pattern(self, content: str, pattern: Dict[str, Any]) -> bool:
        """Check if content matches a learned pattern"""
        # Simple pattern matching - can be enhanced with ML
        context_pattern = pattern.get('context_pattern', {})
        
        if 'error_keywords' in context_pattern:
            return any(keyword in content for keyword in context_pattern['error_keywords'])
        
        return False
    
    def _generalize_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generalize context for pattern matching"""
        generalized = {}
        
        if 'error_text' in context:
            # Extract keywords from error text
            error_keywords = re.findall(r'\b\w+\b', context['error_text'].lower())
            generalized['error_keywords'] = error_keywords[:5]  # Keep top 5 keywords
        
        return generalized


class EnhancedAutofixEngine:
    """Main enhanced autofix engine coordinating all components"""
    
    def __init__(self, repo_path: Path, config_file: Optional[Path] = None):
        self.repo_path = repo_path
        self.logger = self._setup_logging()
        self.config = self._load_config(config_file)
        
        # Initialize components
        self.analyzer = HighResolutionAnalyzer(repo_path)
        self.watchdog = IntegratedWatchdog(repo_path, self)
        self.self_healing = SelfHealingSystem(repo_path)
        
        # Legacy component integration (with fallbacks)
        self.quality_patcher = None
        self.version_keeper = None
        
        if EnhancedClaudeQualityPatcher:
            try:
                self.quality_patcher = EnhancedClaudeQualityPatcher(repo_path)
            except Exception as e:
                self.logger.warning(f"Could not initialize quality patcher: {e}")
        
        if MCPVersionKeeper:
            try:
                self.version_keeper = MCPVersionKeeper(repo_path)
            except Exception as e:
                self.logger.warning(f"Could not initialize version keeper: {e}")
        
        # Statistics
        self.session_stats = {
            'issues_detected': 0,
            'issues_fixed': 0,
            'issues_prevented': 0,
            'patterns_learned': 0,
            'start_time': datetime.now()
        }
    
    async def run_enhanced_autofix(self, enable_monitoring: bool = True) -> Dict[str, Any]:
        """Run the complete enhanced autofix system"""
        self.logger.info("🚀 Starting Enhanced Autofix Engine v3.0")
        
        try:
            # Phase 1: High-resolution analysis
            self.logger.info("🔬 Phase 1: High-resolution analysis")
            issues = self.analyzer.analyze_codebase()
            self.session_stats['issues_detected'] = len(issues)
            
            # Phase 2: Immediate critical fixes
            self.logger.info("🚨 Phase 2: Critical issue resolution")
            critical_fixes = await self._fix_critical_issues(issues)
            
            # Phase 3: Start monitoring for prevention
            if enable_monitoring:
                self.logger.info("👁️ Phase 3: Starting preventive monitoring")
                self.watchdog.start_monitoring()
            
            # Phase 4: Quality improvements
            self.logger.info("🎯 Phase 4: Quality improvements")
            quality_fixes = await self._fix_quality_issues(issues)
            
            # Phase 5: Learn from fixes
            self.logger.info("🧠 Phase 5: Learning from fixes")
            await self._learn_from_session(issues, critical_fixes + quality_fixes)
            
            # Generate comprehensive report
            report = self._generate_enhanced_report(issues, critical_fixes + quality_fixes)
            
            self.logger.info("✅ Enhanced autofix session completed")
            return report
        
        except Exception as e:
            self.logger.error(f"❌ Enhanced autofix failed: {e}")
            raise
    
    async def _fix_critical_issues(self, issues: List[EnhancedIssue]) -> List[Dict[str, Any]]:
        """Fix critical issues that prevent execution"""
        critical_issues = [
            i for i in issues 
            if i.severity in [IssueSeverity.BLOCKER, IssueSeverity.CRITICAL]
        ]
        
        fixes = []
        
        for issue in critical_issues:
            self.logger.info(f"🔧 Fixing critical issue: {issue.description}")
            
            fix_result = await self._apply_fix(issue)
            if fix_result['success']:
                self.session_stats['issues_fixed'] += 1
                self.self_healing.learn_from_fix(issue, fix_result)
            
            fixes.append(fix_result)
        
        return fixes
    
    async def _fix_quality_issues(self, issues: List[EnhancedIssue]) -> List[Dict[str, Any]]:
        """Fix quality and style issues"""
        quality_issues = [
            i for i in issues 
            if i.severity in [IssueSeverity.HIGH, IssueSeverity.MEDIUM]
        ]
        
        fixes = []
        
        # Use existing quality patcher for compatibility (if available)
        if self.quality_patcher:
            try:
                quality_patcher_result = self.quality_patcher.run_batch_fixes(max_fixes=10)
                self.logger.info("✅ Quality patcher integration completed")
            except Exception as e:
                self.logger.warning(f"Quality patcher failed: {e}")
        
        # Process remaining quality issues
        for issue in quality_issues[:self.config.get('max_quality_fixes', 20)]:
            fix_result = await self._apply_fix(issue)
            if fix_result['success']:
                self.session_stats['issues_fixed'] += 1
            
            fixes.append(fix_result)
        
        return fixes
    
    async def _apply_fix(self, issue: EnhancedIssue) -> Dict[str, Any]:
        """Apply a fix for a specific issue"""
        try:
            # Determine fix strategy based on issue type
            if issue.category == IssueCategory.CRITICAL_SYNTAX:
                return await self._fix_syntax_issue(issue)
            elif issue.category == IssueCategory.CRITICAL_IMPORT:
                return await self._fix_import_issue(issue)
            elif issue.category == IssueCategory.CRITICAL_SECURITY:
                return await self._fix_security_issue(issue)
            else:
                return await self._fix_generic_issue(issue)
        
        except Exception as e:
            return {
                'success': False,
                'issue_id': issue.id,
                'error': str(e),
                'fix_type': 'failed'
            }
    
    async def _fix_syntax_issue(self, issue: EnhancedIssue) -> Dict[str, Any]:
        """Fix syntax issues"""
        if 'invalid decimal literal' in issue.description:
            # Fix template syntax issues
            content = issue.file_path.read_text(encoding='utf-8')
            
            # Quote numeric values with units
            fixed_content = re.sub(r'(\w+):\s*(\d+)s', r'\1: "\2s"', content)
            
            if fixed_content != content:
                issue.file_path.write_text(fixed_content, encoding='utf-8')
                return {
                    'success': True,
                    'issue_id': issue.id,
                    'fix_type': 'template_syntax',
                    'description': 'Fixed template syntax by quoting values'
                }
        
        return {'success': False, 'issue_id': issue.id, 'fix_type': 'syntax', 'error': 'No fix strategy available'}
    
    async def _fix_import_issue(self, issue: EnhancedIssue) -> Dict[str, Any]:
        """Fix import issues"""
        if 'hyphen' in issue.description.lower():
            # Fix hyphenated imports
            content = issue.file_path.read_text(encoding='utf-8')
            
            # Replace hyphenated module names
            import_fixes = {
                'mcp-': 'mcp_',
                'claude-': 'claude_',
                'auto-discovery': 'auto_discovery'
            }
            
            fixed_content = content
            for old, new in import_fixes.items():
                fixed_content = fixed_content.replace(old, new)
            
            if fixed_content != content:
                issue.file_path.write_text(fixed_content, encoding='utf-8')
                return {
                    'success': True,
                    'issue_id': issue.id,
                    'fix_type': 'import_hyphen',
                    'description': 'Fixed hyphenated module names'
                }
        
        return {'success': False, 'issue_id': issue.id, 'fix_type': 'import', 'error': 'No fix strategy available'}
    
    async def _fix_security_issue(self, issue: EnhancedIssue) -> Dict[str, Any]:
        """Fix security issues"""
        # Delegate to existing security fixing logic in autofix.py
        return {'success': False, 'issue_id': issue.id, 'fix_type': 'security', 'error': 'Delegated to main autofix'}
    
    async def _fix_generic_issue(self, issue: EnhancedIssue) -> Dict[str, Any]:
        """Fix generic issues"""
        return {'success': False, 'issue_id': issue.id, 'fix_type': 'generic', 'error': 'No specific fix strategy'}
    
    def fix_file_immediately(self, file_path: Path, error: Exception):
        """Fix a file immediately when error is detected"""
        self.logger.info(f"🚨 Immediate fix needed for {file_path}: {error}")
        
        # Quick fixes for common issues
        if isinstance(error, SyntaxError):
            if 'invalid decimal literal' in str(error):
                self._quick_fix_template_syntax(file_path)
            elif 'invalid syntax' in str(error) and '-' in str(error):
                self._quick_fix_hyphenated_imports(file_path)
    
    def _quick_fix_template_syntax(self, file_path: Path):
        """Quick fix for template syntax issues"""
        try:
            content = file_path.read_text(encoding='utf-8')
            fixed_content = re.sub(r'(\w+):\s*(\d+)s', r'\1: "\2s"', content)
            
            if fixed_content != content:
                file_path.write_text(fixed_content, encoding='utf-8')
                self.logger.info(f"✅ Quick-fixed template syntax in {file_path}")
                self.session_stats['issues_prevented'] += 1
        
        except Exception as e:
            self.logger.error(f"❌ Quick fix failed for {file_path}: {e}")
    
    def _quick_fix_hyphenated_imports(self, file_path: Path):
        """Quick fix for hyphenated import issues"""
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Common hyphenated module fixes
            fixes = [
                ('from mcp-', 'from mcp_'),
                ('import mcp-', 'import mcp_'),
                ('from claude-', 'from claude_'),
                ('import claude-', 'import claude_'),
                ('from auto-discovery', 'from auto_discovery'),
                ('import auto-discovery', 'import auto_discovery')
            ]
            
            fixed_content = content
            for old, new in fixes:
                fixed_content = fixed_content.replace(old, new)
            
            if fixed_content != content:
                file_path.write_text(fixed_content, encoding='utf-8')
                self.logger.info(f"✅ Quick-fixed hyphenated imports in {file_path}")
                self.session_stats['issues_prevented'] += 1
        
        except Exception as e:
            self.logger.error(f"❌ Quick fix failed for {file_path}: {e}")
    
    async def _learn_from_session(self, issues: List[EnhancedIssue], fixes: List[Dict[str, Any]]):
        """Learn from the current session"""
        successful_fixes = [f for f in fixes if f.get('success', False)]
        
        for issue in issues:
            # Find corresponding fix
            fix = next((f for f in successful_fixes if f.get('issue_id') == issue.id), None)
            if fix:
                self.self_healing.learn_from_fix(issue, fix)
                self.session_stats['patterns_learned'] += 1
    
    def _generate_enhanced_report(self, issues: List[EnhancedIssue], fixes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive report"""
        return {
            'session_info': {
                'timestamp': datetime.now().isoformat(),
                'duration_seconds': (datetime.now() - self.session_stats['start_time']).total_seconds(),
                'version': '3.0',
                'repo_path': str(self.repo_path)
            },
            'statistics': self.session_stats,
            'issues_summary': {
                'total_detected': len(issues),
                'by_category': self._group_issues_by_category(issues),
                'by_severity': self._group_issues_by_severity(issues)
            },
            'fixes_summary': {
                'total_attempted': len(fixes),
                'successful': len([f for f in fixes if f.get('success', False)]),
                'failed': len([f for f in fixes if not f.get('success', False)])
            },
            'issues': [issue.to_dict() for issue in issues],
            'fixes': fixes,
            'recommendations': self._generate_recommendations(issues, fixes)
        }
    
    def _group_issues_by_category(self, issues: List[EnhancedIssue]) -> Dict[str, int]:
        """Group issues by category"""
        categories = {}
        for issue in issues:
            categories[issue.category.value] = categories.get(issue.category.value, 0) + 1
        return categories
    
    def _group_issues_by_severity(self, issues: List[EnhancedIssue]) -> Dict[str, int]:
        """Group issues by severity"""
        severities = {}
        for issue in issues:
            severities[issue.severity.name] = severities.get(issue.severity.name, 0) + 1
        return severities
    
    def _generate_recommendations(self, issues: List[EnhancedIssue], fixes: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations for preventing future issues"""
        recommendations = []
        
        # Analyze patterns in unfixed issues
        unfixed_categories = set()
        for issue in issues:
            fix = next((f for f in fixes if f.get('issue_id') == issue.id and f.get('success')), None)
            if not fix:
                unfixed_categories.add(issue.category)
        
        if IssueCategory.CRITICAL_SYNTAX in unfixed_categories:
            recommendations.append("Consider adding pre-commit hooks with syntax validation")
        
        if IssueCategory.CRITICAL_IMPORT in unfixed_categories:
            recommendations.append("Add import linting to CI/CD pipeline")
        
        if IssueCategory.CRITICAL_SECURITY in unfixed_categories:
            recommendations.append("Integrate security scanning tools into development workflow")
        
        return recommendations
    
    def _setup_logging(self) -> logging.Logger:
        """Setup enhanced logging"""
        logger = logging.getLogger(__name__)
        
        if not logger.handlers:
            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            # File handler
            log_file = self.repo_path / ".autofix" / "enhanced_autofix.log"
            log_file.parent.mkdir(exist_ok=True)
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            
            # Formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(formatter)
            file_handler.setFormatter(formatter)
            
            logger.addHandler(console_handler)
            logger.addHandler(file_handler)
            logger.setLevel(logging.DEBUG)
        
        return logger
    
    def _load_config(self, config_file: Optional[Path]) -> Dict[str, Any]:
        """Load configuration"""
        default_config = {
            'max_quality_fixes': 20,
            'enable_watchdog': True,
            'enable_learning': True,
            'auto_fix_on_save': True,
            'immediate_validation': True
        }
        
        if config_file and config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                self.logger.warning(f"⚠️ Could not load config file: {e}")
        
        return default_config
    
    def shutdown(self):
        """Clean shutdown"""
        self.watchdog.stop_monitoring()
        self.logger.info("🔄 Enhanced autofix engine shutdown complete")


# CLI Interface
async def main():
    """Main CLI interface for enhanced autofix engine"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Enhanced Autofix Engine v3.0")
    parser.add_argument("--repo-path", type=Path, default=Path.cwd(), help="Repository path")
    parser.add_argument("--config", type=Path, help="Configuration file path")
    parser.add_argument("--no-monitoring", action="store_true", help="Disable file monitoring")
    parser.add_argument("--output", type=Path, help="Output report file")
    
    args = parser.parse_args()
    
    # Initialize and run
    engine = EnhancedAutofixEngine(args.repo_path, args.config)
    
    try:
        report = await engine.run_enhanced_autofix(enable_monitoring=not args.no_monitoring)
        
        # Save report
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"📊 Report saved to {args.output}")
        
        # Print summary
        stats = report['statistics']
        print(f"\n✅ Enhanced Autofix Complete:")
        print(f"   Issues detected: {stats['issues_detected']}")
        print(f"   Issues fixed: {stats['issues_fixed']}")
        print(f"   Issues prevented: {stats['issues_prevented']}")
        print(f"   Patterns learned: {stats['patterns_learned']}")
        
    except KeyboardInterrupt:
        print("\n🛑 Autofix interrupted by user")
    finally:
        engine.shutdown()


if __name__ == "__main__":
    asyncio.run(main())