#!/usr/bin/env python3
"""
Test script for Enhanced MCP Crafter System
Validates all core functionality and features
"""

import json
import sys
import tempfile
import time
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from enhanced_mcp_crafter import EnhancedMCPCrafter, EnhancedServerRequest
    from mcp_crafter_mcp_server import MCPCrafterServer
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running this from the mcp-system root directory")
    sys.exit(1)

def test_enhanced_crafter_basic():
    """Test basic Enhanced MCP Crafter functionality"""
    print("🧪 Testing Enhanced MCP Crafter Basic Functionality...")
    
    crafter = EnhancedMCPCrafter()
    
    # Test basic server generation
    request = EnhancedServerRequest(
        name="test-basic-server",
        template="python-fastmcp",
        description="Basic test server",
        port=8055,
        features=["cli"]
    )
    
    files = crafter.generate_enhanced_server(request)
    
    # Validate generated files
    expected_files = [
        "src/main.py",
        "src/cli.py", 
        "pyproject.toml",
        "README.md",
        ".env.example"
    ]
    
    for expected_file in expected_files:
        assert expected_file in files, f"Missing expected file: {expected_file}"
    
    # Validate main.py content
    main_content = files["src/main.py"]
    assert "from components.cli_component import setup_cli" in main_content
    assert "setup_cli" in main_content
    assert "test-basic-server" in main_content
    
    print("✅ Basic functionality test passed")
    return True

def test_all_features():
    """Test server generation with all features enabled"""
    print("🧪 Testing All Features Generation...")
    
    crafter = EnhancedMCPCrafter()
    
    request = EnhancedServerRequest(
        name="test-full-server",
        template="python-fastmcp",
        description="Server with all features",
        port=8056,
        features=["watchdog", "cli", "automation", "monitoring"],
        dependencies=["httpx"],
        environment={"TEST_VAR": "test_value"}
    )
    
    files = crafter.generate_enhanced_server(request)
    
    # Validate feature-specific files
    feature_files = [
        "src/components/watchdog_component.py",
        "src/components/automation_component.py", 
        "src/components/monitoring_component.py",
        "src/cli.py"
    ]
    
    for feature_file in feature_files:
        assert feature_file in files, f"Missing feature file: {feature_file}"
    
    # Validate dependencies in pyproject.toml
    pyproject_content = files["pyproject.toml"]
    assert "watchdog" in pyproject_content
    assert "schedule" in pyproject_content
    assert "psutil" in pyproject_content
    assert "click" in pyproject_content
    assert "httpx" in pyproject_content
    
    # Validate environment variables in .env.example
    env_content = files[".env.example"]
    assert "WATCHDOG_ENABLED=true" in env_content
    assert "AUTOMATION_ENABLED=true" in env_content
    assert "MONITORING_ENABLED=true" in env_content
    assert "TEST_VAR=test_value" in env_content
    
    print("✅ All features test passed")
    return True

def test_form_processing():
    """Test Claude form processing functionality"""
    print("🧪 Testing Form Processing...")
    
    crafter = EnhancedMCPCrafter()
    
    from enhanced_mcp_crafter import CrafterFormData
    
    form_data = CrafterFormData(
        form_type="server_generation",
        requirements={
            "name": "form-test-server",
            "template": "python-fastmcp",
            "description": "Server generated from form",
            "port": 8057,
            "features": ["cli", "monitoring"]
        },
        options={"test_option": "value"}
    )
    
    result = crafter.process_claude_form(form_data)
    
    assert result["status"] == "success"
    assert result["server_name"] == "form-test-server"
    assert "path" in result
    assert "features" in result
    
    print("✅ Form processing test passed")
    return True

def test_mcp_server_initialization():
    """Test MCP Crafter Server initialization"""
    print("🧪 Testing MCP Crafter Server Initialization...")
    
    # This tests that the server can be created without errors
    crafter_server = MCPCrafterServer()
    
    # Validate that the server has the expected tools
    assert hasattr(crafter_server, 'server')
    assert hasattr(crafter_server, 'crafter')
    assert hasattr(crafter_server, 'active_forms')
    assert hasattr(crafter_server, 'orchestration_tasks')
    
    print("✅ MCP Crafter Server initialization test passed")
    return True

def test_feature_modules():
    """Test individual feature module generation"""
    print("🧪 Testing Feature Module Generation...")
    
    crafter = EnhancedMCPCrafter()
    
    request = EnhancedServerRequest(
        name="module-test-server",
        template="python-fastmcp",
        description="Test server for modules",
        port=8058
    )
    
    # Test each feature module
    features_to_test = ["watchdog", "cli", "automation", "monitoring"]
    
    for feature in features_to_test:
        print(f"  Testing {feature} module...")
        module_method = getattr(crafter, f"_generate_{feature}_module")
        module_files = module_method(request)
        
        assert isinstance(module_files, dict)
        assert len(module_files) > 0
        
        # Each module should generate at least one file
        for file_path, content in module_files.items():
            assert isinstance(content, str)
            assert len(content) > 100  # Should be substantial content
            assert feature in content  # Should mention the feature
    
    print("✅ Feature module generation test passed")
    return True

def test_template_enhancement():
    """Test template enhancement functionality"""
    print("🧪 Testing Template Enhancement...")
    
    crafter = EnhancedMCPCrafter()
    
    # Create a simple base template
    base_files = {
        "src/main.py": """
# Basic server file
SERVER_NAME = "test"
print("Hello world")
""",
        "pyproject.toml": """
[project]
name = "test"
dependencies = ["basic-dep"]
""",
        "README.md": "# Test Server"
    }
    
    request = EnhancedServerRequest(
        name="enhancement-test",
        template="python-fastmcp", 
        description="Test enhancement",
        port=8059,
        features=["cli", "monitoring"],
        dependencies=["extra-dep"]
    )
    
    enhanced_files = crafter._enhance_base_template(base_files, request)
    
    # Should have additional files
    assert len(enhanced_files) > len(base_files)
    
    # Should have feature components
    assert "src/cli.py" in enhanced_files
    assert "src/components/monitoring_component.py" in enhanced_files
    
    # Enhanced pyproject should have additional dependencies
    enhanced_pyproject = enhanced_files["pyproject.toml"]
    assert "click" in enhanced_pyproject  # from CLI feature
    assert "psutil" in enhanced_pyproject  # from monitoring feature
    assert "extra-dep" in enhanced_pyproject  # from custom dependencies
    
    print("✅ Template enhancement test passed")
    return True

def test_file_creation():
    """Test actual file creation in filesystem"""
    print("🧪 Testing File System Creation...")
    
    crafter = EnhancedMCPCrafter()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        request = EnhancedServerRequest(
            name="filesystem-test",
            template="minimal-python", 
            description="Test filesystem creation",
            port=8060,
            features=["cli"],
            path=str(Path(temp_dir) / "test-server")
        )
        
        files = crafter.generate_enhanced_server(request)
        
        # Create files in temp directory
        server_path = Path(temp_dir) / "test-server"
        server_path.mkdir(parents=True, exist_ok=True)
        
        for file_path, content in files.items():
            full_path = server_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)
        
        # Validate files were created
        assert (server_path / "main.py").exists()
        assert (server_path / "src" / "cli.py").exists()
        assert (server_path / "requirements.txt").exists()
        
        # Validate content
        main_content = (server_path / "main.py").read_text()
        assert "filesystem-test" in main_content
    
    print("✅ File system creation test passed")
    return True

def run_all_tests():
    """Run all tests and report results"""
    print("🚀 Starting Enhanced MCP Crafter Test Suite")
    print("=" * 50)
    
    tests = [
        test_enhanced_crafter_basic,
        test_all_features,
        test_form_processing,
        test_mcp_server_initialization,
        test_feature_modules,
        test_template_enhancement,
        test_file_creation
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
                print(f"❌ {test.__name__} failed")
        except Exception as e:
            failed += 1
            print(f"❌ {test.__name__} failed with error: {e}")
    
    print("=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Enhanced MCP Crafter is working correctly.")
        return True
    else:
        print("⚠️ Some tests failed. Please check the output above.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)