#!/usr/bin/env python3
"""
Production RAG Service
Unified interface for evolutionary optimizer

Stack:
- Weaviate: Vector search
- Elasticsearch: BM25/keyword search
- Redis: Caching
- PostgreSQL: Doc registry/metadata only (no vectors)
- Cross-encoder: Reranking
"""

import logging
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import asyncio

from .weaviate_store import WeaviateStore
from .hybrid_retriever import HybridRetriever
from .vector_store import QueryResult

logger = logging.getLogger(__name__)


@dataclass
class RAGResponse:
    """Standardized RAG response"""
    query: str
    results: List[QueryResult]
    latency_ms: float
    num_results: int
    retrieval_method: str  # "vector", "bm25", or "hybrid"
    metadata: Dict[str, Any]


class ProductionRAGService:
    """
    Production RAG service for evolutionary optimizer
    
    Single entry point for all retrieval operations.
    Handles embeddings, retrieval, and caching automatically.
    """
    
    def __init__(
        self,
        weaviate_host: str = None,
        weaviate_http_port: int = 8080,
        weaviate_grpc_port: int = 50051,
        weaviate_class: str = "KnowledgeDocument",  # ← Fixed to match your schema
        es_url: str = None,
        es_index: str = "docs",
        redis_url: str = None,
        embedder_model: str = "sentence-transformers/all-mpnet-base-v2",  # ← Fixed to 768-dim
        reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    ):
        # Vector store (Weaviate)
        self.weaviate = WeaviateStore(
            host=weaviate_host,
            http_port=weaviate_http_port,
            grpc_port=weaviate_grpc_port,
            class_name=weaviate_class
        )
        
        # Hybrid retriever (Weaviate + ES + Reranker)
        self.hybrid = HybridRetriever(
            vector_store=self.weaviate,
            es_url=es_url,
            es_index=es_index,
            redis_url=redis_url,
            reranker_model=reranker_model
        )
        
        # Embedder
        self.embedder_model_name = embedder_model
        self.embedder = None
        
        try:
            from sentence_transformers import SentenceTransformer
            self.embedder = SentenceTransformer(embedder_model)
            logger.info(f"✅ Embedder loaded: {embedder_model}")
        except Exception as e:
            logger.warning(f"Failed to load embedder: {e}")
        
        logger.info("✅ Production RAG Service initialized")
    
    def _embed_query(self, query: str) -> List[float]:
        """Generate query embedding (normalized)"""
        if not self.embedder:
            raise RuntimeError("Embedder not initialized")
        
        embedding = self.embedder.encode(
            query,
            normalize_embeddings=True,
            show_progress_bar=False
        )
        
        return embedding.tolist()
    
    async def query(
        self,
        query_text: str,
        k: int = 8,
        method: str = "hybrid",
        filters: Optional[Dict[str, Any]] = None,
        rerank: bool = True
    ) -> RAGResponse:
        """
        Query the RAG system
        
        Args:
            query_text: User query
            k: Number of results
            method: "hybrid", "vector", or "bm25"
            filters: Optional metadata filters (e.g., {"path": ["doctype"], "operator": "Equal", "valueText": "WI"})
            rerank: Whether to apply cross-encoder reranking
        
        Returns:
            RAGResponse with results and metadata
        """
        import time
        start = time.time()
        
        # Generate embedding
        query_vector = self._embed_query(query_text)
        
        # Retrieve
        if method == "hybrid":
            results = await self.hybrid.search(
                query_text=query_text,
                query_vector=query_vector,
                k=k,
                m=40,  # Retrieve more candidates for fusion
                filters=filters,
                rerank=rerank
            )
        elif method == "vector":
            results = await self.weaviate.query(
                embedding=query_vector,
                k=k,
                filters=filters
            )
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        latency_ms = (time.time() - start) * 1000
        
        return RAGResponse(
            query=query_text,
            results=results,
            latency_ms=latency_ms,
            num_results=len(results),
            retrieval_method=method,
            metadata={
                "embedder": self.embedder_model_name,
                "rerank": rerank,
                "filters": filters
            }
        )
    
    async def query_with_context(
        self,
        query_text: str,
        k: int = 5,
        method: str = "hybrid"
    ) -> str:
        """
        Query and format results as context for LLM
        
        Returns:
            Formatted context string ready to inject into prompt
        """
        response = await self.query(query_text, k=k, method=method)
        
        # Format as context
        context_parts = ["Retrieved Context:"]
        
        for i, result in enumerate(response.results, 1):
            doc_info = []
            if "doc_id" in result.metadata:
                doc_info.append(f"Doc: {result.metadata['doc_id']}")
            if "doctype" in result.metadata:
                doc_info.append(f"Type: {result.metadata['doctype']}")
            
            doc_str = " | ".join(doc_info) if doc_info else f"Result {i}"
            
            context_parts.append(f"\n[{doc_str}]")
            context_parts.append(result.text)
        
        return "\n".join(context_parts)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get all system metrics"""
        return {
            "weaviate": asyncio.run(self.weaviate.get_stats()),
            "hybrid": self.hybrid.get_metrics(),
            "embedder": self.embedder_model_name
        }
    
    async def close(self):
        """Close all connections"""
        self.weaviate.close()
        await self.hybrid.close()


# ============================================================================
# Factory for easy initialization
# ============================================================================

def create_rag_service(
    env: str = "production"
) -> ProductionRAGService:
    """
    Factory to create RAG service from environment
    
    Reads from env vars:
    - WEAVIATE_HOST (default: "weaviate")
    - WEAVIATE_HTTP (default: 8080)
    - WEAVIATE_GRPC (default: 50051)
    - ELASTIC_URL (default: "http://elasticsearch:9200")
    - REDIS_URL (default: "redis://redis:6379/0")
    
    Args:
        env: "production", "development", or "test"
    
    Returns:
        ProductionRAGService instance
    """
    
    # Production defaults
    config = {
        "weaviate_host": os.getenv("WEAVIATE_HOST", "weaviate"),
        "weaviate_http_port": int(os.getenv("WEAVIATE_HTTP", "8080")),
        "weaviate_grpc_port": int(os.getenv("WEAVIATE_GRPC", "50051")),
        "weaviate_class": os.getenv("WEAVIATE_CLASS", "KnowledgeDocument"),  # ← Fixed
        "es_url": os.getenv("ELASTIC_URL", "http://elasticsearch:9200"),
        "es_index": os.getenv("ELASTIC_INDEX", "docs"),
        "redis_url": os.getenv("REDIS_URL", "redis://redis:6379/0"),
        "embedder_model": os.getenv("EMBEDDER_MODEL", "sentence-transformers/all-mpnet-base-v2"),  # ← Fixed to 768-dim
        "reranker_model": os.getenv("RERANKER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")
    }
    
    # Override for dev/test
    if env == "development":
        config["weaviate_host"] = "localhost"
        config["weaviate_http_port"] = 8090  # ← Your actual port
        config["es_url"] = "http://localhost:9200"
        config["redis_url"] = "redis://localhost:6379/0"
    elif env == "test":
        # Use lighter models for testing
        config["embedder_model"] = "sentence-transformers/all-MiniLM-L6-v2"
        config["reranker_model"] = "cross-encoder/ms-marco-TinyBERT-L-2-v2"
    
    logger.info(f"🚀 Creating RAG service ({env} environment)")
    
    return ProductionRAGService(**config)

