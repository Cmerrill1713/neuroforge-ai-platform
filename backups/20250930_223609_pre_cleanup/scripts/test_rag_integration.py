#!/usr/bin/env python3
"""
Comprehensive Functional Test Suite for RAG Integration
Tests all components: Weaviate, Elasticsearch, Redis, Hybrid Retrieval, Evolutionary Optimizer
"""

import asyncio
import logging
import sys
import time
from pathlib import Path
from typing import Dict, Any, List
import json
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))


class RAGIntegrationTestSuite:
    """Comprehensive test suite for RAG integration"""
    
    def __init__(self):
        self.test_results = []
        self.start_time = time.time()
        
        # Component availability
        self.weaviate_available = False
        self.elasticsearch_available = False
        self.redis_available = False
        self.rag_service_available = False
        
    def add_result(self, test_name: str, passed: bool, message: str, duration_ms: float = 0, details: Dict = None):
        """Record test result"""
        result = {
            "test": test_name,
            "passed": passed,
            "message": message,
            "duration_ms": duration_ms,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"{status} | {test_name} | {message} ({duration_ms:.0f}ms)")
    
    # ========================================================================
    # TEST 1: Weaviate Connection
    # ========================================================================
    
    async def test_weaviate_connection(self):
        """Test Weaviate connectivity and basic operations"""
        test_name = "Weaviate Connection"
        start = time.time()
        
        try:
            import weaviate
            from src.core.retrieval.weaviate_store import WeaviateStore
            
            # Try to connect
            store = WeaviateStore(
                host="weaviate",
                http_port=8080,
                grpc_port=50051,
                class_name="DocChunk"
            )
            
            # Get stats
            stats = await store.get_stats()
            
            duration_ms = (time.time() - start) * 1000
            
            if stats.get("is_ready"):
                self.weaviate_available = True
                self.add_result(
                    test_name,
                    True,
                    f"Connected successfully",
                    duration_ms,
                    {"stats": stats}
                )
            else:
                self.add_result(
                    test_name,
                    False,
                    "Weaviate not ready",
                    duration_ms
                )
            
            store.close()
            
        except ImportError as e:
            duration_ms = (time.time() - start) * 1000
            self.add_result(
                test_name,
                False,
                f"Missing dependency: {e}",
                duration_ms
            )
        except Exception as e:
            duration_ms = (time.time() - start) * 1000
            self.add_result(
                test_name,
                False,
                f"Connection failed: {e}",
                duration_ms
            )
    
    # ========================================================================
    # TEST 2: Elasticsearch Connection
    # ========================================================================
    
    async def test_elasticsearch_connection(self):
        """Test Elasticsearch connectivity"""
        test_name = "Elasticsearch Connection"
        start = time.time()
        
        try:
            from elasticsearch import Elasticsearch
            
            es = Elasticsearch("http://elasticsearch:9200", request_timeout=5)
            
            # Test connection
            health = es.cluster.health()
            
            duration_ms = (time.time() - start) * 1000
            
            if health.get("status") in ["green", "yellow"]:
                self.elasticsearch_available = True
                self.add_result(
                    test_name,
                    True,
                    f"Connected - status: {health.get('status')}",
                    duration_ms,
                    {"health": health}
                )
            else:
                self.add_result(
                    test_name,
                    False,
                    f"Unhealthy - status: {health.get('status')}",
                    duration_ms
                )
            
            es.close()
            
        except ImportError as e:
            duration_ms = (time.time() - start) * 1000
            self.add_result(
                test_name,
                False,
                f"Missing dependency: {e}",
                duration_ms
            )
        except Exception as e:
            duration_ms = (time.time() - start) * 1000
            self.add_result(
                test_name,
                False,
                f"Connection failed: {e}",
                duration_ms
            )
    
    # ========================================================================
    # TEST 3: Redis Connection
    # ========================================================================
    
    async def test_redis_connection(self):
        """Test Redis connectivity"""
        test_name = "Redis Connection"
        start = time.time()
        
        try:
            import redis.asyncio as redis
            
            client = redis.from_url("redis://redis:6379/0", decode_responses=True)
            
            # Test ping
            pong = await client.ping()
            
            # Test set/get
            await client.set("test_key", "test_value", ex=10)
            value = await client.get("test_key")
            
            await client.close()
            
            duration_ms = (time.time() - start) * 1000
            
            if pong and value == "test_value":
                self.redis_available = True
                self.add_result(
                    test_name,
                    True,
                    "Connected - read/write OK",
                    duration_ms
                )
            else:
                self.add_result(
                    test_name,
                    False,
                    "Connection OK but read/write failed",
                    duration_ms
                )
                
        except ImportError as e:
            duration_ms = (time.time() - start) * 1000
            self.add_result(
                test_name,
                False,
                f"Missing dependency: {e}",
                duration_ms
            )
        except Exception as e:
            duration_ms = (time.time() - start) * 1000
            self.add_result(
                test_name,
                False,
                f"Connection failed: {e}",
                duration_ms
            )
    
    # ========================================================================
    # TEST 4: RAG Service Initialization
    # ========================================================================
    
    async def test_rag_service_init(self):
        """Test RAG service initialization"""
        test_name = "RAG Service Initialization"
        start = time.time()
        
        try:
            from src.core.retrieval.rag_service import create_rag_service
            
            rag = create_rag_service(env="production")
            
            duration_ms = (time.time() - start) * 1000
            
            # Check components
            has_weaviate = rag.weaviate is not None
            has_hybrid = rag.hybrid is not None
            has_embedder = rag.embedder is not None
            
            if has_weaviate and has_hybrid and has_embedder:
                self.rag_service_available = True
                self.add_result(
                    test_name,
                    True,
                    "All components initialized",
                    duration_ms,
                    {
                        "embedder": rag.embedder_model_name,
                        "weaviate_class": rag.weaviate.class_name
                    }
                )
            else:
                self.add_result(
                    test_name,
                    False,
                    f"Missing components: weaviate={has_weaviate}, hybrid={has_hybrid}, embedder={has_embedder}",
                    duration_ms
                )
            
            await rag.close()
            
        except Exception as e:
            duration_ms = (time.time() - start) * 1000
            self.add_result(
                test_name,
                False,
                f"Initialization failed: {e}",
                duration_ms
            )
    
    # ========================================================================
    # TEST 5: Embedding Generation
    # ========================================================================
    
    async def test_embedding_generation(self):
        """Test embedding generation"""
        test_name = "Embedding Generation"
        start = time.time()
        
        try:
            from src.core.retrieval.rag_service import create_rag_service
            
            rag = create_rag_service(env="production")
            
            # Generate embedding
            test_query = "What are the safety requirements for widget installation?"
            embedding = rag._embed_query(test_query)
            
            duration_ms = (time.time() - start) * 1000
            
            # Check embedding
            is_list = isinstance(embedding, list)
            has_values = len(embedding) > 0
            is_normalized = abs(sum(x**2 for x in embedding) - 1.0) < 0.01 if embedding else False
            
            if is_list and has_values and is_normalized:
                self.add_result(
                    test_name,
                    True,
                    f"Generated {len(embedding)}-dim normalized embedding",
                    duration_ms,
                    {
                        "dimensions": len(embedding),
                        "norm": sum(x**2 for x in embedding)**0.5
                    }
                )
            else:
                self.add_result(
                    test_name,
                    False,
                    f"Invalid embedding: list={is_list}, has_values={has_values}, normalized={is_normalized}",
                    duration_ms
                )
            
            await rag.close()
            
        except Exception as e:
            duration_ms = (time.time() - start) * 1000
            self.add_result(
                test_name,
                False,
                f"Generation failed: {e}",
                duration_ms
            )
    
    # ========================================================================
    # TEST 6: Vector Search (Weaviate)
    # ========================================================================
    
    async def test_vector_search(self):
        """Test vector search via Weaviate"""
        test_name = "Vector Search"
        start = time.time()
        
        if not self.weaviate_available:
            self.add_result(test_name, False, "Skipped - Weaviate not available", 0)
            return
        
        try:
            from src.core.retrieval.rag_service import create_rag_service
            
            rag = create_rag_service(env="production")
            
            # Generate embedding
            query = "safety requirements"
            embedding = rag._embed_query(query)
            
            # Search
            results = await rag.weaviate.query(
                embedding=embedding,
                k=5
            )
            
            duration_ms = (time.time() - start) * 1000
            
            if results:
                self.add_result(
                    test_name,
                    True,
                    f"Found {len(results)} results",
                    duration_ms,
                    {
                        "num_results": len(results),
                        "top_score": results[0].score if results else 0,
                        "sample_text": results[0].text[:100] if results else ""
                    }
                )
            else:
                self.add_result(
                    test_name,
                    False,
                    "No results found (may need to ingest documents first)",
                    duration_ms
                )
            
            await rag.close()
            
        except Exception as e:
            duration_ms = (time.time() - start) * 1000
            self.add_result(
                test_name,
                False,
                f"Search failed: {e}",
                duration_ms
            )
    
    # ========================================================================
    # TEST 7: Hybrid Retrieval
    # ========================================================================
    
    async def test_hybrid_retrieval(self):
        """Test hybrid retrieval (Weaviate + ES + RRF + Rerank)"""
        test_name = "Hybrid Retrieval"
        start = time.time()
        
        if not self.rag_service_available:
            self.add_result(test_name, False, "Skipped - RAG service not available", 0)
            return
        
        try:
            from src.core.retrieval.rag_service import create_rag_service
            
            rag = create_rag_service(env="production")
            
            # Hybrid search
            response = await rag.query(
                query_text="safety requirements for installation",
                k=5,
                method="hybrid",
                rerank=True
            )
            
            duration_ms = (time.time() - start) * 1000
            
            if response.results:
                # Get metrics
                metrics = rag.get_metrics()
                
                self.add_result(
                    test_name,
                    True,
                    f"Found {response.num_results} results",
                    duration_ms,
                    {
                        "num_results": response.num_results,
                        "latency_ms": response.latency_ms,
                        "retrieval_method": response.retrieval_method,
                        "cache_hit_ratio": metrics.get("hybrid", {}).get("cache_hit_ratio", 0),
                        "top_score": response.results[0].score if response.results else 0
                    }
                )
            else:
                self.add_result(
                    test_name,
                    False,
                    "No results found (may need to ingest documents first)",
                    duration_ms
                )
            
            await rag.close()
            
        except Exception as e:
            duration_ms = (time.time() - start) * 1000
            self.add_result(
                test_name,
                False,
                f"Hybrid search failed: {e}",
                duration_ms
            )
    
    # ========================================================================
    # TEST 8: Context Formatting
    # ========================================================================
    
    async def test_context_formatting(self):
        """Test context formatting for LLM prompts"""
        test_name = "Context Formatting"
        start = time.time()
        
        if not self.rag_service_available:
            self.add_result(test_name, False, "Skipped - RAG service not available", 0)
            return
        
        try:
            from src.core.retrieval.rag_service import create_rag_service
            
            rag = create_rag_service(env="production")
            
            # Get formatted context
            context = await rag.query_with_context(
                query_text="safety requirements",
                k=3,
                method="hybrid"
            )
            
            duration_ms = (time.time() - start) * 1000
            
            has_header = "Retrieved Context:" in context
            has_content = len(context) > 50
            
            if has_header and has_content:
                self.add_result(
                    test_name,
                    True,
                    f"Generated {len(context)} char context",
                    duration_ms,
                    {
                        "context_length": len(context),
                        "sample": context[:200]
                    }
                )
            else:
                self.add_result(
                    test_name,
                    False,
                    f"Invalid context: has_header={has_header}, has_content={has_content}",
                    duration_ms
                )
            
            await rag.close()
            
        except Exception as e:
            duration_ms = (time.time() - start) * 1000
            self.add_result(
                test_name,
                False,
                f"Formatting failed: {e}",
                duration_ms
            )
    
    # ========================================================================
    # TEST 9: Evolutionary Optimizer Integration
    # ========================================================================
    
    async def test_evolutionary_integration(self):
        """Test evolutionary optimizer with RAG integration"""
        test_name = "Evolutionary Optimizer Integration"
        start = time.time()
        
        try:
            # Check if integration file exists and is importable
            from src.core.prompting.dual_backend_integration import DualBackendEvolutionaryIntegration
            
            # Initialize (but don't run full evolution)
            integration = DualBackendEvolutionaryIntegration()
            
            # Check if it has the RAG service attribute (after patch is applied)
            has_rag_attr = hasattr(integration, 'rag_service') or hasattr(integration, 'vector_store')
            
            duration_ms = (time.time() - start) * 1000
            
            if has_rag_attr:
                self.add_result(
                    test_name,
                    True,
                    "Integration class loaded successfully",
                    duration_ms,
                    {
                        "has_rag_service": hasattr(integration, 'rag_service'),
                        "has_vector_store": hasattr(integration, 'vector_store')
                    }
                )
            else:
                self.add_result(
                    test_name,
                    False,
                    "Missing RAG/vector_store attribute (patch not applied?)",
                    duration_ms
                )
            
        except ImportError as e:
            duration_ms = (time.time() - start) * 1000
            self.add_result(
                test_name,
                False,
                f"Import failed: {e}",
                duration_ms
            )
        except Exception as e:
            duration_ms = (time.time() - start) * 1000
            self.add_result(
                test_name,
                False,
                f"Test failed: {e}",
                duration_ms
            )
    
    # ========================================================================
    # TEST 10: Performance Benchmark
    # ========================================================================
    
    async def test_performance_benchmark(self):
        """Benchmark retrieval performance"""
        test_name = "Performance Benchmark"
        
        if not self.rag_service_available:
            self.add_result(test_name, False, "Skipped - RAG service not available", 0)
            return
        
        try:
            from src.core.retrieval.rag_service import create_rag_service
            
            rag = create_rag_service(env="production")
            
            # Run multiple queries and measure
            queries = [
                "safety requirements",
                "installation procedures",
                "maintenance schedule",
                "troubleshooting guide",
                "technical specifications"
            ]
            
            latencies = []
            total_start = time.time()
            
            for query in queries:
                query_start = time.time()
                try:
                    response = await rag.query(
                        query_text=query,
                        k=5,
                        method="hybrid"
                    )
                    latency = (time.time() - query_start) * 1000
                    latencies.append(latency)
                except Exception as e:
                    logger.warning(f"Query failed: {e}")
            
            total_duration = (time.time() - total_start) * 1000
            
            if latencies:
                avg_latency = sum(latencies) / len(latencies)
                p95_latency = sorted(latencies)[int(len(latencies) * 0.95)] if len(latencies) > 1 else latencies[0]
                
                # Performance targets
                avg_ok = avg_latency < 500  # < 500ms average
                p95_ok = p95_latency < 1000  # < 1s p95
                
                self.add_result(
                    test_name,
                    avg_ok and p95_ok,
                    f"Avg: {avg_latency:.0f}ms, P95: {p95_latency:.0f}ms",
                    total_duration,
                    {
                        "queries": len(queries),
                        "successful": len(latencies),
                        "avg_latency_ms": avg_latency,
                        "p95_latency_ms": p95_latency,
                        "all_latencies": latencies
                    }
                )
            else:
                self.add_result(
                    test_name,
                    False,
                    "All queries failed",
                    total_duration
                )
            
            await rag.close()
            
        except Exception as e:
            self.add_result(
                test_name,
                False,
                f"Benchmark failed: {e}",
                0
            )
    
    # ========================================================================
    # Run All Tests
    # ========================================================================
    
    async def run_all_tests(self):
        """Run complete test suite"""
        logger.info("="*80)
        logger.info("RAG INTEGRATION FUNCTIONAL TEST SUITE")
        logger.info("="*80)
        logger.info("")
        
        # Run tests in sequence
        await self.test_weaviate_connection()
        await self.test_elasticsearch_connection()
        await self.test_redis_connection()
        await self.test_rag_service_init()
        await self.test_embedding_generation()
        await self.test_vector_search()
        await self.test_hybrid_retrieval()
        await self.test_context_formatting()
        await self.test_evolutionary_integration()
        await self.test_performance_benchmark()
        
        # Generate summary
        self.print_summary()
        self.save_results()
    
    def print_summary(self):
        """Print test summary"""
        logger.info("")
        logger.info("="*80)
        logger.info("TEST SUMMARY")
        logger.info("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r["passed"])
        failed_tests = total_tests - passed_tests
        
        total_duration = time.time() - self.start_time
        
        logger.info(f"\nTotal Tests: {total_tests}")
        logger.info(f"✅ Passed: {passed_tests}")
        logger.info(f"❌ Failed: {failed_tests}")
        logger.info(f"⏱️  Total Time: {total_duration:.2f}s")
        
        # System availability
        logger.info(f"\n📊 Component Availability:")
        logger.info(f"  Weaviate: {'✅' if self.weaviate_available else '❌'}")
        logger.info(f"  Elasticsearch: {'✅' if self.elasticsearch_available else '❌'}")
        logger.info(f"  Redis: {'✅' if self.redis_available else '❌'}")
        logger.info(f"  RAG Service: {'✅' if self.rag_service_available else '❌'}")
        
        # Failed tests detail
        if failed_tests > 0:
            logger.info(f"\n❌ Failed Tests:")
            for result in self.test_results:
                if not result["passed"]:
                    logger.info(f"  - {result['test']}: {result['message']}")
        
        # Performance summary
        perf_test = next((r for r in self.test_results if r["test"] == "Performance Benchmark"), None)
        if perf_test and perf_test["passed"]:
            details = perf_test["details"]
            logger.info(f"\n⚡ Performance:")
            logger.info(f"  Average Latency: {details['avg_latency_ms']:.0f}ms")
            logger.info(f"  P95 Latency: {details['p95_latency_ms']:.0f}ms")
        
        # Overall status
        logger.info("")
        if failed_tests == 0:
            logger.info("🎉 ALL TESTS PASSED!")
        else:
            logger.info(f"⚠️  {failed_tests} TEST(S) FAILED")
        
        logger.info("="*80)
    
    def save_results(self):
        """Save test results to file"""
        results_file = Path("test_results_rag_integration.json")
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_duration_seconds": time.time() - self.start_time,
            "total_tests": len(self.test_results),
            "passed": sum(1 for r in self.test_results if r["passed"]),
            "failed": sum(1 for r in self.test_results if not r["passed"]),
            "component_availability": {
                "weaviate": self.weaviate_available,
                "elasticsearch": self.elasticsearch_available,
                "redis": self.redis_available,
                "rag_service": self.rag_service_available
            },
            "test_results": self.test_results
        }
        
        results_file.write_text(json.dumps(report, indent=2))
        logger.info(f"\n📄 Results saved to: {results_file}")


async def main():
    """Run test suite"""
    suite = RAGIntegrationTestSuite()
    await suite.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())

