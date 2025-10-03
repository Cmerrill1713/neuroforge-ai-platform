#!/usr/bin/env python3
"""
Hybrid Retrieval: Weaviate (ANN) + Elasticsearch (BM25) → RRF → Reranker

Production-grade hybrid search for your stack:
- Weaviate for vector similarity
- Elasticsearch for keyword/BM25
- RRF (Reciprocal Rank Fusion) to combine results
- Cross-encoder reranking for final ordering
- Redis caching for reranker outputs
"""

import logging
import os
import hashlib
import json
from typing import List, Dict, Any, Optional
import asyncio

try:
    from elasticsearch import Elasticsearch, AsyncElasticsearch
    ES_AVAILABLE = True
except ImportError:
    ES_AVAILABLE = False
    logging.warning("elasticsearch not installed: pip install elasticsearch")

try:
    from sentence_transformers import CrossEncoder
    RERANKER_AVAILABLE = True
except ImportError:
    RERANKER_AVAILABLE = False
    logging.warning("sentence-transformers not installed: pip install sentence-transformers")

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logging.warning("redis not installed: pip install redis")

from .vector_store import VectorStore, QueryResult

logger = logging.getLogger(__name__)


class HybridRetriever:
    """
    Hybrid retrieval combining dense (Weaviate) + sparse (ES) + reranking
    
    Pipeline:
    1. Query Weaviate for top-M vector results
    2. Query Elasticsearch for top-M BM25 results
    3. Fuse with RRF (Reciprocal Rank Fusion)
    4. Rerank fused results with cross-encoder
    5. Return top-K reranked results
    """
    
    def __init__(
        self,
        vector_store: VectorStore,
        es_url: str = None,
        es_index: str = "docs",
        redis_url: str = None,
        reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
        cache_ttl: int = 3600
    ):
        self.vector_store = vector_store
        
        # Elasticsearch
        self.es_url = es_url or os.getenv("ELASTIC_URL", "http://elasticsearch:9200")
        self.es_index = es_index
        self.es = None
        
        if ES_AVAILABLE:
            self.es = Elasticsearch(self.es_url, request_timeout=10)
            logger.info(f"✅ Elasticsearch connected: {self.es_url}")
        
        # Reranker
        self.reranker_model_name = reranker_model
        self.reranker = None
        
        if RERANKER_AVAILABLE:
            try:
                self.reranker = CrossEncoder(reranker_model, max_length=512)
                logger.info(f"✅ Reranker loaded: {reranker_model}")
            except Exception as e:
                logger.warning(f"Failed to load reranker: {e}")
        
        # Redis cache
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://redis:6379/0")
        self.redis = None
        self.cache_ttl = cache_ttl
        
        if REDIS_AVAILABLE:
            try:
                self.redis = redis.from_url(self.redis_url, decode_responses=True)
                logger.info(f"✅ Redis connected: {self.redis_url}")
            except Exception as e:
                logger.warning(f"Failed to connect to Redis: {e}")
        
        # Metrics
        self.metrics = {
            "total_queries": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "reranker_calls": 0,
            "avg_latency_ms": 0.0
        }
    
    def _rrf_fusion(
        self,
        vec_ids: List[str],
        bm25_ids: List[str],
        k: int = 60,
        c: int = 60
    ) -> List[str]:
        """
        Reciprocal Rank Fusion
        
        RRF score for document d = Σ 1/(k + rank_i(d))
        where rank_i(d) is the rank of d in retrieval system i
        
        Args:
            vec_ids: IDs from vector search (in rank order)
            bm25_ids: IDs from BM25 search (in rank order)
            k: Consider top-k from each system
            c: Constant (usually 60)
        
        Returns:
            Fused list of IDs sorted by RRF score
        """
        scores = {}
        
        # Add vector ranks
        for rank, doc_id in enumerate(vec_ids[:k]):
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (c + rank + 1)
        
        # Add BM25 ranks
        for rank, doc_id in enumerate(bm25_ids[:k]):
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (c + rank + 1)
        
        # Sort by score descending
        fused = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        return [doc_id for doc_id, score in fused]
    
    async def _get_cached_rerank_scores(self, query: str, doc_ids: List[str]) -> Optional[Dict[str, float]]:
        """Get reranking scores from cache"""
        if not self.redis:
            return None
        
        try:
            # Create cache key from query + doc_ids
            key_input = f"{query}:{':'.join(sorted(doc_ids))}"
            cache_key = f"rerank:{hashlib.sha256(key_input.encode()).hexdigest()}"
            
            cached = await self.redis.get(cache_key)
            if cached:
                self.metrics["cache_hits"] += 1
                return json.loads(cached)
            
            self.metrics["cache_misses"] += 1
            return None
            
        except Exception as e:
            logger.debug(f"Cache read failed: {e}")
            return None
    
    async def _cache_rerank_scores(self, query: str, doc_ids: List[str], scores: Dict[str, float]):
        """Cache reranking scores"""
        if not self.redis:
            return
        
        try:
            key_input = f"{query}:{':'.join(sorted(doc_ids))}"
            cache_key = f"rerank:{hashlib.sha256(key_input.encode()).hexdigest()}"
            
            await self.redis.setex(
                cache_key,
                self.cache_ttl,
                json.dumps(scores)
            )
        except Exception as e:
            logger.debug(f"Cache write failed: {e}")
    
    async def search(
        self,
        query_text: str,
        query_vector: List[float],
        k: int = 8,
        m: int = 40,
        filters: Optional[Dict[str, Any]] = None,
        rerank: bool = True
    ) -> List[QueryResult]:
        """
        Hybrid search with optional reranking
        
        Args:
            query_text: Text query for BM25
            query_vector: Embedding for vector search
            k: Final number of results to return
            m: Number of candidates to retrieve from each source (before fusion)
            filters: Optional metadata filters
            rerank: Whether to apply cross-encoder reranking
        
        Returns:
            Top-k results after fusion and optional reranking
        """
        import time
        start = time.time()
        
        self.metrics["total_queries"] += 1
        
        # 1. Vector search (Weaviate)
        vec_results = await self.vector_store.query(
            embedding=query_vector,
            k=m,
            filters=filters
        )
        vec_ids = [r.id for r in vec_results]
        
        # 2. BM25 search (Elasticsearch)
        bm25_ids = []
        bm25_results = {}
        
        if self.es and ES_AVAILABLE:
            try:
                # Build ES query
                es_query = {
                    "match": {
                        "text": {
                            "query": query_text,
                            "operator": "or"
                        }
                    }
                }
                
                # Add filters if provided
                if filters:
                    es_query = {
                        "bool": {
                            "must": es_query,
                            "filter": self._convert_filters_to_es(filters)
                        }
                    }
                
                # Execute search
                response = self.es.search(
                    index=self.es_index,
                    size=m,
                    query=es_query,
                    _source=["text", "doc_id", "rev", "doctype", "date", "program", "supplier"]
                )
                
                # Extract results
                for hit in response["hits"]["hits"]:
                    bm25_ids.append(hit["_id"])
                    bm25_results[hit["_id"]] = {
                        "text": hit["_source"].get("text", ""),
                        "metadata": hit["_source"],
                        "score": hit["_score"]
                    }
                
                logger.debug(f"ES returned {len(bm25_ids)} results")
                
            except Exception as e:
                logger.warning(f"Elasticsearch query failed: {e}")
        
        # 3. RRF Fusion
        fused_ids = self._rrf_fusion(vec_ids, bm25_ids, k=m)
        
        # Build ID → text mapping
        id_to_data = {}
        
        # Add vector results
        for r in vec_results:
            id_to_data[r.id] = {
                "text": r.text,
                "metadata": r.metadata,
                "vec_score": r.score
            }
        
        # Add BM25 results
        for doc_id, data in bm25_results.items():
            if doc_id not in id_to_data:
                id_to_data[doc_id] = {
                    "text": data["text"],
                    "metadata": data["metadata"],
                    "vec_score": 0.0
                }
            else:
                # Has both vector and BM25 scores
                id_to_data[doc_id]["bm25_score"] = data["score"]
        
        # 4. Reranking (optional)
        if rerank and self.reranker and len(fused_ids) > 0:
            # Check cache
            cached_scores = await self._get_cached_rerank_scores(query_text, fused_ids[:m])
            
            if cached_scores:
                # Use cached scores
                rerank_scores = cached_scores
            else:
                # Rerank with cross-encoder
                self.metrics["reranker_calls"] += 1
                
                pairs = [
                    [query_text, id_to_data[doc_id]["text"]]
                    for doc_id in fused_ids[:m]
                    if doc_id in id_to_data
                ]
                
                scores = self.reranker.predict(pairs)
                
                rerank_scores = {
                    fused_ids[i]: float(scores[i])
                    for i in range(len(scores))
                    if fused_ids[i] in id_to_data
                }
                
                # Cache scores
                await self._cache_rerank_scores(query_text, list(rerank_scores.keys()), rerank_scores)
            
            # Sort by rerank score
            ranked_ids = sorted(
                rerank_scores.keys(),
                key=lambda x: rerank_scores[x],
                reverse=True
            )[:k]
            
            final_results = []
            for doc_id in ranked_ids:
                if doc_id in id_to_data:
                    data = id_to_data[doc_id]
                    final_results.append(QueryResult(
                        id=doc_id,
                        text=data["text"],
                        score=rerank_scores[doc_id],
                        metadata={
                            **data["metadata"],
                            "rerank_score": rerank_scores[doc_id],
                            "vec_score": data.get("vec_score", 0.0),
                            "bm25_score": data.get("bm25_score", 0.0),
                            "retrieval": "hybrid_reranked"
                        }
                    ))
        else:
            # No reranking - use RRF scores
            final_results = []
            for doc_id in fused_ids[:k]:
                if doc_id in id_to_data:
                    data = id_to_data[doc_id]
                    final_results.append(QueryResult(
                        id=doc_id,
                        text=data["text"],
                        score=data.get("vec_score", 0.5),  # Use vector score as proxy
                        metadata={
                            **data["metadata"],
                            "vec_score": data.get("vec_score", 0.0),
                            "bm25_score": data.get("bm25_score", 0.0),
                            "retrieval": "hybrid_rrf"
                        }
                    ))
        
        # Update metrics
        latency_ms = (time.time() - start) * 1000
        n = self.metrics["total_queries"]
        self.metrics["avg_latency_ms"] = (
            (self.metrics["avg_latency_ms"] * (n - 1) + latency_ms) / n
        )
        
        logger.info(
            f"✅ Hybrid search: {len(vec_results)} vec + {len(bm25_ids)} bm25 "
            f"→ {len(final_results)} final ({latency_ms:.0f}ms)"
        )
        
        return final_results
    
    def _convert_filters_to_es(self, weaviate_filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Convert Weaviate filters to Elasticsearch filters"""
        # Simple conversion - expand as needed
        es_filters = []
        
        if "path" in weaviate_filters:
            path = weaviate_filters["path"]
            op = weaviate_filters.get("operator", "Equal")
            value = weaviate_filters.get("valueText") or weaviate_filters.get("valueString")
            
            if op == "Equal":
                es_filters.append({
                    "term": {path[0]: value}
                })
        
        return es_filters
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get retrieval metrics"""
        metrics = {**self.metrics}
        
        # Add cache hit ratio
        total_cache_requests = metrics["cache_hits"] + metrics["cache_misses"]
        if total_cache_requests > 0:
            metrics["cache_hit_ratio"] = metrics["cache_hits"] / total_cache_requests
        else:
            metrics["cache_hit_ratio"] = 0.0
        
        return metrics
    
    async def close(self):
        """Close connections"""
        if self.redis:
            await self.redis.close()
        if self.es:
            await self.es.close()

