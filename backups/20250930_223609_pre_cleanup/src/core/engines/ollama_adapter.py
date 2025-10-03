#!/usr/bin/env python3
"""
Real Ollama Adapter for NeuroForge
Provides integration with Ollama models for local inference
"""

import logging
import asyncio
import aiohttp
import json
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class OllamaResponse:
    """Response from Ollama model"""
    text: str
    model_name: str
    tokens_used: int
    metadata: Dict[str, Any]
    processing_time: float
    created_at: datetime

class OllamaAdapter:
    """
    Real Ollama adapter for local model inference
    Connects to Ollama API for actual model calls
    """
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.session = None
        self.available_models = []
        self.logger = logging.getLogger(__name__)
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        await self._load_available_models()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def _load_available_models(self) -> None:
        """Load available models from Ollama"""
        try:
            # Ensure session is initialized
            if not self.session:
                self.session = aiohttp.ClientSession()
                
            async with self.session.get(f"{self.base_url}/api/tags") as response:
                if response.status == 200:
                    data = await response.json()
                    self.available_models = [model["name"] for model in data.get("models", [])]
                    self.logger.info(f"Loaded {len(self.available_models)} Ollama models: {self.available_models}")
                else:
                    self.logger.warning(f"Failed to load Ollama models: {response.status}")
                    self.available_models = []
        except Exception as e:
            self.logger.error(f"Error loading Ollama models: {e}")
            self.available_models = []
    
    async def generate_text(
        self, 
        prompt: str, 
        model_key: str, 
        max_tokens: int = 1000, 
        temperature: float = 0.7,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate text using Ollama model"""
        start_time = datetime.now()
        
        try:
            # Ensure we have a session
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            # Prepare the request payload
            payload = {
                "model": model_key,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": temperature,
                    **kwargs
                }
            }
            
            # Make the request to Ollama
            async with self.session.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=300)  # 5 minute timeout
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Extract response text and metadata
                    response_text = data.get("response", "")
                    tokens_used = data.get("eval_count", 0)
                    
                    processing_time = (datetime.now() - start_time).total_seconds()
                    
                    return {
                        "text": response_text,
                        "tokens_used": tokens_used,
                        "metadata": {
                            "model": model_key,
                            "temperature": temperature,
                            "max_tokens": max_tokens,
                            "processing_time": processing_time,
                            "ollama_response": data
                        },
                        "processing_time": processing_time
                    }
                else:
                    error_text = await response.text()
                    self.logger.error(f"Ollama API error {response.status}: {error_text}")
                    raise Exception(f"Ollama API error: {response.status} - {error_text}")
                    
        except Exception as e:
            self.logger.error(f"Error generating text with Ollama: {e}")
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Return fallback response
            return {
                "text": f"Error generating response with {model_key}: {str(e)}",
                "tokens_used": 0,
                "metadata": {
                    "model": model_key,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "processing_time": processing_time,
                    "error": str(e)
                },
                "processing_time": processing_time
            }
    
    async def generate_response(
        self, 
        model_key: str, 
        prompt: str, 
        max_tokens: int = 1000, 
        temperature: float = 0.7,
        **kwargs
    ) -> OllamaResponse:
        """Generate response with structured return type"""
        result = await self.generate_text(prompt, model_key, max_tokens, temperature, **kwargs)
        
        return OllamaResponse(
            text=result["text"],
            model_name=model_key,
            tokens_used=result["tokens_used"],
            metadata=result["metadata"],
            processing_time=result["processing_time"],
            created_at=datetime.now()
        )
    
    async def chat(
        self, 
        messages: List[Dict[str, str]], 
        model_key: str, 
        max_tokens: int = 1000, 
        temperature: float = 0.7,
        **kwargs
    ) -> Dict[str, Any]:
        """Chat with Ollama model using conversation format"""
        start_time = datetime.now()
        
        try:
            # Ensure we have a session
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            # Prepare the request payload for chat
            payload = {
                "model": model_key,
                "messages": messages,
                "stream": False,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": temperature,
                    **kwargs
                }
            }
            
            # Make the request to Ollama
            async with self.session.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=300)  # 5 minute timeout
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Extract response text and metadata
                    response_text = data.get("message", {}).get("content", "")
                    tokens_used = data.get("eval_count", 0)
                    
                    processing_time = (datetime.now() - start_time).total_seconds()
                    
                    return {
                        "text": response_text,
                        "tokens_used": tokens_used,
                        "metadata": {
                            "model": model_key,
                            "temperature": temperature,
                            "max_tokens": max_tokens,
                            "processing_time": processing_time,
                            "messages_count": len(messages),
                            "ollama_response": data
                        },
                        "processing_time": processing_time
                    }
                else:
                    error_text = await response.text()
                    self.logger.error(f"Ollama chat API error {response.status}: {error_text}")
                    raise Exception(f"Ollama chat API error: {response.status} - {error_text}")
                    
        except Exception as e:
            self.logger.error(f"Error chatting with Ollama: {e}")
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Return fallback response
            return {
                "text": f"Error generating chat response with {model_key}: {str(e)}",
                "tokens_used": 0,
                "metadata": {
                    "model": model_key,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "processing_time": processing_time,
                    "messages_count": len(messages),
                    "error": str(e)
                },
                "processing_time": processing_time
            }
    
    async def list_models(self) -> List[str]:
        """Get list of available models"""
        if not self.available_models:
            await self._load_available_models()
        return self.available_models.copy()
    
    async def is_model_available(self, model_name: str) -> bool:
        """Check if a specific model is available"""
        if not self.available_models:
            await self._load_available_models()
        return model_name in self.available_models
    
    async def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """Get information about a specific model"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            async with self.session.post(
                f"{self.base_url}/api/show",
                json={"name": model_name}
            ) as response:
                
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"Model {model_name} not found"}
                    
        except Exception as e:
            self.logger.error(f"Error getting model info for {model_name}: {e}")
            return {"error": str(e)}

# Global instance for easy access
_ollama_adapter = None

async def get_ollama_adapter() -> OllamaAdapter:
    """Get global Ollama adapter instance"""
    global _ollama_adapter
    if _ollama_adapter is None:
        _ollama_adapter = OllamaAdapter()
    return _ollama_adapter

async def test_ollama_connection() -> bool:
    """Test connection to Ollama"""
    try:
        async with OllamaAdapter() as adapter:
            models = await adapter.list_models()
            return len(models) > 0
    except Exception as e:
        logger.error(f"Ollama connection test failed: {e}")
        return False