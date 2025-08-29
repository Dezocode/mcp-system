#!/usr/bin/env python3
"""
Demo script to showcase smart import analyzer capabilities
This script demonstrates the enhanced autofix tool with smart import analysis
"""

import tempfile
import os
from pathlib import Path
from scripts.autofix import MCPAutofix, HighResolutionAnalyzer

def create_test_files():
    """Create test files with various import issues"""
    
    # Test file 1: Missing imports and redundant imports
    test_file_1_content = '''import os
import sys
import json
import unused_module_1
import unused_module_2
from typing import Dict, List, Optional
from pathlib import Path
import collections  # unused

def process_data():
    # Using Path, json, but not others
    p = Path('/tmp/test')
    data = json.dumps({'key': 'value'})
    
    # Using undefined symbols that should be imported
    result = defaultdict(list)  # Should import from collections
    pattern = re.compile(r'\\d+')  # Should import re
    
    return p, data, result, pattern

class DataProcessor:
    def __init__(self):
        self.data = {}
    
    def process(self):
        # Using datetime without import
        now = datetime.now()
        return now
'''

    # Test file 2: Local module usage
    test_file_2_content = '''import sys
from pathlib import Path

def helper_function():
    # Should import from test file 1
    processor = DataProcessor()
    return processor.process()

def main():
    result = helper_function()
    print(f"Result: {result}")
'''

    # Create temporary directory
    temp_dir = Path(tempfile.mkdtemp())
    
    # Write test files
    test_file_1 = temp_dir / "test_module_1.py"
    test_file_2 = temp_dir / "test_module_2.py"
    
    test_file_1.write_text(test_file_1_content)
    test_file_2.write_text(test_file_2_content)
    
    return temp_dir, [test_file_1, test_file_2]

def demonstrate_smart_import_analysis():
    """Demonstrate the smart import analyzer capabilities"""
    
    print("🧠 Smart Import Analyzer Demo")
    print("=" * 50)
    
    # Create test files
    temp_dir, test_files = create_test_files()
    
    try:
        # Initialize enhanced autofix with the temp directory
        autofix = MCPAutofix(repo_path=temp_dir, dry_run=True, verbose=False)
        
        if not hasattr(autofix, 'high_res_analyzer'):
            print("❌ High resolution analyzer not available")
            return
        
        analyzer = autofix.high_res_analyzer
        
        print(f"✅ Smart import analysis initialized:")
        print(f"  - Standard library modules: {len(analyzer.standard_library_modules)}")
        print(f"  - Installed packages: {len(analyzer.installed_packages)}")
        print(f"  - Local modules: {len(analyzer.local_modules)}")
        print(f"  - Import usage patterns: {len(analyzer.import_usage_patterns)}")
        print()
        
        # Test import suggestions for common symbols
        symbols_to_test = ['Path', 'defaultdict', 'datetime', 're', 'json']
        
        print("🔍 Smart Import Suggestions:")
        print("-" * 30)
        
        for symbol in symbols_to_test:
            suggestion = analyzer.suggest_smart_import(symbol, test_files[0])
            if suggestion:
                print(f"  {symbol:12} -> {suggestion['import_statement']}")
                print(f"  {'':12}    (confidence: {suggestion['confidence']:.2f}, source: {suggestion['source']})")
            else:
                print(f"  {symbol:12} -> No suggestion found")
        print()
        
        # Analyze import issues in test files
        print("📊 Import Analysis Results:")
        print("-" * 30)
        
        for i, test_file in enumerate(test_files, 1):
            print(f"\nFile {i}: {test_file.name}")
            optimization_result = analyzer.optimize_imports_in_file(test_file)
            
            print(f"  - Redundant imports: {optimization_result['redundant_removed']}")
            print(f"  - Missing imports: {optimization_result['missing_added']}")
            print(f"  - Suggestions provided: {len(optimization_result['suggestions'])}")
            
            if optimization_result['suggestions']:
                print("  - Import suggestions:")
                for suggestion in optimization_result['suggestions'][:3]:  # Show first 3
                    print(f"    * {suggestion['import_statement']} (confidence: {suggestion['confidence']:.2f})")
        
        # Run full import optimization
        print("\n🔧 Running Full Import Optimization:")
        print("-" * 40)
        
        import_results = autofix.fix_import_issues()
        print(f"  - Files processed: {import_results['files_processed']}")
        print(f"  - Files modified: {import_results['files_modified']}")
        print(f"  - Redundant imports removed: {import_results['redundant_removed']}")
        print(f"  - Missing imports added: {import_results['missing_added']}")
        print(f"  - Imports reorganized: {import_results['imports_reorganized']}")
        
        print("\n✅ Smart Import Analysis Demo Complete!")
        
    finally:
        # Clean up temporary files
        import shutil
        shutil.rmtree(temp_dir)

def show_configuration_options():
    """Show the configuration options for smart import analysis"""
    
    print("\n⚙️ Smart Import Analyzer Configuration:")
    print("-" * 40)
    
    autofix = MCPAutofix(dry_run=True, verbose=False)
    config = autofix.config
    
    print(f"  Higher Resolution Features:")
    print(f"  - Enable High Resolution: {config.enable_high_resolution}")
    print(f"  - Granular Classification: {config.granular_classification}")
    print(f"  - Line Level Precision: {config.line_level_precision}")
    print(f"  - Context Aware Fixes: {config.context_aware_fixes}")
    print(f"  - Surgical Fix Mode: {config.surgical_fix_mode}")
    print(f"  - Advanced Validation: {config.advanced_validation}")
    print(f"  - Detailed Reporting: {config.detailed_reporting}")
    
    print(f"\n  Smart Import Analysis Settings:")
    print(f"  - Similarity Threshold: {config.similarity_threshold}")
    print(f"  - Complexity Threshold: {config.complexity_threshold}")
    print(f"  - Dependency Depth: {config.dependency_depth}")
    print(f"  - Validation Levels: {config.validation_levels}")

if __name__ == "__main__":
    print("🔬 Enhanced MCP Autofix - Smart Import Analyzer Demo")
    print("=" * 60)
    
    try:
        demonstrate_smart_import_analysis()
        show_configuration_options()
        
        print("\n🎯 Key Features Demonstrated:")
        print("  ✅ Intelligent import suggestion based on symbol usage")
        print("  ✅ Context-aware confidence scoring")
        print("  ✅ Multi-source import resolution (stdlib, packages, local)")
        print("  ✅ Redundant import detection and removal")
        print("  ✅ Missing import identification and suggestions")
        print("  ✅ Usage pattern analysis for better recommendations")
        print("  ✅ High-resolution analysis with best practices")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()