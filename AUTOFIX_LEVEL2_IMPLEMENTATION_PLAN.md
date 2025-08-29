# Autofix Level 2 Enhancement Implementation Plan
## Bridge to 75-80% Automation Before Self-Transmutation

**Target**: Enhance autofix from 40.1% → 75-80% automation  
**Approach**: Direct implementation of high-confidence patterns  
**Timeline**: 2-3 weeks  
**Prerequisite for**: Self-transmutation protocol (post-L2)

---

## 📊 CURRENT STATE (Post PR #48)
- **Automation Rate**: 40.1% (817/2030 issues)
- **Remaining Issues**: 1213 undefined functions
- **Categories**:
  - Template variables: ~600-750 issues
  - Orphaned methods: ~375-450 issues  
  - Dynamic patterns: ~150-225 issues
  - Cross-file deps: ~100-150 issues

---

## 🎯 LEVEL 2 ENHANCEMENT TARGETS

### **1. Enhanced Template Context Detection (+15-20%)**

#### **Implementation in existing autofix.py:**
```python
class EnhancedTemplateDetector:
    """Add to autofix.py - DO NOT create new file"""
    
    def __init__(self):
        self.template_markers = {
            'jinja2': [r'\{\{', r'\}\}', r'\{%', r'%\}'],
            'django': [r'\{\{', r'\}\}', r'\{%', r'%\}'],
            'fstring': [r'f["\'].*\{.*\}'],
            'format': [r'\.format\('],
        }
        self.confidence_threshold = 0.85
        
    def detect_template_context(self, file_path: Path, line_num: int, code: str) -> Dict:
        """Determine if undefined function is actually a template variable"""
        
        # Check 1: File extension hints
        if file_path.suffix in ['.j2', '.jinja', '.template']:
            return {'is_template': True, 'confidence': 0.95, 'type': 'jinja2'}
            
        # Check 2: Surrounding context analysis (5 lines above/below)
        context = self._get_surrounding_context(file_path, line_num, radius=5)
        
        # Check 3: Template marker detection
        for template_type, markers in self.template_markers.items():
            if self._has_template_markers(context, markers):
                return {'is_template': True, 'confidence': 0.90, 'type': template_type}
                
        # Check 4: Common template patterns
        if self._matches_template_patterns(code):
            return {'is_template': True, 'confidence': 0.85, 'type': 'generic'}
            
        return {'is_template': False, 'confidence': 0.95}
    
    def _matches_template_patterns(self, code: str) -> bool:
        """Check for common template access patterns"""
        patterns = [
            r'\.get\s*\(["\'][^"\']+["\']\s*,\s*[^)]+\)',  # dict.get with default
            r'config\[',  # config access
            r'context\[',  # context access
            r'data\[',  # data access
            r'params\.',  # params access
            r'request\.',  # request object access
        ]
        return any(re.search(p, code) for p in patterns)
```

**Expected Resolution**: ~600-750 template false positives eliminated

---

### **2. Orphaned Method Resolution (+10-15%)**

#### **Implementation enhancement:**
```python
class OrphanedMethodResolver:
    """Add to autofix.py - enhance existing undefined function resolution"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.class_method_map = {}  # Cache of all class methods
        self.confidence_threshold = 0.85
        self._build_class_method_map()
        
    def resolve_orphaned_method(self, func_call: FunctionCall) -> Optional[Dict]:
        """Resolve methods that were extracted from classes"""
        
        # Pattern 1: self.method() without class context
        if func_call.name.startswith('self.'):
            method_name = func_call.name[5:]  # Remove 'self.'
            return self._find_and_fix_self_method(method_name, func_call)
            
        # Pattern 2: Likely method based on naming convention
        if self._looks_like_method(func_call.name):
            return self._find_class_for_method(func_call.name, func_call)
            
        # Pattern 3: Method that should be standalone function
        if self._should_be_standalone(func_call):
            return self._convert_to_standalone(func_call)
            
        return None
    
    def _find_and_fix_self_method(self, method_name: str, func_call: FunctionCall) -> Dict:
        """Find the class this method belongs to"""
        for class_name, methods in self.class_method_map.items():
            if method_name in methods:
                return {
                    'fix_type': 'restore_class_context',
                    'class_name': class_name,
                    'method_name': method_name,
                    'suggestion': f'# TODO: Restore {class_name} class context or convert to function',
                    'confidence': 0.90
                }
        return None
        
    def _should_be_standalone(self, func_call: FunctionCall) -> bool:
        """Determine if orphaned method should become standalone function"""
        # No 'self' references in implementation
        # Pure computational function
        # Utility-like naming
        indicators = [
            'util' in func_call.name.lower(),
            'helper' in func_call.name.lower(),
            'calculate' in func_call.name.lower(),
            'validate' in func_call.name.lower(),
            'parse' in func_call.name.lower(),
        ]
        return any(indicators)
```

**Expected Resolution**: ~375-450 orphaned methods resolved

---

### **3. Dynamic Pattern Staticization (+5-8%)**

#### **Implementation enhancement:**
```python
class DynamicPatternStaticizer:
    """Add to autofix.py - resolve common dynamic patterns statically"""
    
    def __init__(self):
        self.known_dynamic_patterns = {}
        self.confidence_threshold = 0.85
        self._analyze_codebase_patterns()
        
    def staticize_dynamic_call(self, func_call: FunctionCall) -> Optional[Dict]:
        """Convert dynamic calls to static where safely possible"""
        
        # Pattern 1: getattr with literal string
        if 'getattr(' in func_call.context:
            return self._staticize_getattr(func_call)
            
        # Pattern 2: Common decorator-generated methods
        if self._is_decorator_pattern(func_call):
            return self._resolve_decorator_method(func_call)
            
        # Pattern 3: Property access patterns
        if self._is_property_pattern(func_call):
            return self._resolve_property_access(func_call)
            
        return None
        
    def _staticize_getattr(self, func_call: FunctionCall) -> Optional[Dict]:
        """Convert getattr(obj, 'method') to obj.method"""
        pattern = r'getattr\s*\(\s*(\w+)\s*,\s*["\'](\w+)["\']\s*\)'
        match = re.search(pattern, func_call.context)
        if match:
            obj_name, method_name = match.groups()
            return {
                'fix_type': 'staticize_dynamic',
                'original': f'getattr({obj_name}, "{method_name}")',
                'replacement': f'{obj_name}.{method_name}',
                'confidence': 0.90
            }
        return None
```

**Expected Resolution**: ~150-225 dynamic patterns staticized

---

### **4. Cross-File Dependency Resolution (+5-7%)**

#### **Implementation enhancement:**
```python
class CrossFileDependencyResolver:
    """Add to autofix.py - resolve import chains and dependencies"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.import_graph = {}  # Dependency graph
        self.module_exports = {}  # What each module exports
        self._build_dependency_graph()
        
    def resolve_cross_file_dependency(self, func_call: FunctionCall) -> Optional[Dict]:
        """Resolve functions that need multi-file import chains"""
        
        # Find all modules that export this function
        exporting_modules = self._find_exporters(func_call.name)
        
        if not exporting_modules:
            return None
            
        # Calculate shortest import path
        import_path = self._calculate_import_path(
            func_call.file, 
            exporting_modules
        )
        
        if import_path:
            return {
                'fix_type': 'add_import_chain',
                'import_statement': self._generate_import(import_path),
                'confidence': 0.85
            }
            
        return None
```

**Expected Resolution**: ~100-150 cross-file dependencies resolved

---

## 📝 IMPLEMENTATION APPROACH

### **CRITICAL: Enhance existing autofix.py - DO NOT create new file**

```python
# In scripts/autofix.py, add these enhancements to existing class:

class Autofix:
    def __init__(self):
        # ... existing init code ...
        
        # Add Level 2 components
        self.template_detector = EnhancedTemplateDetector()
        self.orphan_resolver = OrphanedMethodResolver(self.project_root)
        self.dynamic_staticizer = DynamicPatternStaticizer()
        self.dependency_resolver = CrossFileDependencyResolver(self.project_root)
        
    def fix_undefined_functions(self) -> Dict:
        """Enhanced with Level 2 resolution strategies"""
        
        # ... existing code ...
        
        for undefined_call in undefined_calls:
            # Existing Level 1 attempts
            if existing_resolution_works:
                continue
                
            # NEW: Level 2 Template Detection
            template_check = self.template_detector.detect_template_context(
                undefined_call.file, 
                undefined_call.line,
                undefined_call.context
            )
            if template_check['is_template'] and template_check['confidence'] >= 0.85:
                # Mark as template variable, not undefined function
                results['template_variables_identified'] += 1
                continue
                
            # NEW: Level 2 Orphaned Method Resolution  
            orphan_fix = self.orphan_resolver.resolve_orphaned_method(undefined_call)
            if orphan_fix and orphan_fix['confidence'] >= 0.85:
                self._apply_orphan_fix(orphan_fix, undefined_call)
                results['orphaned_methods_resolved'] += 1
                continue
                
            # NEW: Level 2 Dynamic Staticization
            static_fix = self.dynamic_staticizer.staticize_dynamic_call(undefined_call)
            if static_fix and static_fix['confidence'] >= 0.85:
                self._apply_static_fix(static_fix, undefined_call)
                results['dynamic_patterns_staticized'] += 1
                continue
                
            # NEW: Level 2 Cross-file Resolution
            dependency_fix = self.dependency_resolver.resolve_cross_file_dependency(undefined_call)
            if dependency_fix and dependency_fix['confidence'] >= 0.85:
                self._apply_dependency_fix(dependency_fix, undefined_call)
                results['cross_file_dependencies_resolved'] += 1
                continue
                
            # If still unresolved, mark for manual review
            results['manual_review_required'].append(undefined_call)
```

---

## 🎯 SUCCESS METRICS

### **Target Outcomes:**
- **Automation Rate**: 75-80% (1520-1624 of 2030 issues)
- **Template Detection**: 600-750 correctly identified
- **Orphan Resolution**: 375-450 methods resolved
- **Dynamic Staticization**: 150-225 patterns converted
- **Dependency Resolution**: 100-150 imports fixed

### **Quality Gates:**
- False positive rate < 1%
- No regressions introduced
- All fixes reversible
- Confidence threshold ≥ 0.85

---

## 🚀 IMPLEMENTATION TIMELINE

### **Week 1: Template & Orphan Detection**
- Days 1-3: Implement EnhancedTemplateDetector
- Days 4-5: Implement OrphanedMethodResolver
- Days 6-7: Test and validate

### **Week 2: Dynamic & Dependency Resolution**  
- Days 8-9: Implement DynamicPatternStaticizer
- Days 10-11: Implement CrossFileDependencyResolver
- Days 12-14: Integration and testing

### **Week 3: Validation & Optimization**
- Days 15-16: Performance optimization
- Days 17-18: Edge case handling
- Days 19-21: Final validation and metrics

---

## ❗ IMPORTANT NOTES FOR @copilot

1. **DO NOT create new autofix file** - Enhance existing scripts/autofix.py
2. **Maintain backward compatibility** - Don't break existing 40.1% functionality
3. **Use confidence thresholds** - Only apply fixes with ≥85% confidence
4. **Preserve safety mechanisms** - All Level 1 safety features must remain
5. **Incremental implementation** - Can be done in phases if needed

---

## 🔄 NEXT STEPS AFTER L2 SUCCESS

Only after achieving 75-80% automation with Level 2:
1. Implement self-transmutation protocol for remaining 20-25%
2. Use agent collaboration for complex patterns
3. Achieve 90-95% total automation

---

## ❓ REQUEST FOR CRITIQUE

@copilot - Please review this Level 2 implementation plan:

1. **Is the 75-80% target realistic** with these enhancements?
2. **Are the implementation approaches sound** for each category?
3. **Should any techniques be modified** for better success?
4. **What edge cases need special attention**?
5. **Is 2-3 weeks sufficient** for this implementation?

Please implement these Level 2 enhancements in the existing autofix.py file to achieve 75-80% automation before we proceed with the self-transmutation protocol.