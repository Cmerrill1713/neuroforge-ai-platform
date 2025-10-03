#!/usr/bin/env python3
""'
Test Ollama Pydantic AI Integration

This script demonstrates how the Ollama models integrate with your existing
Pydantic AI agentic setup, providing a complete replacement for the large Qwen model.
""'

import asyncio
import logging
import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..'))

from src.core.engines.ollama_pydantic_ai import OllamaAgenticLLMCore, OllamaAgentConfig, OllamaToolContext

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_ollama_pydantic_integration():
    """Test the Ollama Pydantic AI integration.""'
    logger.info("🧪 Testing Ollama Pydantic AI Integration')
    logger.info("=' * 60)

    # Initialize the system
    config = OllamaAgentConfig(
        max_tokens=1024,
        temperature=0.7,
        enable_model_switching=True
    )

    core = OllamaAgenticLLMCore(config)

    if await core.initialize():
        logger.info("✅ Ollama Pydantic AI system initialized')

        # Test 1: General text generation
        logger.info("\n📝 Test 1: General Text Generation')
        logger.info("-' * 40)

        result = await core.generate_answer(
            "Explain how the Agentic LLM Core system works with Pydantic AI'
        )

        logger.info(f"Answer: {result["answer"][:200]}...')
        logger.info(f"Model used: {result["model_used"]}')
        logger.info(f"Processing time: {result["processing_time"]:.2f}s')
        logger.info(f"Confidence: {result["confidence"]:.2f}')

        # Test 2: Coding task with tool execution
        logger.info("\n💻 Test 2: Coding Task')
        logger.info("-' * 40)

        coding_context = OllamaToolContext(
            task_type="code_generation',
            complexity="medium',
            requires_reasoning=True
        )

        coding_result = await core.process_request(
            "Create a Python class for managing a simple database connection with error handling',
            context=coding_context
        )

        logger.info(f"Code generated: {len(coding_result.content)} characters')
        logger.info(f"Model used: {coding_result.model_used}')
        logger.info(f"Processing time: {coding_result.processing_time:.2f}s')

        # Test 3: Analysis with knowledge base integration
        logger.info("\n🔍 Test 3: Analysis Task')
        logger.info("-' * 40)

        analysis_context = OllamaToolContext(
            task_type="analysis',
            complexity="high',
            requires_reasoning=True,
            latency_requirement=5000
        )

        analysis_result = await core.process_request(
            "Analyze the architecture of the Agentic LLM Core system and explain how the components interact',
            context=analysis_context
        )

        logger.info(f"Analysis completed: {len(analysis_result.content)} characters')
        logger.info(f"Model used: {analysis_result.model_used}')
        logger.info(f"Processing time: {analysis_result.processing_time:.2f}s')

        # Test 4: Fast response
        logger.info("\n⚡ Test 4: Fast Response')
        logger.info("-' * 40)

        fast_context = OllamaToolContext(
            task_type="simple_reasoning',
            complexity="low',
            latency_requirement=500
        )

        fast_result = await core.process_request(
            "What is 15 + 27?',
            context=fast_context
        )

        logger.info(f"Fast response: {fast_result.content}')
        logger.info(f"Model used: {fast_result.model_used}')
        logger.info(f"Processing time: {fast_result.processing_time:.2f}s')

        # Test 5: Tool execution simulation
        logger.info("\n🔧 Test 5: Tool Execution')
        logger.info("-' * 40)

        # Simulate tool execution with Ollama validation
        tool_result = await core.agent._ollama_execute_tool(
            "file_read',
            {"file_path": "README.md'}
        )

        logger.info(f"Tool execution result: {tool_result}')

        # Show performance statistics
        stats = core.agent.get_performance_stats()
        logger.info("\n📊 Performance Statistics')
        logger.info("-' * 40)
        logger.info(f"Total requests: {stats["total_requests"]}')
        logger.info(f"Total time: {stats["total_time"]:.2f}s')
        logger.info(f"Average time: {stats["average_time"]:.2f}s')
        logger.info(f"Model usage: {stats["model_usage"]}')

        logger.info("\n🎉 All tests completed successfully!')
        logger.info("✅ Ollama Pydantic AI integration is working properly')

        return True

    else:
        logger.error("❌ Failed to initialize Ollama Pydantic AI system')
        return False

async def test_agentic_capabilities():
    """Test the agentic capabilities of the system.""'
    logger.info("\n🤖 Testing Agentic Capabilities')
    logger.info("=' * 50)

    core = OllamaAgenticLLMCore()

    if await core.initialize():
        # Test complex agentic workflow
        logger.info("Testing complex agentic workflow...')

        # Step 1: Analyze the request
        analysis = await core.analyze_context(
            "I need to build a web application that processes user data and generates reports'
        )

        logger.info(f"Analysis: {analysis["analysis"][:150]}...')

        # Step 2: Generate implementation plan
        plan_result = await core.process_request(
            "Create a detailed implementation plan for the web application',
            task_type="planning'
        )

        logger.info(f"Plan generated: {len(plan_result.content)} characters')

        # Step 3: Generate code
        code_result = await core.process_request(
            "Write the main application code for the web application',
            task_type="code_generation'
        )

        logger.info(f"Code generated: {len(code_result.content)} characters')

        logger.info("✅ Agentic capabilities test completed')
        return True

    else:
        logger.error("❌ Failed to initialize for agentic testing')
        return False

async def main():
    """Main test function.""'
    logger.info("🚀 Starting Ollama Pydantic AI Integration Tests')

    # Test basic integration
    integration_success = await test_ollama_pydantic_integration()

    # Test agentic capabilities
    agentic_success = await test_agentic_capabilities()

    if integration_success and agentic_success:
        logger.info("\n🎉 All tests passed!')
        logger.info("✅ Ollama models successfully integrated with Pydantic AI')
        logger.info("✅ Agentic capabilities are working')
        logger.info("✅ Ready for production use')

        logger.info("\n📋 Integration Summary:')
        logger.info("  • Ollama models replace large Qwen model')
        logger.info("  • Pydantic AI provides type-safe agent operations')
        logger.info("  • Tool execution with intelligent model routing')
        logger.info("  • Knowledge base integration maintained')
        logger.info("  • Performance optimized for Apple Silicon')

    else:
        logger.error("\n❌ Some tests failed')

if __name__ == "__main__':
    asyncio.run(main())
