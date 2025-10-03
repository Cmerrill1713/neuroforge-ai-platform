#!/usr/bin/env python3
""'
Performance Optimization System
Implements caching, connection pooling, and response optimization
""'

import asyncio
import time
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime, timedelta
import hashlib
import json

logger = logging.getLogger(__name__)

@dataclass
class CacheEntry:
    """TODO: Add docstring."""
    """Cache entry with metadata""'
    content: str
    timestamp: datetime
    hit_count: int = 0
    metadata: Dict[str, Any] = None

class PerformanceOptimizer:
    """TODO: Add docstring."""
    """Advanced performance optimization system""'

    def __init__(self, cache_size: int = 1000, cache_ttl: int = 300):
        """TODO: Add docstring."""
        """TODO: Add docstring.""'
        self.cache_size = cache_size
        self.cache_ttl = cache_ttl  # 5 minutes
        self.response_cache: Dict[str, CacheEntry] = {}
        self.connection_pool: Dict[str, Any] = {}
        self.performance_metrics: Dict[str, List[float]] = {
            "response_times': [],
            "cache_hits': [],
            "cache_misses': []
        }

    def _generate_cache_key(self, prompt: str, model_key: str, **kwargs) -> str:
        """TODO: Add docstring."""
        """Generate cache key for request""'
        cache_data = {
            "prompt': prompt,
            "model_key': model_key,
            "max_tokens": kwargs.get("max_tokens', 2048),
            "temperature": kwargs.get("temperature', 0.7)
        }
        cache_string = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_string.encode()).hexdigest()

    def _is_cache_valid(self, entry: CacheEntry) -> bool:
        """TODO: Add docstring."""
        """Check if cache entry is still valid""'
        return datetime.now() - entry.timestamp < timedelta(seconds=self.cache_ttl)

    async def get_cached_response(self, prompt: str, model_key: str, **kwargs) -> Optional[str]:
        """Get cached response if available""'
        cache_key = self._generate_cache_key(prompt, model_key, **kwargs)

        if cache_key in self.response_cache:
            entry = self.response_cache[cache_key]
            if self._is_cache_valid(entry):
                entry.hit_count += 1
                self.performance_metrics["cache_hits'].append(time.time())
                logger.info(f"Cache hit for key: {cache_key[:8]}...')
                return entry.content
            else:
                # Remove expired entry
                del self.response_cache[cache_key]

        self.performance_metrics["cache_misses'].append(time.time())
        logger.debug(f"Cache miss for key: {cache_key[:8]}...')
        return None

    async def cache_response(self, prompt: str, model_key: str, response: str, **kwargs):
        """Cache response for future use""'
        cache_key = self._generate_cache_key(prompt, model_key, **kwargs)

        # Implement LRU eviction if cache is full
        if len(self.response_cache) >= self.cache_size:
            # Remove oldest entry
            oldest_key = min(
                self.response_cache.keys(),
                key=lambda k: self.response_cache[k].timestamp
            )
            del self.response_cache[oldest_key]

        self.response_cache[cache_key] = CacheEntry(
            content=response,
            timestamp=datetime.now(),
            metadata={
                "model_key': model_key,
                "prompt_length': len(prompt),
                "response_length': len(response)
            }
        )

        logger.debug(f"Cached response for key: {cache_key[:8]}...')

    def record_response_time(self, response_time: float):
        """TODO: Add docstring."""
        """Record response time for analytics""'
        self.performance_metrics["response_times'].append(response_time)

        # Keep only last 100 measurements
        if len(self.performance_metrics["response_times']) > 100:
            self.performance_metrics["response_times"] = self.performance_metrics["response_times'][-100:]

    def get_performance_stats(self) -> Dict[str, Any]:
        """TODO: Add docstring."""
        """Get current performance statistics""'
        response_times = self.performance_metrics["response_times']
        cache_hits = len(self.performance_metrics["cache_hits'])
        cache_misses = len(self.performance_metrics["cache_misses'])

        stats = {
            "cache_size': len(self.response_cache),
            "cache_hit_rate': cache_hits / (cache_hits + cache_misses) if (cache_hits + cache_misses) > 0 else 0,
            "total_requests': cache_hits + cache_misses,
            "avg_response_time': sum(response_times) / len(response_times) if response_times else 0,
            "max_response_time': max(response_times) if response_times else 0,
            "min_response_time': min(response_times) if response_times else 0
        }

        return stats

    async def optimize_response(self, prompt: str, model_key: str, original_response: str, **kwargs) -> str:
        """Optimize response content for better performance""'
        # Simple optimizations
        optimized = original_response

        # Remove excessive whitespace
        optimized = " '.join(optimized.split())

        # Truncate if too long (keep first 2000 chars)
        if len(optimized) > 2000:
            optimized = optimized[:2000] + "...'

        return optimized

# Global performance optimizer instance
performance_optimizer = PerformanceOptimizer()

class OptimizedOllamaAdapter:
    """TODO: Add docstring."""
    """Performance-optimized wrapper for OllamaAdapter""'

    def __init__(self, original_adapter):
        """TODO: Add docstring."""
        """TODO: Add docstring.""'
        self.original_adapter = original_adapter
        self.optimizer = performance_optimizer

    async def generate_response(self, model_key: str, prompt: str, **kwargs):
        """Generate response with performance optimizations""'
        start_time = time.time()

        # Check cache first
        cached_response = await self.optimizer.get_cached_response(prompt, model_key, **kwargs)
        if cached_response:
            return cached_response

        # Generate new response
        response = await self.original_adapter.generate_response(model_key, prompt, **kwargs)

        # Optimize response
        optimized_content = await self.optimizer.optimize_response(
            prompt, model_key, response.content, **kwargs
        )

        # Update response with optimized content
        response.content = optimized_content

        # Cache the response
        await self.optimizer.cache_response(prompt, model_key, optimized_content, **kwargs)

        # Record performance metrics
        response_time = time.time() - start_time
        self.optimizer.record_response_time(response_time)

        return response

async def apply_performance_optimizations():
    """Apply performance optimizations to the system""'
    logger.info("🚀 Applying performance optimizations...')

    try:
        # Import the enhanced agent selector
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent / "src'))

        from enhanced_agent_selection import EnhancedAgentSelector

        # Create optimized selector
        selector = EnhancedAgentSelector()

        # Wrap the ollama adapter with performance optimizations
        if hasattr(selector, "ollama_adapter'):
            selector.ollama_adapter = OptimizedOllamaAdapter(selector.ollama_adapter)
            logger.info("✅ Performance optimizations applied to OllamaAdapter')

        # Test the optimized system
        test_prompt = "Hello, test performance optimization'
        task_request = {
            "task_type": "text_generation',
            "content': test_prompt,
            "latency_requirement': 1000
        }

        start_time = time.time()
        result = await selector.select_best_agent_with_reasoning(task_request)
        response_time = time.time() - start_time

        logger.info(f"✅ Optimized system test completed in {response_time:.2f}s')

        # Get performance stats
        stats = performance_optimizer.get_performance_stats()
        logger.info(f"📊 Performance Stats: {stats}')

        return True

    except Exception as e:
        logger.error(f"❌ Performance optimization failed: {e}')
        return False

if __name__ == "__main__':
    asyncio.run(apply_performance_optimizations())
