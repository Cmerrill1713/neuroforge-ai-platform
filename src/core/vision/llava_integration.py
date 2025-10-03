#!/usr/bin/env python3
"""
LLaVA Vision Model Integration
Provides image analysis capabilities using LLaVA (Large Language and Vision Assistant)
"""

import logging
import asyncio
import base64
import io
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import json
import requests
from PIL import Image
import numpy as np

logger = logging.getLogger(__name__)

class LLaVAVisionAnalyzer:
    """LLaVA vision model integration for image analysis"""
    
    def __init__(self, model_name: str = "llava-v1.5-7b", api_base: str = "http://localhost:11434"):
        self.model_name = model_name
        self.api_base = api_base
        self.is_available = False
        self.model_loaded = False
        self.analysis_cache = {}
        
    async def initialize(self) -> bool:
        """Initialize the LLaVA vision model"""
        try:
            logger.info(f"🔍 Initializing LLaVA vision model: {self.model_name}")
            
            # Check if Ollama is available
            if not await self._check_ollama_availability():
                logger.warning("⚠️ Ollama not available, vision analysis will be limited")
                return False
            
            # Check if LLaVA model is available
            if not await self._check_model_availability():
                logger.info(f"📥 LLaVA model {self.model_name} not found, attempting to pull...")
                if await self._pull_llava_model():
                    logger.info(f"✅ Successfully pulled LLaVA model {self.model_name}")
                else:
                    logger.warning(f"⚠️ Failed to pull LLaVA model {self.model_name}")
                    return False
            
            self.is_available = True
            self.model_loaded = True
            logger.info(f"✅ LLaVA vision model {self.model_name} initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize LLaVA vision model: {e}")
            return False
    
    async def _check_ollama_availability(self) -> bool:
        """Check if Ollama service is available"""
        try:
            response = requests.get(f"{self.api_base}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Ollama availability check failed: {e}")
            return False
    
    async def _check_model_availability(self) -> bool:
        """Check if LLaVA model is available in Ollama"""
        try:
            response = requests.get(f"{self.api_base}/api/tags", timeout=10)
            if response.status_code == 200:
                models = response.json().get("models", [])
                for model in models:
                    if self.model_name in model.get("name", ""):
                        return True
            return False
        except Exception as e:
            logger.warning(f"Model availability check failed: {e}")
            return False
    
    async def _pull_llava_model(self) -> bool:
        """Pull LLaVA model from Ollama registry"""
        try:
            logger.info(f"📥 Pulling LLaVA model: {self.model_name}")
            response = requests.post(
                f"{self.api_base}/api/pull",
                json={"name": self.model_name},
                timeout=300  # 5 minutes timeout for model pull
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to pull LLaVA model: {e}")
            return False
    
    async def analyze_image(self, image_data: Union[str, bytes, Path], prompt: str = None) -> Dict[str, Any]:
        """Analyze an image using LLaVA vision model"""
        try:
            if not self.is_available:
                return await self._fallback_analysis(image_data)
            
            # Prepare image
            image_base64 = await self._prepare_image(image_data)
            if not image_base64:
                return {"error": "Failed to process image", "fallback": True}
            
            # Use default prompt if none provided
            if not prompt:
                prompt = "Analyze this image in detail. Describe what you see, including objects, people, text, colors, composition, and any other relevant details."
            
            # Check cache first
            cache_key = f"{hash(image_base64)}_{hash(prompt)}"
            if cache_key in self.analysis_cache:
                logger.info("📋 Using cached image analysis")
                return self.analysis_cache[cache_key]
            
            # Call LLaVA API
            analysis_result = await self._call_llava_api(image_base64, prompt)
            
            # Cache the result
            self.analysis_cache[cache_key] = analysis_result
            
            logger.info(f"🔍 Image analysis completed: {len(analysis_result.get('analysis', ''))} characters")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Image analysis failed: {e}")
            return {"error": str(e), "fallback": True}
    
    async def _prepare_image(self, image_data: Union[str, bytes, Path]) -> Optional[str]:
        """Prepare image for LLaVA analysis"""
        try:
            if isinstance(image_data, str):
                # Handle base64 string
                if image_data.startswith('data:image'):
                    return image_data.split(',')[1]
                # Handle file path
                elif Path(image_data).exists():
                    with open(image_data, 'rb') as f:
                        image_bytes = f.read()
                else:
                    # Assume it's base64
                    return image_data
            elif isinstance(image_data, bytes):
                image_bytes = image_data
            elif isinstance(image_data, Path):
                with open(image_data, 'rb') as f:
                    image_bytes = f.read()
            else:
                logger.error(f"Unsupported image data type: {type(image_data)}")
                return None
            
            # Convert to base64
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
            return image_base64
            
        except Exception as e:
            logger.error(f"Image preparation failed: {e}")
            return None
    
    async def _call_llava_api(self, image_base64: str, prompt: str) -> Dict[str, Any]:
        """Call LLaVA API via Ollama"""
        try:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "images": [image_base64],
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "top_p": 0.9,
                    "max_tokens": 2048
                }
            }
            
            response = requests.post(
                f"{self.api_base}/api/generate",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                analysis = result.get("response", "")
                
                return {
                    "analysis": analysis,
                    "model": self.model_name,
                    "timestamp": result.get("created_at"),
                    "processing_time": result.get("total_duration", 0) / 1e9,  # Convert to seconds
                    "tokens_used": result.get("eval_count", 0),
                    "success": True
                }
            else:
                logger.error(f"LLaVA API call failed: {response.status_code}")
                return {"error": f"API call failed: {response.status_code}", "success": False}
                
        except Exception as e:
            logger.error(f"LLaVA API call error: {e}")
            return {"error": str(e), "success": False}
    
    async def _fallback_analysis(self, image_data: Union[str, bytes, Path]) -> Dict[str, Any]:
        """Fallback image analysis using basic image processing"""
        try:
            logger.info("🔄 Using fallback image analysis")
            
            # Load image
            if isinstance(image_data, str) and not image_data.startswith('data:image'):
                image = Image.open(image_data)
            elif isinstance(image_data, Path):
                image = Image.open(image_data)
            elif isinstance(image_data, bytes):
                image = Image.open(io.BytesIO(image_data))
            else:
                # Handle base64
                if isinstance(image_data, str) and image_data.startswith('data:image'):
                    image_data = image_data.split(',')[1]
                image_bytes = base64.b64decode(image_data)
                image = Image.open(io.BytesIO(image_bytes))
            
            # Basic analysis
            width, height = image.size
            mode = image.mode
            format_name = image.format
            
            # Extract basic information
            analysis = f"Image Analysis (Fallback):\n"
            analysis += f"- Dimensions: {width} x {height} pixels\n"
            analysis += f"- Color mode: {mode}\n"
            analysis += f"- Format: {format_name}\n"
            
            # Try to get more details
            try:
                # Convert to RGB for analysis
                if image.mode != 'RGB':
                    rgb_image = image.convert('RGB')
                else:
                    rgb_image = image
                
                # Get dominant colors (simplified)
                colors = rgb_image.getcolors(maxcolors=256*256*256)
                if colors:
                    dominant_color = max(colors, key=lambda x: x[0])
                    analysis += f"- Dominant color: RGB{dominant_color[1]} (appears {dominant_color[0]} times)\n"
                
                # Basic histogram analysis
                histogram = rgb_image.histogram()
                total_pixels = width * height
                avg_brightness = sum(histogram[:256]) / total_pixels
                analysis += f"- Average brightness: {avg_brightness:.2f}\n"
                
            except Exception as e:
                analysis += f"- Additional analysis failed: {str(e)}\n"
            
            analysis += "\nNote: This is a basic fallback analysis. For detailed image understanding, LLaVA model is recommended."
            
            return {
                "analysis": analysis,
                "model": "fallback",
                "timestamp": None,
                "processing_time": 0.1,
                "tokens_used": 0,
                "success": True,
                "fallback": True
            }
            
        except Exception as e:
            logger.error(f"Fallback analysis failed: {e}")
            return {
                "error": str(e),
                "success": False,
                "fallback": True
            }
    
    async def batch_analyze_images(self, image_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze multiple images in batch"""
        try:
            logger.info(f"🔍 Batch analyzing {len(image_list)} images")
            
            results = []
            for i, image_info in enumerate(image_list):
                try:
                    image_data = image_info.get("image_data")
                    prompt = image_info.get("prompt", "Analyze this image in detail.")
                    
                    result = await self.analyze_image(image_data, prompt)
                    result["batch_index"] = i
                    results.append(result)
                    
                    # Small delay to prevent overwhelming the API
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    logger.error(f"Batch analysis failed for image {i}: {e}")
                    results.append({
                        "batch_index": i,
                        "error": str(e),
                        "success": False
                    })
            
            logger.info(f"✅ Batch analysis completed: {len([r for r in results if r.get('success')])} successful")
            return results
            
        except Exception as e:
            logger.error(f"Batch analysis failed: {e}")
            return []
    
    async def get_model_info(self) -> Dict[str, Any]:
        """Get information about the LLaVA model"""
        try:
            if not self.is_available:
                return {
                    "available": False,
                    "model_name": self.model_name,
                    "status": "not_initialized"
                }
            
            # Get model details from Ollama
            response = requests.get(f"{self.api_base}/api/tags", timeout=10)
            if response.status_code == 200:
                models = response.json().get("models", [])
                for model in models:
                    if self.model_name in model.get("name", ""):
                        return {
                            "available": True,
                            "model_name": self.model_name,
                            "model_info": model,
                            "status": "ready",
                            "cache_size": len(self.analysis_cache)
                        }
            
            return {
                "available": False,
                "model_name": self.model_name,
                "status": "model_not_found"
            }
            
        except Exception as e:
            logger.error(f"Failed to get model info: {e}")
            return {
                "available": False,
                "model_name": self.model_name,
                "error": str(e),
                "status": "error"
            }
    
    def clear_cache(self):
        """Clear the analysis cache"""
        cache_size = len(self.analysis_cache)
        self.analysis_cache.clear()
        logger.info(f"🗑️ Cleared image analysis cache ({cache_size} entries)")

# Global instance
llava_analyzer = LLaVAVisionAnalyzer()
