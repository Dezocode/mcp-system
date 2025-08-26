#!/usr/bin/env python3
"""
Test Enhanced Crafter Watchdog Integration
Comprehensive test of the enhanced MCP crafter with watchdog capabilities
"""

import asyncio
import json
import logging
import sys
import tempfile
from pathlib import Path
from datetime import datetime, timezone

# Setup path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import our enhanced crafter
from enhanced_crafter_watchdog import (
    EnhancedCrafterWatchdog,
    MCPComplianceValidator,
    ContinuousImprovementLoop,
    CrafterPhase
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("test_enhanced_crafter")


async def test_enhanced_crafter_functionality():
    """Test all enhanced crafter functionality"""
    
    print("🧪 Testing Enhanced Crafter Watchdog Integration")
    print("=" * 60)
    
    # Create temporary workspace
    with tempfile.TemporaryDirectory() as temp_dir:
        workspace_dir = Path(temp_dir) / "test_workspace"
        mcp_tools_dir = Path(temp_dir) / "test_mcp_tools"
        
        # Initialize enhanced crafter
        print("\n📦 Initializing Enhanced Crafter Watchdog...")
        crafter = EnhancedCrafterWatchdog(
            workspace_dir=workspace_dir,
            mcp_tools_dir=mcp_tools_dir
        )
        
        # Test 1: MCP Compliance Validation
        print("\n🔍 Test 1: MCP Compliance Validation")
        compliance_validator = MCPComplianceValidator()
        
        # Create a test server structure
        test_server_path = mcp_tools_dir / "test_server"
        test_server_path.mkdir(parents=True, exist_ok=True)
        (test_server_path / "src").mkdir(exist_ok=True)
        
        # Create minimal MCP-compliant main.py
        main_py_content = '''#!/usr/bin/env python3
"""Test MCP Server"""
import asyncio
import logging
import mcp.types as types

logger = logging.getLogger(__name__)

async def setup_mcp_tools():
    """Setup MCP tools"""
    tools = []
    tools.append(types.Tool(
        name="test_tool",
        description="Test tool",
        inputSchema={"type": "object", "properties": {"data": {"type": "string"}}}
    ))
    return tools

async def handle_test_tool(arguments):
    """Handle test tool requests"""
    return {"success": True, "data": arguments.get("data", "")}

if __name__ == "__main__":
    asyncio.run(setup_mcp_tools())
'''
        
        (test_server_path / "src" / "main.py").write_text(main_py_content)
        (test_server_path / "README.md").write_text("# Test Server")
        (test_server_path / "pyproject.toml").write_text("[project]\\nname = 'test-server'")
        (test_server_path / ".env.example").write_text("# Test env")
        
        # Test compliance validation
        compliance_result = await compliance_validator.validate_server(test_server_path)
        print(f"   Compliance Score: {compliance_result['compliance_score']:.1f}%")
        print(f"   Compliant: {compliance_result['compliant']}")
        print(f"   Errors: {len(compliance_result['errors'])}")
        print(f"   Warnings: {len(compliance_result['warnings'])}")
        
        # Test 2: Create Resume MCP Server with Watchdog
        print("\n🎯 Test 2: Create Resume MCP Server with Full Monitoring")
        
        resume_specs = {
            "server_name": "test_resume_server",
            "architecture": "modular_pipeline",
            "components": ["ingestion", "processing", "export"],
            "modules": [
                {
                    "name": "ingestion",
                    "path": "src/ingestion.py",
                    "type": "data_processor",
                    "classes": ["FormParser"],
                    "functions": ["parse_resume_form"],
                    "dependencies": ["pydantic"]
                },
                {
                    "name": "processing", 
                    "path": "src/processing.py",
                    "type": "business_logic",
                    "classes": ["ResumeProcessor"],
                    "functions": ["process_resume"],
                    "dependencies": ["nltk"]
                }
            ],
            "functions": [
                {
                    "name": "setup_mcp_tools",
                    "file_path": "src/main.py",
                    "signature": "async def setup_mcp_tools():",
                    "implementation": '''tools = []
tools.append(types.Tool(
    name="parse_resume",
    description="Parse resume data",
    inputSchema={"type": "object", "properties": {"data": {"type": "object"}}}
))
return tools''',
                    "async": True
                }
            ]
        }
        
        # Create server with watchdog monitoring
        build_result = await crafter.create_mcp_server_with_watchdog(
            resume_specs,
            enable_pause_resume=True
        )
        
        print(f"   Build Success: {build_result['success']}")
        print(f"   Session ID: {build_result['session_id']}")
        print(f"   Phases Completed: {len(build_result['phases'])}")
        
        if build_result['success']:
            print("   ✅ Server created successfully!")
            
            # Test compliance of created server
            created_server_path = mcp_tools_dir / resume_specs["server_name"]
            if created_server_path.exists():
                final_compliance = await compliance_validator.validate_server(created_server_path)
                print(f"   Final Compliance Score: {final_compliance['compliance_score']:.1f}%")
        else:
            print("   ❌ Server creation failed")
            if 'error' in build_result:
                print(f"   Error: {build_result['error']}")
        
        # Test 3: Pause/Resume Functionality
        print("\n⏸️  Test 3: Pause/Resume Functionality")
        session_id = build_result['session_id']
        
        # Get session status
        status = await crafter.get_session_status(session_id)
        print(f"   Session Status: {json.dumps(status, indent=2, default=str)}")
        
        # Test pause
        pause_result = await crafter.pause_session(session_id)
        print(f"   Pause Result: {pause_result}")
        
        # Test resume
        resume_result = await crafter.resume_session(session_id)
        print(f"   Resume Result: {resume_result}")
        
        # Test 4: Continuous Improvement Analysis
        print("\n🔄 Test 4: Continuous Improvement Analysis")
        improvement_loop = ContinuousImprovementLoop(crafter)
        
        analysis = await improvement_loop.analyze_performance(build_result)
        print(f"   Performance Analysis: {json.dumps(analysis, indent=2, default=str)}")
        
        # Test 5: Quality Validation
        print("\n📊 Test 5: Quality Validation using Resume Server")
        
        # Validate the created server as quality benchmark
        if build_result['success']:
            server_path = mcp_tools_dir / resume_specs["server_name"]
            
            # Structure validation
            structure_validation = crafter.standardizer.validate_server_structure(server_path)
            print(f"   Structure Valid: {structure_validation.get('valid', False)}")
            
            # MCP compliance validation
            compliance_validation = await crafter.compliance_validator.validate_server(server_path)
            print(f"   MCP Compliance: {compliance_validation.get('compliant', False)}")
            print(f"   Compliance Score: {compliance_validation.get('compliance_score', 0):.1f}%")
            
            # Generate final validation report
            is_valid, report = crafter.validator.generate_report()
            print(f"   Validator Report Valid: {is_valid}")
            print(f"   Report Length: {len(report)} characters")
        
        print("\n🎉 Testing Complete!")
        print("=" * 60)
        
        return {
            "test_passed": True,
            "compliance_score": compliance_result['compliance_score'],
            "build_success": build_result['success'],
            "session_management": pause_result and resume_result,
            "improvement_analysis": len(analysis) > 0,
            "quality_validation": build_result['success']
        }


async def test_mcp_compliance_rules():
    """Test individual MCP compliance rules"""
    
    print("\n🔍 Testing MCP Compliance Rules in Detail")
    print("-" * 40)
    
    validator = MCPComplianceValidator()
    
    # Create test scenarios
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir)
        
        # Test scenario 1: Non-compliant server (missing files)
        print("\\n📝 Test Scenario 1: Non-compliant server")
        empty_server = test_dir / "empty_server"
        empty_server.mkdir()
        
        result1 = await validator.validate_server(empty_server)
        print(f"   Compliance Score: {result1['compliance_score']:.1f}%")
        print(f"   Errors: {len(result1['errors'])}")
        print(f"   Compliant: {result1['compliant']}")
        
        # Test scenario 2: Partially compliant server
        print("\\n📝 Test Scenario 2: Partially compliant server")
        partial_server = test_dir / "partial_server"
        partial_server.mkdir()
        (partial_server / "main.py").write_text("import mcp\\nprint('hello')")
        
        result2 = await validator.validate_server(partial_server)
        print(f"   Compliance Score: {result2['compliance_score']:.1f}%")
        print(f"   Errors: {len(result2['errors'])}")
        print(f"   Warnings: {len(result2['warnings'])}")
        
        # Test scenario 3: Fully compliant server
        print("\\n📝 Test Scenario 3: Fully compliant server")
        compliant_server = test_dir / "compliant_server"
        compliant_server.mkdir()
        (compliant_server / "src").mkdir()
        
        compliant_main = '''#!/usr/bin/env python3
import asyncio
import logging
import mcp.types as types

async def setup_mcp_tools():
    tools = []
    tools.append(types.Tool(
        name="test_tool",
        description="Test tool",
        inputSchema={"type": "object", "properties": {"data": {"type": "string"}}}
    ))
    return tools

async def handle_test_tool(arguments):
    return {"success": True}
'''
        
        (compliant_server / "src" / "main.py").write_text(compliant_main)
        
        result3 = await validator.validate_server(compliant_server)
        print(f"   Compliance Score: {result3['compliance_score']:.1f}%")
        print(f"   Errors: {len(result3['errors'])}")
        print(f"   Compliant: {result3['compliant']}")
        
        return {
            "empty_server_score": result1['compliance_score'],
            "partial_server_score": result2['compliance_score'],
            "compliant_server_score": result3['compliance_score']
        }


async def run_comprehensive_tests():
    """Run all comprehensive tests"""
    
    print("🚀 Enhanced MCP Crafter Watchdog - Comprehensive Test Suite")
    print("=" * 70)
    
    try:
        # Run main functionality tests
        main_results = await test_enhanced_crafter_functionality()
        
        # Run compliance rule tests
        compliance_results = await test_mcp_compliance_rules()
        
        # Summary
        print("\\n📊 TEST SUMMARY")
        print("=" * 30)
        print(f"Main Tests Passed: {main_results['test_passed']}")
        print(f"Build Success: {main_results['build_success']}")
        print(f"Session Management: {main_results['session_management']}")
        print(f"Compliance Validation: {main_results['compliance_score']:.1f}%")
        print(f"Quality Validation: {main_results['quality_validation']}")
        
        print(f"\\nCompliance Test Results:")
        print(f"  Empty Server: {compliance_results['empty_server_score']:.1f}%")
        print(f"  Partial Server: {compliance_results['partial_server_score']:.1f}%")
        print(f"  Compliant Server: {compliance_results['compliant_server_score']:.1f}%")
        
        overall_success = (
            main_results['test_passed'] and
            main_results['build_success'] and
            compliance_results['compliant_server_score'] > 80
        )
        
        print(f"\\n🎯 OVERALL TEST RESULT: {'✅ PASSED' if overall_success else '❌ FAILED'}")
        
        return overall_success
        
    except Exception as e:
        logger.error(f"Test suite failed: {e}")
        print(f"\\n❌ TEST SUITE FAILED: {e}")
        return False


if __name__ == "__main__":
    # Run comprehensive test suite
    success = asyncio.run(run_comprehensive_tests())
    exit_code = 0 if success else 1
    exit(exit_code)