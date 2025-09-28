#!/usr/bin/env python3
"""
Hybrid Vector Store Implementation
Combines PostgreSQL persistence with Redis caching for optimal performance
Based on HRM-enhanced AI model suggestions from continuous improvement loop
"""

import asyncio
import json
import logging
import time
import hashlib
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import numpy as np

# Redis imports
try:
    import redis
    import redis.asyncio as aioredis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logging.warning("Redis not available. Install with: pip install redis")

# PostgreSQL imports (optional for testing)
try:
    import asyncpg
    from pgvector.asyncpg import register_vector
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False
    asyncpg = None
    register_vector = None

logger = logging.getLogger(__name__)

class CacheStrategy(str, Enum):
    """Different caching strategies for the hybrid store."""
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    TTL = "ttl"  # Time To Live
    ADAPTIVE = "adaptive"  # AI-driven adaptive caching
    CHAOS_DRIVEN = "chaos_driven"  # HRM chaos theory caching

@dataclass
class VectorEntry:
    """Represents a vector entry in the hybrid store."""
    id: str
    vector: np.ndarray
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    access_count: int = 0
    last_accessed: float = field(default_factory=time.time)

@dataclass
class CacheMetrics:
    """Metrics for cache performance."""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    total_queries: int = 0
    avg_response_time: float = 0.0
    
    @property
    def hit_rate(self) -> float:
        return self.hits / max(1, self.total_queries)

class HybridVectorStore:
    """
    Hybrid vector store combining PostgreSQL persistence with Redis caching.
    Implements HRM-inspired improvements including chaos-driven caching and
    AI-generated query optimization.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self._default_config()
        self.logger = logging.getLogger(__name__)
        
        # PostgreSQL connection
        self.pg_pool: Optional[asyncpg.Pool] = None
        
        # Redis connection
        self.redis_client: Optional[aioredis.Redis] = None
        self.redis_available = REDIS_AVAILABLE and self.config.get("enable_redis", True)
        
        # Cache metrics
        self.cache_metrics = CacheMetrics()
        
        # HRM-inspired components
        self.chaos_factor = self.config.get("chaos_factor", 0.1)
        self.adaptive_threshold = self.config.get("adaptive_threshold", 0.8)
        self.query_patterns = {}  # For AI-driven optimization
        
        # Dynamic query optimization
        self.query_randomization_enabled = self.config.get("query_randomization", True)
        self.optimization_history = []
        
    def _default_config(self) -> Dict:
        return {
            "postgresql": {
                "host": "localhost",
                "port": 5432,
                "database": "agentic_llm_core",
                "user": "postgres",
                "password": "password",
                "min_connections": 5,
                "max_connections": 20
            },
            "redis": {
                "host": "localhost",
                "port": 6379,
                "db": 0,
                "password": None,
                "max_connections": 10
            },
            "cache_strategy": CacheStrategy.ADAPTIVE,
            "cache_ttl": 3600,  # 1 hour
            "max_cache_size": 10000,
            "enable_redis": True,
            "chaos_factor": 0.1,
            "adaptive_threshold": 0.8,
            "query_randomization": True,
            "vector_dimension": 1536
        }
    
    async def initialize(self):
        """Initialize both PostgreSQL and Redis connections."""
        await self._init_postgresql()
        if self.redis_available:
            await self._init_redis()
        
        self.logger.info(f"Hybrid vector store initialized (Redis: {self.redis_available})")
    
    async def _init_postgresql(self):
        """Initialize PostgreSQL connection pool."""
        if not POSTGRES_AVAILABLE:
            self.logger.warning("PostgreSQL not available - running in mock mode")
            return
            
        pg_config = self.config["postgresql"]
        
        try:
            self.pg_pool = await asyncpg.create_pool(
                host=pg_config["host"],
                port=pg_config["port"],
                database=pg_config["database"],
                user=pg_config["user"],
                password=pg_config["password"],
                min_size=pg_config["min_connections"],
                max_size=pg_config["max_connections"]
            )
            
            # Register pgvector extension
            async with self.pg_pool.acquire() as conn:
                await register_vector(conn)
                
                # Create table if not exists
                await conn.execute("""
                    CREATE EXTENSION IF NOT EXISTS vector;
                    CREATE TABLE IF NOT EXISTS vectors (
                        id TEXT PRIMARY KEY,
                        vector vector(%s),
                        metadata JSONB,
                        created_at TIMESTAMP DEFAULT NOW(),
                        updated_at TIMESTAMP DEFAULT NOW(),
                        access_count INTEGER DEFAULT 0,
                        last_accessed TIMESTAMP DEFAULT NOW()
                    );
                    CREATE INDEX IF NOT EXISTS idx_vectors_vector ON vectors USING ivfflat (vector vector_cosine_ops);
                    CREATE INDEX IF NOT EXISTS idx_vectors_metadata ON vectors USING gin (metadata);
                """, self.config["vector_dimension"])
        except Exception as e:
            self.logger.warning(f"PostgreSQL connection failed: {e} - running in mock mode")
            self.pg_pool = None
    
    async def _init_redis(self):
        """Initialize Redis connection."""
        if not REDIS_AVAILABLE:
            return
            
        redis_config = self.config["redis"]
        
        self.redis_client = aioredis.Redis(
            host=redis_config["host"],
            port=redis_config["port"],
            db=redis_config["db"],
            password=redis_config["password"],
            max_connections=redis_config["max_connections"],
            decode_responses=False  # Keep binary for numpy arrays
        )
        
        # Test connection
        try:
            await self.redis_client.ping()
            self.logger.info("Redis connection established")
        except Exception as e:
            self.logger.warning(f"Redis connection failed: {e}")
            self.redis_available = False
    
    async def store_vector(
        self, 
        vector_id: str, 
        vector: np.ndarray, 
        metadata: Optional[Dict] = None
    ) -> bool:
        """Store a vector in both PostgreSQL and Redis cache."""
        metadata = metadata or {}
        
        try:
            # Store in PostgreSQL (persistent) if available
            if self.pg_pool:
                async with self.pg_pool.acquire() as conn:
                    await conn.execute("""
                        INSERT INTO vectors (id, vector, metadata, created_at, updated_at)
                        VALUES ($1, $2, $3, NOW(), NOW())
                        ON CONFLICT (id) DO UPDATE SET
                            vector = EXCLUDED.vector,
                            metadata = EXCLUDED.metadata,
                            updated_at = NOW()
                    """, vector_id, vector.tolist(), json.dumps(metadata))
            else:
                # Mock storage for testing
                self.logger.debug(f"Mock storing vector {vector_id} (PostgreSQL not available)")
            
            # Store in Redis cache (fast access)
            if self.redis_available and self.redis_client:
                cache_key = f"vector:{vector_id}"
                cache_data = {
                    "vector": vector.tobytes(),
                    "metadata": json.dumps(metadata),
                    "timestamp": time.time()
                }
                
                await self.redis_client.hset(cache_key, mapping=cache_data)
                await self.redis_client.expire(cache_key, self.config["cache_ttl"])
            
            self.logger.debug(f"Stored vector {vector_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to store vector {vector_id}: {e}")
            return False
    
    async def get_vector(self, vector_id: str) -> Optional[VectorEntry]:
        """Retrieve a vector, checking cache first, then PostgreSQL."""
        start_time = time.time()
        self.cache_metrics.total_queries += 1
        
        try:
            # Try Redis cache first
            if self.redis_available and self.redis_client:
                cache_key = f"vector:{vector_id}"
                cached_data = await self.redis_client.hgetall(cache_key)
                
                if cached_data:
                    self.cache_metrics.hits += 1
                    
                    # Deserialize cached data
                    vector = np.frombuffer(cached_data[b"vector"], dtype=np.float32)
                    metadata = json.loads(cached_data[b"metadata"].decode())
                    timestamp = float(cached_data[b"timestamp"])
                    
                    # Update access metrics
                    await self._update_access_metrics(vector_id, cached=True)
                    
                    response_time = time.time() - start_time
                    self._update_avg_response_time(response_time)
                    
                    return VectorEntry(
                        id=vector_id,
                        vector=vector,
                        metadata=metadata,
                        timestamp=timestamp,
                        last_accessed=time.time()
                    )
            
            # Cache miss - get from PostgreSQL
            self.cache_metrics.misses += 1
            
            async with self.pg_pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT vector, metadata, EXTRACT(EPOCH FROM created_at) as timestamp,
                           access_count, EXTRACT(EPOCH FROM last_accessed) as last_accessed
                    FROM vectors 
                    WHERE id = $1
                """, vector_id)
                
                if not row:
                    return None
                
                vector = np.array(row["vector"], dtype=np.float32)
                metadata = row["metadata"] or {}
                
                # Update access metrics in PostgreSQL
                await self._update_access_metrics(vector_id, cached=False)
                
                # Store in cache for future access (if using adaptive caching)
                if self._should_cache(vector_id):
                    await self._cache_vector(vector_id, vector, metadata)
                
                response_time = time.time() - start_time
                self._update_avg_response_time(response_time)
                
                return VectorEntry(
                    id=vector_id,
                    vector=vector,
                    metadata=metadata,
                    timestamp=row["timestamp"],
                    access_count=row["access_count"],
                    last_accessed=row["last_accessed"]
                )
                
        except Exception as e:
            self.logger.error(f"Failed to get vector {vector_id}: {e}")
            return None
    
    async def similarity_search(
        self, 
        query_vector: np.ndarray, 
        limit: int = 10,
        threshold: float = 0.7,
        use_chaos_optimization: bool = True
    ) -> List[Tuple[VectorEntry, float]]:
        """
        Perform similarity search with HRM-inspired optimizations.
        Includes chaos-driven query randomization and adaptive optimization.
        """
        start_time = time.time()
        
        # Apply chaos-driven query optimization
        if use_chaos_optimization and self.query_randomization_enabled:
            query_vector = self._apply_chaos_optimization(query_vector)
        
        try:
            # Generate query hash for pattern tracking
            query_hash = self._generate_query_hash(query_vector, limit, threshold)
            
            # Check if we have a cached result for similar queries
            if self.redis_available and self.redis_client:
                cached_result = await self._get_cached_search_result(query_hash)
                if cached_result:
                    self.cache_metrics.hits += 1
                    return cached_result
            
            self.cache_metrics.misses += 1
            
            # Perform similarity search in PostgreSQL
            async with self.pg_pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT id, vector, metadata, 
                           EXTRACT(EPOCH FROM created_at) as timestamp,
                           access_count,
                           EXTRACT(EPOCH FROM last_accessed) as last_accessed,
                           1 - (vector <=> $1) as similarity
                    FROM vectors
                    WHERE 1 - (vector <=> $1) > $2
                    ORDER BY vector <=> $1
                    LIMIT $3
                """, query_vector.tolist(), threshold, limit)
                
                results = []
                for row in rows:
                    vector_entry = VectorEntry(
                        id=row["id"],
                        vector=np.array(row["vector"], dtype=np.float32),
                        metadata=row["metadata"] or {},
                        timestamp=row["timestamp"],
                        access_count=row["access_count"],
                        last_accessed=row["last_accessed"]
                    )
                    results.append((vector_entry, row["similarity"]))
                
                # Cache the search result
                if self.redis_available and self.redis_client:
                    await self._cache_search_result(query_hash, results)
                
                # Update query patterns for AI optimization
                self._update_query_patterns(query_hash, len(results), time.time() - start_time)
                
                return results
                
        except Exception as e:
            self.logger.error(f"Similarity search failed: {e}")
            return []
    
    def _apply_chaos_optimization(self, query_vector: np.ndarray) -> np.ndarray:
        """Apply chaos theory-inspired query optimization."""
        if np.random.random() < self.chaos_factor:
            # Introduce controlled randomness
            noise_factor = 0.01  # Small noise to explore nearby query space
            noise = np.random.normal(0, noise_factor, query_vector.shape)
            optimized_vector = query_vector + noise
            
            # Normalize to maintain vector properties
            optimized_vector = optimized_vector / np.linalg.norm(optimized_vector)
            
            self.logger.debug("Applied chaos optimization to query vector")
            return optimized_vector
        
        return query_vector
    
    def _generate_query_hash(self, query_vector: np.ndarray, limit: int, threshold: float) -> str:
        """Generate a hash for query caching."""
        # Create a simplified hash based on vector characteristics
        vector_sum = np.sum(query_vector)
        vector_norm = np.linalg.norm(query_vector)
        
        hash_input = f"{vector_sum:.4f}_{vector_norm:.4f}_{limit}_{threshold:.2f}"
        return hashlib.md5(hash_input.encode()).hexdigest()
    
    async def _get_cached_search_result(self, query_hash: str) -> Optional[List[Tuple[VectorEntry, float]]]:
        """Get cached search result."""
        if not self.redis_client:
            return None
            
        try:
            cache_key = f"search:{query_hash}"
            cached_data = await self.redis_client.get(cache_key)
            
            if cached_data:
                # Deserialize cached search results
                data = json.loads(cached_data.decode())
                results = []
                
                for item in data:
                    vector_entry = VectorEntry(
                        id=item["id"],
                        vector=np.array(item["vector"], dtype=np.float32),
                        metadata=item["metadata"],
                        timestamp=item["timestamp"]
                    )
                    results.append((vector_entry, item["similarity"]))
                
                return results
                
        except Exception as e:
            self.logger.error(f"Failed to get cached search result: {e}")
        
        return None
    
    async def _cache_search_result(self, query_hash: str, results: List[Tuple[VectorEntry, float]]):
        """Cache search results."""
        if not self.redis_client:
            return
            
        try:
            cache_key = f"search:{query_hash}"
            
            # Serialize results
            serialized_results = []
            for vector_entry, similarity in results:
                serialized_results.append({
                    "id": vector_entry.id,
                    "vector": vector_entry.vector.tolist(),
                    "metadata": vector_entry.metadata,
                    "timestamp": vector_entry.timestamp,
                    "similarity": similarity
                })
            
            await self.redis_client.setex(
                cache_key, 
                self.config["cache_ttl"], 
                json.dumps(serialized_results)
            )
            
        except Exception as e:
            self.logger.error(f"Failed to cache search result: {e}")
    
    async def _update_access_metrics(self, vector_id: str, cached: bool):
        """Update access metrics for a vector."""
        if not cached:  # Only update PostgreSQL if not from cache
            try:
                async with self.pg_pool.acquire() as conn:
                    await conn.execute("""
                        UPDATE vectors 
                        SET access_count = access_count + 1, 
                            last_accessed = NOW()
                        WHERE id = $1
                    """, vector_id)
            except Exception as e:
                self.logger.error(f"Failed to update access metrics: {e}")
    
    def _update_avg_response_time(self, response_time: float):
        """Update average response time metric."""
        if self.cache_metrics.total_queries == 1:
            self.cache_metrics.avg_response_time = response_time
        else:
            # Exponential moving average
            alpha = 0.1
            self.cache_metrics.avg_response_time = (
                alpha * response_time + 
                (1 - alpha) * self.cache_metrics.avg_response_time
            )
    
    def _should_cache(self, vector_id: str) -> bool:
        """Determine if a vector should be cached based on strategy."""
        strategy = self.config["cache_strategy"]
        
        if strategy == CacheStrategy.CHAOS_DRIVEN:
            # Use chaos theory for caching decisions
            return np.random.random() < (self.chaos_factor * 2)  # Controlled randomness
        elif strategy == CacheStrategy.ADAPTIVE:
            # Use hit rate to determine caching
            return self.cache_metrics.hit_rate < self.adaptive_threshold
        else:
            return True  # Default: cache everything
    
    async def _cache_vector(self, vector_id: str, vector: np.ndarray, metadata: Dict):
        """Cache a vector in Redis."""
        if not self.redis_client:
            return
            
        try:
            cache_key = f"vector:{vector_id}"
            cache_data = {
                "vector": vector.tobytes(),
                "metadata": json.dumps(metadata),
                "timestamp": time.time()
            }
            
            await self.redis_client.hset(cache_key, mapping=cache_data)
            await self.redis_client.expire(cache_key, self.config["cache_ttl"])
            
        except Exception as e:
            self.logger.error(f"Failed to cache vector: {e}")
    
    def _update_query_patterns(self, query_hash: str, result_count: int, response_time: float):
        """Update query patterns for AI-driven optimization."""
        if query_hash not in self.query_patterns:
            self.query_patterns[query_hash] = {
                "count": 0,
                "avg_results": 0,
                "avg_response_time": 0,
                "last_seen": time.time()
            }
        
        pattern = self.query_patterns[query_hash]
        pattern["count"] += 1
        pattern["avg_results"] = (pattern["avg_results"] + result_count) / 2
        pattern["avg_response_time"] = (pattern["avg_response_time"] + response_time) / 2
        pattern["last_seen"] = time.time()
        
        # Keep only recent patterns (cleanup old ones)
        if len(self.query_patterns) > 1000:
            self._cleanup_old_patterns()
    
    def _cleanup_old_patterns(self):
        """Clean up old query patterns."""
        current_time = time.time()
        cutoff_time = current_time - 3600  # Keep patterns from last hour
        
        old_patterns = [
            hash_key for hash_key, pattern in self.query_patterns.items()
            if pattern["last_seen"] < cutoff_time
        ]
        
        for hash_key in old_patterns:
            del self.query_patterns[hash_key]
    
    async def get_cache_metrics(self) -> Dict[str, Any]:
        """Get cache performance metrics."""
        redis_info = {}
        if self.redis_available and self.redis_client:
            try:
                redis_info = await self.redis_client.info("memory")
            except Exception as e:
                self.logger.error(f"Failed to get Redis info: {e}")
        
        return {
            "cache_metrics": {
                "hits": self.cache_metrics.hits,
                "misses": self.cache_metrics.misses,
                "hit_rate": self.cache_metrics.hit_rate,
                "total_queries": self.cache_metrics.total_queries,
                "avg_response_time": self.cache_metrics.avg_response_time
            },
            "redis_available": self.redis_available,
            "redis_memory_info": redis_info,
            "query_patterns_count": len(self.query_patterns),
            "chaos_factor": self.chaos_factor,
            "adaptive_threshold": self.adaptive_threshold
        }
    
    async def close(self):
        """Close all connections."""
        if self.pg_pool:
            await self.pg_pool.close()
        
        if self.redis_client:
            await self.redis_client.close()
        
        self.logger.info("Hybrid vector store connections closed")

# Example usage and testing
async def test_hybrid_vector_store():
    """Test the hybrid vector store implementation."""
    
    # Initialize store
    store = HybridVectorStore()
    await store.initialize()
    
    # Test vector storage
    test_vector = np.random.rand(1536).astype(np.float32)
    test_metadata = {"type": "test", "category": "example"}
    
    success = await store.store_vector("test_vector_1", test_vector, test_metadata)
    print(f"Storage success: {success}")
    
    # Test vector retrieval
    retrieved = await store.get_vector("test_vector_1")
    if retrieved:
        print(f"Retrieved vector: {retrieved.id}")
        print(f"Metadata: {retrieved.metadata}")
    
    # Test similarity search
    query_vector = np.random.rand(1536).astype(np.float32)
    results = await store.similarity_search(query_vector, limit=5)
    print(f"Similarity search results: {len(results)}")
    
    # Get metrics
    metrics = await store.get_cache_metrics()
    print(f"Cache metrics: {metrics}")
    
    # Close connections
    await store.close()

if __name__ == "__main__":
    asyncio.run(test_hybrid_vector_store())
