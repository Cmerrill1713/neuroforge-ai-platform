""'
Task Runner Example

This example demonstrates how to use the task runner to execute TaskGraphs
with tool selection, retry mechanisms, comprehensive logging, and evidence capture.

Created: 2024-09-24
Status: Draft
""'

import asyncio
import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List

from src.core.runtime.runner import (
    create_task_runner,
    create_runner_config,
    ExecutionStatus,
    RetryStrategy,
    LogLevel,
    ToolExecutor,
    MockToolExecutor
)

from src.core.models.contracts import Task, TaskGraph, TaskStatus, ToolSpec, ToolParameter


# ============================================================================
# Custom Tool Executor Example
# ============================================================================

class CustomToolExecutor(ToolExecutor):
    """TODO: Add docstring."""
    """Custom tool executor for demonstration.""'

    def __init__(self):
        """TODO: Add docstring."""
        """TODO: Add docstring.""'
        self.tools = [
            ToolSpec(
                name="data_processor',
                description="Process data with various operations',
                parameters=[
                    ToolParameter(name="data", type="list", description="Data to process'),
                    ToolParameter(name="operation", type="str", description="Operation to perform'),
                    ToolParameter(name="options", type="dict", description="Processing options', default={})
                ],
                returns={"result": "list", "metadata": "dict'},
                category="data'
            ),
            ToolSpec(
                name="file_operations',
                description="Perform file operations',
                parameters=[
                    ToolParameter(name="operation", type="str", description="File operation'),
                    ToolParameter(name="path", type="str", description="File path'),
                    ToolParameter(name="content", type="str", description="File content", default="')
                ],
                returns={"success": "bool", "message": "str'},
                category="file'
            ),
            ToolSpec(
                name="api_client',
                description="Make API calls',
                parameters=[
                    ToolParameter(name="url", type="str", description="API URL'),
                    ToolParameter(name="method", type="str", description="HTTP method'),
                    ToolParameter(name="headers", type="dict", description="Request headers', default={}),
                    ToolParameter(name="data", type="dict", description="Request data', default={})
                ],
                returns={"status_code": "int", "response": "dict'},
                category="network'
            ),
            ToolSpec(
                name="database_query',
                description="Execute database queries',
                parameters=[
                    ToolParameter(name="query", type="str", description="SQL query'),
                    ToolParameter(name="params", type="dict", description="Query parameters', default={})
                ],
                returns={"rows": "list", "count": "int'},
                category="database'
            ),
            ToolSpec(
                name="ml_predictor',
                description="Make ML predictions',
                parameters=[
                    ToolParameter(name="model", type="str", description="Model name'),
                    ToolParameter(name="features", type="list", description="Input features'),
                    ToolParameter(name="confidence_threshold", type="float", description="Confidence threshold', default=0.8)
                ],
                returns={"prediction": "any", "confidence": "float'},
                category="ml'
            )
        ]

    async def execute(self, tool_name: str, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool with given parameters.""'
        if tool_name == "data_processor':
            return await self._execute_data_processor(parameters)
        elif tool_name == "file_operations':
            return await self._execute_file_operations(parameters)
        elif tool_name == "api_client':
            return await self._execute_api_client(parameters)
        elif tool_name == "database_query':
            return await self._execute_database_query(parameters)
        elif tool_name == "ml_predictor':
            return await self._execute_ml_predictor(parameters)
        else:
            raise ValueError(f"Unknown tool: {tool_name}')

    def get_available_tools(self) -> List[ToolSpec]:
        """TODO: Add docstring."""
        """Get list of available tools.""'
        return self.tools

    def validate_tool_call(self, tool_name: str, parameters: Dict[str, Any]) -> bool:
        """TODO: Add docstring."""
        """Validate tool call parameters.""'
        tool_spec = next((tool for tool in self.tools if tool.name == tool_name), None)
        if not tool_spec:
            return False

        # Check required parameters
        required_params = [param.name for param in tool_spec.parameters if param.required]
        return all(param in parameters for param in required_params)

    async def _execute_data_processor(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute data processing tool.""'
        data = parameters.get("data', [])
        operation = parameters.get("operation", "sum')
        options = parameters.get("options', {})

        # Simulate processing time
        await asyncio.sleep(0.2)

        if operation == "sum':
            result = sum(data) if data else 0
        elif operation == "average':
            result = sum(data) / len(data) if data else 0
        elif operation == "filter':
            threshold = options.get("threshold', 0)
            result = [x for x in data if x > threshold]
        elif operation == "sort':
            reverse = options.get("reverse', False)
            result = sorted(data, reverse=reverse)
        else:
            result = data

        return {
            "result': result,
            "metadata': {
                "operation': operation,
                "input_size': len(data),
                "processing_time': 0.2
            }
        }

    async def _execute_file_operations(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute file operations tool.""'
        operation = parameters.get("operation", "read')
        path = parameters.get("path", "')
        content = parameters.get("content", "')

        # Simulate file operation
        await asyncio.sleep(0.1)

        if operation == "read':
            # Simulate reading file
            return {"success": True, "message": f"Read file {path}'}
        elif operation == "write':
            # Simulate writing file
            return {"success": True, "message": f"Wrote {len(content)} bytes to {path}'}
        elif operation == "delete':
            # Simulate deleting file
            return {"success": True, "message": f"Deleted file {path}'}
        else:
            return {"success": False, "message": f"Unknown operation: {operation}'}

    async def _execute_api_client(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute API client tool.""'
        url = parameters.get("url", "')
        method = parameters.get("method", "GET')
        headers = parameters.get("headers', {})
        data = parameters.get("data', {})

        # Simulate API call
        await asyncio.sleep(0.3)

        # Simulate different responses based on URL
        if "error' in url.lower():
            return {"status_code": 500, "response": {"error": "Internal server error'}}
        elif "notfound' in url.lower():
            return {"status_code": 404, "response": {"error": "Not found'}}
        else:
            return {
                "status_code': 200,
                "response': {
                    "message": "Success',
                    "data': data,
                    "timestamp': datetime.now().isoformat()
                }
            }

    async def _execute_database_query(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute database query tool.""'
        query = parameters.get("query", "')
        params = parameters.get("params', {})

        # Simulate database query
        await asyncio.sleep(0.15)

        # Simulate different query results
        if "SELECT' in query.upper():
            rows = [
                {"id": 1, "name": "Alice", "age': 30},
                {"id": 2, "name": "Bob", "age': 25},
                {"id": 3, "name": "Charlie", "age': 35}
            ]
            return {"rows": rows, "count': len(rows)}
        elif "INSERT' in query.upper():
            return {"rows": [], "count': 1}
        elif "UPDATE' in query.upper():
            return {"rows": [], "count': 1}
        elif "DELETE' in query.upper():
            return {"rows": [], "count': 1}
        else:
            return {"rows": [], "count': 0}

    async def _execute_ml_predictor(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute ML predictor tool.""'
        model = parameters.get("model", "default')
        features = parameters.get("features', [])
        confidence_threshold = parameters.get("confidence_threshold', 0.8)

        # Simulate ML prediction
        await asyncio.sleep(0.5)

        # Simulate prediction based on features
        if len(features) == 0:
            prediction = "unknown'
            confidence = 0.0
        elif len(features) > 5:
            prediction = "positive'
            confidence = 0.9
        else:
            prediction = "negative'
            confidence = 0.7

        return {
            "prediction': prediction,
            "confidence': confidence,
            "model': model,
            "threshold_met': confidence >= confidence_threshold
        }


# ============================================================================
# Example Usage
# ============================================================================

async def main():
    """Main example function.""'
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    logger.info("Starting Task Runner Example')

    try:
        # 1. Example 1: Basic Task Execution
        logger.info("Example 1: Basic Task Execution')
        await example_basic_execution()

        # 2. Example 2: Parallel Task Execution
        logger.info("Example 2: Parallel Task Execution')
        await example_parallel_execution()

        # 3. Example 3: Sequential Task Execution with Dependencies
        logger.info("Example 3: Sequential Task Execution with Dependencies')
        await example_sequential_execution()

        # 4. Example 4: Retry Mechanisms
        logger.info("Example 4: Retry Mechanisms')
        await example_retry_mechanisms()

        # 5. Example 5: Evidence Capture and Logging
        logger.info("Example 5: Evidence Capture and Logging')
        await example_evidence_logging()

        # 6. Example 6: Complex Workflow
        logger.info("Example 6: Complex Workflow')
        await example_complex_workflow()

        # 7. Example 7: Performance Testing
        logger.info("Example 7: Performance Testing')
        await example_performance_testing()

        logger.info("Task Runner Example completed successfully!')

    except Exception as e:
        logger.error(f"Example failed: {e}')
        raise


async def example_basic_execution():
    """Example: Basic task execution.""'
    logger = logging.getLogger(__name__)

    # Create custom tool executor
    tool_executor = CustomToolExecutor()

    # Create task runner
    runner = create_task_runner(
        max_concurrent_tasks=2,
        task_timeout=30.0,
        max_retries=2,
        retry_strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
        log_level=LogLevel.INFO,
        enable_evidence_capture=True
    )

    # Create simple task
    task = Task(
        task_id="basic_task',
        name="Basic Data Processing',
        description="Process some data using the data processor tool',
        input_data={
            "data': [1, 2, 3, 4, 5],
            "operation": "sum',
            "options': {}
        },
        required_tools=["data_processor'],
        dependencies=[]
    )

    # Create task graph
    task_graph = TaskGraph(
        graph_id="basic_graph',
        name="Basic Graph',
        description="Simple task graph for basic execution',
        tasks=[task],
        entry_points=[task.task_id],
        exit_points=[task.task_id]
    )

    # Execute task graph
    logger.info("Executing basic task graph...')
    start_time = time.time()
    context = await runner.run(task_graph, {"example": "basic_execution'})
    end_time = time.time()

    # Display results
    logger.info(f"Execution Status: {context.status}')
    logger.info(f"Execution Time: {end_time - start_time:.2f}s')
    logger.info(f"Completed Tasks: {len(context.completed_tasks)}')
    logger.info(f"Failed Tasks: {len(context.failed_tasks)}')
    logger.info(f"Retry Count: {context.retry_count}')

    # Show runner statistics
    stats = runner.get_statistics()
    logger.info(f"Runner Statistics: {stats}')


async def example_parallel_execution():
    """Example: Parallel task execution.""'
    logger = logging.getLogger(__name__)

    # Create runner with parallel execution
    runner = create_task_runner(
        max_concurrent_tasks=5,
        enable_parallel_execution=True,
        log_level=LogLevel.INFO
    )

    # Create multiple independent tasks
    tasks = []
    for i in range(5):
        task = Task(
            task_id=f"parallel_task_{i}',
            name=f"Parallel Task {i}',
            description=f"Independent task {i} for parallel execution',
            input_data={
                "data': list(range(i * 10, (i + 1) * 10)),
                "operation": "sum'
            },
            required_tools=["data_processor'],
            dependencies=[]
        )
        tasks.append(task)

    # Create task graph
    task_graph = TaskGraph(
        graph_id="parallel_graph',
        name="Parallel Graph',
        description="Graph with parallel tasks',
        tasks=tasks,
        entry_points=[task.task_id for task in tasks],
        exit_points=[task.task_id for task in tasks]
    )

    # Execute task graph
    logger.info("Executing parallel task graph...')
    start_time = time.time()
    context = await runner.run(task_graph)
    end_time = time.time()

    # Display results
    logger.info(f"Execution Status: {context.status}')
    logger.info(f"Execution Time: {end_time - start_time:.2f}s')
    logger.info(f"Completed Tasks: {len(context.completed_tasks)}')
    logger.info(f"Parallel Efficiency: {len(tasks) / (end_time - start_time):.1f} tasks/second')


async def example_sequential_execution():
    """Example: Sequential task execution with dependencies.""'
    logger = logging.getLogger(__name__)

    # Create runner with sequential execution
    runner = create_task_runner(
        max_concurrent_tasks=1,
        enable_parallel_execution=False,
        log_level=LogLevel.INFO
    )

    # Create tasks with dependencies
    task1 = Task(
        task_id="data_collection',
        name="Data Collection',
        description="Collect data from API',
        input_data={
            "url": "https://api.example.com/data',
            "method": "GET',
            "headers": {"Authorization": "Bearer token'}
        },
        required_tools=["api_client'],
        dependencies=[]
    )

    task2 = Task(
        task_id="data_processing',
        name="Data Processing',
        description="Process collected data',
        input_data={
            "data': [1, 2, 3, 4, 5],  # This would come from task1 output
            "operation": "filter',
            "options": {"threshold': 3}
        },
        required_tools=["data_processor'],
        dependencies=["data_collection']
    )

    task3 = Task(
        task_id="data_storage',
        name="Data Storage',
        description="Store processed data',
        input_data={
            "operation": "write',
            "path": "/data/processed.json',
            "content": "processed data'
        },
        required_tools=["file_operations'],
        dependencies=["data_processing']
    )

    # Create task graph
    task_graph = TaskGraph(
        graph_id="sequential_graph',
        name="Sequential Graph',
        description="Graph with sequential dependencies',
        tasks=[task1, task2, task3],
        entry_points=["data_collection'],
        exit_points=["data_storage']
    )

    # Execute task graph
    logger.info("Executing sequential task graph...')
    start_time = time.time()
    context = await runner.run(task_graph)
    end_time = time.time()

    # Display results
    logger.info(f"Execution Status: {context.status}')
    logger.info(f"Execution Time: {end_time - start_time:.2f}s')
    logger.info(f"Completed Tasks: {context.completed_tasks}')
    logger.info(f"Execution Order: {" -> ".join(context.completed_tasks)}')


async def example_retry_mechanisms():
    """Example: Retry mechanisms with different strategies.""'
    logger = logging.getLogger(__name__)

    # Create custom executor that fails initially
    class RetryableExecutor(CustomToolExecutor):
        """TODO: Add docstring."""
        """TODO: Add docstring.""'
        def __init__(self):
            """TODO: Add docstring."""
            """TODO: Add docstring.""'
            super().__init__()
            self.call_counts = {}

        async def execute(self, tool_name: str, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
            # Track call counts
            key = f"{tool_name}_{parameters.get("operation", "default")}'
            self.call_counts[key] = self.call_counts.get(key, 0) + 1

            # Fail first few times for retry testing
            if key == "data_processor_sum' and self.call_counts[key] <= 2:
                raise Exception(f"Retryable failure (attempt {self.call_counts[key]})')

            return await super().execute(tool_name, parameters, context)

    retryable_executor = RetryableExecutor()

    # Test different retry strategies
    strategies = [
        RetryStrategy.IMMEDIATE,
        RetryStrategy.FIXED_DELAY,
        RetryStrategy.LINEAR_BACKOFF,
        RetryStrategy.EXPONENTIAL_BACKOFF
    ]

    for strategy in strategies:
        logger.info(f"Testing retry strategy: {strategy}')

        # Create runner with specific retry strategy
        runner = create_task_runner(
            max_retries=3,
            retry_strategy=strategy,
            log_level=LogLevel.INFO
        )

        # Create task that will fail initially
        task = Task(
            task_id="retry_task',
            name="Retry Test Task',
            description="Task that fails initially for retry testing',
            input_data={
                "data': [1, 2, 3],
                "operation": "sum'
            },
            required_tools=["data_processor'],
            dependencies=[]
        )

        task_graph = TaskGraph(
            graph_id="retry_graph',
            name="Retry Graph',
            description="Graph for retry testing',
            tasks=[task],
            entry_points=[task.task_id],
            exit_points=[task.task_id]
        )

        # Execute with retry
        start_time = time.time()
        context = await runner.run(task_graph)
        end_time = time.time()

        logger.info(f"  Strategy: {strategy}')
        logger.info(f"  Status: {context.status}')
        logger.info(f"  Retry Count: {context.retry_count}')
        logger.info(f"  Execution Time: {end_time - start_time:.2f}s')


async def example_evidence_logging():
    """Example: Evidence capture and logging.""'
    logger = logging.getLogger(__name__)

    # Create runner with comprehensive evidence capture
    runner = create_task_runner(
        enable_evidence_capture=True,
        log_level=LogLevel.DEBUG,
        max_retries=1
    )

    # Create task with multiple tools
    task = Task(
        task_id="evidence_task',
        name="Evidence Capture Task',
        description="Task for demonstrating evidence capture',
        input_data={
            "data': [10, 20, 30, 40, 50],
            "operation": "average'
        },
        required_tools=["data_processor'],
        dependencies=[]
    )

    task_graph = TaskGraph(
        graph_id="evidence_graph',
        name="Evidence Graph',
        description="Graph for evidence capture demonstration',
        tasks=[task],
        entry_points=[task.task_id],
        exit_points=[task.task_id]
    )

    # Execute with evidence capture
    logger.info("Executing task with evidence capture...')
    context = await runner.run(task_graph, {"evidence_test': True})

    # Display evidence information
    logger.info(f"Execution Status: {context.status}')
    logger.info(f"Evidence captured for task: {task.task_id}')

    # Note: In a real implementation, you would access the evidence capture
    # through the runner's internal components or return it in the context


async def example_complex_workflow():
    """Example: Complex workflow with multiple task types.""'
    logger = logging.getLogger(__name__)

    # Create runner for complex workflow
    runner = create_task_runner(
        max_concurrent_tasks=3,
        task_timeout=60.0,
        max_retries=2,
        log_level=LogLevel.INFO,
        enable_evidence_capture=True
    )

    # Create complex workflow tasks
    tasks = [
        # Data collection phase
        Task(
            task_id="collect_user_data',
            name="Collect User Data',
            description="Collect user data from API',
            input_data={
                "url": "https://api.example.com/users',
                "method": "GET'
            },
            required_tools=["api_client'],
            dependencies=[]
        ),

        Task(
            task_id="collect_product_data',
            name="Collect Product Data',
            description="Collect product data from API',
            input_data={
                "url": "https://api.example.com/products',
                "method": "GET'
            },
            required_tools=["api_client'],
            dependencies=[]
        ),

        # Data processing phase
        Task(
            task_id="process_user_data',
            name="Process User Data',
            description="Process collected user data',
            input_data={
                "data': [1, 2, 3, 4, 5],
                "operation": "filter',
                "options": {"threshold': 2}
            },
            required_tools=["data_processor'],
            dependencies=["collect_user_data']
        ),

        Task(
            task_id="process_product_data',
            name="Process Product Data',
            description="Process collected product data',
            input_data={
                "data': [10, 20, 30, 40, 50],
                "operation": "sort',
                "options": {"reverse': True}
            },
            required_tools=["data_processor'],
            dependencies=["collect_product_data']
        ),

        # ML prediction phase
        Task(
            task_id="predict_recommendations',
            name="Predict Recommendations',
            description="Generate ML recommendations',
            input_data={
                "model": "recommendation_model',
                "features': [1, 2, 3, 4, 5],
                "confidence_threshold': 0.8
            },
            required_tools=["ml_predictor'],
            dependencies=["process_user_data", "process_product_data']
        ),

        # Storage phase
        Task(
            task_id="store_recommendations',
            name="Store Recommendations',
            description="Store recommendations to file',
            input_data={
                "operation": "write',
                "path": "/data/recommendations.json',
                "content": "recommendation data'
            },
            required_tools=["file_operations'],
            dependencies=["predict_recommendations']
        ),

        Task(
            task_id="update_database',
            name="Update Database',
            description="Update database with results',
            input_data={
                "query": "INSERT INTO recommendations (data) VALUES (%(data)s)',
                "params": {"data": "recommendation_data'}
            },
            required_tools=["database_query'],
            dependencies=["predict_recommendations']
        )
    ]

    # Create complex task graph
    task_graph = TaskGraph(
        graph_id="complex_workflow',
        name="Complex Workflow',
        description="Complex workflow with multiple phases and dependencies',
        tasks=tasks,
        entry_points=["collect_user_data", "collect_product_data'],
        exit_points=["store_recommendations", "update_database']
    )

    # Execute complex workflow
    logger.info("Executing complex workflow...')
    start_time = time.time()
    context = await runner.run(task_graph, {
        "workflow_type": "recommendation_system',
        "user_id": "user_123',
        "session_id": "session_456'
    })
    end_time = time.time()

    # Display results
    logger.info(f"Complex Workflow Results:')
    logger.info(f"  Status: {context.status}')
    logger.info(f"  Execution Time: {end_time - start_time:.2f}s')
    logger.info(f"  Completed Tasks: {len(context.completed_tasks)}')
    logger.info(f"  Failed Tasks: {len(context.failed_tasks)}')
    logger.info(f"  Retry Count: {context.retry_count}')

    if context.completed_tasks:
        logger.info(f"  Completed: {", ".join(context.completed_tasks)}')

    if context.failed_tasks:
        logger.info(f"  Failed: {", ".join(context.failed_tasks)}')

    # Show workflow efficiency
    total_tasks = len(tasks)
    completion_rate = len(context.completed_tasks) / total_tasks * 100
    logger.info(f"  Completion Rate: {completion_rate:.1f}%')
    logger.info(f"  Tasks per Second: {total_tasks / (end_time - start_time):.1f}')


async def example_performance_testing():
    """Example: Performance testing with different configurations.""'
    logger = logging.getLogger(__name__)

    # Create test scenarios
    scenarios = [
        {"name": "Small Workload", "tasks": 5, "concurrency': 2},
        {"name": "Medium Workload", "tasks": 10, "concurrency': 5},
        {"name": "Large Workload", "tasks": 20, "concurrency': 10}
    ]

    logger.info("Running Performance Tests...')

    for scenario in scenarios:
        logger.info(f"Scenario: {scenario["name"]}')

        # Create runner with specific configuration
        runner = create_task_runner(
            max_concurrent_tasks=scenario["concurrency'],
            task_timeout=30.0,
            log_level=LogLevel.WARNING  # Reduce logging for performance
        )

        # Create tasks for this scenario
        tasks = []
        for i in range(scenario["tasks']):
            task = Task(
                task_id=f"perf_task_{i}',
                name=f"Performance Task {i}',
                description=f"Task {i} for performance testing',
                input_data={
                    "data': list(range(i * 5, (i + 1) * 5)),
                    "operation": "sum'
                },
                required_tools=["data_processor'],
                dependencies=[]
            )
            tasks.append(task)

        task_graph = TaskGraph(
            graph_id=f"perf_graph_{scenario["name"].lower().replace(" ", "_")}',
            name=f"Performance Graph - {scenario["name"]}',
            description=f"Graph for {scenario["name"]} performance testing',
            tasks=tasks,
            entry_points=[task.task_id for task in tasks],
            exit_points=[task.task_id for task in tasks]
        )

        # Execute performance test
        start_time = time.time()
        context = await runner.run(task_graph)
        end_time = time.time()

        execution_time = end_time - start_time

        # Calculate metrics
        tasks_per_second = len(tasks) / execution_time
        efficiency = len(context.completed_tasks) / len(tasks) * 100

        logger.info(f"  Tasks: {len(tasks)}')
        logger.info(f"  Concurrency: {scenario["concurrency"]}')
        logger.info(f"  Execution Time: {execution_time:.2f}s')
        logger.info(f"  Tasks/Second: {tasks_per_second:.1f}')
        logger.info(f"  Success Rate: {efficiency:.1f}%')
        logger.info(f"  Status: {context.status}')

        # Show runner statistics
        stats = runner.get_statistics()
        logger.info(f"  Runner Stats: {stats}')


# ============================================================================
# Advanced Examples
# ============================================================================

async def advanced_example():
    """Advanced example with custom retry logic and error handling.""'
    logger = logging.getLogger(__name__)

    # Create custom executor with sophisticated error handling
    class AdvancedExecutor(CustomToolExecutor):
        """TODO: Add docstring."""
        """TODO: Add docstring.""'
        async def execute(self, tool_name: str, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
            try:
                # Add some randomness for realistic behavior
                import random
                if random.random() < 0.1:  # 10% chance of failure
                    raise Exception("Random failure for testing')

                return await super().execute(tool_name, parameters, context)
            except Exception as e:
                # Add context to error
                error_context = {
                    "tool': tool_name,
                    "parameters': parameters,
                    "timestamp': datetime.now().isoformat(),
                    "context': context
                }
                raise Exception(f"Tool execution failed: {e}') from e

    advanced_executor = AdvancedExecutor()

    # Create runner with advanced configuration
    runner = create_task_runner(
        max_concurrent_tasks=3,
        task_timeout=45.0,
        max_retries=5,
        retry_strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
        log_level=LogLevel.DEBUG,
        enable_evidence_capture=True
    )

    # Create resilient task graph
    tasks = [
        Task(
            task_id="resilient_task_1',
            name="Resilient Task 1',
            description="Task with built-in resilience',
            input_data={"data": [1, 2, 3], "operation": "sum'},
            required_tools=["data_processor'],
            dependencies=[]
        ),
        Task(
            task_id="resilient_task_2',
            name="Resilient Task 2',
            description="Another resilient task',
            input_data={"data": [4, 5, 6], "operation": "average'},
            required_tools=["data_processor'],
            dependencies=["resilient_task_1']
        )
    ]

    task_graph = TaskGraph(
        graph_id="resilient_graph',
        name="Resilient Graph',
        description="Graph with advanced error handling',
        tasks=tasks,
        entry_points=["resilient_task_1'],
        exit_points=["resilient_task_2']
    )

    # Execute with advanced error handling
    logger.info("Executing advanced resilient workflow...')
    context = await runner.run(task_graph, {"advanced': True})

    logger.info(f"Advanced execution completed: {context.status}')
    logger.info(f"Total retries: {context.retry_count}')


# ============================================================================
# Main execution
# ============================================================================

if __name__ == "__main__':
    # Run the main example
    asyncio.run(main())

    # Uncomment to run advanced examples
    # asyncio.run(advanced_example())
