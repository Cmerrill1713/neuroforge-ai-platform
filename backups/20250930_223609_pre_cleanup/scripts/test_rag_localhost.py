#!/usr/bin/env python3
"""
Localhost RAG Integration Test
Tests with actual running services on localhost
"""

import asyncio
import logging
import sys
import time
from pathlib import Path
import json
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

sys.path.insert(0, str(Path(__file__).parent))


class LocalhostRAGTest:
    """Test RAG integration with localhost services"""
    
    def __init__(self):
        self.results = []
    
    def log_result(self, test: str, passed: bool, message: str, duration_ms: float = 0):
        """Log test result"""
        status = "✅" if passed else "❌"
        logger.info(f"{status} {test}: {message} ({duration_ms:.0f}ms)")
        self.results.append({"test": test, "passed": passed, "message": message, "duration_ms": duration_ms})
    
    async def test_weaviate_localhost(self):
        """Test Weaviate on localhost:8090"""
        test = "Weaviate (localhost:8090)"
        start = time.time()
        
        try:
            import weaviate
            
            client = weaviate.connect_to_custom(
                http_host="localhost",
                http_port=8090,  # Your port
                http_secure=False,
                grpc_host="localhost",
                grpc_port=50051,
                grpc_secure=False
            )
            
            is_ready = client.is_ready()
            duration_ms = (time.time() - start) * 1000
            
            if is_ready:
                # Try to get collection
                try:
                    collections = client.collections.list_all()
                    self.log_result(test, True, f"Connected! Found {len(collections)} collections", duration_ms)
                except Exception as e:
                    self.log_result(test, True, f"Connected! (collection list failed: {e})", duration_ms)
            else:
                self.log_result(test, False, "Not ready", duration_ms)
            
            client.close()
            
        except Exception as e:
            duration_ms = (time.time() - start) * 1000
            self.log_result(test, False, f"Failed: {e}", duration_ms)
    
    async def test_elasticsearch_localhost(self):
        """Test Elasticsearch on localhost:9200"""
        test = "Elasticsearch (localhost:9200)"
        start = time.time()
        
        try:
            from elasticsearch import Elasticsearch
            
            es = Elasticsearch("http://localhost:9200", request_timeout=5, verify_certs=False)
            health = es.cluster.health()
            
            duration_ms = (time.time() - start) * 1000
            
            status = health.get("status", "unknown")
            num_docs = es.cat.count(format="json")
            
            self.log_result(test, True, f"Connected! Status: {status}, Docs: {num_docs}", duration_ms)
            es.close()
            
        except ImportError:
            duration_ms = (time.time() - start) * 1000
            self.log_result(test, False, "elasticsearch not installed: pip install elasticsearch", duration_ms)
        except Exception as e:
            duration_ms = (time.time() - start) * 1000
            self.log_result(test, False, f"Failed: {e}", duration_ms)
    
    async def test_redis_localhost(self):
        """Test Redis on localhost:6379"""
        test = "Redis (localhost:6379)"
        start = time.time()
        
        try:
            import redis.asyncio as redis
            
            client = redis.from_url("redis://localhost:6379/0", decode_responses=True)
            pong = await client.ping()
            
            # Test set/get
            await client.set("test_key", "test_value", ex=10)
            value = await client.get("test_key")
            
            duration_ms = (time.time() - start) * 1000
            
            if pong and value == "test_value":
                self.log_result(test, True, "Connected! Read/write OK", duration_ms)
            else:
                self.log_result(test, False, "Ping failed", duration_ms)
            
            await client.close()
            
        except Exception as e:
            duration_ms = (time.time() - start) * 1000
            self.log_result(test, False, f"Failed: {e}", duration_ms)
    
    async def test_postgres_localhost(self):
        """Test PostgreSQL on localhost:5433"""
        test = "PostgreSQL (localhost:5433)"
        start = time.time()
        
        try:
            import psycopg2
            
            conn = psycopg2.connect(
                host="localhost",
                port=5433,
                database="postgres",
                user="postgres",
                password="postgres",
                connect_timeout=5
            )
            
            cur = conn.cursor()
            cur.execute("SELECT version();")
            version = cur.fetchone()[0]
            
            duration_ms = (time.time() - start) * 1000
            
            self.log_result(test, True, f"Connected! Version: {version[:50]}", duration_ms)
            
            conn.close()
            
        except ImportError:
            duration_ms = (time.time() - start) * 1000
            self.log_result(test, False, "psycopg2 not installed", duration_ms)
        except Exception as e:
            duration_ms = (time.time() - start) * 1000
            self.log_result(test, False, f"Failed: {e}", duration_ms)
    
    async def test_rag_service_localhost(self):
        """Test RAG service with localhost config"""
        test = "RAG Service (localhost)"
        start = time.time()
        
        try:
            from src.core.retrieval.weaviate_store import WeaviateStore
            
            # Create store with localhost config
            store = WeaviateStore(
                host="localhost",
                http_port=8090,
                grpc_port=50051,
                class_name="DocChunk"
            )
            
            # Get stats
            stats = await store.get_stats()
            
            duration_ms = (time.time() - start) * 1000
            
            if stats.get("is_ready"):
                self.log_result(test, True, f"Weaviate store ready", duration_ms)
            else:
                self.log_result(test, False, "Store not ready", duration_ms)
            
            store.close()
            
        except Exception as e:
            duration_ms = (time.time() - start) * 1000
            self.log_result(test, False, f"Failed: {e}", duration_ms)
    
    async def test_embeddings(self):
        """Test embedding generation"""
        test = "Embeddings (sentence-transformers)"
        start = time.time()
        
        try:
            from sentence_transformers import SentenceTransformer
            
            model = SentenceTransformer("BAAI/bge-small-en-v1.5")
            
            query = "What are the safety requirements?"
            embedding = model.encode(query, normalize_embeddings=True, show_progress_bar=False)
            
            duration_ms = (time.time() - start) * 1000
            
            # Check normalization
            norm = sum(x**2 for x in embedding)**0.5
            
            self.log_result(
                test, 
                True, 
                f"Generated {len(embedding)}-dim embedding (norm: {norm:.3f})", 
                duration_ms
            )
            
        except Exception as e:
            duration_ms = (time.time() - start) * 1000
            self.log_result(test, False, f"Failed: {e}", duration_ms)
    
    async def test_query_weaviate(self):
        """Test actual Weaviate query"""
        test = "Weaviate Query"
        start = time.time()
        
        try:
            from src.core.retrieval.weaviate_store import WeaviateStore
            from sentence_transformers import SentenceTransformer
            
            # Get embedder
            model = SentenceTransformer("BAAI/bge-small-en-v1.5")
            embedding = model.encode("safety requirements", normalize_embeddings=True, show_progress_bar=False)
            
            # Query
            store = WeaviateStore(host="localhost", http_port=8090, grpc_port=50051, class_name="DocChunk")
            results = await store.query(embedding=embedding.tolist(), k=5)
            
            duration_ms = (time.time() - start) * 1000
            
            if results:
                self.log_result(test, True, f"Found {len(results)} results (top score: {results[0].score:.3f})", duration_ms)
            else:
                self.log_result(test, False, "No results (may need to ingest docs first)", duration_ms)
            
            store.close()
            
        except Exception as e:
            duration_ms = (time.time() - start) * 1000
            self.log_result(test, False, f"Failed: {e}", duration_ms)
    
    async def run_all(self):
        """Run all tests"""
        logger.info("="*80)
        logger.info("LOCALHOST RAG INTEGRATION TEST")
        logger.info("="*80)
        logger.info("")
        
        await self.test_weaviate_localhost()
        await self.test_elasticsearch_localhost()
        await self.test_redis_localhost()
        await self.test_postgres_localhost()
        await self.test_rag_service_localhost()
        await self.test_embeddings()
        await self.test_query_weaviate()
        
        # Summary
        logger.info("")
        logger.info("="*80)
        logger.info("SUMMARY")
        logger.info("="*80)
        
        passed = sum(1 for r in self.results if r["passed"])
        failed = len(self.results) - passed
        
        logger.info(f"Total: {len(self.results)} | Passed: {passed} | Failed: {failed}")
        
        if failed == 0:
            logger.info("🎉 ALL TESTS PASSED!")
        else:
            logger.info(f"⚠️  {failed} test(s) failed")
        
        logger.info("="*80)
        
        # Save
        Path("test_results_localhost.json").write_text(json.dumps({
            "timestamp": datetime.now().isoformat(),
            "results": self.results,
            "passed": passed,
            "failed": failed
        }, indent=2))


async def main():
    test = LocalhostRAGTest()
    await test.run_all()


if __name__ == "__main__":
    asyncio.run(main())

