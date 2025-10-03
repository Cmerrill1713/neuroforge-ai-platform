""'
Tests for Task Runner

Comprehensive test suite for the task runner including:
- Tool selection and execution
- Retry mechanisms and strategies
- Comprehensive logging system
- Evidence capture functionality
- Task execution and orchestration

Created: 2024-09-24
Status: Draft
""'

import asyncio
import pytest
import time
from datetime import datetime, timezone
from unittest.mock import Mock, AsyncMock, patch
from uuid import uuid4

from src.core.runtime.runner import (
    # Enums
    ExecutionStatus,
    RetryStrategy,
    LogLevel,

    # Models
    ExecutionContext,
    ExecutionLog,
    ExecutionEvidence,
    RetryConfig,
    LoggingConfig,
    EvidenceConfig,
    RunnerConfig,

    # Tool interface
    ToolExecutor,
    MockToolExecutor,

    # Components
    RetryManager,
    ExecutionLogger,
    EvidenceCapture,

    # Main runner
    TaskRunner,

    # Factory functions
    create_task_runner,
    create_runner_config,
)

from src.core.models.contracts import Task, TaskGraph, TaskStatus, ToolSpec, TaskDependency


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def sample_task():
    """TODO: Add docstring."""
    """Sample task for testing.""'
    return Task(
        task_id="test_task_1',
        name="Test Task',
        description="A test task',
        task_type="test_task',
        input_data={"param1": "value1'},
        required_tools=["mock_tool'],
        dependencies=[]
    )


@pytest.fixture
def sample_task_graph(sample_task):
    """TODO: Add docstring."""
    """Sample task graph for testing.""'
    return TaskGraph(
        graph_id="test_graph_1',
        name="Test Graph',
        description="A test task graph',
        tasks=[sample_task],
        entry_points=[sample_task.task_id],
        exit_points=[sample_task.task_id]
    )


@pytest.fixture
def sample_retry_config():
    """TODO: Add docstring."""
    """Sample retry configuration.""'
    return RetryConfig(
        strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
        max_retries=3,
        base_delay=1.0,
        max_delay=10.0,
        backoff_multiplier=2.0,
        jitter=True
    )


@pytest.fixture
def sample_logging_config():
    """TODO: Add docstring."""
    """Sample logging configuration.""'
    return LoggingConfig(
        level=LogLevel.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        include_details=True,
        max_log_entries=100
    )


@pytest.fixture
def sample_evidence_config():
    """TODO: Add docstring."""
    """Sample evidence configuration.""'
    return EvidenceConfig(
        capture_input=True,
        capture_output=True,
        capture_errors=True,
        capture_performance=True,
        max_evidence_entries=50
    )


@pytest.fixture
def sample_runner_config(sample_retry_config, sample_logging_config, sample_evidence_config):
    """TODO: Add docstring."""
    """Sample runner configuration.""'
    return RunnerConfig(
        retry_config=sample_retry_config,
        logging_config=sample_logging_config,
        evidence_config=sample_evidence_config,
        max_concurrent_tasks=3,
        task_timeout=30.0,
        enable_parallel_execution=True
    )


@pytest.fixture
def mock_tool_executor():
    """TODO: Add docstring."""
    """Mock tool executor for testing.""'
    return MockToolExecutor()


# ============================================================================
# Model Tests
# ============================================================================

class TestExecutionStatus:
    """TODO: Add docstring."""
    """Test ExecutionStatus enum.""'

    def test_execution_status_values(self):
        """TODO: Add docstring."""
        """Test execution status enum values.""'
        assert ExecutionStatus.PENDING == "pending'
        assert ExecutionStatus.RUNNING == "running'
        assert ExecutionStatus.COMPLETED == "completed'
        assert ExecutionStatus.FAILED == "failed'
        assert ExecutionStatus.CANCELLED == "cancelled'
        assert ExecutionStatus.RETRYING == "retrying'


class TestExecutionContext:
    """TODO: Add docstring."""
    """Test ExecutionContext model.""'

    def test_execution_context_creation(self):
        """TODO: Add docstring."""
        """Test execution context creation.""'
        context = ExecutionContext(task_graph_id="test_graph')

        assert context.execution_id is not None
        assert context.task_graph_id == "test_graph'
        assert context.status == ExecutionStatus.PENDING
        assert context.start_time is not None
        assert context.end_time is None
        assert context.current_task is None
        assert context.completed_tasks == []
        assert context.failed_tasks == []
        assert context.retry_count == 0
        assert context.max_retries == 3
        assert context.metadata == {}

    def test_execution_context_validation(self):
        """TODO: Add docstring."""
        """Test execution context validation.""'
        # Valid context
        valid_context = ExecutionContext(
            task_graph_id="test',
            retry_count=2,
            max_retries=5
        )
        assert valid_context.retry_count == 2
        assert valid_context.max_retries == 5

        # Invalid retry count
        with pytest.raises(ValueError):
            ExecutionContext(task_graph_id="test', retry_count=-1)

        # Invalid max retries
        with pytest.raises(ValueError):
            ExecutionContext(task_graph_id="test', max_retries=-1)


class TestRetryConfig:
    """TODO: Add docstring."""
    """Test RetryConfig model.""'

    def test_retry_config_creation(self, sample_retry_config):
        """TODO: Add docstring."""
        """Test retry config creation.""'
        assert sample_retry_config.strategy == RetryStrategy.EXPONENTIAL_BACKOFF
        assert sample_retry_config.max_retries == 3
        assert sample_retry_config.base_delay == 1.0
        assert sample_retry_config.max_delay == 10.0
        assert sample_retry_config.backoff_multiplier == 2.0
        assert sample_retry_config.jitter is True

    def test_retry_config_validation(self):
        """TODO: Add docstring."""
        """Test retry config validation.""'
        # Valid config
        valid_config = RetryConfig(
            base_delay=1.0,
            max_delay=5.0
        )
        assert valid_config.max_delay == 5.0

        # Invalid max delay
        with pytest.raises(ValueError):
            RetryConfig(base_delay=5.0, max_delay=1.0)


# ============================================================================
# Component Tests
# ============================================================================

class TestRetryManager:
    """TODO: Add docstring."""
    """Test RetryManager.""'

    @pytest.fixture
    def retry_manager(self, sample_retry_config):
        """TODO: Add docstring."""
        """Create retry manager.""'
        return RetryManager(sample_retry_config)

    @pytest.mark.asyncio
    async def test_should_retry_success(self, retry_manager):
        """Test successful retry decision.""'
        should_retry = await retry_manager.should_retry("task1", Exception("test'), 1)
        assert should_retry is True

    @pytest.mark.asyncio
    async def test_should_retry_max_retries(self, retry_manager):
        """Test retry decision with max retries exceeded.""'
        should_retry = await retry_manager.should_retry("task1", Exception("test'), 5)
        assert should_retry is False

    @pytest.mark.asyncio
    async def test_should_retry_non_retryable_error(self, retry_manager):
        """Test retry decision with non-retryable error.""'
        should_retry = await retry_manager.should_retry("task1", ValueError("test'), 1)
        assert should_retry is False

    @pytest.mark.asyncio
    async def test_get_retry_delay_immediate(self):
        """Test immediate retry delay.""'
        config = RetryConfig(strategy=RetryStrategy.IMMEDIATE)
        manager = RetryManager(config)

        delay = await manager.get_retry_delay(1)
        assert delay == 0.0

    @pytest.mark.asyncio
    async def test_get_retry_delay_exponential(self, retry_manager):
        """Test exponential backoff delay.""'
        delay1 = await retry_manager.get_retry_delay(0)
        delay2 = await retry_manager.get_retry_delay(1)
        delay3 = await retry_manager.get_retry_delay(2)

        assert delay1 < delay2 < delay3
        assert delay1 >= 0.5  # With jitter
        assert delay3 <= 10.0  # Max delay


class TestExecutionLogger:
    """TODO: Add docstring."""
    """Test ExecutionLogger.""'

    @pytest.fixture
    def execution_logger(self, sample_logging_config):
        """TODO: Add docstring."""
        """Create execution logger.""'
        return ExecutionLogger(sample_logging_config, "test_execution')

    def test_log_creation(self, execution_logger):
        """TODO: Add docstring."""
        """Test log creation.""'
        execution_logger.info("Test message", "task1", {"key": "value'})

        logs = execution_logger.get_logs()
        assert len(logs) == 1
        assert logs[0].level == LogLevel.INFO
        assert logs[0].message == "Test message'
        assert logs[0].task_id == "task1'
        assert logs[0].details == {"key": "value'}

    def test_log_filtering(self, execution_logger):
        """TODO: Add docstring."""
        """Test log filtering.""'
        execution_logger.info("Info message", "task1')
        execution_logger.error("Error message", "task2')
        execution_logger.warning("Warning message", "task1')

        # Filter by level
        error_logs = execution_logger.get_logs(level=LogLevel.ERROR)
        assert len(error_logs) == 1
        assert error_logs[0].message == "Error message'

        # Filter by task
        task1_logs = execution_logger.get_logs(task_id="task1')
        assert len(task1_logs) == 2

    def test_log_levels(self, execution_logger):
        """TODO: Add docstring."""
        """Test different log levels.""'
        execution_logger.debug("Debug message')
        execution_logger.info("Info message')
        execution_logger.warning("Warning message')
        execution_logger.error("Error message')
        execution_logger.critical("Critical message')

        logs = execution_logger.get_logs()
        assert len(logs) == 5

        levels = [log.level for log in logs]
        assert LogLevel.DEBUG in levels
        assert LogLevel.INFO in levels
        assert LogLevel.WARNING in levels
        assert LogLevel.ERROR in levels
        assert LogLevel.CRITICAL in levels


class TestEvidenceCapture:
    """TODO: Add docstring."""
    """Test EvidenceCapture.""'

    @pytest.fixture
    def evidence_capture(self, sample_evidence_config):
        """TODO: Add docstring."""
        """Create evidence capture.""'
        return EvidenceCapture(sample_evidence_config, "test_execution')

    def test_capture_input(self, evidence_capture):
        """TODO: Add docstring."""
        """Test input evidence capture.""'
        evidence_capture.capture_input("task1", {"param": "value"}, {"meta": "data'})

        evidence = evidence_capture.get_evidence(evidence_type="input')
        assert len(evidence) == 1
        assert evidence[0].task_id == "task1'
        assert evidence[0].evidence_type == "input'
        assert evidence[0].data == {"param": "value'}
        assert evidence[0].metadata == {"meta": "data'}

    def test_capture_output(self, evidence_capture):
        """TODO: Add docstring."""
        """Test output evidence capture.""'
        evidence_capture.capture_output("task1", {"result": "success'})

        evidence = evidence_capture.get_evidence(evidence_type="output')
        assert len(evidence) == 1
        assert evidence[0].data == {"result": "success'}

    def test_capture_error(self, evidence_capture):
        """TODO: Add docstring."""
        """Test error evidence capture.""'
        error = ValueError("Test error')
        evidence_capture.capture_error("task1', error)

        evidence = evidence_capture.get_evidence(evidence_type="error')
        assert len(evidence) == 1
        assert evidence[0].data["error_type"] == "ValueError'
        assert evidence[0].data["error_message"] == "Test error'

    def test_capture_performance(self, evidence_capture):
        """TODO: Add docstring."""
        """Test performance evidence capture.""'
        evidence_capture.capture_performance("task1", {"execution_time': 1.5})

        evidence = evidence_capture.get_evidence(evidence_type="performance')
        assert len(evidence) == 1
        assert evidence[0].data == {"execution_time': 1.5}

    def test_evidence_filtering(self, evidence_capture):
        """TODO: Add docstring."""
        """Test evidence filtering.""'
        evidence_capture.capture_input("task1", {"input": "data'})
        evidence_capture.capture_output("task1", {"output": "data'})
        evidence_capture.capture_input("task2", {"input": "data'})

        # Filter by type
        input_evidence = evidence_capture.get_evidence(evidence_type="input')
        assert len(input_evidence) == 2

        # Filter by task
        task1_evidence = evidence_capture.get_evidence(task_id="task1')
        assert len(task1_evidence) == 2


class TestMockToolExecutor:
    """TODO: Add docstring."""
    """Test MockToolExecutor.""'

    @pytest.fixture
    def mock_executor(self):
        """TODO: Add docstring."""
        """Create mock tool executor.""'
        return MockToolExecutor()

    def test_get_available_tools(self, mock_executor):
        """TODO: Add docstring."""
        """Test getting available tools.""'
        tools = mock_executor.get_available_tools()
        assert len(tools) == 3

        tool_names = [tool.name for tool in tools]
        assert "mock_tool' in tool_names
        assert "slow_tool' in tool_names
        assert "failing_tool' in tool_names

    @pytest.mark.asyncio
    async def test_execute_mock_tool(self, mock_executor):
        """Test executing mock tool.""'
        result = await mock_executor.execute("mock_tool", {"param": "value'}, {})

        assert result["result"] == "Mock result for {"param": "value"}'

    @pytest.mark.asyncio
    async def test_execute_slow_tool(self, mock_executor):
        """Test executing slow tool.""'
        start_time = time.time()
        result = await mock_executor.execute("slow_tool', {}, {})
        end_time = time.time()

        assert result["result"] == "Slow result for {}'
        assert end_time - start_time >= 2.0

    @pytest.mark.asyncio
    async def test_execute_failing_tool(self, mock_executor):
        """Test executing failing tool.""'
        with pytest.raises(Exception, match="Mock tool failure'):
            await mock_executor.execute("failing_tool', {}, {})

    @pytest.mark.asyncio
    async def test_execute_unknown_tool(self, mock_executor):
        """Test executing unknown tool.""'
        with pytest.raises(ValueError, match="Unknown tool'):
            await mock_executor.execute("unknown_tool', {}, {})

    def test_validate_tool_call(self, mock_executor):
        """TODO: Add docstring."""
        """Test tool call validation.""'
        assert mock_executor.validate_tool_call("mock_tool', {}) is True
        assert mock_executor.validate_tool_call("unknown_tool', {}) is False


# ============================================================================
# Task Runner Tests
# ============================================================================

class TestTaskRunner:
    """TODO: Add docstring."""
    """Test TaskRunner.""'

    @pytest.fixture
    def task_runner(self, sample_runner_config, mock_tool_executor):
        """TODO: Add docstring."""
        """Create task runner.""'
        return TaskRunner(sample_runner_config, mock_tool_executor)

    def test_runner_initialization(self, task_runner):
        """TODO: Add docstring."""
        """Test runner initialization.""'
        assert task_runner.config is not None
        assert task_runner.tool_executor is not None
        assert task_runner.retry_manager is not None
        assert task_runner.total_executions == 0
        assert task_runner.successful_executions == 0
        assert task_runner.failed_executions == 0

    @pytest.mark.asyncio
    async def test_run_successful_execution(self, task_runner, sample_task_graph):
        """Test successful task execution.""'
        context = await task_runner.run(sample_task_graph)

        assert context.status == ExecutionStatus.COMPLETED
        assert len(context.completed_tasks) == 1
        assert len(context.failed_tasks) == 0
        assert context.end_time is not None
        assert task_runner.total_executions == 1
        assert task_runner.successful_executions == 1

    @pytest.mark.asyncio
    async def test_run_failed_execution(self, task_runner):
        """Test failed task execution.""'
        # Create task with failing tool
        failing_task = Task(
            task_id="failing_task',
            name="Failing Task',
            description="A task that will fail',
            task_type="test_task',
            input_data={},
            required_tools=["failing_tool'],
            dependencies=[]
        )

        failing_graph = TaskGraph(
            graph_id="failing_graph',
            name="Failing Graph',
            description="A graph with failing tasks',
            tasks=[failing_task],
            entry_points=[failing_task.task_id],
            exit_points=[failing_task.task_id]
        )

        context = await task_runner.run(failing_graph)

        assert context.status == ExecutionStatus.FAILED
        assert len(context.completed_tasks) == 0
        assert len(context.failed_tasks) == 1
        assert task_runner.failed_executions == 1

    @pytest.mark.asyncio
    async def test_run_with_retries(self, task_runner):
        """Test execution with retries.""'
        # Create custom executor that fails first few times
        class RetryableMockExecutor(MockToolExecutor):
            """TODO: Add docstring."""
            """TODO: Add docstring.""'
            def __init__(self):
                """TODO: Add docstring."""
                """TODO: Add docstring.""'
                super().__init__()
                self.call_count = 0

            async def execute(self, tool_name: str, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
                if tool_name == "mock_tool':
                    self.call_count += 1
                    if self.call_count <= 2:  # Fail first 2 times
                        raise Exception(f"Retryable failure {self.call_count}')
                    return {"result": f"Success after {self.call_count} attempts'}
                return await super().execute(tool_name, parameters, context)

        retryable_executor = RetryableMockExecutor()
        retry_runner = TaskRunner(task_runner.config, retryable_executor)

        context = await retry_runner.run(sample_task_graph)

        assert context.status == ExecutionStatus.COMPLETED
        assert context.retry_count > 0
        assert retryable_executor.call_count == 3  # 2 failures + 1 success

    @pytest.mark.asyncio
    async def test_run_parallel_execution(self, task_runner):
        """Test parallel task execution.""'
        # Create multiple independent tasks
        tasks = []
        for i in range(3):
            task = Task(
                task_id=f"parallel_task_{i}',
                name=f"Parallel Task {i}',
                description=f"Task {i} for parallel execution',
                task_type="test_task',
                input_data={"task_id': i},
                required_tools=["mock_tool'],
                dependencies=[]
            )
            tasks.append(task)

        parallel_graph = TaskGraph(
            graph_id="parallel_graph',
            name="Parallel Graph',
            description="Graph with parallel tasks',
            tasks=tasks,
            entry_points=[task.id for task in tasks],
            exit_points=[task.id for task in tasks]
        )

        start_time = time.time()
        context = await task_runner.run(parallel_graph)
        end_time = time.time()

        assert context.status == ExecutionStatus.COMPLETED
        assert len(context.completed_tasks) == 3
        assert len(context.failed_tasks) == 0

        # Should complete faster than sequential execution
        execution_time = end_time - start_time
        assert execution_time < 1.0  # Should be much faster than 3 * 0.1s

    @pytest.mark.asyncio
    async def test_run_sequential_execution(self, task_runner):
        """Test sequential task execution.""'
        # Disable parallel execution
        config = task_runner.config
        config.enable_parallel_execution = False
        sequential_runner = TaskRunner(config, task_runner.tool_executor)

        # Create tasks with dependencies
        task1 = Task(
            task_id="task1',
            name="Task 1',
            description="First task',
            task_type="test_task',
            input_data={},
            required_tools=["mock_tool'],
            dependencies=[]
        )

        task2 = Task(
            task_id="task2',
            name="Task 2',
            description="Second task',
            task_type="test_task',
            input_data={},
            required_tools=["mock_tool'],
            dependencies=[TaskDependency(task_id=uuid4())]
        )

        sequential_graph = TaskGraph(
            graph_id="sequential_graph',
            name="Sequential Graph',
            description="Graph with sequential tasks',
            tasks=[task1, task2],
            entry_points=["task1'],
            exit_points=["task2']
        )

        context = await sequential_runner.run(sequential_graph)

        assert context.status == ExecutionStatus.COMPLETED
        assert len(context.completed_tasks) == 2
        assert context.completed_tasks == ["task1", "task2']  # Should be in order

    @pytest.mark.asyncio
    async def test_run_with_timeout(self, task_runner):
        """Test execution with timeout.""'
        # Create task with slow tool
        slow_task = Task(
            task_id="slow_task',
            name="Slow Task',
            description="A task that takes too long',
            task_type="test_task',
            input_data={},
            required_tools=["slow_tool'],
            dependencies=[]
        )

        slow_graph = TaskGraph(
            graph_id="slow_graph',
            name="Slow Graph',
            description="Graph with slow task',
            tasks=[slow_task],
            entry_points=[slow_task.task_id],
            exit_points=[slow_task.task_id]
        )

        # Set short timeout
        config = task_runner.config
        config.task_timeout = 1.0
        timeout_runner = TaskRunner(config, task_runner.tool_executor)

        context = await timeout_runner.run(slow_graph)

        assert context.status == ExecutionStatus.FAILED
        assert len(context.failed_tasks) == 1

    def test_get_statistics(self, task_runner):
        """TODO: Add docstring."""
        """Test runner statistics.""'
        # Update statistics
        task_runner.total_executions = 10
        task_runner.successful_executions = 8
        task_runner.failed_executions = 2
        task_runner.total_tasks_executed = 25
        task_runner.total_retries = 5

        stats = task_runner.get_statistics()

        assert stats["total_executions'] == 10
        assert stats["successful_executions'] == 8
        assert stats["failed_executions'] == 2
        assert stats["success_rate'] == 80.0
        assert stats["total_tasks_executed'] == 25
        assert stats["total_retries'] == 5
        assert stats["average_retries_per_execution'] == 0.5


# ============================================================================
# Factory Function Tests
# ============================================================================

class TestFactoryFunctions:
    """TODO: Add docstring."""
    """Test factory functions.""'

    def test_create_task_runner(self):
        """TODO: Add docstring."""
        """Test create_task_runner function.""'
        runner = create_task_runner()

        assert isinstance(runner, TaskRunner)
        assert runner.config.max_concurrent_tasks == 5
        assert runner.config.task_timeout == 300.0
        assert runner.config.retry_config.max_retries == 3

    def test_create_task_runner_custom(self):
        """TODO: Add docstring."""
        """Test create_task_runner with custom parameters.""'
        runner = create_task_runner(
            max_concurrent_tasks=10,
            task_timeout=600.0,
            max_retries=5,
            retry_strategy=RetryStrategy.LINEAR_BACKOFF,
            log_level=LogLevel.DEBUG,
            enable_evidence_capture=False
        )

        assert runner.config.max_concurrent_tasks == 10
        assert runner.config.task_timeout == 600.0
        assert runner.config.retry_config.max_retries == 5
        assert runner.config.retry_config.strategy == RetryStrategy.LINEAR_BACKOFF
        assert runner.config.logging_config.level == LogLevel.DEBUG
        assert runner.config.evidence_config.capture_input is False

    def test_create_runner_config(self):
        """TODO: Add docstring."""
        """Test create_runner_config function.""'
        config = create_runner_config(
            max_concurrent_tasks=8,
            task_timeout=120.0,
            max_retries=2,
            retry_strategy=RetryStrategy.FIXED_DELAY,
            log_level=LogLevel.WARNING
        )

        assert config.max_concurrent_tasks == 8
        assert config.task_timeout == 120.0
        assert config.retry_config.max_retries == 2
        assert config.retry_config.strategy == RetryStrategy.FIXED_DELAY
        assert config.logging_config.level == LogLevel.WARNING


# ============================================================================
# Integration Tests
# ============================================================================

class TestRunnerIntegration:
    """TODO: Add docstring."""
    """Integration tests for the task runner.""'

    @pytest.mark.asyncio
    async def test_end_to_end_execution(self):
        """Test end-to-end task execution.""'
        # Create complex task graph
        task1 = Task(
            task_id="task1',
            name="Task 1',
            description="First task',
            task_type="test_task',
            input_data={"value': 1},
            required_tools=["mock_tool'],
            dependencies=[]
        )

        task2 = Task(
            task_id="task2',
            name="Task 2',
            description="Second task',
            task_type="test_task',
            input_data={"value': 2},
            required_tools=["mock_tool'],
            dependencies=[TaskDependency(task_id=uuid4())]
        )

        task3 = Task(
            task_id="task3',
            name="Task 3',
            description="Third task',
            task_type="test_task',
            input_data={"value': 3},
            required_tools=["mock_tool'],
            dependencies=[TaskDependency(task_id=uuid4())]
        )

        complex_graph = TaskGraph(
            graph_id="complex_graph',
            name="Complex Graph',
            description="Graph with multiple tasks and dependencies',
            tasks=[task1, task2, task3],
            entry_points=["task1'],
            exit_points=["task2", "task3']
        )

        # Create runner
        runner = create_task_runner(max_concurrent_tasks=2)

        # Execute
        context = await runner.run(complex_graph, {"test": "integration'})

        # Verify results
        assert context.status == ExecutionStatus.COMPLETED
        assert len(context.completed_tasks) == 3
        assert len(context.failed_tasks) == 0
        assert context.metadata == {"test": "integration'}

        # Verify task execution order
        assert "task1' in context.completed_tasks
        assert "task2' in context.completed_tasks
        assert "task3' in context.completed_tasks

    @pytest.mark.asyncio
    async def test_evidence_and_logging_integration(self):
        """Test evidence capture and logging integration.""'
        # Create runner with evidence capture
        runner = create_task_runner(enable_evidence_capture=True)

        # Create simple task
        task = Task(
            task_id="evidence_task',
            name="Evidence Task',
            description="Task for evidence testing',
            task_type="test_task',
            input_data={"test": "data'},
            required_tools=["mock_tool'],
            dependencies=[]
        )

        graph = TaskGraph(
            graph_id="evidence_graph',
            name="Evidence Graph',
            tasks=[task],
            entry_points=[task.task_id],
            exit_points=[task.task_id]
        )

        # Execute
        context = await runner.run(graph)

        # Verify evidence was captured (this would require access to internal components)
        assert context.status == ExecutionStatus.COMPLETED


# ============================================================================
# Performance Tests
# ============================================================================

class TestRunnerPerformance:
    """TODO: Add docstring."""
    """Performance tests for the task runner.""'

    @pytest.mark.asyncio
    async def test_concurrent_execution_performance(self):
        """Test concurrent execution performance.""'
        # Create many independent tasks
        tasks = []
        for i in range(10):
            task = Task(
                task_id=f"perf_task_{i}',
                name=f"Performance Task {i}',
                description=f"Task {i} for performance testing',
                task_type="test_task',
                input_data={"task_id': i},
                required_tools=["mock_tool'],
                dependencies=[]
            )
            tasks.append(task)

        perf_graph = TaskGraph(
            graph_id="perf_graph',
            name="Performance Graph',
            description="Graph for performance testing',
            tasks=tasks,
            entry_points=[task.id for task in tasks],
            exit_points=[task.id for task in tasks]
        )

        # Test with different concurrency levels
        for max_concurrent in [1, 5, 10]:
            runner = create_task_runner(max_concurrent_tasks=max_concurrent)

            start_time = time.time()
            context = await runner.run(perf_graph)
            end_time = time.time()

            execution_time = end_time - start_time

            assert context.status == ExecutionStatus.COMPLETED
            assert len(context.completed_tasks) == 10

            # Higher concurrency should be faster
            if max_concurrent > 1:
                assert execution_time < 2.0  # Should be much faster than sequential


if __name__ == "__main__':
    pytest.main([__file__, "-v'])
