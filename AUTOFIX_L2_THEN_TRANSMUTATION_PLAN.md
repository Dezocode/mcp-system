# Autofix Enhancement Roadmap: L2 First, Then Transmutation
## Complete Implementation Strategy for 40.1% → 95% Automation

**Document Version**: 1.0  
**Created**: 2025-08-29  
**Current State**: 40.1% automation (PR #48 merged)  
**Target**: 95% automation through phased approach  

---

## 📊 EXECUTIVE SUMMARY

This document outlines the complete roadmap for enhancing autofix from 40.1% to 95% automation through a two-phase approach:

1. **Phase 1 (Level 2)**: Direct implementation enhancements (40.1% → 75-80%)
2. **Phase 2 (Transmutation)**: Agent-mediated self-enhancement (75-80% → 95%)

**CRITICAL**: Phase 1 MUST be completed before Phase 2 can begin.

---

# PHASE 1: LEVEL 2 ENHANCEMENTS (IMMEDIATE PRIORITY)

## 🎯 Level 2 Targets: 40.1% → 75-80% Automation

### **Current Remaining Issues (1,213 of 2,030)**
- Template variables: ~600-750 issues (49-62%)
- Orphaned methods: ~375-450 issues (31-37%)
- Dynamic patterns: ~150-225 issues (12-19%)
- Cross-file dependencies: ~88-138 issues (7-11%)

---

## 🔧 LEVEL 2 IMPLEMENTATION DETAILS

### **1. Enhanced Template Context Detection**
**Target Impact**: +600-750 fixes (15-20% improvement)

#### **Implementation in scripts/autofix.py:**
```python
class EnhancedTemplateDetector:
    """Template variable detection to reduce false positives"""
    
    def __init__(self):
        self.template_engines = {
            'jinja2': {
                'markers': [r'\{\{', r'\}\}', r'\{%', r'%\}', r'\{#', r'#\}'],
                'extensions': ['.j2', '.jinja', '.jinja2', '.html.j2'],
                'keywords': ['render', 'template', 'context', 'environment']
            },
            'django': {
                'markers': [r'\{\{', r'\}\}', r'\{%', r'%\}', r'\{#', r'#\}'],
                'extensions': ['.html', '.txt', '.xml'],
                'keywords': ['render', 'RequestContext', 'loader', 'template']
            },
            'python': {
                'markers': [r'f["\'].*\{.*\}', r'\.format\(', r'%\s*\('],
                'extensions': ['.py'],
                'keywords': ['format', 'f-string', 'interpolate']
            }
        }
        self.confidence_threshold = 0.85
        self.context_radius = 5  # Lines to check around target
        
    def detect_template_context(self, file_path: Path, line_num: int, code: str) -> Dict:
        """
        Determine if an undefined function is actually a template variable.
        Returns confidence score and template type if detected.
        """
        result = {
            'is_template': False,
            'confidence': 0.0,
            'template_type': None,
            'evidence': []
        }
        
        # Priority 1: File extension analysis
        file_ext = file_path.suffix.lower()
        for engine, config in self.template_engines.items():
            if file_ext in config['extensions']:
                result['confidence'] += 0.3
                result['evidence'].append(f"File extension {file_ext} suggests {engine}")
                result['template_type'] = engine
        
        # Priority 2: Template marker detection in surrounding context
        context_lines = self._get_context(file_path, line_num, self.context_radius)
        for engine, config in self.template_engines.items():
            marker_count = sum(
                1 for marker in config['markers'] 
                for line in context_lines 
                if re.search(marker, line)
            )
            if marker_count > 0:
                result['confidence'] += min(0.4, marker_count * 0.1)
                result['evidence'].append(f"Found {marker_count} {engine} markers nearby")
                result['template_type'] = engine
        
        # Priority 3: Template-specific patterns in the code itself
        template_patterns = [
            (r'\.get\s*\(["\'][^"\']+["\']\s*,\s*[^)]+\)', 0.2, 'dict.get pattern'),
            (r'(config|context|data|params|request|session)\[', 0.25, 'template object access'),
            (r'(loop|forloop)\.(index|counter|first|last)', 0.35, 'loop variable'),
            (r'(super|block|include|extends|load)\s+', 0.3, 'template directive'),
        ]
        
        for pattern, boost, description in template_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                result['confidence'] += boost
                result['evidence'].append(description)
        
        # Priority 4: File content analysis
        if self._file_has_template_structure(file_path):
            result['confidence'] += 0.2
            result['evidence'].append("File structure suggests template")
        
        # Final determination
        if result['confidence'] >= self.confidence_threshold:
            result['is_template'] = True
        
        return result
    
    def _get_context(self, file_path: Path, line_num: int, radius: int) -> List[str]:
        """Get surrounding lines for context analysis"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            start = max(0, line_num - radius - 1)
            end = min(len(lines), line_num + radius)
            return lines[start:end]
        except:
            return []
    
    def _file_has_template_structure(self, file_path: Path) -> bool:
        """Check if file has template-like structure"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read(1000)  # Check first 1000 chars
            # Look for HTML/XML structure with template markers
            has_html = bool(re.search(r'<[^>]+>', content))
            has_markers = bool(re.search(r'\{\{|\{%|\{\#', content))
            return has_html and has_markers
        except:
            return False
```

---

### **2. Orphaned Method Resolution**
**Target Impact**: +375-450 fixes (10-15% improvement)

#### **Implementation:**
```python
class OrphanedMethodResolver:
    """Resolve methods that were incorrectly extracted from classes"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.class_method_cache = {}  # Cache all class methods in project
        self.confidence_threshold = 0.85
        self._build_class_method_cache()
    
    def resolve_orphaned_method(self, func_call: FunctionCall) -> Optional[Dict]:
        """
        Resolve methods that appear undefined but exist in classes.
        Three resolution strategies:
        1. Restore class context (if method needs class)
        2. Convert to standalone function (if pure utility)
        3. Add proper import (if defined elsewhere)
        """
        
        # Strategy 1: self.method() without class instance
        if func_call.name.startswith('self.'):
            return self._resolve_self_method(func_call)
        
        # Strategy 2: Method name exists in a class
        if self._is_known_method(func_call.name):
            return self._resolve_class_method(func_call)
        
        # Strategy 3: Should be standalone function
        if self._should_be_standalone(func_call):
            return self._convert_to_function(func_call)
        
        return None
    
    def _resolve_self_method(self, func_call: FunctionCall) -> Dict:
        """Handle self.method() calls without class context"""
        method_name = func_call.name[5:]  # Remove 'self.'
        
        # Find all classes with this method
        containing_classes = self._find_classes_with_method(method_name)
        
        if not containing_classes:
            return {
                'fix_type': 'remove_self_prefix',
                'action': f"Convert self.{method_name}() to {method_name}()",
                'confidence': 0.9,
                'reasoning': 'No class found with this method, likely a function'
            }
        
        # If single class found, suggest restoration
        if len(containing_classes) == 1:
            class_name = containing_classes[0]
            return {
                'fix_type': 'restore_class_context',
                'action': f"Add class instance: {class_name.lower()} = {class_name}(); {class_name.lower()}.{method_name}()",
                'confidence': 0.85,
                'class_name': class_name,
                'method_name': method_name
            }
        
        # Multiple classes: need context analysis
        return self._analyze_context_for_class(func_call, containing_classes)
    
    def _should_be_standalone(self, func_call: FunctionCall) -> bool:
        """Determine if method should be converted to standalone function"""
        standalone_indicators = [
            'util', 'helper', 'calculate', 'validate', 'parse', 
            'format', 'convert', 'check', 'get', 'create'
        ]
        
        name_lower = func_call.name.lower()
        
        # Check naming patterns
        if any(indicator in name_lower for indicator in standalone_indicators):
            # Verify no class dependencies in implementation
            if not self._has_class_dependencies(func_call):
                return True
        
        return False
    
    def _has_class_dependencies(self, func_call: FunctionCall) -> bool:
        """Check if function uses class-specific features"""
        # Look for self references, instance variables, super() calls
        implementation = self._get_function_implementation(func_call)
        if implementation:
            class_patterns = [
                r'\bself\.',
                r'\bsuper\(\)',
                r'\bcls\.',
                r'@classmethod',
                r'@property'
            ]
            return any(re.search(pattern, implementation) for pattern in class_patterns)
        return False
    
    def _build_class_method_cache(self):
        """Build cache of all class methods in project"""
        for py_file in self.project_root.rglob('*.py'):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read())
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        class_name = node.name
                        methods = [
                            n.name for n in node.body 
                            if isinstance(n, ast.FunctionDef)
                        ]
                        self.class_method_cache[class_name] = {
                            'file': py_file,
                            'methods': methods
                        }
            except:
                continue
```

---

### **3. Dynamic Pattern Staticization**
**Target Impact**: +150-225 fixes (5-8% improvement)

#### **Implementation:**
```python
class DynamicPatternStaticizer:
    """Convert dynamic function calls to static where safely possible"""
    
    def __init__(self):
        self.confidence_threshold = 0.85
        self.safe_conversions = {}
        
    def staticize_dynamic_call(self, func_call: FunctionCall) -> Optional[Dict]:
        """
        Convert dynamic patterns to static equivalents.
        Handles: getattr, __getattribute__, property access, decorators
        """
        
        # Pattern 1: getattr with literal string
        if 'getattr' in func_call.context:
            return self._staticize_getattr(func_call)
        
        # Pattern 2: Dictionary of functions
        if self._is_function_dict_pattern(func_call):
            return self._staticize_function_dict(func_call)
        
        # Pattern 3: Decorator-generated methods
        if self._is_decorator_pattern(func_call):
            return self._resolve_decorator_method(func_call)
        
        # Pattern 4: Property access that looks like function
        if self._is_property_pattern(func_call):
            return self._resolve_property(func_call)
        
        return None
    
    def _staticize_getattr(self, func_call: FunctionCall) -> Optional[Dict]:
        """Convert getattr(obj, 'method_name') to obj.method_name"""
        
        # Match getattr pattern with literal string
        pattern = r'getattr\s*\(\s*([a-zA-Z_]\w*)\s*,\s*["\']([a-zA-Z_]\w*)["\']\s*\)'
        match = re.search(pattern, func_call.context)
        
        if match:
            obj_name, attr_name = match.groups()
            
            # Verify the attribute exists on the object
            if self._verify_attribute_exists(obj_name, attr_name, func_call):
                return {
                    'fix_type': 'staticize_getattr',
                    'original': f'getattr({obj_name}, "{attr_name}")',
                    'replacement': f'{obj_name}.{attr_name}',
                    'confidence': 0.90,
                    'reasoning': 'Literal string in getattr can be static'
                }
        
        # Handle getattr with default value
        pattern_with_default = r'getattr\s*\(\s*([a-zA-Z_]\w*)\s*,\s*["\']([a-zA-Z_]\w*)["\']\s*,\s*([^)]+)\)'
        match = re.search(pattern_with_default, func_call.context)
        
        if match:
            obj_name, attr_name, default = match.groups()
            return {
                'fix_type': 'staticize_getattr_with_fallback',
                'original': f'getattr({obj_name}, "{attr_name}", {default})',
                'replacement': f'{obj_name}.{attr_name} if hasattr({obj_name}, "{attr_name}") else {default}',
                'confidence': 0.85,
                'reasoning': 'Getattr with default converted to conditional'
            }
        
        return None
    
    def _is_decorator_pattern(self, func_call: FunctionCall) -> bool:
        """Check if undefined function is from a decorator"""
        common_decorators = [
            '@property', '@cached_property', '@staticmethod', '@classmethod',
            '@dataclass', '@lru_cache', '@wraps', '@contextmanager'
        ]
        
        # Check file for decorator usage
        context = self._get_file_context(func_call.file)
        return any(decorator in context for decorator in common_decorators)
    
    def _resolve_decorator_method(self, func_call: FunctionCall) -> Optional[Dict]:
        """Resolve methods generated by decorators"""
        
        # Common patterns from decorators
        decorator_patterns = {
            '_cache_clear': ('lru_cache', 'functools'),
            '_cache_info': ('lru_cache', 'functools'),
            '__wrapped__': ('wraps', 'functools'),
            '__post_init__': ('dataclass', 'dataclasses'),
        }
        
        if func_call.name in decorator_patterns:
            decorator, module = decorator_patterns[func_call.name]
            return {
                'fix_type': 'add_decorator_import',
                'action': f'from {module} import {decorator}',
                'confidence': 0.87,
                'reasoning': f'Method {func_call.name} is generated by {decorator} decorator'
            }
        
        return None
```

---

### **4. Cross-File Dependency Resolution**
**Target Impact**: +100-150 fixes (5-7% improvement)

#### **Implementation:**
```python
class CrossFileDependencyResolver:
    """Resolve complex import chains and circular dependencies"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.import_graph = {}  # Full dependency graph
        self.module_exports = {}  # What each module exports
        self.confidence_threshold = 0.85
        self._build_import_graph()
    
    def resolve_cross_file_dependency(self, func_call: FunctionCall) -> Optional[Dict]:
        """
        Find and fix missing imports across multiple files.
        Handles: import chains, relative imports, circular dependencies
        """
        
        # Find all possible sources for this function
        sources = self._find_function_sources(func_call.name)
        
        if not sources:
            return None
        
        # Calculate best import path
        best_import = self._calculate_optimal_import(
            func_call.file,
            sources,
            func_call.name
        )
        
        if best_import:
            return {
                'fix_type': 'add_cross_file_import',
                'import_statement': best_import['statement'],
                'source_file': best_import['source'],
                'confidence': best_import['confidence'],
                'reasoning': best_import['reasoning']
            }
        
        return None
    
    def _find_function_sources(self, func_name: str) -> List[Dict]:
        """Find all files that define or export this function"""
        sources = []
        
        for py_file in self.project_root.rglob('*.py'):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    tree = ast.parse(content)
                
                # Check direct function definitions
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef) and node.name == func_name:
                        sources.append({
                            'file': py_file,
                            'type': 'direct_definition',
                            'line': node.lineno
                        })
                    
                    # Check class methods
                    elif isinstance(node, ast.ClassDef):
                        for item in node.body:
                            if isinstance(item, ast.FunctionDef) and item.name == func_name:
                                sources.append({
                                    'file': py_file,
                                    'type': 'class_method',
                                    'class': node.name,
                                    'line': item.lineno
                                })
                    
                    # Check imports that re-export
                    elif isinstance(node, ast.ImportFrom):
                        for alias in node.names:
                            name = alias.asname if alias.asname else alias.name
                            if name == func_name or alias.name == '*':
                                sources.append({
                                    'file': py_file,
                                    'type': 're_export',
                                    'from': node.module
                                })
                
            except:
                continue
        
        return sources
    
    def _calculate_optimal_import(self, target_file: Path, sources: List[Dict], func_name: str) -> Optional[Dict]:
        """Calculate the best import statement"""
        
        best_option = None
        highest_confidence = 0
        
        for source in sources:
            # Calculate relative path
            try:
                rel_path = source['file'].relative_to(self.project_root)
                module_path = str(rel_path.with_suffix('')).replace('/', '.')
                
                # Check if direct import is possible
                if source['type'] == 'direct_definition':
                    import_stmt = f"from {module_path} import {func_name}"
                    confidence = 0.90
                    
                    # Check for circular dependency
                    if not self._creates_circular_dependency(target_file, source['file']):
                        if confidence > highest_confidence:
                            highest_confidence = confidence
                            best_option = {
                                'statement': import_stmt,
                                'source': source['file'],
                                'confidence': confidence,
                                'reasoning': 'Direct import from definition file'
                            }
                
                elif source['type'] == 'class_method':
                    import_stmt = f"from {module_path} import {source['class']}"
                    confidence = 0.85
                    
                    if confidence > highest_confidence:
                        highest_confidence = confidence
                        best_option = {
                            'statement': import_stmt,
                            'source': source['file'],
                            'confidence': confidence,
                            'reasoning': f"Import class {source['class']} containing method"
                        }
                
            except:
                continue
        
        return best_option
    
    def _creates_circular_dependency(self, file_a: Path, file_b: Path) -> bool:
        """Check if importing from file_b into file_a creates circular dependency"""
        # Simplified check - in practice would need full graph traversal
        try:
            with open(file_b, 'r') as f:
                content = f.read()
            # Check if file_b imports from file_a
            file_a_module = str(file_a.with_suffix('')).replace('/', '.')
            return file_a_module in content
        except:
            return False
```

---

## 📦 INTEGRATION INTO EXISTING AUTOFIX.PY

### **Critical: Modify existing file, don't create new one**

```python
# In scripts/autofix.py, enhance the existing Autofix class:

class Autofix:
    def __init__(self, config_file: Optional[Path] = None):
        # ... existing initialization ...
        
        # ADD Level 2 Enhancement Components
        self.template_detector = EnhancedTemplateDetector()
        self.orphan_resolver = OrphanedMethodResolver(self.project_root)
        self.dynamic_staticizer = DynamicPatternStaticizer()
        self.dependency_resolver = CrossFileDependencyResolver(self.project_root)
        
        # Level 2 metrics tracking
        self.l2_metrics = {
            'templates_identified': 0,
            'orphans_resolved': 0,
            'dynamics_staticized': 0,
            'dependencies_fixed': 0
        }
    
    def fix_undefined_functions(self) -> Dict:
        """Enhanced undefined function resolution with Level 2 strategies"""
        
        # ... existing initialization and scanning ...
        
        for undefined_call in undefined_calls:
            # Try existing Level 1 fixes first (40.1% success)
            if self._try_level1_fixes(undefined_call):
                continue
            
            # === LEVEL 2 ENHANCEMENTS START HERE ===
            
            # L2.1: Template Detection (Highest Impact)
            template_result = self.template_detector.detect_template_context(
                undefined_call.file,
                undefined_call.line,
                undefined_call.context
            )
            
            if template_result['is_template'] and template_result['confidence'] >= 0.85:
                # Not a real undefined function - it's a template variable
                self.l2_metrics['templates_identified'] += 1
                self._log_template_variable(undefined_call, template_result)
                continue
            
            # L2.2: Orphaned Method Resolution
            orphan_fix = self.orphan_resolver.resolve_orphaned_method(undefined_call)
            if orphan_fix and orphan_fix['confidence'] >= 0.85:
                success = self._apply_fix(orphan_fix, undefined_call)
                if success:
                    self.l2_metrics['orphans_resolved'] += 1
                    continue
            
            # L2.3: Dynamic Pattern Staticization
            static_fix = self.dynamic_staticizer.staticize_dynamic_call(undefined_call)
            if static_fix and static_fix['confidence'] >= 0.85:
                success = self._apply_fix(static_fix, undefined_call)
                if success:
                    self.l2_metrics['dynamics_staticized'] += 1
                    continue
            
            # L2.4: Cross-File Dependency Resolution
            dependency_fix = self.dependency_resolver.resolve_cross_file_dependency(undefined_call)
            if dependency_fix and dependency_fix['confidence'] >= 0.85:
                success = self._apply_fix(dependency_fix, undefined_call)
                if success:
                    self.l2_metrics['dependencies_fixed'] += 1
                    continue
            
            # If all strategies fail, mark for manual review
            results['manual_review'].append(undefined_call)
        
        # Report Level 2 metrics
        results.update({
            'level2_enhancements': self.l2_metrics,
            'total_automation_rate': self._calculate_total_automation_rate(results)
        })
        
        return results
```

---

## 📊 EXPECTED OUTCOMES AFTER LEVEL 2

### **Success Metrics:**
```
Before Level 2 (Current):
- Total Issues: 2,030
- Automated Fixes: 817 (40.1%)
- Manual Review: 1,213 (59.9%)

After Level 2 (Target):
- Total Issues: 2,030
- Automated Fixes: 1,530-1,625 (75-80%)
- Manual Review: 405-500 (20-25%)

Breakdown of L2 Improvements:
- Templates Identified: 600-750 (removes false positives)
- Orphans Resolved: 375-450 (restores context)
- Dynamics Staticized: 150-225 (converts patterns)
- Dependencies Fixed: 100-150 (adds imports)
```

### **Quality Assurance:**
- All fixes require ≥85% confidence
- Every fix is reversible
- No regressions introduced
- Existing 40.1% functionality preserved

---

## 🚀 IMPLEMENTATION TIMELINE

### **Week 1: Core Detection Systems**
- Day 1-2: Implement EnhancedTemplateDetector
- Day 3-4: Implement OrphanedMethodResolver
- Day 5: Integration testing with existing autofix

### **Week 2: Advanced Resolution**
- Day 6-7: Implement DynamicPatternStaticizer
- Day 8-9: Implement CrossFileDependencyResolver
- Day 10: Full integration into autofix.py

### **Week 3: Testing & Optimization**
- Day 11-12: Comprehensive testing on real codebase
- Day 13-14: Performance optimization
- Day 15: Final validation and metrics reporting

---

# PHASE 2: SELF-TRANSMUTATION (AFTER L2 SUCCESS)

## 🔄 Agent-Mediated Self-Enhancement: 75-80% → 95%

### **Prerequisites:**
- ✅ Level 2 implementation complete
- ✅ 75-80% automation achieved
- ✅ Remaining 20-25% analyzed and categorized

### **Transmutation Protocol Overview:**
Only after Level 2 success, autofix will:
1. Generate detailed analysis of remaining issues
2. Create formal request (TRF-001) for agent assistance
3. Receive agent insights (TRF-002) with new patterns
4. Safely integrate new capabilities
5. Iterate until 95% automation achieved

### **Why Transmutation AFTER Level 2:**
- Level 2 handles deterministic patterns (high confidence)
- Transmutation handles ambiguous cases (needs intelligence)
- Agent collaboration required for final 20-25%
- Safety-critical integration needs robust foundation

---

## 📋 AGENT REQUEST FORMAT (POST-L2)

```json
{
  "transmutation_request": {
    "current_state": {
      "automation_rate": 77.5,
      "total_issues": 2030,
      "resolved_by_l1": 817,
      "resolved_by_l2": 757,
      "remaining": 456
    },
    "remaining_categories": {
      "ambiguous_context": 230,
      "complex_inheritance": 115,
      "runtime_only": 75,
      "business_logic": 36
    },
    "sample_problems": [
      {
        "type": "ambiguous_context",
        "description": "Cannot determine if template or code",
        "confidence": 0.5,
        "needs": "Semantic understanding"
      }
    ],
    "request": "Provide patterns to resolve ambiguous cases"
  }
}
```

---

## ✅ DECISION CRITERIA

### **When to Proceed to Phase 2 (Transmutation):**
1. Level 2 achieves ≥75% automation
2. Remaining issues are categorized
3. Safety protocols are tested
4. Rollback mechanisms verified

### **When NOT to Proceed:**
1. Level 2 achieves <75% (need more direct fixes)
2. High false positive rate (>1%)
3. Safety concerns identified
4. Performance degradation observed

---

## 🎯 FINAL ARCHITECTURE

```
Current (40.1%) 
    ↓
Level 2 Enhancements (75-80%) ← [YOU ARE HERE]
    ↓
Self-Transmutation Protocol (90-95%)
    ↓
Human-in-Loop for Final 5%
```

---

## 📢 CALL TO ACTION

**Immediate Next Step**: Implement Level 2 enhancements in existing autofix.py

**Do NOT**:
- Create new autofix files
- Skip to transmutation before L2
- Remove existing functionality
- Lower confidence thresholds

**DO**:
- Enhance existing scripts/autofix.py
- Maintain backward compatibility
- Use ≥85% confidence threshold
- Track metrics for validation

---

## 🏁 CONCLUSION

This plan provides a clear, phased approach to achieving 95% automation:

1. **Phase 1 (Level 2)**: Direct implementation gets us to 75-80%
2. **Phase 2 (Transmutation)**: Agent collaboration reaches 95%

The Level 2 enhancements are deterministic, high-confidence improvements that can be implemented immediately. Only after their success should the self-transmutation protocol be considered for the remaining ambiguous cases.

**The path is clear: Level 2 first, transmutation second.**