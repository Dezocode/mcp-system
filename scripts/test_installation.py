#!/usr/bin/env python3
"""
Test script to verify MCP System installation
"""

import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path

def run_command(cmd, cwd=None, timeout=30):
    """Run command and return result"""
    try:
        result = subprocess.run(
            cmd.split() if isinstance(cmd, str) else cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def test_prerequisites():
    """Test system prerequisites"""
    print("🔍 Testing prerequisites...")
    
    # Test Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        return False
    print("✅ Python version OK")
    
    # Test Git
    success, _, _ = run_command("git --version")
    if not success:
        print("❌ Git not found")
        return False
    print("✅ Git found")
    
    return True

def test_installation():
    """Test MCP System installation"""
    print("\n🚀 Testing installation...")
    
    # Run installer
    installer_path = Path(__file__).parent.parent / "install.sh"
    if not installer_path.exists():
        print("❌ Installer not found")
        return False
    
    success, stdout, stderr = run_command(f"bash {installer_path}", timeout=120)
    if not success:
        print(f"❌ Installation failed: {stderr}")
        return False
    print("✅ Installation completed")
    
    return True

def test_commands():
    """Test installed commands"""
    print("\n🔧 Testing commands...")
    
    # Set PATH
    home = Path.home()
    os.environ["PATH"] = f"{home}/bin:{os.environ.get('PATH', '')}"
    
    commands = [
        "mcp-universal --help",
        "mcp-init-project --help"
    ]
    
    for cmd in commands:
        success, _, stderr = run_command(cmd)
        if not success:
            print(f"❌ Command failed: {cmd} - {stderr}")
            return False
        print(f"✅ {cmd.split()[0]} OK")
    
    return True

def test_project_initialization():
    """Test project initialization"""
    print("\n📁 Testing project initialization...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        test_project = Path(temp_dir) / "test-project"
        test_project.mkdir()
        
        # Create a Node.js project
        package_json = test_project / "package.json"
        package_json.write_text('{"name": "test-project", "version": "1.0.0"}')
        
        # Test initialization
        success, stdout, stderr = run_command("mcp-init-project", cwd=test_project)
        if not success:
            print(f"❌ Project initialization failed: {stderr}")
            return False
        
        print("✅ Project initialization OK")
    
    return True

def test_server_creation():
    """Test server creation"""
    print("\n🏗️ Testing server creation...")
    
    # Test creating a server
    success, stdout, stderr = run_command(
        "mcp-universal create test-server --template python-fastmcp --port 8055"
    )
    
    if not success:
        print(f"❌ Server creation failed: {stderr}")
        return False
    
    # Check if server directory was created
    server_dir = Path.home() / "mcp-test-server"
    if not server_dir.exists():
        print("❌ Server directory not created")
        return False
    
    print("✅ Server creation OK")
    
    # Cleanup
    shutil.rmtree(server_dir, ignore_errors=True)
    
    return True

def test_claude_integration():
    """Test Claude integration"""
    print("\n🤖 Testing Claude integration...")
    
    # Test bridge status
    success, stdout, stderr = run_command("mcp-universal bridge status")
    if not success:
        print(f"❌ Bridge status check failed: {stderr}")
        return False
    
    print("✅ Claude bridge OK")
    return True

def test_upgrade_system():
    """Test upgrade system"""
    print("\n⚡ Testing upgrade system...")
    
    # Test listing modules
    success, stdout, stderr = run_command("mcp-universal upgrade list-modules")
    if not success:
        print(f"❌ Upgrade system test failed: {stderr}")
        return False
    
    print("✅ Upgrade system OK")
    return True

def cleanup():
    """Cleanup test artifacts"""
    print("\n🧹 Cleaning up...")
    
    # Remove test servers
    home = Path.home()
    for item in home.glob("mcp-test-*"):
        if item.is_dir():
            shutil.rmtree(item, ignore_errors=True)
    
    print("✅ Cleanup completed")

def main():
    """Main test function"""
    print("🧪 MCP System Installation Test")
    print("=" * 40)
    
    tests = [
        ("Prerequisites", test_prerequisites),
        ("Installation", test_installation),
        ("Commands", test_commands),
        ("Project Initialization", test_project_initialization),
        ("Server Creation", test_server_creation),
        ("Claude Integration", test_claude_integration),
        ("Upgrade System", test_upgrade_system)
    ]
    
    passed = 0
    total = len(tests)
    
    try:
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed += 1
                else:
                    print(f"\n💥 Test failed: {test_name}")
            except Exception as e:
                print(f"\n💥 Test error: {test_name} - {e}")
        
        print("\n" + "=" * 40)
        print(f"📊 Test Results: {passed}/{total} passed")
        
        if passed == total:
            print("🎉 All tests passed! MCP System is ready to use.")
            return 0
        else:
            print("❌ Some tests failed. Please check the installation.")
            return 1
            
    finally:
        cleanup()

if __name__ == "__main__":
    sys.exit(main())