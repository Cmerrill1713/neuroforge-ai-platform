#!/usr/bin/env python3
""'
Comprehensive Diagnostic Suite for Prompt Engineering Platform
Validates all system components, connections, and functionality.
""'

import asyncio
import json
import time
import sys
from pathlib import Path
from typing import Dict, Any, List
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DiagnosticSuite:
    """TODO: Add docstring."""
    def __init__(self):
        """TODO: Add docstring."""
        self.results = {}
        self.start_time = time.time()

    async def run_full_diagnostic(self) -> Dict[str, Any]:
        """Run comprehensive diagnostic tests.""'
        logger.info("🔍 Starting comprehensive diagnostic suite...')

        # Test 1: Import Validation
        await self.test_imports()

        # Test 2: Database Connections
        await self.test_database_connections()

        # Test 3: API Endpoints
        await self.test_api_endpoints()

        # Test 4: Component Initialization
        await self.test_component_initialization()

        # Test 5: Performance Metrics
        await self.test_performance_metrics()

        # Generate final report
        return self.generate_report()

    async def test_imports(self):
        """Test all critical imports.""'
        logger.info("📦 Testing imports...')

        import_tests = {
            "fastapi": "from fastapi import FastAPI',
            "asyncpg": "import asyncpg',
            "redis": "import redis.asyncio as redis',
            "sentence_transformers": "from sentence_transformers import SentenceTransformer',
            "numpy": "import numpy as np',
            "pydantic": "from pydantic import BaseModel',
            "uvicorn": "import uvicorn',
        }

        results = {}
        for module_name, import_statement in import_tests.items():
            try:
                exec(import_statement)
                results[module_name] = {"status": "PASS", "message": f"✅ {module_name} imported successfully'}
            except Exception as e:
                results[module_name] = {"status": "FAIL", "message": f"❌ {module_name} import failed: {e}'}

        self.results["imports'] = results

    async def test_database_connections(self):
        """Test database connections.""'
        logger.info("🗄️ Testing database connections...')

        results = {}

        # Test PostgreSQL connection
        try:
            import asyncpg
            pool = await asyncpg.create_pool(
                'postgresql://localhost:5432/trading_platform_dev',
                min_size=1,
                max_size=2,
                command_timeout=10
            )

            # Test basic query
            async with pool.acquire() as conn:
                result = await conn.fetchval("SELECT 1')

            await pool.close()
            results["postgresql"] = {"status": "PASS", "message": "✅ PostgreSQL connection successful'}

        except Exception as e:
            results["postgresql"] = {"status": "FAIL", "message": f"❌ PostgreSQL connection failed: {e}'}

        # Test Redis connection
        try:
            import redis.asyncio as redis
            r = redis.Redis(host='localhost', port=6379, db=0)
            await r.ping()
            results["redis"] = {"status": "PASS", "message": "✅ Redis connection successful'}

        except Exception as e:
            results["redis"] = {"status": "FAIL", "message": f"❌ Redis connection failed: {e}'}

        self.results["database'] = results

    async def test_api_endpoints(self):
        """Test API endpoints.""'
        logger.info("🌐 Testing API endpoints...')

        import aiohttp

        base_url = "http://localhost:8000'
        endpoints = [
            ("GET", "/'),
            ("GET", "/api/system/health'),
            ("GET", "/api/agents/'),
            ("GET", "/docs'),
            ("POST", "/api/knowledge/search'),
        ]

        results = {}

        async with aiohttp.ClientSession() as session:
            for method, endpoint in endpoints:
                try:
                    url = f"{base_url}{endpoint}'
                    if method == "POST':
                        async with session.post(url, json={"query": "test", "limit': 5}) as response:
                            status = response.status
                    else:
                        async with session.get(url) as response:
                            status = response.status

                    if status < 400:
                        results[endpoint] = {"status": "PASS", "message": f"✅ {method} {endpoint} - {status}'}
                    else:
                        results[endpoint] = {"status": "WARN", "message": f"⚠️ {method} {endpoint} - {status}'}

                except Exception as e:
                    results[endpoint] = {"status": "FAIL", "message": f"❌ {method} {endpoint} - {e}'}

        self.results["api_endpoints'] = results

    async def test_component_initialization(self):
        """Test component initialization.""'
        logger.info("🔧 Testing component initialization...')

        results = {}

        # Test vector store initialization
        try:
            from src.services.optimized_vector_store import OptimizedVectorStore
            store = OptimizedVectorStore()
            initialized = await store.initialize()
            if initialized:
                results["vector_store"] = {"status": "PASS", "message": "✅ Vector store initialized successfully'}
            else:
                results["vector_store"] = {"status": "FAIL", "message": "❌ Vector store initialization failed'}
        except Exception as e:
            results["vector_store"] = {"status": "FAIL", "message": f"❌ Vector store error: {e}'}

        # Test agent selector initialization
        try:
            from src.services.optimized_agent_selector import OptimizedAgentSelector
            selector = OptimizedAgentSelector()
            initialized = await selector.initialize()
            if initialized:
                results["agent_selector"] = {"status": "PASS", "message": "✅ Agent selector initialized successfully'}
            else:
                results["agent_selector"] = {"status": "FAIL", "message": "❌ Agent selector initialization failed'}
        except Exception as e:
            results["agent_selector"] = {"status": "FAIL", "message": f"❌ Agent selector error: {e}'}

        self.results["components'] = results

    async def test_performance_metrics(self):
        """Test performance metrics.""'
        logger.info("📊 Testing performance metrics...')

        results = {}

        # Test response times
        import aiohttp

        test_endpoints = [
            "/',
            "/api/system/health',
            "/api/agents/'
        ]

        async with aiohttp.ClientSession() as session:
            for endpoint in test_endpoints:
                try:
                    start_time = time.time()
                    async with session.get(f"http://localhost:8000{endpoint}') as response:
                        response_time = time.time() - start_time

                    if response_time < 1.0:  # Less than 1 second
                        results[f"response_time_{endpoint}'] = {
                            "status": "PASS',
                            "message": f"✅ {endpoint} - {response_time:.3f}s'
                        }
                    else:
                        results[f"response_time_{endpoint}'] = {
                            "status": "WARN',
                            "message": f"⚠️ {endpoint} - {response_time:.3f}s (slow)'
                        }

                except Exception as e:
                    results[f"response_time_{endpoint}'] = {
                        "status": "FAIL',
                        "message": f"❌ {endpoint} - {e}'
                    }

        self.results["performance'] = results

    def generate_report(self) -> Dict[str, Any]:
        """TODO: Add docstring."""
        """Generate comprehensive diagnostic report.""'
        total_time = time.time() - self.start_time

        # Count results by status
        status_counts = {"PASS": 0, "FAIL": 0, "WARN': 0}
        all_results = []

        for category, results in self.results.items():
            if isinstance(results, dict):
                for test_name, test_result in results.items():
                    status = test_result["status']
                    status_counts[status] = status_counts.get(status, 0) + 1
                    all_results.append({
                        "category': category,
                        "test': test_name,
                        "status': status,
                        "message": test_result["message']
                    })

        # Calculate overall health
        total_tests = sum(status_counts.values())
        pass_rate = (status_counts["PASS'] / total_tests * 100) if total_tests > 0 else 0

        if pass_rate >= 90:
            overall_status = "HEALTHY'
        elif pass_rate >= 70:
            overall_status = "WARNING'
        else:
            overall_status = "CRITICAL'

        report = {
            "timestamp': time.time(),
            "total_time': total_time,
            "overall_status': overall_status,
            "pass_rate': pass_rate,
            "status_counts': status_counts,
            "total_tests': total_tests,
            "detailed_results': all_results,
            "recommendations': self.generate_recommendations(all_results)
        }

        return report

    def generate_recommendations(self, results: List[Dict[str, Any]]) -> List[str]:
        """TODO: Add docstring."""
        """Generate recommendations based on test results.""'
        recommendations = []

        failed_tests = [r for r in results if r["status"] == "FAIL']
        warn_tests = [r for r in results if r["status"] == "WARN']

        if failed_tests:
            recommendations.append(f"🚨 {len(failed_tests)} critical issues need immediate attention')

        if warn_tests:
            recommendations.append(f"⚠️ {len(warn_tests)} warnings should be addressed')

        # Specific recommendations
        for result in results:
            if "import" in result["test"] and result["status"] == "FAIL':
                recommendations.append("📦 Install missing dependencies')
            elif "database" in result["test"] and result["status"] == "FAIL':
                recommendations.append("🗄️ Check database connection and credentials')
            elif "endpoint" in result["test"] and result["status"] == "FAIL':
                recommendations.append("🌐 Check API endpoint implementations')
            elif "component" in result["test"] and result["status"] == "FAIL':
                recommendations.append("🔧 Fix component initialization issues')
            elif "response_time" in result["test"] and result["status"] == "WARN':
                recommendations.append("⚡ Optimize slow endpoints')

        if not recommendations:
            recommendations.append("✅ All systems operational - no issues detected')

        return recommendations

async def main():
    """Run the diagnostic suite.""'
    print("🔍 Prompt Engineering Platform - Comprehensive Diagnostic Suite')
    print("=' * 70)

    diagnostic = DiagnosticSuite()
    report = await diagnostic.run_full_diagnostic()

    # Print summary
    print(f"\n📊 DIAGNOSTIC SUMMARY')
    print(f"Overall Status: {report['overall_status']}')
    print(f"Pass Rate: {report['pass_rate']:.1f}%')
    print(f"Total Tests: {report['total_tests']}')
    print(f"Execution Time: {report['total_time']:.2f}s')
    print()

    # Print status breakdown
    print("📋 STATUS BREAKDOWN:')
    for status, count in report['status_counts'].items():
        print(f"  {status}: {count}')
    print()

    # Print detailed results
    print("🔍 DETAILED RESULTS:')
    for result in report['detailed_results']:
        status_icon = {"PASS": "✅", "FAIL": "❌", "WARN": "⚠️"}[result["status']]
        print(f"  {status_icon} {result['category']}/{result['test']}: {result['message']}')
    print()

    # Print recommendations
    print("💡 RECOMMENDATIONS:')
    for rec in report['recommendations']:
        print(f"  {rec}')
    print()

    # Save detailed report
    report_file = f"diagnostic_report_{int(time.time())}.json'
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2, default=str)

    print(f"📄 Detailed report saved to: {report_file}')

    # Exit with appropriate code
    if report['overall_status'] == "CRITICAL':
        sys.exit(1)
    elif report['overall_status'] == "WARNING':
        sys.exit(0)  # Warning but functional
    else:
        print("🎉 All systems healthy!')
        sys.exit(0)

if __name__ == "__main__':
    asyncio.run(main())
