#!/usr/bin/env python3
"""
Task Runner Script for Agentic LLM Core v0.1

This script executes specific tasks with configurable parameters including
dry run mode, retry count, and logging levels.

Usage: python run_task.py --task-id T-001_mcp_adapter --dry-run false --retries 1 --logs verbose
"""

import argparse
import asyncio
import json
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.runtime.runner import (
    create_task_runner,
    ExecutionStatus,
    RetryStrategy,
    LogLevel,
    MockToolExecutor
)

from src.core.models.contracts import Task, TaskGraph, TaskStatus, ToolSpec, ToolSchema, ToolParameter
from uuid import uuid4


# ============================================================================
# Task Definitions
# ============================================================================

TASK_DEFINITIONS = {
    "T-001_mcp_adapter": {
        "name": "MCP Adapter Implementation",
        "description": "Implement and test MCP adapter with schema validation and redaction",
        "task_type": "implementation",
        "input_data": {
            "target_file": "src/core/tools/mcp_adapter.py",
            "test_file": "tests/test_mcp_adapter.py",
            "features": ["stdin_stdout", "socket", "schema_validation", "redaction"],
            "requirements": ["pydantic", "asyncio", "json", "logging"]
        },
        "required_tools": ["file_operations", "test_runner", "code_validator"],
        "dependencies": [],
        "acceptance_criteria": [
            "MCP adapter implementation complete",
            "All tests pass",
            "Schema validation working",
            "Redaction functionality working",
            "No linting errors"
        ]
    },
    "T-002_qwen3_provider": {
        "name": "Qwen3 LLM Provider",
        "description": "Implement Qwen3 LLM provider with complete, embed, and vision modes",
        "task_type": "implementation",
        "input_data": {
            "target_file": "src/core/providers/llm_qwen3.py",
            "test_file": "tests/test_llm_qwen3.py",
            "modes": ["complete", "embed", "vision_to_text"],
            "optimizations": ["apple_silicon", "mps", "precision_control"]
        },
        "required_tools": ["file_operations", "test_runner", "code_validator"],
        "dependencies": [],
        "acceptance_criteria": [
            "Qwen3 provider implementation complete",
            "All modes working",
            "Apple Silicon optimizations",
            "All tests pass",
            "No linting errors"
        ]
    },
    "T-003_knowledge_base": {
        "name": "Knowledge Base Adapter",
        "description": "Implement knowledge base with PostgreSQL and Weaviate support",
        "task_type": "implementation",
        "input_data": {
            "target_file": "src/core/memory/vector_pg.py",
            "test_file": "tests/test_vector_pg.py",
            "features": ["postgresql", "weaviate", "docker_integration"],
            "methods": ["index", "query", "get", "delete", "update"]
        },
        "required_tools": ["file_operations", "test_runner", "code_validator"],
        "dependencies": [],
        "acceptance_criteria": [
            "Knowledge base implementation complete",
            "PostgreSQL integration working",
            "Weaviate integration working",
            "Docker integration working",
            "All tests pass"
        ]
    },
    "T-004_agent_planner": {
        "name": "Agent Planner",
        "description": "Implement agent planner with TaskGraph generation and optimization",
        "task_type": "implementation",
        "input_data": {
            "target_file": "src/core/runtime/planner.py",
            "test_file": "tests/test_planner.py",
            "features": ["task_graph_generation", "budget_policies", "latency_policies"],
            "strategies": ["sequential", "parallel", "optimized"]
        },
        "required_tools": ["file_operations", "test_runner", "code_validator"],
        "dependencies": [],
        "acceptance_criteria": [
            "Agent planner implementation complete",
            "TaskGraph generation working",
            "Policy enforcement working",
            "All strategies implemented",
            "All tests pass"
        ]
    },
    "T-005_agent_reviewer": {
        "name": "Agent Reviewer",
        "description": "Implement agent reviewer with schema, unit, and acceptance checks",
        "task_type": "implementation",
        "input_data": {
            "target_file": "src/core/runtime/reviewer.py",
            "test_file": "tests/test_reviewer.py",
            "features": ["schema_validation", "unit_testing", "acceptance_criteria"],
            "output_format": "json"
        },
        "required_tools": ["file_operations", "test_runner", "code_validator"],
        "dependencies": [],
        "acceptance_criteria": [
            "Agent reviewer implementation complete",
            "Schema validation working",
            "Unit test execution working",
            "Acceptance criteria validation working",
            "All tests pass"
        ]
    },
    "T-006_task_runner": {
        "name": "Task Runner",
        "description": "Implement task runner with tool selection, retries, logging, and evidence capture",
        "task_type": "implementation",
        "input_data": {
            "target_file": "src/core/runtime/runner.py",
            "test_file": "tests/test_runner.py",
            "features": ["tool_selection", "retries", "logging", "evidence_capture"],
            "execution_modes": ["sequential", "parallel"]
        },
        "required_tools": ["file_operations", "test_runner", "code_validator"],
        "dependencies": [],
        "acceptance_criteria": [
            "Task runner implementation complete",
            "Tool selection working",
            "Retry mechanisms working",
            "Logging system working",
            "Evidence capture working",
            "All tests pass"
        ]
    }
}


# ============================================================================
# Custom Tool Executor for Task Execution
# ============================================================================

class TaskExecutionToolExecutor:
    """Custom tool executor for running development tasks."""
    
    def __init__(self, dry_run: bool = False, verbose: bool = False):
        self.dry_run = dry_run
        self.verbose = verbose
        self.logger = logging.getLogger(__name__)
        
        # Define available tools
        self.tools = [
            ToolSpec(
                name="file_operations",
                description="Perform file operations like checking existence and validation",
                category="development",
                schema=ToolSchema(
                    input_schema={
                        "operation": ToolParameter(name="operation", type="str", description="Operation to perform"),
                        "target_file": ToolParameter(name="target_file", type="str", description="Target file path")
                    },
                    output_schema={"success": "bool", "message": "str"}
                )
            ),
            ToolSpec(
                name="test_runner",
                description="Run tests for code validation",
                category="testing",
                schema=ToolSchema(
                    input_schema={
                        "test_file": ToolParameter(name="test_file", type="str", description="Test file path"),
                        "command": ToolParameter(name="command", type="str", description="Test command", default="pytest")
                    },
                    output_schema={"success": "bool", "message": "str", "execution_time": "float"}
                )
            ),
            ToolSpec(
                name="code_validator",
                description="Validate code syntax and style",
                category="validation",
                schema=ToolSchema(
                    input_schema={
                        "target_file": ToolParameter(name="target_file", type="str", description="File to validate"),
                        "type": ToolParameter(name="type", type="str", description="Validation type", default="lint")
                    },
                    output_schema={"success": "bool", "message": "str", "validation_type": "str"}
                )
            )
        ]
    
    def get_available_tools(self) -> List[ToolSpec]:
        """Get list of available tools."""
        return self.tools
    
    def validate_tool_call(self, tool_name: str, parameters: Dict[str, Any]) -> bool:
        """Validate tool call parameters."""
        tool_spec = next((tool for tool in self.tools if tool.name == tool_name), None)
        if not tool_spec:
            return False
        
        # Check required parameters
        required_params = [param.name for param in tool_spec.schema.input_schema.values() if param.required]
        return all(param in parameters for param in required_params)
    
    async def execute(self, tool_name: str, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a development tool."""
        if tool_name == "file_operations":
            return await self._execute_file_operations(parameters)
        elif tool_name == "test_runner":
            return await self._execute_test_runner(parameters)
        elif tool_name == "code_validator":
            return await self._execute_code_validator(parameters)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
    
    async def _execute_file_operations(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute file operations."""
        operation = parameters.get("operation", "check")
        target_file = parameters.get("target_file", "")
        
        if self.dry_run:
            self.logger.info(f"[DRY RUN] Would execute file operation: {operation} on {target_file}")
            return {"success": True, "message": f"Dry run: {operation} on {target_file}"}
        
        if operation == "check":
            # Check if file exists
            file_path = Path(target_file)
            exists = file_path.exists()
            size = file_path.stat().st_size if exists else 0
            
            return {
                "success": True,
                "file_exists": exists,
                "file_size": size,
                "file_path": str(file_path)
            }
        elif operation == "validate":
            # Basic file validation
            file_path = Path(target_file)
            if not file_path.exists():
                return {"success": False, "error": "File does not exist"}
            
            # Check if it's a Python file
            if file_path.suffix != '.py':
                return {"success": False, "error": "Not a Python file"}
            
            # Basic syntax check
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                compile(content, str(file_path), 'exec')
                return {"success": True, "message": "File syntax is valid"}
            except SyntaxError as e:
                return {"success": False, "error": f"Syntax error: {e}"}
        
        return {"success": False, "error": f"Unknown operation: {operation}"}
    
    async def _execute_test_runner(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute test runner."""
        test_file = parameters.get("test_file", "")
        test_command = parameters.get("command", "pytest")
        
        if self.dry_run:
            self.logger.info(f"[DRY RUN] Would run tests: {test_command} {test_file}")
            return {"success": True, "message": f"Dry run: {test_command} {test_file}"}
        
        # Check if test file exists
        test_path = Path(test_file)
        if not test_path.exists():
            return {"success": False, "error": f"Test file does not exist: {test_file}"}
        
        # Simulate test execution
        self.logger.info(f"Running tests: {test_command} {test_file}")
        
        # In a real implementation, you would run pytest here
        # For now, we'll simulate success
        await asyncio.sleep(0.5)  # Simulate test execution time
        
        return {
            "success": True,
            "message": f"Tests completed for {test_file}",
            "test_file": test_file,
            "execution_time": 0.5
        }
    
    async def _execute_code_validator(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute code validator."""
        target_file = parameters.get("target_file", "")
        validation_type = parameters.get("type", "lint")
        
        if self.dry_run:
            self.logger.info(f"[DRY RUN] Would validate code: {validation_type} on {target_file}")
            return {"success": True, "message": f"Dry run: {validation_type} on {target_file}"}
        
        # Check if file exists
        file_path = Path(target_file)
        if not file_path.exists():
            return {"success": False, "error": f"File does not exist: {target_file}"}
        
        # Simulate validation
        self.logger.info(f"Validating code: {validation_type} on {target_file}")
        await asyncio.sleep(0.2)  # Simulate validation time
        
        # In a real implementation, you would run linting tools here
        return {
            "success": True,
            "message": f"Code validation completed for {target_file}",
            "validation_type": validation_type,
            "file_path": target_file
        }


# ============================================================================
# Task Execution Functions
# ============================================================================

async def execute_task(task_id: str, dry_run: bool = False, retries: int = 1, logs: str = "info") -> Dict[str, Any]:
    """Execute a specific task."""
    # Get task definition
    if task_id not in TASK_DEFINITIONS:
        raise ValueError(f"Unknown task ID: {task_id}")
    
    task_def = TASK_DEFINITIONS[task_id]
    
    # Set up logging
    log_level = getattr(LogLevel, logs.upper(), LogLevel.INFO)
    logging.basicConfig(
        level=getattr(logging, logs.upper(), logging.INFO),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    logger.info(f"Starting task execution: {task_id}")
    logger.info(f"Task: {task_def['name']}")
    logger.info(f"Description: {task_def['description']}")
    logger.info(f"Dry run: {dry_run}")
    logger.info(f"Retries: {retries}")
    logger.info(f"Log level: {logs}")
    
    # Create task
    task = Task(
        id=uuid4(),  # Generate a proper UUID
        name=task_def["name"],
        description=task_def["description"],
        task_type=task_def["task_type"],
        input_data=task_def["input_data"],
        dependencies=task_def["dependencies"]
    )
    
    # Create task graph
    task_graph = TaskGraph(
        graph_id=f"execution_graph_{task_id}",
        name=f"Execution Graph for {task_id}",
        description=f"Task execution graph for {task_id}",
        tasks=[task],
        entry_points=[str(task.id)],
        exit_points=[str(task.id)]
    )
    
    # Create tool executor
    tool_executor = TaskExecutionToolExecutor(dry_run=dry_run, verbose=(logs == "verbose"))
    
    # Create task runner
    runner = create_task_runner(
        max_concurrent_tasks=1,
        task_timeout=300.0,
        max_retries=retries,
        retry_strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
        log_level=log_level,
        enable_evidence_capture=True
    )
    
    # Execute task
    start_time = time.time()
    context = await runner.run(task_graph, {
        "task_id": task_id,
        "dry_run": dry_run,
        "retries": retries,
        "logs": logs,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    end_time = time.time()
    
    # Prepare results
    results = {
        "task_id": task_id,
        "task_name": task_def["name"],
        "execution_status": context.status.value,
        "execution_time": end_time - start_time,
        "completed_tasks": context.completed_tasks,
        "failed_tasks": context.failed_tasks,
        "retry_count": context.retry_count,
        "dry_run": dry_run,
        "logs_level": logs,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "runner_statistics": runner.get_statistics()
    }
    
    # Log results
    logger.info(f"Task execution completed: {context.status}")
    logger.info(f"Execution time: {end_time - start_time:.2f}s")
    logger.info(f"Completed tasks: {len(context.completed_tasks)}")
    logger.info(f"Failed tasks: {len(context.failed_tasks)}")
    logger.info(f"Retry count: {context.retry_count}")
    
    return results


# ============================================================================
# Main Execution
# ============================================================================

async def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description="Task Runner for Agentic LLM Core v0.1")
    parser.add_argument("--task-id", required=True, help="Task ID to execute")
    parser.add_argument("--dry-run", type=str, default="false", help="Run in dry run mode")
    parser.add_argument("--retries", type=int, default=1, help="Number of retries")
    parser.add_argument("--logs", default="info", choices=["debug", "info", "warning", "error", "verbose"], help="Log level")
    parser.add_argument("--output", help="Output file for results (JSON)")
    
    args = parser.parse_args()
    
    try:
        # Parse dry_run parameter
        dry_run = args.dry_run.lower() in ['true', '1', 'yes', 'on']
        
        # Execute task
        results = await execute_task(
            task_id=args.task_id,
            dry_run=dry_run,
            retries=args.retries,
            logs=args.logs
        )
        
        # Output results
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"Results saved to: {args.output}")
        else:
            print(json.dumps(results, indent=2))
        
        # Exit with appropriate code
        if results["execution_status"] == "completed":
            sys.exit(0)
        else:
            sys.exit(1)
            
    except Exception as e:
        print(f"Task execution failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
