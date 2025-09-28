"""
Pydantic AI MCP Integration for Agentic LLM Core v0.1

This module provides enhanced MCP integration using Pydantic AI for better
tool execution, validation, and knowledge base integration.

Created: 2024-09-24
Status: Enhanced
"""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Union, Type, Callable, Awaitable
from uuid import uuid4

import pydantic
from pydantic import BaseModel, Field, field_validator
from pydantic_ai import Agent, RunContext, Tool

from .mcp_adapter import MCPAdapter, MCPRequest, MCPResponse, MCPNotification
from ..models.contracts import ToolCall as ContractToolCall, ToolResult as ContractToolResult
from ..memory.vector_pg import VectorStore, Document
from ..engines.ollama_adapter import OllamaAdapter, ModelResponse


# ============================================================================
# Pydantic AI Enhanced Models
# ============================================================================

class PydanticAIToolSpec(BaseModel):
    """Enhanced tool specification for Pydantic AI integration."""
    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Tool parameters schema")
    returns: Dict[str, Any] = Field(default_factory=dict, description="Return value schema")
    safety_level: str = Field(default="safe", description="Tool safety level")
    requires_permissions: List[str] = Field(default_factory=list, description="Required permissions")
    knowledge_base_enabled: bool = Field(default=True, description="Enable knowledge base integration")
    context_aware: bool = Field(default=True, description="Enable context awareness")
    
    @field_validator('safety_level')
    @classmethod
    def validate_safety_level(cls, v):
        allowed_levels = ['safe', 'moderate', 'dangerous', 'critical']
        if v not in allowed_levels:
            raise ValueError(f"Safety level must be one of: {allowed_levels}")
        return v


class KnowledgeBaseContext(BaseModel):
    """Context for knowledge base integration."""
    query: str = Field(..., description="Knowledge base query")
    context_type: str = Field(default="general", description="Type of context")
    max_results: int = Field(default=5, description="Maximum results to return")
    similarity_threshold: float = Field(default=0.7, description="Similarity threshold")
    include_metadata: bool = Field(default=True, description="Include metadata in results")
    
    @field_validator('similarity_threshold')
    @classmethod
    def validate_threshold(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError("Similarity threshold must be between 0.0 and 1.0")
        return v


class EnhancedToolCall(BaseModel):
    """Enhanced tool call with knowledge base integration."""
    tool_call_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique tool call ID")
    tool_name: str = Field(..., description="Name of the tool to call")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Tool parameters")
    context: Optional[KnowledgeBaseContext] = Field(None, description="Knowledge base context")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Call timestamp")
    
    @field_validator('tool_name')
    @classmethod
    def validate_tool_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Tool name cannot be empty")
        return v.strip().lower()


class EnhancedToolResult(BaseModel):
    """Enhanced tool result with knowledge base integration."""
    tool_call_id: str = Field(..., description="Corresponding tool call ID")
    success: bool = Field(..., description="Whether the call was successful")
    result: Any = Field(..., description="Tool execution result")
    knowledge_base_results: Optional[List[Dict[str, Any]]] = Field(None, description="Knowledge base results")
    execution_time: float = Field(..., description="Execution time in seconds")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Result timestamp")


class OllamaGenerationRequest(BaseModel):
    """Request for Ollama model generation."""
    prompt: str = Field(..., description="Input prompt for generation")
    model_key: str = Field(default="primary", description="Ollama model key to use")
    max_tokens: int = Field(default=1024, description="Maximum tokens to generate")
    temperature: float = Field(default=0.7, description="Generation temperature")
    task_type: str = Field(default="text_generation", description="Type of task")
    
    @field_validator('temperature')
    @classmethod
    def validate_temperature(cls, v):
        if not 0.0 <= v <= 2.0:
            raise ValueError("Temperature must be between 0.0 and 2.0")
        return v


class OllamaGenerationResult(BaseModel):
    """Result from Ollama model generation."""
    content: str = Field(..., description="Generated content")
    model_used: str = Field(..., description="Model that generated the content")
    processing_time: float = Field(..., description="Processing time in seconds")
    tokens_generated: int = Field(..., description="Number of tokens generated")
    confidence: float = Field(default=0.8, description="Confidence in the result")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Generation timestamp")


# ============================================================================
# Pydantic AI MCP Agent
# ============================================================================

class PydanticAIMCPAgent:
    """Enhanced MCP agent using Pydantic AI for better tool execution."""
    
    def __init__(
        self,
        mcp_adapter: MCPAdapter,
        vector_store: Optional[VectorStore] = None,
        agent_name: str = "pydantic_ai_mcp_agent",
        ollama_config_path: Optional[str] = None
    ):
        self.mcp_adapter = mcp_adapter
        self.vector_store = vector_store
        self.agent_name = agent_name
        self.logger = logging.getLogger(__name__)
        
        # Initialize Ollama adapter if config provided
        self.ollama_adapter = None
        if ollama_config_path:
            self.ollama_adapter = OllamaAdapter(ollama_config_path)
        
        # Initialize Pydantic AI agent
        self.agent = Agent(
            'openai:gpt-3.5-turbo',  # Use a valid model format
            result_type=str,
            tools=self._get_available_tools()
        )
        
        # Tool registry
        self.tool_registry: Dict[str, PydanticAIToolSpec] = {}
        self._register_default_tools()
        
        # Performance tracking
        self.stats = {
            "total_requests": 0,
            "mcp_tool_calls": 0,
            "ollama_generations": 0,
            "total_time": 0.0
        }
    
    def _get_available_tools(self) -> List[Callable]:
        """Get available tools for Pydantic AI agent."""
        tools = [
            self._execute_tool_call,
            self._query_knowledge_base,
            self._validate_tool_parameters,
            self._get_tool_specifications
        ]
        
        # Add Ollama tools if adapter is available
        if self.ollama_adapter:
            tools.extend([
                self._ollama_generate_text,
                self._ollama_generate_code,
                self._ollama_analyze_text,
                self._ollama_quick_response
            ])
        
        return tools
    
    def _register_default_tools(self):
        """Register default tools from the tool catalog."""
        default_tools = [
            PydanticAIToolSpec(
                name="file_read",
                description="Read contents of a file",
                parameters={
                    "file_path": {"type": "string", "required": True},
                    "encoding": {"type": "string", "default": "utf-8"}
                },
                returns={"content": "string", "size": "integer"},
                safety_level="safe",
                requires_permissions=["read"]
            ),
            PydanticAIToolSpec(
                name="file_write",
                description="Write content to a file",
                parameters={
                    "file_path": {"type": "string", "required": True},
                    "content": {"type": "string", "required": True},
                    "encoding": {"type": "string", "default": "utf-8"}
                },
                returns={"success": "boolean", "bytes_written": "integer"},
                safety_level="moderate",
                requires_permissions=["write"]
            ),
            PydanticAIToolSpec(
                name="text_summarize",
                description="Generate a summary of text",
                parameters={
                    "text": {"type": "string", "required": True},
                    "max_length": {"type": "integer", "default": 200},
                    "style": {"type": "string", "default": "extractive"}
                },
                returns={"summary": "string", "compression_ratio": "float"},
                safety_level="safe",
                requires_permissions=[]
            ),
            PydanticAIToolSpec(
                name="data_analyze",
                description="Analyze structured data",
                parameters={
                    "data": {"type": "array", "required": True},
                    "analysis_type": {"type": "string", "required": True},
                    "columns": {"type": "array", "required": False}
                },
                returns={"results": "object", "insights": "array"},
                safety_level="safe",
                requires_permissions=[]
            )
        ]
        
        for tool in default_tools:
            self.tool_registry[tool.name] = tool
    
    async def _execute_tool_call(
        self,
        tool_call: EnhancedToolCall,
        context: RunContext[str]
    ) -> EnhancedToolResult:
        """Execute a tool call with enhanced capabilities."""
        start_time = datetime.utcnow()
        
        try:
            # Validate tool exists
            if tool_call.tool_name not in self.tool_registry:
                raise ValueError(f"Unknown tool: {tool_call.tool_name}")
            
            tool_spec = self.tool_registry[tool_call.tool_name]
            
            # Query knowledge base if enabled
            knowledge_base_results = None
            if tool_call.context and tool_spec.knowledge_base_enabled:
                knowledge_base_results = await self._query_knowledge_base_internal(
                    tool_call.context
                )
            
            # Execute tool via MCP
            mcp_request = MCPRequest(
                method="tools/call",
                params={
                    "name": tool_call.tool_name,
                    "arguments": tool_call.parameters
                }
            )
            
            mcp_response = await self.mcp_adapter.send_request(mcp_request)
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            return EnhancedToolResult(
                tool_call_id=tool_call.tool_call_id,
                success=mcp_response.error is None,
                result=mcp_response.result if mcp_response.error is None else None,
                knowledge_base_results=knowledge_base_results,
                execution_time=execution_time,
                error_message=mcp_response.error.get("message") if mcp_response.error else None,
                metadata={
                    "tool_spec": tool_spec.model_dump(),
                    "mcp_response_id": mcp_response.id
                }
            )
            
        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            self.logger.error(f"Tool execution failed: {e}")
            
            return EnhancedToolResult(
                tool_call_id=tool_call.tool_call_id,
                success=False,
                result=None,
                knowledge_base_results=None,
                execution_time=execution_time,
                error_message=str(e),
                metadata={"error_type": type(e).__name__}
            )
    
    async def _query_knowledge_base(
        self,
        query: str,
        context_type: str = "general",
        max_results: int = 5,
        context: RunContext[str] = None
    ) -> List[Dict[str, Any]]:
        """Query the knowledge base for relevant information."""
        if not self.vector_store:
            return []
        
        try:
            # Search for relevant documents
            results = await self.vector_store.search(
                query=query,
                limit=max_results,
                similarity_threshold=0.7
            )
            
            return [
                {
                    "content": result.document.content,
                    "metadata": result.document.metadata,
                    "similarity": result.similarity,
                    "source": result.document.source
                }
                for result in results
            ]
            
        except Exception as e:
            self.logger.error(f"Knowledge base query failed: {e}")
            return []
    
    async def _query_knowledge_base_internal(
        self,
        kb_context: KnowledgeBaseContext
    ) -> List[Dict[str, Any]]:
        """Internal knowledge base query method."""
        return await self._query_knowledge_base(
            query=kb_context.query,
            context_type=kb_context.context_type,
            max_results=kb_context.max_results
        )
    
    async def _validate_tool_parameters(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        context: RunContext[str] = None
    ) -> Dict[str, Any]:
        """Validate tool parameters against the tool specification."""
        if tool_name not in self.tool_registry:
            return {"valid": False, "error": f"Unknown tool: {tool_name}"}
        
        tool_spec = self.tool_registry[tool_name]
        
        try:
            # Validate required parameters
            for param_name, param_spec in tool_spec.parameters.items():
                if param_spec.get("required", False) and param_name not in parameters:
                    return {
                        "valid": False,
                        "error": f"Missing required parameter: {param_name}"
                    }
            
            # Validate parameter types
            for param_name, param_value in parameters.items():
                if param_name in tool_spec.parameters:
                    expected_type = tool_spec.parameters[param_name].get("type")
                    if expected_type and not self._validate_type(param_value, expected_type):
                        return {
                            "valid": False,
                            "error": f"Invalid type for parameter {param_name}: expected {expected_type}"
                        }
            
            return {"valid": True, "validated_parameters": parameters}
            
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def _validate_type(self, value: Any, expected_type: str) -> bool:
        """Validate a value against an expected type."""
        type_mapping = {
            "string": str,
            "integer": int,
            "float": float,
            "boolean": bool,
            "array": list,
            "object": dict
        }
        
        if expected_type not in type_mapping:
            return True  # Unknown type, assume valid
        
        return isinstance(value, type_mapping[expected_type])
    
    async def _get_tool_specifications(
        self,
        tool_name: Optional[str] = None,
        context: RunContext[str] = None
    ) -> Dict[str, Any]:
        """Get tool specifications."""
        if tool_name:
            if tool_name in self.tool_registry:
                return {tool_name: self.tool_registry[tool_name].model_dump()}
            else:
                return {"error": f"Tool not found: {tool_name}"}
        else:
            return {
                name: spec.model_dump()
                for name, spec in self.tool_registry.items()
            }
    
    async def execute_with_knowledge_base(
        self,
        tool_call: EnhancedToolCall,
        user_context: Optional[str] = None
    ) -> EnhancedToolResult:
        """Execute a tool call with knowledge base integration."""
        # Add user context to knowledge base query if provided
        if user_context and tool_call.context:
            tool_call.context.query = f"{tool_call.context.query} Context: {user_context}"
        
        # Execute the tool call
        result = await self._execute_tool_call(tool_call, None)
        
        # Log the execution
        self.logger.info(
            f"Tool {tool_call.tool_name} executed in {result.execution_time:.3f}s "
            f"with {len(result.knowledge_base_results or [])} knowledge base results"
        )
        
        return result
    
    async def batch_execute_tools(
        self,
        tool_calls: List[EnhancedToolCall],
        parallel: bool = True
    ) -> List[EnhancedToolResult]:
        """Execute multiple tool calls in batch."""
        if parallel:
            # Execute tools in parallel
            tasks = [self._execute_tool_call(call, None) for call in tool_calls]
            return await asyncio.gather(*tasks)
        else:
            # Execute tools sequentially
            results = []
            for call in tool_calls:
                result = await self._execute_tool_call(call, None)
                results.append(result)
            return results
    
    def register_tool(self, tool_spec: PydanticAIToolSpec):
        """Register a new tool specification."""
        self.tool_registry[tool_spec.name] = tool_spec
        self.logger.info(f"Registered tool: {tool_spec.name}")
    
    def get_tool_catalog(self) -> Dict[str, PydanticAIToolSpec]:
        """Get the complete tool catalog."""
        return self.tool_registry.copy()
    
    # ============================================================================
    # Ollama Integration Methods
    # ============================================================================
    
    async def _ollama_generate_text(
        self,
        prompt: str,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        context: RunContext[str] = None
    ) -> Dict[str, Any]:
        """Generate text using Ollama models."""
        if not self.ollama_adapter:
            return {"error": "Ollama adapter not initialized"}
        
        try:
            response = await self.ollama_adapter.generate_response(
                model_key="primary",
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            self.stats["ollama_generations"] += 1
            
            return {
                "success": True,
                "content": response.content,
                "model_used": response.model,
                "processing_time": response.processing_time,
                "tokens_generated": response.tokens_generated,
                "metadata": {"ollama_generation": True, "tool_type": "text_generation"}
            }
            
        except Exception as e:
            self.logger.error(f"Ollama text generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "processing_time": 0.0
            }
    
    async def _ollama_generate_code(
        self,
        prompt: str,
        language: str = "python",
        context: RunContext[str] = None
    ) -> Dict[str, Any]:
        """Generate code using Ollama Phi3 model."""
        if not self.ollama_adapter:
            return {"error": "Ollama adapter not initialized"}
        
        try:
            code_prompt = f"Write {language} code for: {prompt}"
            
            response = await self.ollama_adapter.generate_response(
                model_key="coding",
                prompt=code_prompt,
                max_tokens=1024,
                temperature=0.3
            )
            
            self.stats["ollama_generations"] += 1
            
            return {
                "success": True,
                "code": response.content,
                "model_used": response.model,
                "processing_time": response.processing_time,
                "language": language,
                "metadata": {"ollama_generation": True, "tool_type": "code_generation"}
            }
            
        except Exception as e:
            self.logger.error(f"Ollama code generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "processing_time": 0.0
            }
    
    async def _ollama_analyze_text(
        self,
        text: str,
        analysis_type: str = "general",
        context: RunContext[str] = None
    ) -> Dict[str, Any]:
        """Analyze text using Ollama Qwen2.5 model."""
        if not self.ollama_adapter:
            return {"error": "Ollama adapter not initialized"}
        
        try:
            analysis_prompt = f"""
            Analyze the following text ({analysis_type} analysis):
            
            {text}
            
            Provide key insights and findings.
            """
            
            response = await self.ollama_adapter.generate_response(
                model_key="primary",
                prompt=analysis_prompt,
                max_tokens=512,
                temperature=0.5
            )
            
            self.stats["ollama_generations"] += 1
            
            return {
                "success": True,
                "analysis": response.content,
                "model_used": response.model,
                "processing_time": response.processing_time,
                "analysis_type": analysis_type,
                "metadata": {"ollama_generation": True, "tool_type": "text_analysis"}
            }
            
        except Exception as e:
            self.logger.error(f"Ollama text analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "processing_time": 0.0
            }
    
    async def _ollama_quick_response(
        self,
        prompt: str,
        context: RunContext[str] = None
    ) -> Dict[str, Any]:
        """Generate quick response using Ollama Llama3.2 model."""
        if not self.ollama_adapter:
            return {"error": "Ollama adapter not initialized"}
        
        try:
            response = await self.ollama_adapter.generate_response(
                model_key="lightweight",
                prompt=prompt,
                max_tokens=200,
                temperature=0.3
            )
            
            self.stats["ollama_generations"] += 1
            
            return {
                "success": True,
                "response": response.content,
                "model_used": response.model,
                "processing_time": response.processing_time,
                "metadata": {"ollama_generation": True, "tool_type": "quick_response"}
            }
            
        except Exception as e:
            self.logger.error(f"Ollama quick response failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "processing_time": 0.0
            }
    
    async def initialize_ollama(self) -> bool:
        """Initialize Ollama adapter."""
        if not self.ollama_adapter:
            return False
        
        try:
            if await self.ollama_adapter.check_ollama_status():
                self.logger.info("Ollama adapter initialized successfully")
                return True
            else:
                self.logger.error("Ollama is not running")
                return False
        except Exception as e:
            self.logger.error(f"Failed to initialize Ollama: {e}")
            return False
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        stats = self.stats.copy()
        if stats["total_requests"] > 0:
            stats["average_time"] = stats["total_time"] / stats["total_requests"]
        else:
            stats["average_time"] = 0.0
        return stats


# ============================================================================
# Factory Functions
# ============================================================================

async def create_pydantic_ai_mcp_agent(
    mcp_adapter: MCPAdapter,
    vector_store: Optional[VectorStore] = None,
    agent_name: str = "pydantic_ai_mcp_agent",
    ollama_config_path: Optional[str] = None
) -> PydanticAIMCPAgent:
    """Create a new Pydantic AI MCP agent with optional Ollama integration."""
    agent = PydanticAIMCPAgent(mcp_adapter, vector_store, agent_name, ollama_config_path)
    
    # Initialize Ollama if configured
    if ollama_config_path:
        await agent.initialize_ollama()
    
    return agent


def create_enhanced_tool_call(
    tool_name: str,
    parameters: Dict[str, Any],
    knowledge_base_query: Optional[str] = None,
    context_type: str = "general"
) -> EnhancedToolCall:
    """Create an enhanced tool call with knowledge base integration."""
    context = None
    if knowledge_base_query:
        context = KnowledgeBaseContext(
            query=knowledge_base_query,
            context_type=context_type
        )
    
    return EnhancedToolCall(
        tool_name=tool_name,
        parameters=parameters,
        context=context
    )


# ============================================================================
# Example Usage
# ============================================================================

async def example_usage():
    """Example usage of the Pydantic AI MCP integration."""
    # This would be used in actual implementation
    pass
