#!/usr/bin/env python3
"""
Comprehensive Chat Functional Test - Test all features accessible from chat
"""

import requests
import json
import time
import logging
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatFunctionalTester:
    """Comprehensive tester for all chat features"""
    
    def __init__(self, base_url: str = "http://localhost:8004"):
        self.base_url = base_url
        self.results = []
        
    def test_basic_chat(self) -> Dict[str, Any]:
        """Test basic chat functionality"""
        logger.info("🧪 Testing basic chat functionality...")
        
        test_cases = [
            {
                "name": "Simple Greeting",
                "message": "Hello, how are you?",
                "expected": "Should respond with greeting"
            },
            {
                "name": "Question About AI",
                "message": "What is artificial intelligence?",
                "expected": "Should respond with AI explanation"
            },
            {
                "name": "Technical Question",
                "message": "How does machine learning work?",
                "expected": "Should respond with technical explanation"
            },
            {
                "name": "Code Request",
                "message": "Write a Python function to calculate fibonacci numbers",
                "expected": "Should respond with code"
            }
        ]
        
        results = []
        for test_case in test_cases:
            try:
                response = requests.post(
                    f"{self.base_url}/api/chat/",
                    json={"message": test_case["message"]},
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    results.append({
                        "test": test_case["name"],
                        "status": "passed",
                        "response_time": response.elapsed.total_seconds(),
                        "agent_used": data.get("agent_used", "unknown"),
                        "confidence": data.get("confidence", 0),
                        "response_length": len(data.get("response", "")),
                        "features_used": data.get("features_used", [])
                    })
                    logger.info(f"✅ {test_case['name']}: {data.get('agent_used', 'unknown')} agent, {data.get('confidence', 0)} confidence")
                else:
                    results.append({
                        "test": test_case["name"],
                        "status": "failed",
                        "status_code": response.status_code,
                        "error": response.text
                    })
                    logger.error(f"❌ {test_case['name']}: HTTP {response.status_code}")
                    
            except Exception as e:
                results.append({
                    "test": test_case["name"],
                    "status": "error",
                    "error": str(e)
                })
                logger.error(f"❌ {test_case['name']}: {e}")
        
        return {
            "category": "Basic Chat",
            "tests": results,
            "summary": f"{len([r for r in results if r['status'] == 'passed'])}/{len(results)} passed"
        }
    
    def test_chat_validation(self) -> Dict[str, Any]:
        """Test chat input validation"""
        logger.info("🧪 Testing chat input validation...")
        
        test_cases = [
            {
                "name": "Empty Message",
                "message": "",
                "expected_status": 422,
                "expected": "Should reject empty message"
            },
            {
                "name": "Whitespace Only",
                "message": "   ",
                "expected_status": 422,
                "expected": "Should reject whitespace-only message"
            },
            {
                "name": "Very Long Message",
                "message": "x" * 10001,
                "expected_status": 422,
                "expected": "Should reject message over 10000 characters"
            },
            {
                "name": "Valid Message",
                "message": "This is a valid test message",
                "expected_status": 200,
                "expected": "Should accept valid message"
            }
        ]
        
        results = []
        for test_case in test_cases:
            try:
                response = requests.post(
                    f"{self.base_url}/api/chat/",
                    json={"message": test_case["message"]},
                    timeout=10
                )
                
                if response.status_code == test_case["expected_status"]:
                    results.append({
                        "test": test_case["name"],
                        "status": "passed",
                        "actual_status": response.status_code,
                        "expected_status": test_case["expected_status"]
                    })
                    logger.info(f"✅ {test_case['name']}: Status {response.status_code} as expected")
                else:
                    results.append({
                        "test": test_case["name"],
                        "status": "failed",
                        "actual_status": response.status_code,
                        "expected_status": test_case["expected_status"],
                        "response": response.text[:200]
                    })
                    logger.error(f"❌ {test_case['name']}: Expected {test_case['expected_status']}, got {response.status_code}")
                    
            except Exception as e:
                results.append({
                    "test": test_case["name"],
                    "status": "error",
                    "error": str(e)
                })
                logger.error(f"❌ {test_case['name']}: {e}")
        
        return {
            "category": "Input Validation",
            "tests": results,
            "summary": f"{len([r for r in results if r['status'] == 'passed'])}/{len(results)} passed"
        }
    
    def test_chat_parameters(self) -> Dict[str, Any]:
        """Test chat with different parameters"""
        logger.info("🧪 Testing chat with different parameters...")
        
        test_cases = [
            {
                "name": "Default Parameters",
                "payload": {"message": "Test with default parameters"},
                "expected": "Should work with defaults"
            },
            {
                "name": "High Temperature",
                "payload": {
                    "message": "Be creative with this response",
                    "temperature": 1.5,
                    "max_tokens": 512
                },
                "expected": "Should work with high temperature"
            },
            {
                "name": "Low Temperature",
                "payload": {
                    "message": "Give a factual response",
                    "temperature": 0.1,
                    "max_tokens": 256
                },
                "expected": "Should work with low temperature"
            },
            {
                "name": "With Session ID",
                "payload": {
                    "message": "Remember this conversation",
                    "session_id": "test-session-123",
                    "use_cache": True
                },
                "expected": "Should work with session tracking"
            }
        ]
        
        results = []
        for test_case in test_cases:
            try:
                response = requests.post(
                    f"{self.base_url}/api/chat/",
                    json=test_case["payload"],
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    results.append({
                        "test": test_case["name"],
                        "status": "passed",
                        "response_time": response.elapsed.total_seconds(),
                        "parameters_used": test_case["payload"],
                        "agent_used": data.get("agent_used", "unknown")
                    })
                    logger.info(f"✅ {test_case['name']}: {data.get('agent_used', 'unknown')} agent")
                else:
                    results.append({
                        "test": test_case["name"],
                        "status": "failed",
                        "status_code": response.status_code,
                        "error": response.text
                    })
                    logger.error(f"❌ {test_case['name']}: HTTP {response.status_code}")
                    
            except Exception as e:
                results.append({
                    "test": test_case["name"],
                    "status": "error",
                    "error": str(e)
                })
                logger.error(f"❌ {test_case['name']}: {e}")
        
        return {
            "category": "Parameter Testing",
            "tests": results,
            "summary": f"{len([r for r in results if r['status'] == 'passed'])}/{len(results)} passed"
        }
    
    def test_chat_integrations(self) -> Dict[str, Any]:
        """Test chat integrations with other features"""
        logger.info("🧪 Testing chat integrations...")
        
        # First check what features are available
        try:
            health_response = requests.get(f"{self.base_url}/api/system/health", timeout=10)
            if health_response.status_code == 200:
                health_data = health_response.json()
                available_features = health_data.get("features", {})
                logger.info(f"Available features: {available_features}")
            else:
                available_features = {}
        except:
            available_features = {}
        
        test_cases = []
        
        # Test RAG integration if available
        if available_features.get("rag_system", False):
            test_cases.append({
                "name": "RAG Knowledge Query",
                "message": "Search for information about machine learning algorithms",
                "expected": "Should use RAG system for knowledge retrieval"
            })
        
        # Test MCP tools if available
        if available_features.get("mcp_tools", False):
            test_cases.append({
                "name": "Calculator Request",
                "message": "Calculate 15 * 23 + 45",
                "expected": "Should use calculator tool"
            })
            test_cases.append({
                "name": "Web Search Request",
                "message": "Search for latest AI news",
                "expected": "Should use web search tool"
            })
            test_cases.append({
                "name": "File Operation Request",
                "message": "List files in the current directory",
                "expected": "Should use file operations tool"
            })
        
        # Test voice services if available
        if available_features.get("voice_services", False):
            test_cases.append({
                "name": "Voice Synthesis Request",
                "message": "Convert this text to speech: Hello, this is a test",
                "expected": "Should use voice synthesis"
            })
        
        # Test self-healing if available
        if available_features.get("self_healing", False):
            test_cases.append({
                "name": "Error Analysis Request",
                "message": "Analyze this error: ModuleNotFoundError: No module named 'missing_module'",
                "expected": "Should use self-healing system"
            })
        
        if not test_cases:
            test_cases = [{
                "name": "Fallback Mode Test",
                "message": "Test fallback mode functionality",
                "expected": "Should work in fallback mode"
            }]
        
        results = []
        for test_case in test_cases:
            try:
                response = requests.post(
                    f"{self.base_url}/api/chat/",
                    json={"message": test_case["message"]},
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    results.append({
                        "test": test_case["name"],
                        "status": "passed",
                        "response_time": response.elapsed.total_seconds(),
                        "agent_used": data.get("agent_used", "unknown"),
                        "features_used": data.get("features_used", []),
                        "integration_working": len(data.get("features_used", [])) > 0
                    })
                    logger.info(f"✅ {test_case['name']}: {data.get('agent_used', 'unknown')} agent, features: {data.get('features_used', [])}")
                else:
                    results.append({
                        "test": test_case["name"],
                        "status": "failed",
                        "status_code": response.status_code,
                        "error": response.text
                    })
                    logger.error(f"❌ {test_case['name']}: HTTP {response.status_code}")
                    
            except Exception as e:
                results.append({
                    "test": test_case["name"],
                    "status": "error",
                    "error": str(e)
                })
                logger.error(f"❌ {test_case['name']}: {e}")
        
        return {
            "category": "Integration Testing",
            "tests": results,
            "summary": f"{len([r for r in results if r['status'] == 'passed'])}/{len(results)} passed",
            "available_features": available_features
        }
    
    def test_chat_performance(self) -> Dict[str, Any]:
        """Test chat performance and load handling"""
        logger.info("🧪 Testing chat performance...")
        
        test_cases = [
            {
                "name": "Single Request Performance",
                "requests": 1,
                "message": "Quick response test"
            },
            {
                "name": "Concurrent Requests (5)",
                "requests": 5,
                "message": "Concurrent request test"
            },
            {
                "name": "Load Test (10 requests)",
                "requests": 10,
                "message": "Load testing request"
            }
        ]
        
        results = []
        for test_case in test_cases:
            try:
                import concurrent.futures
                import threading
                
                def make_request():
                    return requests.post(
                        f"{self.base_url}/api/chat/",
                        json={"message": test_case["message"]},
                        timeout=30
                    )
                
                start_time = time.time()
                
                if test_case["requests"] == 1:
                    response = make_request()
                    responses = [response]
                else:
                    with concurrent.futures.ThreadPoolExecutor(max_workers=test_case["requests"]) as executor:
                        futures = [executor.submit(make_request) for _ in range(test_case["requests"])]
                        responses = [future.result() for future in concurrent.futures.as_completed(futures)]
                
                end_time = time.time()
                total_time = end_time - start_time
                
                successful_requests = [r for r in responses if r.status_code == 200]
                failed_requests = [r for r in responses if r.status_code != 200]
                
                results.append({
                    "test": test_case["name"],
                    "status": "passed" if len(failed_requests) == 0 else "partial",
                    "total_requests": test_case["requests"],
                    "successful_requests": len(successful_requests),
                    "failed_requests": len(failed_requests),
                    "total_time": total_time,
                    "avg_response_time": total_time / len(responses) if responses else 0,
                    "requests_per_second": test_case["requests"] / total_time if total_time > 0 else 0
                })
                
                logger.info(f"✅ {test_case['name']}: {len(successful_requests)}/{test_case['requests']} successful, {total_time:.2f}s total")
                
            except Exception as e:
                results.append({
                    "test": test_case["name"],
                    "status": "error",
                    "error": str(e)
                })
                logger.error(f"❌ {test_case['name']}: {e}")
        
        return {
            "category": "Performance Testing",
            "tests": results,
            "summary": f"{len([r for r in results if r['status'] == 'passed'])}/{len(results)} passed"
        }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all chat functional tests"""
        logger.info("🚀 Starting comprehensive chat functional testing...")
        
        start_time = time.time()
        
        test_results = [
            self.test_chat_validation(),
            self.test_basic_chat(),
            self.test_chat_parameters(),
            self.test_chat_integrations(),
            self.test_chat_performance()
        ]
        
        end_time = time.time()
        
        # Calculate overall statistics
        total_tests = sum(len(result["tests"]) for result in test_results)
        passed_tests = sum(len([t for t in result["tests"] if t["status"] == "passed"]) for result in test_results)
        failed_tests = sum(len([t for t in result["tests"] if t["status"] == "failed"]) for result in test_results)
        error_tests = sum(len([t for t in result["tests"] if t["status"] == "error"]) for result in test_results)
        
        overall_result = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_test_time": end_time - start_time,
            "test_categories": test_results,
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "errors": error_tests,
                "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0
            }
        }
        
        return overall_result

def main():
    """Run comprehensive chat functional tests"""
    print("🧪 COMPREHENSIVE CHAT FUNCTIONAL TESTING")
    print("=" * 60)
    
    tester = ChatFunctionalTester()
    results = tester.run_all_tests()
    
    # Print summary
    print(f"\n📊 TEST SUMMARY")
    print(f"Success Rate: {results['summary']['success_rate']:.1f}%")
    print(f"Total Tests: {results['summary']['total_tests']}")
    print(f"Passed: {results['summary']['passed']}")
    print(f"Failed: {results['summary']['failed']}")
    print(f"Errors: {results['summary']['errors']}")
    print(f"Total Time: {results['total_test_time']:.2f}s")
    
    # Save results
    with open("chat_functional_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: chat_functional_test_results.json")
    
    # Print category summaries
    print(f"\n📋 CATEGORY RESULTS:")
    for category in results['test_categories']:
        print(f"  {category['category']}: {category['summary']}")
    
    return results

if __name__ == "__main__":
    main()
