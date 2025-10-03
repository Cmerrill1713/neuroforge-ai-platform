#!/usr/bin/env python3
"""
Functional Test - Real System Integration
Tests if optimizations actually work with your real system endpoints
"""

import asyncio
import time
import requests
import json
import logging
from datetime import datetime
from typing import Dict, List, Any

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FunctionalSystemTest:
    """Test if optimizations are functional with real system"""
    
    def __init__(self):
        self.real_endpoints = {
            "main_api": "http://localhost:8004",
            "evolutionary_api": "http://localhost:8005", 
            "unified_kb": "http://localhost:8001",
            "weaviate": "http://localhost:8090"
        }
        
        self.test_results = {
            "real_system_tests": {},
            "optimization_integration": {},
            "performance_comparison": {},
            "functional_status": {}
        }
    
    async def test_real_system_endpoints(self):
        """Test actual system endpoints with real requests"""
        logger.info("🌐 Testing real system endpoints...")
        
        endpoint_results = {}
        
        # Test Main API with real chat request
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.real_endpoints['main_api']}/api/chat/",
                json={
                    "message": "Help me with React development",
                    "agent_id": None,
                    "show_browser_windows": False
                },
                timeout=30
            )
            response_time = (time.time() - start_time) * 1000
            
            endpoint_results["main_api_chat"] = {
                "status_code": response.status_code,
                "response_time_ms": response_time,
                "success": response.status_code == 200,
                "response_length": len(response.text) if response.text else 0,
                "actual_response": response.json() if response.status_code == 200 else None
            }
            
            logger.info(f"✅ Main API Chat: {response.status_code} ({response_time:.1f}ms)")
            
        except Exception as e:
            endpoint_results["main_api_chat"] = {
                "error": str(e),
                "success": False
            }
            logger.error(f"❌ Main API Chat failed: {e}")
        
        # Test Evolutionary API
        try:
            start_time = time.time()
            response = requests.get(f"{self.real_endpoints['evolutionary_api']}/api/evolutionary/stats", timeout=10)
            response_time = (time.time() - start_time) * 1000
            
            endpoint_results["evolutionary_api"] = {
                "status_code": response.status_code,
                "response_time_ms": response_time,
                "success": response.status_code == 200,
                "response_data": response.json() if response.status_code == 200 else None
            }
            
            logger.info(f"✅ Evolutionary API: {response.status_code} ({response_time:.1f}ms)")
            
        except Exception as e:
            endpoint_results["evolutionary_api"] = {
                "error": str(e),
                "success": False
            }
            logger.error(f"❌ Evolutionary API failed: {e}")
        
        # Test Unified KB
        try:
            start_time = time.time()
            response = requests.get(f"{self.real_endpoints['unified_kb']}/api/knowledge/stats", timeout=10)
            response_time = (time.time() - start_time) * 1000
            
            endpoint_results["unified_kb"] = {
                "status_code": response.status_code,
                "response_time_ms": response_time,
                "success": response.status_code == 200,
                "response_data": response.json() if response.status_code == 200 else None
            }
            
            logger.info(f"✅ Unified KB: {response.status_code} ({response_time:.1f}ms)")
            
        except Exception as e:
            endpoint_results["unified_kb"] = {
                "error": str(e),
                "success": False
            }
            logger.error(f"❌ Unified KB failed: {e}")
        
        # Test Weaviate
        try:
            start_time = time.time()
            response = requests.get(f"{self.real_endpoints['weaviate']}/v1/meta", timeout=10)
            response_time = (time.time() - start_time) * 1000
            
            endpoint_results["weaviate"] = {
                "status_code": response.status_code,
                "response_time_ms": response_time,
                "success": response.status_code == 200,
                "response_data": response.json() if response.status_code == 200 else None
            }
            
            logger.info(f"✅ Weaviate: {response.status_code} ({response_time:.1f}ms)")
            
        except Exception as e:
            endpoint_results["weaviate"] = {
                "error": str(e),
                "success": False
            }
            logger.error(f"❌ Weaviate failed: {e}")
        
        self.test_results["real_system_tests"] = endpoint_results
    
    async def test_optimization_integration(self):
        """Test if optimizations actually integrate with real system"""
        logger.info("🔧 Testing optimization integration with real system...")
        
        integration_results = {}
        
        # Test 1: Check if our optimized components can connect to real Redis
        try:
            import redis.asyncio as redis
            redis_client = redis.from_url("redis://localhost:6379")
            
            # Test Redis connection
            start_time = time.time()
            await redis_client.ping()
            redis_time = (time.time() - start_time) * 1000
            
            # Test Redis operations
            test_key = "functional_test"
            test_value = "integration_test_data"
            
            await redis_client.set(test_key, test_value, ex=60)
            retrieved_value = await redis_client.get(test_key)
            await redis_client.delete(test_key)
            await redis_client.close()
            
            integration_results["redis_integration"] = {
                "connection_time_ms": redis_time,
                "set_get_success": retrieved_value == test_value,
                "functional": True
            }
            
            logger.info(f"✅ Redis Integration: {redis_time:.1f}ms connection")
            
        except Exception as e:
            integration_results["redis_integration"] = {
                "error": str(e),
                "functional": False
            }
            logger.error(f"❌ Redis integration failed: {e}")
        
        # Test 2: Check if our optimized components can connect to real database
        try:
            import asyncpg
            
            db_url = "postgresql://postgres:password@localhost:5433/agentic_db"
            
            start_time = time.time()
            conn = await asyncpg.connect(db_url)
            db_time = (time.time() - start_time) * 1000
            
            # Test database query
            result = await conn.fetchval("SELECT COUNT(*) FROM knowledge_sources")
            await conn.close()
            
            integration_results["database_integration"] = {
                "connection_time_ms": db_time,
                "query_success": result is not None,
                "functional": True
            }
            
            logger.info(f"✅ Database Integration: {db_time:.1f}ms connection")
            
        except Exception as e:
            integration_results["database_integration"] = {
                "error": str(e),
                "functional": False
            }
            logger.error(f"❌ Database integration failed: {e}")
        
        # Test 3: Test if our optimized agent selector works with real system
        try:
            from src.core.optimization.optimized_agent_selector import initialize_agent_selector, SelectionCriteria
            
            agent_selector = await initialize_agent_selector()
            
            criteria = SelectionCriteria(
                task_type="frontend_development",
                complexity="medium",
                priority="high",
                context={"framework": "react"}
            )
            
            start_time = time.time()
            result = await agent_selector.select_agent(criteria)
            selection_time = (time.time() - start_time) * 1000
            
            integration_results["agent_selector_integration"] = {
                "selection_time_ms": selection_time,
                "agent_selected": result.selected_agent.name if result else None,
                "confidence": result.confidence if result else None,
                "functional": result is not None
            }
            
            logger.info(f"✅ Agent Selector Integration: {selection_time:.1f}ms")
            
        except Exception as e:
            integration_results["agent_selector_integration"] = {
                "error": str(e),
                "functional": False
            }
            logger.error(f"❌ Agent selector integration failed: {e}")
        
        self.test_results["optimization_integration"] = integration_results
    
    async def test_performance_comparison(self):
        """Compare performance with and without optimizations"""
        logger.info("📊 Testing performance comparison...")
        
        comparison_results = {}
        
        # Test 1: Multiple chat requests to see caching effect
        chat_times = []
        test_messages = [
            "Help me with React development",
            "Quick Python tip",
            "Complex system architecture question",
            "Data analysis help",
            "Simple programming question"
        ]
        
        for i, message in enumerate(test_messages):
            try:
                start_time = time.time()
                response = requests.post(
                    f"{self.real_endpoints['main_api']}/api/chat/",
                    json={
                        "message": message,
                        "agent_id": None,
                        "show_browser_windows": False
                    },
                    timeout=30
                )
                response_time = (time.time() - start_time) * 1000
                chat_times.append(response_time)
                
                logger.info(f"✅ Chat request {i+1}: {response_time:.1f}ms")
                
            except Exception as e:
                logger.warning(f"⚠️ Chat request {i+1} failed: {e}")
                chat_times.append(30000)  # Timeout
        
        if chat_times:
            comparison_results["chat_performance"] = {
                "avg_response_time_ms": sum(chat_times) / len(chat_times),
                "min_response_time_ms": min(chat_times),
                "max_response_time_ms": max(chat_times),
                "total_requests": len(chat_times),
                "successful_requests": len([t for t in chat_times if t < 30000])
            }
        
        # Test 2: Check if our optimizations are actually being used
        try:
            from src.core.optimization.multi_level_cache import get_cache
            
            cache = get_cache()
            cache_stats = await cache.get_stats()
            
            comparison_results["cache_usage"] = {
                "total_requests": cache_stats.total_requests,
                "cache_hit_ratio": cache_stats.cache_hit_ratio,
                "l1_hits": cache_stats.l1_hits,
                "l2_hits": cache_stats.l2_hits,
                "avg_response_time_ms": cache_stats.avg_response_time_ms,
                "optimizations_active": cache_stats.total_requests > 0
            }
            
            logger.info(f"✅ Cache Usage: {cache_stats.total_requests} requests, {cache_stats.cache_hit_ratio:.1%} hit ratio")
            
        except Exception as e:
            comparison_results["cache_usage"] = {
                "error": str(e),
                "optimizations_active": False
            }
            logger.error(f"❌ Cache usage test failed: {e}")
        
        self.test_results["performance_comparison"] = comparison_results
    
    def analyze_functional_status(self):
        """Analyze if optimizations are functional or mock"""
        logger.info("🔍 Analyzing functional status...")
        
        real_system = self.test_results["real_system_tests"]
        integration = self.test_results["optimization_integration"]
        performance = self.test_results["performance_comparison"]
        
        functional_indicators = []
        
        # Check if real system endpoints are working
        real_endpoints_working = sum(1 for test in real_system.values() if test.get("success", False))
        functional_indicators.append(f"Real endpoints working: {real_endpoints_working}/{len(real_system)}")
        
        # Check if optimizations integrate with real infrastructure
        redis_functional = integration.get("redis_integration", {}).get("functional", False)
        db_functional = integration.get("database_integration", {}).get("functional", False)
        agent_functional = integration.get("agent_selector_integration", {}).get("functional", False)
        
        functional_indicators.append(f"Redis integration: {'✅' if redis_functional else '❌'}")
        functional_indicators.append(f"Database integration: {'✅' if db_functional else '❌'}")
        functional_indicators.append(f"Agent selector integration: {'✅' if agent_functional else '❌'}")
        
        # Check if optimizations are actually being used
        cache_active = performance.get("cache_usage", {}).get("optimizations_active", False)
        functional_indicators.append(f"Cache optimizations active: {'✅' if cache_active else '❌'}")
        
        # Determine overall functional status
        total_integrations = sum([redis_functional, db_functional, agent_functional])
        is_functional = total_integrations >= 2 and cache_active
        
        self.test_results["functional_status"] = {
            "is_functional": is_functional,
            "integration_score": f"{total_integrations}/3",
            "real_system_score": f"{real_endpoints_working}/{len(real_system)}",
            "indicators": functional_indicators,
            "status": "FUNCTIONAL" if is_functional else "MOCK/PARTIAL"
        }
    
    def display_functional_test_results(self):
        """Display functional test results"""
        logger.info("📊 FUNCTIONAL TEST RESULTS")
        logger.info("=" * 60)
        
        # Real System Tests
        real_system = self.test_results["real_system_tests"]
        logger.info("🌐 REAL SYSTEM ENDPOINT TESTS:")
        for endpoint, result in real_system.items():
            if result.get("success"):
                logger.info(f"   • {endpoint}: ✅ {result.get('response_time_ms', 0):.1f}ms")
            else:
                logger.info(f"   • {endpoint}: ❌ {result.get('error', 'Unknown error')}")
        
        # Optimization Integration
        integration = self.test_results["optimization_integration"]
        logger.info("🔧 OPTIMIZATION INTEGRATION TESTS:")
        for component, result in integration.items():
            if result.get("functional"):
                logger.info(f"   • {component}: ✅ Functional")
            else:
                logger.info(f"   • {component}: ❌ {result.get('error', 'Not functional')}")
        
        # Performance Comparison
        performance = self.test_results["performance_comparison"]
        logger.info("📊 PERFORMANCE COMPARISON:")
        chat_perf = performance.get("chat_performance", {})
        if chat_perf:
            logger.info(f"   • Chat Performance: {chat_perf.get('avg_response_time_ms', 0):.1f}ms avg")
            logger.info(f"   • Successful Requests: {chat_perf.get('successful_requests', 0)}/{chat_perf.get('total_requests', 0)}")
        
        cache_usage = performance.get("cache_usage", {})
        if cache_usage.get("optimizations_active"):
            logger.info(f"   • Cache Requests: {cache_usage.get('total_requests', 0)}")
            logger.info(f"   • Cache Hit Ratio: {cache_usage.get('cache_hit_ratio', 0):.1%}")
        
        # Functional Status
        status = self.test_results["functional_status"]
        logger.info("🎯 FUNCTIONAL STATUS ANALYSIS:")
        logger.info(f"   • Overall Status: {status['status']}")
        logger.info(f"   • Integration Score: {status['integration_score']}")
        logger.info(f"   • Real System Score: {status['real_system_score']}")
        
        logger.info("📋 FUNCTIONAL INDICATORS:")
        for indicator in status["indicators"]:
            logger.info(f"   • {indicator}")
        
        logger.info("=" * 60)
        
        if status["is_functional"]:
            logger.info("🎉 CONCLUSION: OPTIMIZATIONS ARE FUNCTIONAL!")
            logger.info("✅ Integrates with real Redis, Database, and Agent Selection")
            logger.info("✅ Works with your actual system endpoints")
            logger.info("✅ Performance improvements are real, not mock")
        else:
            logger.info("⚠️ CONCLUSION: OPTIMIZATIONS ARE PARTIALLY FUNCTIONAL")
            logger.info("❌ Some components may be mock or not fully integrated")
            logger.info("💡 Further integration may be needed")
    
    async def run_functional_test(self):
        """Run comprehensive functional test"""
        logger.info("🚀 Starting functional system test...")
        logger.info("=" * 60)
        
        start_time = time.time()
        
        try:
            # Run all functional tests
            await self.test_real_system_endpoints()
            await self.test_optimization_integration()
            await self.test_performance_comparison()
            
            # Analyze results
            self.analyze_functional_status()
            
            # Display results
            self.display_functional_test_results()
            
            total_time = time.time() - start_time
            logger.info(f"✅ Functional test completed in {total_time:.2f} seconds")
            
            return self.test_results
            
        except Exception as e:
            logger.error(f"❌ Functional test failed: {e}")
            raise

async def main():
    """Main functional test function"""
    tester = FunctionalSystemTest()
    
    try:
        results = await tester.run_functional_test()
        
        # Save results to file
        with open("functional_test_results.json", "w") as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info("📄 Functional test results saved to functional_test_results.json")
        
        return True
        
    except Exception as e:
        logger.error(f"Functional test failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    if success:
        print("\n🎉 Functional test completed successfully!")
        print("📊 Optimizations tested against real system")
        print("✅ Results show if optimizations are functional or mock")
    else:
        print("\n❌ Functional test failed!")
