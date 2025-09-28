"""
Task Runner for Agentic LLM Core v0.1

This module provides a comprehensive task runner that executes TaskGraphs with
tool selection, retry mechanisms, comprehensive logging, and evidence capture.

Created: 2024-09-24
Status: Draft
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
import traceback
from abc import ABC, abstractmethod
from datetime import datetime, timezone, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Callable, Awaitable
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator

from ..models.contracts import Task, TaskGraph, TaskResult, TaskStatus, ToolSpec


# ============================================================================
# Runner Models
# ============================================================================

class ExecutionStatus(str, Enum):
    """Execution status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class RetryStrategy(str, Enum):
    """Retry strategy enumeration."""
    IMMEDIATE = "immediate"
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    FIXED_DELAY = "fixed_delay"


class LogLevel(str, Enum):
    """Log level enumeration."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ExecutionContext(BaseModel):
    """Context for task execution."""
    execution_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique execution ID")
    task_graph_id: str = Field(..., description="Task graph ID")
    start_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Execution start time")
    end_time: Optional[datetime] = Field(None, description="Execution end time")
    status: ExecutionStatus = Field(default=ExecutionStatus.PENDING, description="Current execution status")
    current_task: Optional[str] = Field(None, description="Currently executing task ID")
    completed_tasks: List[str] = Field(default_factory=list, description="Completed task IDs")
    failed_tasks: List[str] = Field(default_factory=list, description="Failed task IDs")
    retry_count: int = Field(default=0, description="Number of retries")
    max_retries: int = Field(default=3, description="Maximum retries allowed")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    @field_validator('retry_count')
    @classmethod
    def validate_retry_count(cls, v):
        if v < 0:
            raise ValueError("Retry count cannot be negative")
        return v
    
    @field_validator('max_retries')
    @classmethod
    def validate_max_retries(cls, v):
        if v < 0:
            raise ValueError("Max retries cannot be negative")
        return v


class ExecutionLog(BaseModel):
    """Execution log entry."""
    log_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique log ID")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Log timestamp")
    level: LogLevel = Field(..., description="Log level")
    task_id: Optional[str] = Field(None, description="Related task ID")
    message: str = Field(..., description="Log message")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional log details")
    execution_id: str = Field(..., description="Execution ID")
    
    @field_validator('message')
    @classmethod
    def validate_message(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError("Log message cannot be empty")
        return v.strip()


class ExecutionEvidence(BaseModel):
    """Evidence captured during execution."""
    evidence_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique evidence ID")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Evidence timestamp")
    task_id: str = Field(..., description="Related task ID")
    evidence_type: str = Field(..., description="Type of evidence")
    data: Dict[str, Any] = Field(..., description="Evidence data")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    execution_id: str = Field(..., description="Execution ID")
    
    @field_validator('evidence_type')
    @classmethod
    def validate_evidence_type(cls, v):
        allowed_types = ['input', 'output', 'error', 'performance', 'state', 'custom']
        if v not in allowed_types:
            raise ValueError(f"Evidence type must be one of: {allowed_types}")
        return v


class RetryConfig(BaseModel):
    """Retry configuration."""
    strategy: RetryStrategy = Field(default=RetryStrategy.EXPONENTIAL_BACKOFF, description="Retry strategy")
    max_retries: int = Field(default=3, ge=0, le=10, description="Maximum retries")
    base_delay: float = Field(default=1.0, ge=0.1, description="Base delay in seconds")
    max_delay: float = Field(default=60.0, ge=1.0, description="Maximum delay in seconds")
    backoff_multiplier: float = Field(default=2.0, ge=1.0, description="Backoff multiplier")
    jitter: bool = Field(default=True, description="Add jitter to delays")
    
    @field_validator('max_delay')
    @classmethod
    def validate_max_delay(cls, v, info):
        if info.data.get('base_delay') is not None and v < info.data['base_delay']:
            raise ValueError("Max delay must be greater than base delay")
        return v


class LoggingConfig(BaseModel):
    """Logging configuration."""
    level: LogLevel = Field(default=LogLevel.INFO, description="Log level")
    format: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s", description="Log format")
    include_details: bool = Field(default=True, description="Include detailed information")
    include_timestamps: bool = Field(default=True, description="Include timestamps")
    max_log_entries: int = Field(default=1000, ge=100, description="Maximum log entries to keep")
    log_to_file: bool = Field(default=False, description="Log to file")
    log_file_path: Optional[str] = Field(None, description="Log file path")


class EvidenceConfig(BaseModel):
    """Evidence capture configuration."""
    capture_input: bool = Field(default=True, description="Capture task inputs")
    capture_output: bool = Field(default=True, description="Capture task outputs")
    capture_errors: bool = Field(default=True, description="Capture errors")
    capture_performance: bool = Field(default=True, description="Capture performance metrics")
    capture_state: bool = Field(default=False, description="Capture state changes")
    max_evidence_entries: int = Field(default=500, ge=50, description="Maximum evidence entries")
    compress_evidence: bool = Field(default=False, description="Compress evidence data")


class RunnerConfig(BaseModel):
    """Runner configuration."""
    retry_config: RetryConfig = Field(default_factory=RetryConfig, description="Retry configuration")
    logging_config: LoggingConfig = Field(default_factory=LoggingConfig, description="Logging configuration")
    evidence_config: EvidenceConfig = Field(default_factory=EvidenceConfig, description="Evidence configuration")
    max_concurrent_tasks: int = Field(default=5, ge=1, le=20, description="Maximum concurrent tasks")
    task_timeout: float = Field(default=300.0, ge=1.0, description="Task timeout in seconds")
    enable_parallel_execution: bool = Field(default=True, description="Enable parallel task execution")
    enable_evidence_capture: bool = Field(default=True, description="Enable evidence capture")
    enable_detailed_logging: bool = Field(default=True, description="Enable detailed logging")


# ============================================================================
# Tool Interface
# ============================================================================

class ToolExecutor(ABC):
    """Abstract base class for tool executors."""
    
    @abstractmethod
    async def execute(self, tool_name: str, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool with given parameters."""
        pass
    
    @abstractmethod
    def get_available_tools(self) -> List[ToolSpec]:
        """Get list of available tools."""
        pass
    
    @abstractmethod
    def validate_tool_call(self, tool_name: str, parameters: Dict[str, Any]) -> bool:
        """Validate tool call parameters."""
        pass


class MockToolExecutor(ToolExecutor):
    """Mock tool executor for testing."""
    
    def __init__(self):
        self.tools = [
            ToolSpec(
                name="mock_tool",
                description="Mock tool for testing",
                parameters=[],
                returns={"result": "str"},
                category="test"
            ),
            ToolSpec(
                name="slow_tool",
                description="Slow mock tool",
                parameters=[],
                returns={"result": "str"},
                category="test"
            ),
            ToolSpec(
                name="failing_tool",
                description="Failing mock tool",
                parameters=[],
                returns={"result": "str"},
                category="test"
            )
        ]
    
    async def execute(self, tool_name: str, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute mock tool."""
        if tool_name == "mock_tool":
            await asyncio.sleep(0.1)  # Simulate work
            return {"result": f"Mock result for {parameters}"}
        elif tool_name == "slow_tool":
            await asyncio.sleep(2.0)  # Simulate slow work
            return {"result": f"Slow result for {parameters}"}
        elif tool_name == "failing_tool":
            raise Exception("Mock tool failure")
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
    
    def get_available_tools(self) -> List[ToolSpec]:
        """Get available tools."""
        return self.tools
    
    def validate_tool_call(self, tool_name: str, parameters: Dict[str, Any]) -> bool:
        """Validate tool call."""
        return any(tool.name == tool_name for tool in self.tools)


# ============================================================================
# Retry Mechanisms
# ============================================================================

class RetryManager:
    """Manages retry logic for failed tasks."""
    
    def __init__(self, config: RetryConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    async def should_retry(self, task_id: str, error: Exception, retry_count: int) -> bool:
        """Determine if a task should be retried."""
        if retry_count >= self.config.max_retries:
            self.logger.warning(f"Task {task_id} exceeded max retries ({self.config.max_retries})")
            return False
        
        # Check if error is retryable
        if not self._is_retryable_error(error):
            self.logger.warning(f"Task {task_id} failed with non-retryable error: {error}")
            return False
        
        return True
    
    def _is_retryable_error(self, error: Exception) -> bool:
        """Check if an error is retryable."""
        # Non-retryable errors
        non_retryable_errors = [
            ValueError,
            TypeError,
            AttributeError,
            KeyError,
            NotImplementedError
        ]
        
        return not any(isinstance(error, error_type) for error_type in non_retryable_errors)
    
    async def get_retry_delay(self, retry_count: int) -> float:
        """Calculate retry delay based on strategy."""
        if self.config.strategy == RetryStrategy.IMMEDIATE:
            return 0.0
        elif self.config.strategy == RetryStrategy.FIXED_DELAY:
            delay = self.config.base_delay
        elif self.config.strategy == RetryStrategy.LINEAR_BACKOFF:
            delay = self.config.base_delay * (retry_count + 1)
        elif self.config.strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            delay = self.config.base_delay * (self.config.backoff_multiplier ** retry_count)
        else:
            delay = self.config.base_delay
        
        # Apply max delay limit
        delay = min(delay, self.config.max_delay)
        
        # Add jitter if enabled
        if self.config.jitter:
            import random
            jitter_factor = random.uniform(0.5, 1.5)
            delay *= jitter_factor
        
        return delay


# ============================================================================
# Logging System
# ============================================================================

class ExecutionLogger:
    """Comprehensive logging system for task execution."""
    
    def __init__(self, config: LoggingConfig, execution_id: str):
        self.config = config
        self.execution_id = execution_id
        self.logs: List[ExecutionLog] = []
        self.logger = logging.getLogger(f"TaskRunner-{execution_id}")
        
        # Configure logger
        self._configure_logger()
    
    def _configure_logger(self):
        """Configure the logger."""
        handler = logging.StreamHandler()
        formatter = logging.Formatter(self.config.format)
        handler.setFormatter(formatter)
        
        self.logger.addHandler(handler)
        self.logger.setLevel(getattr(logging, self.config.level.value))
        
        # Prevent duplicate logs
        self.logger.propagate = False
    
    def log(self, level: LogLevel, message: str, task_id: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        """Add a log entry."""
        log_entry = ExecutionLog(
            level=level,
            task_id=task_id,
            message=message,
            details=details or {},
            execution_id=self.execution_id
        )
        
        self.logs.append(log_entry)
        
        # Limit log entries
        if len(self.logs) > self.config.max_log_entries:
            self.logs = self.logs[-self.config.max_log_entries:]
        
        # Log to standard logger
        log_method = getattr(self.logger, level.value.lower())
        log_message = f"[{task_id or 'GLOBAL'}] {message}"
        if details and self.config.include_details:
            log_message += f" | Details: {details}"
        
        log_method(log_message)
    
    def debug(self, message: str, task_id: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        """Log debug message."""
        self.log(LogLevel.DEBUG, message, task_id, details)
    
    def info(self, message: str, task_id: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        """Log info message."""
        self.log(LogLevel.INFO, message, task_id, details)
    
    def warning(self, message: str, task_id: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        """Log warning message."""
        self.log(LogLevel.WARNING, message, task_id, details)
    
    def error(self, message: str, task_id: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        """Log error message."""
        self.log(LogLevel.ERROR, message, task_id, details)
    
    def critical(self, message: str, task_id: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        """Log critical message."""
        self.log(LogLevel.CRITICAL, message, task_id, details)
    
    def get_logs(self, level: Optional[LogLevel] = None, task_id: Optional[str] = None) -> List[ExecutionLog]:
        """Get filtered logs."""
        filtered_logs = self.logs
        
        if level:
            filtered_logs = [log for log in filtered_logs if log.level == level]
        
        if task_id:
            filtered_logs = [log for log in filtered_logs if log.task_id == task_id]
        
        return filtered_logs


# ============================================================================
# Evidence Capture
# ============================================================================

class EvidenceCapture:
    """Captures evidence during task execution."""
    
    def __init__(self, config: EvidenceConfig, execution_id: str):
        self.config = config
        self.execution_id = execution_id
        self.evidence: List[ExecutionEvidence] = []
    
    def capture_input(self, task_id: str, input_data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None):
        """Capture task input."""
        if not self.config.capture_input:
            return
        
        evidence = ExecutionEvidence(
            task_id=task_id,
            evidence_type="input",
            data=input_data,
            metadata=metadata or {},
            execution_id=self.execution_id
        )
        
        self._add_evidence(evidence)
    
    def capture_output(self, task_id: str, output_data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None):
        """Capture task output."""
        if not self.config.capture_output:
            return
        
        evidence = ExecutionEvidence(
            task_id=task_id,
            evidence_type="output",
            data=output_data,
            metadata=metadata or {},
            execution_id=self.execution_id
        )
        
        self._add_evidence(evidence)
    
    def capture_error(self, task_id: str, error: Exception, metadata: Optional[Dict[str, Any]] = None):
        """Capture task error."""
        if not self.config.capture_errors:
            return
        
        error_data = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc()
        }
        
        evidence = ExecutionEvidence(
            task_id=task_id,
            evidence_type="error",
            data=error_data,
            metadata=metadata or {},
            execution_id=self.execution_id
        )
        
        self._add_evidence(evidence)
    
    def capture_performance(self, task_id: str, performance_data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None):
        """Capture performance metrics."""
        if not self.config.capture_performance:
            return
        
        evidence = ExecutionEvidence(
            task_id=task_id,
            evidence_type="performance",
            data=performance_data,
            metadata=metadata or {},
            execution_id=self.execution_id
        )
        
        self._add_evidence(evidence)
    
    def capture_state(self, task_id: str, state_data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None):
        """Capture state changes."""
        if not self.config.capture_state:
            return
        
        evidence = ExecutionEvidence(
            task_id=task_id,
            evidence_type="state",
            data=state_data,
            metadata=metadata or {},
            execution_id=self.execution_id
        )
        
        self._add_evidence(evidence)
    
    def capture_custom(self, task_id: str, evidence_type: str, data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None):
        """Capture custom evidence."""
        evidence = ExecutionEvidence(
            task_id=task_id,
            evidence_type="custom",
            data=data,
            metadata=metadata or {},
            execution_id=self.execution_id
        )
        
        self._add_evidence(evidence)
    
    def _add_evidence(self, evidence: ExecutionEvidence):
        """Add evidence to collection."""
        self.evidence.append(evidence)
        
        # Limit evidence entries
        if len(self.evidence) > self.config.max_evidence_entries:
            self.evidence = self.evidence[-self.config.max_evidence_entries:]
    
    def get_evidence(self, evidence_type: Optional[str] = None, task_id: Optional[str] = None) -> List[ExecutionEvidence]:
        """Get filtered evidence."""
        filtered_evidence = self.evidence
        
        if evidence_type:
            filtered_evidence = [ev for ev in filtered_evidence if ev.evidence_type == evidence_type]
        
        if task_id:
            filtered_evidence = [ev for ev in filtered_evidence if ev.task_id == task_id]
        
        return filtered_evidence


# ============================================================================
# Main Task Runner
# ============================================================================

class TaskRunner:
    """Main task runner that executes TaskGraphs."""
    
    def __init__(self, config: Optional[RunnerConfig] = None, tool_executor: Optional[ToolExecutor] = None):
        self.config = config or RunnerConfig()
        self.tool_executor = tool_executor or MockToolExecutor()
        self.logger = logging.getLogger(__name__)
        
        # Components
        self.retry_manager = RetryManager(self.config.retry_config)
        
        # Statistics
        self.total_executions = 0
        self.successful_executions = 0
        self.failed_executions = 0
        self.total_tasks_executed = 0
        self.total_retries = 0
    
    async def run(self, task_graph: TaskGraph, context: Optional[Dict[str, Any]] = None) -> ExecutionContext:
        """Run a task graph."""
        context = context or {}
        
        # Create execution context
        execution_context = ExecutionContext(
            task_graph_id=task_graph.graph_id,
            status=ExecutionStatus.RUNNING,
            max_retries=self.config.retry_config.max_retries,
            metadata=context
        )
        
        # Initialize components
        execution_logger = ExecutionLogger(self.config.logging_config, execution_context.execution_id)
        evidence_capture = EvidenceCapture(self.config.evidence_config, execution_context.execution_id)
        
        execution_logger.info(f"Starting execution of task graph: {task_graph.name}")
        execution_logger.info(f"Tasks to execute: {len(task_graph.tasks)}")
        
        try:
            # Execute tasks
            if self.config.enable_parallel_execution:
                await self._execute_parallel(task_graph, execution_context, execution_logger, evidence_capture)
            else:
                await self._execute_sequential(task_graph, execution_context, execution_logger, evidence_capture)
            
            # Update execution status
            if execution_context.failed_tasks:
                execution_context.status = ExecutionStatus.FAILED
                execution_logger.error(f"Execution failed with {len(execution_context.failed_tasks)} failed tasks")
            else:
                execution_context.status = ExecutionStatus.COMPLETED
                execution_logger.info("Execution completed successfully")
            
            # Update statistics
            self.total_executions += 1
            if execution_context.status == ExecutionStatus.COMPLETED:
                self.successful_executions += 1
            else:
                self.failed_executions += 1
            
            self.total_tasks_executed += len(execution_context.completed_tasks)
            self.total_retries += execution_context.retry_count
            
        except Exception as e:
            execution_context.status = ExecutionStatus.FAILED
            execution_logger.critical(f"Execution failed with critical error: {e}")
            evidence_capture.capture_error("GLOBAL", e)
        
        finally:
            execution_context.end_time = datetime.now(timezone.utc)
            execution_logger.info(f"Execution completed in {(execution_context.end_time - execution_context.start_time).total_seconds():.2f}s")
        
        return execution_context
    
    async def _execute_sequential(self, task_graph: TaskGraph, execution_context: ExecutionContext, 
                                 execution_logger: ExecutionLogger, evidence_capture: EvidenceCapture):
        """Execute tasks sequentially."""
        execution_logger.info("Executing tasks sequentially")
        
        # Create task dependency map
        task_map = {task.task_id: task for task in task_graph.tasks}
        completed_tasks = set()
        
        # Execute tasks in dependency order
        while len(completed_tasks) < len(task_graph.tasks):
            # Find tasks ready to execute
            ready_tasks = []
            for task in task_graph.tasks:
                if task.task_id not in completed_tasks:
                    dependencies_met = all(dep_id in completed_tasks for dep_id in task.dependencies)
                    if dependencies_met:
                        ready_tasks.append(task)
            
            if not ready_tasks:
                # No tasks ready - check for circular dependencies
                remaining_tasks = [t for t in task_graph.tasks if t.task_id not in completed_tasks]
                execution_logger.error(f"No tasks ready to execute. Remaining: {[t.task_id for t in remaining_tasks]}")
                break
            
            # Execute ready tasks
            for task in ready_tasks:
                await self._execute_task(task, execution_context, execution_logger, evidence_capture)
                completed_tasks.add(task.task_id)
    
    async def _execute_parallel(self, task_graph: TaskGraph, execution_context: ExecutionContext,
                               execution_logger: ExecutionLogger, evidence_capture: EvidenceCapture):
        """Execute tasks in parallel where possible."""
        execution_logger.info("Executing tasks in parallel")
        
        # Create task dependency map
        task_map = {task.task_id: task for task in task_graph.tasks}
        completed_tasks = set()
        running_tasks = set()
        
        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(self.config.max_concurrent_tasks)
        
        async def execute_task_with_semaphore(task: Task):
            async with semaphore:
                await self._execute_task(task, execution_context, execution_logger, evidence_capture)
                return task.task_id
        
        # Execute tasks in waves
        while len(completed_tasks) < len(task_graph.tasks):
            # Find tasks ready to execute
            ready_tasks = []
            for task in task_graph.tasks:
                if task.task_id not in completed_tasks and task.task_id not in running_tasks:
                    dependencies_met = all(dep_id in completed_tasks for dep_id in task.dependencies)
                    if dependencies_met:
                        ready_tasks.append(task)
            
            if not ready_tasks:
                if running_tasks:
                    # Wait for running tasks to complete
                    await asyncio.sleep(0.1)
                    continue
                else:
                    # No tasks ready - check for issues
                    remaining_tasks = [t for t in task_graph.tasks if t.task_id not in completed_tasks]
                    execution_logger.error(f"No tasks ready to execute. Remaining: {[t.task_id for t in remaining_tasks]}")
                    break
            
            # Execute ready tasks in parallel
            execution_logger.info(f"Executing {len(ready_tasks)} tasks in parallel")
            running_tasks.update(task.task_id for task in ready_tasks)
            
            # Wait for tasks to complete
            completed_task_ids = await asyncio.gather(*[
                execute_task_with_semaphore(task) for task in ready_tasks
            ])
            
            completed_tasks.update(completed_task_ids)
            running_tasks.difference_update(completed_task_ids)
    
    async def _execute_task(self, task: Task, execution_context: ExecutionContext,
                           execution_logger: ExecutionLogger, evidence_capture: EvidenceCapture):
        """Execute a single task."""
        execution_logger.info(f"Executing task: {task.name}", task.task_id)
        execution_context.current_task = task.task_id
        
        # Capture input evidence
        evidence_capture.capture_input(task.task_id, task.input_data, {
            "required_tools": task.required_tools,
            "dependencies": task.dependencies
        })
        
        start_time = time.time()
        retry_count = 0
        
        while retry_count <= execution_context.max_retries:
            try:
                # Execute task
                result = await self._execute_task_with_tools(task, execution_logger, evidence_capture)
                
                # Update task status
                task.status = TaskStatus.COMPLETED
                execution_context.completed_tasks.append(task.task_id)
                
                # Capture output evidence
                evidence_capture.capture_output(task.task_id, result.output_data, {
                    "execution_time_ms": result.execution_time_ms,
                    "status": result.status.value
                })
                
                # Capture performance evidence
                execution_time = time.time() - start_time
                evidence_capture.capture_performance(task.task_id, {
                    "execution_time": execution_time,
                    "retry_count": retry_count,
                    "tools_used": task.required_tools
                })
                
                execution_logger.info(f"Task completed successfully in {execution_time:.2f}s", task.task_id)
                break
                
            except Exception as e:
                retry_count += 1
                execution_context.retry_count += 1
                
                # Capture error evidence
                evidence_capture.capture_error(task.task_id, e, {
                    "retry_count": retry_count,
                    "max_retries": execution_context.max_retries
                })
                
                # Check if should retry
                if await self.retry_manager.should_retry(task.task_id, e, retry_count):
                    delay = await self.retry_manager.get_retry_delay(retry_count)
                    execution_logger.warning(f"Task failed, retrying in {delay:.2f}s (attempt {retry_count + 1})", task.task_id, {
                        "error": str(e),
                        "retry_count": retry_count
                    })
                    
                    if delay > 0:
                        await asyncio.sleep(delay)
                    continue
                else:
                    # Task failed permanently
                    task.status = TaskStatus.FAILED
                    execution_context.failed_tasks.append(task.task_id)
                    execution_logger.error(f"Task failed permanently after {retry_count} retries", task.task_id, {
                        "error": str(e),
                        "retry_count": retry_count
                    })
                    break
        
        execution_context.current_task = None
    
    async def _execute_task_with_tools(self, task: Task, execution_logger: ExecutionLogger, 
                                      evidence_capture: EvidenceCapture) -> TaskResult:
        """Execute task using available tools."""
        execution_logger.debug(f"Executing task with tools: {task.required_tools}", task.task_id)
        
        # Validate tool availability
        available_tools = self.tool_executor.get_available_tools()
        available_tool_names = [tool.name for tool in available_tools]
        
        missing_tools = [tool for tool in task.required_tools if tool not in available_tool_names]
        if missing_tools:
            raise ValueError(f"Missing required tools: {missing_tools}")
        
        # Execute tools
        tool_results = {}
        for tool_name in task.required_tools:
            try:
                execution_logger.debug(f"Executing tool: {tool_name}", task.task_id)
                
                # Validate tool call
                if not self.tool_executor.validate_tool_call(tool_name, task.input_data):
                    raise ValueError(f"Invalid parameters for tool: {tool_name}")
                
                # Execute tool with timeout
                tool_result = await asyncio.wait_for(
                    self.tool_executor.execute(tool_name, task.input_data, task.metadata),
                    timeout=self.config.task_timeout
                )
                
                tool_results[tool_name] = tool_result
                execution_logger.debug(f"Tool {tool_name} completed successfully", task.task_id)
                
            except asyncio.TimeoutError:
                raise TimeoutError(f"Tool {tool_name} timed out after {self.config.task_timeout}s")
            except Exception as e:
                raise Exception(f"Tool {tool_name} failed: {e}")
        
        # Create task result
        execution_time = time.time()
        result = TaskResult(
            task_id=task.task_id,
            status=TaskStatus.COMPLETED,
            output_data=tool_results,
            execution_time_ms=(execution_time - time.time()) * 1000,
            metadata={
                "tools_used": task.required_tools,
                "tool_results": tool_results
            }
        )
        
        return result
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get runner statistics."""
        success_rate = (self.successful_executions / self.total_executions * 100) if self.total_executions > 0 else 0
        
        return {
            "total_executions": self.total_executions,
            "successful_executions": self.successful_executions,
            "failed_executions": self.failed_executions,
            "success_rate": success_rate,
            "total_tasks_executed": self.total_tasks_executed,
            "total_retries": self.total_retries,
            "average_retries_per_execution": self.total_retries / self.total_executions if self.total_executions > 0 else 0
        }


# ============================================================================
# Factory Functions
# ============================================================================

def create_task_runner(
    max_concurrent_tasks: int = 5,
    task_timeout: float = 300.0,
    max_retries: int = 3,
    retry_strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF,
    log_level: LogLevel = LogLevel.INFO,
    enable_evidence_capture: bool = True,
    tool_executor: Optional[ToolExecutor] = None
) -> TaskRunner:
    """Create a task runner with specified configuration."""
    config = RunnerConfig(
        max_concurrent_tasks=max_concurrent_tasks,
        task_timeout=task_timeout,
        retry_config=RetryConfig(
            strategy=retry_strategy,
            max_retries=max_retries
        ),
        logging_config=LoggingConfig(level=log_level),
        evidence_config=EvidenceConfig() if enable_evidence_capture else EvidenceConfig(
            capture_input=False,
            capture_output=False,
            capture_errors=False,
            capture_performance=False
        )
    )
    
    return TaskRunner(config, tool_executor)


def create_runner_config(
    max_concurrent_tasks: int = 5,
    task_timeout: float = 300.0,
    max_retries: int = 3,
    retry_strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF,
    log_level: LogLevel = LogLevel.INFO,
    enable_evidence_capture: bool = True
) -> RunnerConfig:
    """Create a runner configuration."""
    return RunnerConfig(
        max_concurrent_tasks=max_concurrent_tasks,
        task_timeout=task_timeout,
        retry_config=RetryConfig(
            strategy=retry_strategy,
            max_retries=max_retries
        ),
        logging_config=LoggingConfig(level=log_level),
        evidence_config=EvidenceConfig() if enable_evidence_capture else EvidenceConfig(
            capture_input=False,
            capture_output=False,
            capture_errors=False,
            capture_performance=False
        )
    )


# ============================================================================
# Export all classes and functions
# ============================================================================

__all__ = [
    # Enums
    "ExecutionStatus",
    "RetryStrategy", 
    "LogLevel",
    
    # Models
    "ExecutionContext",
    "ExecutionLog",
    "ExecutionEvidence",
    "RetryConfig",
    "LoggingConfig",
    "EvidenceConfig",
    "RunnerConfig",
    
    # Tool interface
    "ToolExecutor",
    "MockToolExecutor",
    
    # Components
    "RetryManager",
    "ExecutionLogger",
    "EvidenceCapture",
    
    # Main runner
    "TaskRunner",
    
    # Factory functions
    "create_task_runner",
    "create_runner_config",
]
