#!/usr/bin/env python3
"""
MLX RAG API Server
Provides MLX-powered RAG endpoints for Apple GPU acceleration
"""

import logging
import asyncio
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

from src.core.retrieval.mlx_rag_service import get_mlx_rag_service

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="MLX RAG API",
    description="MLX-powered RAG service for Apple GPU acceleration",
    version="1.0.0"
)

# Global MLX RAG service
mlx_rag_service = None

class RAGRequest(BaseModel):
    """RAG request model"""
    query: str
    context: Optional[str] = ""
    max_tokens: Optional[int] = 256
    temperature: Optional[float] = 0.3

class RAGResponse(BaseModel):
    """RAG response model"""
    response: str
    model_used: str
    generation_time_ms: float
    device: str
    metadata: Dict[str, Any]

@app.on_event("startup")
async def startup_event():
    """Initialize MLX RAG service on startup"""
    global mlx_rag_service
    logger.info("🚀 Starting MLX RAG API Server")
    
    try:
        mlx_rag_service = get_mlx_rag_service()
        if mlx_rag_service.load_model():
            logger.info("✅ MLX RAG service initialized successfully")
        else:
            logger.error("❌ Failed to initialize MLX RAG service")
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "MLX RAG API",
        "version": "1.0.0",
        "status": "running",
        "device": str(mlx_rag_service.get_model_info()["device"]) if mlx_rag_service else "unknown"
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    if not mlx_rag_service or not mlx_rag_service.loaded:
        raise HTTPException(status_code=503, detail="MLX RAG service not available")
    
    return {
        "status": "healthy",
        "model_loaded": mlx_rag_service.loaded,
        "device": mlx_rag_service.get_model_info()["device"]
    }

@app.post("/rag/query", response_model=RAGResponse)
async def rag_query(request: RAGRequest):
    """MLX RAG query endpoint"""
    if not mlx_rag_service or not mlx_rag_service.loaded:
        raise HTTPException(status_code=503, detail="MLX RAG service not available")
    
    try:
        import time
        start_time = time.time()
        
        logger.info(f"🔍 MLX RAG query: {request.query[:50]}...")
        
        # Generate response
        response = mlx_rag_service.generate_response(
            query=request.query,
            context=request.context or "",
            max_tokens=request.max_tokens
        )
        
        generation_time = (time.time() - start_time) * 1000
        model_info = mlx_rag_service.get_model_info()
        
        logger.info(f"✅ MLX RAG response generated in {generation_time:.0f}ms")
        
        return RAGResponse(
            response=response,
            model_used=model_info["model_type"],
            generation_time_ms=generation_time,
            device=model_info["device"],
            metadata={
                "framework": "mlx",
                "quantization": "4-bit",
                "context_provided": bool(request.context)
            }
        )
        
    except Exception as e:
        logger.error(f"❌ MLX RAG query failed: {e}")
        raise HTTPException(status_code=500, detail=f"RAG query failed: {str(e)}")

@app.get("/rag/info")
async def rag_info():
    """Get RAG service information"""
    if not mlx_rag_service:
        raise HTTPException(status_code=503, detail="MLX RAG service not available")
    
    return mlx_rag_service.get_model_info()

@app.post("/rag/test")
async def test_rag():
    """Test RAG service"""
    if not mlx_rag_service or not mlx_rag_service.loaded:
        raise HTTPException(status_code=503, detail="MLX RAG service not available")
    
    try:
        test_query = "What is machine learning?"
        response = mlx_rag_service.generate_response(test_query, max_tokens=100)
        
        return {
            "test_query": test_query,
            "response": response,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"❌ RAG test failed: {e}")
        raise HTTPException(status_code=500, detail=f"RAG test failed: {str(e)}")

if __name__ == "__main__":
    logger.info("🚀 Starting MLX RAG API Server on port 8006")
    uvicorn.run(app, host="0.0.0.0", port=8006)
