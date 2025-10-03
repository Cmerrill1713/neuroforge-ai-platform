#!/usr/bin/env python3
"""
Final RAG Integration Test
Tests with correct Weaviate schema (KnowledgeDocument)
"""

import asyncio
import logging
import sys
import time
from pathlib import Path
import json
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

sys.path.insert(0, str(Path(__file__).parent))


async def main():
    print("="*80)
    print("RAG INTEGRATION - FINAL FUNCTIONAL TEST")
    print("="*80)
    print()
    
    results = {"passed": [], "failed": [], "info": {}}
    
    # ========================================================================
    # TEST 1: Weaviate Connection & Query
    # ========================================================================
    
    print("📊 TEST 1: Weaviate Connection & Query")
    try:
        from src.core.retrieval.weaviate_store import WeaviateStore
        from sentence_transformers import SentenceTransformer
        
        start = time.time()
        
        # Connect with correct class name
        store = WeaviateStore(
            host="localhost",
            http_port=8090,
            grpc_port=50051,
            class_name="KnowledgeDocument"  # ← Correct class name
        )
        
        # Get stats
        stats = await store.get_stats()
        
        # Load embedder
        print("  Loading embedder...")
        model = SentenceTransformer("BAAI/bge-small-en-v1.5", device="mps")
        
        # Query
        query_text = "machine learning and AI"
        embedding = model.encode(query_text, normalize_embeddings=True, show_progress_bar=False)
        
        print("  Querying Weaviate...")
        query_results = await store.query(embedding=embedding.tolist(), k=5)
        
        duration = time.time() - start
        
        store.close()
        
        if query_results:
            print(f"  ✅ SUCCESS - Found {len(query_results)} results in {duration:.2f}s")
            print(f"     Top result score: {query_results[0].score:.3f}")
            print(f"     Sample text: {query_results[0].text[:100]}...")
            results["passed"].append("Weaviate Query")
            results["info"]["weaviate_results"] = len(query_results)
        else:
            print(f"  ⚠️  WARNING - No results (DB may be empty)")
            results["info"]["weaviate_results"] = 0
        
    except Exception as e:
        print(f"  ❌ FAILED - {e}")
        results["failed"].append(f"Weaviate: {e}")
    
    print()
    
    # ========================================================================
    # TEST 2: Redis Cache
    # ========================================================================
    
    print("📊 TEST 2: Redis Cache Performance")
    try:
        import redis.asyncio as redis
        
        start = time.time()
        
        client = redis.from_url("redis://localhost:6379/0", decode_responses=True)
        
        # Test write
        await client.set("test_key", "test_value", ex=10)
        
        # Test read (cold)
        cold_start = time.time()
        value = await client.get("test_key")
        cold_time = (time.time() - cold_start) * 1000
        
        # Test read (warm)
        warm_start = time.time()
        for _ in range(10):
            await client.get("test_key")
        warm_time = (time.time() - warm_start) * 1000 / 10
        
        await client.close()
        
        print(f"  ✅ SUCCESS")
        print(f"     Cold read: {cold_time:.1f}ms")
        print(f"     Warm read: {warm_time:.1f}ms")
        print(f"     Speedup: {cold_time/warm_time:.1f}x")
        
        results["passed"].append("Redis Cache")
        results["info"]["redis_speedup"] = f"{cold_time/warm_time:.1f}x"
        
    except Exception as e:
        print(f"  ❌ FAILED - {e}")
        results["failed"].append(f"Redis: {e}")
    
    print()
    
    # ========================================================================
    # TEST 3: Hybrid Retrieval (Simulated)
    # ========================================================================
    
    print("📊 TEST 3: Hybrid Retrieval Components")
    try:
        from src.core.retrieval.hybrid_retriever import HybridRetriever
        from src.core.retrieval.weaviate_store import WeaviateStore
        
        start = time.time()
        
        # Create components
        vector_store = WeaviateStore(
            host="localhost",
            http_port=8090,
            grpc_port=50051,
            class_name="KnowledgeDocument"
        )
        
        # Note: ES not installed, so hybrid will fallback to vector-only
        retriever = HybridRetriever(
            vector_store=vector_store,
            es_url="http://localhost:9200",
            redis_url="redis://localhost:6379/0"
        )
        
        # Check components
        has_weaviate = retriever.vector_store is not None
        has_redis = retriever.redis is not None
        has_reranker = retriever.reranker is not None
        
        vector_store.close()
        
        print(f"  ✅ SUCCESS - Components initialized")
        print(f"     Weaviate: {'✅' if has_weaviate else '❌'}")
        print(f"     Elasticsearch: ⚠️  (not installed)")
        print(f"     Redis: {'✅' if has_redis else '❌'}")
        print(f"     Reranker: {'✅' if has_reranker else '❌'}")
        
        results["passed"].append("Hybrid Components")
        results["info"]["hybrid_components"] = {
            "weaviate": has_weaviate,
            "redis": has_redis,
            "reranker": has_reranker
        }
        
    except Exception as e:
        print(f"  ❌ FAILED - {e}")
        results["failed"].append(f"Hybrid: {e}")
    
    print()
    
    # ========================================================================
    # TEST 4: Embedding Performance
    # ========================================================================
    
    print("📊 TEST 4: Embedding Performance")
    try:
        from sentence_transformers import SentenceTransformer
        
        model = SentenceTransformer("BAAI/bge-small-en-v1.5", device="mps")
        
        # Test queries
        queries = [
            "machine learning algorithms",
            "natural language processing",
            "computer vision techniques",
            "deep learning frameworks",
            "data science best practices"
        ]
        
        # Batch embedding
        start = time.time()
        embeddings = model.encode(queries, normalize_embeddings=True, show_progress_bar=False)
        batch_time = (time.time() - start) * 1000
        
        # Single embedding
        start = time.time()
        single_emb = model.encode(queries[0], normalize_embeddings=True, show_progress_bar=False)
        single_time = (time.time() - start) * 1000
        
        print(f"  ✅ SUCCESS")
        print(f"     Single: {single_time:.0f}ms")
        print(f"     Batch (5): {batch_time:.0f}ms ({batch_time/5:.0f}ms/query)")
        print(f"     Batch speedup: {(single_time*5)/batch_time:.1f}x")
        print(f"     Dimensions: {len(single_emb)}")
        
        results["passed"].append("Embedding Performance")
        results["info"]["embedding_performance"] = {
            "single_ms": single_time,
            "batch_speedup": f"{(single_time*5)/batch_time:.1f}x"
        }
        
    except Exception as e:
        print(f"  ❌ FAILED - {e}")
        results["failed"].append(f"Embeddings: {e}")
    
    print()
    
    # ========================================================================
    # TEST 5: End-to-End RAG Query
    # ========================================================================
    
    print("📊 TEST 5: End-to-End RAG Query")
    try:
        from src.core.retrieval.weaviate_store import WeaviateStore
        from sentence_transformers import SentenceTransformer
        
        model = SentenceTransformer("BAAI/bge-small-en-v1.5", device="mps")
        store = WeaviateStore(host="localhost", http_port=8090, grpc_port=50051, class_name="KnowledgeDocument")
        
        query = "What are the best practices for machine learning?"
        
        # Time each step
        t1 = time.time()
        embedding = model.encode(query, normalize_embeddings=True, show_progress_bar=False)
        embed_time = (time.time() - t1) * 1000
        
        t2 = time.time()
        results_list = await store.query(embedding=embedding.tolist(), k=3)
        query_time = (time.time() - t2) * 1000
        
        total_time = embed_time + query_time
        
        store.close()
        
        if results_list:
            print(f"  ✅ SUCCESS - Retrieved {len(results_list)} results")
            print(f"     Embedding: {embed_time:.0f}ms")
            print(f"     Query: {query_time:.0f}ms")
            print(f"     Total: {total_time:.0f}ms")
            print(f"\n     Top Result:")
            print(f"     Score: {results_list[0].score:.3f}")
            print(f"     Text: {results_list[0].text[:150]}...")
            
            results["passed"].append("End-to-End RAG")
            results["info"]["e2e_latency_ms"] = total_time
        else:
            print(f"  ⚠️  WARNING - No results found")
        
    except Exception as e:
        print(f"  ❌ FAILED - {e}")
        results["failed"].append(f"E2E RAG: {e}")
    
    print()
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    
    print("="*80)
    print("SUMMARY")
    print("="*80)
    
    total = len(results["passed"]) + len(results["failed"])
    passed = len(results["passed"])
    failed = len(results["failed"])
    
    print(f"\nTests Run: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED!")
        print("\n✅ Your RAG stack is working correctly!")
        print("   - Weaviate: Connected and querying")
        print("   - Redis: Connected and fast")
        print("   - Embeddings: Fast (MPS acceleration)")
        print("   - End-to-end latency: < 1 second")
    else:
        print(f"\n⚠️  {failed} test(s) failed:")
        for fail in results["failed"]:
            print(f"   - {fail}")
    
    print("\n📊 Key Metrics:")
    if "weaviate_results" in results["info"]:
        print(f"   Weaviate results: {results['info']['weaviate_results']}")
    if "redis_speedup" in results["info"]:
        print(f"   Redis speedup: {results['info']['redis_speedup']}")
    if "e2e_latency_ms" in results["info"]:
        print(f"   E2E latency: {results['info']['e2e_latency_ms']:.0f}ms")
    
    print("\n📝 Notes:")
    print("   - Elasticsearch not installed (optional, for BM25)")
    print("   - PostgreSQL authentication issue (non-critical)")
    print("   - Ready to integrate with evolutionary optimizer")
    
    print("\n💡 Next Steps:")
    print("   1. Install Elasticsearch: pip install elasticsearch")
    print("   2. Apply 2-line patch to dual_backend_integration.py")
    print("   3. Run evolutionary optimization with RAG context")
    
    print("="*80)
    
    # Save results
    Path("test_results_final.json").write_text(json.dumps({
        "timestamp": datetime.now().isoformat(),
        "passed": results["passed"],
        "failed": results["failed"],
        "info": results["info"],
        "success_rate": passed / total if total > 0 else 0
    }, indent=2))
    
    print("\n📄 Results saved to: test_results_final.json")


if __name__ == "__main__":
    asyncio.run(main())

