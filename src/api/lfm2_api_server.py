#!/usr/bin/env python3
"""
LFM2 API Endpoint
Dedicated endpoint for Liquid AI LFM2-1.2B-RAG model
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

# Import LFM2Model from the project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from test_lfm2_integration import LFM2Model

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="LFM2 API", version="1.0.0")

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
    max_length: int = 20  # Much smaller for speed
    temperature: float = 0.7

class ChatResponse(BaseModel):
    message: str
    agent_used: str
    metadata: dict

# Global LFM2 instance
lfm2_model = None

@app.on_event("startup")
async def startup_event():
    """Initialize LFM2 model on startup"""
    global lfm2_model
    logger.info("🚀 Starting LFM2 API Server")
    logger.info("🔄 Initializing LFM2 model...")
    
    lfm2_model = LFM2Model()
    lfm2_model.setup_device()
    
    if lfm2_model.load_model():
        logger.info("✅ LFM2 model ready!")
    else:
        logger.error("❌ Failed to load LFM2 model")

@app.get("/")
async def root():
    return {"message": "LFM2 API Server", "status": "running", "model": "LiquidAI/LFM2-2.6B"}

@app.get("/health")
async def health():
    return {
        "status": "running",
        "model": "LiquidAI/LFM2-2.6B",
        "loaded": lfm2_model is not None and lfm2_model.model is not None
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with LFM2 model"""
    if not lfm2_model or not lfm2_model.model:
        raise HTTPException(status_code=500, detail="LFM2 model not loaded")
    
    try:
        logger.info(f"🤖 LFM2 request: {request.message[:50]}...")
        
        response_text = lfm2_model.generate_response(
            request.message,
            max_length=request.max_length,
            temperature=request.temperature
        )
        
        logger.info(f"✅ LFM2 response: {response_text[:50]}...")
        
        return ChatResponse(
            message=response_text,
            agent_used="lfm2",
            metadata={
                "model": "LiquidAI/LFM2-2.6B",
                "device": "cpu",
                "max_length": request.max_length,
                "temperature": request.temperature
            }
        )
        
    except Exception as e:
        logger.error(f"❌ LFM2 chat error: {e}")
        raise HTTPException(status_code=500, detail=f"LFM2 generation failed: {e}")

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting LFM2 API Server on PORT 8088")
    uvicorn.run(app, host="0.0.0.0", port=8088)
