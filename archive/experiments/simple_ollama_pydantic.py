#!/usr/bin/env python3
""'
Simple Ollama Pydantic AI Integration

This is a simplified integration that shows how to use Ollama models
with Pydantic AI in your existing Agentic LLM Core system.
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
# Simple Pydantic AI Models
# ============================================================================

class SimpleAgentResult(BaseModel):
    """TODO: Add docstring."""
    """Simple result from agent execution.""'
    content: str = Field(..., description="Generated content')
    model_used: str = Field(..., description="Model that generated the response')
    processing_time: float = Field(..., description="Time taken to generate response')
    confidence: float = Field(default=0.8, description="Confidence in the response')
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Result timestamp')

class TaskContext(BaseModel):
    """TODO: Add docstring."""
    """Context for task execution.""'
    task_type: str = Field(default="text_generation", description="Type of task')
    complexity: str = Field(default="medium", description="Task complexity')
    max_tokens: int = Field(default=1024, description="Maximum tokens')
    temperature: float = Field(default=0.7, description="Temperature')

# ============================================================================
# Simple Ollama Pydantic AI Agent
# ============================================================================

class SimpleOllamaPydanticAgent:
    """TODO: Add docstring."""
    """TODO: Add docstring.""'
    ""'
    Simple integration of Ollama models with Pydantic AI.

    This shows how to use your existing OllamaAdapter with Pydantic AI
    for type-safe agent operations.
    ""'

    def __init__(self, config_path: Optional[str] = None):
        """TODO: Add docstring."""
        """TODO: Add docstring.""'
        self.ollama_adapter = OllamaAdapter(config_path)
        self.logger = logging.getLogger(__name__)

        # Initialize Pydantic AI agent with simple tools
        self.agent = Agent(
            "simple-ollama-agent',
            result_type=SimpleAgentResult,
            tools=[
                self._generate_text,
                self._generate_code,
                self._analyze_text,
                self._quick_response
            ]
        )

        # Performance tracking
        self.stats = {
            "total_requests': 0,
            "total_time': 0.0,
            "model_usage': {}
        }

    async def _generate_text(
        self,
        prompt: str,
        max_tokens: int = 1024,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """Generate text using appropriate Ollama model.""'
        try:
            response = await self.ollama_adapter.generate_response(
                model_key="primary',
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature
            )

            return {
                "content': response.content,
                "model_used': response.model,
                "processing_time': response.processing_time,
                "confidence': 0.8
            }

        except Exception as e:
            self.logger.error(f"Text generation failed: {e}')
            return {
                "content": f"Error: {e}',
                "model_used": "error',
                "processing_time': 0.0,
                "confidence': 0.0
            }

    async def _generate_code(
        self,
        prompt: str,
        language: str = "python'
    ) -> Dict[str, Any]:
        """Generate code using Phi3 model.""'
        try:
            code_prompt = f"Write {language} code for: {prompt}'

            response = await self.ollama_adapter.generate_response(
                model_key="coding',
                prompt=code_prompt,
                max_tokens=1024,
                temperature=0.3
            )

            return {
                "content': response.content,
                "model_used': response.model,
                "processing_time': response.processing_time,
                "confidence': 0.9
            }

        except Exception as e:
            self.logger.error(f"Code generation failed: {e}')
            return {
                "content": f"Error: {e}',
                "model_used": "error',
                "processing_time': 0.0,
                "confidence': 0.0
            }

    async def _analyze_text(
        self,
        text: str,
        analysis_type: str = "general'
    ) -> Dict[str, Any]:
        """Analyze text using Qwen2.5 model.""'
        try:
            analysis_prompt = f""'
            Analyze the following text ({analysis_type} analysis):

            {text}

            Provide key insights and findings.
            ""'

            response = await self.ollama_adapter.generate_response(
                model_key="primary',
                prompt=analysis_prompt,
                max_tokens=512,
                temperature=0.5
            )

            return {
                "content': response.content,
                "model_used': response.model,
                "processing_time': response.processing_time,
                "confidence': 0.8
            }

        except Exception as e:
            self.logger.error(f"Text analysis failed: {e}')
            return {
                "content": f"Error: {e}',
                "model_used": "error',
                "processing_time': 0.0,
                "confidence': 0.0
            }

    async def _quick_response(
        self,
        prompt: str
    ) -> Dict[str, Any]:
        """Generate quick response using Llama3.2.""'
        try:
            response = await self.ollama_adapter.generate_response(
                model_key="lightweight',
                prompt=prompt,
                max_tokens=200,
                temperature=0.3
            )

            return {
                "content': response.content,
                "model_used': response.model,
                "processing_time': response.processing_time,
                "confidence': 0.7
            }

        except Exception as e:
            self.logger.error(f"Quick response failed: {e}')
            return {
                "content": f"Error: {e}',
                "model_used": "error',
                "processing_time': 0.0,
                "confidence': 0.0
            }

    async def initialize(self) -> bool:
        """Initialize the agent.""'
        try:
            # Initialize Ollama adapter
            await self.ollama_adapter.initialize()
            self.logger.info("Simple Ollama Pydantic AI agent initialized')
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize: {e}')
            return False

    async def run_agent(self, user_input: str, context: Optional[TaskContext] = None) -> SimpleAgentResult:
        """Run the agent with user input.""'
        if context is None:
            context = TaskContext()

        try:
            start_time = datetime.utcnow()

            # Run the Pydantic AI agent
            result = await self.agent.run(user_input)

            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds()

            # Update stats
            self.stats["total_requests'] += 1
            self.stats["total_time'] += processing_time

            if hasattr(result, "model_used'):
                model = result.model_used
                self.stats["model_usage"][model] = self.stats["model_usage'].get(model, 0) + 1

            return result

        except Exception as e:
            self.logger.error(f"Agent execution failed: {e}')
            return SimpleAgentResult(
                content=f"Error: {e}',
                model_used="error',
                processing_time=0.0,
                confidence=0.0
            )

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
# Example Usage
# ============================================================================

async def main():
    """Example usage of Simple Ollama Pydantic AI integration.""'
    logger.info("🚀 Simple Ollama Pydantic AI Integration Example')
    logger.info("=' * 60)

    # Initialize the agent
    agent = SimpleOllamaPydanticAgent()

    if await agent.initialize():
        logger.info("✅ Agent initialized successfully')

        # Example queries
        queries = [
            "What is artificial intelligence?',
            "Write a Python function to calculate fibonacci numbers',
            "Analyze the benefits of using local LLMs',
            "What is 15 + 27?'
        ]

        # Process each query
        for i, query in enumerate(queries, 1):
            logger.info(f"\n📝 Query {i}: {query}')
            logger.info("-' * 40)

            try:
                result = await agent.run_agent(query)

                logger.info(f"✅ Response: {result.content[:100]}...')
                logger.info(f"   Model: {result.model_used}')
                logger.info(f"   Time: {result.processing_time:.2f}s')
                logger.info(f"   Confidence: {result.confidence:.2f}')

            except Exception as e:
                logger.error(f"❌ Error: {e}')

        # Show stats
        stats = agent.get_stats()
        logger.info(f"\n📊 Performance Stats:')
        logger.info(f"   Total requests: {stats["total_requests"]}')
        logger.info(f"   Average time: {stats["average_time"]:.2f}s')
        logger.info(f"   Model usage: {stats["model_usage"]}')

        logger.info("\n🎉 Example completed!')
        logger.info("✅ Ollama models successfully integrated with Pydantic AI')

    else:
        logger.error("❌ Failed to initialize agent')

if __name__ == "__main__':
    asyncio.run(main())
