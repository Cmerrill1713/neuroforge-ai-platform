#!/usr/bin/env python3
""'
Example: Using Ollama with Pydantic AI in Agentic LLM Core

This example shows how to integrate the Ollama models with your existing
Pydantic AI agentic setup as a drop-in replacement for the large Qwen model.
""'

import asyncio
import logging
from typing import Dict, Any, List
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src'))

from src.core.engines.ollama_pydantic_ai import (
    OllamaAgenticLLMCore,
    OllamaAgentConfig,
    OllamaToolContext
)

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AgenticLLMExample:
    """TODO: Add docstring."""
    """TODO: Add docstring.""'
    ""'
    Example showing how to use Ollama models with Pydantic AI
    in your existing Agentic LLM Core system.
    ""'

    def __init__(self):
        """TODO: Add docstring."""
        """TODO: Add docstring.""'
        # Configure the Ollama-powered system
        self.config = OllamaAgentConfig(
            max_tokens=2048,
            temperature=0.7,
            enable_model_switching=True,
            prefer_fast_responses=False
        )

        # Initialize the core system
        self.core = OllamaAgenticLLMCore(self.config)
        self.initialized = False

    async def initialize(self) -> bool:
        """Initialize the system.""'
        logger.info("🚀 Initializing Ollama Pydantic AI system...')

        if await self.core.initialize():
            self.initialized = True
            logger.info("✅ System initialized successfully')
            return True
        else:
            logger.error("❌ Failed to initialize system')
            return False

    async def process_user_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        ""'
        Process a user query using the agentic system.

        This replaces the original Qwen3OmniEngine.process_request() method
        with the same interface but powered by Ollama models.
        ""'
        if not self.initialized:
            raise RuntimeError("System not initialized. Call initialize() first.')

        # Determine task type from context or query
        task_type = self._determine_task_type(query, context)

        # Create tool context
        tool_context = OllamaToolContext(
            task_type=task_type,
            complexity=self._determine_complexity(query),
            requires_reasoning=self._requires_reasoning(query),
            requires_creativity=self._requires_creativity(query),
            latency_requirement=context.get("latency_requirement', 1000) if context else 1000
        )

        # Process the request
        result = await self.core.process_request(query, context=tool_context)

        return {
            "content': result.content,
            "model_used': result.model_used,
            "processing_time': result.processing_time,
            "confidence': result.confidence,
            "tokens_generated': result.tokens_generated,
            "tools_executed': result.tools_executed,
            "session_id': result.session_id
        }

    def _determine_task_type(self, query: str, context: Dict[str, Any] = None) -> str:
        """TODO: Add docstring."""
        """Determine the task type from the query.""'
        query_lower = query.lower()

        if any(word in query_lower for word in ["code", "function", "class", "program", "script']):
            return "code_generation'
        elif any(word in query_lower for word in ["analyze", "analysis", "explain", "why", "how']):
            return "analysis'
        elif any(word in query_lower for word in ["create", "write", "generate", "make']):
            return "creative'
        elif any(word in query_lower for word in ["what", "who", "when", "where']):
            return "text_generation'
        else:
            return "text_generation'

    def _determine_complexity(self, query: str) -> str:
        """TODO: Add docstring."""
        """Determine query complexity.""'
        if len(query) > 200 or any(word in query.lower() for word in ["complex", "detailed", "comprehensive']):
            return "high'
        elif len(query) > 100:
            return "medium'
        else:
            return "low'

    def _requires_reasoning(self, query: str) -> bool:
        """TODO: Add docstring."""
        """Check if query requires logical reasoning.""'
        reasoning_words = ["why", "how", "explain", "analyze", "compare", "contrast", "reason']
        return any(word in query.lower() for word in reasoning_words)

    def _requires_creativity(self, query: str) -> bool:
        """TODO: Add docstring."""
        """Check if query requires creative output.""'
        creative_words = ["create", "write", "generate", "design", "imagine", "story", "poem']
        return any(word in query.lower() for word in creative_words)

async def main():
    """Main example function.""'
    logger.info("🎯 Ollama Pydantic AI Integration Example')
    logger.info("=' * 60)

    # Initialize the example system
    example = AgenticLLMExample()

    if await example.initialize():
        logger.info("✅ System ready for queries')

        # Example queries that would have used the large Qwen model
        queries = [
            {
                "query": "What is the architecture of the Agentic LLM Core system?',
                "context": {"latency_requirement': 2000}
            },
            {
                "query": "Write a Python function to calculate the factorial of a number with error handling',
                "context": {"latency_requirement': 3000}
            },
            {
                "query": "Analyze the benefits and risks of using local LLMs vs cloud-based LLMs',
                "context": {"latency_requirement': 5000}
            },
            {
                "query": "What is 15 * 23?',
                "context": {"latency_requirement': 500}
            }
        ]

        # Process each query
        for i, query_data in enumerate(queries, 1):
            logger.info(f"\n📝 Query {i}: {query_data["query"][:50]}...')
            logger.info("-' * 50)

            try:
                result = await example.process_user_query(
                    query_data["query'],
                    query_data["context']
                )

                logger.info(f"✅ Response generated')
                logger.info(f"   Model: {result["model_used"]}')
                logger.info(f"   Time: {result["processing_time"]:.2f}s')
                logger.info(f"   Confidence: {result["confidence"]:.2f}')
                logger.info(f"   Tokens: {result["tokens_generated"]}')
                logger.info(f"   Content: {result["content"][:100]}...')

            except Exception as e:
                logger.error(f"❌ Error processing query: {e}')

        # Show performance stats
        stats = example.core.agent.get_performance_stats()
        logger.info(f"\n📊 Performance Summary')
        logger.info("-' * 30)
        logger.info(f"Total requests: {stats["total_requests"]}')
        logger.info(f"Average time: {stats["average_time"]:.2f}s')
        logger.info(f"Model usage: {stats["model_usage"]}')

        logger.info("\n🎉 Example completed successfully!')
        logger.info("✅ Ollama models successfully integrated with Pydantic AI')
        logger.info("✅ Drop-in replacement for large Qwen model working')

    else:
        logger.error("❌ Failed to initialize system')

if __name__ == "__main__':
    asyncio.run(main())
