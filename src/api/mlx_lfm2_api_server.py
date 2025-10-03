#!/usr/bin/env python3
"""
MLX LFM2 API Server - Correct Implementation
Uses nightmedia/LFM2-2.6B-bf16-mlx directly from Hugging Face
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

app = FastAPI(title="MLX LFM2 API", version="1.0.0")

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
mlx_tokenizer = None

@app.on_event("startup")
async def startup_event():
    """Initialize MLX LFM2 model on startup"""
    global mlx_model, mlx_tokenizer
    logger.info("🚀 Starting MLX LFM2 API Server")
    logger.info("🔄 Initializing LFM2-2.6B-MLX model...")
    
    try:
        # Import MLX-LM
        from mlx_lm import load, generate
        
        # Load the MLX LFM2 model directly from Hugging Face
        model_id = "nightmedia/LFM2-2.6B-bf16-mlx"
        logger.info(f"📁 Loading MLX LFM2 model: {model_id}")
        
        mlx_model, mlx_tokenizer = load(model_id)
        
        logger.info("✅ LFM2-2.6B-MLX model loaded successfully!")
        logger.info(f"🔤 Tokenizer vocab size: {len(mlx_tokenizer)}")
        
    except Exception as e:
        logger.error(f"❌ Failed to load MLX LFM2 model: {e}")
        mlx_model = None
        mlx_tokenizer = None

@app.get("/")
async def root():
    return {"message": "MLX LFM2 API Server", "status": "running", "model": "LFM2-2.6B-MLX"}

@app.get("/health")
async def health():
    return {
        "status": "running",
        "model": "LFM2-2.6B-MLX",
        "loaded": mlx_model is not None and mlx_tokenizer is not None
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with MLX LFM2 model"""
    if not mlx_model or not mlx_tokenizer:
        raise HTTPException(status_code=500, detail="MLX LFM2 model not loaded")
    
    try:
        logger.info(f"🤖 MLX LFM2 request: {request.message[:50]}...")
        
        # Import generate function
        from mlx_lm import generate
        
        # Prepare prompt with chat template if available
        prompt = request.message
        if mlx_tokenizer.chat_template is not None:
            messages = [{"role": "user", "content": request.message}]
            prompt = mlx_tokenizer.apply_chat_template(
                messages, add_generation_prompt=True
            )
        
        # Generate response using MLX
        response_text = generate(
            mlx_model, 
            mlx_tokenizer, 
            prompt=prompt, 
            max_tokens=request.max_length,
            temp=request.temperature,
            verbose=False
        )
        
        # Extract just the generated part (remove the prompt)
        if response_text.startswith(prompt):
            response_text = response_text[len(prompt):].strip()
        
        logger.info(f"✅ MLX LFM2 response: {response_text[:50]}...")
        
        return ChatResponse(
            message=response_text,
            agent_used="lfm2-mlx",
            metadata={
                "model": "LFM2-2.6B-MLX",
                "device": "mlx",
                "max_length": request.max_length,
                "temperature": request.temperature,
                "chat_template_used": mlx_tokenizer.chat_template is not None
            }
        )
        
    except Exception as e:
        logger.error(f"❌ MLX LFM2 chat error: {e}")
        raise HTTPException(status_code=500, detail=f"MLX LFM2 generation failed: {e}")

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting MLX LFM2 API Server on PORT 8088")
    uvicorn.run(app, host="0.0.0.0", port=8088)