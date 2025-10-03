#!/usr/bin/env python3
"""
LFM2 RAG API Server
Dedicated endpoint for Liquid AI LFM2-2.6B-RAG model for retrieval-augmented generation
"""

import asyncio
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import LFM2RAGModel from the project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from test_lfm2_rag_integration import LFM2RAGModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="LFM2 RAG API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RAGRequest(BaseModel):
    query: str
    context: str = ""
    max_length: int = 200
    temperature: float = 0.7

class RAGResponse(BaseModel):
    answer: str
    agent_used: str
    metadata: dict

# Global LFM2 RAG instance
lfm2_rag_model = None

@app.on_event("startup")
async def startup_event():
    """Initialize LFM2 RAG model on startup"""
    global lfm2_rag_model
    logger.info("🚀 Starting LFM2 RAG API Server")
    logger.info("🔄 Initializing LFM2 RAG model...")
    
    lfm2_rag_model = LFM2RAGModel()
    lfm2_rag_model.setup_device()
    
    if lfm2_rag_model.load_model():
        logger.info("✅ LFM2 RAG model ready!")
    else:
        logger.error("❌ Failed to load LFM2 RAG model")

@app.get("/")
async def root():
    return {"message": "LFM2 RAG API Server", "status": "running", "model": "LiquidAI/LFM2-1.2B-RAG"}

@app.get("/health")
async def health():
    return {
        "status": "running",
        "model": "LiquidAI/LFM2-1.2B-RAG",
        "loaded": lfm2_rag_model is not None and lfm2_rag_model.model is not None
    }

@app.post("/rag", response_model=RAGResponse)
async def rag_query(request: RAGRequest):
    """RAG query with LFM2 model"""
    if not lfm2_rag_model or not lfm2_rag_model.model:
        raise HTTPException(status_code=500, detail="LFM2 RAG model not loaded")
    
    try:
        logger.info(f"🔍 LFM2 RAG query: {request.query[:50]}...")
        
        response_text = lfm2_rag_model.generate_rag_response(
            request.query,
            context=request.context,
            max_length=request.max_length,
            temperature=request.temperature
        )
        
        logger.info(f"✅ LFM2 RAG response: {response_text[:50]}...")
        
        return RAGResponse(
            answer=response_text,
            agent_used="lfm2-rag",
            metadata={
                "model": "LiquidAI/LFM2-1.2B-RAG",
                "device": "cpu",
                "max_length": request.max_length,
                "temperature": request.temperature,
                "has_context": bool(request.context)
            }
        )
        
    except Exception as e:
        logger.error(f"❌ LFM2 RAG error: {e}")
        raise HTTPException(status_code=500, detail=f"LFM2 RAG generation failed: {e}")

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting LFM2 RAG API Server on PORT 8089")
    uvicorn.run(app, host="0.0.0.0", port=8089)
