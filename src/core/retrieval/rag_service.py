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
        weaviate_http_port: int = 8090,
        weaviate_grpc_port: int = 50051,
        weaviate_class: str = "KnowledgeDocumentBGE",  # ← Updated to BGE collection
        es_url: str = None,
        es_index: str = "docs",
        redis_url: str = None,
        embedder_model: str = "BAAI/bge-large-en-v1.5",  # ← Upgraded to BGE-Large model
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
            if embedder_model == "BAAI/bge-large-en-v1.5":
                # Use BGE-Large embedder (best performance)
                from sentence_transformers import SentenceTransformer
                self.embedder = SentenceTransformer(embedder_model)
                logger.info(f"✅ BGE-Large embedder loaded: {embedder_model}")
            elif "LFM2" in embedder_model:
                # LFM2 model requires special handling
                from transformers import AutoTokenizer, AutoModel
                import torch
                
                self.tokenizer = AutoTokenizer.from_pretrained(embedder_model)
                self.model = AutoModel.from_pretrained(embedder_model)
                
                # Set to evaluation mode
                self.model.eval()
                
                logger.info(f"✅ LFM2 RAG model loaded: {embedder_model}")
                logger.info(f"✅ LFM2 vocab size: {self.tokenizer.vocab_size}")
            else:
                # Standard sentence transformer
                from sentence_transformers import SentenceTransformer
                self.embedder = SentenceTransformer(embedder_model)
                logger.info(f"✅ SentenceTransformer loaded: {embedder_model}")
                
        except Exception as e:
            logger.warning(f"Failed to load embedder: {e}")
        
        logger.info("✅ Production RAG Service initialized")
    
    async def _embed_query(self, query: str) -> List[float]:
        """Generate query embedding (normalized) with caching"""
        if not self.embedder and not hasattr(self, 'model'):
            raise RuntimeError("No embedder or LFM2 model initialized")
        
        # Check for cached embedding first
        cached_embedding = None
        try:
            cached_embedding = await self.hybrid._get_cached_embedding(query)
        except Exception as e:
            logger.debug(f"Embedding cache check failed: {e}")
        
        if cached_embedding:
            logger.debug(f"✅ Using cached embedding for: {query[:50]}...")
            return cached_embedding
        
        # Generate new embedding
        if hasattr(self, 'model') and hasattr(self, 'tokenizer'):
            # LFM2 model embedding
            import torch
            import torch.nn.functional as F
            
            # Tokenize input
            inputs = self.tokenizer(query, return_tensors="pt", padding=True, truncation=True, max_length=512)
            
            # Generate embeddings
            with torch.no_grad():
                outputs = self.model(**inputs)
                # Use mean pooling of last hidden states
                embeddings = outputs.last_hidden_state.mean(dim=1)
                # Normalize embeddings
                embeddings = F.normalize(embeddings, p=2, dim=1)
                embedding_list = embeddings.squeeze().tolist()
        else:
            # Standard sentence transformer or Jina v4
            embedding = self.embedder.encode(
                query,
                normalize_embeddings=True,
                show_progress_bar=False
            )
            # Handle both numpy arrays and lists
            if hasattr(embedding, 'tolist'):
                embedding_list = embedding.tolist()
            else:
                embedding_list = embedding
        
        # Cache the embedding
        try:
            await self.hybrid._cache_embedding(query, embedding_list)
        except Exception as e:
            logger.debug(f"Embedding cache write failed: {e}")
        
        return embedding_list
    
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
        query_vector = await self._embed_query(query_text)
        
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
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get all system metrics with proper error handling"""
        try:
            # Get document count directly from Weaviate with better error handling
            if self.weaviate and hasattr(self.weaviate, 'connection_pool') and self.weaviate.connection_pool:
                try:
                    # Get a connection from the pool
                    client = await self.weaviate._get_connection()
                    collection = client.collections.get(self.weaviate.class_name)
                    weaviate_docs = collection.aggregate.over_all(total_count=True).total_count
                    await self.weaviate._return_connection(client)
                    logger.debug(f"✅ Retrieved Weaviate document count: {weaviate_docs}")
                except Exception as e:
                    logger.warning(f"Could not get Weaviate document count: {e}")
                    weaviate_docs = 0
            else:
                logger.warning("Weaviate connection pool not available")
                weaviate_docs = 0
        except Exception as e:
            logger.error(f"Failed to get Weaviate metrics: {e}")
            weaviate_docs = 0
            
        # Get hybrid metrics with error handling
        try:
            hybrid_metrics = self.hybrid.get_metrics()
        except Exception as e:
            logger.warning(f"Could not get hybrid metrics: {e}")
            hybrid_metrics = {}
            
        return {
            "weaviate_docs": weaviate_docs,
            "hybrid": hybrid_metrics,
            "embedder": self.embedder_model_name,
            "cache_hit_ratio": hybrid_metrics.get("cache_hit_ratio", 0.0),
            "avg_latency_ms": hybrid_metrics.get("avg_latency_ms", 0.0),
            "total_queries": hybrid_metrics.get("total_queries", 0),
            "status": "operational" if weaviate_docs > 0 else "degraded"
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
        "weaviate_http_port": int(os.getenv("WEAVIATE_HTTP", "8090")),
        "weaviate_grpc_port": int(os.getenv("WEAVIATE_GRPC", "50051")),
        "weaviate_class": os.getenv("WEAVIATE_CLASS", "KnowledgeDocumentBGE"),  # ← Updated to BGE
        "es_url": os.getenv("ELASTIC_URL", "http://elasticsearch:9200"),
        "es_index": os.getenv("ELASTIC_INDEX", "docs"),
        "redis_url": os.getenv("REDIS_URL", "redis://redis:6379/0"),
        "embedder_model": os.getenv("EMBEDDER_MODEL", "BAAI/bge-large-en-v1.5"),  # ← Upgraded to BGE-Large
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

