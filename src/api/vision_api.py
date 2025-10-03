#!/usr/bin/env python3
"""
Vision API - Image analysis using LLaVA and other vision models
Provides endpoints for image analysis, object detection, and visual understanding
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel, Field
from datetime import datetime
import base64
import io

from ..core.vision.llava_integration import llava_analyzer

logger = logging.getLogger(__name__)

# Request/response models
class ImageAnalysisRequest(BaseModel):
    """Image analysis request"""
    image_data: str = Field(..., description="Base64 encoded image data")
    prompt: Optional[str] = Field(default=None, description="Custom analysis prompt")
    cache_result: bool = Field(default=True, description="Whether to cache the analysis result")

class BatchImageAnalysisRequest(BaseModel):
    """Batch image analysis request"""
    images: List[Dict[str, Any]] = Field(..., description="List of images to analyze")
    default_prompt: Optional[str] = Field(default=None, description="Default prompt for all images")

class ImageAnalysisResponse(BaseModel):
    """Image analysis response"""
    success: bool
    analysis: Optional[str] = None
    model_used: str
    processing_time: float
    tokens_used: Optional[int] = None
    timestamp: Optional[str] = None
    error: Optional[str] = None
    fallback: bool = False

class BatchAnalysisResponse(BaseModel):
    """Batch analysis response"""
    success: bool
    total_images: int
    successful_analyses: int
    failed_analyses: int
    results: List[Dict[str, Any]]
    processing_time: float

class ModelInfoResponse(BaseModel):
    """Model information response"""
    available: bool
    model_name: str
    status: str
    model_info: Optional[Dict[str, Any]] = None
    cache_size: int = 0

# Create router
router = APIRouter(prefix="/api/vision", tags=["Vision"])

@router.post("/analyze", response_model=ImageAnalysisResponse)
async def analyze_image(request: ImageAnalysisRequest):
    """Analyze a single image using LLaVA vision model"""
    try:
        import time
        start_time = time.time()
        
        logger.info("🔍 Image analysis request received")
        
        # Ensure vision analyzer is initialized
        if not llava_analyzer.is_available:
            await llava_analyzer.initialize()
        
        # Analyze the image
        result = await llava_analyzer.analyze_image(
            image_data=request.image_data,
            prompt=request.prompt
        )
        
        processing_time = time.time() - start_time
        
        if result.get("success"):
            return ImageAnalysisResponse(
                success=True,
                analysis=result.get("analysis", ""),
                model_used=result.get("model", "unknown"),
                processing_time=processing_time,
                tokens_used=result.get("tokens_used"),
                timestamp=result.get("timestamp"),
                fallback=result.get("fallback", False)
            )
        else:
            return ImageAnalysisResponse(
                success=False,
                error=result.get("error", "Analysis failed"),
                model_used=result.get("model", "unknown"),
                processing_time=processing_time,
                fallback=result.get("fallback", False)
            )
            
    except Exception as e:
        logger.error(f"Image analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Image analysis failed: {str(e)}")

@router.post("/analyze/upload")
async def analyze_uploaded_image(
    file: UploadFile = File(...),
    prompt: str = Form(default="Analyze this image in detail. Describe what you see, including objects, people, text, colors, composition, and any other relevant details.")
):
    """Analyze an uploaded image file"""
    try:
        logger.info(f"🔍 Image upload analysis request: {file.filename}")
        
        # Read the uploaded file
        image_data = await file.read()
        
        # Convert to base64
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # Ensure vision analyzer is initialized
        if not llava_analyzer.is_available:
            await llava_analyzer.initialize()
        
        # Analyze the image
        result = await llava_analyzer.analyze_image(
            image_data=image_base64,
            prompt=prompt
        )
        
        if result.get("success"):
            return {
                "success": True,
                "filename": file.filename,
                "analysis": result.get("analysis", ""),
                "model_used": result.get("model", "unknown"),
                "processing_time": result.get("processing_time", 0),
                "tokens_used": result.get("tokens_used"),
                "fallback": result.get("fallback", False)
            }
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"Image analysis failed: {result.get('error', 'Unknown error')}"
            )
            
    except Exception as e:
        logger.error(f"Uploaded image analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Uploaded image analysis failed: {str(e)}")

@router.post("/analyze/batch", response_model=BatchAnalysisResponse)
async def batch_analyze_images(request: BatchImageAnalysisRequest):
    """Analyze multiple images in batch"""
    try:
        import time
        start_time = time.time()
        
        logger.info(f"🔍 Batch image analysis request: {len(request.images)} images")
        
        # Ensure vision analyzer is initialized
        if not llava_analyzer.is_available:
            await llava_analyzer.initialize()
        
        # Prepare images for batch analysis
        image_list = []
        for img_data in request.images:
            image_info = {
                "image_data": img_data.get("image_data"),
                "prompt": img_data.get("prompt", request.default_prompt)
            }
            image_list.append(image_info)
        
        # Perform batch analysis
        results = await llava_analyzer.batch_analyze_images(image_list)
        
        processing_time = time.time() - start_time
        successful = len([r for r in results if r.get("success")])
        failed = len(results) - successful
        
        return BatchAnalysisResponse(
            success=successful > 0,
            total_images=len(results),
            successful_analyses=successful,
            failed_analyses=failed,
            results=results,
            processing_time=processing_time
        )
        
    except Exception as e:
        logger.error(f"Batch image analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Batch image analysis failed: {str(e)}")

@router.get("/model/info", response_model=ModelInfoResponse)
async def get_model_info():
    """Get information about the vision model"""
    try:
        logger.info("🔍 Getting vision model information")
        
        # Ensure vision analyzer is initialized
        if not llava_analyzer.is_available:
            await llava_analyzer.initialize()
        
        model_info = await llava_analyzer.get_model_info()
        
        return ModelInfoResponse(
            available=model_info.get("available", False),
            model_name=model_info.get("model_name", "unknown"),
            status=model_info.get("status", "unknown"),
            model_info=model_info.get("model_info"),
            cache_size=model_info.get("cache_size", 0)
        )
        
    except Exception as e:
        logger.error(f"Failed to get model info: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get model info: {str(e)}")

@router.post("/model/initialize")
async def initialize_vision_model():
    """Manually initialize the vision model"""
    try:
        logger.info("🔍 Manual vision model initialization")
        
        success = await llava_analyzer.initialize()
        
        if success:
            model_info = await llava_analyzer.get_model_info()
            return {
                "success": True,
                "message": "Vision model initialized successfully",
                "model_info": model_info
            }
        else:
            return {
                "success": False,
                "message": "Failed to initialize vision model",
                "fallback_available": True
            }
            
    except Exception as e:
        logger.error(f"Vision model initialization failed: {e}")
        raise HTTPException(status_code=500, detail=f"Vision model initialization failed: {str(e)}")

@router.post("/cache/clear")
async def clear_analysis_cache():
    """Clear the image analysis cache"""
    try:
        logger.info("🗑️ Clearing image analysis cache")
        
        cache_size = len(llava_analyzer.analysis_cache)
        llava_analyzer.clear_cache()
        
        return {
            "success": True,
            "message": f"Cleared {cache_size} cached analyses",
            "cache_size_before": cache_size,
            "cache_size_after": 0
        }
        
    except Exception as e:
        logger.error(f"Cache clear failed: {e}")
        raise HTTPException(status_code=500, detail=f"Cache clear failed: {str(e)}")

@router.get("/health")
async def vision_health_check():
    """Health check for the vision system"""
    try:
        # Check if vision analyzer is available
        is_available = llava_analyzer.is_available
        model_loaded = llava_analyzer.model_loaded
        
        if not is_available:
            # Try to initialize
            await llava_analyzer.initialize()
            is_available = llava_analyzer.is_available
        
        return {
            "status": "healthy" if is_available else "degraded",
            "vision_model_available": is_available,
            "model_loaded": model_loaded,
            "model_name": llava_analyzer.model_name,
            "cache_size": len(llava_analyzer.analysis_cache),
            "fallback_available": True,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Vision health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/examples")
async def get_analysis_examples():
    """Get examples of image analysis prompts"""
    return {
        "examples": [
            {
                "prompt": "Analyze this image in detail. Describe what you see, including objects, people, text, colors, composition, and any other relevant details.",
                "description": "Comprehensive image analysis"
            },
            {
                "prompt": "What objects and items can you identify in this image? List them with their approximate locations.",
                "description": "Object identification and localization"
            },
            {
                "prompt": "Read and transcribe any text visible in this image.",
                "description": "OCR and text extraction"
            },
            {
                "prompt": "Describe the emotions and expressions of any people in this image.",
                "description": "Emotional analysis"
            },
            {
                "prompt": "What is the setting or environment shown in this image?",
                "description": "Environmental context"
            },
            {
                "prompt": "Identify any potential safety hazards or concerning elements in this image.",
                "description": "Safety assessment"
            },
            {
                "prompt": "What is the artistic style, composition, and visual elements of this image?",
                "description": "Artistic analysis"
            }
        ],
        "tips": [
            "Be specific in your prompts for better results",
            "Include context about what you're looking for",
            "Use descriptive language to guide the analysis",
            "Consider the use case when crafting prompts"
        ]
    }

# Include the router in the main API
def include_vision_routes(app):
    """Include vision routes in the FastAPI app"""
    app.include_router(router)
    logger.info("Vision API routes included")
