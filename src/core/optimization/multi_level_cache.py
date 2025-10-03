#!/usr/bin/env python3
"""
Multi-Level Caching System
Implements L1 (memory) + L2 (Redis) caching architecture for optimal performance
"""

import asyncio
import json
import logging
import time
from typing import Any, Dict, Optional, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
import hashlib
import pickle
import redis.asyncio as redis
from functools import wraps

logger = logging.getLogger(__name__)

@dataclass
class CacheStats:
    """Cache performance statistics"""
    l1_hits: int = 0
    l1_misses: int = 0
    l2_hits: int = 0
    l2_misses: int = 0
    total_requests: int = 0
    avg_response_time_ms: float = 0.0
    cache_hit_ratio: float = 0.0
    
    def update_hit_ratio(self):
        """Update cache hit ratio"""
        if self.total_requests > 0:
            total_hits = self.l1_hits + self.l2_hits
            self.cache_hit_ratio = total_hits / self.total_requests

class L1Cache:
    """Level 1: In-memory cache with LRU eviction"""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.access_times: Dict[str, float] = {}
        
    def _is_expired(self, key: str) -> bool:
        """Check if cache entry is expired"""
        if key not in self.cache:
            return True
        
        entry = self.cache[key]
        if 'expires_at' not in entry:
            return False
            
        return datetime.now().timestamp() > entry['expires_at']
    
    def _evict_lru(self):
        """Evict least recently used entry"""
        if not self.access_times:
            return
            
        lru_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
        self._remove(lru_key)
    
    def _remove(self, key: str):
        """Remove entry from cache"""
        self.cache.pop(key, None)
        self.access_times.pop(key, None)
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from L1 cache"""
        if key in self.cache and not self._is_expired(key):
            self.access_times[key] = time.time()
            return self.cache[key]['value']
        
        # Clean up expired entry
        if key in self.cache:
            self._remove(key)
        
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in L1 cache"""
        try:
            # Evict if at capacity
            if len(self.cache) >= self.max_size and key not in self.cache:
                self._evict_lru()
            
            ttl = ttl or self.default_ttl
            expires_at = datetime.now().timestamp() + ttl
            
            self.cache[key] = {
                'value': value,
                'expires_at': expires_at,
                'created_at': datetime.now().timestamp()
            }
            self.access_times[key] = time.time()
            
            return True
        except Exception as e:
            logger.error(f"L1 cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete entry from L1 cache"""
        self._remove(key)
        return True
    
    def clear(self):
        """Clear all entries"""
        self.cache.clear()
        self.access_times.clear()
    
    def size(self) -> int:
        """Get current cache size"""
        return len(self.cache)

class L2Cache:
    """Level 2: Redis cache with async operations"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379", default_ttl: int = 3600):
        self.redis_url = redis_url
        self.default_ttl = default_ttl
        self.redis_client: Optional[redis.Redis] = None
        self._connection_lock = asyncio.Lock()
    
    async def _ensure_connection(self):
        """Ensure Redis connection is established"""
        if self.redis_client is None:
            async with self._connection_lock:
                if self.redis_client is None:
                    try:
                        self.redis_client = redis.from_url(
                            self.redis_url,
                            encoding="utf-8",
                            decode_responses=False,  # We'll handle serialization
                            socket_connect_timeout=5,
                            socket_timeout=5,
                            retry_on_timeout=True,
                            health_check_interval=30
                        )
                        # Test connection
                        await self.redis_client.ping()
                        logger.info("✅ Redis L2 cache connected")
                    except Exception as e:
                        logger.error(f"❌ Redis connection failed: {e}")
                        self.redis_client = None
                        raise
    
    def _serialize(self, value: Any) -> bytes:
        """Serialize value for Redis storage"""
        try:
            return pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL)
        except Exception as e:
            logger.error(f"Serialization error: {e}")
            return pickle.dumps(str(value))
    
    def _deserialize(self, data: bytes) -> Any:
        """Deserialize value from Redis"""
        try:
            return pickle.loads(data)
        except Exception as e:
            logger.error(f"Deserialization error: {e}")
            return None
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from L2 cache"""
        try:
            await self._ensure_connection()
            data = await self.redis_client.get(key)
            if data:
                return self._deserialize(data)
            return None
        except Exception as e:
            logger.error(f"L2 cache get error: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in L2 cache"""
        try:
            await self._ensure_connection()
            ttl = ttl or self.default_ttl
            data = self._serialize(value)
            await self.redis_client.setex(key, ttl, data)
            return True
        except Exception as e:
            logger.error(f"L2 cache set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete entry from L2 cache"""
        try:
            await self._ensure_connection()
            result = await self.redis_client.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"L2 cache delete error: {e}")
            return False
    
    async def clear_pattern(self, pattern: str = "*") -> int:
        """Clear entries matching pattern"""
        try:
            await self._ensure_connection()
            keys = await self.redis_client.keys(pattern)
            if keys:
                return await self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"L2 cache clear pattern error: {e}")
            return 0

class MultiLevelCache:
    """Multi-level cache system with L1 (memory) + L2 (Redis)"""
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        l1_max_size: int = 1000,
        l1_default_ttl: int = 300,
        l2_default_ttl: int = 3600
    ):
        self.l1_cache = L1Cache(max_size=l1_max_size, default_ttl=l1_default_ttl)
        self.l2_cache = L2Cache(redis_url=redis_url, default_ttl=l2_default_ttl)
        self.stats = CacheStats()
        self._stats_lock = asyncio.Lock()
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key from arguments"""
        # Create deterministic key from arguments
        key_data = {
            'prefix': prefix,
            'args': args,
            'kwargs': sorted(kwargs.items()) if kwargs else {}
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from multi-level cache"""
        start_time = time.time()
        
        # Try L1 cache first
        value = self.l1_cache.get(key)
        if value is not None:
            async with self._stats_lock:
                self.stats.l1_hits += 1
                self.stats.total_requests += 1
                self.stats.update_hit_ratio()
            
            response_time = (time.time() - start_time) * 1000
            self._update_avg_response_time(response_time)
            logger.debug(f"L1 cache hit for key: {key[:16]}...")
            return value
        
        # Try L2 cache
        value = await self.l2_cache.get(key)
        if value is not None:
            # Promote to L1 cache
            self.l1_cache.set(key, value)
            
            async with self._stats_lock:
                self.stats.l2_hits += 1
                self.stats.total_requests += 1
                self.stats.update_hit_ratio()
            
            response_time = (time.time() - start_time) * 1000
            self._update_avg_response_time(response_time)
            logger.debug(f"L2 cache hit for key: {key[:16]}...")
            return value
        
        # Cache miss
        async with self._stats_lock:
            self.stats.l1_misses += 1
            self.stats.l2_misses += 1
            self.stats.total_requests += 1
            self.stats.update_hit_ratio()
        
        response_time = (time.time() - start_time) * 1000
        self._update_avg_response_time(response_time)
        logger.debug(f"Cache miss for key: {key[:16]}...")
        return None
    
    async def set(self, key: str, value: Any, l1_ttl: Optional[int] = None, l2_ttl: Optional[int] = None) -> bool:
        """Set value in both cache levels"""
        try:
            # Set in L1 cache
            l1_success = self.l1_cache.set(key, value, l1_ttl)
            
            # Set in L2 cache
            l2_success = await self.l2_cache.set(key, value, l2_ttl)
            
            success = l1_success and l2_success
            if success:
                logger.debug(f"Cache set for key: {key[:16]}...")
            else:
                logger.warning(f"Cache set partially failed for key: {key[:16]}...")
            
            return success
        except Exception as e:
            logger.error(f"Multi-level cache set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from both cache levels"""
        try:
            l1_success = self.l1_cache.delete(key)
            l2_success = await self.l2_cache.delete(key)
            
            success = l1_success or l2_success
            if success:
                logger.debug(f"Cache delete for key: {key[:16]}...")
            
            return success
        except Exception as e:
            logger.error(f"Multi-level cache delete error: {e}")
            return False
    
    async def clear(self, pattern: str = "*") -> int:
        """Clear cache entries"""
        try:
            l1_count = self.l1_cache.size()
            self.l1_cache.clear()
            
            l2_count = await self.l2_cache.clear_pattern(pattern)
            
            total_cleared = l1_count + l2_count
            logger.info(f"Cleared {total_cleared} cache entries")
            return total_cleared
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return 0
    
    def _update_avg_response_time(self, response_time_ms: float):
        """Update average response time"""
        if self.stats.total_requests > 0:
            # Simple moving average
            alpha = 0.1  # Smoothing factor
            self.stats.avg_response_time_ms = (
                alpha * response_time_ms + 
                (1 - alpha) * self.stats.avg_response_time_ms
            )
    
    async def get_stats(self) -> CacheStats:
        """Get cache performance statistics"""
        async with self._stats_lock:
            return CacheStats(
                l1_hits=self.stats.l1_hits,
                l1_misses=self.stats.l1_misses,
                l2_hits=self.stats.l2_hits,
                l2_misses=self.stats.l2_misses,
                total_requests=self.stats.total_requests,
                avg_response_time_ms=self.stats.avg_response_time_ms,
                cache_hit_ratio=self.stats.cache_hit_ratio
            )
    
    async def warm_cache(self, warmup_data: Dict[str, Any]):
        """Warm up cache with frequently accessed data"""
        logger.info(f"Warming cache with {len(warmup_data)} entries...")
        
        warmup_tasks = []
        for key, value in warmup_data.items():
            task = self.set(key, value)
            warmup_tasks.append(task)
        
        results = await asyncio.gather(*warmup_tasks, return_exceptions=True)
        
        successful = sum(1 for r in results if r is True)
        failed = len(results) - successful
        
        logger.info(f"Cache warmup complete: {successful} successful, {failed} failed")
        return successful, failed

def cache_key(prefix: str, ttl: Optional[int] = None, l1_ttl: Optional[int] = None, l2_ttl: Optional[int] = None):
    """Decorator for automatic caching of function results"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Generate cache key
            cache_instance = getattr(func, '_cache_instance', None)
            if not cache_instance:
                logger.warning(f"No cache instance found for {func.__name__}")
                return await func(*args, **kwargs)
            
            key = cache_instance._generate_key(prefix, func.__name__, *args, **kwargs)
            
            # Try to get from cache
            cached_result = await cache_instance.get(key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await cache_instance.set(key, result, l1_ttl, l2_ttl)
            
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # For sync functions, we'll need to handle differently
            logger.warning(f"Sync function {func.__name__} cannot use async cache decorator")
            return func(*args, **kwargs)
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

# Global cache instance
_global_cache: Optional[MultiLevelCache] = None

def get_cache() -> MultiLevelCache:
    """Get global cache instance"""
    global _global_cache
    if _global_cache is None:
        _global_cache = MultiLevelCache()
    return _global_cache

async def initialize_cache(redis_url: str = "redis://localhost:6379") -> MultiLevelCache:
    """Initialize global cache instance"""
    global _global_cache
    _global_cache = MultiLevelCache(redis_url=redis_url)
    
    # Test cache functionality
    test_key = "cache_test"
    test_value = {"test": True, "timestamp": time.time()}
    
    await _global_cache.set(test_key, test_value)
    retrieved = await _global_cache.get(test_key)
    
    if retrieved and retrieved.get("test"):
        logger.info("✅ Multi-level cache initialized successfully")
    else:
        logger.error("❌ Cache initialization test failed")
    
    return _global_cache

if __name__ == "__main__":
    # Test the cache system
    async def test_cache():
        cache = await initialize_cache()
        
        # Test basic operations
        await cache.set("test_key", {"data": "test_value"})
        result = await cache.get("test_key")
        print(f"Retrieved: {result}")
        
        # Test stats
        stats = await cache.get_stats()
        print(f"Cache stats: {stats}")
        
        # Test warmup
        warmup_data = {
            f"warmup_{i}": f"data_{i}" for i in range(10)
        }
        await cache.warm_cache(warmup_data)
        
        stats = await cache.get_stats()
        print(f"After warmup: {stats}")
    
    asyncio.run(test_cache())
