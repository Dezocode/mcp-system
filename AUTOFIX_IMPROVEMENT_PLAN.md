# Autofix Tool Improvement Plan - Preventing Induced Errors

## 🔴 Current Critical Issues

1. **Broken utils/functions.py** - Contains orphaned `__init__` method without class context
2. **Blind code extraction** - Pulls methods out of classes without understanding context
3. **No rollback on failure** - Creates syntax errors then continues
4. **Insufficient validation** - Only checks syntax AFTER making changes

## 🎯 High-Resolution Improvements Needed

### 1. **Context-Aware Code Analysis**
```python
def extract_function_with_context(self, node, file_content):
    """Extract function only if it's safe to move"""
    
    # Check if function is part of a class
    parent = self.get_parent_node(node)
    if isinstance(parent, ast.ClassDef):
        # Don't extract class methods
        if node.name in ['__init__', '__str__', '__repr__', '__call__']:
            return None  # NEVER extract special methods
        
        # Check if method uses self/cls
        if self.uses_instance_variables(node):
            return None  # Can't safely extract
    
    # Check dependencies
    if self.has_local_dependencies(node):
        return None  # Has dependencies that can't be moved
    
    return self.safe_extract(node)
```

### 2. **Pre-Flight Validation**
```python
def validate_before_change(self, file_path, old_content, new_content):
    """Validate changes BEFORE writing to file"""
    
    # 1. Parse both versions
    try:
        old_tree = ast.parse(old_content)
        new_tree = ast.parse(new_content)
    except SyntaxError:
        return False, "Syntax error in new content"
    
    # 2. Check function count preserved
    old_funcs = self.count_functions(old_tree)
    new_funcs = self.count_functions(new_tree)
    if new_funcs < old_funcs and not self.intentional_removal:
        return False, "Functions lost"
    
    # 3. Check imports still valid
    if not self.validate_imports(new_tree):
        return False, "Invalid imports"
    
    # 4. Test parse in isolated environment
    if not self.sandbox_test(new_content):
        return False, "Failed sandbox test"
    
    return True, "Valid"
```

### 3. **Atomic Operations with Rollback**
```python
class AtomicFix:
    """Ensure all fixes are atomic with rollback capability"""
    
    def __init__(self, file_path):
        self.file_path = file_path
        self.original_content = None
        self.backup_path = None
    
    def __enter__(self):
        # Create backup
        self.original_content = self.file_path.read_text()
        self.backup_path = self.file_path.with_suffix('.autofix.backup')
        self.backup_path.write_text(self.original_content)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # Rollback on any exception
            self.file_path.write_text(self.original_content)
            print(f"Rolled back {self.file_path}")
        
        # Clean up backup
        if self.backup_path.exists():
            self.backup_path.unlink()
```

### 4. **Smart Duplicate Detection**
```python
def identify_safe_duplicates(self):
    """Only identify duplicates that can be safely consolidated"""
    
    safe_duplicates = []
    
    for dup_group in self.find_duplicates():
        # Filter out class methods
        standalone_funcs = [
            f for f in dup_group 
            if not self.is_class_method(f)
        ]
        
        # Need at least 2 standalone functions
        if len(standalone_funcs) >= 2:
            # Check they're truly identical (not just similar)
            if self.are_identical(standalone_funcs):
                safe_duplicates.append(standalone_funcs)
    
    return safe_duplicates
```

### 5. **AST-Based Safe Transformations**
```python
class SafeTransformer(ast.NodeTransformer):
    """Only make safe AST transformations"""
    
    def visit_FunctionDef(self, node):
        # Never modify __init__ or other special methods
        if node.name.startswith('__') and node.name.endswith('__'):
            return node
        
        # Check if function is safe to modify
        if not self.is_safe_to_modify(node):
            return node
        
        # Apply transformation
        return self.transform_safely(node)
    
    def is_safe_to_modify(self, node):
        """Determine if node can be safely modified"""
        # Check for decorators
        if node.decorator_list:
            return False  # Don't modify decorated functions
        
        # Check for complex control flow
        if self.has_complex_control_flow(node):
            return False
        
        return True
```

### 6. **Incremental Testing**
```python
def test_after_each_fix(self):
    """Run quick tests after each fix to catch issues early"""
    
    # Quick syntax check
    if not self.quick_syntax_check():
        return False
    
    # Import check
    if not self.can_import_all_modules():
        return False
    
    # Run fast unit tests if available
    if self.has_fast_tests():
        if not self.run_fast_tests():
            return False
    
    return True
```

### 7. **Enhanced Error Recovery**
```python
def fix_induced_errors(self):
    """Detect and fix errors we may have caused"""
    
    # Detect common induced errors
    induced_errors = []
    
    # Orphaned methods
    orphaned = self.find_orphaned_methods()
    for method in orphaned:
        # Either remove or properly wrap in class
        self.fix_orphaned_method(method)
    
    # Broken imports
    broken_imports = self.find_broken_imports()
    for imp in broken_imports:
        self.fix_import(imp)
    
    # Indentation errors
    indent_errors = self.find_indentation_errors()
    for error in indent_errors:
        self.fix_indentation(error)
```

## 🚀 Implementation Priority

1. **IMMEDIATE FIX** - Fix the broken utils/functions.py
2. **Add rollback system** - Every change must be reversible
3. **Context-aware extraction** - Never extract class methods blindly
4. **Pre-validation** - Check syntax BEFORE writing
5. **Smart duplicate detection** - Only consolidate truly safe duplicates
6. **Incremental testing** - Test after each change
7. **Error recovery** - Detect and fix induced errors

## 📋 Specific Improvements to scripts/autofix.py

### Fix the move_to_utils method
```python
def move_to_utils(self, func_info: Dict) -> bool:
    """Move function to utils module ONLY if safe"""
    
    # NEW: Check if it's a class method
    if self.is_class_method(func_info):
        self.log(f"Cannot move class method {func_info['name']} to utils", "warning")
        return False
    
    # NEW: Validate the function can stand alone
    if not self.can_function_stand_alone(func_info):
        self.log(f"Function {func_info['name']} has dependencies, cannot move", "warning")
        return False
    
    # Continue with safe extraction...
```

### Fix the replace_with_import method
```python
def replace_with_import(self, duplicate: Dict, best: Dict) -> bool:
    """Replace duplicate ONLY if it's safe"""
    
    # NEW: Pre-flight checks
    with AtomicFix(Path(duplicate["file"])) as fix:
        try:
            # Make changes
            new_content = self.create_replacement(duplicate, best)
            
            # Validate BEFORE writing
            valid, msg = self.validate_before_change(
                duplicate["file"], 
                fix.original_content, 
                new_content
            )
            
            if not valid:
                raise ValueError(f"Invalid replacement: {msg}")
            
            # Write only if valid
            Path(duplicate["file"]).write_text(new_content)
            
            # Test immediately
            if not self.test_after_each_fix():
                raise RuntimeError("Tests failed after fix")
                
        except Exception as e:
            self.log(f"Failed to replace duplicate: {e}", "error")
            # AtomicFix will rollback automatically
            return False
```

## 🎯 Expected Outcomes

- **Zero induced errors** - No more breaking working code
- **Safe consolidation** - Only move truly standalone functions
- **Automatic recovery** - Rollback on any failure
- **Preserve functionality** - Never break existing code
- **Higher success rate** - 95%+ successful fixes

## 🔧 Next Steps

1. Fix the immediate issue in utils/functions.py
2. Implement AtomicFix context manager
3. Add context-aware code analysis
4. Enhance validation before changes
5. Test thoroughly with rollback capability