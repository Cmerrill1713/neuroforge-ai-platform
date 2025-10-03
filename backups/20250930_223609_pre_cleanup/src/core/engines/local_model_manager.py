#!/usr/bin/env python3
"""
Local Model Manager for NeuroForge
Unified interface for local AI models (Ollama, MLX, etc.)
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from enum import Enum

logger = logging.getLogger(__name__)

class ModelType(str, Enum):
    """Supported local model types"""
    OLLAMA = "ollama"
    MLX = "mlx"
    QWEN = "qwen"
    AIM = "aim"

class LocalModelConfig:
    """Configuration for a local model"""

    def __init__(
        self,
        name: str,
        model_type: ModelType,
        model_name: str,
        base_url: Optional[str] = None,
        model_path: Optional[str] = None,
        **kwargs
    ):
        self.name = name
        self.model_type = model_type
        self.model_name = model_name
        self.base_url = base_url
        self.model_path = model_path
        self.options = kwargs

class LocalModelManager:
    """
    Unified manager for local AI models
    Supports Ollama, MLX, and other local model platforms
    """

    def __init__(self):
        self.models: Dict[str, Any] = {}
        self.adapters: Dict[str, Any] = {}
        self.current_model: Optional[str] = None
        self.logger = logging.getLogger(__name__)

    def register_model(self, config: LocalModelConfig) -> bool:
        """
        Register a new local model

        Args:
            config: Model configuration

        Returns:
            True if registration successful
        """
        try:
            if config.model_type == ModelType.OLLAMA:
                from src.core.engines.ollama_adapter import OllamaAdapter
                adapter = OllamaAdapter(
                    base_url=config.base_url or "http://localhost:11434"
                )
                self.adapters[config.name] = adapter
                self.models[config.name] = config
                logger.info(f"Registered Ollama model: {config.name}")

            elif config.model_type == ModelType.MLX:
                from src.core.engines.mlx_adapter import MLXAdapter
                if not config.model_path:
                    logger.error(f"Model path required for MLX model: {config.name}")
                    return False
                adapter = MLXAdapter(
                    model_path=config.model_path,
                    model_name=config.name
                )
                self.adapters[config.name] = adapter
                self.models[config.name] = config
                logger.info(f"Registered MLX model: {config.name}")

            elif config.model_type == ModelType.AIM:
                from src.core.engines.aim_adapter import AIMAdapter
                adapter = AIMAdapter(model_name=config.model_name)
                self.adapters[config.name] = adapter
                self.models[config.name] = config
                logger.info(f"Registered AIM model: {config.name}")

            elif config.model_type == ModelType.QWEN:
                # Qwen models could use either Ollama or MLX
                if config.model_path:
                    # Assume MLX for local path
                    from src.core.engines.mlx_adapter import MLXAdapter
                    adapter = MLXAdapter(
                        model_path=config.model_path,
                        model_name=config.name
                    )
                else:
                    # Assume Ollama
                    from src.core.engines.ollama_adapter import OllamaAdapter
                    adapter = OllamaAdapter(
                        model_name=config.model_name,
                        base_url=config.base_url or "http://localhost:11434"
                    )
                self.adapters[config.name] = adapter
                self.models[config.name] = config
                logger.info(f"Registered Qwen model: {config.name}")

            else:
                logger.error(f"Unsupported model type: {config.model_type}")
                return False

            return True

        except Exception as e:
            logger.error(f"Failed to register model {config.name}: {e}")
            return False

    def switch_model(self, model_name: str) -> bool:
        """
        Switch to a different model

        Args:
            model_name: Name of the model to switch to

        Returns:
            True if switch successful
        """
        if model_name in self.models:
            self.current_model = model_name
            logger.info(f"Switched to model: {model_name}")
            return True
        else:
            logger.error(f"Model not registered: {model_name}")
            return False

    async def generate_text(
        self,
        prompt: str,
        model_name: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Generate text using the current or specified model

        Args:
            prompt: Input prompt
            model_name: Optional model name (uses current if None)
            **kwargs: Additional generation options

        Returns:
            Generated text
        """
        target_model = model_name or self.current_model
        if not target_model:
            raise RuntimeError("No model selected")

        if target_model not in self.adapters:
            raise RuntimeError(f"Model not available: {target_model}")

        adapter = self.adapters[target_model]
        config = self.models[target_model]

        try:
            if config.model_type == ModelType.OLLAMA:
                async with adapter:
                    return await adapter.generate(prompt, **kwargs)
            else:
                # Synchronous generation for MLX and others
                return adapter.generate_text(prompt, **kwargs)

        except Exception as e:
            logger.error(f"Generation failed with model {target_model}: {e}")
            raise

    async def chat(
        self,
        messages: List[Dict[str, str]],
        model_name: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Chat with the current or specified model

        Args:
            messages: List of message dicts
            model_name: Optional model name (uses current if None)
            **kwargs: Additional chat options

        Returns:
            Generated response
        """
        target_model = model_name or self.current_model
        if not target_model:
            raise RuntimeError("No model selected")

        if target_model not in self.adapters:
            raise RuntimeError(f"Model not available: {target_model}")

        adapter = self.adapters[target_model]
        config = self.models[target_model]

        try:
            if config.model_type == ModelType.OLLAMA:
                async with adapter:
                    response = await adapter.chat(messages, target_model, **kwargs)
                    # Extract text from Ollama response dict
                    if isinstance(response, dict):
                        return response.get("text", str(response))
                    return str(response)
            else:
                # Synchronous chat for MLX and others
                return adapter.chat(messages, **kwargs)

        except Exception as e:
            logger.error(f"Chat failed with model {target_model}: {e}")
            raise

    def list_available_models(self) -> List[str]:
        """List registered model names"""
        return list(self.models.keys())

    def get_model_info(self, model_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get information about a model"""
        target_model = model_name or self.current_model
        if not target_model or target_model not in self.models:
            return None

        config = self.models[target_model]
        adapter = self.adapters[target_model]

        info = {
            "name": config.name,
            "type": config.model_type.value,
            "model_name": config.model_name,
        }

        # Get adapter-specific info
        if hasattr(adapter, 'get_model_info'):
            try:
                # Check if the method is async
                import asyncio
                import inspect
                
                if inspect.iscoroutinefunction(adapter.get_model_info):
                    # Handle async method
                    try:
                        # Try calling with model_name parameter for async methods
                        adapter_info = asyncio.run(adapter.get_model_info(target_model))
                        info.update(adapter_info)
                    except Exception as e:
                        self.logger.warning(f"Failed to get async adapter info for {target_model}: {e}")
                else:
                    # Handle sync method
                    try:
                        # Try calling without parameters first
                        adapter_info = adapter.get_model_info()
                        info.update(adapter_info)
                    except TypeError:
                        # If that fails, try with model_name parameter
                        try:
                            adapter_info = adapter.get_model_info(target_model)
                            info.update(adapter_info)
                        except Exception as e:
                            self.logger.warning(f"Failed to get sync adapter info for {target_model}: {e}")
            except Exception as e:
                self.logger.warning(f"Failed to get adapter info for {target_model}: {e}")

        return info

    def check_model_health(self, model_name: Optional[str] = None) -> Dict[str, Any]:
        """Check health status of a model"""
        target_model = model_name or self.current_model
        if not target_model or target_model not in self.models:
            return {"status": "not_found", "model": target_model}

        config = self.models[target_model]
        adapter = self.adapters[target_model]

        try:
            if config.model_type == ModelType.OLLAMA:
                healthy = adapter.check_ollama_running()
                return {
                    "status": "healthy" if healthy else "unhealthy",
                    "model": target_model,
                    "type": "ollama",
                    "url": config.base_url
                }
            elif config.model_type == ModelType.MLX:
                healthy = adapter.loaded if hasattr(adapter, 'loaded') else False
                return {
                    "status": "healthy" if healthy else "unhealthy",
                    "model": target_model,
                    "type": "mlx",
                    "path": config.model_path
                }
            else:
                return {
                    "status": "unknown",
                    "model": target_model,
                    "type": config.model_type.value
                }

        except Exception as e:
            return {
                "status": "error",
                "model": target_model,
                "error": str(e)
            }

    def initialize_default_models(self):
        """Initialize with common default models"""
        # Try to register common Ollama models
        default_models = [
            LocalModelConfig(
                name="llama2",
                model_type=ModelType.OLLAMA,
                model_name="llama2"
            ),
            LocalModelConfig(
                name="codellama",
                model_type=ModelType.OLLAMA,
                model_name="codellama"
            ),
            LocalModelConfig(
                name="mistral",
                model_type=ModelType.OLLAMA,
                model_name="mistral"
            )
        ]

        registered = 0
        for config in default_models:
            if self.register_model(config):
                registered += 1

        logger.info(f"Initialized {registered} default models")
        return registered

# Global instance
model_manager = LocalModelManager()

# Convenience functions
async def generate_with_local_model(
    prompt: str,
    model_name: Optional[str] = None,
    **kwargs
) -> str:
    """Generate text with local model"""
    return await model_manager.generate_text(prompt, model_name, **kwargs)

async def chat_with_local_model(
    messages: List[Dict[str, str]],
    model_name: Optional[str] = None,
    **kwargs
) -> str:
    """Chat with local model"""
    return await model_manager.chat(messages, model_name, **kwargs)

# Export main components
__all__ = [
    "ModelType",
    "LocalModelConfig",
    "LocalModelManager",
    "model_manager",
    "generate_with_local_model",
    "chat_with_local_model"
]
