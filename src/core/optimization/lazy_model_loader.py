#!/usr/bin/env python3
"""
Lazy Model Loader for AI Assistant Platform
Efficient model loading with on-demand initialization and memory optimization.
"""

import logging
import threading
import time
from typing import Dict, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
import torch
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class ModelState(Enum):
    """Model loading states."""
    UNLOADED = "unloaded"
    LOADING = "loading"
    LOADED = "loaded"
    ERROR = "error"

@dataclass
class ModelInfo:
    """Information about a model."""
    name: str
    model_type: str
    model_path: str
    estimated_memory_gb: float
    loader_function: Callable
    state: ModelState = ModelState.UNLOADED
    model_instance: Optional[Any] = None
    load_time: Optional[float] = None
    error_message: Optional[str] = None

class LazyModelLoader:
    """
    Lazy loading system for AI models.
    
    Features:
    - On-demand model loading
    - Memory-aware loading decisions
    - Thread-safe operations
    - Automatic cleanup
    - Performance monitoring
    """
    
    def __init__(self):
        """Initialize the lazy model loader."""
        self.logger = logging.getLogger(__name__)
        self.models: Dict[str, ModelInfo] = {}
        self.loading_locks: Dict[str, threading.Lock] = {}
        self.max_concurrent_loads = 2
        self.current_loads = 0
        self.load_semaphore = threading.Semaphore(self.max_concurrent_loads)
        
        # Import performance manager
        try:
            from src.core.optimization.performance_manager import get_performance_manager
            self.performance_manager = get_performance_manager()
        except ImportError:
            self.performance_manager = None
            self.logger.warning("Performance manager not available")
    
    def register_model(self, name: str, model_type: str, model_path: str, 
                      estimated_memory_gb: float, loader_function: Callable) -> None:
        """Register a model for lazy loading."""
        model_info = ModelInfo(
            name=name,
            model_type=model_type,
            model_path=model_path,
            estimated_memory_gb=estimated_memory_gb,
            loader_function=loader_function
        )
        
        self.models[name] = model_info
        self.loading_locks[name] = threading.Lock()
        
        self.logger.info(f"📝 Registered model: {name} ({model_type}) - "
                        f"estimated {estimated_memory_gb:.1f}GB")
    
    def get_model(self, name: str, force_reload: bool = False) -> Optional[Any]:
        """Get a model instance, loading it if necessary."""
        if name not in self.models:
            self.logger.error(f"Model {name} not registered")
            return None
        
        model_info = self.models[name]
        
        # Return existing model if loaded and not forcing reload
        if model_info.state == ModelState.LOADED and not force_reload:
            return model_info.model_instance
        
        # Check if already loading
        if model_info.state == ModelState.LOADING:
            self.logger.info(f"⏳ Model {name} is already loading, waiting...")
            with self.loading_locks[name]:
                if model_info.state == ModelState.LOADED:
                    return model_info.model_instance
                elif model_info.state == ModelState.ERROR:
                    return None
        
        # Load the model
        return self._load_model(name)
    
    def _load_model(self, name: str) -> Optional[Any]:
        """Load a model with memory optimization."""
        model_info = self.models[name]
        
        # Check memory availability
        if self.performance_manager:
            if not self.performance_manager.should_load_model(name, model_info.estimated_memory_gb):
                self.logger.warning(f"❌ Insufficient memory for {name}")
                model_info.state = ModelState.ERROR
                model_info.error_message = "Insufficient memory"
                return None
        
        # Acquire loading semaphore
        with self.load_semaphore:
            with self.loading_locks[name]:
                # Double-check state after acquiring lock
                if model_info.state == ModelState.LOADED:
                    return model_info.model_instance
                elif model_info.state == ModelState.LOADING:
                    # Another thread is loading, wait for it
                    return self._wait_for_loading(name)
                
                # Set loading state
                model_info.state = ModelState.LOADING
                self.current_loads += 1
                
                try:
                    self.logger.info(f"🔄 Loading model: {name}")
                    start_time = time.time()
                    
                    # Use performance manager context if available
                    if self.performance_manager:
                        with self.performance_manager.memory_context(f"loading_{name}"):
                            model_instance = model_info.loader_function()
                    else:
                        model_instance = model_info.loader_function()
                    
                    load_time = time.time() - start_time
                    
                    # Update model info
                    model_info.model_instance = model_instance
                    model_info.state = ModelState.LOADED
                    model_info.load_time = load_time
                    model_info.error_message = None
                    
                    # Record performance profile
                    if self.performance_manager:
                        stats = self.performance_manager.get_memory_stats()
                        actual_memory = model_info.estimated_memory_gb  # Simplified
                        self.performance_manager.record_model_profile(
                            name, model_info.estimated_memory_gb, 
                            actual_memory, load_time, "lazy_loading"
                        )
                    
                    self.logger.info(f"✅ Model {name} loaded successfully in {load_time:.2f}s")
                    return model_instance
                    
                except Exception as e:
                    self.logger.error(f"❌ Failed to load model {name}: {e}")
                    model_info.state = ModelState.ERROR
                    model_info.error_message = str(e)
                    return None
                
                finally:
                    self.current_loads -= 1
    
    def _wait_for_loading(self, name: str) -> Optional[Any]:
        """Wait for another thread to finish loading a model."""
        model_info = self.models[name]
        
        # Wait for loading to complete
        while model_info.state == ModelState.LOADING:
            time.sleep(0.1)
        
        if model_info.state == ModelState.LOADED:
            return model_info.model_instance
        else:
            return None
    
    def unload_model(self, name: str) -> bool:
        """Unload a model to free memory."""
        if name not in self.models:
            return False
        
        model_info = self.models[name]
        
        if model_info.state != ModelState.LOADED:
            return False
        
        try:
            self.logger.info(f"🗑️ Unloading model: {name}")
            
            # Clear model instance
            model_info.model_instance = None
            model_info.state = ModelState.UNLOADED
            model_info.load_time = None
            
            # Perform memory cleanup
            if self.performance_manager:
                self.performance_manager.cleanup_memory()
            
            self.logger.info(f"✅ Model {name} unloaded successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to unload model {name}: {e}")
            return False
    
    def unload_all_models(self) -> int:
        """Unload all loaded models."""
        unloaded_count = 0
        
        for name in list(self.models.keys()):
            if self.unload_model(name):
                unloaded_count += 1
        
        self.logger.info(f"🗑️ Unloaded {unloaded_count} models")
        return unloaded_count
    
    def get_model_status(self, name: str) -> Optional[Dict[str, Any]]:
        """Get status information for a model."""
        if name not in self.models:
            return None
        
        model_info = self.models[name]
        
        return {
            "name": model_info.name,
            "type": model_info.model_type,
            "state": model_info.state.value,
            "estimated_memory_gb": model_info.estimated_memory_gb,
            "load_time": model_info.load_time,
            "error_message": model_info.error_message,
            "is_loaded": model_info.state == ModelState.LOADED
        }
    
    def get_all_model_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status for all registered models."""
        return {name: self.get_model_status(name) for name in self.models.keys()}
    
    def get_memory_usage(self) -> Dict[str, float]:
        """Get estimated memory usage for all models."""
        memory_usage = {}
        
        for name, model_info in self.models.items():
            if model_info.state == ModelState.LOADED:
                memory_usage[name] = model_info.estimated_memory_gb
            else:
                memory_usage[name] = 0.0
        
        return memory_usage
    
    def optimize_memory_usage(self) -> int:
        """Optimize memory usage by unloading least recently used models."""
        if not self.performance_manager:
            return 0
        
        stats = self.performance_manager.get_memory_stats()
        
        # If memory usage is high, unload some models
        if stats.percentage > 80:
            self.logger.info("🧹 High memory usage detected, optimizing...")
            
            # Simple strategy: unload all models except the most recent
            loaded_models = [name for name, info in self.models.items() 
                           if info.state == ModelState.LOADED]
            
            # Keep only the most recently loaded model
            if len(loaded_models) > 1:
                models_to_unload = loaded_models[:-1]  # All except the last one
                
                for name in models_to_unload:
                    self.unload_model(name)
                
                return len(models_to_unload)
        
        return 0

# Global lazy loader instance
_lazy_loader = None

def get_lazy_loader() -> LazyModelLoader:
    """Get the global lazy model loader instance."""
    global _lazy_loader
    if _lazy_loader is None:
        _lazy_loader = LazyModelLoader()
    return _lazy_loader
