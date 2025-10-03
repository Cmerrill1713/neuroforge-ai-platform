#!/usr/bin/env python3
"""
MLX API - Real MLX processing endpoints
Provides endpoints for real MLX inference instead of simulations
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime
import json

from ..core.mlx.real_mlx_processor import (
    real_mlx_processor,
    MLXRequest,
    MLXConfig,
    MLXResponse
)

logger = logging.getLogger(__name__)

# Request/response models
class MLXProcessingRequest(BaseModel):
    """MLX processing request"""
    text: str = Field(..., min_length=1, max_length=10000, description="Input text to process")
    operation: str = Field(..., description="Processing operation: generate, embed, classify")
    model_name: Optional[str] = Field(default=None, description="Specific model to use")
    device: Optional[str] = Field(default="mps", description="Processing device: cpu, gpu, mps")
    precision: Optional[str] = Field(default="float16", description="Precision: float16, float32")
    max_tokens: Optional[int] = Field(default=None, description="Maximum tokens for generation")
    temperature: Optional[float] = Field(default=0.7, description="Sampling temperature")
    batch_size: Optional[int] = Field(default=1, description="Batch size for processing")

class MLXModelLoadRequest(BaseModel):
    """MLX model loading request"""
    model_name: str = Field(..., description="Name of the model to load")

class MLXBenchmarkRequest(BaseModel):
    """MLX benchmark request"""
    iterations: int = Field(default=10, ge=1, le=100, description="Number of benchmark iterations")

class MLXStatusResponse(BaseModel):
    """MLX status response"""
    status: str
    mlx_available: bool
    current_model: Optional[str]
    available_models: List[str]
    model_count: int
    default_config: Dict[str, Any]
    timestamp: str

class MLXBenchmarkResponse(BaseModel):
    """MLX benchmark response"""
    iterations: int
    average_time: float
    min_time: float
    max_time: float
    throughput: float
    mlx_available: bool
    model_used: Optional[str]

# Create router
router = APIRouter(prefix="/api/mlx", tags=["MLX Processing"])

@router.post("/process", response_model=MLXResponse)
async def process_text(request: MLXProcessingRequest):
    """Process text using real MLX inference"""
    try:
        logger.info(f"🧠 MLX processing request: {request.operation}")
        
        # Ensure MLX processor is initialized
        if real_mlx_processor.status.value == "idle":
            await real_mlx_processor.initialize()
        
        # Create MLX configuration
        config = MLXConfig(
            model_path="",  # Will be set by the processor
            device=request.device,
            precision=request.precision,
            batch_size=request.batch_size,
            max_sequence_length=2048,
            temperature=request.temperature,
            top_p=0.9
        )
        
        # Load specific model if requested
        if request.model_name and request.model_name != real_mlx_processor.current_model:
            await real_mlx_processor.load_model(request.model_name)
        
        # Create MLX request
        mlx_request = MLXRequest(
            text=request.text,
            operation=request.operation,
            config=config,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        
        # Process the request
        response = await real_mlx_processor.process_text(mlx_request)
        
        if response.success:
            logger.info(f"✅ MLX processing completed: {response.processing_time:.2f}s")
        else:
            logger.warning(f"⚠️ MLX processing failed: {response.error}")
        
        return response
        
    except Exception as e:
        logger.error(f"MLX processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"MLX processing failed: {str(e)}")

@router.post("/generate")
async def generate_text(request: MLXProcessingRequest):
    """Generate text using MLX"""
    try:
        # Set operation to generate
        request.operation = "generate"
        
        response = await process_text(request)
        
        if response.success:
            return {
                "success": True,
                "generated_text": response.result,
                "processing_time": response.processing_time,
                "tokens_processed": response.tokens_processed,
                "model_used": response.model_used
            }
        else:
            raise HTTPException(status_code=400, detail=response.error)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Text generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Text generation failed: {str(e)}")

@router.post("/embed")
async def embed_text(request: MLXProcessingRequest):
    """Generate embeddings using MLX"""
    try:
        # Set operation to embed
        request.operation = "embed"
        
        response = await process_text(request)
        
        if response.success:
            return {
                "success": True,
                "embedding": response.result,
                "embedding_dimension": len(response.result),
                "processing_time": response.processing_time,
                "tokens_processed": response.tokens_processed,
                "model_used": response.model_used
            }
        else:
            raise HTTPException(status_code=400, detail=response.error)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Text embedding failed: {e}")
        raise HTTPException(status_code=500, detail=f"Text embedding failed: {str(e)}")

@router.post("/classify")
async def classify_text(request: MLXProcessingRequest):
    """Classify text using MLX"""
    try:
        # Set operation to classify
        request.operation = "classify"
        
        response = await process_text(request)
        
        if response.success:
            return {
                "success": True,
                "classification": response.result,
                "processing_time": response.processing_time,
                "tokens_processed": response.tokens_processed,
                "model_used": response.model_used
            }
        else:
            raise HTTPException(status_code=400, detail=response.error)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Text classification failed: {e}")
        raise HTTPException(status_code=500, detail=f"Text classification failed: {str(e)}")

@router.post("/model/load")
async def load_model(request: MLXModelLoadRequest):
    """Load a specific MLX model"""
    try:
        logger.info(f"📦 Loading MLX model: {request.model_name}")
        
        success = await real_mlx_processor.load_model(request.model_name)
        
        if success:
            return {
                "success": True,
                "message": f"Model {request.model_name} loaded successfully",
                "current_model": request.model_name
            }
        else:
            raise HTTPException(status_code=404, detail=f"Failed to load model {request.model_name}")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Model loading failed: {e}")
        raise HTTPException(status_code=500, detail=f"Model loading failed: {str(e)}")

@router.get("/status", response_model=MLXStatusResponse)
async def get_mlx_status():
    """Get current MLX processing status"""
    try:
        status = await real_mlx_processor.get_status()
        
        return MLXStatusResponse(
            status=status["status"],
            mlx_available=status["mlx_available"],
            current_model=status["current_model"],
            available_models=status["available_models"],
            model_count=status["model_count"],
            default_config=status["default_config"],
            timestamp=status["timestamp"]
        )
        
    except Exception as e:
        logger.error(f"Failed to get MLX status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get MLX status: {str(e)}")

@router.post("/benchmark", response_model=MLXBenchmarkResponse)
async def benchmark_mlx(request: MLXBenchmarkRequest):
    """Benchmark MLX processing performance"""
    try:
        logger.info(f"🏃 MLX benchmark: {request.iterations} iterations")
        
        benchmark_results = await real_mlx_processor.benchmark_performance(request.iterations)
        
        if "error" in benchmark_results:
            raise HTTPException(status_code=500, detail=benchmark_results["error"])
        
        return MLXBenchmarkResponse(
            iterations=benchmark_results["iterations"],
            average_time=benchmark_results["average_time"],
            min_time=benchmark_results["min_time"],
            max_time=benchmark_results["max_time"],
            throughput=benchmark_results["throughput"],
            mlx_available=benchmark_results["mlx_available"],
            model_used=benchmark_results["model_used"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"MLX benchmark failed: {e}")
        raise HTTPException(status_code=500, detail=f"MLX benchmark failed: {str(e)}")

@router.post("/initialize")
async def initialize_mlx():
    """Manually initialize the MLX processing system"""
    try:
        logger.info("🚀 Manual MLX initialization")
        
        success = await real_mlx_processor.initialize()
        
        if success:
            status = await real_mlx_processor.get_status()
            return {
                "success": True,
                "message": "MLX processing system initialized successfully",
                "status": status
            }
        else:
            return {
                "success": False,
                "message": "Failed to initialize MLX processing system",
                "fallback_available": True
            }
            
    except Exception as e:
        logger.error(f"MLX initialization failed: {e}")
        raise HTTPException(status_code=500, detail=f"MLX initialization failed: {str(e)}")

@router.get("/models")
async def list_available_models():
    """List all available MLX models"""
    try:
        status = await real_mlx_processor.get_status()
        
        models = []
        for model_name in status["available_models"]:
            models.append({
                "name": model_name,
                "status": "available",
                "path": real_mlx_processor.available_models.get(model_name, {}).get("path", "unknown")
            })
        
        return {
            "success": True,
            "models": models,
            "total_count": len(models),
            "current_model": status["current_model"]
        }
        
    except Exception as e:
        logger.error(f"Failed to list models: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list models: {str(e)}")

@router.get("/health")
async def mlx_health_check():
    """Health check for the MLX processing system"""
    try:
        status = await real_mlx_processor.get_status()
        
        is_healthy = status["status"] in ["ready", "idle"]
        
        return {
            "status": "healthy" if is_healthy else "degraded",
            "mlx_available": status["mlx_available"],
            "current_model": status["current_model"],
            "available_models": len(status["available_models"]),
            "processing_status": status["status"],
            "timestamp": status["timestamp"]
        }
        
    except Exception as e:
        logger.error(f"MLX health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/capabilities")
async def get_mlx_capabilities():
    """Get MLX processing capabilities"""
    return {
        "supported_operations": [
            {
                "name": "generate",
                "description": "Text generation using MLX models",
                "supported": True
            },
            {
                "name": "embed",
                "description": "Text embedding generation",
                "supported": True
            },
            {
                "name": "classify",
                "description": "Text classification",
                "supported": True
            }
        ],
        "supported_devices": ["cpu", "gpu", "mps"],
        "supported_precisions": ["float16", "float32"],
        "max_sequence_length": 2048,
        "batch_processing": True,
        "streaming": False,  # Can be added later
        "mlx_version": "0.0.1"  # Would be actual MLX version in real implementation
    }

# Include the router in the main API
def include_mlx_routes(app):
    """Include MLX routes in the FastAPI app"""
    app.include_router(router)
    logger.info("MLX API routes included")
