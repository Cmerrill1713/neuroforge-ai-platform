#!/usr/bin/env python3
"""
Frontend Diagnostic Suite
Tests the frontend application from a user perspective.
"""

import asyncio
import json
import time
import aiohttp
import logging
from typing import Dict, Any, List

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class FrontendDiagnosticTester:
    def __init__(self):
        self.frontend_url = "http://localhost:3000"
        self.backend_url = "http://localhost:8000"
        self.session = None
        self.test_results = []

    async def initialize(self):
        """Initialize the test session."""
        self.session = aiohttp.ClientSession()

    async def cleanup(self):
        """Clean up the test session."""
        if self.session:
            await self.session.close()

    async def test_frontend_comprehensive(self) -> Dict[str, Any]:
        """Run comprehensive frontend diagnostic tests."""
        logger.info("🎨 Starting Frontend Diagnostic Testing...")

        start_time = time.time()

        # Test 1: Frontend Server Availability
        await self.test_frontend_server()

        # Test 2: Frontend Page Loading
        await self.test_frontend_pages()

        # Test 3: Frontend-Backend Integration
        await self.test_frontend_backend_integration()

        # Test 4: Frontend Components
        await self.test_frontend_components()

        # Test 5: Performance Metrics
        await self.test_frontend_performance()

        total_time = time.time() - start_time

        # Generate summary
        passed_tests = len([r for r in self.test_results if r["status"] == "PASS"])
        total_tests = len(self.test_results)
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        summary = {
            "total_time": total_time,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "success_rate": success_rate,
            "detailed_results": self.test_results
        }

        return summary

    async def test_frontend_server(self):
        """Test if frontend server is responding."""
        logger.info("🌐 Testing Frontend Server...")

        try:
            async with self.session.get(f"{self.frontend_url}/") as response:
                if response.status == 200:
                    # Check if it's actually a Next.js page (not just a redirect)
                    text = await response.text()
                    if "Next.js" in text or "AI Chat" in text or "React" in text:
                        self.test_results.append({
                            "test": "frontend_server_basic",
                            "status": "PASS",
                            "message": f"✅ Frontend server responding: {response.status}"
                        })
                    else:
                        self.test_results.append({
                            "test": "frontend_server_basic",
                            "status": "WARN",
                            "message": f"⚠️ Frontend responding but may not be Next.js app: {response.status}"
                        })
                else:
                    self.test_results.append({
                        "test": "frontend_server_basic",
                        "status": "FAIL",
                        "message": f"❌ Frontend server failed: {response.status}"
                    })
        except Exception as e:
            self.test_results.append({
                "test": "frontend_server_basic",
                "status": "FAIL",
                "message": f"❌ Frontend server error: {e}"
            })

    async def test_frontend_pages(self):
        """Test frontend page loading."""
        logger.info("📄 Testing Frontend Pages...")

        test_pages = [
            "/",
            "/_next/static/css/app/layout.css",  # CSS loading
            "/favicon.ico"  # Static assets
        ]

        for page in test_pages:
            try:
                async with self.session.get(f"{self.frontend_url}{page}") as response:
                    if response.status == 200:
                        self.test_results.append({
                            "test": f"frontend_page_{page.replace('/', '_').replace('.', '_')}",
                            "status": "PASS",
                            "message": f"✅ {page} - {response.status}"
                        })
                    elif response.status == 404 and "_next" in page:
                        # 404 for CSS is expected if not built yet
                        self.test_results.append({
                            "test": f"frontend_page_{page.replace('/', '_').replace('.', '_')}",
                            "status": "WARN",
                            "message": f"⚠️ {page} - {response.status} (build may be needed)"
                        })
                    else:
                        self.test_results.append({
                            "test": f"frontend_page_{page.replace('/', '_').replace('.', '_')}",
                            "status": "FAIL",
                            "message": f"❌ {page} - {response.status}"
                        })
            except Exception as e:
                self.test_results.append({
                    "test": f"frontend_page_{page.replace('/', '_').replace('.', '_')}",
                    "status": "FAIL",
                    "message": f"❌ {page} error: {e}"
                })

    async def test_frontend_backend_integration(self):
        """Test frontend-backend API integration."""
        logger.info("🔗 Testing Frontend-Backend Integration...")

        # Test API endpoints that frontend would use
        api_tests = [
            ("GET", "/api/system/health"),
            ("GET", "/api/agents/"),
            ("POST", "/api/knowledge/search"),
        ]

        for method, endpoint in api_tests:
            try:
                url = f"{self.backend_url}{endpoint}"
                if method == "POST":
                    async with self.session.post(url, json={"query": "test", "limit": 5}) as response:
                        status = response.status
                else:
                    async with self.session.get(url) as response:
                        status = response.status

                if status < 400:
                    self.test_results.append({
                        "test": f"frontend_backend_{method.lower()}_{endpoint.replace('/', '_').replace('-', '_')}",
                        "status": "PASS",
                        "message": f"✅ {method} {endpoint} - {status}"
                    })
                else:
                    self.test_results.append({
                        "test": f"frontend_backend_{method.lower()}_{endpoint.replace('/', '_').replace('-', '_')}",
                        "status": "FAIL",
                        "message": f"❌ {method} {endpoint} - {status}"
                    })
            except Exception as e:
                self.test_results.append({
                    "test": f"frontend_backend_{method.lower()}_{endpoint.replace('/', '_').replace('-', '_')}",
                    "status": "FAIL",
                    "message": f"❌ {method} {endpoint} error: {e}"
                })

    async def test_frontend_components(self):
        """Test frontend component functionality."""
        logger.info("🧩 Testing Frontend Components...")

        # Test chat interface (simulated user interaction)
        try:
            # This would be a WebSocket connection in real frontend
            chat_payload = {
                "message": "Hello, can you help me?",
                "task_type": "text_generation",
                "max_tokens": 100,
                "temperature": 0.7
            }

            async with self.session.post(
                f"{self.backend_url}/api/chat/",
                json=chat_payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    response_text = data.get("response", "")
                    if len(response_text) > 10:
                        self.test_results.append({
                            "test": "frontend_chat_simulation",
                            "status": "PASS",
                            "message": f"✅ Chat simulation working: {len(response_text)} chars"
                        })
                    else:
                        self.test_results.append({
                            "test": "frontend_chat_simulation",
                            "status": "WARN",
                            "message": "⚠️ Chat responded but content seems short"
                        })
                else:
                    self.test_results.append({
                        "test": "frontend_chat_simulation",
                        "status": "FAIL",
                        "message": f"❌ Chat simulation failed: {response.status}"
                    })
        except Exception as e:
            self.test_results.append({
                "test": "frontend_chat_simulation",
                "status": "FAIL",
                "message": f"❌ Chat simulation error: {e}"
            })

    async def test_frontend_performance(self):
        """Test frontend performance metrics."""
        logger.info("⚡ Testing Frontend Performance...")

        # Test frontend loading performance
        test_urls = [
            f"{self.frontend_url}/",
            f"{self.backend_url}/api/system/health"
        ]

        for url in test_urls:
            try:
                start_time = time.time()
                async with self.session.get(url) as response:
                    response_time = time.time() - start_time

                if response_time < 2.0:  # Less than 2 seconds
                    self.test_results.append({
                        "test": f"frontend_performance_{url.replace('http://localhost:', '').replace('/', '_')}",
                        "status": "PASS",
                        "message": f"✅ {url} - {response_time:.3f}s"
                    })
                elif response_time < 5.0:  # Less than 5 seconds
                    self.test_results.append({
                        "test": f"frontend_performance_{url.replace('http://localhost:', '').replace('/', '_')}",
                        "status": "WARN",
                        "message": f"⚠️ {url} - {response_time:.3f}s (slow but acceptable)"
                    })
                else:
                    self.test_results.append({
                        "test": f"frontend_performance_{url.replace('http://localhost:', '').replace('/', '_')}",
                        "status": "FAIL",
                        "message": f"❌ {url} - {response_time:.3f}s (too slow)"
                    })
            except Exception as e:
                self.test_results.append({
                    "test": f"frontend_performance_{url.replace('http://localhost:', '').replace('/', '_')}",
                    "status": "FAIL",
                    "message": f"❌ {url} performance error: {e}"
                })

    def generate_frontend_report(self, results: Dict[str, Any]) -> str:
        """Generate a comprehensive frontend diagnostic report."""
        report = []
        report.append("🎨 FRONTEND DIAGNOSTIC REPORT")
        report.append("=" * 50)
        report.append("")
        report.append("📊 SUMMARY:")
        report.append(f"  Total Tests: {results['total_tests']}")
        report.append(f"  Passed: {results['passed_tests']}")
        report.append(f"  Failed: {results['failed_tests']}")
        report.append(f"  Success Rate: {results['success_rate']:.1f}%")
        report.append(f"  Total Time: {results['total_time']:.2f}s")
        report.append("")

        # Group results by category
        categories = {
            "server": [r for r in results["detailed_results"] if "frontend_server" in r["test"]],
            "pages": [r for r in results["detailed_results"] if "frontend_page" in r["test"]],
            "integration": [r for r in results["detailed_results"] if "frontend_backend" in r["test"]],
            "components": [r for r in results["detailed_results"] if "frontend_chat" in r["test"] or "frontend_component" in r["test"]],
            "performance": [r for r in results["detailed_results"] if "frontend_performance" in r["test"]]
        }

        for category, tests in categories.items():
            if tests:
                report.append(f"🔍 {category.upper()} TESTS:")
                for test in tests:
                    status_icon = {"PASS": "✅", "FAIL": "❌", "WARN": "⚠️"}[test["status"]]
                    report.append(f"  {status_icon} {test['test']}: {test['message']}")
                report.append("")

        # Recommendations
        failed_tests = [r for r in results["detailed_results"] if r["status"] == "FAIL"]
        if failed_tests:
            report.append("🚨 ISSUES TO ADDRESS:")
            for test in failed_tests:
                report.append(f"  • {test['test']}: {test['message']}")
            report.append("")

        if results["success_rate"] >= 90:
            report.append("🎉 EXCELLENT FRONTEND EXPERIENCE!")
            report.append("The frontend provides a smooth, responsive user interface.")
        elif results["success_rate"] >= 70:
            report.append("👍 GOOD FRONTEND EXPERIENCE")
            report.append("The frontend is functional with minor issues to address.")
        else:
            report.append("⚠️ FRONTEND NEEDS IMPROVEMENT")
            report.append("Several issues are impacting the user interface.")

        return "\n".join(report)

async def main():
    """Run the frontend diagnostic suite."""
    tester = FrontendDiagnosticTester()
    await tester.initialize()

    try:
        results = await tester.test_frontend_comprehensive()
        report = tester.generate_frontend_report(results)
        print(report)

        # Save detailed results
        with open(f"frontend_diagnostic_{int(time.time())}.json", 'w') as f:
            json.dump(results, f, indent=2)

        print(f"\n📄 Detailed results saved to: frontend_diagnostic_{int(time.time())}.json")

    finally:
        await tester.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
