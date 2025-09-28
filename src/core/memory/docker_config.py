"""
Docker-aware Configuration for Knowledge Base Adapter

This module provides configuration that leverages existing Docker infrastructure:
- PostgreSQL: agi-postgres-consolidated (port 5432)
- Weaviate: universal-ai-tools-weaviate (port 8090)
- Redis: agi-redis (for caching)
- Supabase: Multiple services for additional functionality

Created: 2024-09-24
Status: Draft
"""

from __future__ import annotations

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

from .vector_pg import PostgreSQLConfig
from .vector_weaviate import WeaviateConfig


# ============================================================================
# Docker Infrastructure Configuration
# ============================================================================

class DockerInfrastructureConfig(BaseModel):
    """Configuration for Docker infrastructure services."""
    
    # PostgreSQL Configuration (agi-postgres-consolidated)
    postgresql: PostgreSQLConfig = Field(
        default_factory=lambda: PostgreSQLConfig(
            host="localhost",
            port=5432,
            database="agi_agents",
            username="agi_user",
            password="default_db_password",
            vector_dimension=1536,
            min_connections=5,
            max_connections=20,
            enable_parallel_indexing=True,
            batch_size=1000
        ),
        description="PostgreSQL vector store configuration"
    )
    
    # Weaviate Configuration (universal-ai-tools-weaviate)
    weaviate: WeaviateConfig = Field(
        default_factory=lambda: WeaviateConfig(
            host="localhost",
            port=8090,
            scheme="http",
            class_name="Document",
            vector_dimension=1536,
            batch_size=100,
            timeout=30.0
        ),
        description="Weaviate vector store configuration"
    )
    
    # Redis Configuration (agi-redis)
    redis: Dict[str, Any] = Field(
        default_factory=lambda: {
            "host": "localhost",
            "port": 6379,
            "db": 0,
            "password": None,
            "max_connections": 20,
            "socket_timeout": 5.0,
            "socket_connect_timeout": 5.0,
            "retry_on_timeout": True
        },
        description="Redis cache configuration"
    )
    
    # Supabase Configuration
    supabase: Dict[str, Any] = Field(
        default_factory=lambda: {
            "url": "http://localhost:54321",
            "anon_key": "your_anon_key_here",
            "service_role_key": "your_service_role_key_here",
            "database_url": "postgresql://agi_user:default_db_password@localhost:54322/agi_agents"
        },
        description="Supabase configuration"
    )
    
    # Monitoring Configuration
    monitoring: Dict[str, Any] = Field(
        default_factory=lambda: {
            "prometheus_url": "http://localhost:9090",
            "grafana_url": "http://localhost:3000",
            "loki_url": "http://localhost:3100",
            "cadvisor_url": "http://localhost:8080"
        },
        description="Monitoring services configuration"
    )
    
    # Search Configuration (searxng-search)
    search: Dict[str, Any] = Field(
        default_factory=lambda: {
            "url": "http://localhost:8888",
            "timeout": 10.0,
            "max_results": 50
        },
        description="Search service configuration"
    )


# ============================================================================
# Service Discovery
# ============================================================================

class ServiceDiscovery:
    """Service discovery for Docker infrastructure."""
    
    def __init__(self, config: DockerInfrastructureConfig):
        self.config = config
    
    def get_postgresql_config(self) -> PostgreSQLConfig:
        """Get PostgreSQL configuration."""
        return self.config.postgresql
    
    def get_weaviate_config(self) -> WeaviateConfig:
        """Get Weaviate configuration."""
        return self.config.weaviate
    
    def get_redis_config(self) -> Dict[str, Any]:
        """Get Redis configuration."""
        return self.config.redis
    
    def get_supabase_config(self) -> Dict[str, Any]:
        """Get Supabase configuration."""
        return self.config.supabase
    
    def get_monitoring_config(self) -> Dict[str, Any]:
        """Get monitoring configuration."""
        return self.config.monitoring
    
    def get_search_config(self) -> Dict[str, Any]:
        """Get search configuration."""
        return self.config.search
    
    def get_all_services(self) -> Dict[str, Dict[str, Any]]:
        """Get all service configurations."""
        return {
            "postgresql": self.config.postgresql.dict(),
            "weaviate": self.config.weaviate.dict(),
            "redis": self.config.redis,
            "supabase": self.config.supabase,
            "monitoring": self.config.monitoring,
            "search": self.config.search
        }


# ============================================================================
# Docker Health Check
# ============================================================================

class DockerHealthChecker:
    """Health checker for Docker services."""
    
    def __init__(self, config: DockerInfrastructureConfig):
        self.config = config
    
    async def check_postgresql_health(self) -> Dict[str, Any]:
        """Check PostgreSQL health."""
        try:
            import asyncpg
            
            conn = await asyncpg.connect(
                host=self.config.postgresql.host,
                port=self.config.postgresql.port,
                database=self.config.postgresql.database,
                user=self.config.postgresql.username,
                password=self.config.postgresql.password
            )
            
            # Test basic connectivity
            result = await conn.fetchval("SELECT 1")
            await conn.close()
            
            return {
                "service": "postgresql",
                "status": "healthy",
                "host": self.config.postgresql.host,
                "port": self.config.postgresql.port,
                "database": self.config.postgresql.database,
                "test_result": result
            }
            
        except Exception as e:
            return {
                "service": "postgresql",
                "status": "unhealthy",
                "error": str(e),
                "host": self.config.postgresql.host,
                "port": self.config.postgresql.port
            }
    
    async def check_weaviate_health(self) -> Dict[str, Any]:
        """Check Weaviate health."""
        try:
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.config.weaviate.base_url}/v1/meta",
                    timeout=aiohttp.ClientTimeout(total=5.0)
                ) as response:
                    if response.status == 200:
                        meta = await response.json()
                        return {
                            "service": "weaviate",
                            "status": "healthy",
                            "url": self.config.weaviate.base_url,
                            "version": meta.get("version", "unknown")
                        }
                    else:
                        return {
                            "service": "weaviate",
                            "status": "unhealthy",
                            "error": f"HTTP {response.status}",
                            "url": self.config.weaviate.base_url
                        }
                        
        except Exception as e:
            return {
                "service": "weaviate",
                "status": "unhealthy",
                "error": str(e),
                "url": self.config.weaviate.base_url
            }
    
    async def check_redis_health(self) -> Dict[str, Any]:
        """Check Redis health."""
        try:
            import redis.asyncio as redis
            
            r = redis.Redis(
                host=self.config.redis["host"],
                port=self.config.redis["port"],
                db=self.config.redis["db"],
                password=self.config.redis["password"],
                socket_timeout=self.config.redis["socket_timeout"],
                socket_connect_timeout=self.config.redis["socket_connect_timeout"]
            )
            
            # Test basic connectivity
            result = await r.ping()
            await r.close()
            
            return {
                "service": "redis",
                "status": "healthy",
                "host": self.config.redis["host"],
                "port": self.config.redis["port"],
                "test_result": result
            }
            
        except Exception as e:
            return {
                "service": "redis",
                "status": "unhealthy",
                "error": str(e),
                "host": self.config.redis["host"],
                "port": self.config.redis["port"]
            }
    
    async def check_all_services(self) -> Dict[str, Dict[str, Any]]:
        """Check health of all services."""
        import asyncio
        
        # Run all health checks concurrently
        results = await asyncio.gather(
            self.check_postgresql_health(),
            self.check_weaviate_health(),
            self.check_redis_health(),
            return_exceptions=True
        )
        
        return {
            "postgresql": results[0] if not isinstance(results[0], Exception) else {"service": "postgresql", "status": "unhealthy", "error": str(results[0])},
            "weaviate": results[1] if not isinstance(results[1], Exception) else {"service": "weaviate", "status": "unhealthy", "error": str(results[1])},
            "redis": results[2] if not isinstance(results[2], Exception) else {"service": "redis", "status": "unhealthy", "error": str(results[2])}
        }


# ============================================================================
# Factory Functions
# ============================================================================

def create_docker_config(
    postgresql_overrides: Optional[Dict[str, Any]] = None,
    weaviate_overrides: Optional[Dict[str, Any]] = None,
    redis_overrides: Optional[Dict[str, Any]] = None
) -> DockerInfrastructureConfig:
    """Create Docker infrastructure configuration with optional overrides."""
    
    config = DockerInfrastructureConfig()
    
    # Apply PostgreSQL overrides
    if postgresql_overrides:
        for key, value in postgresql_overrides.items():
            if hasattr(config.postgresql, key):
                setattr(config.postgresql, key, value)
    
    # Apply Weaviate overrides
    if weaviate_overrides:
        for key, value in weaviate_overrides.items():
            if hasattr(config.weaviate, key):
                setattr(config.weaviate, key, value)
    
    # Apply Redis overrides
    if redis_overrides:
        config.redis.update(redis_overrides)
    
    return config


def create_service_discovery(config: Optional[DockerInfrastructureConfig] = None) -> ServiceDiscovery:
    """Create service discovery instance."""
    if config is None:
        config = DockerInfrastructureConfig()
    return ServiceDiscovery(config)


def create_health_checker(config: Optional[DockerInfrastructureConfig] = None) -> DockerHealthChecker:
    """Create health checker instance."""
    if config is None:
        config = DockerInfrastructureConfig()
    return DockerHealthChecker(config)


# ============================================================================
# Export all classes and functions
# ============================================================================

__all__ = [
    # Configuration
    "DockerInfrastructureConfig",
    
    # Service discovery
    "ServiceDiscovery",
    
    # Health checking
    "DockerHealthChecker",
    
    # Factory functions
    "create_docker_config",
    "create_service_discovery",
    "create_health_checker",
]
