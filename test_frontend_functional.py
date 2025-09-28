#!/usr/bin/env python3
"""
Frontend Functional Testing and Debugging
Comprehensive test suite for the completed frontend
"""

import asyncio
import json
import subprocess
import sys
import time
import requests
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FrontendTester:
    """Comprehensive frontend testing suite."""
    
    def __init__(self):
        self.base_url = "http://localhost:3000"
        self.api_url = "http://127.0.0.1:8000"
        self.test_results = {
            "frontend": {"status": "unknown", "details": []},
            "backend": {"status": "unknown", "details": []},
            "components": {"status": "unknown", "details": []},
            "api": {"status": "unknown", "details": []},
            "mcp": {"status": "unknown", "details": []},
            "performance": {"status": "unknown", "details": []}
        }
    
    async def run_all_tests(self):
        """Run all functional tests."""
        print("🧪 Frontend Functional Testing & Debugging")
        print("=" * 60)
        
        # Test 1: Frontend Server
        await self.test_frontend_server()
        
        # Test 2: Backend API
        await self.test_backend_api()
        
        # Test 3: Component Functionality
        await self.test_component_functionality()
        
        # Test 4: API Integration
        await self.test_api_integration()
        
        # Test 5: MCP Tools
        await self.test_mcp_tools()
        
        # Test 6: Performance
        await self.test_performance()
        
        # Generate Report
        self.generate_report()
    
    async def test_frontend_server(self):
        """Test frontend server availability and basic functionality."""
        print("\n🌐 Testing Frontend Server...")
        
        try:
            # Test basic connectivity
            response = requests.get(self.base_url, timeout=10)
            if response.status_code == 200:
                self.test_results["frontend"]["status"] = "pass"
                self.test_results["frontend"]["details"].append("✅ Frontend server responding")
                
                # Check for key content
                content = response.text
                if "AI Studio 2025" in content:
                    self.test_results["frontend"]["details"].append("✅ AI Studio 2025 content found")
                else:
                    self.test_results["frontend"]["details"].append("⚠️ AI Studio 2025 content not found")
                
                if "Material-UI" in content or "MUI" in content:
                    self.test_results["frontend"]["details"].append("✅ Material-UI integration detected")
                else:
                    self.test_results["frontend"]["details"].append("⚠️ Material-UI integration not detected")
                
                # Check for React/Next.js
                if "React" in content or "Next.js" in content:
                    self.test_results["frontend"]["details"].append("✅ React/Next.js framework detected")
                else:
                    self.test_results["frontend"]["details"].append("⚠️ React/Next.js framework not detected")
                
            else:
                self.test_results["frontend"]["status"] = "fail"
                self.test_results["frontend"]["details"].append(f"❌ Frontend server returned {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            self.test_results["frontend"]["status"] = "fail"
            self.test_results["frontend"]["details"].append("❌ Frontend server not accessible")
            self.test_results["frontend"]["details"].append("💡 Try: cd frontend && npm run dev")
            
        except Exception as e:
            self.test_results["frontend"]["status"] = "fail"
            self.test_results["frontend"]["details"].append(f"❌ Frontend test error: {e}")
    
    async def test_backend_api(self):
        """Test backend API availability and functionality."""
        print("\n🔧 Testing Backend API...")
        
        try:
            # Test basic connectivity
            response = requests.get(f"{self.api_url}/status", timeout=10)
            if response.status_code == 200:
                self.test_results["backend"]["status"] = "pass"
                self.test_results["backend"]["details"].append("✅ Backend API responding")
                
                # Test models endpoint
                models_response = requests.get(f"{self.api_url}/models", timeout=10)
                if models_response.status_code == 200:
                    models_data = models_response.json()
                    self.test_results["backend"]["details"].append(f"✅ Models endpoint working ({len(models_data)} models)")
                else:
                    self.test_results["backend"]["details"].append("⚠️ Models endpoint not responding")
                
                # Test chat endpoint
                chat_payload = {
                    "message": "Hello, this is a test message",
                    "model": "qwen2.5:7b",
                    "stream": False
                }
                chat_response = requests.post(f"{self.api_url}/chat", json=chat_payload, timeout=30)
                if chat_response.status_code == 200:
                    self.test_results["backend"]["details"].append("✅ Chat endpoint working")
                else:
                    self.test_results["backend"]["details"].append("⚠️ Chat endpoint not responding")
                
            else:
                self.test_results["backend"]["status"] = "fail"
                self.test_results["backend"]["details"].append(f"❌ Backend API returned {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            self.test_results["backend"]["status"] = "fail"
            self.test_results["backend"]["details"].append("❌ Backend API not accessible")
            self.test_results["backend"]["details"].append("💡 Try: python3 -m uvicorn src.main:app --reload --port 8000")
            
        except Exception as e:
            self.test_results["backend"]["status"] = "fail"
            self.test_results["backend"]["details"].append(f"❌ Backend test error: {e}")
    
    async def test_component_functionality(self):
        """Test frontend component functionality."""
        print("\n🧩 Testing Component Functionality...")
        
        # Check if component files exist
        component_files = [
            "frontend/src/components/AdvancedChatFeatures.tsx",
            "frontend/src/components/VoiceIntegration.tsx",
            "frontend/src/components/RealTimeCollaboration.tsx",
            "frontend/src/components/PerformanceMonitor.tsx",
            "frontend/src/components/MuiEnhancedChatPanel.tsx",
            "frontend/src/components/CodeEditor.tsx",
            "frontend/src/components/LearningDashboard.tsx",
            "frontend/src/components/MultimodalPanel.tsx"
        ]
        
        existing_components = []
        missing_components = []
        
        for component_file in component_files:
            if Path(component_file).exists():
                existing_components.append(component_file)
            else:
                missing_components.append(component_file)
        
        if len(existing_components) == len(component_files):
            self.test_results["components"]["status"] = "pass"
            self.test_results["components"]["details"].append(f"✅ All {len(existing_components)} components exist")
        else:
            self.test_results["components"]["status"] = "partial"
            self.test_results["components"]["details"].append(f"⚠️ {len(existing_components)}/{len(component_files)} components exist")
        
        # Check for Material-UI imports
        for component_file in existing_components:
            try:
                with open(component_file, 'r') as f:
                    content = f.read()
                    if "@mui/material" in content:
                        self.test_results["components"]["details"].append(f"✅ {Path(component_file).name} uses Material-UI")
                    else:
                        self.test_results["components"]["details"].append(f"⚠️ {Path(component_file).name} may not use Material-UI")
            except Exception as e:
                self.test_results["components"]["details"].append(f"❌ Error reading {component_file}: {e}")
        
        # Check main page integration
        main_page = "frontend/app/page.tsx"
        if Path(main_page).exists():
            try:
                with open(main_page, 'r') as f:
                    content = f.read()
                    if "AdvancedChatFeatures" in content:
                        self.test_results["components"]["details"].append("✅ AdvancedChatFeatures integrated in main page")
                    if "VoiceIntegration" in content:
                        self.test_results["components"]["details"].append("✅ VoiceIntegration integrated in main page")
                    if "RealTimeCollaboration" in content:
                        self.test_results["components"]["details"].append("✅ RealTimeCollaboration integrated in main page")
                    if "PerformanceMonitor" in content:
                        self.test_results["components"]["details"].append("✅ PerformanceMonitor integrated in main page")
            except Exception as e:
                self.test_results["components"]["details"].append(f"❌ Error reading main page: {e}")
    
    async def test_api_integration(self):
        """Test API integration between frontend and backend."""
        print("\n🔗 Testing API Integration...")
        
        try:
            # Test if frontend can reach backend
            response = requests.get(f"{self.base_url}/api/health", timeout=10)
            if response.status_code == 200:
                self.test_results["api"]["status"] = "pass"
                self.test_results["api"]["details"].append("✅ Frontend API health check working")
            else:
                self.test_results["api"]["status"] = "partial"
                self.test_results["api"]["details"].append("⚠️ Frontend API health check not responding")
                
        except requests.exceptions.ConnectionError:
            self.test_results["api"]["status"] = "partial"
            self.test_results["api"]["details"].append("⚠️ Frontend API health check not accessible")
        
        # Check API client configuration
        api_client = "frontend/src/lib/api.ts"
        if Path(api_client).exists():
            try:
                with open(api_client, 'r') as f:
                    content = f.read()
                    if "API_BASE_URL" in content:
                        self.test_results["api"]["details"].append("✅ API client configuration found")
                    if "sendMessage" in content:
                        self.test_results["api"]["details"].append("✅ Chat API method found")
                    if "getModels" in content:
                        self.test_results["api"]["details"].append("✅ Models API method found")
                    if "WebSocket" in content:
                        self.test_results["api"]["details"].append("✅ WebSocket integration found")
            except Exception as e:
                self.test_results["api"]["details"].append(f"❌ Error reading API client: {e}")
    
    async def test_mcp_tools(self):
        """Test MCP tools functionality."""
        print("\n🔧 Testing MCP Tools...")
        
        # Test MCP configuration
        mcp_config = "mcp.json"
        if Path(mcp_config).exists():
            try:
                with open(mcp_config, 'r') as f:
                    config = json.load(f)
                    if "mui-mcp" in config.get("mcp", {}).get("servers", {}):
                        self.test_results["mcp"]["details"].append("✅ MUI MCP server configured")
                    if "docker-mcp" in config.get("mcp", {}).get("servers", {}):
                        self.test_results["mcp"]["details"].append("✅ Docker MCP server configured")
                    
                    self.test_results["mcp"]["status"] = "pass"
            except Exception as e:
                self.test_results["mcp"]["status"] = "fail"
                self.test_results["mcp"]["details"].append(f"❌ Error reading MCP config: {e}")
        else:
            self.test_results["mcp"]["status"] = "fail"
            self.test_results["mcp"]["details"].append("❌ MCP configuration not found")
        
        # Test MCP server files
        mcp_servers = [
            "mcp_docker_server.py",
            "test_docker_mcp.py",
            "test_mui_mcp_official.py"
        ]
        
        for server_file in mcp_servers:
            if Path(server_file).exists():
                self.test_results["mcp"]["details"].append(f"✅ {server_file} exists")
            else:
                self.test_results["mcp"]["details"].append(f"⚠️ {server_file} not found")
    
    async def test_performance(self):
        """Test performance and optimization."""
        print("\n⚡ Testing Performance...")
        
        try:
            # Test frontend load time
            start_time = time.time()
            response = requests.get(self.base_url, timeout=10)
            load_time = (time.time() - start_time) * 1000
            
            if load_time < 1000:  # Less than 1 second
                self.test_results["performance"]["status"] = "pass"
                self.test_results["performance"]["details"].append(f"✅ Frontend load time: {load_time:.0f}ms (excellent)")
            elif load_time < 3000:  # Less than 3 seconds
                self.test_results["performance"]["status"] = "partial"
                self.test_results["performance"]["details"].append(f"⚠️ Frontend load time: {load_time:.0f}ms (acceptable)")
            else:
                self.test_results["performance"]["status"] = "fail"
                self.test_results["performance"]["details"].append(f"❌ Frontend load time: {load_time:.0f}ms (slow)")
            
            # Test backend response time
            start_time = time.time()
            response = requests.get(f"{self.api_url}/status", timeout=10)
            api_time = (time.time() - start_time) * 1000
            
            if api_time < 500:  # Less than 500ms
                self.test_results["performance"]["details"].append(f"✅ Backend response time: {api_time:.0f}ms (excellent)")
            elif api_time < 1000:  # Less than 1 second
                self.test_results["performance"]["details"].append(f"⚠️ Backend response time: {api_time:.0f}ms (acceptable)")
            else:
                self.test_results["performance"]["details"].append(f"❌ Backend response time: {api_time:.0f}ms (slow)")
                
        except Exception as e:
            self.test_results["performance"]["status"] = "fail"
            self.test_results["performance"]["details"].append(f"❌ Performance test error: {e}")
    
    def generate_report(self):
        """Generate comprehensive test report."""
        print("\n" + "=" * 60)
        print("📊 FUNCTIONAL TEST REPORT")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result["status"] == "pass")
        partial_tests = sum(1 for result in self.test_results.values() if result["status"] == "partial")
        failed_tests = sum(1 for result in self.test_results.values() if result["status"] == "fail")
        
        print(f"\n📈 Overall Status: {passed_tests}/{total_tests} tests passed")
        print(f"   ✅ Passed: {passed_tests}")
        print(f"   ⚠️ Partial: {partial_tests}")
        print(f"   ❌ Failed: {failed_tests}")
        
        # Detailed results
        for test_name, result in self.test_results.items():
            status_icon = "✅" if result["status"] == "pass" else "⚠️" if result["status"] == "partial" else "❌"
            print(f"\n{status_icon} {test_name.upper()}: {result['status'].upper()}")
            
            for detail in result["details"]:
                print(f"   {detail}")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        
        if self.test_results["frontend"]["status"] != "pass":
            print("   • Start frontend server: cd frontend && npm run dev")
        
        if self.test_results["backend"]["status"] != "pass":
            print("   • Start backend server: python3 -m uvicorn src.main:app --reload --port 8000")
        
        if self.test_results["components"]["status"] != "pass":
            print("   • Check component files and Material-UI imports")
        
        if self.test_results["api"]["status"] != "pass":
            print("   • Verify API client configuration and endpoints")
        
        if self.test_results["mcp"]["status"] != "pass":
            print("   • Check MCP configuration and server files")
        
        if self.test_results["performance"]["status"] != "pass":
            print("   • Optimize performance and check server resources")
        
        # Success message
        if passed_tests == total_tests:
            print(f"\n🎉 ALL TESTS PASSED! Frontend is fully functional.")
        elif passed_tests + partial_tests == total_tests:
            print(f"\n✅ MOSTLY FUNCTIONAL! Minor issues to address.")
        else:
            print(f"\n⚠️ ISSUES DETECTED! Please address failed tests.")
        
        print(f"\n🕒 Test completed at: {time.strftime('%Y-%m-%d %H:%M:%S')}")

async def main():
    """Main test runner."""
    tester = FrontendTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
