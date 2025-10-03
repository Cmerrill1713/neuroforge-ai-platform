#!/usr/bin/env python3
"""
MLX Chat API Server
Uses DIA-1.6B-MLX model for fast Apple Silicon acceleration
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

app = FastAPI(title="MLX Chat API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    max_length: int = 50
    temperature: float = 0.7

class ChatResponse(BaseModel):
    message: str
    agent_used: str
    metadata: dict

# Global MLX model instance
mlx_model = None

@app.on_event("startup")
async def startup_event():
    """Initialize MLX model on startup"""
    global mlx_model
    logger.info("🚀 Starting MLX Chat API Server")
    logger.info("🔄 Initializing DIA-1.6B-MLX model...")
    
    try:
        # Import MLX
        import mlx.core as mx
        import mlx.nn as nn
        from mlx_lm import load, generate
        
        # Load the DIA-1.6B-MLX model
        model_path = "./mlx_models/dia-1.6b-mlx"
        if os.path.exists(model_path):
            logger.info(f"📁 Loading MLX model from: {model_path}")
            model, tokenizer = load(model_path)
            mlx_model = {"model": model, "tokenizer": tokenizer}
            logger.info("✅ DIA-1.6B-MLX model loaded successfully!")
        else:
            logger.error(f"❌ Model path not found: {model_path}")
            mlx_model = None
            
    except Exception as e:
        logger.error(f"❌ Failed to load MLX model: {e}")
        mlx_model = None

@app.get("/")
async def root():
    return {"message": "MLX Chat API Server", "status": "running", "model": "DIA-1.6B-MLX"}

@app.get("/health")
async def health():
    return {
        "status": "running",
        "model": "DIA-1.6B-MLX",
        "loaded": mlx_model is not None
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with MLX model"""
    if not mlx_model:
        raise HTTPException(status_code=500, detail="MLX model not loaded")
    
    try:
        logger.info(f"🤖 MLX request: {request.message[:50]}...")
        
        # Generate response using MLX
        from mlx_lm import generate
        
        response_text = generate(
            mlx_model["model"],
            mlx_model["tokenizer"],
            prompt=request.message,
            max_tokens=request.max_length,
            temp=request.temperature,
            verbose=False
        )
        
        # Extract just the generated part (remove the prompt)
        if response_text.startswith(request.message):
            response_text = response_text[len(request.message):].strip()
        
        logger.info(f"✅ MLX response: {response_text[:50]}...")
        
        return ChatResponse(
            message=response_text,
            agent_used="dia-mlx",
            metadata={
                "model": "DIA-1.6B-MLX",
                "device": "mlx",
                "max_length": request.max_length,
                "temperature": request.temperature
            }
        )
        
    except Exception as e:
        logger.error(f"❌ MLX chat error: {e}")
        raise HTTPException(status_code=500, detail=f"MLX generation failed: {e}")

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting MLX Chat API Server on PORT 8088")
    uvicorn.run(app, host="0.0.0.0", port=8088)
