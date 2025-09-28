"""
Knowledge Base Adapter Example

This example demonstrates how to use the knowledge base adapter with the existing
Docker infrastructure including PostgreSQL, Weaviate, and Redis.

Created: 2024-09-24
Status: Draft
"""

import asyncio
import logging
from typing import List, Dict, Any

from src.core.memory.docker_config import create_docker_config, create_health_checker
from src.core.memory.vector_pg import create_and_initialize_vector_store
from src.core.memory.vector_weaviate import create_and_initialize_weaviate_store
from src.core.memory.ingest import create_ingestion_pipeline
from src.core.providers.llm_qwen3 import create_qwen3_provider_for_apple_silicon


# ============================================================================
# Example Usage
# ============================================================================

async def main():
    """Main example function."""
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    logger.info("Starting Knowledge Base Adapter Example")
    
    try:
        # 1. Check Docker infrastructure health
        logger.info("Checking Docker infrastructure health...")
        health_checker = create_health_checker()
        health_status = await health_checker.check_all_services()
        
        for service, status in health_status.items():
            logger.info(f"{service}: {status['status']}")
            if status['status'] == 'unhealthy':
                logger.warning(f"{service} is unhealthy: {status.get('error', 'Unknown error')}")
        
        # 2. Create Docker configuration
        logger.info("Creating Docker configuration...")
        docker_config = create_docker_config()
        
        # 3. Initialize vector stores
        logger.info("Initializing vector stores...")
        
        # PostgreSQL vector store
        pg_store = await create_and_initialize_vector_store(
            database=docker_config.postgresql.database,
            username=docker_config.postgresql.username,
            password=docker_config.postgresql.password,
            host=docker_config.postgresql.host,
            port=docker_config.postgresql.port,
            vector_dimension=docker_config.postgresql.vector_dimension
        )
        logger.info("PostgreSQL vector store initialized")
        
        # Weaviate vector store
        weaviate_store = await create_and_initialize_weaviate_store(
            host=docker_config.weaviate.host,
            port=docker_config.weaviate.port,
            class_name=docker_config.weaviate.class_name,
            vector_dimension=docker_config.weaviate.vector_dimension
        )
        logger.info("Weaviate vector store initialized")
        
        # 4. Create embedding provider
        logger.info("Creating embedding provider...")
        embedding_provider = create_qwen3_provider_for_apple_silicon(
            model_path="/models/qwen3-omni",
            enable_fallback=True
        )
        await embedding_provider.initialize()
        logger.info("Embedding provider initialized")
        
        # 5. Create ingestion pipeline
        logger.info("Creating ingestion pipeline...")
        ingestion_pipeline = create_ingestion_pipeline(
            vector_store=pg_store,  # Use PostgreSQL as primary store
            embedding_provider=embedding_provider,
            chunk_size=1000,
            chunk_overlap=200,
            batch_size=32
        )
        logger.info("Ingestion pipeline created")
        
        # 6. Ingest sample documents
        logger.info("Ingesting sample documents...")
        
        # Sample documents
        sample_texts = [
            "Artificial intelligence is transforming the way we work and live. Machine learning algorithms can now process vast amounts of data to identify patterns and make predictions.",
            "Natural language processing enables computers to understand and generate human language. This technology powers chatbots, translation services, and voice assistants.",
            "Computer vision allows machines to interpret and understand visual information from the world. Applications include autonomous vehicles, medical imaging, and facial recognition.",
            "Deep learning uses neural networks with multiple layers to learn complex patterns in data. This approach has revolutionized fields like image recognition and natural language understanding.",
            "The future of AI lies in developing more efficient algorithms, better data processing techniques, and more powerful computing resources. Quantum computing may play a crucial role in advancing AI capabilities."
        ]
        
        # Ingest each text
        for i, text in enumerate(sample_texts):
            logger.info(f"Ingesting document {i + 1}/5...")
            
            job = await ingestion_pipeline.ingest_text(
                content=text,
                title=f"AI Document {i + 1}",
                metadata={
                    "category": "artificial_intelligence",
                    "topic": f"ai_topic_{i + 1}",
                    "source": "example",
                    "index": i + 1
                }
            )
            
            logger.info(f"Document {i + 1} ingested successfully. Status: {job.status}")
            logger.info(f"Total documents: {job.total_documents}, Total chunks: {job.total_chunks}")
        
        # 7. Query the knowledge base
        logger.info("Querying the knowledge base...")
        
        # Create a query vector (in practice, this would come from the embedding provider)
        query_vector = [0.1] * 1536  # Placeholder vector
        
        # Query PostgreSQL store
        logger.info("Querying PostgreSQL vector store...")
        pg_results = await pg_store.query(
            vector=query_vector,
            limit=3,
            filter_metadata={"category": "artificial_intelligence"}
        )
        
        logger.info(f"PostgreSQL returned {len(pg_results)} results:")
        for i, result in enumerate(pg_results):
            logger.info(f"  {i + 1}. {result.document.title} (similarity: {result.similarity_score:.3f})")
            logger.info(f"     Content: {result.document.content[:100]}...")
        
        # Query Weaviate store
        logger.info("Querying Weaviate vector store...")
        weaviate_results = await weaviate_store.query(
            vector=query_vector,
            limit=3,
            filter_metadata={"category": "artificial_intelligence"}
        )
        
        logger.info(f"Weaviate returned {len(weaviate_results)} results:")
        for i, result in enumerate(weaviate_results):
            logger.info(f"  {i + 1}. {result.document.title} (similarity: {result.similarity_score:.3f})")
            logger.info(f"     Content: {result.document.content[:100]}...")
        
        # 8. Search by metadata
        logger.info("Searching by metadata...")
        metadata_results = await pg_store.search_by_metadata(
            metadata={"category": "artificial_intelligence"},
            limit=5
        )
        
        logger.info(f"Metadata search returned {len(metadata_results)} results:")
        for i, doc in enumerate(metadata_results):
            logger.info(f"  {i + 1}. {doc.title} - {doc.metadata}")
        
        # 9. Get store statistics
        logger.info("Getting store statistics...")
        pg_stats = await pg_store.get_stats()
        weaviate_stats = await weaviate_store.get_stats()
        
        logger.info("PostgreSQL Statistics:")
        for key, value in pg_stats.items():
            logger.info(f"  {key}: {value}")
        
        logger.info("Weaviate Statistics:")
        for key, value in weaviate_stats.items():
            logger.info(f"  {key}: {value}")
        
        # 10. Health checks
        logger.info("Performing health checks...")
        pg_health = await pg_store.health_check()
        weaviate_health = await weaviate_store.health_check()
        
        logger.info(f"PostgreSQL Health: {pg_health['status']}")
        logger.info(f"Weaviate Health: {weaviate_health['status']}")
        
        logger.info("Knowledge Base Adapter Example completed successfully!")
        
    except Exception as e:
        logger.error(f"Example failed: {e}")
        raise
    
    finally:
        # Cleanup
        logger.info("Cleaning up resources...")
        if 'pg_store' in locals():
            await pg_store.close()
        if 'weaviate_store' in locals():
            await weaviate_store.close()
        logger.info("Cleanup completed")


# ============================================================================
# Advanced Examples
# ============================================================================

async def advanced_example():
    """Advanced example with custom configuration and error handling."""
    logger = logging.getLogger(__name__)
    
    try:
        # Custom Docker configuration
        docker_config = create_docker_config(
            postgresql_overrides={
                "min_connections": 10,
                "max_connections": 50,
                "batch_size": 2000
            },
            weaviate_overrides={
                "batch_size": 200,
                "timeout": 60.0
            },
            redis_overrides={
                "max_connections": 50,
                "socket_timeout": 10.0
            }
        )
        
        logger.info("Using custom Docker configuration")
        
        # Initialize stores with custom config
        pg_store = await create_and_initialize_vector_store(
            database=docker_config.postgresql.database,
            username=docker_config.postgresql.username,
            password=docker_config.postgresql.password,
            host=docker_config.postgresql.host,
            port=docker_config.postgresql.port,
            vector_dimension=docker_config.postgresql.vector_dimension,
            min_connections=docker_config.postgresql.min_connections,
            max_connections=docker_config.postgresql.max_connections,
            batch_size=docker_config.postgresql.batch_size
        )
        
        weaviate_store = await create_and_initialize_weaviate_store(
            host=docker_config.weaviate.host,
            port=docker_config.weaviate.port,
            class_name=docker_config.weaviate.class_name,
            vector_dimension=docker_config.weaviate.vector_dimension,
            batch_size=docker_config.weaviate.batch_size,
            timeout=docker_config.weaviate.timeout
        )
        
        logger.info("Advanced configuration applied successfully")
        
        # Perform advanced operations
        # ... (additional advanced operations would go here)
        
    except Exception as e:
        logger.error(f"Advanced example failed: {e}")
        raise


# ============================================================================
# Performance Benchmark
# ============================================================================

async def performance_benchmark():
    """Performance benchmark for knowledge base operations."""
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize stores
        docker_config = create_docker_config()
        
        pg_store = await create_and_initialize_vector_store(
            database=docker_config.postgresql.database,
            username=docker_config.postgresql.username,
            password=docker_config.postgresql.password,
            host=docker_config.postgresql.host,
            port=docker_config.postgresql.port,
            vector_dimension=docker_config.postgresql.vector_dimension
        )
        
        # Benchmark indexing
        logger.info("Benchmarking indexing performance...")
        
        import time
        from src.core.memory.vector_pg import Document, DocumentType
        
        # Create test documents
        test_documents = [
            Document(
                content=f"Test document {i} with some content about artificial intelligence and machine learning.",
                title=f"Test Doc {i}",
                doc_type=DocumentType.TEXT,
                metadata={"index": i, "category": "test"}
            )
            for i in range(100)
        ]
        
        # Create test vectors
        test_vectors = [[0.1 + i * 0.001] * 1536 for i in range(100)]
        
        # Benchmark indexing
        start_time = time.time()
        indexed_ids = await pg_store.index(test_documents, test_vectors)
        end_time = time.time()
        
        indexing_time = end_time - start_time
        docs_per_second = len(indexed_ids) / indexing_time
        
        logger.info(f"Indexing Performance:")
        logger.info(f"  Documents indexed: {len(indexed_ids)}")
        logger.info(f"  Time taken: {indexing_time:.2f} seconds")
        logger.info(f"  Documents per second: {docs_per_second:.2f}")
        
        # Benchmark querying
        logger.info("Benchmarking query performance...")
        
        query_vector = [0.1] * 1536
        
        start_time = time.time()
        for _ in range(10):
            results = await pg_store.query(query_vector, limit=10)
        end_time = time.time()
        
        query_time = (end_time - start_time) / 10
        queries_per_second = 1 / query_time
        
        logger.info(f"Query Performance:")
        logger.info(f"  Average query time: {query_time:.3f} seconds")
        logger.info(f"  Queries per second: {queries_per_second:.2f}")
        
        # Cleanup
        await pg_store.delete(indexed_ids)
        await pg_store.close()
        
        logger.info("Performance benchmark completed")
        
    except Exception as e:
        logger.error(f"Performance benchmark failed: {e}")
        raise


# ============================================================================
# Main execution
# ============================================================================

if __name__ == "__main__":
    # Run the main example
    asyncio.run(main())
    
    # Uncomment to run advanced examples
    # asyncio.run(advanced_example())
    # asyncio.run(performance_benchmark())
