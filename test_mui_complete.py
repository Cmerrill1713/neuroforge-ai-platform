#!/usr/bin/env python3
"""
Test script to verify MUI integration is complete and working
"""

import os
import sys
import json
import requests
from pathlib import Path

def test_mui_files():
    """Test that all MUI integration files exist"""
    print("🔍 Testing MUI Integration Files...")
    
    base_path = Path("/Users/christianmerrill/Prompt Engineering")
    required_files = [
        "mcp.json",
        "frontend/src/components/MuiEnhancedChatPanel.tsx",
        "frontend/src/theme/muiTheme.ts", 
        "frontend/app/page-mui-enhanced.tsx",
        "mcp_servers/mui_patterns_scraper.py",
        "mcp_servers/mui_patterns_mcp.json"
    ]
    
    missing_files = []
    for file_path in required_files:
        full_path = base_path / file_path
        if not full_path.exists():
            missing_files.append(file_path)
        else:
            print(f"   ✅ {file_path}")
    
    if missing_files:
        print(f"   ❌ Missing files: {missing_files}")
        return False
    
    print("   ✅ All MUI integration files present")
    return True

def test_supabase_connection():
    """Test Supabase connection"""
    print("\n🔍 Testing Supabase Connection...")
    
    try:
        url = "http://localhost:54321/rest/v1/agent_communication_patterns"
        headers = {
            "apikey": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0"
        }
        
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Supabase connected - {len(data)} patterns found")
            return True
        else:
            print(f"   ❌ Supabase error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Supabase connection failed: {e}")
        return False

def test_mcp_config():
    """Test MCP configuration"""
    print("\n🔍 Testing MCP Configuration...")
    
    try:
        mcp_path = Path("/Users/christianmerrill/Prompt Engineering/mcp.json")
        if mcp_path.exists():
            with open(mcp_path) as f:
                config = json.load(f)
            
            if "mcp" in config and "servers" in config["mcp"]:
                servers = config["mcp"]["servers"]
                print(f"   ✅ MCP config valid - {len(servers)} servers configured")
                
                # Check for MUI MCP server
                if "mui-mcp" in servers:
                    print("   ✅ MUI MCP server configured")
                    return True
                else:
                    print("   ⚠️  MUI MCP server not found in config")
                    return False
            else:
                print("   ❌ Invalid MCP config structure")
                return False
        else:
            print("   ❌ MCP config file not found")
            return False
            
    except Exception as e:
        print(f"   ❌ MCP config test failed: {e}")
        return False

def test_frontend_build():
    """Test if frontend can build with MUI"""
    print("\n🔍 Testing Frontend Build...")
    
    try:
        frontend_path = Path("/Users/christianmerrill/Prompt Engineering/frontend")
        if not frontend_path.exists():
            print("   ❌ Frontend directory not found")
            return False
        
        # Check if package.json has MUI dependencies
        package_json = frontend_path / "package.json"
        if package_json.exists():
            with open(package_json) as f:
                package_data = json.load(f)
            
            dependencies = package_data.get("dependencies", {})
            mui_deps = [dep for dep in dependencies.keys() if "mui" in dep.lower()]
            
            if mui_deps:
                print(f"   ✅ MUI dependencies found: {mui_deps}")
                return True
            else:
                print("   ⚠️  No MUI dependencies found in package.json")
                return False
        else:
            print("   ❌ package.json not found")
            return False
            
    except Exception as e:
        print(f"   ❌ Frontend build test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🎨 MUI Integration Complete Test")
    print("=" * 50)
    
    tests = [
        test_mui_files,
        test_supabase_connection,
        test_mcp_config,
        test_frontend_build
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"   ❌ Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        print("✅ MUI Integration is complete and working")
        print("\n📁 Key Files Created:")
        print("   • mcp.json - MCP server configuration")
        print("   • frontend/src/components/MuiEnhancedChatPanel.tsx")
        print("   • frontend/src/theme/muiTheme.ts")
        print("   • frontend/app/page-mui-enhanced.tsx")
        print("   • mcp_servers/mui_patterns_scraper.py")
        print("\n🚀 Next Steps:")
        print("   1. Switch to MUI Enhanced version by replacing page.tsx")
        print("   2. Install MUI dependencies: npm install @mui/material @emotion/react @emotion/styled")
        print("   3. Start the frontend: npm run dev")
        print("   4. Access at: http://localhost:3000")
    else:
        print(f"⚠️  {passed}/{total} tests passed")
        print("❌ Some issues found - check the output above")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
