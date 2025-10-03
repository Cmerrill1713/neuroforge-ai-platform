#!/usr/bin/env python3
""'
Ingest Parallel-R1 paper into knowledge base with embeddings
""'

import asyncio
import logging
import sys
from pathlib import Path
from datetime import datetime, timezone

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src'))

from src.core.memory.ingest import IngestionPipeline, IngestionJob, IngestionSource, IngestionStatus
from src.core.memory.vector_pg import PostgreSQLVectorStore, PostgreSQLConfig
from src.core.providers.llm_qwen3 import Qwen3Provider
from src.core.memory.docker_config import create_docker_config

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def ingest_parallel_r1_paper():
    """Ingest the Parallel-R1 paper into the knowledge base with embeddings.""'

    logger.info("📚 Ingesting Parallel-R1 paper into knowledge base')
    logger.info("=' * 60)

    try:
        # 1. Create Docker configuration
        logger.info("Creating Docker configuration...')
        docker_config = create_docker_config()

        # 2. Initialize PostgreSQL vector store
        logger.info("Initializing PostgreSQL vector store...')
        pg_config = PostgreSQLConfig(
            database=docker_config.postgresql.database,
            username=docker_config.postgresql.username,
            password=docker_config.postgresql.password,
            host=docker_config.postgresql.host,
            port=docker_config.postgresql.port,
            vector_dimension=docker_config.postgresql.vector_dimension
        )
        vector_store = PostgreSQLVectorStore(pg_config)

        await vector_store.initialize()
        logger.info("✅ PostgreSQL vector store initialized')

        # 3. Create embedding provider
        logger.info("Creating embedding provider...')
        embedding_provider = Qwen3Provider(
            model_path="/models/qwen3-omni',
            enable_fallback=True
        )
        await embedding_provider.initialize()
        logger.info("✅ Embedding provider initialized')

        # 4. Create ingestion pipeline
        logger.info("Creating ingestion pipeline...')
        pipeline = IngestionPipeline(
            vector_store=vector_store,
            embedding_provider=embedding_provider
        )
        logger.info("✅ Ingestion pipeline created')

        # 5. Create ingestion job for Parallel-R1 paper
        logger.info("Creating ingestion job for Parallel-R1 paper...')

        # Read the paper content
        paper_path = Path("knowledge_base/parallel_r1_paper.md')
        if not paper_path.exists():
            logger.error(f"❌ Paper file not found: {paper_path}')
            return False

        with open(paper_path, "r", encoding="utf-8') as f:
            paper_content = f.read()

        # Create ingestion source
        source = IngestionSource(
            source_type="file',
            source_path=str(paper_path),
            content=paper_content,
            metadata={
                "title": "Parallel-R1: Towards Parallel Thinking via Reinforcement Learning',
                "authors": "Tong Zheng, Hongming Zhang, Wenhao Yu, Xiaoyang Wang, Runpeng Dai, Rui Liu, Huiwen Bao, Chengsong Huang, Heng Huang, Dong Yu',
                "source_url": "https://arxiv.org/pdf/2509.07980',
                "github_url": "https://github.com/zhengkid/Parallel-R1',
                "document_type": "research_paper',
                "domain": "artificial_intelligence',
                "subdomain": "reinforcement_learning',
                "keywords": ["parallel_thinking", "reinforcement_learning", "llm", "reasoning", "curriculum_learning'],
                "ingested_at': datetime.now(timezone.utc).isoformat()
            }
        )

        # Create ingestion job
        job = IngestionJob(
            job_id=f"parallel_r1_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            sources=[source],
            description="Ingest Parallel-R1 research paper into knowledge base'
        )

        logger.info(f"✅ Ingestion job created: {job.job_id}')

        # 6. Execute ingestion
        logger.info("Executing ingestion pipeline...')
        result_job = await pipeline.ingest_job(job)

        # 7. Report results
        logger.info("\n📊 Ingestion Results:')
        logger.info(f"   Job ID: {result_job.job_id}')
        logger.info(f"   Status: {result_job.status}')
        logger.info(f"   Total Documents: {result_job.total_documents}')
        logger.info(f"   Total Chunks: {result_job.total_chunks}')
        logger.info(f"   Successful Documents: {result_job.successful_documents}')
        logger.info(f"   Progress: {result_job.progress:.1%}')

        if result_job.status == IngestionStatus.COMPLETED:
            logger.info("✅ Parallel-R1 paper successfully ingested into knowledge base!')
            logger.info("   The paper is now available for retrieval with embeddings.')
            return True
        else:
            logger.error(f"❌ Ingestion failed: {result_job.error_message}')
            return False

    except Exception as e:
        logger.error(f"❌ Failed to ingest Parallel-R1 paper: {e}')
        return False

async def verify_ingestion():
    """Verify that the paper was properly ingested.""'

    logger.info("\n🔍 Verifying ingestion...')

    try:
        # Create vector store connection
        docker_config = create_docker_config()
        pg_config = PostgreSQLConfig(
            database=docker_config.postgresql.database,
            username=docker_config.postgresql.username,
            password=docker_config.postgresql.password,
            host=docker_config.postgresql.host,
            port=docker_config.postgresql.port,
            vector_dimension=docker_config.postgresql.vector_dimension
        )
        vector_store = PostgreSQLVectorStore(pg_config)

        await vector_store.initialize()

        # Search for Parallel-R1 content
        search_results = await vector_store.search(
            query="Parallel-R1 parallel thinking reinforcement learning',
            limit=5
        )

        logger.info(f"📋 Found {len(search_results)} relevant chunks:')
        for i, result in enumerate(search_results, 1):
            logger.info(f"   {i}. Score: {result.score:.3f}')
            logger.info(f"      Content: {result.content[:100]}...')
            logger.info(f"      Metadata: {result.metadata}')

        if search_results:
            logger.info("✅ Verification successful - Parallel-R1 paper is retrievable!')
            return True
        else:
            logger.warning("⚠️  No results found - may need to check ingestion')
            return False

    except Exception as e:
        logger.error(f"❌ Verification failed: {e}')
        return False

async def main():
    """Main function to ingest and verify Parallel-R1 paper.""'

    logger.info("🚀 Starting Parallel-R1 Knowledge Base Ingestion')
    logger.info("=' * 70)

    # Ingest the paper
    success = await ingest_parallel_r1_paper()

    if success:
        # Verify ingestion
        await verify_ingestion()

        logger.info("\n🎉 Parallel-R1 paper successfully added to knowledge base!')
        logger.info("   The paper is now embedded and available for retrieval.')
        logger.info("   You can query it using semantic search.')
    else:
        logger.error("\n❌ Failed to ingest Parallel-R1 paper into knowledge base')

if __name__ == "__main__':
    asyncio.run(main())
