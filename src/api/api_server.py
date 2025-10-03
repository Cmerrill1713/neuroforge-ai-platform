#!/usr/bin/env python3
"""
FastAPI Web Server for Agentic LLM Core
Provides REST API and WebSocket endpoints for frontend integration
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import uuid

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

try:
    from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import HTMLResponse
    from pydantic import BaseModel

    # Import core modules
    from src.core.security.sanitizer import sanitize_user_text
    from src.core.assessment.response_reviewer import evaluate_response
    from src.core.assessment.response_judge import judge_response
    from src.core.logging.event_tracker import log_event
    from src.core.engines.local_model_manager import model_manager, ModelType, LocalModelConfig
except ImportError as e:
    print(f"❌ Missing dependencies: {e}")
    print("Install with: pip install fastapi uvicorn websockets aiohttp")
    sys.exit(1)

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Pydantic models for API
class ChatRequest(BaseModel):
    """Chat request model"""
    request_id: str = str(uuid.uuid4())
    message: str
    model: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    """Chat response model"""
    request_id: str
    response: str
    model_used: str
    processing_time: float
    status: str = "success"

class ModelConfigRequest(BaseModel):
    """Model configuration request"""
    name: str
    model_type: str  # "ollama", "mlx", "qwen"
    model_name: str
    base_url: Optional[str] = None
    model_path: Optional[str] = None

class ModelInfo(BaseModel):
    """Model information"""
    name: str
    type: str
    model_name: str
    status: str
    details: Optional[Dict[str, Any]] = None

# Initialize default models on startup using lifespan events
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI"""
    # Startup
    try:
        registered = model_manager.initialize_default_models()
        logger.info(f"Initialized {registered} default models on startup")
    except Exception as e:
        logger.warning(f"Failed to initialize default models: {e}")

    yield

    # Shutdown
    logger.info("Shutting down NeuroForge API")

# FastAPI app
app = FastAPI(
    title="NeuroForge API",
    description="AI Development Platform API with Local Model Support",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Model management endpoints
@app.get("/api/models", response_model=List[ModelInfo])
async def list_models():
    """List all registered models"""
    models = []
    for model_name in model_manager.list_available_models():
        health = model_manager.check_model_health(model_name)
        info = model_manager.get_model_info(model_name)
        models.append(ModelInfo(
            name=model_name,
            type=info.get("type", "unknown") if info else "unknown",
            model_name=info.get("model_name", model_name) if info else model_name,
            status=health.get("status", "unknown"),
            details=info
        ))
    return models

@app.post("/api/models/register")
async def register_model(config: ModelConfigRequest):
    """Register a new local model"""
    try:
        # Convert string type to enum
        model_type_map = {
            "ollama": ModelType.OLLAMA,
            "mlx": ModelType.MLX,
            "qwen": ModelType.QWEN
        }

        if config.model_type not in model_type_map:
            raise HTTPException(status_code=400, detail=f"Unsupported model type: {config.model_type}")

        model_config = LocalModelConfig(
            name=config.name,
            model_type=model_type_map[config.model_type],
            model_name=config.model_name,
            base_url=config.base_url,
            model_path=config.model_path
        )

        success = model_manager.register_model(model_config)
        if success:
            return {"message": f"Model {config.name} registered successfully"}
        else:
            raise HTTPException(status_code=500, detail=f"Failed to register model {config.name}")

    except Exception as e:
        logger.error(f"Model registration failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/models/switch/{model_name}")
async def switch_model(model_name: str):
    """Switch to a different model"""
    success = model_manager.switch_model(model_name)
    if success:
        return {"message": f"Switched to model: {model_name}"}
    else:
        raise HTTPException(status_code=404, detail=f"Model not found: {model_name}")

@app.get("/api/models/current")
async def get_current_model():
    """Get information about the current model"""
    info = model_manager.get_model_info(model_manager.current_model)
    if info:
        return info
    else:
        return {"message": "No model selected"}

# Chat endpoint
@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Process chat request with local AI models"""
    try:
        start_time = datetime.now()

        # Sanitize input
        sanitized = sanitize_user_text(request.message)

        # Log event
        await log_event({
            "event_type": "chat_request",
            "request_id": request.request_id,
            "message_length": len(request.message),
            "model": request.model,
            "timestamp": start_time.isoformat()
        })

        # Generate response using local model
        try:
            # Prepare messages for chat
            messages = [
                {"role": "user", "content": sanitized.text}
            ]

            # Use specified model or current model
            response_text = await model_manager.chat(
                messages=messages,
                model_name=request.model
            )

            # Get model info for response
            model_info = model_manager.get_model_info(request.model)
            model_used = model_info.get("name", "unknown") if model_info else "unknown"

        except Exception as model_error:
            logger.warning(f"Model generation failed: {model_error}, falling back to echo")
            response_text = f"Echo: {sanitized.text}"
            model_used = "echo_fallback"

        processing_time = (datetime.now() - start_time).total_seconds()

        return ChatResponse(
            request_id=request.request_id,
            response=response_text,
            model_used=model_used,
            processing_time=processing_time
        )

    except Exception as e:
        logger.error(f"Error processing chat request: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# WebSocket endpoint
@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time chat"""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # Echo back for now
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

