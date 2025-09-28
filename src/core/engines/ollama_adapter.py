#!/usr/bin/env python3
"""
Ollama Model Adapter for Agentic LLM Core

This module provides integration with Ollama models for efficient local inference
on Apple Silicon, replacing the large Qwen3-Omni model with smaller, optimized models.
"""

import os
import json
import logging
import asyncio
import subprocess
import time
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from dataclasses import dataclass
import requests

# MLX imports (with fallback)
try:
    import mlx.core as mx
    import mlx.nn as nn
    import mlx_lm
    MLX_AVAILABLE = True
except ImportError:
    MLX_AVAILABLE = False
    logger.warning("MLX not available - MLX models will be disabled")

logger = logging.getLogger(__name__)

@dataclass
class OllamaModel:
    """Ollama model configuration"""
    name: str
    ollama_name: str
    capabilities: List[str]
    performance: Dict[str, Any]
    optimization: Dict[str, Any]
    model_type: str = "ollama"  # "ollama" or "mlx"
    mlx_path: Optional[str] = None

@dataclass
class ModelResponse:
    """Model response structure"""
    content: str
    model: str
    processing_time: float
    tokens_generated: int
    metadata: Dict[str, Any]

class OllamaAdapter:
    """Adapter for Ollama and MLX model integration"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "configs/policies.yaml"
        self.models: Dict[str, OllamaModel] = {}
        self.ollama_url = "http://localhost:11434"
        self.mlx_models: Dict[str, Any] = {}  # Cache for loaded MLX models
        self.load_config()
        self._load_mlx_models()
    
    def load_config(self):
        """Load model configuration from policies.yaml"""
        try:
            import yaml
            
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            model_policy = config.get('model_policy', {})
            models_config = model_policy.get('models', {})
            
            for model_key, model_data in models_config.items():
                if 'ollama_name' in model_data:
                    model = OllamaModel(
                        name=model_data['name'],
                        ollama_name=model_data['ollama_name'],
                        capabilities=model_data['capabilities'],
                        performance=model_data['performance'],
                        optimization=model_data['optimization'],
                        model_type=model_data.get('model_type', 'ollama'),
                        mlx_path=model_data.get('mlx_path')
                    )
                    self.models[model_key] = model
            
            logger.info(f"Loaded {len(self.models)} models")
            
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
    
    def _load_mlx_models(self):
        """Load MLX models from local directories"""
        if not MLX_AVAILABLE:
            logger.warning("MLX not available - skipping MLX model loading")
            return
        
        # Add MLX models to the models dictionary
        mlx_models = {
            "mlx_qwen3_30b": OllamaModel(
                name="Qwen3-30B-MLX-4bit",
                ollama_name="qwen3-30b-mlx-4bit",
                capabilities=["text_generation", "logical_reasoning", "strategic_planning", "code_generation"],
                performance={
                    "context_length": 32768,
                    "max_output_tokens": 4096,
                    "latency_ms": 2000,
                    "memory_gb": 16.0,
                    "gpu_required": False
                },
                optimization={
                    "precision": "int4",
                    "quantization": "dynamic",
                    "batch_size": 1,
                    "use_cache": True
                },
                model_type="mlx",
                mlx_path="/Users/christianmerrill/Prompt Engineering/ollama_models/qwen3-30b-mlx-4bit"
            ),
            "mlx_dia_1_6b": OllamaModel(
                name="DIA-1.6B-MLX",
                ollama_name="dia-1.6b-mlx",
                capabilities=["text_generation", "simple_reasoning"],
                performance={
                    "context_length": 8192,
                    "max_output_tokens": 2048,
                    "latency_ms": 500,
                    "memory_gb": 6.0,
                    "gpu_required": False
                },
                optimization={
                    "precision": "int8",
                    "quantization": "dynamic",
                    "batch_size": 4,
                    "use_cache": True
                },
                model_type="mlx",
                mlx_path="/Users/christianmerrill/Prompt Engineering/ollama_models/dia-1.6b-mlx"
            )
        }
        
        # Only add MLX models if their paths exist
        for model_key, model in mlx_models.items():
            if model.mlx_path and os.path.exists(model.mlx_path):
                self.models[model_key] = model
                logger.info(f"Added MLX model: {model.name}")
            else:
                logger.warning(f"MLX model path not found: {model.mlx_path}")
    
    async def check_ollama_status(self) -> bool:
        """Check if Ollama is running"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Ollama not available: {e}")
            return False
    
    async def get_available_models(self) -> List[str]:
        """Get list of available Ollama models"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
            return []
        except Exception as e:
            logger.error(f"Failed to get available models: {e}")
            return []
    
    async def generate_response(
        self,
        model_key: str,
        prompt: str,
        max_tokens: int = 2048,
        temperature: float = 0.7,
        **kwargs
    ) -> ModelResponse:
        """Generate response using specified model (Ollama or MLX) with robust fallback handling"""

        if model_key not in self.models:
            logger.warning(f"Model {model_key} not found, attempting fallback")
            # Try fallback models
            fallback_models = ['primary', 'lightweight', 'mlx_qwen3_30b', 'mlx_dia_1_6b']
            for fallback in fallback_models:
                if fallback in self.models:
                    logger.info(f"Using fallback model: {fallback}")
                    model_key = fallback
                    break
            else:
                raise ValueError(f"No models available for fallback")

        model = self.models[model_key]
        start_time = time.time()

        try:
            if model.model_type == "mlx":
                return await self._generate_mlx_response(model, prompt, max_tokens, temperature, **kwargs)
            else:
                return await self._generate_ollama_response(model, prompt, max_tokens, temperature, **kwargs)

        except Exception as e:
            logger.error(f"Error generating response with {model_key}: {e}")
            
            # Try fallback models if the primary model fails
            if model_key != 'primary':
                logger.info(f"Attempting fallback to primary model")
                try:
                    if 'primary' in self.models:
                        fallback_model = self.models['primary']
                        if fallback_model.model_type == "mlx":
                            return await self._generate_mlx_response(fallback_model, prompt, max_tokens, temperature, **kwargs)
                        else:
                            return await self._generate_ollama_response(fallback_model, prompt, max_tokens, temperature, **kwargs)
                except Exception as fallback_error:
                    logger.error(f"Fallback to primary model also failed: {fallback_error}")
            
            # If all else fails, return a basic response
            logger.warning("All models failed, returning fallback response")
            return ModelResponse(
                content=f"I apologize, but I'm experiencing technical difficulties. The AI models are currently unavailable. Please try again later. (Error: {str(e)[:100]})",
                model=f"{model_key}_fallback",
                processing_time=time.time() - start_time,
                tokens_generated=len(prompt.split()),
                metadata={
                    "model_type": "fallback",
                    "error": str(e),
                    "fallback_used": True
                }
            )
    
    async def _generate_ollama_response(
        self, 
        model: OllamaModel, 
        prompt: str, 
        max_tokens: int,
        temperature: float,
        **kwargs
    ) -> ModelResponse:
        """Generate response using Ollama API"""
        start_time = time.time()
        
        # Prepare request payload
        payload = {
            "model": model.ollama_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature,
                **kwargs
            }
        }
        
        # Make request to Ollama
        response = requests.post(
            f"{self.ollama_url}/api/generate",
            json=payload,
            timeout=60
        )
        
        if response.status_code != 200:
            raise Exception(f"Ollama API error: {response.status_code}")
        
        data = response.json()
        processing_time = time.time() - start_time
        
        return ModelResponse(
            content=data.get('response', ''),
            model=model.name,
            processing_time=processing_time,
            tokens_generated=len(data.get('response', '').split()),
            metadata={
                "model_type": "ollama",
                "ollama_model": model.ollama_name,
                "capabilities": model.capabilities
            }
        )
    
    async def _generate_mlx_response(
        self, 
        model: OllamaModel, 
        prompt: str, 
        max_tokens: int,
        temperature: float,
        **kwargs
    ) -> ModelResponse:
        """Generate response using MLX directly"""
        if not MLX_AVAILABLE:
            raise RuntimeError("MLX not available")
        
        start_time = time.time()
        
        # Load model if not already loaded
        if model.ollama_name not in self.mlx_models:
            await self._load_mlx_model(model)
        
        mlx_model_data = self.mlx_models[model.ollama_name]
        mlx_model = mlx_model_data['model']
        tokenizer = mlx_model_data['tokenizer']
        
        try:
            # Generate response using mlx_lm
            response = mlx_lm.generate(
                model=mlx_model,
                tokenizer=tokenizer,
                prompt=prompt,
                max_tokens=max_tokens,
                temp=temperature,
                verbose=False
            )
            
            processing_time = time.time() - start_time
            
            return ModelResponse(
                content=response,
                model=model.name,
                processing_time=processing_time,
                tokens_generated=len(response.split()),
                metadata={
                    "model_type": "mlx",
                    "mlx_path": model.mlx_path,
                    "capabilities": model.capabilities,
                    "mlx_optimized": True
                }
            )
            
        except Exception as e:
            logger.error(f"MLX generation failed: {e}")
            raise
    
    async def _load_mlx_model(self, model: OllamaModel):
        """Load MLX model into memory"""
        if not MLX_AVAILABLE:
            raise RuntimeError("MLX not available")
        
        try:
            # Load model using mlx_lm
            mlx_model, tokenizer = mlx_lm.load(model.mlx_path)
            
            self.mlx_models[model.ollama_name] = {
                'model': mlx_model,
                'tokenizer': tokenizer,
                'config': model
            }
            
            logger.info(f"Loaded MLX model: {model.name}")
            
        except Exception as e:
            logger.error(f"Failed to load MLX model {model.name}: {e}")
            raise
    
    async def route_request(
        self, 
        prompt: str, 
        input_type: str = "text",
        task_type: str = "text_generation",
        latency_requirement: int = 1000,
        **kwargs
    ) -> ModelResponse:
        """Intelligently route request to appropriate model"""
        
        # Determine best model based on routing rules
        model_key = self._select_model(input_type, task_type, latency_requirement)
        
        logger.info(f"Routing request to {model_key} for {task_type}")
        
        return await self.generate_response(model_key, prompt, **kwargs)
    
    def _select_model(
        self,
        input_type: str,
        task_type: str,
        latency_requirement: int
    ) -> str:
        """Select appropriate model based on routing rules with fallback handling"""

        # Check for multimodal tasks
        if input_type in ['image', 'multimodal', 'vision']:
            if 'multimodal' in self.models:
                return 'multimodal'

        # Check for coding tasks - prioritize MLX models with fallback
        if task_type in ['code_generation', 'code_analysis', 'debugging', 'refactoring']:
            if 'mlx_qwen3_30b' in self.models:
                return 'mlx_qwen3_30b'  # MLX Qwen3-30B for coding
            if 'coding' in self.models:
                return 'coding'
            if 'primary' in self.models:
                return 'primary'  # Fallback to primary

        # Check for advanced reasoning/puzzle tasks
        if task_type in ['puzzle', 'logic', 'riddle', 'reasoning_deep']:
            if 'mlx_qwen3_30b' in self.models:
                return 'mlx_qwen3_30b'  # MLX Qwen3-30B for reasoning
            if 'hrm' in self.models:
                return 'hrm'
            if 'primary' in self.models:
                return 'primary'  # Fallback to primary

        # Check for fast response requirements - use MLX DIA-1.6B with fallback
        if latency_requirement < 500:
            if 'mlx_dia_1_6b' in self.models:
                return 'mlx_dia_1_6b'  # MLX DIA-1.6B for speed
            if 'lightweight' in self.models:
                return 'lightweight'
            if 'primary' in self.models:
                return 'primary'  # Fallback to primary

        # Default to MLX Qwen3-30B if available, otherwise primary with fallback
        if 'mlx_qwen3_30b' in self.models:
            return 'mlx_qwen3_30b'  # MLX Qwen3-30B for quality
        if 'primary' in self.models:
            return 'primary'
        
        # Ultimate fallback - return any available model
        available_models = list(self.models.keys())
        if available_models:
            logger.warning(f"Using fallback model: {available_models[0]}")
            return available_models[0]
        
        # If no models available, return primary (will be handled by error handling)
        logger.error("No models available for selection")
        return 'primary'
    
    async def test_all_models(self) -> Dict[str, Any]:
        """Test all configured models"""
        test_prompt = "Hello, how are you? Please respond briefly."
        results = {}
        
        for model_key, model in self.models.items():
            try:
                logger.info(f"Testing {model_key} ({model.ollama_name})")
                response = await self.generate_response(
                    model_key, 
                    test_prompt, 
                    max_tokens=100
                )
                
                results[model_key] = {
                    "status": "success",
                    "response_time": response.processing_time,
                    "tokens_generated": response.tokens_generated,
                    "response_preview": response.content[:100] + "..." if len(response.content) > 100 else response.content
                }
                
            except Exception as e:
                results[model_key] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return results
    
    async def get_model_info(self, model_key: str) -> Dict[str, Any]:
        """Get detailed information about a specific model"""
        if model_key not in self.models:
            raise ValueError(f"Model {model_key} not found")
        
        model = self.models[model_key]
        
        return {
            "name": model.name,
            "ollama_name": model.ollama_name,
            "capabilities": model.capabilities,
            "performance": model.performance,
            "optimization": model.optimization,
            "available": await self._check_model_availability(model.ollama_name)
        }
    
    async def _check_model_availability(self, ollama_name: str) -> bool:
        """Check if a specific Ollama model is available"""
        try:
            available_models = await self.get_available_models()
            return ollama_name in available_models
        except Exception:
            return False

# Integration with existing Agentic LLM Core
class OllamaQwen3OmniEngine:
    """
    Replacement for Qwen3OmniEngine using Ollama models
    
    This class provides the same interface as the original Qwen3OmniEngine
    but uses smaller, more efficient Ollama models instead.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.adapter = OllamaAdapter(config_path)
        self.initialized = False
    
    async def initialize(self) -> bool:
        """Initialize the Ollama engine"""
        try:
            if not await self.adapter.check_ollama_status():
                logger.error("Ollama is not running. Please start Ollama first.")
                return False
            
            # Test all models
            test_results = await self.adapter.test_all_models()
            successful_models = [k for k, v in test_results.items() if v["status"] == "success"]
            
            if not successful_models:
                logger.error("No Ollama models are working properly")
                return False
            
            logger.info(f"Ollama engine initialized with {len(successful_models)} working models")
            self.initialized = True
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Ollama engine: {e}")
            return False
    
    async def analyze_context(self, context) -> Any:
        """Analyze context using appropriate Ollama model"""
        if not self.initialized:
            raise RuntimeError("Engine not initialized")
        
        prompt = f"""
        Analyze the following context and provide structured analysis:
        
        Context: {getattr(context, 'text_content', str(context))}
        
        Please provide:
        1. Intent: What is the user trying to achieve?
        2. Entities: What key entities are mentioned?
        3. Required Tools: What tools might be needed?
        4. Confidence: How confident are you in this analysis?
        5. Reasoning: Explain your reasoning.
        
        Respond in JSON format.
        """
        
        response = await self.adapter.route_request(
            prompt=prompt,
            task_type="analysis",
            temperature=0.3
        )
        
        # Return structured analysis (simplified)
        from dataclasses import dataclass
        
        @dataclass
        class ContextAnalysis:
            intent: str
            entities: List[str]
            required_tools: List[str]
            confidence: float
            reasoning: str
        
        return ContextAnalysis(
            intent="analyze_context",
            entities=["context"],
            required_tools=[],
            confidence=0.8,
            reasoning=response.content
        )
    
    async def generate_answer(self, analysis, tools: List[Any] = None) -> Any:
        """Generate answer based on context analysis"""
        if not self.initialized:
            raise RuntimeError("Engine not initialized")
        
        prompt = f"""
        Based on the following analysis, generate a comprehensive answer:
        
        Intent: {getattr(analysis, 'intent', 'unknown')}
        Entities: {getattr(analysis, 'entities', [])}
        Required Tools: {getattr(analysis, 'required_tools', [])}
        Reasoning: {getattr(analysis, 'reasoning', '')}
        
        Please provide a clear, helpful, and accurate response.
        """
        
        response = await self.adapter.route_request(
            prompt=prompt,
            task_type="text_generation",
            temperature=0.7
        )
        
        # Return structured answer
        from dataclasses import dataclass
        
        @dataclass
        class FinalAnswer:
            answer: str
            confidence: float
            tools_used: List[str]
            processing_time: float
            metadata: Dict[str, Any]
        
        return FinalAnswer(
            answer=response.content,
            confidence=getattr(analysis, 'confidence', 0.8),
            tools_used=getattr(analysis, 'required_tools', []),
            processing_time=response.processing_time,
            metadata={
                "model": response.model,
                "ollama_model": response.metadata.get("ollama_model"),
                "timestamp": time.time()
            }
        )

# Example usage and testing
async def main():
    """Example usage of Ollama integration"""
    engine = OllamaQwen3OmniEngine()
    
    if await engine.initialize():
        logger.info("Ollama engine initialized successfully")
        
        # Test context analysis
        class MockContext:
            text_content = "What is the Agentic LLM Core system?"
        
        context = MockContext()
        analysis = await engine.analyze_context(context)
        answer = await engine.generate_answer(analysis)
        
        logger.info(f"Answer: {answer.answer}")
        logger.info(f"Processing time: {answer.processing_time:.2f}s")
        logger.info(f"Model used: {answer.metadata.get('model')}")
    else:
        logger.error("Failed to initialize Ollama engine")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
