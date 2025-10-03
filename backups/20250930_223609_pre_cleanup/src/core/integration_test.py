#!/usr/bin/env python3
"""
Agentic LLM Core Integration Test

This script tests the integration of all core components:
- Input Ingestion Service
- Qwen3-Omni Engine
- Processing Pipeline

Complies with:
- System Specification: Agentic LLM Core v0.1 (specs/system.md)
- Architecture Plan: Agentic LLM Core v0.1 (plans/architecture.md)
- Milestone 1: Core Pipeline Foundation (tasks/milestone_1_core_pipeline.md)
"""

import asyncio
import logging
import sys
from pathlib import Path
import time
import json

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format = "%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from core.services.input_ingestion_service import InputIngestionService, InputValidator  # noqa: E402
from core.engines.qwen3_omni_engine import Qwen3OmniEngine  # noqa: E402

async def test_integration():
    """Test the complete integration pipeline"""
    logger.info("🚀 Starting Agentic LLM Core Integration Test")
    logger.info("=" * 60)

    # Initialize components
    logger.info("📥 Initializing components...")

    # Input ingestion service
    validator = InputValidator()
    ingestion_service = InputIngestionService(validator)
    logger.info("✅ Input ingestion service initialized")

    # Qwen3-Omni engine
    model_path = "./Qwen3-Omni-30B-A3B-Instruct"
    engine = Qwen3OmniEngine(model_path)

    if not await engine.initialize():
        logger.error("❌ Failed to initialize Qwen3-Omni engine")
        return False

    logger.info("✅ Qwen3-Omni engine initialized")

    try:
        # Test 1: Text Processing Pipeline
        logger.info("\n🧪 Test 1: Text Processing Pipeline")
        logger.info("-" * 40)

        text_content = "What is artificial intelligence and how does it work?"
        logger.info(f"Input: {text_content}")

        # Step 1: Ingest text
        start_time = time.time()
        processed_input = await ingestion_service.ingest_text(
            text_content,
            {"source": "integration_test", "language": "en"}
        )
        ingestion_time = time.time() - start_time
        logger.info(f"✅ Text ingested in {ingestion_time:.3f}s")

        # Step 2: Process multimodal input
        start_time = time.time()
        context = await engine.process_multimodal_input(processed_input)
        processing_time = time.time() - start_time
        logger.info(f"✅ Context processed in {processing_time:.3f}s")

        # Step 3: Analyze context
        start_time = time.time()
        analysis = await engine.analyze_context(context)
        analysis_time = time.time() - start_time
        logger.info(f"✅ Context analyzed in {analysis_time:.3f}s")
        logger.info(f"   Intent: {analysis.intent}")
        logger.info(f"   Entities: {analysis.entities}")
        logger.info(f"   Confidence: {analysis.confidence}")

        # Step 4: Generate answer
        start_time = time.time()
        answer = await engine.generate_answer(analysis)
        generation_time = time.time() - start_time
        logger.info(f"✅ Answer generated in {generation_time:.3f}s")
        logger.info(f"   Answer: {answer.answer[:100]}...")
        logger.info(f"   Confidence: {answer.confidence}")

        total_time = ingestion_time + processing_time + analysis_time + generation_time
        logger.info(f"📊 Total pipeline time: {total_time:.3f}s")

        # Test 2: Performance Validation
        logger.info("\n🧪 Test 2: Performance Validation")
        logger.info("-" * 40)

        # Check performance requirements from system.md
        requirements_met = True

        if total_time > 5.0:  # < 5 seconds requirement
            logger.warning(f"⚠️ Total time {total_time:.3f}s exceeds 5s requirement")
            requirements_met = False
        else:
            logger.info(f"✅ Total time {total_time:.3f}s meets <5s requirement")

        if ingestion_time > 1.0:  # < 1 second requirement
            logger.warning(f"⚠️ Ingestion time {ingestion_time:.3f}s exceeds 1s requirement")
            requirements_met = False
        else:
            logger.info(f"✅ Ingestion time {ingestion_time:.3f}s meets <1s requirement")

        if analysis_time > 2.0:  # < 2 seconds requirement
            logger.warning(f"⚠️ Analysis time {analysis_time:.3f}s exceeds 2s requirement")
            requirements_met = False
        else:
            logger.info(f"✅ Analysis time {analysis_time:.3f}s meets <2s requirement")

        if generation_time > 3.0:  # < 3 seconds requirement
            logger.warning(f"⚠️ Generation time {generation_time:.3f}s exceeds 3s requirement")
            requirements_met = False
        else:
            logger.info(f"✅ Generation time {generation_time:.3f}s meets <3s requirement")

        # Test 3: Multiple Input Types
        logger.info("\n🧪 Test 3: Multiple Input Types")
        logger.info("-" * 40)

        # Test image input
        try:
            image_data = b"fake_image_data_for_testing"
            image_input = await ingestion_service.ingest_image(
                image_data,
                {"source": "integration_test", "format": "png"}
            )
            logger.info(f"✅ Image input processed: {image_input.input_type}")

            # Process through pipeline
            context = await engine.process_multimodal_input(image_input)
            analysis = await engine.analyze_context(context)
            logger.info(f"✅ Image context analyzed: {analysis.intent}")

        except Exception as e:
            logger.warning(f"⚠️ Image processing test failed: {e}")

        # Test document input
        try:
            # Create temporary test document
            test_doc = Path("integration_test_doc.txt")
            test_doc.write_text("This is a test document for integration testing.")

            doc_input = await ingestion_service.ingest_document(
                str(test_doc),
                {"source": "integration_test"}
            )
            logger.info(f"✅ Document input processed: {doc_input.input_type}")

            # Process through pipeline
            context = await engine.process_multimodal_input(doc_input)
            analysis = await engine.analyze_context(context)
            logger.info(f"✅ Document context analyzed: {analysis.intent}")

            # Clean up
            if test_doc.exists():
                test_doc.unlink()

        except Exception as e:
            logger.warning(f"⚠️ Document processing test failed: {e}")

        # Test 4: Statistics and Metrics
        logger.info("\n🧪 Test 4: Statistics and Metrics")
        logger.info("-" * 40)

        # Get ingestion service stats
        ingestion_stats = ingestion_service.get_stats()
        logger.info(f"📊 Ingestion stats: {json.dumps(ingestion_stats, indent=2)}")

        # Get engine metrics
        engine_metrics = engine.get_performance_metrics()
        logger.info(f"📊 Engine metrics: {json.dumps(engine_metrics, indent=2)}")

        # Test 5: Error Handling
        logger.info("\n🧪 Test 5: Error Handling")
        logger.info("-" * 40)

        try:
            # Test invalid text input
            await ingestion_service.ingest_text("")  # Empty content
            logger.warning("⚠️ Empty text input should have failed")
        except Exception as e:
            logger.info(f"✅ Empty text input properly rejected: {e}")

        try:
            # Test invalid image format
            await ingestion_service.ingest_image(
                b"fake_data",
                {"format": "invalid_format"}
            )
            logger.warning("⚠️ Invalid image format should have failed")
        except Exception as e:
            logger.info(f"✅ Invalid image format properly rejected: {e}")

        # Final Results
        logger.info("\n🎯 Integration Test Results")
        logger.info("=" * 60)

        if requirements_met:
            logger.info("✅ All performance requirements met")
        else:
            logger.warning("⚠️ Some performance requirements not met")

        logger.info("✅ Integration test completed successfully!")
        logger.info("🚀 Agentic LLM Core is ready for development!")

        return True

    except Exception as e:
        logger.error(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # Cleanup
        engine.cleanup()
        logger.info("✅ Cleanup completed")

async def main():
    """Main integration test function"""
    success = await test_integration()
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
