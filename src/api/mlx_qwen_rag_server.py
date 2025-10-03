#!/usr/bin/env python3
"""
MLX Qwen RAG API Server
Uses qwen3-30b-mlx-4bit for RAG with MLX acceleration
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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="MLX Qwen RAG API", version="1.0.0")

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

# Global MLX model instance
mlx_model = None
mlx_tokenizer = None

@app.on_event("startup")
async def startup_event():
    """Initialize MLX Qwen model on startup"""
    global mlx_model, mlx_tokenizer
    logger.info("🚀 Starting MLX Qwen RAG API Server")
    logger.info("🔄 Initializing Qwen3-30B-MLX model...")
    
    try:
        # Import MLX-LM
        from mlx_lm import load, generate
        
        # Load the MLX Qwen model
        model_path = "./mlx_models/qwen3-30b-mlx-4bit"
        if os.path.exists(model_path):
            logger.info(f"📁 Loading MLX Qwen model from: {model_path}")
            mlx_model, mlx_tokenizer = load(model_path)
        else:
            # Try loading from Hugging Face if local doesn't exist
            logger.info("📁 Loading MLX Qwen model from Hugging Face...")
            mlx_model, mlx_tokenizer = load("Qwen/Qwen2.5-32B-Instruct")
        
        logger.info("✅ Qwen3-30B-MLX model loaded successfully!")
        logger.info(f"🔤 Tokenizer vocab size: {len(mlx_tokenizer)}")
        
    except Exception as e:
        logger.error(f"❌ Failed to load MLX Qwen model: {e}")
        mlx_model = None
        mlx_tokenizer = None

@app.get("/")
async def root():
    return {"message": "MLX Qwen RAG API Server", "status": "running", "model": "Qwen3-30B-MLX"}

@app.get("/health")
async def health():
    return {
        "status": "running",
        "model": "Qwen3-30B-MLX",
        "loaded": mlx_model is not None and mlx_tokenizer is not None
    }

@app.post("/rag", response_model=RAGResponse)
async def rag_query(request: RAGRequest):
    """RAG query with MLX Qwen model"""
    if not mlx_model or not mlx_tokenizer:
        raise HTTPException(status_code=500, detail="MLX Qwen model not loaded")
    
    try:
        logger.info(f"🔍 MLX Qwen RAG query: {request.query[:50]}...")
        
        # Import generate function
        from mlx_lm import generate
        
        # Create RAG prompt
        if request.context:
            prompt = f"""Context: {request.context}

Question: {request.query}

Answer:"""
        else:
            prompt = f"""Question: {request.query}

Answer:"""
        }
        
        # Generate response using MLX
        response_text = generate(
            mlx_model, 
            mlx_tokenizer, 
            prompt=prompt, 
            max_tokens=request.max_length,
            temp=request.temperature,
            verbose=False
        )
        
        # Extract just the generated part
        if response_text.startswith(prompt):
            response_text = response_text[len(prompt):].strip()
        
        logger.info(f"✅ MLX Qwen RAG response: {response_text[:50]}...")
        
        return RAGResponse(
            answer=response_text,
            agent_used="qwen-mlx",
            metadata={
                "model": "Qwen3-30B-MLX",
                "device": "mlx",
                "max_length": request.max_length,
                "temperature": request.temperature,
                "has_context": bool(request.context)
            }
        )
        
    except Exception as e:
        logger.error(f"❌ MLX Qwen RAG error: {e}")
        raise HTTPException(status_code=500, detail=f"MLX Qwen RAG failed: {e}")

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting MLX Qwen RAG API Server on PORT 8089")
    uvicorn.run(app, host="0.0.0.0", port=8089)
