#!/usr/bin/env python3
""'
Demo Script for MCP Automated Content Processing

This script demonstrates how to use the MCP-powered content processing pipeline
to automatically crawl, process, and store content from multiple sources.
""'

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path

from mcp_automated_content_processor import (
    MCPContentProcessor,
    ContentSource,
    ContentProcessingJob
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def demo_arxiv_processing():
    """Demo processing arXiv papers.""'
    logger.info("🔬 Starting arXiv processing demo...')

    # Initialize processor
    processor = MCPContentProcessor()

    if not await processor.initialize():
        logger.error("❌ Failed to initialize processor')
        return

    # Create arXiv-specific sources
    arxiv_sources = [
        ContentSource(
            name="arxiv_transformer',
            url="https://arxiv.org/search/?query=transformer+attention&searchtype=all',
            type="arxiv',
            priority=9,
            filters={"categories": ["cs.LG", "cs.CL"], "max_results': 20}
        ),
        ContentSource(
            name="arxiv_llm',
            url="https://arxiv.org/search/?query=large+language+model&searchtype=all',
            type="arxiv',
            priority=8,
            filters={"categories": ["cs.CL", "cs.AI"], "max_results': 15}
        )
    ]

    # Create processing job
    job = await processor.create_processing_job(
        sources=arxiv_sources,
        max_parallel=2,
        quality_threshold=0.7,
        relevance_threshold=0.6,
        auto_update_kb=True
    )

    logger.info(f"📋 Created job: {job.job_id}')

    # Process sources
    results = await processor.process_content_sources(job.job_id)

    logger.info(f"✅ Processing completed: {results}')

    # Get statistics
    stats = await processor.get_processing_stats()
    logger.info(f"📊 Processing stats: {json.dumps(stats, indent=2)}')

    return processor

async def demo_content_search(processor: MCPContentProcessor):
    """Demo searching processed content.""'
    logger.info("🔍 Starting content search demo...')

    # Search queries
    search_queries = [
        "transformer attention mechanism',
        "large language model training',
        "neural network architecture',
        "machine learning optimization'
    ]

    for query in search_queries:
        logger.info(f"🔎 Searching for: {query}')

        results = await processor.search_processed_content(
            query=query,
            limit=3,
            min_quality=0.6
        )

        logger.info(f"Found {len(results)} results:')
        for i, content in enumerate(results, 1):
            logger.info(f"  {i}. {content.title}')
            logger.info(f"     Source: {content.source}')
            logger.info(f"     Quality: {content.quality_score:.2f}')
            logger.info(f"     Category: {content.category}')
            logger.info(f"     Tags: {', '.join(content.tags[:3])}')
            logger.info("')

async def demo_quality_analysis(processor: MCPContentProcessor):
    """Demo quality analysis of processed content.""'
    logger.info("📈 Starting quality analysis demo...')

    # Get all processed content
    all_content = processor.processed_content

    if not all_content:
        logger.warning("No processed content found for quality analysis')
        return

    # Analyze quality distribution
    quality_scores = [c.quality_score for c in all_content]
    relevance_scores = [c.relevance_score for c in all_content]

    avg_quality = sum(quality_scores) / len(quality_scores)
    avg_relevance = sum(relevance_scores) / len(relevance_scores)

    high_quality = len([s for s in quality_scores if s >= 0.8])
    high_relevance = len([s for s in relevance_scores if s >= 0.8])

    logger.info(f"📊 Quality Analysis Results:')
    logger.info(f"   Total content items: {len(all_content)}')
    logger.info(f"   Average quality score: {avg_quality:.3f}')
    logger.info(f"   Average relevance score: {avg_relevance:.3f}')
    logger.info(f"   High quality items (≥0.8): {high_quality}')
    logger.info(f"   High relevance items (≥0.8): {high_relevance}')

    # Show top quality items
    top_quality = sorted(all_content, key=lambda x: x.quality_score, reverse=True)[:3]

    logger.info(f"🏆 Top Quality Items:')
    for i, content in enumerate(top_quality, 1):
        logger.info(f"   {i}. {content.title}')
        logger.info(f"      Quality: {content.quality_score:.3f}')
        logger.info(f"      Relevance: {content.relevance_score:.3f}')
        logger.info(f"      Source: {content.source}')

async def demo_continuous_processing():
    """Demo continuous processing setup.""'
    logger.info("🔄 Starting continuous processing demo...')

    processor = MCPContentProcessor()

    if not await processor.initialize():
        logger.error("❌ Failed to initialize processor')
        return

    # Create a continuous processing job
    continuous_sources = [
        ContentSource(
            name="arxiv_daily',
            url="https://arxiv.org/list/cs.AI/recent',
            type="arxiv',
            priority=9,
            crawl_interval=3600,  # 1 hour
            filters={"max_results': 10}
        ),
        ContentSource(
            name="github_daily',
            url="https://github.com/trending/python',
            type="github',
            priority=7,
            crawl_interval=1800,  # 30 minutes
            filters={"max_results': 5}
        )
    ]

    # Process continuously for a few cycles
    for cycle in range(3):
        logger.info(f"🔄 Processing cycle {cycle + 1}/3')

        job = await processor.create_processing_job(
            sources=continuous_sources,
            max_parallel=2,
            quality_threshold=0.5,
            relevance_threshold=0.4
        )

        results = await processor.process_content_sources(job.job_id)

        stats = await processor.get_processing_stats()
        logger.info(f"   Cycle {cycle + 1} stats: {stats['total_content_items']} items, avg quality: {stats['average_quality_score']:.3f}')

        # Wait before next cycle
        if cycle < 2:
            logger.info("⏳ Waiting 10 seconds before next cycle...')
            await asyncio.sleep(10)

async def main():
    """Main demo function.""'
    logger.info("🚀 Starting MCP Automated Content Processing Demo')
    logger.info("=' * 60)

    try:
        # Demo 1: Process arXiv papers
        processor = await demo_arxiv_processing()

        if processor:
            logger.info("\n" + "=' * 60)

            # Demo 2: Search processed content
            await demo_content_search(processor)

            logger.info("\n" + "=' * 60)

            # Demo 3: Quality analysis
            await demo_quality_analysis(processor)

            logger.info("\n" + "=' * 60)

            # Demo 4: Continuous processing
            await demo_continuous_processing()

        logger.info("\n🎉 Demo completed successfully!')

    except Exception as e:
        logger.error(f"❌ Demo failed: {e}')
        raise

if __name__ == "__main__':
    asyncio.run(main())
