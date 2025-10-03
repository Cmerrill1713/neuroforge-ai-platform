#!/usr/bin/env python3
""'
Comprehensive Backtesting and Experimentation Framework
for Agentic LLM Core with MCP + Pydantic AI + Ollama Integration

This framework provides comprehensive testing, benchmarking, and analysis
of the complete agentic system to validate performance, reliability, and capabilities.
""'

import asyncio
import logging
import json
import time
import statistics
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import traceback

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src'))

from src.core.tools.pydantic_ai_mcp import (
    PydanticAIMCPAgent,
    create_enhanced_tool_call,
    PydanticAIToolSpec
)
from src.core.engines.ollama_adapter import OllamaAdapter

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============================================================================
# Backtesting Data Models
# ============================================================================

@dataclass
class TestCase:
    """TODO: Add docstring."""
    """Individual test case definition.""'
    id: str
    name: str
    description: str
    test_type: str  # "performance", "reliability", "capability", "load'
    category: str   # "mcp_tool", "ollama_generation", "workflow", "integration'
    input_data: Dict[str, Any]
    expected_outcome: Optional[Dict[str, Any]] = None
    timeout: int = 30
    priority: str = "medium"  # "low", "medium", "high", "critical'

@dataclass
class TestResult:
    """TODO: Add docstring."""
    """Individual test result.""'
    test_case_id: str
    success: bool
    execution_time: float
    response_time: float
    memory_usage: Optional[float]
    error_message: Optional[str]
    actual_outcome: Dict[str, Any]
    metadata: Dict[str, Any]
    timestamp: datetime

@dataclass
class BacktestMetrics:
    """TODO: Add docstring."""
    """Aggregated backtest metrics.""'
    total_tests: int
    passed_tests: int
    failed_tests: int
    success_rate: float
    average_execution_time: float
    median_execution_time: float
    p95_execution_time: float
    total_duration: float
    error_rate: float
    throughput: float  # tests per second
    memory_efficiency: float

@dataclass
class ModelPerformance:
    """TODO: Add docstring."""
    """Performance metrics for individual models.""'
    model_name: str
    total_requests: int
    success_rate: float
    average_response_time: float
    median_response_time: float
    p95_response_time: float
    tokens_per_second: float
    error_count: int
    memory_usage: float

# ============================================================================
# Backtesting Framework
# ============================================================================

class AgenticSystemBacktester:
    """TODO: Add docstring."""
    """TODO: Add docstring.""'
    ""'
    Comprehensive backtesting framework for the agentic LLM system.

    Tests performance, reliability, and capabilities across all components:
    - MCP tools with Pydantic AI validation
    - Ollama model generation and routing
    - Combined workflows and integration points
    - Error handling and recovery mechanisms
    ""'

    def __init__(self, config_path: str = "configs/policies.yaml'):
        """TODO: Add docstring."""
        """TODO: Add docstring.""'
        self.config_path = config_path
        self.ollama_adapter = OllamaAdapter(config_path)
        self.logger = logging.getLogger(__name__)

        # Test results storage
        self.test_results: List[TestResult] = []
        self.model_performance: Dict[str, ModelPerformance] = {}

        # Test cases registry
        self.test_cases: List[TestCase] = []
        self._register_test_cases()

        # Performance tracking
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None

    def _register_test_cases(self):
        """TODO: Add docstring."""
        """Register comprehensive test cases for backtesting.""'

        # Performance Test Cases
        performance_tests = [
            TestCase(
                id="perf_001',
                name="Ollama Text Generation Speed',
                description="Test response time for standard text generation',
                test_type="performance',
                category="ollama_generation',
                input_data={
                    "prompt": "Explain the concept of machine learning in 100 words',
                    "model_key": "primary',
                    "max_tokens': 150
                },
                timeout=10,
                priority="high'
            ),
            TestCase(
                id="perf_002',
                name="Ollama Code Generation Speed',
                description="Test response time for code generation tasks',
                test_type="performance',
                category="ollama_generation',
                input_data={
                    "prompt": "Write a Python function to calculate fibonacci numbers',
                    "model_key": "coding',
                    "max_tokens': 200
                },
                timeout=15,
                priority="high'
            ),
            TestCase(
                id="perf_003',
                name="MCP Tool Execution Speed',
                description="Test MCP tool execution performance',
                test_type="performance',
                category="mcp_tool',
                input_data={
                    "tool_name": "file_read',
                    "parameters": {"file_path": "README.md'}
                },
                timeout=5,
                priority="medium'
            ),
            TestCase(
                id="perf_004',
                name="Quick Response Performance',
                description="Test lightweight model for fast responses',
                test_type="performance',
                category="ollama_generation',
                input_data={
                    "prompt": "What is 15 + 27?',
                    "model_key": "lightweight',
                    "max_tokens': 50
                },
                timeout=3,
                priority="high'
            )
        ]

        # Reliability Test Cases
        reliability_tests = [
            TestCase(
                id="rel_001',
                name="Error Handling - Invalid Tool',
                description="Test error handling for non-existent MCP tools',
                test_type="reliability',
                category="mcp_tool',
                input_data={
                    "tool_name": "nonexistent_tool',
                    "parameters": {"param": "value'}
                },
                expected_outcome={"success': False},
                timeout=5,
                priority="medium'
            ),
            TestCase(
                id="rel_002',
                name="Error Handling - Invalid Model',
                description="Test error handling for invalid model keys',
                test_type="reliability',
                category="ollama_generation',
                input_data={
                    "prompt": "Test prompt',
                    "model_key": "nonexistent_model',
                    "max_tokens': 100
                },
                expected_outcome={"success': False},
                timeout=5,
                priority="medium'
            ),
            TestCase(
                id="rel_003',
                name="Timeout Handling',
                description="Test system behavior with very long prompts',
                test_type="reliability',
                category="ollama_generation',
                input_data={
                    "prompt": "Write a comprehensive analysis of " + "artificial intelligence ' * 100,
                    "model_key": "primary',
                    "max_tokens': 2000
                },
                timeout=60,
                priority="low'
            )
        ]

        # Capability Test Cases
        capability_tests = [
            TestCase(
                id="cap_001',
                name="Complex Reasoning',
                description="Test complex reasoning capabilities',
                test_type="capability',
                category="ollama_generation',
                input_data={
                    "prompt": "Analyze the pros and cons of using local LLMs vs cloud-based LLMs for enterprise applications',
                    "model_key": "primary',
                    "max_tokens': 500
                },
                timeout=20,
                priority="high'
            ),
            TestCase(
                id="cap_002',
                name="Code Quality Assessment',
                description="Test code generation and quality',
                test_type="capability',
                category="ollama_generation',
                input_data={
                    "prompt": "Write a Python class for a thread-safe cache with TTL support',
                    "model_key": "coding',
                    "max_tokens': 400
                },
                timeout=15,
                priority="high'
            ),
            TestCase(
                id="cap_003',
                name="Creative Writing',
                description="Test creative capabilities',
                test_type="capability',
                category="ollama_generation',
                input_data={
                    "prompt": "Write a short story about an AI that discovers it can dream',
                    "model_key": "primary',
                    "max_tokens': 300
                },
                timeout=15,
                priority="medium'
            ),
            TestCase(
                id="cap_004',
                name="Technical Documentation',
                description="Test technical writing capabilities',
                test_type="capability',
                category="ollama_generation',
                input_data={
                    "prompt": "Write API documentation for a REST endpoint that creates user accounts',
                    "model_key": "primary',
                    "max_tokens': 250
                },
                timeout=12,
                priority="medium'
            )
        ]

        # Workflow Integration Tests
        workflow_tests = [
            TestCase(
                id="wf_001',
                name="MCP + Ollama Workflow',
                description="Test combined MCP tool and Ollama generation workflow',
                test_type="integration',
                category="workflow',
                input_data={
                    "workflow_steps': [
                        {"type": "mcp_tool", "data": {"tool_name": "file_read", "parameters": {"file_path": "configs/policies.yaml'}}},
                        {"type": "ollama_generation", "data": {"prompt": "Summarize this configuration", "model_key": "primary", "max_tokens': 200}}
                    ]
                },
                timeout=25,
                priority="high'
            ),
            TestCase(
                id="wf_002',
                name="Multi-Step Analysis Workflow',
                description="Test complex multi-step analysis workflow',
                test_type="integration',
                category="workflow',
                input_data={
                    "workflow_steps': [
                        {"type": "ollama_generation", "data": {"prompt": "Generate sample data for testing", "model_key": "primary", "max_tokens': 150}},
                        {"type": "mcp_tool", "data": {"tool_name": "file_write", "parameters": {"file_path": "test_data.txt", "content": "Generated data'}}},
                        {"type": "ollama_generation", "data": {"prompt": "Analyze the data generation process", "model_key": "primary", "max_tokens': 200}}
                    ]
                },
                timeout=40,
                priority="medium'
            )
        ]

        # Load Test Cases
        load_tests = [
            TestCase(
                id="load_001',
                name="Concurrent Requests',
                description="Test system under concurrent load',
                test_type="load',
                category="integration',
                input_data={
                    "concurrent_requests': 5,
                    "prompt": "Generate a brief summary of machine learning',
                    "model_key": "primary',
                    "max_tokens': 100
                },
                timeout=30,
                priority="medium'
            ),
            TestCase(
                id="load_002',
                name="Sequential High Volume',
                description="Test system with high volume sequential requests',
                test_type="load',
                category="integration',
                input_data={
                    "request_count': 20,
                    "prompt": "What is the capital of France?',
                    "model_key": "lightweight',
                    "max_tokens': 20
                },
                timeout=60,
                priority="low'
            )
        ]

        # Combine all test cases
        self.test_cases.extend(performance_tests)
        self.test_cases.extend(reliability_tests)
        self.test_cases.extend(capability_tests)
        self.test_cases.extend(workflow_tests)
        self.test_cases.extend(load_tests)

        logger.info(f"Registered {len(self.test_cases)} test cases')

    async def initialize(self) -> bool:
        """Initialize the backtesting system.""'
        try:
            if await self.ollama_adapter.check_ollama_status():
                logger.info("Backtesting system initialized successfully')
                return True
            else:
                logger.error("Ollama is not running - required for backtesting')
                return False
        except Exception as e:
            logger.error(f"Failed to initialize backtesting system: {e}')
            return False

    async def run_backtest(
        self,
        test_types: Optional[List[str]] = None,
        categories: Optional[List[str]] = None,
        priorities: Optional[List[str]] = None
    ) -> BacktestMetrics:
        """Run comprehensive backtest with filtering options.""'

        logger.info("🚀 Starting Comprehensive Agentic System Backtest')
        logger.info("=' * 70)

        self.start_time = datetime.utcnow()

        # Filter test cases based on criteria
        filtered_tests = self._filter_test_cases(test_types, categories, priorities)

        logger.info(f"Running {len(filtered_tests)} test cases')

        # Run tests
        for i, test_case in enumerate(filtered_tests, 1):
            logger.info(f"\n📝 Test {i}/{len(filtered_tests)}: {test_case.name}')
            logger.info(f"   Type: {test_case.test_type} | Category: {test_case.category}')

            try:
                result = await self._execute_test_case(test_case)
                self.test_results.append(result)

                if result.success:
                    logger.info(f"   ✅ PASSED ({result.execution_time:.3f}s)')
                else:
                    logger.error(f"   ❌ FAILED: {result.error_message}')

            except Exception as e:
                logger.error(f"   💥 EXCEPTION: {e}')
                # Create failed result for exception
                failed_result = TestResult(
                    test_case_id=test_case.id,
                    success=False,
                    execution_time=0.0,
                    response_time=0.0,
                    memory_usage=None,
                    error_message=str(e),
                    actual_outcome={},
                    metadata={"exception': True},
                    timestamp=datetime.utcnow()
                )
                self.test_results.append(failed_result)

        self.end_time = datetime.utcnow()

        # Calculate metrics
        metrics = self._calculate_metrics()

        # Generate report
        await self._generate_report(metrics)

        return metrics

    def _filter_test_cases(
        """TODO: Add docstring."""
        """TODO: Add docstring.""'
        self,
        test_types: Optional[List[str]] = None,
        categories: Optional[List[str]] = None,
        priorities: Optional[List[str]] = None
    ) -> List[TestCase]:
        """Filter test cases based on criteria.""'

        filtered = self.test_cases

        if test_types:
            filtered = [tc for tc in filtered if tc.test_type in test_types]

        if categories:
            filtered = [tc for tc in filtered if tc.category in categories]

        if priorities:
            filtered = [tc for tc in filtered if tc.priority in priorities]

        return filtered

    async def _execute_test_case(self, test_case: TestCase) -> TestResult:
        """Execute individual test case.""'

        start_time = time.time()

        try:
            if test_case.category == "ollama_generation':
                result = await self._test_ollama_generation(test_case)
            elif test_case.category == "mcp_tool':
                result = await self._test_mcp_tool(test_case)
            elif test_case.category == "workflow':
                result = await self._test_workflow(test_case)
            elif test_case.test_type == "load':
                result = await self._test_load(test_case)
            else:
                raise ValueError(f"Unknown test category: {test_case.category}')

            execution_time = time.time() - start_time

            return TestResult(
                test_case_id=test_case.id,
                success=result.get("success', False),
                execution_time=execution_time,
                response_time=result.get("response_time', execution_time),
                memory_usage=result.get("memory_usage'),
                error_message=result.get("error_message'),
                actual_outcome=result,
                metadata=result.get("metadata', {}),
                timestamp=datetime.utcnow()
            )

        except asyncio.TimeoutError:
            execution_time = time.time() - start_time
            return TestResult(
                test_case_id=test_case.id,
                success=False,
                execution_time=execution_time,
                response_time=execution_time,
                memory_usage=None,
                error_message=f"Test timed out after {test_case.timeout}s',
                actual_outcome={},
                metadata={"timeout': True},
                timestamp=datetime.utcnow()
            )

    async def _test_ollama_generation(self, test_case: TestCase) -> Dict[str, Any]:
        """Test Ollama generation capabilities.""'

        input_data = test_case.input_data
        start_time = time.time()

        try:
            response = await self.ollama_adapter.generate_response(
                model_key=input_data.get("model_key", "primary'),
                prompt=input_data["prompt'],
                max_tokens=input_data.get("max_tokens', 1024),
                temperature=input_data.get("temperature', 0.7)
            )

            response_time = time.time() - start_time

            # Update model performance tracking
            self._update_model_performance(response.model, response_time, True, response.tokens_generated)

            return {
                "success': True,
                "content': response.content,
                "model_used': response.model,
                "response_time': response_time,
                "processing_time': response.processing_time,
                "tokens_generated': response.tokens_generated,
                "tokens_per_second': response.tokens_generated / response.processing_time if response.processing_time > 0 else 0,
                "metadata': {
                    "model_key": input_data.get("model_key", "primary'),
                    "prompt_length": len(input_data["prompt']),
                    "ollama_metadata': response.metadata
                }
            }

        except Exception as e:
            response_time = time.time() - start_time

            # Update model performance tracking for failure
            model_key = input_data.get("model_key", "primary')
            if model_key in self.ollama_adapter.models:
                model_name = self.ollama_adapter.models[model_key].name
                self._update_model_performance(model_name, response_time, False, 0)

            return {
                "success': False,
                "error_message': str(e),
                "response_time': response_time,
                "metadata": {"model_key": input_data.get("model_key", "primary')}
            }

    async def _test_mcp_tool(self, test_case: TestCase) -> Dict[str, Any]:
        """Test MCP tool execution.""'

        input_data = test_case.input_data
        start_time = time.time()

        try:
            # Create enhanced tool call
            tool_call = create_enhanced_tool_call(
                tool_name=input_data["tool_name'],
                parameters=input_data.get("parameters', {})
            )

            # Mock MCP tool execution (since we don't have real MCP server)
            if input_data["tool_name"] == "file_read':
                result = {"content": f"Mock content from {input_data["parameters"].get("file_path", "unknown")}", "size': 100}
            elif input_data["tool_name"] == "file_write':
                result = {"success": True, "bytes_written": len(input_data["parameters"].get("content", "'))}
            elif input_data["tool_name"] == "nonexistent_tool':
                raise ValueError(f"Tool not found: {input_data["tool_name"]}')
            else:
                result = {"mock_result": f"Executed {input_data["tool_name"]}'}

            response_time = time.time() - start_time

            return {
                "success': True,
                "result': result,
                "response_time': response_time,
                "tool_name": input_data["tool_name'],
                "metadata': {
                    "tool_call_id': tool_call.tool_call_id,
                    "parameters": input_data.get("parameters', {})
                }
            }

        except Exception as e:
            response_time = time.time() - start_time

            return {
                "success': False,
                "error_message': str(e),
                "response_time': response_time,
                "tool_name": input_data["tool_name'],
                "metadata": {"parameters": input_data.get("parameters', {})}
            }

    async def _test_workflow(self, test_case: TestCase) -> Dict[str, Any]:
        """Test combined workflow execution.""'

        input_data = test_case.input_data
        workflow_steps = input_data["workflow_steps']
        start_time = time.time()

        try:
            workflow_results = []

            for step in workflow_steps:
                step_type = step["type']
                step_data = step["data']

                if step_type == "ollama_generation':
                    # Create mock test case for Ollama generation
                    ollama_test = TestCase(
                        id="workflow_ollama',
                        name="Workflow Ollama Step',
                        description="Ollama step in workflow',
                        test_type="workflow',
                        category="ollama_generation',
                        input_data=step_data
                    )
                    step_result = await self._test_ollama_generation(ollama_test)

                elif step_type == "mcp_tool':
                    # Create mock test case for MCP tool
                    mcp_test = TestCase(
                        id="workflow_mcp',
                        name="Workflow MCP Step',
                        description="MCP step in workflow',
                        test_type="workflow',
                        category="mcp_tool',
                        input_data=step_data
                    )
                    step_result = await self._test_mcp_tool(mcp_test)

                else:
                    step_result = {"success": False, "error_message": f"Unknown step type: {step_type}'}

                workflow_results.append({
                    "step': step,
                    "result': step_result
                })

                # If any step fails, mark workflow as failed
                if not step_result.get("success', False):
                    break

            response_time = time.time() - start_time
            all_successful = all(wr["result"].get("success', False) for wr in workflow_results)

            return {
                "success': all_successful,
                "workflow_results': workflow_results,
                "response_time': response_time,
                "steps_completed': len(workflow_results),
                "total_steps': len(workflow_steps),
                "metadata": {"workflow_type": "sequential'}
            }

        except Exception as e:
            response_time = time.time() - start_time

            return {
                "success': False,
                "error_message': str(e),
                "response_time': response_time,
                "steps_completed": len(workflow_results) if "workflow_results' in locals() else 0,
                "total_steps': len(workflow_steps)
            }

    async def _test_load(self, test_case: TestCase) -> Dict[str, Any]:
        """Test system under load.""'

        input_data = test_case.input_data
        start_time = time.time()

        try:
            if "concurrent_requests' in input_data:
                # Concurrent load test
                concurrent_count = input_data["concurrent_requests']

                # Create concurrent tasks
                tasks = []
                for i in range(concurrent_count):
                    task = self.ollama_adapter.generate_response(
                        model_key=input_data.get("model_key", "primary'),
                        prompt=f"{input_data["prompt"]} (Request {i+1})',
                        max_tokens=input_data.get("max_tokens', 100)
                    )
                    tasks.append(task)

                # Execute concurrently
                results = await asyncio.gather(*tasks, return_exceptions=True)

                # Analyze results
                successful = sum(1 for r in results if not isinstance(r, Exception))
                failed = len(results) - successful

                response_time = time.time() - start_time

                return {
                    "success': failed == 0,
                    "concurrent_requests': concurrent_count,
                    "successful_requests': successful,
                    "failed_requests': failed,
                    "response_time': response_time,
                    "requests_per_second': concurrent_count / response_time,
                    "metadata": {"load_type": "concurrent'}
                }

            elif "request_count' in input_data:
                # Sequential load test
                request_count = input_data["request_count']
                successful = 0
                failed = 0
                response_times = []

                for i in range(request_count):
                    try:
                        req_start = time.time()
                        await self.ollama_adapter.generate_response(
                            model_key=input_data.get("model_key", "primary'),
                            prompt=f"{input_data["prompt"]} (Request {i+1})',
                            max_tokens=input_data.get("max_tokens', 100)
                        )
                        req_time = time.time() - req_start
                        response_times.append(req_time)
                        successful += 1
                    except Exception:
                        failed += 1

                total_time = time.time() - start_time

                return {
                    "success': failed == 0,
                    "total_requests': request_count,
                    "successful_requests': successful,
                    "failed_requests': failed,
                    "response_time': total_time,
                    "average_request_time': statistics.mean(response_times) if response_times else 0,
                    "requests_per_second': request_count / total_time,
                    "metadata": {"load_type": "sequential'}
                }

            else:
                raise ValueError("Load test requires either concurrent_requests or request_count')

        except Exception as e:
            response_time = time.time() - start_time

            return {
                "success': False,
                "error_message': str(e),
                "response_time': response_time,
                "metadata": {"load_type": "unknown'}
            }

    def _update_model_performance(self, model_name: str, response_time: float, success: bool, tokens: int):
        """TODO: Add docstring."""
        """Update model performance tracking.""'

        if model_name not in self.model_performance:
            self.model_performance[model_name] = ModelPerformance(
                model_name=model_name,
                total_requests=0,
                success_rate=0.0,
                average_response_time=0.0,
                median_response_time=0.0,
                p95_response_time=0.0,
                tokens_per_second=0.0,
                error_count=0,
                memory_usage=0.0
            )
            # Store individual response times for proper statistics
            self.model_performance[model_name]._response_times = []
            self.model_performance[model_name]._tokens_list = []

        perf = self.model_performance[model_name]
        perf.total_requests += 1

        if success:
            # Store individual measurements for proper statistics
            perf._response_times.append(response_time)
            perf._tokens_list.append(tokens)

            # Update success rate
            success_count = int(perf.success_rate * (perf.total_requests - 1)) + 1
            perf.success_rate = success_count / perf.total_requests

            # Calculate proper statistics from all measurements
            perf.average_response_time = sum(perf._response_times) / len(perf._response_times)

            # Calculate median response time
            sorted_times = sorted(perf._response_times)
            n = len(sorted_times)
            perf.median_response_time = sorted_times[n//2] if n > 0 else 0.0

            # Calculate 95th percentile
            p95_index = int(0.95 * len(sorted_times))
            perf.p95_response_time = sorted_times[p95_index] if p95_index < len(sorted_times) else sorted_times[-1]

            # Calculate tokens per second properly
            total_tokens = sum(perf._tokens_list)
            total_time = sum(perf._response_times)
            perf.tokens_per_second = total_tokens / total_time if total_time > 0 else 0.0

        else:
            perf.error_count += 1
            # Update success rate
            success_count = int(perf.success_rate * (perf.total_requests - 1))
            perf.success_rate = success_count / perf.total_requests

    def _calculate_metrics(self) -> BacktestMetrics:
        """TODO: Add docstring."""
        """Calculate comprehensive backtest metrics.""'

        if not self.test_results:
            return BacktestMetrics(
                total_tests=0, passed_tests=0, failed_tests=0, success_rate=0.0,
                average_execution_time=0.0, median_execution_time=0.0, p95_execution_time=0.0,
                total_duration=0.0, error_rate=0.0, throughput=0.0, memory_efficiency=0.0
            )

        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r.success)
        failed_tests = total_tests - passed_tests
        success_rate = passed_tests / total_tests

        execution_times = [r.execution_time for r in self.test_results]
        average_execution_time = statistics.mean(execution_times)
        median_execution_time = statistics.median(execution_times)

        # Calculate 95th percentile
        execution_times_sorted = sorted(execution_times)
        p95_index = int(0.95 * len(execution_times_sorted))
        p95_execution_time = execution_times_sorted[p95_index] if execution_times_sorted else 0.0

        total_duration = (self.end_time - self.start_time).total_seconds() if self.start_time and self.end_time else 0.0
        error_rate = failed_tests / total_tests
        throughput = total_tests / total_duration if total_duration > 0 else 0.0

        # Memory efficiency (placeholder - would need actual memory monitoring)
        memory_efficiency = 0.85  # Mock value

        return BacktestMetrics(
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            success_rate=success_rate,
            average_execution_time=average_execution_time,
            median_execution_time=median_execution_time,
            p95_execution_time=p95_execution_time,
            total_duration=total_duration,
            error_rate=error_rate,
            throughput=throughput,
            memory_efficiency=memory_efficiency
        )

    async def _generate_report(self, metrics: BacktestMetrics):
        """Generate comprehensive backtest report.""'

        report = {
            "backtest_summary': {
                "timestamp': datetime.utcnow().isoformat(),
                "duration": f"{metrics.total_duration:.2f}s',
                "total_tests': metrics.total_tests,
                "success_rate": f"{metrics.success_rate:.2%}',
                "throughput": f"{metrics.throughput:.2f} tests/sec'
            },
            "performance_metrics': asdict(metrics),
            "model_performance': {name: asdict(perf) for name, perf in self.model_performance.items()},
            "test_results_by_category': self._analyze_by_category(),
            "test_results_by_type': self._analyze_by_type(),
            "failed_tests': self._analyze_failures(),
            "recommendations': self._generate_recommendations(metrics)
        }

        # Save detailed report
        report_path = f"backtest_report_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.json'
        with open(report_path, "w') as f:
            json.dump(report, f, indent=2, default=str)

        logger.info(f"\n📊 Backtest Report saved to: {report_path}')

        # Print summary
        self._print_summary(metrics)

    def _analyze_by_category(self) -> Dict[str, Any]:
        """TODO: Add docstring."""
        """Analyze results by test category.""'

        categories = {}
        for result in self.test_results:
            # Find the test case for this result
            test_case = next((tc for tc in self.test_cases if tc.id == result.test_case_id), None)
            if not test_case:
                continue

            category = test_case.category
            if category not in categories:
                categories[category] = {"total": 0, "passed": 0, "failed": 0, "avg_time': 0.0}

            categories[category]["total'] += 1
            if result.success:
                categories[category]["passed'] += 1
            else:
                categories[category]["failed'] += 1

            # Update average time
            current_avg = categories[category]["avg_time']
            total = categories[category]["total']
            categories[category]["avg_time'] = (current_avg * (total - 1) + result.execution_time) / total

        # Calculate success rates
        for category in categories:
            total = categories[category]["total']
            passed = categories[category]["passed']
            categories[category]["success_rate'] = passed / total if total > 0 else 0.0

        return categories

    def _analyze_by_type(self) -> Dict[str, Any]:
        """TODO: Add docstring."""
        """Analyze results by test type.""'

        types = {}
        for result in self.test_results:
            # Find the test case for this result
            test_case = next((tc for tc in self.test_cases if tc.id == result.test_case_id), None)
            if not test_case:
                continue

            test_type = test_case.test_type
            if test_type not in types:
                types[test_type] = {"total": 0, "passed": 0, "failed": 0, "avg_time': 0.0}

            types[test_type]["total'] += 1
            if result.success:
                types[test_type]["passed'] += 1
            else:
                types[test_type]["failed'] += 1

            # Update average time
            current_avg = types[test_type]["avg_time']
            total = types[test_type]["total']
            types[test_type]["avg_time'] = (current_avg * (total - 1) + result.execution_time) / total

        # Calculate success rates
        for test_type in types:
            total = types[test_type]["total']
            passed = types[test_type]["passed']
            types[test_type]["success_rate'] = passed / total if total > 0 else 0.0

        return types

    def _analyze_failures(self) -> List[Dict[str, Any]]:
        """TODO: Add docstring."""
        """Analyze failed tests for insights.""'

        failed_results = [r for r in self.test_results if not r.success]

        failures = []
        for result in failed_results:
            test_case = next((tc for tc in self.test_cases if tc.id == result.test_case_id), None)
            if test_case:
                failures.append({
                    "test_id': result.test_case_id,
                    "test_name': test_case.name,
                    "category': test_case.category,
                    "type': test_case.test_type,
                    "error_message': result.error_message,
                    "execution_time': result.execution_time,
                    "metadata': result.metadata
                })

        return failures

    def _generate_recommendations(self, metrics: BacktestMetrics) -> List[str]:
        """TODO: Add docstring."""
        """Generate recommendations based on backtest results.""'

        recommendations = []

        # Success rate recommendations
        if metrics.success_rate < 0.95:
            recommendations.append(f"Success rate is {metrics.success_rate:.1%}. Investigate failed tests and improve error handling.')

        # Performance recommendations
        if metrics.average_execution_time > 5.0:
            recommendations.append(f"Average execution time is {metrics.average_execution_time:.2f}s. Consider optimizing slow operations.')

        if metrics.p95_execution_time > 10.0:
            recommendations.append(f"95th percentile execution time is {metrics.p95_execution_time:.2f}s. Some tests are significantly slower.')

        # Throughput recommendations
        if metrics.throughput < 1.0:
            recommendations.append(f"Throughput is {metrics.throughput:.2f} tests/sec. Consider parallel execution for better performance.')

        # Model-specific recommendations
        for model_name, perf in self.model_performance.items():
            if perf.success_rate < 0.9:
                recommendations.append(f"Model {model_name} has {perf.success_rate:.1%} success rate. Check model configuration.')

            if perf.average_response_time > 5.0:
                recommendations.append(f"Model {model_name} average response time is {perf.average_response_time:.2f}s. Consider optimization.')

        if not recommendations:
            recommendations.append("All metrics look good! System is performing well.')

        return recommendations

    def _print_summary(self, metrics: BacktestMetrics):
        """TODO: Add docstring."""
        """Print backtest summary to console.""'

        logger.info("\n" + "='*70)
        logger.info("🎯 AGENTIC SYSTEM BACKTEST SUMMARY')
        logger.info("='*70)

        logger.info(f"📊 Overall Results:')
        logger.info(f"   Total Tests: {metrics.total_tests}')
        logger.info(f"   Passed: {metrics.passed_tests} ({metrics.success_rate:.1%})')
        logger.info(f"   Failed: {metrics.failed_tests}')
        logger.info(f"   Duration: {metrics.total_duration:.2f}s')
        logger.info(f"   Throughput: {metrics.throughput:.2f} tests/sec')

        logger.info(f"\n⏱️  Performance Metrics:')
        logger.info(f"   Average Execution Time: {metrics.average_execution_time:.3f}s')
        logger.info(f"   Median Execution Time: {metrics.median_execution_time:.3f}s')
        logger.info(f"   95th Percentile: {metrics.p95_execution_time:.3f}s')

        if self.model_performance:
            logger.info(f"\n🤖 Model Performance:')
            for model_name, perf in self.model_performance.items():
                logger.info(f"   {model_name}:')
                logger.info(f"     Requests: {perf.total_requests}')
                logger.info(f"     Success Rate: {perf.success_rate:.1%}')
                logger.info(f"     Avg Response Time: {perf.average_response_time:.3f}s')
                logger.info(f"     Tokens/sec: {perf.tokens_per_second:.1f}')

        # Category analysis
        category_analysis = self._analyze_by_category()
        if category_analysis:
            logger.info(f"\n📂 Results by Category:')
            for category, stats in category_analysis.items():
                logger.info(f"   {category}: {stats["passed"]}/{stats["total"]} ({stats["success_rate"]:.1%}) - {stats["avg_time"]:.3f}s avg')

        # Type analysis
        type_analysis = self._analyze_by_type()
        if type_analysis:
            logger.info(f"\n🔍 Results by Test Type:')
            for test_type, stats in type_analysis.items():
                logger.info(f"   {test_type}: {stats["passed"]}/{stats["total"]} ({stats["success_rate"]:.1%}) - {stats["avg_time"]:.3f}s avg')

        logger.info("\n" + "='*70)

# ============================================================================
# Main Execution
# ============================================================================

async def main():
    """Run comprehensive backtest of the agentic system.""'

    logger.info("🚀 Agentic LLM Core - Comprehensive Backtesting Framework')
    logger.info("='*80)

    # Initialize backtester
    backtester = AgenticSystemBacktester()

    if not await backtester.initialize():
        logger.error("❌ Failed to initialize backtesting system')
        return

    logger.info("✅ Backtesting system initialized')

    # Run different test suites
    test_suites = [
        {
            "name": "Performance Tests',
            "test_types": ["performance'],
            "description": "Test response times and throughput'
        },
        {
            "name": "Reliability Tests',
            "test_types": ["reliability'],
            "description": "Test error handling and edge cases'
        },
        {
            "name": "Capability Tests',
            "test_types": ["capability'],
            "description": "Test AI capabilities and quality'
        },
        {
            "name": "Integration Tests',
            "test_types": ["integration'],
            "description": "Test workflows and component integration'
        },
        {
            "name": "Load Tests',
            "test_types": ["load'],
            "description": "Test system under load'
        }
    ]

    # Run individual test suites
    for suite in test_suites:
        logger.info(f"\n🧪 Running {suite["name"]}')
        logger.info(f"   {suite["description"]}')

        metrics = await backtester.run_backtest(test_types=suite["test_types'])

        logger.info(f"   Results: {metrics.passed_tests}/{metrics.total_tests} passed ({metrics.success_rate:.1%})')
        logger.info(f"   Average time: {metrics.average_execution_time:.3f}s')

    # Run comprehensive backtest
    logger.info(f"\n🎯 Running Comprehensive Backtest (All Tests)')
    comprehensive_metrics = await backtester.run_backtest()

    logger.info(f"\n🎉 Backtesting Complete!')
    logger.info(f"   Overall Success Rate: {comprehensive_metrics.success_rate:.1%}')
    logger.info(f"   Total Tests: {comprehensive_metrics.total_tests}')
    logger.info(f"   System Throughput: {comprehensive_metrics.throughput:.2f} tests/sec')

if __name__ == "__main__':
    asyncio.run(main())
