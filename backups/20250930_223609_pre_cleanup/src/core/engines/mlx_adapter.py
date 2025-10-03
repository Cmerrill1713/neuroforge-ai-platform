#!/usr/bin/env python3
"""
MLX Local Model Adapter for NeuroForge
Provides integration with Apple MLX models for fast local inference on Apple Silicon
"""

import logging
import time
from typing import Dict, Any, List, Optional, Union
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)

class MLXModel:
    """Represents an MLX model configuration"""

    def __init__(self, model_path: str, model_name: str = "mlx_model"):
        self.model_path = model_path
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self.vision_encoder = None
        self.vision_processor = None

    def load_model(self):
        """Load MLX model and tokenizer"""
        try:
            # Import MLX components
            from mlx_lm import load, generate
            self.model, self.tokenizer = load(self.model_path)
            logger.info(f"Loaded MLX model: {self.model_name}")
            return True
        except ImportError:
            logger.error("MLX not installed. Install with: pip install mlx mlx-lm")
            return False
        except Exception as e:
            logger.error(f"Failed to load MLX model {self.model_name}: {e}")
            return False

    def load_vision_model(self):
        """Load MLX vision model components"""
        try:
            from mlx_vlm import load, generate
            self.model, self.vision_processor = load(self.model_path)
            logger.info(f"Loaded MLX vision model: {self.model_name}")
            return True
        except ImportError:
            logger.error("MLX VLM not installed. Install with: pip install mlx-vlm")
            return False
        except Exception as e:
            logger.error(f"Failed to load MLX vision model {self.model_name}: {e}")
            return False

    def is_loaded(self) -> bool:
        """Check if model is loaded"""
        return self.model is not None

class MLXAdapter:
    """
    Adapter for MLX local models
    Optimized for Apple Silicon with fast inference
    """

    def __init__(self, model_path: str, model_name: str = "mlx_model"):
        self.model_name = model_name
        self.model_path = model_path
        self.mlx_model = MLXModel(model_path, model_name)
        self.loaded = False
        self.is_vision_model = "vlm" in model_name.lower() or "vision" in model_name.lower()

    def initialize(self) -> bool:
        """Initialize and load the MLX model"""
        if not self.loaded:
            if self.is_vision_model:
                self.loaded = self.mlx_model.load_vision_model()
            else:
                self.loaded = self.mlx_model.load_model()
        return self.loaded

    def generate_text(
        self,
        prompt: str,
        max_tokens: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.9,
        repetition_penalty: float = 1.1,
        verbose: bool = False
    ) -> str:
        """
        Generate text using MLX model

        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Top-p sampling parameter
            repetition_penalty: Repetition penalty
            verbose: Whether to show verbose output

        Returns:
            Generated text
        """
        if not self.initialize():
            raise RuntimeError("Failed to initialize MLX model")

        try:
            from mlx_lm import generate

            start_time = time.time()

            # Generate text with MLX
            response = generate(
                model=self.mlx_model.model,
                tokenizer=self.mlx_model.tokenizer,
                prompt=prompt,
                max_tokens=max_tokens,
                temp=temperature,
                top_p=top_p,
                repetition_penalty=repetition_penalty,
                verbose=verbose
            )

            generation_time = time.time() - start_time
            logger.info(f"Text generation generated in {generation_time:.2f}s")

            return response

        except Exception as e:
            logger.error(f"MLX generation failed: {e}")
            raise

    def analyze_image(
        self,
        image: Image.Image,
        prompt: str,
        max_tokens: int = 512,
        temperature: float = 0.7,
        verbose: bool = False
    ) -> str:
        """
        Analyze an image with a text prompt using MLX vision model.

        Args:
            image: PIL Image object
            prompt: Text prompt for the analysis
            max_tokens: Maximum tokens for the generated response
            temperature: Sampling temperature
            verbose: Verbose output

        Returns:
            Generated text analysis
        """
        if not self.is_vision_model:
            raise RuntimeError("This is not a vision model.")

        if not self.initialize():
            raise RuntimeError("Failed to initialize MLX vision model")

        try:
            from mlx_vlm import generate

            start_time = time.time()
            
            response = generate(
                model=self.mlx_model.model,
                processor=self.mlx_model.vision_processor,
                image=image,
                prompt=prompt,
                max_tokens=max_tokens,
                temp=temperature,
                verbose=verbose
            )

            generation_time = time.time() - start_time
            logger.info(f"Image analysis generated in {generation_time:.2f}s")
            
            return response

        except Exception as e:
            logger.error(f"MLX image analysis failed: {e}")
            raise

    def chat(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 512,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Chat with MLX model using conversation format

        Args:
            messages: List of message dicts with 'role' and 'content'
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            system_prompt: System prompt to prepend

        Returns:
            Generated response
        """
        if not self.initialize():
            raise RuntimeError("Failed to initialize MLX model")

        # Format conversation
        conversation_parts = []

        if system_prompt:
            conversation_parts.append(f"System: {system_prompt}")

        for message in messages:
            role = message.get('role', 'user')
            content = message.get('content', '')
            if role == 'system':
                conversation_parts.append(f"System: {content}")
            elif role == 'user':
                conversation_parts.append(f"Human: {content}")
            elif role == 'assistant':
                conversation_parts.append(f"Assistant: {content}")

        # Add final assistant prompt
        conversation_parts.append("Assistant:")

        # Create prompt
        prompt = "\n\n".join(conversation_parts)

        return self.generate_text(
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature
        )

    def embed_text(self, text: str) -> Optional[List[float]]:
        """
        Generate embeddings for text using MLX model

        Args:
            text: Input text to embed

        Returns:
            List of embedding values or None if not supported
        """
        # MLX models may not support embeddings directly
        # This would need model-specific implementation
        logger.warning("Embedding not implemented for MLX models")
        return None

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        return {
            "name": self.model_name,
            "path": self.model_path,
            "loaded": self.loaded,
            "type": "mlx",
            "is_vision": self.is_vision_model,
            "platform": "apple_silicon"
        }

    def unload_model(self):
        """Unload model to free memory"""
        self.mlx_model.model = None
        self.mlx_model.tokenizer = None
        self.mlx_model.vision_encoder = None
        self.mlx_model.vision_processor = None
        self.loaded = False
        logger.info(f"Unloaded MLX model: {self.model_name}")

class MLXModelManager:
    """
    Manager for multiple MLX models
    Provides model switching and memory management
    """

    def __init__(self):
        self.models: Dict[str, MLXAdapter] = {}
        self.current_model: Optional[str] = None

    def load_model(self, model_name: str, model_path: str) -> bool:
        """Load a new MLX model"""
        try:
            adapter = MLXAdapter(model_path, model_name)
            if adapter.initialize():
                self.models[model_name] = adapter
                logger.info(f"Loaded MLX model: {model_name}")
                return True
            else:
                logger.error(f"Failed to load MLX model: {model_name}")
                return False
        except Exception as e:
            logger.error(f"Error loading model {model_name}: {e}")
            return False

    def switch_model(self, model_name: str) -> bool:
        """Switch to a different model"""
        if model_name in self.models:
            self.current_model = model_name
            logger.info(f"Switched to model: {model_name}")
            return True
        else:
            logger.error(f"Model not loaded: {model_name}")
            return False

    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text with current model"""
        if not self.current_model:
            raise RuntimeError("No model selected")

        model = self.models[self.current_model]
        return model.generate_text(prompt, **kwargs)

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Chat with current model"""
        if not self.current_model:
            raise RuntimeError("No model selected")

        model = self.models[self.current_model]
        return model.chat(messages, **kwargs)

    def list_models(self) -> List[str]:
        """List loaded models"""
        return list(self.models.keys())

    def get_current_model_info(self) -> Optional[Dict[str, Any]]:
        """Get info about current model"""
        if self.current_model:
            return self.models[self.current_model].get_model_info()
        return None

    def unload_all(self):
        """Unload all models"""
        for name, model in self.models.items():
            model.unload_model()
        self.models.clear()
        self.current_model = None
        logger.info("Unloaded all MLX models")

# Convenience functions
def create_mlx_adapter(model_path: str, model_name: str = "mlx_model") -> MLXAdapter:
    """Create and initialize MLX adapter"""
    adapter = MLXAdapter(model_path, model_name)
    adapter.initialize()
    return adapter

def generate_with_mlx(
    prompt: str,
    model_path: str,
    model_name: str = "mlx_model",
    **kwargs
) -> str:
    """Convenience function for MLX text generation"""
    adapter = create_mlx_adapter(model_path, model_name)
    return adapter.generate_text(prompt, **kwargs)

def generate_with_fastvlm(
    prompt: str,
    image: Image.Image,
    model_path: str,
    model_name: str = "fastvlm",
    **kwargs
) -> str:
    """Convenience function for MLX VLM generation"""
    adapter = create_mlx_adapter(model_path, model_name)
    return adapter.analyze_image(image, prompt, **kwargs)


# Export main classes
__all__ = [
    "MLXAdapter",
    "MLXModel",
    "MLXModelManager",
    "create_mlx_adapter",
    "generate_with_mlx",
    "generate_with_fastvlm"
]
