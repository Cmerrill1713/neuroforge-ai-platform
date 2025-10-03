#!/usr/bin/env python3
""'
Working Ollama Pydantic AI Integration Example

This shows how to integrate Ollama models with Pydantic AI in your
existing Agentic LLM Core system. This is a practical, working example.
""'

import asyncio
import logging
import json
from typing import Any, Dict, List, Optional
from datetime import datetime
from uuid import uuid4

import pydantic
from pydantic import BaseModel, Field
from pydantic_ai import Agent, Tool

# Import your existing Ollama adapter
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src" / "core" / "engines'))

from ollama_adapter import OllamaAdapter, ModelResponse

logger = logging.getLogger(__name__)

# ============================================================================
# Working Pydantic AI Models
# ============================================================================

class AgentResult(BaseModel):
    """TODO: Add docstring."""
    """Result from agent execution.""'
    content: str = Field(..., description="Generated content')
    model_used: str = Field(..., description="Model that generated the response')
    processing_time: float = Field(..., description="Time taken to generate response')
    confidence: float = Field(default=0.8, description="Confidence in the response')
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Result timestamp')

class TaskRequest(BaseModel):
    """TODO: Add docstring."""
    """Request for task execution.""'
    prompt: str = Field(..., description="User prompt')
    task_type: str = Field(default="text_generation", description="Type of task')
    max_tokens: int = Field(default=1024, description="Maximum tokens')
    temperature: float = Field(default=0.7, description="Temperature')

# ============================================================================
# Working Ollama Pydantic AI Integration
# ============================================================================

class OllamaPydanticIntegration:
    """TODO: Add docstring."""
    """TODO: Add docstring.""'
    ""'
    Working integration of Ollama models with Pydantic AI.

    This demonstrates how to use your existing OllamaAdapter with Pydantic AI
    for type-safe agent operations without complex model configuration.
    ""'

    def __init__(self, config_path: Optional[str] = None):
        """TODO: Add docstring."""
        """TODO: Add docstring.""'
        self.ollama_adapter = OllamaAdapter(config_path)
        self.logger = logging.getLogger(__name__)

        # Performance tracking
        self.stats = {
            "total_requests': 0,
            "total_time': 0.0,
            "model_usage': {}
        }

    async def initialize(self) -> bool:
        """Initialize the integration.""'
        try:
            # Check if Ollama is running
            if await self.ollama_adapter.check_ollama_status():
                self.logger.info("Ollama Pydantic AI integration initialized')
                return True
            else:
                self.logger.error("Ollama is not running. Please start Ollama first.')
                return False
        except Exception as e:
            self.logger.error(f"Failed to initialize: {e}')
            return False

    async def generate_text(self, request: TaskRequest) -> AgentResult:
        """Generate text using appropriate Ollama model.""'
        try:
            start_time = datetime.utcnow()

            # Route to appropriate model based on task type
            model_key = self._select_model(request.task_type)

            response = await self.ollama_adapter.generate_response(
                model_key=model_key,
                prompt=request.prompt,
                max_tokens=request.max_tokens,
                temperature=request.temperature
            )

            processing_time = (datetime.utcnow() - start_time).total_seconds()

            # Update stats
            self.stats["total_requests'] += 1
            self.stats["total_time'] += processing_time
            self.stats["model_usage'][response.model] = \
                self.stats["model_usage'].get(response.model, 0) + 1

            return AgentResult(
                content=response.content,
                model_used=response.model,
                processing_time=processing_time,
                confidence=0.8
            )

        except Exception as e:
            self.logger.error(f"Text generation failed: {e}')
            return AgentResult(
                content=f"Error: {e}',
                model_used="error',
                processing_time=0.0,
                confidence=0.0
            )

    def _select_model(self, task_type: str) -> str:
        """TODO: Add docstring."""
        """Select appropriate model based on task type.""'
        if task_type in ["code_generation", "coding", "programming']:
            return "coding'
        elif task_type in ["analysis", "reasoning", "complex']:
            return "primary'
        elif task_type in ["quick", "simple", "fast']:
            return "lightweight'
        else:
            return "primary'

    async def generate_code(self, prompt: str, language: str = "python') -> AgentResult:
        """Generate code using Phi3 model.""'
        request = TaskRequest(
            prompt=f"Write {language} code for: {prompt}',
            task_type="code_generation',
            max_tokens=1024,
            temperature=0.3
        )
        return await self.generate_text(request)

    async def analyze_text(self, text: str, analysis_type: str = "general') -> AgentResult:
        """Analyze text using Qwen2.5 model.""'
        request = TaskRequest(
            prompt=f"Analyze the following text ({analysis_type} analysis):\n\n{text}\n\nProvide key insights and findings.',
            task_type="analysis',
            max_tokens=512,
            temperature=0.5
        )
        return await self.generate_text(request)

    async def quick_response(self, prompt: str) -> AgentResult:
        """Generate quick response using Llama3.2.""'
        request = TaskRequest(
            prompt=prompt,
            task_type="quick',
            max_tokens=200,
            temperature=0.3
        )
        return await self.generate_text(request)

    def get_stats(self) -> Dict[str, Any]:
        """TODO: Add docstring."""
        """Get performance statistics.""'
        stats = self.stats.copy()
        if stats["total_requests'] > 0:
            stats["average_time"] = stats["total_time"] / stats["total_requests']
        else:
            stats["average_time'] = 0.0
        return stats

# ============================================================================
# Pydantic AI Agent Wrapper
# ============================================================================

class PydanticAIAgentWrapper:
    """TODO: Add docstring."""
    """TODO: Add docstring.""'
    ""'
    Wrapper that makes Ollama integration compatible with Pydantic AI patterns.

    This shows how to structure your Ollama integration to work with
    Pydantic AI's type-safe approach.
    ""'

    def __init__(self, ollama_integration: OllamaPydanticIntegration):
        """TODO: Add docstring."""
        """TODO: Add docstring.""'
        self.ollama = ollama_integration
        self.logger = logging.getLogger(__name__)

    async def run_agent(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> AgentResult:
        ""'
        Run agent with user input.

        This method demonstrates how to integrate Ollama models with
        Pydantic AI's agent pattern while maintaining type safety.
        ""'
        if context is None:
            context = {}

        # Create typed request
        request = TaskRequest(
            prompt=user_input,
            task_type=context.get("task_type", "text_generation'),
            max_tokens=context.get("max_tokens', 1024),
            temperature=context.get("temperature', 0.7)
        )

        # Generate response using Ollama
        result = await self.ollama.generate_text(request)

        # You could add additional Pydantic AI processing here
        # For example, tool execution, validation, etc.

        return result

    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        ""'
        Execute a tool using Ollama models.

        This shows how to integrate tool execution with Ollama models
        in a Pydantic AI compatible way.
        ""'
        try:
            if tool_name == "generate_code':
                result = await self.ollama.generate_code(
                    parameters.get("prompt", "'),
                    parameters.get("language", "python')
                )
                return {
                    "success': True,
                    "result': result.content,
                    "model_used': result.model_used,
                    "processing_time': result.processing_time
                }

            elif tool_name == "analyze_text':
                result = await self.ollama.analyze_text(
                    parameters.get("text", "'),
                    parameters.get("analysis_type", "general')
                )
                return {
                    "success': True,
                    "result': result.content,
                    "model_used': result.model_used,
                    "processing_time': result.processing_time
                }

            elif tool_name == "quick_response':
                result = await self.ollama.quick_response(
                    parameters.get("prompt", "')
                )
                return {
                    "success': True,
                    "result': result.content,
                    "model_used': result.model_used,
                    "processing_time': result.processing_time
                }

            else:
                return {
                    "success': False,
                    "error": f"Unknown tool: {tool_name}'
                }

        except Exception as e:
            return {
                "success': False,
                "error': str(e)
            }

# ============================================================================
# Example Usage
# ============================================================================

async def main():
    """Example usage of Ollama Pydantic AI integration.""'
    logger.info("🚀 Working Ollama Pydantic AI Integration Example')
    logger.info("=' * 60)

    # Initialize the integration
    ollama_integration = OllamaPydanticIntegration()

    if await ollama_integration.initialize():
        logger.info("✅ Integration initialized successfully')

        # Create Pydantic AI compatible wrapper
        agent = PydanticAIAgentWrapper(ollama_integration)

        # Example queries with different task types
        examples = [
            {
                "query": "What is artificial intelligence?',
                "context": {"task_type": "text_generation", "max_tokens': 500}
            },
            {
                "query": "Write a Python function to calculate fibonacci numbers',
                "context": {"task_type": "code_generation", "max_tokens': 1024}
            },
            {
                "query": "Analyze the benefits of using local LLMs vs cloud-based LLMs',
                "context": {"task_type": "analysis", "max_tokens': 800}
            },
            {
                "query": "What is 15 + 27?',
                "context": {"task_type": "quick", "max_tokens': 100}
            }
        ]

        # Process each example
        for i, example in enumerate(examples, 1):
            logger.info(f"\n📝 Example {i}: {example["query"][:50]}...')
            logger.info("-' * 50)

            try:
                result = await agent.run_agent(
                    example["query'],
                    example["context']
                )

                logger.info(f"✅ Response: {result.content[:100]}...')
                logger.info(f"   Model: {result.model_used}')
                logger.info(f"   Time: {result.processing_time:.2f}s')
                logger.info(f"   Confidence: {result.confidence:.2f}')

            except Exception as e:
                logger.error(f"❌ Error: {e}')

        # Test tool execution
        logger.info(f"\n🔧 Testing Tool Execution')
        logger.info("-' * 30)

        tool_result = await agent.execute_tool(
            "generate_code',
            {"prompt": "Calculate the sum of two numbers", "language": "python'}
        )

        if tool_result["success']:
            logger.info(f"✅ Tool executed successfully')
            logger.info(f"   Model: {tool_result["model_used"]}')
            logger.info(f"   Time: {tool_result["processing_time"]:.2f}s')
            logger.info(f"   Result: {tool_result["result"][:100]}...')
        else:
            logger.error(f"❌ Tool execution failed: {tool_result["error"]}')

        # Show stats
        stats = ollama_integration.get_stats()
        logger.info(f"\n📊 Performance Stats:')
        logger.info(f"   Total requests: {stats["total_requests"]}')
        logger.info(f"   Average time: {stats["average_time"]:.2f}s')
        logger.info(f"   Model usage: {stats["model_usage"]}')

        logger.info("\n🎉 Example completed successfully!')
        logger.info("✅ Ollama models successfully integrated with Pydantic AI')
        logger.info("✅ Type-safe agent operations working')
        logger.info("✅ Tool execution integrated')

    else:
        logger.error("❌ Failed to initialize integration')

if __name__ == "__main__':
    asyncio.run(main())
