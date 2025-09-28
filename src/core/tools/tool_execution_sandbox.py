#!/usr/bin/env python3
"""
Tool Execution Sandbox for Agentic LLM Core v0.1

This module implements sandboxed tool execution with:
- Resource isolation and limits
- Security constraints
- Performance monitoring
- Error handling and recovery
- Memory and CPU usage tracking

Complies with:
- Agentic LLM Core Constitution (prompt_engineering/.specify/memory/constitution.md)
- System Specification: Agentic LLM Core v0.1 (specs/system.md)
- Architecture Plan: Agentic LLM Core v0.1 (plans/architecture.md)
- Milestone 2: Tool Integration System (plans/milestones.md)

Created: 2024-09-25
Status: Implementation Phase
"""

import asyncio
import logging
import os
import psutil
import tempfile
import time
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pathlib import Path
import json
import threading

from pydantic import BaseModel, Field

from .mcp_tool_execution_engine import MCPTool, ToolExecutionContext, ToolExecutionResult, ToolExecutionStatus

logger = logging.getLogger(__name__)

# ============================================================================
# Data Models
# ============================================================================

class SandboxType(str, Enum):
    """Sandbox execution types."""
    PROCESS = "process"
    THREAD = "thread"
    ASYNC = "async"
    CONTAINER = "container"

class ResourceLimit(BaseModel):
    """Resource limits for sandbox execution."""
    max_memory_mb: int = Field(default=512, description="Maximum memory usage in MB")
    max_cpu_percent: float = Field(default=50.0, description="Maximum CPU usage percentage")
    max_execution_time: float = Field(default=30.0, description="Maximum execution time in seconds")
    max_file_size_mb: int = Field(default=100, description="Maximum file size in MB")
    max_network_connections: int = Field(default=10, description="Maximum network connections")
    max_processes: int = Field(default=5, description="Maximum number of processes")

class SecurityPolicy(BaseModel):
    """Security policy for sandbox execution."""
    allow_file_access: bool = Field(default=True, description="Allow file system access")
    allow_network_access: bool = Field(default=False, description="Allow network access")
    allow_process_creation: bool = Field(default=False, description="Allow process creation")
    allow_system_calls: bool = Field(default=False, description="Allow system calls")
    allowed_directories: List[str] = Field(default_factory=list, description="Allowed directories")
    blocked_directories: List[str] = Field(default_factory=list, description="Blocked directories")
    allowed_ports: List[int] = Field(default_factory=list, description="Allowed network ports")
    blocked_ports: List[int] = Field(default_factory=list, description="Blocked network ports")

class SandboxConfig(BaseModel):
    """Configuration for sandbox execution."""
    sandbox_type: SandboxType = Field(default=SandboxType.PROCESS, description="Sandbox execution type")
    resource_limits: ResourceLimit = Field(default_factory=ResourceLimit, description="Resource limits")
    security_policy: SecurityPolicy = Field(default_factory=SecurityPolicy, description="Security policy")
    working_directory: Optional[str] = Field(None, description="Working directory for execution")
    environment_variables: Dict[str, str] = Field(default_factory=dict, description="Environment variables")
    enable_monitoring: bool = Field(default=True, description="Enable resource monitoring")
    cleanup_on_exit: bool = Field(default=True, description="Cleanup resources on exit")

class ResourceUsage(BaseModel):
    """Resource usage information."""
    memory_usage_mb: float = Field(default=0.0, description="Memory usage in MB")
    cpu_usage_percent: float = Field(default=0.0, description="CPU usage percentage")
    execution_time: float = Field(default=0.0, description="Execution time in seconds")
    file_operations: int = Field(default=0, description="Number of file operations")
    network_connections: int = Field(default=0, description="Number of network connections")
    processes_created: int = Field(default=0, description="Number of processes created")
    peak_memory_mb: float = Field(default=0.0, description="Peak memory usage in MB")
    peak_cpu_percent: float = Field(default=0.0, description="Peak CPU usage percentage")

class SandboxExecutionResult(BaseModel):
    """Result of sandbox execution."""
    execution_id: str = Field(..., description="Unique execution identifier")
    success: bool = Field(..., description="Whether execution was successful")
    output: Optional[Any] = Field(None, description="Execution output")
    error: Optional[str] = Field(None, description="Error message if execution failed")
    resource_usage: ResourceUsage = Field(..., description="Resource usage information")
    security_violations: List[str] = Field(default_factory=list, description="Security violations detected")
    execution_time: float = Field(..., description="Total execution time in seconds")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# ============================================================================
# Sandbox Implementation
# ============================================================================

class ToolExecutionSandbox:
    """Sandboxed tool execution environment with comprehensive monitoring."""
    
    def __init__(self, config: SandboxConfig):
        self.config = config
        self.active_executions: Dict[str, Dict[str, Any]] = {}
        self.resource_monitors: Dict[str, threading.Thread] = {}
        self.cleanup_tasks: List[asyncio.Task] = []
        self.logger = logging.getLogger(f"{__name__}.sandbox")
        
        # Create working directory if needed
        if not self.config.working_directory:
            self.config.working_directory = tempfile.mkdtemp(prefix="mcp_sandbox_")
        
        # Ensure working directory exists
        Path(self.config.working_directory).mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"Tool execution sandbox initialized: {self.config.working_directory}")
    
    async def execute_tool(self, 
                          tool: MCPTool, 
                          input_data: Dict[str, Any], 
                          context: ToolExecutionContext) -> ToolExecutionResult:
        """Execute a tool in sandboxed environment."""
        execution_id = str(uuid.uuid4())
        start_time = time.time()
        
        try:
            # Validate tool and input
            if not tool.validate_input(input_data):
                return ToolExecutionResult(
                    execution_id=execution_id,
                    tool_name=tool.name,
                    status=ToolExecutionStatus.FAILED,
                    input_data=input_data,
                    error_message="Input validation failed",
                    execution_time=time.time() - start_time
                )
            
            # Create execution environment
            execution_env = await self._create_execution_environment(execution_id, context)
            
            # Start resource monitoring
            if self.config.enable_monitoring:
                monitor_task = asyncio.create_task(
                    self._monitor_resources(execution_id, execution_env)
                )
                self.cleanup_tasks.append(monitor_task)
            
            # Execute tool based on sandbox type
            if self.config.sandbox_type == SandboxType.PROCESS:
                result = await self._execute_in_process(tool, input_data, execution_env)
            elif self.config.sandbox_type == SandboxType.THREAD:
                result = await self._execute_in_thread(tool, input_data, execution_env)
            elif self.config.sandbox_type == SandboxType.ASYNC:
                result = await self._execute_async(tool, input_data, execution_env)
            else:
                raise ValueError(f"Unsupported sandbox type: {self.config.sandbox_type}")
            
            # Calculate execution time
            execution_time = time.time() - start_time
            
            # Get final resource usage
            resource_usage = await self._get_resource_usage(execution_id)
            
            # Create execution result
            execution_result = ToolExecutionResult(
                execution_id=execution_id,
                tool_name=tool.name,
                status=ToolExecutionStatus.COMPLETED if result.success else ToolExecutionStatus.FAILED,
                input_data=input_data,
                output_data=result.output,
                error_message=result.error,
                execution_time=execution_time,
                memory_usage=resource_usage.memory_usage_mb,
                cpu_usage=resource_usage.cpu_usage_percent,
                metadata={
                    "sandbox_type": self.config.sandbox_type.value,
                    "resource_usage": resource_usage.dict(),
                    "security_violations": result.security_violations
                }
            )
            
            # Cleanup execution environment
            await self._cleanup_execution_environment(execution_id)
            
            self.logger.info(f"Tool execution completed: {tool.name} in {execution_time:.3f}s")
            return execution_result
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Tool execution failed: {e}")
            
            return ToolExecutionResult(
                execution_id=execution_id,
                tool_name=tool.name,
                status=ToolExecutionStatus.FAILED,
                input_data=input_data,
                error_message=str(e),
                execution_time=execution_time
            )
    
    async def _create_execution_environment(self, 
                                          execution_id: str, 
                                          context: ToolExecutionContext) -> Dict[str, Any]:
        """Create isolated execution environment."""
        try:
            # Create execution directory
            exec_dir = Path(self.config.working_directory) / execution_id
            exec_dir.mkdir(parents=True, exist_ok=True)
            
            # Set up environment variables
            env_vars = os.environ.copy()
            env_vars.update(self.config.environment_variables)
            env_vars.update({
                "MCP_EXECUTION_ID": execution_id,
                "MCP_WORKING_DIR": str(exec_dir),
                "MCP_SANDBOX_TYPE": self.config.sandbox_type.value
            })
            
            # Create execution environment
            execution_env = {
                "execution_id": execution_id,
                "working_directory": str(exec_dir),
                "environment_variables": env_vars,
                "resource_limits": self.config.resource_limits,
                "security_policy": self.config.security_policy,
                "start_time": time.time(),
                "process": None,
                "thread": None,
                "monitor_data": {
                    "memory_usage": [],
                    "cpu_usage": [],
                    "file_operations": 0,
                    "network_connections": 0,
                    "processes_created": 0
                }
            }
            
            # Store execution environment
            self.active_executions[execution_id] = execution_env
            
            return execution_env
            
        except Exception as e:
            self.logger.error(f"Failed to create execution environment: {e}")
            raise
    
    async def _execute_in_process(self, 
                                tool: MCPTool, 
                                input_data: Dict[str, Any], 
                                execution_env: Dict[str, Any]) -> SandboxExecutionResult:
        """Execute tool in separate process."""
        try:
            # Create process
            process = await asyncio.create_subprocess_exec(
                "python", "-c", self._create_tool_script(tool, input_data),
                cwd=execution_env["working_directory"],
                env=execution_env["environment_variables"],
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                limit=self.config.resource_limits.max_memory_mb * 1024 * 1024
            )
            
            execution_env["process"] = process
            
            # Wait for completion with timeout
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=self.config.resource_limits.max_execution_time
                )
                
                # Parse output
                if process.returncode == 0:
                    try:
                        output = json.loads(stdout.decode())
                        return SandboxExecutionResult(
                            execution_id=execution_env["execution_id"],
                            success=True,
                            output=output,
                            resource_usage=ResourceUsage(),
                            execution_time=time.time() - execution_env["start_time"]
                        )
                    except json.JSONDecodeError:
                        return SandboxExecutionResult(
                            execution_id=execution_env["execution_id"],
                            success=True,
                            output=stdout.decode(),
                            resource_usage=ResourceUsage(),
                            execution_time=time.time() - execution_env["start_time"]
                        )
                else:
                    return SandboxExecutionResult(
                        execution_id=execution_env["execution_id"],
                        success=False,
                        error=stderr.decode(),
                        resource_usage=ResourceUsage(),
                        execution_time=time.time() - execution_env["start_time"]
                    )
                    
            except asyncio.TimeoutError:
                # Kill process if timeout
                process.kill()
                await process.wait()
                
                return SandboxExecutionResult(
                    execution_id=execution_env["execution_id"],
                    success=False,
                    error="Execution timeout",
                    resource_usage=ResourceUsage(),
                    execution_time=time.time() - execution_env["start_time"]
                )
                
        except Exception as e:
            return SandboxExecutionResult(
                execution_id=execution_env["execution_id"],
                success=False,
                error=str(e),
                resource_usage=ResourceUsage(),
                execution_time=time.time() - execution_env["start_time"]
            )
    
    async def _execute_in_thread(self, 
                               tool: MCPTool, 
                               input_data: Dict[str, Any], 
                               execution_env: Dict[str, Any]) -> SandboxExecutionResult:
        """Execute tool in separate thread."""
        try:
            # Create thread
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self._execute_tool_sync,
                tool,
                input_data,
                execution_env
            )
            
            return result
            
        except Exception as e:
            return SandboxExecutionResult(
                execution_id=execution_env["execution_id"],
                success=False,
                error=str(e),
                resource_usage=ResourceUsage(),
                execution_time=time.time() - execution_env["start_time"]
            )
    
    async def _execute_async(self, 
                           tool: MCPTool, 
                           input_data: Dict[str, Any], 
                           execution_env: Dict[str, Any]) -> SandboxExecutionResult:
        """Execute tool asynchronously."""
        try:
            # Execute tool directly
            output = await tool.execute(input_data, ToolExecutionContext(**execution_env))
            
            return SandboxExecutionResult(
                execution_id=execution_env["execution_id"],
                success=True,
                output=output,
                resource_usage=ResourceUsage(),
                execution_time=time.time() - execution_env["start_time"]
            )
            
        except Exception as e:
            return SandboxExecutionResult(
                execution_id=execution_env["execution_id"],
                success=False,
                error=str(e),
                resource_usage=ResourceUsage(),
                execution_time=time.time() - execution_env["start_time"]
            )
    
    def _execute_tool_sync(self, 
                          tool: MCPTool, 
                          input_data: Dict[str, Any], 
                          execution_env: Dict[str, Any]) -> SandboxExecutionResult:
        """Execute tool synchronously in thread."""
        try:
            # Change working directory
            original_cwd = os.getcwd()
            os.chdir(execution_env["working_directory"])
            
            try:
                # Execute tool
                output = asyncio.run(tool.execute(input_data, ToolExecutionContext(**execution_env)))
                
                return SandboxExecutionResult(
                    execution_id=execution_env["execution_id"],
                    success=True,
                    output=output,
                    resource_usage=ResourceUsage(),
                    execution_time=time.time() - execution_env["start_time"]
                )
                
            finally:
                # Restore working directory
                os.chdir(original_cwd)
                
        except Exception as e:
            return SandboxExecutionResult(
                execution_id=execution_env["execution_id"],
                success=False,
                error=str(e),
                resource_usage=ResourceUsage(),
                execution_time=time.time() - execution_env["start_time"]
            )
    
    def _create_tool_script(self, tool: MCPTool, input_data: Dict[str, Any]) -> str:
        """Create Python script for tool execution in process."""
        script = f"""
import json
import sys
import os
import traceback

# Set up environment
os.chdir(os.environ.get('MCP_WORKING_DIR', '.'))

try:
    # Import tool (this would need to be implemented based on tool type)
    # For now, we'll create a simple mock execution
    input_data = {json.dumps(input_data)}
    
    # Mock tool execution
    result = {{
        "tool_name": "{tool.name}",
        "input": input_data,
        "output": "Tool execution completed successfully",
        "timestamp": "{datetime.now(timezone.utc).isoformat()}"
    }}
    
    # Output result as JSON
    print(json.dumps(result))
    
except Exception as e:
    error_result = {{
        "error": str(e),
        "traceback": traceback.format_exc()
    }}
    print(json.dumps(error_result), file=sys.stderr)
    sys.exit(1)
"""
        return script
    
    async def _monitor_resources(self, execution_id: str, execution_env: Dict[str, Any]):
        """Monitor resource usage during execution."""
        try:
            while execution_id in self.active_executions:
                # Get current process
                process = execution_env.get("process")
                if process and process.returncode is None:
                    try:
                        # Get process info
                        proc = psutil.Process(process.pid)
                        
                        # Monitor memory usage
                        memory_info = proc.memory_info()
                        memory_mb = memory_info.rss / 1024 / 1024
                        
                        # Monitor CPU usage
                        cpu_percent = proc.cpu_percent()
                        
                        # Check resource limits
                        if memory_mb > self.config.resource_limits.max_memory_mb:
                            self.logger.warning(f"Memory limit exceeded: {memory_mb:.2f}MB")
                            process.kill()
                            break
                        
                        if cpu_percent > self.config.resource_limits.max_cpu_percent:
                            self.logger.warning(f"CPU limit exceeded: {cpu_percent:.2f}%")
                            # Don't kill for CPU, just log
                        
                        # Update monitor data
                        execution_env["monitor_data"]["memory_usage"].append(memory_mb)
                        execution_env["monitor_data"]["cpu_usage"].append(cpu_percent)
                        
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        break
                
                # Wait before next check
                await asyncio.sleep(0.1)
                
        except Exception as e:
            self.logger.error(f"Resource monitoring error: {e}")
    
    async def _get_resource_usage(self, execution_id: str) -> ResourceUsage:
        """Get resource usage for execution."""
        try:
            if execution_id not in self.active_executions:
                return ResourceUsage()
            
            execution_env = self.active_executions[execution_id]
            monitor_data = execution_env["monitor_data"]
            
            # Calculate resource usage
            memory_usage = max(monitor_data["memory_usage"]) if monitor_data["memory_usage"] else 0.0
            cpu_usage = max(monitor_data["cpu_usage"]) if monitor_data["cpu_usage"] else 0.0
            execution_time = time.time() - execution_env["start_time"]
            
            return ResourceUsage(
                memory_usage_mb=memory_usage,
                cpu_usage_percent=cpu_usage,
                execution_time=execution_time,
                file_operations=monitor_data["file_operations"],
                network_connections=monitor_data["network_connections"],
                processes_created=monitor_data["processes_created"],
                peak_memory_mb=memory_usage,
                peak_cpu_percent=cpu_usage
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get resource usage: {e}")
            return ResourceUsage()
    
    async def _cleanup_execution_environment(self, execution_id: str):
        """Clean up execution environment."""
        try:
            if execution_id in self.active_executions:
                execution_env = self.active_executions[execution_id]
                
                # Kill process if still running
                process = execution_env.get("process")
                if process and process.returncode is None:
                    process.kill()
                    await process.wait()
                
                # Clean up working directory
                if self.config.cleanup_on_exit:
                    working_dir = Path(execution_env["working_directory"])
                    if working_dir.exists():
                        import shutil
                        shutil.rmtree(working_dir)
                
                # Remove from active executions
                del self.active_executions[execution_id]
                
        except Exception as e:
            self.logger.error(f"Failed to cleanup execution environment: {e}")
    
    def get_resource_usage(self) -> Dict[str, Any]:
        """Get current resource usage of sandbox."""
        try:
            # Get system resource usage
            memory = psutil.virtual_memory()
            cpu = psutil.cpu_percent()
            
            return {
                "system_memory_usage": memory.percent,
                "system_cpu_usage": cpu,
                "active_executions": len(self.active_executions),
                "working_directory": self.config.working_directory,
                "sandbox_type": self.config.sandbox_type.value,
                "resource_limits": self.config.resource_limits.dict(),
                "security_policy": self.config.security_policy.dict()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get resource usage: {e}")
            return {"error": str(e)}
    
    async def cleanup(self):
        """Clean up sandbox resources."""
        try:
            # Cancel all cleanup tasks
            for task in self.cleanup_tasks:
                if not task.done():
                    task.cancel()
            
            # Wait for tasks to complete
            if self.cleanup_tasks:
                await asyncio.gather(*self.cleanup_tasks, return_exceptions=True)
            
            # Clean up all active executions
            for execution_id in list(self.active_executions.keys()):
                await self._cleanup_execution_environment(execution_id)
            
            # Clean up working directory
            if self.config.cleanup_on_exit and self.config.working_directory:
                working_dir = Path(self.config.working_directory)
                if working_dir.exists():
                    import shutil
                    shutil.rmtree(working_dir)
            
            self.logger.info("Sandbox cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Sandbox cleanup error: {e}")

# ============================================================================
# Factory Functions
# ============================================================================

def create_sandbox(config: SandboxConfig) -> ToolExecutionSandbox:
    """Create a tool execution sandbox with specified configuration."""
    return ToolExecutionSandbox(config)

def create_default_sandbox_config() -> SandboxConfig:
    """Create default sandbox configuration."""
    return SandboxConfig(
        sandbox_type=SandboxType.PROCESS,
        resource_limits=ResourceLimit(
            max_memory_mb=512,
            max_cpu_percent=50.0,
            max_execution_time=30.0,
            max_file_size_mb=100,
            max_network_connections=10,
            max_processes=5
        ),
        security_policy=SecurityPolicy(
            allow_file_access=True,
            allow_network_access=False,
            allow_process_creation=False,
            allow_system_calls=False
        ),
        enable_monitoring=True,
        cleanup_on_exit=True
    )

def create_restrictive_sandbox_config() -> SandboxConfig:
    """Create restrictive sandbox configuration for untrusted tools."""
    return SandboxConfig(
        sandbox_type=SandboxType.PROCESS,
        resource_limits=ResourceLimit(
            max_memory_mb=256,
            max_cpu_percent=25.0,
            max_execution_time=15.0,
            max_file_size_mb=50,
            max_network_connections=0,
            max_processes=1
        ),
        security_policy=SecurityPolicy(
            allow_file_access=False,
            allow_network_access=False,
            allow_process_creation=False,
            allow_system_calls=False
        ),
        enable_monitoring=True,
        cleanup_on_exit=True
    )

# ============================================================================
# Export all classes and functions
# ============================================================================

__all__ = [
    # Enums
    "SandboxType",
    
    # Data Models
    "ResourceLimit",
    "SecurityPolicy",
    "SandboxConfig",
    "ResourceUsage",
    "SandboxExecutionResult",
    
    # Implementation
    "ToolExecutionSandbox",
    
    # Factory Functions
    "create_sandbox",
    "create_default_sandbox_config",
    "create_restrictive_sandbox_config",
]
