#!/usr/bin/env python3
"""
Performance Manager for AI Assistant Platform
Comprehensive memory optimization and performance monitoring system.
"""

import gc
import logging
import os
import psutil
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import torch
import threading
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class MemoryStrategy(Enum):
    """Memory optimization strategies."""
    CONSERVATIVE = "conservative"  # Use minimal memory
    BALANCED = "balanced"          # Balance performance and memory
    PERFORMANCE = "performance"    # Prioritize performance
    DYNAMIC = "dynamic"           # Adapt based on system state

@dataclass
class MemoryStats:
    """Memory usage statistics."""
    total_gb: float
    available_gb: float
    used_gb: float
    percentage: float
    mps_available: bool
    cuda_available: bool

@dataclass
class ModelMemoryProfile:
    """Memory profile for a model."""
    model_name: str
    estimated_memory_gb: float
    actual_memory_gb: float
    load_time_seconds: float
    strategy_used: str

class PerformanceManager:
    """
    Comprehensive performance and memory management system.
    
    Features:
    - Dynamic memory allocation
    - Model loading optimization
    - Memory monitoring and cleanup
    - Performance profiling
    - Resource-aware model selection
    """
    
    def __init__(self):
        """Initialize the performance manager."""
        self.logger = logging.getLogger(__name__)
        self.memory_strategy = MemoryStrategy.BALANCED
        self.model_profiles: Dict[str, ModelMemoryProfile] = {}
        self.memory_threshold = 0.85  # 85% memory usage threshold
        self.cleanup_interval = 300  # 5 minutes
        self.monitoring_active = False
        self.monitor_thread = None
        
        # Initialize memory optimization settings
        self._optimize_system_settings()
        
        # Start monitoring
        self.start_monitoring()
    
    def _optimize_system_settings(self) -> None:
        """Optimize system-level settings for better performance."""
        self.logger.info("🔧 Optimizing system settings...")
        
        # PyTorch memory optimization
        if torch.cuda.is_available():
            torch.backends.cuda.matmul.allow_tf32 = True
            torch.backends.cudnn.allow_tf32 = True
            torch.backends.cuda.enable_flash_sdp(True)
        
        # MPS optimization
        if torch.backends.mps.is_available():
            torch.mps.empty_cache()
        
        # Environment variables for memory optimization
        os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:512"
        os.environ["TOKENIZERS_PARALLELISM"] = "false"
        
        self.logger.info("✅ System settings optimized")
    
    def get_memory_stats(self) -> MemoryStats:
        """Get current memory statistics."""
        memory = psutil.virtual_memory()
        
        return MemoryStats(
            total_gb=memory.total / 1024**3,
            available_gb=memory.available / 1024**3,
            used_gb=memory.used / 1024**3,
            percentage=memory.percent,
            mps_available=torch.backends.mps.is_available(),
            cuda_available=torch.cuda.is_available()
        )
    
    def calculate_optimal_memory_allocation(self) -> Dict[str, str]:
        """Calculate optimal memory allocation based on current system state."""
        stats = self.get_memory_stats()
        
        # Conservative allocation strategy
        if self.memory_strategy == MemoryStrategy.CONSERVATIVE:
            cpu_memory = min(stats.available_gb * 0.6, 20)  # Use 60%, max 20GB
            memory_map = {"cpu": f"{cpu_memory:.0f}GB"}
            
        # Balanced allocation strategy
        elif self.memory_strategy == MemoryStrategy.BALANCED:
            cpu_memory = min(stats.available_gb * 0.75, 30)  # Use 75%, max 30GB
            memory_map = {"cpu": f"{cpu_memory:.0f}GB"}
            
        # Performance allocation strategy
        elif self.memory_strategy == MemoryStrategy.PERFORMANCE:
            cpu_memory = min(stats.available_gb * 0.85, 50)  # Use 85%, max 50GB
            memory_map = {"cpu": f"{cpu_memory:.0f}GB"}
            
        # Dynamic allocation strategy
        else:  # DYNAMIC
            if stats.percentage < 50:
                cpu_memory = min(stats.available_gb * 0.8, 40)
            elif stats.percentage < 75:
                cpu_memory = min(stats.available_gb * 0.7, 30)
            else:
                cpu_memory = min(stats.available_gb * 0.6, 20)
            memory_map = {"cpu": f"{cpu_memory:.0f}GB"}
        
        # Add MPS if available
        if stats.mps_available:
            memory_map["mps"] = "8GB"  # Conservative MPS allocation
        
        self.logger.info(f"📊 Memory allocation: {memory_map}")
        return memory_map
    
    def should_load_model(self, model_name: str, estimated_memory_gb: float) -> bool:
        """Determine if a model should be loaded based on current memory state."""
        stats = self.get_memory_stats()
        
        # Check if we have enough memory
        if stats.available_gb < estimated_memory_gb * 1.2:  # 20% buffer
            self.logger.warning(f"❌ Insufficient memory for {model_name}: "
                              f"need {estimated_memory_gb:.1f}GB, have {stats.available_gb:.1f}GB")
            return False
        
        # Check memory threshold
        projected_usage = (stats.used_gb + estimated_memory_gb) / stats.total_gb
        if projected_usage > self.memory_threshold:
            self.logger.warning(f"⚠️ Memory threshold exceeded for {model_name}: "
                              f"projected usage {projected_usage:.1%}")
            return False
        
        return True
    
    def optimize_model_loading(self, model_name: str, model_path: str) -> Dict[str, Any]:
        """Get optimized loading configuration for a model."""
        memory_map = self.calculate_optimal_memory_allocation()
        
        # Base configuration
        config = {
            "torch_dtype": torch.float16 if torch.cuda.is_available() else torch.float32,
            "device_map": "auto",
            "trust_remote_code": True,
            "low_cpu_mem_usage": True,
            "max_memory": memory_map
        }
        
        # Add quantization for large models
        if "7B" in model_name or "13B" in model_name:
            from transformers import BitsAndBytesConfig
            config["quantization_config"] = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=True,
                bnb_4bit_compute_dtype=torch.bfloat16
            )
            self.logger.info(f"🔧 Added quantization for {model_name}")
        
        return config
    
    def record_model_profile(self, model_name: str, estimated_memory: float, 
                           actual_memory: float, load_time: float, strategy: str) -> None:
        """Record memory profile for a model."""
        profile = ModelMemoryProfile(
            model_name=model_name,
            estimated_memory_gb=estimated_memory,
            actual_memory_gb=actual_memory,
            load_time_seconds=load_time,
            strategy_used=strategy
        )
        self.model_profiles[model_name] = profile
        self.logger.info(f"📊 Recorded profile for {model_name}: "
                        f"{actual_memory:.1f}GB, {load_time:.2f}s")
    
    def cleanup_memory(self) -> None:
        """Perform memory cleanup."""
        self.logger.info("🧹 Performing memory cleanup...")
        
        # Python garbage collection
        collected = gc.collect()
        
        # PyTorch cache cleanup
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        if torch.backends.mps.is_available():
            torch.mps.empty_cache()
        
        stats = self.get_memory_stats()
        self.logger.info(f"✅ Memory cleanup complete: "
                        f"collected {collected} objects, "
                        f"available: {stats.available_gb:.1f}GB")
    
    def start_monitoring(self) -> None:
        """Start background memory monitoring."""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitor_memory, daemon=True)
        self.monitor_thread.start()
        self.logger.info("📊 Started memory monitoring")
    
    def stop_monitoring(self) -> None:
        """Stop background memory monitoring."""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
        self.logger.info("📊 Stopped memory monitoring")
    
    def _monitor_memory(self) -> None:
        """Background memory monitoring thread."""
        while self.monitoring_active:
            try:
                stats = self.get_memory_stats()
                
                # Trigger cleanup if memory usage is high
                if stats.percentage > self.memory_threshold * 100:
                    self.logger.warning(f"⚠️ High memory usage: {stats.percentage:.1f}%")
                    self.cleanup_memory()
                
                # Sleep for monitoring interval
                time.sleep(self.cleanup_interval)
                
            except Exception as e:
                self.logger.error(f"Memory monitoring error: {e}")
                time.sleep(60)  # Wait 1 minute before retrying
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report."""
        stats = self.get_memory_stats()
        
        return {
            "memory_stats": {
                "total_gb": stats.total_gb,
                "available_gb": stats.available_gb,
                "used_gb": stats.used_gb,
                "percentage": stats.percentage
            },
            "model_profiles": {
                name: {
                    "estimated_memory_gb": profile.estimated_memory_gb,
                    "actual_memory_gb": profile.actual_memory_gb,
                    "load_time_seconds": profile.load_time_seconds,
                    "strategy_used": profile.strategy_used
                }
                for name, profile in self.model_profiles.items()
            },
            "system_info": {
                "mps_available": stats.mps_available,
                "cuda_available": stats.cuda_available,
                "memory_strategy": self.memory_strategy.value,
                "monitoring_active": self.monitoring_active
            }
        }
    
    @contextmanager
    def memory_context(self, operation_name: str):
        """Context manager for memory-aware operations."""
        start_stats = self.get_memory_stats()
        start_time = time.time()
        
        self.logger.info(f"🚀 Starting {operation_name} - "
                        f"Memory: {start_stats.available_gb:.1f}GB available")
        
        try:
            yield
        finally:
            end_stats = self.get_memory_stats()
            end_time = time.time()
            
            memory_used = start_stats.available_gb - end_stats.available_gb
            duration = end_time - start_time
            
            self.logger.info(f"✅ Completed {operation_name} - "
                            f"Memory used: {memory_used:.1f}GB, "
                            f"Duration: {duration:.2f}s")

# Global performance manager instance
_performance_manager = None

def get_performance_manager() -> PerformanceManager:
    """Get the global performance manager instance."""
    global _performance_manager
    if _performance_manager is None:
        _performance_manager = PerformanceManager()
    return _performance_manager
