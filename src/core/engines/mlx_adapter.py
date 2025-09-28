#!/usr/bin/env python3
"""
MLX Model Adapter for Agentic LLM Core

This module provides integration with MLX models for efficient local inference
on Apple Silicon, complementing the Ollama adapter with native MLX performance.
"""

import os
import json
import logging
import asyncio
import time
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from dataclasses import dataclass
import mlx.core as mx
import mlx.nn as nn
import mlx_lm

logger = logging.getLogger(__name__)

@dataclass
class MLXModel:
    """MLX model configuration"""
    name: str
    mlx_path: str
    capabilities: List[str]
    performance: Dict[str, Any]
    optimization: Dict[str, Any]

@dataclass
class MLXResponse:
    """MLX model response structure"""
    content: str
    model: str
    processing_time: float
    tokens_generated: int
    metadata: Dict[str, Any]

class MLXAdapter:
    """Adapter for MLX model integration"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "configs/policies.yaml"
        self.models: Dict[str, MLXModel] = {}
        self.loaded_models: Dict[str, Any] = {}
        self.load_config()
    
    def load_config(self):
        """Load model configuration from policies.yaml"""
        try:
            import yaml
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            # Load MLX models from config
            mlx_models = config.get('model_policy', {}).get('models', {})
            
            for model_key, model_config in mlx_models.items():
                if 'mlx_path' in model_config:
                    self.models[model_key] = MLXModel(
                        name=model_config['name'],
                        mlx_path=model_config['mlx_path'],
                        capabilities=model_config.get('capabilities', []),
                        performance=model_config.get('performance', {}),
                        optimization=model_config.get('optimization', {})
                    )
            
            logger.info(f"Loaded {len(self.models)} MLX models")
            
        except Exception as e:
            logger.error(f"Failed to load MLX config: {e}")
            # Fallback to default MLX models
            self._load_default_models()
    
    def _load_default_models(self):
        """Load default MLX models"""
        self.models = {
            "mlx_qwen3_30b": MLXModel(
                name="Qwen3-30B-MLX-4bit",
                mlx_path="/Users/christianmerrill/Prompt Engineering/ollama_models/qwen3-30b-mlx-4bit",
                capabilities=["text_generation", "logical_reasoning", "strategic_planning"],
                performance={
                    "context_length": 32768,
                    "max_output_tokens": 4096,
                    "latency_ms": 2000,
                    "memory_gb": 20.0,
                    "gpu_required": False
                },
                optimization={
                    "precision": "int4",
                    "quantization": "dynamic",
                    "batch_size": 1,
                    "use_cache": True
                }
            ),
            "mlx_dia_1_6b": MLXModel(
                name="DIA-1.6B-MLX",
                mlx_path="/Users/christianmerrill/Prompt Engineering/ollama_models/dia-1.6b-mlx",
                capabilities=["text_generation", "simple_reasoning"],
                performance={
                    "context_length": 8192,
                    "max_output_tokens": 2048,
                    "latency_ms": 500,
                    "memory_gb": 2.0,
                    "gpu_required": False
                },
                optimization={
                    "precision": "int8",
                    "quantization": "dynamic",
                    "batch_size": 4,
                    "use_cache": True
                }
            )
        }
        logger.info(f"Loaded {len(self.models)} default MLX models")
    
    async def check_mlx_status(self) -> bool:
        """Check if MLX is available and working"""
        try:
            # Test basic MLX functionality
            test_array = mx.array([1, 2, 3])
            result = mx.sum(test_array)
            return result.item() == 6
        except Exception as e:
            logger.error(f"MLX status check failed: {e}")
            return False
    
    async def get_available_models(self) -> List[str]:
        """Get list of available MLX models"""
        try:
            available = []
            for model_key, model in self.models.items():
                if os.path.exists(model.mlx_path):
                    available.append(model_key)
            return available
        except Exception as e:
            logger.error(f"Failed to get available MLX models: {e}")
            return []
    
    async def load_model(self, model_key: str) -> bool:
        """Load an MLX model into memory"""
        try:
            if model_key not in self.models:
                raise ValueError(f"Model {model_key} not found")
            
            model_config = self.models[model_key]
            
            if not os.path.exists(model_config.mlx_path):
                raise FileNotFoundError(f"Model path not found: {model_config.mlx_path}")
            
            # Load model using mlx_lm
            model, tokenizer = mlx_lm.load(model_config.mlx_path)
            
            self.loaded_models[model_key] = {
                'model': model,
                'tokenizer': tokenizer,
                'config': model_config
            }
            
            logger.info(f"Loaded MLX model: {model_key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load MLX model {model_key}: {e}")
            return False
    
    async def generate_response(
        self, 
        model_key: str, 
        prompt: str, 
        max_tokens: int = 2048,
        temperature: float = 0.7,
        **kwargs
    ) -> MLXResponse:
        """Generate response using specified MLX model"""
        
        if model_key not in self.models:
            raise ValueError(f"Model {model_key} not found in configuration")
        
        # Load model if not already loaded
        if model_key not in self.loaded_models:
            success = await self.load_model(model_key)
            if not success:
                raise RuntimeError(f"Failed to load model {model_key}")
        
        model_data = self.loaded_models[model_key]
        model = model_data['model']
        tokenizer = model_data['tokenizer']
        model_config = model_data['config']
        
        start_time = time.time()
        
        try:
            # Generate response using mlx_lm
            response = mlx_lm.generate(
                model=model,
                tokenizer=tokenizer,
                prompt=prompt,
                max_tokens=max_tokens,
                temp=temperature,
                verbose=False
            )
            
            processing_time = time.time() - start_time
            
            # Count tokens (approximate)
            tokens_generated = len(response.split())
            
            return MLXResponse(
                content=response,
                model=model_config.name,
                processing_time=processing_time,
                tokens_generated=tokens_generated,
                metadata={
                    "model_key": model_key,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "mlx_optimized": True
                }
            )
            
        except Exception as e:
            logger.error(f"MLX generation failed for {model_key}: {e}")
            raise
    
    async def route_request(
        self, 
        prompt: str, 
        task_type: str = "text_generation",
        latency_requirement: int = 1000,
        **kwargs
    ) -> MLXResponse:
        """Route request to appropriate MLX model"""
        
        # Simple routing logic
        if latency_requirement < 500:
            model_key = "mlx_dia_1_6b"  # Fast model
        else:
            model_key = "mlx_qwen3_30b"  # Powerful model
        
        # Check if model is available
        available_models = await self.get_available_models()
        if model_key not in available_models:
            # Fallback to any available model
            if available_models:
                model_key = available_models[0]
            else:
                raise RuntimeError("No MLX models available")
        
        return await self.generate_response(model_key, prompt, **kwargs)
    
    def _select_model(self, task_type: str, latency_requirement: int) -> str:
        """Select appropriate model based on task requirements"""
        
        # Model selection logic
        if task_type in ["code_generation", "code_analysis"]:
            return "mlx_qwen3_30b"  # Better for coding tasks
        elif latency_requirement < 500:
            return "mlx_dia_1_6b"  # Fast response
        else:
            return "mlx_qwen3_30b"  # High quality response
    
    async def test_all_models(self) -> Dict[str, Any]:
        """Test all available MLX models"""
        results = {}
        
        for model_key in self.models.keys():
            try:
                test_prompt = "Hello, how are you?"
                response = await self.generate_response(model_key, test_prompt, max_tokens=50)
                results[model_key] = {
                    "status": "working",
                    "response_time": response.processing_time,
                    "sample_response": response.content[:100]
                }
            except Exception as e:
                results[model_key] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return results
    
    async def get_model_info(self, model_key: str) -> Dict[str, Any]:
        """Get information about a specific model"""
        if model_key not in self.models:
            raise ValueError(f"Model {model_key} not found")
        
        model = self.models[model_key]
        is_loaded = model_key in self.loaded_models
        
        return {
            "name": model.name,
            "path": model.mlx_path,
            "capabilities": model.capabilities,
            "performance": model.performance,
            "optimization": model.optimization,
            "is_loaded": is_loaded,
            "exists": os.path.exists(model.mlx_path)
        }

# MLX Model Manager for advanced operations
class MLXModelManager:
    """Advanced MLX model management"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.adapter = MLXAdapter(config_path)
        self.initialized = False
    
    async def initialize(self) -> bool:
        """Initialize MLX model manager"""
        try:
            status = await self.adapter.check_mlx_status()
            if not status:
                logger.error("MLX is not available")
                return False
            
            self.initialized = True
            logger.info("MLX Model Manager initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"MLX Model Manager initialization failed: {e}")
            return False
    
    async def analyze_context(self, context) -> Any:
        """Analyze context using MLX models"""
        if not self.initialized:
            raise RuntimeError("MLX Model Manager not initialized")
        
        # Use the most capable model for context analysis
        response = await self.adapter.generate_response(
            model_key="mlx_qwen3_30b",
            prompt=f"Analyze this context: {context}",
            max_tokens=512,
            temperature=0.3
        )
        
        return response.content
    
    async def generate_answer(self, analysis, tools: List[Any] = None) -> Any:
        """Generate answer using MLX models"""
        if not self.initialized:
            raise RuntimeError("MLX Model Manager not initialized")
        
        # Use appropriate model based on complexity
        model_key = "mlx_qwen3_30b" if len(str(analysis)) > 1000 else "mlx_dia_1_6b"
        
        response = await self.adapter.generate_response(
            model_key=model_key,
            prompt=f"Based on this analysis, provide a comprehensive answer: {analysis}",
            max_tokens=1024,
            temperature=0.7
        )
        
        return response.content

async def main():
    """Test MLX adapter functionality"""
    print("🧪 Testing MLX Adapter...")
    
    adapter = MLXAdapter()
    
    # Check MLX status
    status = await adapter.check_mlx_status()
    print(f"MLX Status: {'✅ Working' if status else '❌ Failed'}")
    
    # List available models
    models = await adapter.get_available_models()
    print(f"Available MLX Models: {models}")
    
    # Test model info
    for model_key in models:
        info = await adapter.get_model_info(model_key)
        print(f"Model {model_key}: {info['name']} - {'✅ Loaded' if info['is_loaded'] else '⏳ Not loaded'}")
    
    # Test generation if models are available
    if models:
        try:
            response = await adapter.route_request(
                prompt="Hello, can you tell me about machine learning?",
                task_type="text_generation",
                latency_requirement=1000
            )
            print(f"✅ MLX Generation Test: {response.content[:100]}...")
            print(f"Processing Time: {response.processing_time:.2f}s")
        except Exception as e:
            print(f"❌ MLX Generation Test Failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
