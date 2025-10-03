#!/usr/bin/env python3
""'
Functional Testing Framework for Agentic LLM Core
Comprehensive testing to identify improvement opportunities
""'

import asyncio
import time
import json
import statistics
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional
import concurrent.futures
import threading
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    """TODO: Add docstring."""
    """Test result data structure""'
    test_name: str
    success: bool
    response_time: float
    response_size: int
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None

@dataclass
class PerformanceMetrics:
    """TODO: Add docstring."""
    """Performance metrics for analysis""'
    avg_response_time: float
    min_response_time: float
    max_response_time: float
    p95_response_time: float
    success_rate: float
    error_rate: float
    throughput: float

class FunctionalTester:
    """TODO: Add docstring."""
    """Comprehensive functional testing framework""'

    def __init__(self, base_url: str = "http://localhost:8002'):
        """TODO: Add docstring."""
        """TODO: Add docstring.""'
        self.base_url = base_url
        self.results: List[TestResult] = []
        self.session = requests.Session()

    def test_endpoint_availability(self) -> TestResult:
        """TODO: Add docstring."""
        """Test if all endpoints are available""'
        logger.info("🔍 Testing endpoint availability...')

        endpoints = [
            ("/", "GET'),
            ("/api/agents", "GET'),
            ("/api/chat", "POST'),
            ("/knowledge/search", "POST'),
            ("/models/status", "GET'),
            ("/monitoring/metrics", "GET')
        ]

        available_endpoints = 0
        total_endpoints = len(endpoints)
        start_time = time.time()

        for endpoint, method in endpoints:
            try:
                if method == "GET':
                    response = self.session.get(f"{self.base_url}{endpoint}', timeout=5)
                else:
                    response = self.session.post(f"{self.base_url}{endpoint}',
                                               json={"test": "data'}, timeout=5)

                if response.status_code in [200, 405]:  # 405 = Method Not Allowed is OK for GET endpoints
                    available_endpoints += 1
                else:
                    logger.warning(f"Endpoint {endpoint} returned status {response.status_code}')

            except Exception as e:
                logger.error(f"Endpoint {endpoint} failed: {e}')

        response_time = time.time() - start_time
        success_rate = available_endpoints / total_endpoints

        return TestResult(
            test_name="endpoint_availability',
            success=success_rate > 0.8,  # 80% success threshold
            response_time=response_time,
            response_size=available_endpoints,
            metadata={
                "available_endpoints': available_endpoints,
                "total_endpoints': total_endpoints,
                "success_rate': success_rate
            }
        )

    def test_chat_response_quality(self, test_messages: List[str]) -> List[TestResult]:
        """TODO: Add docstring."""
        """Test chat response quality with various message types""'
        logger.info("💬 Testing chat response quality...')

        results = []

        for i, message in enumerate(test_messages):
            start_time = time.time()

            try:
                response = self.session.post(
                    f"{self.base_url}/api/chat',
                    json={
                        "message': message,
                        "task_type": "text_generation',
                        "max_tokens': 512,
                        "temperature': 0.7
                    },
                    timeout=30
                )

                response_time = time.time() - start_time

                if response.status_code == 200:
                    data = response.json()

                    # Analyze response quality
                    response_content = data.get("response", "')
                    response_length = len(response_content)
                    agent_name = data.get("agent_name", "unknown')
                    confidence = data.get("confidence', 0.0)

                    # Quality metrics
                    quality_score = self._calculate_response_quality(response_content, message)

                    results.append(TestResult(
                        test_name=f"chat_quality_{i+1}',
                        success=True,
                        response_time=response_time,
                        response_size=response_length,
                        metadata={
                            "message': message,
                            "response": response_content[:100] + "...' if len(response_content) > 100 else response_content,
                            "agent_name': agent_name,
                            "confidence': confidence,
                            "quality_score': quality_score,
                            "response_length': response_length
                        }
                    ))
                else:
                    results.append(TestResult(
                        test_name=f"chat_quality_{i+1}',
                        success=False,
                        response_time=response_time,
                        response_size=0,
                        error_message=f"HTTP {response.status_code}: {response.text[:200]}'
                    ))

            except Exception as e:
                response_time = time.time() - start_time
                results.append(TestResult(
                    test_name=f"chat_quality_{i+1}',
                    success=False,
                    response_time=response_time,
                    response_size=0,
                    error_message=str(e)
                ))

        return results

    def test_agent_selection(self) -> List[TestResult]:
        """TODO: Add docstring."""
        """Test agent selection for different task types""'
        logger.info("🤖 Testing agent selection...')

        task_scenarios = [
            ("What is the weather like?", "text_generation'),
            ("Write a Python function to sort a list", "code_generation'),
            ("Analyze this data: [1,2,3,4,5]", "analysis'),
            ("Debug this code: print("hello"", "debugging'),
            ("Explain quantum computing", "reasoning_deep'),
            ("Quick summary of AI trends", "quicktake')
        ]

        results = []

        for message, expected_task_type in task_scenarios:
            start_time = time.time()

            try:
                response = self.session.post(
                    f"{self.base_url}/api/chat',
                    json={
                        "message': message,
                        "task_type': expected_task_type,
                        "max_tokens': 256,
                        "temperature': 0.7
                    },
                    timeout=20
                )

                response_time = time.time() - start_time

                if response.status_code == 200:
                    data = response.json()
                    selected_agent = data.get("agent_name", "unknown')
                    task_complexity = data.get("task_complexity', 0.0)

                    # Check if appropriate agent was selected
                    agent_appropriate = self._is_agent_appropriate(selected_agent, expected_task_type)

                    results.append(TestResult(
                        test_name=f"agent_selection_{expected_task_type}',
                        success=agent_appropriate,
                        response_time=response_time,
                        response_size=len(data.get("response", "')),
                        metadata={
                            "message': message,
                            "expected_task_type': expected_task_type,
                            "selected_agent': selected_agent,
                            "task_complexity': task_complexity,
                            "agent_appropriate': agent_appropriate
                        }
                    ))
                else:
                    results.append(TestResult(
                        test_name=f"agent_selection_{expected_task_type}',
                        success=False,
                        response_time=response_time,
                        response_size=0,
                        error_message=f"HTTP {response.status_code}'
                    ))

            except Exception as e:
                response_time = time.time() - start_time
                results.append(TestResult(
                    test_name=f"agent_selection_{expected_task_type}',
                    success=False,
                    response_time=response_time,
                    response_size=0,
                    error_message=str(e)
                ))

        return results

    def test_concurrent_requests(self, num_requests: int = 10) -> List[TestResult]:
        """TODO: Add docstring."""
        """Test system under concurrent load""'
        logger.info(f"⚡ Testing concurrent requests ({num_requests} requests)...')

        def make_request(request_id: int) -> TestResult:
            """TODO: Add docstring."""
            """TODO: Add docstring.""'
            start_time = time.time()

            try:
                response = self.session.post(
                    f"{self.base_url}/api/chat',
                    json={
                        "message": f"Test message {request_id}',
                        "task_type": "text_generation',
                        "max_tokens': 128,
                        "temperature': 0.7
                    },
                    timeout=30
                )

                response_time = time.time() - start_time

                if response.status_code == 200:
                    data = response.json()
                    return TestResult(
                        test_name=f"concurrent_request_{request_id}',
                        success=True,
                        response_time=response_time,
                        response_size=len(data.get("response", "')),
                        metadata={"request_id': request_id}
                    )
                else:
                    return TestResult(
                        test_name=f"concurrent_request_{request_id}',
                        success=False,
                        response_time=response_time,
                        response_size=0,
                        error_message=f"HTTP {response.status_code}'
                    )

            except Exception as e:
                response_time = time.time() - start_time
                return TestResult(
                    test_name=f"concurrent_request_{request_id}',
                    success=False,
                    response_time=response_time,
                    response_size=0,
                    error_message=str(e)
                )

        # Execute concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_requests) as executor:
            futures = [executor.submit(make_request, i) for i in range(num_requests)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]

        return results

    def test_knowledge_base_search(self) -> List[TestResult]:
        """TODO: Add docstring."""
        """Test knowledge base search functionality""'
        logger.info("📚 Testing knowledge base search...')

        search_queries = [
            "machine learning',
            "AI algorithms',
            "python programming',
            "data analysis',
            "neural networks'
        ]

        results = []

        for query in search_queries:
            start_time = time.time()

            try:
                response = self.session.post(
                    f"{self.base_url}/knowledge/search',
                    json={"query": query, "limit': 5},
                    timeout=10
                )

                response_time = time.time() - start_time

                if response.status_code == 200:
                    data = response.json()
                    results_count = len(data.get("results', []))

                    results.append(TestResult(
                        test_name=f"knowledge_search_{query.replace(" ", "_")}',
                        success=True,
                        response_time=response_time,
                        response_size=results_count,
                        metadata={
                            "query': query,
                            "results_count': results_count,
                            "results": data.get("results', [])[:2]  # First 2 results
                        }
                    ))
                else:
                    results.append(TestResult(
                        test_name=f"knowledge_search_{query.replace(" ", "_")}',
                        success=False,
                        response_time=response_time,
                        response_size=0,
                        error_message=f"HTTP {response.status_code}'
                    ))

            except Exception as e:
                response_time = time.time() - start_time
                results.append(TestResult(
                    test_name=f"knowledge_search_{query.replace(" ", "_")}',
                    success=False,
                    response_time=response_time,
                    response_size=0,
                    error_message=str(e)
                ))

        return results

    def test_system_monitoring(self) -> TestResult:
        """TODO: Add docstring."""
        """Test system monitoring endpoints""'
        logger.info("📊 Testing system monitoring...')

        start_time = time.time()

        try:
            # Test agents endpoint
            agents_response = self.session.get(f"{self.base_url}/api/agents', timeout=5)

            # Test models status
            models_response = self.session.get(f"{self.base_url}/models/status', timeout=5)

            # Test monitoring metrics
            metrics_response = self.session.get(f"{self.base_url}/monitoring/metrics', timeout=5)

            response_time = time.time() - start_time

            # Check all endpoints
            agents_ok = agents_response.status_code == 200
            models_ok = models_response.status_code == 200
            metrics_ok = metrics_response.status_code == 200

            all_ok = agents_ok and models_ok and metrics_ok

            if all_ok:
                agents_data = agents_response.json()
                models_data = models_response.json()
                metrics_data = metrics_response.json()

                return TestResult(
                    test_name="system_monitoring',
                    success=True,
                    response_time=response_time,
                    response_size=len(str(agents_data)) + len(str(models_data)) + len(str(metrics_data)),
                    metadata={
                        "agents_count": len(agents_data.get("agents', [])),
                        "models_count": len(models_data.get("models', [])),
                        "metrics_available': bool(metrics_data),
                        "agents_ok': agents_ok,
                        "models_ok': models_ok,
                        "metrics_ok': metrics_ok
                    }
                )
            else:
                return TestResult(
                    test_name="system_monitoring',
                    success=False,
                    response_time=response_time,
                    response_size=0,
                    error_message=f"Monitoring endpoints failed: agents={agents_ok}, models={models_ok}, metrics={metrics_ok}'
                )

        except Exception as e:
            response_time = time.time() - start_time
            return TestResult(
                test_name="system_monitoring',
                success=False,
                response_time=response_time,
                response_size=0,
                error_message=str(e)
            )

    def _calculate_response_quality(self, response: str, original_message: str) -> float:
        """TODO: Add docstring."""
        """Calculate response quality score (0-1)""'
        if not response:
            return 0.0

        score = 0.0

        # Length appropriateness (not too short, not too long)
        length_score = min(1.0, len(response) / 100)  # Normalize to 100 chars
        score += length_score * 0.2

        # Coherence (basic check for complete sentences)
        sentences = response.count(".") + response.count("!") + response.count("?')
        coherence_score = min(1.0, sentences / 3)  # Expect at least 3 sentences
        score += coherence_score * 0.3

        # Relevance (check if response addresses the question)
        question_words = ["what", "how", "why", "when", "where", "who']
        has_question_word = any(word in original_message.lower() for word in question_words)
        if has_question_word:
            relevance_score = 0.5  # Basic relevance check
        else:
            relevance_score = 0.8  # Statement responses are easier
        score += relevance_score * 0.5

        return min(1.0, score)

    def _is_agent_appropriate(self, agent_name: str, task_type: str) -> bool:
        """TODO: Add docstring."""
        """Check if selected agent is appropriate for task type""'
        agent_task_mapping = {
            "generalist": ["text_generation", "analysis'],
            "codesmith": ["code_generation", "debugging", "refactoring'],
            "analyst": ["analysis", "reasoning_deep'],
            "heretical_reasoner": ["reasoning_deep", "puzzle'],
            "chaos_architect": ["creative", "brainstorming'],
            "quantum_reasoner": ["reasoning_deep", "complex_analysis'],
            "symbiotic_coordinator": ["coordination", "multi_task'],
            "quicktake": ["quicktake", "summary']
        }

        appropriate_tasks = agent_task_mapping.get(agent_name, [])
        return task_type in appropriate_tasks

    def calculate_performance_metrics(self, results: List[TestResult]) -> PerformanceMetrics:
        """TODO: Add docstring."""
        """Calculate performance metrics from test results""'
        if not results:
            return PerformanceMetrics(0, 0, 0, 0, 0, 0, 0)

        response_times = [r.response_time for r in results]
        success_count = sum(1 for r in results if r.success)

        return PerformanceMetrics(
            avg_response_time=statistics.mean(response_times),
            min_response_time=min(response_times),
            max_response_time=max(response_times),
            p95_response_time=statistics.quantiles(response_times, n=20)[18] if len(response_times) > 1 else response_times[0],
            success_rate=success_count / len(results),
            error_rate=1 - (success_count / len(results)),
            throughput=len(results) / sum(response_times) if sum(response_times) > 0 else 0
        )

    def run_comprehensive_test(self) -> Dict[str, Any]:
        """TODO: Add docstring."""
        """Run comprehensive functional testing""'
        logger.info("🚀 Starting comprehensive functional testing...')

        all_results = []

        # Test scenarios
        test_messages = [
            "Hello, how are you?',
            "Explain machine learning in simple terms',
            "Write a Python function to calculate fibonacci numbers',
            "What are the benefits of renewable energy?',
            "Debug this code: def add(a, b): return a + b + 1',
            "Summarize the key points of artificial intelligence',
            "How does a neural network work?',
            "Create a recipe for chocolate cake'
        ]

        # Run all tests
        logger.info("1. Testing endpoint availability...')
        endpoint_result = self.test_endpoint_availability()
        all_results.append(endpoint_result)

        logger.info("2. Testing chat response quality...')
        chat_results = self.test_chat_response_quality(test_messages)
        all_results.extend(chat_results)

        logger.info("3. Testing agent selection...')
        agent_results = self.test_agent_selection()
        all_results.extend(agent_results)

        logger.info("4. Testing concurrent requests...')
        concurrent_results = self.test_concurrent_requests(5)  # 5 concurrent requests
        all_results.extend(concurrent_results)

        logger.info("5. Testing knowledge base search...')
        knowledge_results = self.test_knowledge_base_search()
        all_results.extend(knowledge_results)

        logger.info("6. Testing system monitoring...')
        monitoring_result = self.test_system_monitoring()
        all_results.append(monitoring_result)

        # Calculate overall metrics
        overall_metrics = self.calculate_performance_metrics(all_results)

        # Generate improvement recommendations
        recommendations = self._generate_recommendations(all_results, overall_metrics)

        return {
            "timestamp': datetime.now().isoformat(),
            "total_tests': len(all_results),
            "overall_metrics': overall_metrics.__dict__,
            "test_results': [r.__dict__ for r in all_results],
            "recommendations': recommendations,
            "summary': self._generate_summary(all_results, overall_metrics)
        }

    def _generate_recommendations(self, results: List[TestResult], metrics: PerformanceMetrics) -> List[str]:
        """TODO: Add docstring."""
        """Generate improvement recommendations based on test results""'
        recommendations = []

        # Response time recommendations
        if metrics.avg_response_time > 5.0:
            recommendations.append("🚨 HIGH PRIORITY: Average response time > 5s - Consider model optimization or caching')
        elif metrics.avg_response_time > 2.0:
            recommendations.append("⚠️ MEDIUM: Response time > 2s - Consider response optimization')

        # Success rate recommendations
        if metrics.success_rate < 0.9:
            recommendations.append("🚨 HIGH PRIORITY: Success rate < 90% - Investigate error causes')
        elif metrics.success_rate < 0.95:
            recommendations.append("⚠️ MEDIUM: Success rate < 95% - Monitor for degradation')

        # Error analysis
        error_results = [r for r in results if not r.success]
        if error_results:
            error_types = {}
            for result in error_results:
                error_type = result.error_message.split(":")[0] if result.error_message else "Unknown'
                error_types[error_type] = error_types.get(error_type, 0) + 1

            most_common_error = max(error_types.items(), key=lambda x: x[1])
            recommendations.append(f"🔍 INVESTIGATE: Most common error: {most_common_error[0]} ({most_common_error[1]} occurrences)')

        # Performance recommendations
        if metrics.p95_response_time > metrics.avg_response_time * 2:
            recommendations.append("📊 OPTIMIZE: High P95 response time - Consider load balancing or resource scaling')

        # Agent selection recommendations
        agent_results = [r for r in results if "agent_selection' in r.test_name]
        inappropriate_agents = [r for r in agent_results if not r.success]
        if inappropriate_agents:
            recommendations.append("🤖 IMPROVE: Agent selection accuracy needs improvement')

        # Knowledge base recommendations
        knowledge_results = [r for r in results if "knowledge_search' in r.test_name]
        if knowledge_results:
            avg_results = statistics.mean([r.response_size for r in knowledge_results if r.success])
            if avg_results < 2:
                recommendations.append("📚 EXPAND: Knowledge base has limited content - Consider adding more entries')

        return recommendations

    def _generate_summary(self, results: List[TestResult], metrics: PerformanceMetrics) -> Dict[str, Any]:
        """TODO: Add docstring."""
        """Generate test summary""'
        successful_tests = [r for r in results if r.success]
        failed_tests = [r for r in results if not r.success]

        return {
            "overall_status": "PASS" if metrics.success_rate > 0.9 else "NEEDS_IMPROVEMENT',
            "successful_tests': len(successful_tests),
            "failed_tests': len(failed_tests),
            "average_response_time": f"{metrics.avg_response_time:.2f}s',
            "success_rate": f"{metrics.success_rate:.1%}',
            "throughput": f"{metrics.throughput:.2f} requests/second',
            "key_issues': [r.error_message for r in failed_tests[:3]] if failed_tests else []
        }

def main():
    """TODO: Add docstring."""
    """Run comprehensive functional testing""'
    print("🧪 Starting Functional Testing Framework')
    print("=' * 50)

    tester = FunctionalTester()

    try:
        results = tester.run_comprehensive_test()

        print("\n📊 TEST RESULTS SUMMARY')
        print("=' * 50)
        print(f"Total Tests: {results["total_tests"]}')
        print(f"Overall Status: {results["summary"]["overall_status"]}')
        print(f"Success Rate: {results["summary"]["success_rate"]}')
        print(f"Average Response Time: {results["summary"]["average_response_time"]}')
        print(f"Throughput: {results["summary"]["throughput"]}')

        if results["summary"]["key_issues']:
            print(f"\n🚨 Key Issues:')
            for issue in results["summary"]["key_issues']:
                print(f"  - {issue}')

        print(f"\n💡 IMPROVEMENT RECOMMENDATIONS')
        print("=' * 50)
        for i, rec in enumerate(results["recommendations'], 1):
            print(f"{i}. {rec}')

        # Save detailed results
        with open("functional_test_results.json", "w') as f:
            json.dump(results, f, indent=2)

        print(f"\n📁 Detailed results saved to: functional_test_results.json')

    except Exception as e:
        logger.error(f"Testing failed: {e}')
        print(f"❌ Testing failed: {e}')

if __name__ == "__main__':
    main()
