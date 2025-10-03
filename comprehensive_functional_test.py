#!/usr/bin/env python3
"""
Comprehensive Functional Test Suite
Tests all implemented features and systems
"""

import requests
import json
import time
import sys
from typing import Dict, List, Any
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ComprehensiveFunctionalTest:
    """Comprehensive functional test suite for all system features."""
    
    def __init__(self, base_url: str = "http://localhost:8004"):
        """Initialize the test suite."""
        self.base_url = base_url
        self.test_results = {
            "passed": 0,
            "failed": 0,
            "total": 0,
            "details": []
        }
        
    def log_test_result(self, test_name: str, success: bool, details: str = ""):
        """Log test result."""
        self.test_results["total"] += 1
        if success:
            self.test_results["passed"] += 1
            logger.info(f"✅ {test_name}: PASSED")
        else:
            self.test_results["failed"] += 1
            logger.error(f"❌ {test_name}: FAILED - {details}")
        
        self.test_results["details"].append({
            "test": test_name,
            "success": success,
            "details": details
        })
    
    def test_api_connection(self) -> bool:
        """Test basic API connection."""
        try:
            response = requests.get(f"{self.base_url}/api/system/health", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"API connection failed: {e}")
            return False
    
    def test_system_health(self):
        """Test system health endpoint."""
        try:
            response = requests.get(f"{self.base_url}/api/system/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                success = data.get("status") in ["healthy", "degraded"]
                self.log_test_result("System Health Check", success, f"Status: {data.get('status')}")
            else:
                self.log_test_result("System Health Check", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test_result("System Health Check", False, str(e))
    
    def test_voice_services(self):
        """Test voice services."""
        # Test voice health
        try:
            response = requests.get(f"{self.base_url}/api/voice/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                success = data.get("overall") == "healthy" or data.get("status") == "healthy"
                self.log_test_result("Voice Health Check", success, f"Overall: {data.get('overall')}, Status: {data.get('status')}")
            else:
                self.log_test_result("Voice Health Check", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test_result("Voice Health Check", False, str(e))
        
        # Test voice options
        try:
            response = requests.get(f"{self.base_url}/api/voice/options", timeout=5)
            if response.status_code == 200:
                data = response.json()
                success = "voices" in data and len(data["voices"]) > 0
                self.log_test_result("Voice Options", success, f"Available voices: {len(data.get('voices', []))}")
            else:
                self.log_test_result("Voice Options", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test_result("Voice Options", False, str(e))
    
    def test_enhanced_rag(self):
        """Test enhanced RAG system."""
        # Test RAG health
        try:
            response = requests.get(f"{self.base_url}/api/rag/enhanced/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                success = data.get("status") == "healthy"
                self.log_test_result("Enhanced RAG Health", success, f"Status: {data.get('status')}")
            else:
                self.log_test_result("Enhanced RAG Health", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test_result("Enhanced RAG Health", False, str(e))
        
        # Test RAG search
        try:
            payload = {"query_text": "test search", "top_k": 5}
            response = requests.post(f"{self.base_url}/api/rag/enhanced/search", 
                                   json=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                success = "results" in data
                self.log_test_result("Enhanced RAG Search", success, f"Results: {len(data.get('results', []))}")
            else:
                self.log_test_result("Enhanced RAG Search", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test_result("Enhanced RAG Search", False, str(e))
    
    def test_enhanced_mcp(self):
        """Test enhanced MCP tools."""
        # Test MCP health
        try:
            response = requests.get(f"{self.base_url}/api/mcp/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                success = data.get("status") == "healthy"
                self.log_test_result("Enhanced MCP Health", success, f"Status: {data.get('status')}")
            else:
                self.log_test_result("Enhanced MCP Health", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test_result("Enhanced MCP Health", False, str(e))
        
        # Test MCP tools
        try:
            response = requests.get(f"{self.base_url}/api/mcp/tools", timeout=5)
            if response.status_code == 200:
                data = response.json()
                success = "tools" in data and len(data["tools"]) > 0
                self.log_test_result("Enhanced MCP Tools", success, f"Available tools: {len(data.get('tools', []))}")
            else:
                self.log_test_result("Enhanced MCP Tools", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test_result("Enhanced MCP Tools", False, str(e))
    
    def test_self_healing(self):
        """Test self-healing system."""
        # Test healing health
        try:
            response = requests.get(f"{self.base_url}/api/healing/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                success = data.get("status") == "healthy"
                self.log_test_result("Self-Healing Health", success, f"Status: {data.get('status')}")
            else:
                self.log_test_result("Self-Healing Health", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test_result("Self-Healing Health", False, str(e))
        
        # Test healing stats
        try:
            response = requests.get(f"{self.base_url}/api/healing/stats", timeout=5)
            if response.status_code == 200:
                data = response.json()
                success = "total_healing_attempts" in data
                self.log_test_result("Self-Healing Stats", success, f"Attempts: {data.get('total_healing_attempts', 0)}")
            else:
                self.log_test_result("Self-Healing Stats", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test_result("Self-Healing Stats", False, str(e))
    
    def test_vision_api(self):
        """Test vision API."""
        try:
            response = requests.get(f"{self.base_url}/api/vision/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                success = data.get("status") == "healthy"
                self.log_test_result("Vision API Health", success, f"Status: {data.get('status')}")
            else:
                self.log_test_result("Vision API Health", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test_result("Vision API Health", False, str(e))
    
    def test_optimized_models(self):
        """Test optimized model API."""
        try:
            response = requests.get(f"{self.base_url}/api/model/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                success = True  # Any response is good
                self.log_test_result("Optimized Models Status", success, f"Model status available")
            else:
                self.log_test_result("Optimized Models Status", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test_result("Optimized Models Status", False, str(e))
    
    def test_mlx_processing(self):
        """Test MLX processing API."""
        try:
            response = requests.get(f"{self.base_url}/api/mlx/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                success = data.get("status") == "healthy"
                self.log_test_result("MLX Processing Health", success, f"Status: {data.get('status')}")
            else:
                self.log_test_result("MLX Processing Health", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test_result("MLX Processing Health", False, str(e))
    
    def test_chat_functionality(self):
        """Test chat functionality."""
        try:
            payload = {"message": "Hello, this is a test message"}
            response = requests.post(f"{self.base_url}/api/chat/", json=payload, timeout=15)
            if response.status_code == 200:
                data = response.json()
                success = "response" in data
                self.log_test_result("Chat Functionality", success, f"Response received: {len(data.get('response', ''))}")
            else:
                self.log_test_result("Chat Functionality", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test_result("Chat Functionality", False, str(e))
    
    def test_file_cleanup_system(self):
        """Test file cleanup system."""
        try:
            import subprocess
            result = subprocess.run(["python3", "scripts/maintenance/comprehensive_file_cleanup.py", "--test"], 
                                  capture_output=True, text=True, timeout=30)
            success = result.returncode == 0
            self.log_test_result("File Cleanup System", success, f"Exit code: {result.returncode}")
        except Exception as e:
            self.log_test_result("File Cleanup System", False, str(e))
    
    def run_all_tests(self):
        """Run all functional tests."""
        logger.info("🚀 Starting Comprehensive Functional Tests...")
        logger.info("=" * 60)
        
        # Test API connection first
        if not self.test_api_connection():
            logger.error("❌ API connection failed. Cannot proceed with tests.")
            return False
        
        logger.info("✅ API connection established")
        
        # Run all tests
        self.test_system_health()
        self.test_voice_services()
        self.test_enhanced_rag()
        self.test_enhanced_mcp()
        self.test_self_healing()
        self.test_vision_api()
        self.test_optimized_models()
        self.test_mlx_processing()
        self.test_chat_functionality()
        self.test_file_cleanup_system()
        
        # Print summary
        logger.info("=" * 60)
        logger.info("📊 TEST SUMMARY")
        logger.info(f"Total Tests: {self.test_results['total']}")
        logger.info(f"Passed: {self.test_results['passed']}")
        logger.info(f"Failed: {self.test_results['failed']}")
        logger.info(f"Success Rate: {(self.test_results['passed'] / self.test_results['total'] * 100):.1f}%")
        
        # Save results
        with open("functional_test_results.json", "w") as f:
            json.dump(self.test_results, f, indent=2)
        
        logger.info("📄 Results saved to functional_test_results.json")
        
        return self.test_results["failed"] == 0

if __name__ == "__main__":
    tester = ComprehensiveFunctionalTest()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
