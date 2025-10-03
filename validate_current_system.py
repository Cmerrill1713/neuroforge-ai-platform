#!/usr/bin/env python3
"""
Current System Performance Validation
Comprehensive analysis of existing system performance before implementing optimizations
"""

import asyncio
import time
import json
import logging
import requests
import statistics
from datetime import datetime
from typing import Dict, List, Any, Optional
import psutil
import os

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SystemPerformanceValidator:
    """Validates current system performance to establish accurate baseline"""
    
    def __init__(self):
        self.baseline_results = {
            "system_info": {},
            "api_endpoints": {},
            "database_performance": {},
            "cache_performance": {},
            "agent_selection": {},
            "overall_system": {},
            "bottlenecks": [],
            "recommendations": []
        }
        
        # System endpoints to test
        self.endpoints = {
            "main_api": "http://localhost:8004",
            "evolutionary_api": "http://localhost:8005", 
            "unified_kb": "http://localhost:8001",
            "weaviate": "http://localhost:8090",
            "redis": "redis://localhost:6379"
        }
    
    async def validate_system_info(self):
        """Validate system resources and configuration"""
        logger.info("🔍 Validating system information...")
        
        try:
            # System resources
            cpu_count = psutil.cpu_count()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Docker containers
            docker_containers = await self._get_docker_containers()
            
            self.baseline_results["system_info"] = {
                "cpu_cores": cpu_count,
                "total_memory_gb": round(memory.total / (1024**3), 2),
                "available_memory_gb": round(memory.available / (1024**3), 2),
                "memory_usage_percent": memory.percent,
                "disk_total_gb": round(disk.total / (1024**3), 2),
                "disk_used_gb": round(disk.used / (1024**3), 2),
                "disk_usage_percent": round((disk.used / disk.total) * 100, 2),
                "docker_containers": docker_containers,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"✅ System info validated - {cpu_count} cores, {memory.percent:.1f}% memory used")
            
        except Exception as e:
            logger.error(f"❌ System info validation failed: {e}")
            self.baseline_results["system_info"]["error"] = str(e)
    
    async def _get_docker_containers(self) -> List[Dict[str, str]]:
        """Get running Docker containers"""
        try:
            import subprocess
            result = subprocess.run(
                ["docker", "ps", "--format", "{{.Names}}|{{.Status}}|{{.Ports}}"],
                capture_output=True, text=True, timeout=10
            )
            
            containers = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split('|')
                    if len(parts) >= 3:
                        containers.append({
                            "name": parts[0],
                            "status": parts[1],
                            "ports": parts[2]
                        })
            
            return containers
            
        except Exception as e:
            logger.warning(f"Could not get Docker containers: {e}")
            return []
    
    async def validate_api_endpoints(self):
        """Test all API endpoints for availability and performance"""
        logger.info("🌐 Validating API endpoints...")
        
        endpoint_results = {}
        
        for name, url in self.endpoints.items():
            if name == "redis":
                continue  # Skip Redis for now
                
            try:
                start_time = time.time()
                
                if name == "weaviate":
                    # Test Weaviate health endpoint
                    response = requests.get(f"{url}/v1/meta", timeout=10)
                else:
                    # Test standard health/root endpoint
                    response = requests.get(f"{url}/", timeout=10)
                
                response_time = (time.time() - start_time) * 1000
                
                endpoint_results[name] = {
                    "url": url,
                    "status_code": response.status_code,
                    "response_time_ms": response_time,
                    "available": response.status_code < 500,
                    "error": None
                }
                
                logger.info(f"✅ {name}: {response.status_code} ({response_time:.1f}ms)")
                
            except Exception as e:
                endpoint_results[name] = {
                    "url": url,
                    "status_code": None,
                    "response_time_ms": None,
                    "available": False,
                    "error": str(e)
                }
                logger.warning(f"⚠️ {name}: {e}")
        
        self.baseline_results["api_endpoints"] = endpoint_results
    
    async def validate_database_performance(self):
        """Test database performance"""
        logger.info("🗄️ Validating database performance...")
        
        try:
            # Test PostgreSQL connection
            import asyncpg
            
            db_url = "postgresql://postgres:password@localhost:5433/agentic_db"
            
            # Test connection time
            start_time = time.time()
            conn = await asyncpg.connect(db_url)
            connection_time = (time.time() - start_time) * 1000
            
            # Test simple query
            start_time = time.time()
            result = await conn.fetchval("SELECT 1")
            query_time = (time.time() - start_time) * 1000
            
            # Test table existence and counts
            tables_info = {}
            try:
                tables = await conn.fetch("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """)
                
                for table in tables:
                    table_name = table['table_name']
                    try:
                        count_result = await conn.fetchval(f"SELECT COUNT(*) FROM {table_name}")
                        tables_info[table_name] = count_result
                    except Exception as e:
                        tables_info[table_name] = f"Error: {e}"
                        
            except Exception as e:
                tables_info["error"] = str(e)
            
            await conn.close()
            
            self.baseline_results["database_performance"] = {
                "connection_time_ms": connection_time,
                "simple_query_time_ms": query_time,
                "tables": tables_info,
                "available": True,
                "error": None
            }
            
            logger.info(f"✅ Database: {connection_time:.1f}ms connection, {query_time:.1f}ms query")
            
        except Exception as e:
            self.baseline_results["database_performance"] = {
                "available": False,
                "error": str(e)
            }
            logger.error(f"❌ Database validation failed: {e}")
    
    async def validate_cache_performance(self):
        """Test current caching system"""
        logger.info("🗄️ Validating cache performance...")
        
        try:
            import redis.asyncio as redis
            
            # Test Redis connection
            redis_client = redis.from_url("redis://localhost:6379")
            
            # Test connection
            start_time = time.time()
            await redis_client.ping()
            connection_time = (time.time() - start_time) * 1000
            
            # Test set/get operations
            test_key = "validation_test"
            test_value = "test_data"
            
            start_time = time.time()
            await redis_client.set(test_key, test_value, ex=60)
            set_time = (time.time() - start_time) * 1000
            
            start_time = time.time()
            retrieved_value = await redis_client.get(test_key)
            get_time = (time.time() - start_time) * 1000
            
            # Clean up
            await redis_client.delete(test_key)
            await redis_client.close()
            
            self.baseline_results["cache_performance"] = {
                "connection_time_ms": connection_time,
                "set_operation_ms": set_time,
                "get_operation_ms": get_time,
                "available": True,
                "error": None
            }
            
            logger.info(f"✅ Cache: {connection_time:.1f}ms connection, {get_time:.1f}ms get")
            
        except Exception as e:
            self.baseline_results["cache_performance"] = {
                "available": False,
                "error": str(e)
            }
            logger.error(f"❌ Cache validation failed: {e}")
    
    async def validate_agent_selection(self):
        """Test current agent selection performance"""
        logger.info("🤖 Validating agent selection performance...")
        
        try:
            # Test agent selection via API
            api_url = self.endpoints["main_api"]
            
            # Test multiple agent selection requests
            selection_times = []
            
            test_messages = [
                "Help me with frontend development",
                "Analyze this data for me", 
                "Quick answer needed",
                "Complex system design question",
                "Simple query about programming"
            ]
            
            for i, message in enumerate(test_messages):
                try:
                    start_time = time.time()
                    
                    response = requests.post(
                        f"{api_url}/api/chat/",
                        json={
                            "message": message,
                            "agent_id": None,
                            "show_browser_windows": False
                        },
                        timeout=30
                    )
                    
                    response_time = (time.time() - start_time) * 1000
                    selection_times.append(response_time)
                    
                    logger.info(f"✅ Agent selection {i+1}: {response_time:.1f}ms")
                    
                except Exception as e:
                    logger.warning(f"⚠️ Agent selection {i+1} failed: {e}")
                    selection_times.append(30000)  # 30s timeout
            
            if selection_times:
                self.baseline_results["agent_selection"] = {
                    "avg_time_ms": statistics.mean(selection_times),
                    "min_time_ms": min(selection_times),
                    "max_time_ms": max(selection_times),
                    "p95_time_ms": statistics.quantiles(selection_times, n=20)[18] if len(selection_times) > 20 else max(selection_times),
                    "total_tests": len(selection_times),
                    "successful_tests": len([t for t in selection_times if t < 30000]),
                    "available": True
                }
            else:
                self.baseline_results["agent_selection"] = {
                    "available": False,
                    "error": "No successful tests"
                }
            
        except Exception as e:
            self.baseline_results["agent_selection"] = {
                "available": False,
                "error": str(e)
            }
            logger.error(f"❌ Agent selection validation failed: {e}")
    
    async def validate_overall_system(self):
        """Test overall system performance with realistic workloads"""
        logger.info("🎯 Validating overall system performance...")
        
        try:
            api_url = self.endpoints["main_api"]
            
            # Simulate realistic user workload
            workload_tests = [
                {"message": "Hello, how are you?", "expected_type": "greeting"},
                {"message": "Help me build a React component", "expected_type": "frontend"},
                {"message": "What's 2+2?", "expected_type": "simple"},
                {"message": "Design a microservices architecture", "expected_type": "complex"},
                {"message": "Quick tip for Python", "expected_type": "quick"}
            ]
            
            response_times = []
            success_count = 0
            
            for i, test in enumerate(workload_tests):
                try:
                    start_time = time.time()
                    
                    response = requests.post(
                        f"{api_url}/api/chat/",
                        json={
                            "message": test["message"],
                            "agent_id": None,
                            "show_browser_windows": False
                        },
                        timeout=30
                    )
                    
                    response_time = (time.time() - start_time) * 1000
                    response_times.append(response_time)
                    
                    if response.status_code == 200:
                        success_count += 1
                    
                    logger.info(f"✅ Workload test {i+1}: {response_time:.1f}ms")
                    
                except Exception as e:
                    logger.warning(f"⚠️ Workload test {i+1} failed: {e}")
                    response_times.append(30000)  # Timeout
            
            if response_times:
                self.baseline_results["overall_system"] = {
                    "avg_response_time_ms": statistics.mean(response_times),
                    "min_response_time_ms": min(response_times),
                    "max_response_time_ms": max(response_times),
                    "p95_response_time_ms": statistics.quantiles(response_times, n=20)[18] if len(response_times) > 20 else max(response_times),
                    "success_rate": success_count / len(response_times),
                    "total_tests": len(response_times),
                    "successful_tests": success_count
                }
            else:
                self.baseline_results["overall_system"] = {
                    "available": False,
                    "error": "No successful tests"
                }
            
        except Exception as e:
            self.baseline_results["overall_system"] = {
                "available": False,
                "error": str(e)
            }
            logger.error(f"❌ Overall system validation failed: {e}")
    
    def analyze_bottlenecks(self):
        """Analyze performance bottlenecks based on validation results"""
        logger.info("🔍 Analyzing performance bottlenecks...")
        
        bottlenecks = []
        
        # Analyze agent selection performance
        agent_selection = self.baseline_results.get("agent_selection", {})
        if agent_selection.get("available") and agent_selection.get("avg_time_ms", 0) > 2000:
            bottlenecks.append({
                "component": "agent_selection",
                "severity": "high" if agent_selection["avg_time_ms"] > 10000 else "medium",
                "current_time_ms": agent_selection["avg_time_ms"],
                "threshold_ms": 2000,
                "description": f"Agent selection taking {agent_selection['avg_time_ms']:.1f}ms (target: <2000ms)"
            })
        
        # Analyze overall system performance
        overall_system = self.baseline_results.get("overall_system", {})
        if overall_system.get("available") and overall_system.get("avg_response_time_ms", 0) > 5000:
            bottlenecks.append({
                "component": "overall_system",
                "severity": "high" if overall_system["avg_response_time_ms"] > 15000 else "medium",
                "current_time_ms": overall_system["avg_response_time_ms"],
                "threshold_ms": 5000,
                "description": f"Overall system response time {overall_system['avg_response_time_ms']:.1f}ms (target: <5000ms)"
            })
        
        # Analyze database performance
        db_perf = self.baseline_results.get("database_performance", {})
        if db_perf.get("available") and db_perf.get("simple_query_time_ms", 0) > 100:
            bottlenecks.append({
                "component": "database",
                "severity": "medium" if db_perf["simple_query_time_ms"] > 500 else "low",
                "current_time_ms": db_perf["simple_query_time_ms"],
                "threshold_ms": 100,
                "description": f"Database query time {db_perf['simple_query_time_ms']:.1f}ms (target: <100ms)"
            })
        
        # Analyze cache performance
        cache_perf = self.baseline_results.get("cache_performance", {})
        if cache_perf.get("available") and cache_perf.get("get_operation_ms", 0) > 10:
            bottlenecks.append({
                "component": "cache",
                "severity": "low",
                "current_time_ms": cache_perf["get_operation_ms"],
                "threshold_ms": 10,
                "description": f"Cache get operation {cache_perf['get_operation_ms']:.1f}ms (target: <10ms)"
            })
        
        self.baseline_results["bottlenecks"] = bottlenecks
        
        logger.info(f"🔍 Found {len(bottlenecks)} performance bottlenecks")
        for bottleneck in bottlenecks:
            logger.info(f"   • {bottleneck['component']}: {bottleneck['description']}")
    
    def generate_recommendations(self):
        """Generate optimization recommendations based on bottlenecks"""
        logger.info("💡 Generating optimization recommendations...")
        
        recommendations = []
        
        # Agent selection recommendations
        agent_selection = self.baseline_results.get("agent_selection", {})
        if agent_selection.get("avg_time_ms", 0) > 2000:
            recommendations.append({
                "priority": "high",
                "component": "agent_selection",
                "recommendation": "Implement intelligent caching for agent selection results",
                "expected_improvement": "Reduce selection time by 80-95%",
                "implementation": "Add Redis cache with 5-minute TTL for agent selection results"
            })
        
        # Overall system recommendations
        overall_system = self.baseline_results.get("overall_system", {})
        if overall_system.get("avg_response_time_ms", 0) > 5000:
            recommendations.append({
                "priority": "high",
                "component": "overall_system",
                "recommendation": "Implement multi-level caching system",
                "expected_improvement": "Reduce response time by 60-90%",
                "implementation": "Add L1 (memory) + L2 (Redis) caching with intelligent cache warming"
            })
        
        # Database recommendations
        db_perf = self.baseline_results.get("database_performance", {})
        if db_perf.get("simple_query_time_ms", 0) > 100:
            recommendations.append({
                "priority": "medium",
                "component": "database",
                "recommendation": "Implement database connection pooling",
                "expected_improvement": "Reduce connection overhead by 70-80%",
                "implementation": "Add AsyncPG connection pool with 20 connections"
            })
        
        # Cache recommendations
        cache_perf = self.baseline_results.get("cache_performance", {})
        if cache_perf.get("get_operation_ms", 0) > 10:
            recommendations.append({
                "priority": "low",
                "component": "cache",
                "recommendation": "Optimize Redis configuration",
                "expected_improvement": "Reduce cache access time by 50-70%",
                "implementation": "Optimize Redis memory settings and connection parameters"
            })
        
        self.baseline_results["recommendations"] = recommendations
        
        logger.info(f"💡 Generated {len(recommendations)} optimization recommendations")
        for rec in recommendations:
            logger.info(f"   • {rec['component']}: {rec['recommendation']}")
    
    def display_validation_results(self):
        """Display comprehensive validation results"""
        logger.info("📊 SYSTEM VALIDATION RESULTS")
        logger.info("=" * 60)
        
        # System Info
        sys_info = self.baseline_results["system_info"]
        logger.info("🖥️  SYSTEM INFORMATION:")
        logger.info(f"   • CPU Cores: {sys_info.get('cpu_cores', 'N/A')}")
        logger.info(f"   • Memory: {sys_info.get('memory_usage_percent', 'N/A')}% used")
        logger.info(f"   • Disk: {sys_info.get('disk_usage_percent', 'N/A')}% used")
        logger.info(f"   • Docker Containers: {len(sys_info.get('docker_containers', []))}")
        
        # API Endpoints
        endpoints = self.baseline_results["api_endpoints"]
        logger.info("🌐 API ENDPOINTS:")
        for name, result in endpoints.items():
            status = "✅" if result["available"] else "❌"
            logger.info(f"   • {name}: {status} {result.get('response_time_ms', 'N/A')}ms")
        
        # Database Performance
        db_perf = self.baseline_results["database_performance"]
        logger.info("🗄️  DATABASE PERFORMANCE:")
        if db_perf.get("available"):
            logger.info(f"   • Connection Time: {db_perf.get('connection_time_ms', 'N/A')}ms")
            logger.info(f"   • Query Time: {db_perf.get('simple_query_time_ms', 'N/A')}ms")
            logger.info(f"   • Tables: {len(db_perf.get('tables', {}))}")
        else:
            logger.info(f"   • Status: ❌ {db_perf.get('error', 'Unknown error')}")
        
        # Cache Performance
        cache_perf = self.baseline_results["cache_performance"]
        logger.info("🗄️  CACHE PERFORMANCE:")
        if cache_perf.get("available"):
            logger.info(f"   • Connection Time: {cache_perf.get('connection_time_ms', 'N/A')}ms")
            logger.info(f"   • Get Operation: {cache_perf.get('get_operation_ms', 'N/A')}ms")
        else:
            logger.info(f"   • Status: ❌ {cache_perf.get('error', 'Unknown error')}")
        
        # Agent Selection Performance
        agent_selection = self.baseline_results["agent_selection"]
        logger.info("🤖 AGENT SELECTION PERFORMANCE:")
        if agent_selection.get("available"):
            logger.info(f"   • Average Time: {agent_selection.get('avg_time_ms', 'N/A')}ms")
            logger.info(f"   • Success Rate: {agent_selection.get('successful_tests', 0)}/{agent_selection.get('total_tests', 0)}")
        else:
            logger.info(f"   • Status: ❌ {agent_selection.get('error', 'Unknown error')}")
        
        # Overall System Performance
        overall_system = self.baseline_results["overall_system"]
        logger.info("🎯 OVERALL SYSTEM PERFORMANCE:")
        if overall_system.get("available"):
            logger.info(f"   • Average Response Time: {overall_system.get('avg_response_time_ms', 'N/A')}ms")
            logger.info(f"   • Success Rate: {overall_system.get('success_rate', 0):.1%}")
        else:
            logger.info(f"   • Status: ❌ {overall_system.get('error', 'Unknown error')}")
        
        # Bottlenecks
        bottlenecks = self.baseline_results["bottlenecks"]
        logger.info("🔍 PERFORMANCE BOTTLENECKS:")
        if bottlenecks:
            for bottleneck in bottlenecks:
                severity_icon = "🚨" if bottleneck["severity"] == "high" else "⚠️" if bottleneck["severity"] == "medium" else "ℹ️"
                logger.info(f"   • {severity_icon} {bottleneck['description']}")
        else:
            logger.info("   • No significant bottlenecks detected")
        
        # Recommendations
        recommendations = self.baseline_results["recommendations"]
        logger.info("💡 OPTIMIZATION RECOMMENDATIONS:")
        if recommendations:
            for rec in recommendations:
                priority_icon = "🔥" if rec["priority"] == "high" else "⚡" if rec["priority"] == "medium" else "💡"
                logger.info(f"   • {priority_icon} {rec['component']}: {rec['recommendation']}")
        else:
            logger.info("   • System performance is within acceptable ranges")
        
        logger.info("=" * 60)
    
    async def run_comprehensive_validation(self):
        """Run comprehensive system validation"""
        logger.info("🚀 Starting comprehensive system validation...")
        logger.info("=" * 60)
        
        start_time = time.time()
        
        try:
            # Run all validation tests
            await self.validate_system_info()
            await self.validate_api_endpoints()
            await self.validate_database_performance()
            await self.validate_cache_performance()
            await self.validate_agent_selection()
            await self.validate_overall_system()
            
            # Analyze results
            self.analyze_bottlenecks()
            self.generate_recommendations()
            
            # Display results
            self.display_validation_results()
            
            total_time = time.time() - start_time
            logger.info(f"✅ Comprehensive validation completed in {total_time:.2f} seconds")
            
            return self.baseline_results
            
        except Exception as e:
            logger.error(f"❌ Validation failed: {e}")
            raise

async def main():
    """Main validation function"""
    validator = SystemPerformanceValidator()
    
    try:
        results = await validator.run_comprehensive_validation()
        
        # Save results to file
        with open("system_validation_baseline.json", "w") as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info("📄 Validation results saved to system_validation_baseline.json")
        
        return True
        
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    if success:
        print("\n🎉 System validation completed successfully!")
        print("📊 Baseline performance metrics established")
        print("💡 Ready to implement targeted optimizations")
    else:
        print("\n❌ System validation failed!")
