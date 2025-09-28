#!/usr/bin/env python3
"""
MCP Tool Execution Engine for Agentic LLM Core v0.1

This module implements the MCP tool execution engine with:
- Tool selection and routing logic
- Sandboxed tool execution
- Input/output validation
- Execution history tracking
- Error handling and recovery

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
import time
import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Union
import json

from pydantic import BaseModel, Field

from ..models.contracts import ToolCall, ToolSchema
from ..engines.qwen3_omni_engine import ContextAnalysis

logger = logging.getLogger(__name__)

# ============================================================================
# Data Models
# ============================================================================

class ToolExecutionStatus(str, Enum):
    """Tool execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"

class ToolExecutionPriority(int, Enum):
    """Tool execution priority levels."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

class ToolExecutionResult(BaseModel):
    """Tool execution result with comprehensive metadata."""
    execution_id: str = Field(..., description="Unique execution identifier")
    tool_name: str = Field(..., description="Name of the executed tool")
    status: ToolExecutionStatus = Field(..., description="Execution status")
    input_data: Dict[str, Any] = Field(..., description="Input data provided to tool")
    output_data: Optional[Dict[str, Any]] = Field(None, description="Output data from tool")
    error_message: Optional[str] = Field(None, description="Error message if execution failed")
    execution_time: float = Field(..., description="Execution time in seconds")
    memory_usage: Optional[int] = Field(None, description="Memory usage in bytes")
    cpu_usage: Optional[float] = Field(None, description="CPU usage percentage")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class ToolExecutionContext(BaseModel):
    """Context for tool execution."""
    execution_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tool_name: str = Field(..., description="Name of the tool to execute")
    input_schema: ToolSchema = Field(..., description="Input schema for validation")
    output_schema: ToolSchema = Field(..., description="Output schema for validation")
    priority: ToolExecutionPriority = Field(default=ToolExecutionPriority.NORMAL)
    timeout: float = Field(default=30.0, description="Execution timeout in seconds")
    retry_count: int = Field(default=0, description="Number of retries attempted")
    max_retries: int = Field(default=3, description="Maximum number of retries")
    sandbox_config: Dict[str, Any] = Field(default_factory=dict, description="Sandbox configuration")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional context metadata")

class ToolSelectionCriteria(BaseModel):
    """Criteria for tool selection."""
    context_analysis: ContextAnalysis = Field(..., description="Context analysis for tool selection")
    required_capabilities: List[str] = Field(default_factory=list, description="Required tool capabilities")
    preferred_tools: List[str] = Field(default_factory=list, description="Preferred tool names")
    excluded_tools: List[str] = Field(default_factory=list, description="Excluded tool names")
    max_tools: int = Field(default=5, description="Maximum number of tools to select")
    priority_threshold: ToolExecutionPriority = Field(default=ToolExecutionPriority.LOW)

class ToolExecutionMetrics(BaseModel):
    """Metrics for tool execution performance."""
    total_executions: int = Field(default=0)
    successful_executions: int = Field(default=0)
    failed_executions: int = Field(default=0)
    average_execution_time: float = Field(default=0.0)
    total_execution_time: float = Field(default=0.0)
    memory_usage_peak: int = Field(default=0)
    cpu_usage_peak: float = Field(default=0.0)
    error_rate: float = Field(default=0.0)
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# ============================================================================
# Tool Execution Interfaces
# ============================================================================

class MCPTool(ABC):
    """Abstract base class for MCP tools."""
    
    def __init__(self, name: str, description: str, schema: ToolSchema):
        self.name = name
        self.description = description
        self.schema = schema
        self.execution_count = 0
        self.last_execution = None
        self.metrics = ToolExecutionMetrics()
    
    @abstractmethod
    async def execute(self, input_data: Dict[str, Any], context: ToolExecutionContext) -> Dict[str, Any]:
        """Execute the tool with given input data and context."""
        pass
    
    @abstractmethod
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data against tool schema."""
        pass
    
    @abstractmethod
    def validate_output(self, output_data: Dict[str, Any]) -> bool:
        """Validate output data against tool schema."""
        pass
    
    def get_capabilities(self) -> List[str]:
        """Get list of tool capabilities."""
        return getattr(self, 'capabilities', [])
    
    def is_available(self) -> bool:
        """Check if tool is available for execution."""
        return True
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get tool health status."""
        return {
            "name": self.name,
            "available": self.is_available(),
            "execution_count": self.execution_count,
            "last_execution": self.last_execution.isoformat() if self.last_execution else None,
            "metrics": self.metrics.dict()
        }

class ToolExecutionSandbox(ABC):
    """Abstract base class for tool execution sandboxes."""
    
    @abstractmethod
    async def execute_tool(self, tool: MCPTool, input_data: Dict[str, Any], context: ToolExecutionContext) -> ToolExecutionResult:
        """Execute tool in sandboxed environment."""
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """Clean up sandbox resources."""
        pass
    
    @abstractmethod
    def get_resource_usage(self) -> Dict[str, Any]:
        """Get current resource usage."""
        pass

# ============================================================================
# Tool Registry Implementation
# ============================================================================

class MCPToolRegistry:
    """Registry for managing MCP tools with schema validation and versioning."""
    
    def __init__(self):
        self.tools: Dict[str, MCPTool] = {}
        self.schemas: Dict[str, ToolSchema] = {}
        self.capabilities_index: Dict[str, List[str]] = {}
        self.version_history: Dict[str, List[str]] = {}
        self.logger = logging.getLogger(f"{__name__}.registry")
    
    def register_tool(self, tool: MCPTool, schema: ToolSchema, version: str = "1.0.0") -> bool:
        """Register a tool with schema validation."""
        try:
            # Validate schema
            if not self._validate_schema(schema):
                self.logger.error(f"Invalid schema for tool {tool.name}")
                return False
            
            # Register tool
            self.tools[tool.name] = tool
            self.schemas[tool.name] = schema
            
            # Update capabilities index
            capabilities = tool.get_capabilities()
            for capability in capabilities:
                if capability not in self.capabilities_index:
                    self.capabilities_index[capability] = []
                if tool.name not in self.capabilities_index[capability]:
                    self.capabilities_index[capability].append(tool.name)
            
            # Track version history
            if tool.name not in self.version_history:
                self.version_history[tool.name] = []
            self.version_history[tool.name].append(version)
            
            self.logger.info(f"Successfully registered tool: {tool.name} v{version}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register tool {tool.name}: {e}")
            return False
    
    def unregister_tool(self, tool_name: str) -> bool:
        """Unregister a tool."""
        if tool_name not in self.tools:
            return False
        
        # Remove from tools and schemas
        del self.tools[tool_name]
        del self.schemas[tool_name]
        
        # Remove from capabilities index
        for capability, tools in self.capabilities_index.items():
            if tool_name in tools:
                tools.remove(tool_name)
        
        self.logger.info(f"Successfully unregistered tool: {tool_name}")
        return True
    
    def get_tool(self, tool_name: str) -> Optional[MCPTool]:
        """Get a tool by name."""
        return self.tools.get(tool_name)
    
    def get_tools_by_capability(self, capability: str) -> List[MCPTool]:
        """Get tools that provide a specific capability."""
        tool_names = self.capabilities_index.get(capability, [])
        return [self.tools[name] for name in tool_names if name in self.tools]
    
    def discover_tools(self, criteria: Union[ToolSelectionCriteria, Dict[str, Any]]) -> List[MCPTool]:
        """Discover tools based on selection criteria."""
        available_tools = []
        
        # Handle both ToolSelectionCriteria and dict inputs
        if isinstance(criteria, dict):
            # Convert dict to ToolSelectionCriteria-like object
            class Criteria:
                def __init__(self, data):
                    self.excluded_tools = data.get('excluded_tools', [])
                    self.required_capabilities = data.get('required_capabilities', [])
                    self.preferred_tools = data.get('preferred_tools', [])
                    self.max_tools = data.get('max_tools', 5)
                    self.context_analysis = data.get('context_analysis', None)
            
            criteria = Criteria(criteria)
        
        for tool_name, tool in self.tools.items():
            # Check if tool is available
            if not tool.is_available():
                continue
            
            # Check if tool is excluded
            if tool_name in criteria.excluded_tools:
                continue
            
            # Check if tool matches required capabilities
            tool_capabilities = tool.get_capabilities()
            if criteria.required_capabilities:
                if not any(cap in tool_capabilities for cap in criteria.required_capabilities):
                    continue
            
            # Check if tool matches context analysis
            if criteria.context_analysis and self._tool_matches_context(tool, criteria.context_analysis):
                available_tools.append(tool)
            elif not criteria.context_analysis:
                available_tools.append(tool)
        
        # Sort by preference and priority
        available_tools.sort(key=lambda t: (
            t.name in criteria.preferred_tools,
            t.metrics.successful_executions / max(t.metrics.total_executions, 1),
            -t.metrics.average_execution_time
        ), reverse=True)
        
        # Limit to max_tools
        return available_tools[:criteria.max_tools]
    
    def _validate_schema(self, schema: ToolSchema) -> bool:
        """Validate tool schema."""
        try:
            # Basic schema validation
            if not schema.input_schema or not schema.output_schema:
                return False
            
            # Additional validation logic can be added here
            return True
            
        except Exception as e:
            self.logger.error(f"Schema validation failed: {e}")
            return False
    
    def _tool_matches_context(self, tool: MCPTool, context_analysis: ContextAnalysis) -> bool:
        """Check if tool matches context analysis."""
        # Simple matching logic - can be enhanced
        tool_capabilities = tool.get_capabilities()
        
        # Match based on intent
        if "file" in context_analysis.intent.lower() and "file" in tool_capabilities:
            return True
        
        if "database" in context_analysis.intent.lower() and "database" in tool_capabilities:
            return True
        
        if "web" in context_analysis.intent.lower() and "web" in tool_capabilities:
            return True
        
        # Match based on entities
        for entity in context_analysis.entities:
            if entity.lower() in tool_capabilities:
                return True
        
        return False
    
    def get_registry_status(self) -> Dict[str, Any]:
        """Get registry status and statistics."""
        return {
            "total_tools": len(self.tools),
            "total_capabilities": len(self.capabilities_index),
            "tools": {
                name: {
                    "capabilities": tool.get_capabilities(),
                    "available": tool.is_available(),
                    "execution_count": tool.execution_count,
                    "metrics": tool.metrics.dict()
                }
                for name, tool in self.tools.items()
            },
            "capabilities": self.capabilities_index,
            "version_history": self.version_history
        }

# ============================================================================
# Tool Execution Engine Implementation
# ============================================================================

class MCPToolExecutionEngine:
    """Main MCP tool execution engine with comprehensive features."""
    
    def __init__(self, registry: MCPToolRegistry, sandbox: ToolExecutionSandbox):
        self.registry = registry
        self.sandbox = sandbox
        self.execution_history: List[ToolExecutionResult] = []
        self.active_executions: Dict[str, asyncio.Task] = {}
        self.execution_queue = asyncio.Queue(maxsize=100)
        self.metrics = ToolExecutionMetrics()
        self.logger = logging.getLogger(f"{__name__}.engine")
        
        # Start execution worker
        self._worker_task = asyncio.create_task(self._execution_worker())
    
    async def select_tools(self, criteria: ToolSelectionCriteria) -> List[MCPTool]:
        """Select tools based on criteria."""
        try:
            tools = self.registry.discover_tools(criteria)
            self.logger.info(f"Selected {len(tools)} tools for execution")
            return tools
            
        except Exception as e:
            self.logger.error(f"Tool selection failed: {e}")
            return []
    
    async def execute_tool(self, tool_call: ToolCall, context: Optional[ToolExecutionContext] = None) -> ToolExecutionResult:
        """Execute a single tool with comprehensive error handling."""
        execution_id = str(uuid.uuid4())
        
        try:
            # Get tool implementation from registry
            tool = self.registry.get_tool_implementation(tool_call.tool_name)
            if not tool:
                return ToolExecutionResult(
                    execution_id=execution_id,
                    tool_name=tool_call.tool_name,
                    status=ToolExecutionStatus.FAILED,
                    input_data=tool_call.parameters,
                    error_message=f"Tool {tool_call.tool_name} not found in registry",
                    execution_time=0.0
                )
            
            # Create execution context
            if not context:
                context = ToolExecutionContext(
                    tool_name=tool_call.tool_name,
                    input_schema=self.registry.schemas[tool_call.tool_name],
                    output_schema=self.registry.schemas[tool_call.tool_name]
                )
            
            # Validate input
            if not tool.validate_input(tool_call.parameters):
                return ToolExecutionResult(
                    execution_id=execution_id,
                    tool_name=tool_call.tool_name,
                    status=ToolExecutionStatus.FAILED,
                    input_data=tool_call.parameters,
                    error_message="Input validation failed",
                    execution_time=0.0
                )
            
            # Execute tool in sandbox
            start_time = time.time()
            result = await self.sandbox.execute_tool(tool, tool_call.parameters, context)
            execution_time = time.time() - start_time
            
            # Update tool metrics
            tool.execution_count += 1
            tool.last_execution = datetime.now(timezone.utc)
            tool.metrics.total_executions += 1
            
            if result.status == ToolExecutionStatus.COMPLETED:
                tool.metrics.successful_executions += 1
            else:
                tool.metrics.failed_executions += 1
            
            tool.metrics.total_execution_time += execution_time
            tool.metrics.average_execution_time = (
                tool.metrics.total_execution_time / tool.metrics.total_executions
            )
            tool.metrics.error_rate = (
                tool.metrics.failed_executions / tool.metrics.total_executions
            )
            
            # Update engine metrics
            self._update_engine_metrics(result)
            
            # Add to execution history
            self.execution_history.append(result)
            
            # Limit history size
            if len(self.execution_history) > 1000:
                self.execution_history = self.execution_history[-500:]
            
            self.logger.info(f"Tool execution completed: {tool_call.tool_name} in {execution_time:.3f}s")
            return result
            
        except Exception as e:
            self.logger.error(f"Tool execution failed: {e}")
            return ToolExecutionResult(
                execution_id=execution_id,
                tool_name=tool_call.tool_name,
                status=ToolExecutionStatus.FAILED,
                input_data=tool_call.parameters,
                error_message=str(e),
                execution_time=time.time() - start_time if 'start_time' in locals() else 0.0
            )
    
    async def execute_tools_parallel(self, tool_calls: List[ToolCall], max_concurrent: int = 5) -> List[ToolExecutionResult]:
        """Execute multiple tools in parallel with concurrency control."""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def execute_with_semaphore(tool_call: ToolCall):
            async with semaphore:
                return await self.execute_tool(tool_call)
        
        tasks = [execute_with_semaphore(tool_call) for tool_call in tool_calls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(ToolExecutionResult(
                    execution_id=str(uuid.uuid4()),
                    tool_name=tool_calls[i].tool_name,
                    status=ToolExecutionStatus.FAILED,
                    input_data=tool_calls[i].parameters,
                    error_message=str(result),
                    execution_time=0.0
                ))
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def _execution_worker(self):
        """Background worker for processing execution queue."""
        while True:
            try:
                # Get next execution from queue
                execution_task = await self.execution_queue.get()
                
                if execution_task is None:  # Shutdown signal
                    break
                
                # Process execution
                await execution_task()
                
            except Exception as e:
                self.logger.error(f"Execution worker error: {e}")
                await asyncio.sleep(1)  # Brief pause before retrying
    
    def _update_engine_metrics(self, result: ToolExecutionResult):
        """Update engine-level metrics."""
        self.metrics.total_executions += 1
        
        if result.status == ToolExecutionStatus.COMPLETED:
            self.metrics.successful_executions += 1
        else:
            self.metrics.failed_executions += 1
        
        self.metrics.total_execution_time += result.execution_time
        self.metrics.average_execution_time = (
            self.metrics.total_execution_time / self.metrics.total_executions
        )
        
        if result.memory_usage:
            self.metrics.memory_usage_peak = max(self.metrics.memory_usage_peak, result.memory_usage)
        
        if result.cpu_usage:
            self.metrics.cpu_usage_peak = max(self.metrics.cpu_usage_peak, result.cpu_usage)
        
        self.metrics.error_rate = (
            self.metrics.failed_executions / self.metrics.total_executions
        )
        self.metrics.last_updated = datetime.now(timezone.utc)
    
    def get_execution_history(self, limit: int = 100) -> List[ToolExecutionResult]:
        """Get execution history with limit."""
        return self.execution_history[-limit:]
    
    def get_engine_status(self) -> Dict[str, Any]:
        """Get engine status and metrics."""
        return {
            "metrics": self.metrics.dict(),
            "active_executions": len(self.active_executions),
            "queue_size": self.execution_queue.qsize(),
            "registry_status": self.registry.get_registry_status(),
            "sandbox_status": self.sandbox.get_resource_usage()
        }
    
    async def shutdown(self):
        """Shutdown the execution engine."""
        # Signal worker to stop
        await self.execution_queue.put(None)
        
        # Wait for worker to finish
        if self._worker_task:
            await self._worker_task
        
        # Cleanup sandbox
        await self.sandbox.cleanup()
        
        self.logger.info("Tool execution engine shutdown completed")

# ============================================================================
# Tool Integration Service
# ============================================================================

class ToolIntegrationService:
    """Service for integrating tool results into answer generation."""
    
    def __init__(self, execution_engine: MCPToolExecutionEngine):
        self.execution_engine = execution_engine
        self.logger = logging.getLogger(f"{__name__}.integration")
    
    async def integrate_tool_results(self, 
                                   base_answer: str, 
                                   tool_results: List[ToolExecutionResult],
                                   context_analysis: ContextAnalysis) -> str:
        """Integrate tool results into base answer."""
        try:
            if not tool_results:
                return base_answer
            
            # Filter successful results
            successful_results = [
                result for result in tool_results 
                if result.status == ToolExecutionStatus.COMPLETED and result.output_data
            ]
            
            if not successful_results:
                return base_answer
            
            # Create integration prompt
            self._create_integration_prompt(
                base_answer, successful_results, context_analysis
            )
            
            # For now, return a simple integration
            # In the future, this will use Qwen3-Omni for intelligent integration
            integrated_answer = await self._simple_integration(
                base_answer, successful_results
            )
            
            self.logger.info(f"Integrated {len(successful_results)} tool results into answer")
            return integrated_answer
            
        except Exception as e:
            self.logger.error(f"Tool integration failed: {e}")
            return base_answer
    
    def _create_integration_prompt(self, 
                                 base_answer: str, 
                                 tool_results: List[ToolExecutionResult],
                                 context_analysis: ContextAnalysis) -> str:
        """Create prompt for intelligent tool result integration."""
        prompt = f"""
        Base Answer: {base_answer}
        
        Context Analysis:
        - Intent: {context_analysis.intent}
        - Entities: {', '.join(context_analysis.entities)}
        - Confidence: {context_analysis.confidence}
        
        Tool Results:
        """
        
        for i, result in enumerate(tool_results, 1):
            prompt += f"""
        {i}. Tool: {result.tool_name}
           Output: {json.dumps(result.output_data, indent=2)}
           Execution Time: {result.execution_time:.3f}s
        """
        
        prompt += """
        
        Please integrate the tool results into the base answer to provide a comprehensive response.
        """
        
        return prompt
    
    async def _simple_integration(self, 
                                base_answer: str, 
                                tool_results: List[ToolExecutionResult]) -> str:
        """Simple integration logic for tool results."""
        if not tool_results:
            return base_answer
        
        integration_parts = [base_answer]
        
        for result in tool_results:
            if result.output_data:
                # Add tool result to integration
                tool_info = f"\n\n**Tool Result from {result.tool_name}:**\n"
                tool_output = json.dumps(result.output_data, indent=2)
                integration_parts.append(tool_info + tool_output)
        
        return "\n".join(integration_parts)

# ============================================================================
# Factory Functions
# ============================================================================

def create_tool_execution_engine(registry: MCPToolRegistry, sandbox: ToolExecutionSandbox) -> MCPToolExecutionEngine:
    """Create a tool execution engine with registry and sandbox."""
    return MCPToolExecutionEngine(registry, sandbox)

def create_tool_registry() -> MCPToolRegistry:
    """Create a new tool registry."""
    return MCPToolRegistry()

def create_tool_integration_service(execution_engine: MCPToolExecutionEngine) -> ToolIntegrationService:
    """Create a tool integration service."""
    return ToolIntegrationService(execution_engine)

# ============================================================================
# Export all classes and functions
# ============================================================================

__all__ = [
    # Enums
    "ToolExecutionStatus",
    "ToolExecutionPriority",
    
    # Data Models
    "ToolExecutionResult",
    "ToolExecutionContext",
    "ToolSelectionCriteria",
    "ToolExecutionMetrics",
    
    # Interfaces
    "MCPTool",
    "ToolExecutionSandbox",
    
    # Implementations
    "MCPToolRegistry",
    "MCPToolExecutionEngine",
    "ToolIntegrationService",
    
    # Factory Functions
    "create_tool_execution_engine",
    "create_tool_registry",
    "create_tool_integration_service",
]
