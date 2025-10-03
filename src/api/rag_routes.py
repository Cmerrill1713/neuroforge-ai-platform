#!/usr/bin/env python3
"""
RAG System API Routes
FastAPI endpoints for the frontend RAG Search panel
"""

import logging
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Router
router = APIRouter(prefix="/api/rag", tags=["rag"])

# Global state (will be initialized on app startup)
rag_service = None


class RAGQueryRequest(BaseModel):
    """RAG query request"""
    query_text: str = Field(..., min_length=1, max_length=1000)
    k: int = Field(default=5, ge=1, le=20)
    method: str = Field(default="hybrid")  # "vector", "bm25", "hybrid"
    rerank: bool = Field(default=True)
    filters: Optional[Dict[str, Any]] = None


class RAGResult(BaseModel):
    """Single RAG result"""
    id: str
    text: str
    score: float
    metadata: Dict[str, Any]


class RAGQueryResponse(BaseModel):
    """RAG query response"""
    query: str
    results: List[RAGResult]
    latency_ms: float
    num_results: int
    retrieval_method: str
    cache_hit: bool = False


def set_rag_service(service):
    """Set the global RAG service instance"""
    global rag_service
    rag_service = service


@router.post("/query", response_model=RAGQueryResponse)
async def query_rag(request: RAGQueryRequest) -> RAGQueryResponse:
    """
    Query the RAG system with hybrid retrieval
    
    Returns:
        Ranked results with relevance scores and metadata
    """
    if not rag_service:
        raise HTTPException(status_code=503, detail="RAG service not initialized")
    
    try:
        logger.info(f"🔍 RAG query: '{request.query_text}' (k={request.k}, method={request.method})")
        
        # Execute query
        response = await rag_service.query(
            query_text=request.query_text,
            k=request.k,
            method=request.method,
            filters=request.filters,
            rerank=request.rerank
        )
        
        # Format results
        results = [
            RAGResult(
                id=r.id,
                text=r.text,
                score=r.score,
                metadata=r.metadata
            )
            for r in response.results
        ]
        
        # Check if cached (from metadata)
        cache_hit = any(
            "retrieval" in r.metadata and "cached" in r.metadata.get("retrieval", "")
            for r in response.results
        )
        
        logger.info(f"✅ RAG query complete: {response.num_results} results in {response.latency_ms:.0f}ms")
        
        return RAGQueryResponse(
            query=response.query,
            results=results,
            latency_ms=response.latency_ms,
            num_results=response.num_results,
            retrieval_method=response.retrieval_method,
            cache_hit=cache_hit
        )
        
    except Exception as e:
        logger.error(f"RAG query failed: {e}")
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@router.get("/metrics")
async def get_rag_metrics() -> Dict[str, Any]:
    """
    Get RAG system performance metrics
    
    Returns:
        - cache_hit_ratio: Percentage of cached queries
        - avg_latency_ms: Average query latency
        - total_queries: Total queries processed
        - weaviate_docs: Total documents indexed
    """
    if not rag_service:
        return {
            "cache_hit_ratio": 0.0,
            "avg_latency_ms": 0.0,
            "total_queries": 0,
            "weaviate_docs": 0,
            "status": "not_initialized"
        }
    
    try:
        metrics = await rag_service.get_metrics()
        
        # Extract key metrics
        hybrid_metrics = metrics.get("hybrid", {})
        weaviate_metrics = metrics.get("weaviate", {})
        
        return {
            "cache_hit_ratio": hybrid_metrics.get("cache_hit_ratio", 0.0),
            "avg_latency_ms": hybrid_metrics.get("avg_latency_ms", 0.0),
            "total_queries": hybrid_metrics.get("total_queries", 0),
            "weaviate_docs": metrics.get("weaviate_docs", 0),  # Fixed: use direct weaviate_docs
            "embedder": metrics.get("embedder", "unknown"),
            "status": "operational"
        }
        
    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        return {
            "cache_hit_ratio": 0.0,
            "avg_latency_ms": 0.0,
            "total_queries": 0,
            "weaviate_docs": 0,
            "error": str(e)
        }


@router.get("/stats")
async def get_rag_stats() -> Dict[str, Any]:
    """Get detailed RAG system statistics"""
    if not rag_service:
        return {"status": "not_initialized"}
    
    try:
        return rag_service.get_metrics()
    except Exception as e:
        logger.error(f"Failed to get RAG stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query/context")
async def query_with_context(request: RAGQueryRequest) -> Dict[str, Any]:
    """
    Query RAG and return formatted context for LLM
    
    Returns:
        - context: Formatted string ready to inject into prompt
        - results: Raw results for reference
    """
    if not rag_service:
        raise HTTPException(status_code=503, detail="RAG service not initialized")
    
    try:
        context = await rag_service.query_with_context(
            query_text=request.query_text,
            k=request.k,
            method=request.method
        )
        
        response = await rag_service.query(
            query_text=request.query_text,
            k=request.k,
            method=request.method
        )
        
        return {
            "context": context,
            "results": [
                {
                    "id": r.id,
                    "text": r.text,
                    "score": r.score,
                    "metadata": r.metadata
                }
                for r in response.results
            ],
            "num_results": len(response.results)
        }
        
    except Exception as e:
        logger.error(f"Context query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

