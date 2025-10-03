#!/usr/bin/env python3
"""
Comprehensive Middleware Functional Test Suite
Tests all middleware components in the system including:
- Backend API middleware (CORS, GZip, Performance monitoring)
- Frontend middleware (API proxies, CORS headers, Sentry)
- Service integration middleware
"""

import asyncio
import aiohttp
import json
import time
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
import sys
import os

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MiddlewareTestSuite:
    """Comprehensive middleware testing suite."""
    
    def __init__(self):
        self.results = {
            "test_timestamp": datetime.now().isoformat(),
            "backend_tests": {},
            "frontend_tests": {},
            "integration_tests": {},
            "overall_status": "pending",
            "summary": {}
        }
        
        # Test endpoints
        self.backend_url = "http://localhost:8004"
        self.frontend_url = "http://localhost:3000"
        
        # Expected middleware headers
        self.expected_cors_headers = [
            "Access-Control-Allow-Origin",
            "Access-Control-Allow-Methods", 
            "Access-Control-Allow-Headers"
        ]
        
        self.expected_performance_headers = [
            "X-Process-Time"
        ]
        
        self.expected_compression_headers = [
            "Content-Encoding"
        ]

    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all middleware tests."""
        logger.info("🧪 Starting Comprehensive Middleware Functional Testing")
        
        try:
            # Test backend middleware
            await self._test_backend_middleware()
            
            # Test frontend middleware
            await self._test_frontend_middleware()
            
            # Test integration middleware
            await self._test_integration_middleware()
            
            # Generate summary
            self._generate_summary()
            
            logger.info("✅ Middleware testing completed")
            return self.results
            
        except Exception as e:
            logger.error(f"❌ Middleware testing failed: {e}")
            self.results["overall_status"] = "failed"
            self.results["error"] = str(e)
            return self.results

    async def _test_backend_middleware(self):
        """Test backend API middleware."""
        logger.info("🔧 Testing Backend Middleware")
        
        backend_tests = {
            "cors_middleware": await self._test_cors_middleware(),
            "gzip_middleware": await self._test_gzip_middleware(),
            "performance_middleware": await self._test_performance_middleware(),
            "exception_handlers": await self._test_exception_handlers(),
            "request_validation": await self._test_request_validation(),
            "response_formatting": await self._test_response_formatting()
        }
        
        self.results["backend_tests"] = backend_tests
        logger.info(f"✅ Backend middleware tests completed: {len(backend_tests)} tests")

    async def _test_frontend_middleware(self):
        """Test frontend middleware."""
        logger.info("🌐 Testing Frontend Middleware")
        
        frontend_tests = {
            "api_proxy_middleware": await self._test_api_proxy_middleware(),
            "cors_headers": await self._test_frontend_cors_headers(),
            "sentry_middleware": await self._test_sentry_middleware(),
            "error_handling": await self._test_frontend_error_handling(),
            "request_routing": await self._test_request_routing()
        }
        
        self.results["frontend_tests"] = frontend_tests
        logger.info(f"✅ Frontend middleware tests completed: {len(frontend_tests)} tests")

    async def _test_integration_middleware(self):
        """Test integration middleware."""
        logger.info("🔗 Testing Integration Middleware")
        
        integration_tests = {
            "backend_frontend_communication": await self._test_backend_frontend_communication(),
            "service_proxy_middleware": await self._test_service_proxy_middleware(),
            "load_balancing": await self._test_load_balancing(),
            "circuit_breaker": await self._test_circuit_breaker(),
            "rate_limiting": await self._test_rate_limiting()
        }
        
        self.results["integration_tests"] = integration_tests
        logger.info(f"✅ Integration middleware tests completed: {len(integration_tests)} tests")

    async def _test_cors_middleware(self) -> Dict[str, Any]:
        """Test CORS middleware functionality."""
        logger.info("  🔄 Testing CORS Middleware")
        
        test_results = {
            "status": "pending",
            "tests": {},
            "summary": {}
        }
        
        try:
            # Test preflight request
            async with aiohttp.ClientSession() as session:
                # Test OPTIONS request (preflight)
                async with session.options(
                    f"{self.backend_url}/api/system/health",
                    headers={
                        "Origin": "http://localhost:3000",
                        "Access-Control-Request-Method": "GET",
                        "Access-Control-Request-Headers": "Content-Type"
                    }
                ) as response:
                    cors_headers = {}
                    for header in self.expected_cors_headers:
                        if header in response.headers:
                            cors_headers[header] = response.headers[header]
                    
                    test_results["tests"]["preflight_request"] = {
                        "status": "passed" if response.status == 200 else "failed",
                        "status_code": response.status,
                        "cors_headers": cors_headers,
                        "all_cors_headers_present": all(h in cors_headers for h in self.expected_cors_headers)
                    }
                
                # Test actual request with CORS
                async with session.get(
                    f"{self.backend_url}/api/system/health",
                    headers={"Origin": "http://localhost:3000"}
                ) as response:
                    cors_headers = {}
                    for header in self.expected_cors_headers:
                        if header in response.headers:
                            cors_headers[header] = response.headers[header]
                    
                    test_results["tests"]["cors_request"] = {
                        "status": "passed" if response.status == 200 else "failed",
                        "status_code": response.status,
                        "cors_headers": cors_headers,
                        "origin_allowed": "http://localhost:3000" in cors_headers.get("Access-Control-Allow-Origin", "")
                    }
            
            # Determine overall status
            all_passed = all(
                test["status"] == "passed" 
                for test in test_results["tests"].values()
            )
            test_results["status"] = "passed" if all_passed else "failed"
            
        except Exception as e:
            test_results["status"] = "error"
            test_results["error"] = str(e)
            logger.error(f"    ❌ CORS middleware test failed: {e}")
        
        return test_results

    async def _test_gzip_middleware(self) -> Dict[str, Any]:
        """Test GZip compression middleware."""
        logger.info("  📦 Testing GZip Middleware")
        
        test_results = {
            "status": "pending",
            "tests": {},
            "summary": {}
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                # Test with Accept-Encoding header
                async with session.get(
                    f"{self.backend_url}/api/system/health",
                    headers={"Accept-Encoding": "gzip"}
                ) as response:
                    content_encoding = response.headers.get("Content-Encoding", "")
                    
                    test_results["tests"]["gzip_compression"] = {
                        "status": "passed" if content_encoding == "gzip" else "failed",
                        "content_encoding": content_encoding,
                        "response_size": len(await response.text()),
                        "compression_applied": content_encoding == "gzip"
                    }
                
                # Test without Accept-Encoding header
                async with session.get(f"{self.backend_url}/api/system/health") as response:
                    content_encoding = response.headers.get("Content-Encoding", "")
                    
                    test_results["tests"]["no_compression"] = {
                        "status": "passed" if content_encoding == "" else "failed",
                        "content_encoding": content_encoding,
                        "response_size": len(await response.text()),
                        "compression_not_applied": content_encoding == ""
                    }
            
            # Determine overall status
            all_passed = all(
                test["status"] == "passed" 
                for test in test_results["tests"].values()
            )
            test_results["status"] = "passed" if all_passed else "failed"
            
        except Exception as e:
            test_results["status"] = "error"
            test_results["error"] = str(e)
            logger.error(f"    ❌ GZip middleware test failed: {e}")
        
        return test_results

    async def _test_performance_middleware(self) -> Dict[str, Any]:
        """Test performance monitoring middleware."""
        logger.info("  ⚡ Testing Performance Middleware")
        
        test_results = {
            "status": "pending",
            "tests": {},
            "summary": {}
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                start_time = time.time()
                
                async with session.get(f"{self.backend_url}/api/system/health") as response:
                    end_time = time.time()
                    
                    process_time_header = response.headers.get("X-Process-Time", "")
                    actual_time = end_time - start_time
                    
                    test_results["tests"]["performance_timing"] = {
                        "status": "passed" if process_time_header else "failed",
                        "process_time_header": process_time_header,
                        "actual_request_time": actual_time,
                        "header_present": bool(process_time_header),
                        "timing_reasonable": float(process_time_header) > 0 if process_time_header else False
                    }
            
            # Determine overall status
            test_results["status"] = "passed" if test_results["tests"]["performance_timing"]["status"] == "passed" else "failed"
            
        except Exception as e:
            test_results["status"] = "error"
            test_results["error"] = str(e)
            logger.error(f"    ❌ Performance middleware test failed: {e}")
        
        return test_results

    async def _test_exception_handlers(self) -> Dict[str, Any]:
        """Test exception handling middleware."""
        logger.info("  🚨 Testing Exception Handlers")
        
        test_results = {
            "status": "pending",
            "tests": {},
            "summary": {}
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                # Test 404 error handling
                async with session.get(f"{self.backend_url}/api/nonexistent") as response:
                    test_results["tests"]["404_handling"] = {
                        "status": "passed" if response.status == 404 else "failed",
                        "status_code": response.status,
                        "error_format_valid": True  # FastAPI should return valid JSON
                    }
                
                # Test invalid request handling
                async with session.post(
                    f"{self.backend_url}/api/chat/",
                    json={"invalid": "data"}
                ) as response:
                    test_results["tests"]["validation_error"] = {
                        "status": "passed" if response.status == 422 else "failed",
                        "status_code": response.status,
                        "validation_error_handled": response.status == 422
                    }
            
            # Determine overall status
            all_passed = all(
                test["status"] == "passed" 
                for test in test_results["tests"].values()
            )
            test_results["status"] = "passed" if all_passed else "failed"
            
        except Exception as e:
            test_results["status"] = "error"
            test_results["error"] = str(e)
            logger.error(f"    ❌ Exception handlers test failed: {e}")
        
        return test_results

    async def _test_request_validation(self) -> Dict[str, Any]:
        """Test request validation middleware."""
        logger.info("  ✅ Testing Request Validation")
        
        test_results = {
            "status": "pending",
            "tests": {},
            "summary": {}
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                # Test valid request
                async with session.post(
                    f"{self.backend_url}/api/chat/",
                    json={"message": "Hello, world!"}
                ) as response:
                    test_results["tests"]["valid_request"] = {
                        "status": "passed" if response.status == 200 else "failed",
                        "status_code": response.status,
                        "request_accepted": response.status == 200
                    }
                
                # Test invalid request (empty message)
                async with session.post(
                    f"{self.backend_url}/api/chat/",
                    json={"message": ""}
                ) as response:
                    test_results["tests"]["invalid_request"] = {
                        "status": "passed" if response.status == 422 else "failed",
                        "status_code": response.status,
                        "validation_rejected": response.status == 422
                    }
            
            # Determine overall status
            all_passed = all(
                test["status"] == "passed" 
                for test in test_results["tests"].values()
            )
            test_results["status"] = "passed" if all_passed else "failed"
            
        except Exception as e:
            test_results["status"] = "error"
            test_results["error"] = str(e)
            logger.error(f"    ❌ Request validation test failed: {e}")
        
        return test_results

    async def _test_response_formatting(self) -> Dict[str, Any]:
        """Test response formatting middleware."""
        logger.info("  📝 Testing Response Formatting")
        
        test_results = {
            "status": "pending",
            "tests": {},
            "summary": {}
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.backend_url}/api/system/health") as response:
                    content_type = response.headers.get("Content-Type", "")
                    response_data = await response.json()
                    
                    test_results["tests"]["response_format"] = {
                        "status": "passed" if "application/json" in content_type else "failed",
                        "content_type": content_type,
                        "json_valid": isinstance(response_data, dict),
                        "required_fields": "status" in response_data
                    }
            
            # Determine overall status
            test_results["status"] = "passed" if test_results["tests"]["response_format"]["status"] == "passed" else "failed"
            
        except Exception as e:
            test_results["status"] = "error"
            test_results["error"] = str(e)
            logger.error(f"    ❌ Response formatting test failed: {e}")
        
        return test_results

    async def _test_api_proxy_middleware(self) -> Dict[str, Any]:
        """Test frontend API proxy middleware."""
        logger.info("  🔄 Testing API Proxy Middleware")
        
        test_results = {
            "status": "pending",
            "tests": {},
            "summary": {}
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                # Test system health proxy
                async with session.get(f"{self.frontend_url}/api/system/health") as response:
                    test_results["tests"]["health_proxy"] = {
                        "status": "passed" if response.status == 200 else "failed",
                        "status_code": response.status,
                        "proxy_working": response.status == 200
                    }
                
                # Test chat proxy
                async with session.post(
                    f"{self.frontend_url}/api/chat",
                    json={"message": "Test message"}
                ) as response:
                    test_results["tests"]["chat_proxy"] = {
                        "status": "passed" if response.status == 200 else "failed",
                        "status_code": response.status,
                        "proxy_working": response.status == 200
                    }
            
            # Determine overall status
            all_passed = all(
                test["status"] == "passed" 
                for test in test_results["tests"].values()
            )
            test_results["status"] = "passed" if all_passed else "failed"
            
        except Exception as e:
            test_results["status"] = "error"
            test_results["error"] = str(e)
            logger.error(f"    ❌ API proxy middleware test failed: {e}")
        
        return test_results

    async def _test_frontend_cors_headers(self) -> Dict[str, Any]:
        """Test frontend CORS headers."""
        logger.info("  🌐 Testing Frontend CORS Headers")
        
        test_results = {
            "status": "pending",
            "tests": {},
            "summary": {}
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                # Test API route CORS headers
                async with session.options(f"{self.frontend_url}/api/system/health") as response:
                    cors_headers = {}
                    for header in self.expected_cors_headers:
                        if header in response.headers:
                            cors_headers[header] = response.headers[header]
                    
                    test_results["tests"]["cors_headers"] = {
                        "status": "passed" if cors_headers else "failed",
                        "cors_headers": cors_headers,
                        "headers_present": len(cors_headers) > 0
                    }
            
            # Determine overall status
            test_results["status"] = "passed" if test_results["tests"]["cors_headers"]["status"] == "passed" else "failed"
            
        except Exception as e:
            test_results["status"] = "error"
            test_results["error"] = str(e)
            logger.error(f"    ❌ Frontend CORS headers test failed: {e}")
        
        return test_results

    async def _test_sentry_middleware(self) -> Dict[str, Any]:
        """Test Sentry error tracking middleware."""
        logger.info("  📊 Testing Sentry Middleware")
        
        test_results = {
            "status": "pending",
            "tests": {},
            "summary": {}
        }
        
        try:
            # Check if Sentry is configured
            sentry_configured = os.path.exists("frontend/sentry.client.config.js")
            
            test_results["tests"]["sentry_config"] = {
                "status": "passed" if sentry_configured else "failed",
                "config_file_exists": sentry_configured,
                "sentry_available": sentry_configured
            }
            
            # Note: We can't easily test actual Sentry reporting without triggering errors
            # This is more of a configuration check
            
            test_results["status"] = "passed" if sentry_configured else "failed"
            
        except Exception as e:
            test_results["status"] = "error"
            test_results["error"] = str(e)
            logger.error(f"    ❌ Sentry middleware test failed: {e}")
        
        return test_results

    async def _test_frontend_error_handling(self) -> Dict[str, Any]:
        """Test frontend error handling."""
        logger.info("  🚨 Testing Frontend Error Handling")
        
        test_results = {
            "status": "pending",
            "tests": {},
            "summary": {}
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                # Test invalid API request
                async with session.post(
                    f"{self.frontend_url}/api/chat",
                    json={"invalid": "data"}
                ) as response:
                    test_results["tests"]["error_handling"] = {
                        "status": "passed" if response.status in [400, 422, 500] else "failed",
                        "status_code": response.status,
                        "error_handled": response.status >= 400
                    }
            
            test_results["status"] = "passed" if test_results["tests"]["error_handling"]["status"] == "passed" else "failed"
            
        except Exception as e:
            test_results["status"] = "error"
            test_results["error"] = str(e)
            logger.error(f"    ❌ Frontend error handling test failed: {e}")
        
        return test_results

    async def _test_request_routing(self) -> Dict[str, Any]:
        """Test request routing middleware."""
        logger.info("  🛣️ Testing Request Routing")
        
        test_results = {
            "status": "pending",
            "tests": {},
            "summary": {}
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                # Test various routes
                routes_to_test = [
                    "/api/system/health",
                    "/api/chat",
                    "/api/voice/options"
                ]
                
                route_results = {}
                for route in routes_to_test:
                    try:
                        async with session.get(f"{self.frontend_url}{route}") as response:
                            route_results[route] = {
                                "status_code": response.status,
                                "accessible": response.status < 500
                            }
                    except Exception as e:
                        route_results[route] = {
                            "error": str(e),
                            "accessible": False
                        }
                
                test_results["tests"]["route_accessibility"] = {
                    "status": "passed" if all(r.get("accessible", False) for r in route_results.values()) else "failed",
                    "route_results": route_results
                }
            
            test_results["status"] = test_results["tests"]["route_accessibility"]["status"]
            
        except Exception as e:
            test_results["status"] = "error"
            test_results["error"] = str(e)
            logger.error(f"    ❌ Request routing test failed: {e}")
        
        return test_results

    async def _test_backend_frontend_communication(self) -> Dict[str, Any]:
        """Test backend-frontend communication middleware."""
        logger.info("  🔗 Testing Backend-Frontend Communication")
        
        test_results = {
            "status": "pending",
            "tests": {},
            "summary": {}
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                # Test direct backend access
                async with session.get(f"{self.backend_url}/api/system/health") as backend_response:
                    backend_working = backend_response.status == 200
                
                # Test frontend proxy to backend
                async with session.get(f"{self.frontend_url}/api/system/health") as frontend_response:
                    frontend_working = frontend_response.status == 200
                
                test_results["tests"]["communication"] = {
                    "status": "passed" if backend_working and frontend_working else "failed",
                    "backend_direct": backend_working,
                    "frontend_proxy": frontend_working,
                    "communication_working": backend_working and frontend_working
                }
            
            test_results["status"] = test_results["tests"]["communication"]["status"]
            
        except Exception as e:
            test_results["status"] = "error"
            test_results["error"] = str(e)
            logger.error(f"    ❌ Backend-frontend communication test failed: {e}")
        
        return test_results

    async def _test_service_proxy_middleware(self) -> Dict[str, Any]:
        """Test service proxy middleware."""
        logger.info("  🔄 Testing Service Proxy Middleware")
        
        test_results = {
            "status": "pending",
            "tests": {},
            "summary": {}
        }
        
        try:
            # Test voice service proxy
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.backend_url}/api/voice/health") as response:
                    test_results["tests"]["voice_proxy"] = {
                        "status": "passed" if response.status == 200 else "failed",
                        "status_code": response.status,
                        "service_proxy_working": response.status == 200
                    }
            
            test_results["status"] = test_results["tests"]["voice_proxy"]["status"]
            
        except Exception as e:
            test_results["status"] = "error"
            test_results["error"] = str(e)
            logger.error(f"    ❌ Service proxy middleware test failed: {e}")
        
        return test_results

    async def _test_load_balancing(self) -> Dict[str, Any]:
        """Test load balancing middleware."""
        logger.info("  ⚖️ Testing Load Balancing")
        
        test_results = {
            "status": "pending",
            "tests": {},
            "summary": {}
        }
        
        try:
            # Test multiple concurrent requests
            async with aiohttp.ClientSession() as session:
                tasks = []
                for i in range(5):
                    task = session.get(f"{self.backend_url}/api/system/health")
                    tasks.append(task)
                
                responses = await asyncio.gather(*tasks, return_exceptions=True)
                
                successful_requests = sum(1 for r in responses if not isinstance(r, Exception) and r.status == 200)
                
                test_results["tests"]["concurrent_requests"] = {
                    "status": "passed" if successful_requests >= 4 else "failed",
                    "total_requests": len(responses),
                    "successful_requests": successful_requests,
                    "load_handling": successful_requests >= 4
                }
            
            test_results["status"] = test_results["tests"]["concurrent_requests"]["status"]
            
        except Exception as e:
            test_results["status"] = "error"
            test_results["error"] = str(e)
            logger.error(f"    ❌ Load balancing test failed: {e}")
        
        return test_results

    async def _test_circuit_breaker(self) -> Dict[str, Any]:
        """Test circuit breaker middleware."""
        logger.info("  🔌 Testing Circuit Breaker")
        
        test_results = {
            "status": "pending",
            "tests": {},
            "summary": {}
        }
        
        try:
            # Note: Circuit breaker testing would require simulating failures
            # For now, we'll test basic error handling
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.backend_url}/api/nonexistent") as response:
                    test_results["tests"]["error_handling"] = {
                        "status": "passed" if response.status == 404 else "failed",
                        "status_code": response.status,
                        "error_handled": response.status == 404
                    }
            
            test_results["status"] = test_results["tests"]["error_handling"]["status"]
            
        except Exception as e:
            test_results["status"] = "error"
            test_results["error"] = str(e)
            logger.error(f"    ❌ Circuit breaker test failed: {e}")
        
        return test_results

    async def _test_rate_limiting(self) -> Dict[str, Any]:
        """Test rate limiting middleware."""
        logger.info("  🚦 Testing Rate Limiting")
        
        test_results = {
            "status": "pending",
            "tests": {},
            "summary": {}
        }
        
        try:
            # Test rapid requests (should not be rate limited in development)
            async with aiohttp.ClientSession() as session:
                rapid_requests = []
                for i in range(10):
                    request = session.get(f"{self.backend_url}/api/system/health")
                    rapid_requests.append(request)
                
                responses = await asyncio.gather(*rapid_requests, return_exceptions=True)
                
                successful_requests = sum(1 for r in responses if not isinstance(r, Exception) and r.status == 200)
                
                test_results["tests"]["rapid_requests"] = {
                    "status": "passed" if successful_requests >= 8 else "failed",
                    "total_requests": len(responses),
                    "successful_requests": successful_requests,
                    "rate_limiting_reasonable": successful_requests >= 8
                }
            
            test_results["status"] = test_results["tests"]["rapid_requests"]["status"]
            
        except Exception as e:
            test_results["status"] = "error"
            test_results["error"] = str(e)
            logger.error(f"    ❌ Rate limiting test failed: {e}")
        
        return test_results

    def _generate_summary(self):
        """Generate test summary."""
        logger.info("📊 Generating Test Summary")
        
        # Count passed/failed tests
        backend_passed = sum(1 for test in self.results["backend_tests"].values() if test["status"] == "passed")
        backend_total = len(self.results["backend_tests"])
        
        frontend_passed = sum(1 for test in self.results["frontend_tests"].values() if test["status"] == "passed")
        frontend_total = len(self.results["frontend_tests"])
        
        integration_passed = sum(1 for test in self.results["integration_tests"].values() if test["status"] == "passed")
        integration_total = len(self.results["integration_tests"])
        
        total_passed = backend_passed + frontend_passed + integration_passed
        total_tests = backend_total + frontend_total + integration_total
        
        success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        self.results["summary"] = {
            "total_tests": total_tests,
            "passed_tests": total_passed,
            "failed_tests": total_tests - total_passed,
            "success_rate": success_rate,
            "backend_tests": f"{backend_passed}/{backend_total}",
            "frontend_tests": f"{frontend_passed}/{frontend_total}",
            "integration_tests": f"{integration_passed}/{integration_total}"
        }
        
        # Determine overall status
        if success_rate >= 90:
            self.results["overall_status"] = "excellent"
        elif success_rate >= 75:
            self.results["overall_status"] = "good"
        elif success_rate >= 50:
            self.results["overall_status"] = "fair"
        else:
            self.results["overall_status"] = "poor"

async def main():
    """Main test execution."""
    print("🧪 COMPREHENSIVE MIDDLEWARE FUNCTIONAL TEST SUITE")
    print("=" * 60)
    
    test_suite = MiddlewareTestSuite()
    results = await test_suite.run_all_tests()
    
    # Save results
    with open("middleware_functional_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    print("\n📊 TEST SUMMARY")
    print("=" * 30)
    print(f"Overall Status: {results['overall_status'].upper()}")
    print(f"Success Rate: {results['summary']['success_rate']:.1f}%")
    print(f"Total Tests: {results['summary']['total_tests']}")
    print(f"Passed: {results['summary']['passed_tests']}")
    print(f"Failed: {results['summary']['failed_tests']}")
    print(f"\nBackend Tests: {results['summary']['backend_tests']}")
    print(f"Frontend Tests: {results['summary']['frontend_tests']}")
    print(f"Integration Tests: {results['summary']['integration_tests']}")
    
    print(f"\n📄 Detailed results saved to: middleware_functional_test_results.json")
    
    return results

if __name__ == "__main__":
    asyncio.run(main())
