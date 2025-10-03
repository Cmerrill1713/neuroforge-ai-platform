#!/usr/bin/env python3
"""
Optimized Model API - Large model inference with timeout management
Provides endpoints for optimized large model inference with streaming and session management
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from datetime import datetime
import json

from ..core.models.optimized_large_model import (
    optimized_large_model, 
    InferenceRequest, 
    ModelConfig,
    InferenceResponse
)

logger = logging.getLogger(__name__)

# Request/response models
class ModelInferenceRequest(BaseModel):
    """Model inference request"""
    prompt: str = Field(..., min_length=1, max_length=50000, description="Input prompt for inference")
    model_name: Optional[str] = Field(default=None, description="Specific model to use")
    max_tokens: Optional[int] = Field(default=None, ge=1, le=8192, description="Maximum tokens to generate")
    temperature: Optional[float] = Field(default=None, ge=0.0, le=2.0, description="Sampling temperature")
    stream: Optional[bool] = Field(default=True, description="Whether to stream the response")
    session_id: Optional[str] = Field(default=None, description="Session ID for conversation context")

class ModelStatusResponse(BaseModel):
    """Model status response"""
    status: str
    default_model: str
    active_sessions: int
    available_models: List[str]
    timestamp: str

class ModelConfigResponse(BaseModel):
    """Model configuration response"""
    model_name: str
    max_tokens: int
    temperature: float
    top_p: float
    timeout: int
    stream: bool
    context_length: int

class SessionManagementRequest(BaseModel):
    """Session management request"""
    session_id: str = Field(..., description="Session ID to manage")

# Create router
router = APIRouter(prefix="/api/model", tags=["Optimized Model"])

@router.post("/inference", response_model=InferenceResponse)
async def generate_inference(request: ModelInferenceRequest):
    """Generate inference using optimized large model"""
    try:
        logger.info(f"🔮 Model inference request: {request.model_name or 'default'}")
        
        # Ensure model is initialized
        if not optimized_large_model.model_status.value == "ready":
            await optimized_large_model.initialize()
        
        # Get model configuration
        model_name = request.model_name or optimized_large_model.default_model
        model_config = await optimized_large_model.get_model_config(model_name)
        
        if not model_config:
            # Create default config
            model_config = ModelConfig(
                name=model_name,
                max_tokens=request.max_tokens or 4096,
                temperature=request.temperature or 0.7,
                top_p=0.9,
                timeout=120,
                stream=request.stream or True,
                context_length=32768
            )
        
        # Override config with request parameters
        if request.max_tokens:
            model_config.max_tokens = request.max_tokens
        if request.temperature:
            model_config.temperature = request.temperature
        if request.stream is not None:
            model_config.stream = request.stream
        
        # Create inference request
        inference_request = InferenceRequest(
            prompt=request.prompt,
            model_config=model_config,
            session_id=request.session_id,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            stream=request.stream
        )
        
        # Generate response
        response = await optimized_large_model.generate_response(
            inference_request, 
            request.session_id
        )
        
        if response.success:
            logger.info(f"✅ Inference completed: {response.tokens_used} tokens in {response.processing_time:.2f}s")
        else:
            logger.warning(f"⚠️ Inference failed: {response.error}")
        
        return response
        
    except Exception as e:
        logger.error(f"Model inference failed: {e}")
        raise HTTPException(status_code=500, detail=f"Model inference failed: {str(e)}")

@router.post("/inference/stream")
async def generate_streaming_inference(request: ModelInferenceRequest):
    """Generate streaming inference response"""
    try:
        logger.info(f"🔮 Streaming inference request: {request.model_name or 'default'}")
        
        # Ensure model is initialized
        if not optimized_large_model.model_status.value == "ready":
            await optimized_large_model.initialize()
        
        # Get model configuration
        model_name = request.model_name or optimized_large_model.default_model
        model_config = await optimized_large_model.get_model_config(model_name)
        
        if not model_config:
            # Create default config
            model_config = ModelConfig(
                name=model_name,
                max_tokens=request.max_tokens or 4096,
                temperature=request.temperature or 0.7,
                top_p=0.9,
                timeout=120,
                stream=True,
                context_length=32768
            )
        
        # Override config with request parameters
        if request.max_tokens:
            model_config.max_tokens = request.max_tokens
        if request.temperature:
            model_config.temperature = request.temperature
        
        # Create inference request
        inference_request = InferenceRequest(
            prompt=request.prompt,
            model_config=model_config,
            session_id=request.session_id,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            stream=True  # Force streaming
        )
        
        # Create streaming response generator
        async def generate_stream():
            try:
                async for chunk in optimized_large_model.generate_streaming_response(inference_request):
                    yield f"data: {chunk}\n\n"
            except Exception as e:
                error_response = json.dumps({
                    "error": str(e),
                    "done": True
                })
                yield f"data: {error_response}\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
        
    except Exception as e:
        logger.error(f"Streaming inference failed: {e}")
        raise HTTPException(status_code=500, detail=f"Streaming inference failed: {str(e)}")

@router.get("/status", response_model=ModelStatusResponse)
async def get_model_status():
    """Get current model status"""
    try:
        status = await optimized_large_model.get_model_status()
        
        return ModelStatusResponse(
            status=status["status"],
            default_model=status["default_model"],
            active_sessions=status["active_sessions"],
            available_models=status["available_models"],
            timestamp=status["timestamp"]
        )
        
    except Exception as e:
        logger.error(f"Failed to get model status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get model status: {str(e)}")

@router.get("/config/{model_name}", response_model=ModelConfigResponse)
async def get_model_config(model_name: str):
    """Get configuration for a specific model"""
    try:
        config = await optimized_large_model.get_model_config(model_name)
        
        if not config:
            raise HTTPException(status_code=404, detail=f"Model {model_name} not found")
        
        return ModelConfigResponse(
            model_name=config.name,
            max_tokens=config.max_tokens,
            temperature=config.temperature,
            top_p=config.top_p,
            timeout=config.timeout,
            stream=config.stream,
            context_length=config.context_length
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get model config: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get model config: {str(e)}")

@router.post("/initialize")
async def initialize_model():
    """Manually initialize the model system"""
    try:
        logger.info("🚀 Manual model initialization")
        
        success = await optimized_large_model.initialize()
        
        if success:
            status = await optimized_large_model.get_model_status()
            return {
                "success": True,
                "message": "Model system initialized successfully",
                "status": status
            }
        else:
            return {
                "success": False,
                "message": "Failed to initialize model system",
                "status": optimized_large_model.model_status.value
            }
            
    except Exception as e:
        logger.error(f"Model initialization failed: {e}")
        raise HTTPException(status_code=500, detail=f"Model initialization failed: {str(e)}")

@router.post("/session/clear")
async def clear_session(request: SessionManagementRequest):
    """Clear a specific session"""
    try:
        await optimized_large_model.clear_session(request.session_id)
        
        return {
            "success": True,
            "message": f"Session {request.session_id} cleared",
            "session_id": request.session_id
        }
        
    except Exception as e:
        logger.error(f"Session clear failed: {e}")
        raise HTTPException(status_code=500, detail=f"Session clear failed: {str(e)}")

@router.post("/session/clear-all")
async def clear_all_sessions():
    """Clear all active sessions"""
    try:
        await optimized_large_model.clear_all_sessions()
        
        return {
            "success": True,
            "message": "All sessions cleared"
        }
        
    except Exception as e:
        logger.error(f"Clear all sessions failed: {e}")
        raise HTTPException(status_code=500, detail=f"Clear all sessions failed: {str(e)}")

@router.get("/health")
async def model_health_check():
    """Health check for the model system"""
    try:
        status = await optimized_large_model.get_model_status()
        
        is_healthy = status["status"] in ["ready", "idle"]
        
        return {
            "status": "healthy" if is_healthy else "degraded",
            "model_status": status["status"],
            "default_model": status["default_model"],
            "active_sessions": status["active_sessions"],
            "available_models": len(status["available_models"]),
            "timestamp": status["timestamp"]
        }
        
    except Exception as e:
        logger.error(f"Model health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/performance")
async def get_performance_metrics():
    """Get performance metrics for the model system"""
    try:
        status = await optimized_large_model.get_model_status()
        
        # Calculate performance metrics
        active_sessions = status["active_sessions"]
        available_models = len(status["available_models"])
        
        return {
            "model_status": status["status"],
            "active_sessions": active_sessions,
            "available_models": available_models,
            "session_utilization": f"{(active_sessions / 10) * 100:.1f}%" if active_sessions > 0 else "0%",
            "model_availability": "100%" if available_models > 0 else "0%",
            "timestamp": status["timestamp"]
        }
        
    except Exception as e:
        logger.error(f"Performance metrics failed: {e}")
        raise HTTPException(status_code=500, detail=f"Performance metrics failed: {str(e)}")

# Include the router in the main API
def include_optimized_model_routes(app):
    """Include optimized model routes in the FastAPI app"""
    app.include_router(router)
    logger.info("Optimized Model API routes included")
