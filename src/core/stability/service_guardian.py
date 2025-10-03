#!/usr/bin/env python3
"""
Service Guardian - Permanent solution to prevent recurring service issues
"""

import asyncio
import logging
import time
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ServiceStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"

@dataclass
class ServiceConfig:
    """Configuration for a service"""
    name: str
    url: str
    health_endpoint: str
    timeout: float = 5.0
    retry_count: int = 3
    retry_delay: float = 1.0
    fallback_handler: Optional[Callable] = None

class ServiceGuardian:
    """Permanent solution for service stability and recovery"""
    
    def __init__(self):
        self.services: Dict[str, ServiceConfig] = {}
        self.service_status: Dict[str, ServiceStatus] = {}
        self.last_health_check: Dict[str, float] = {}
        self.health_check_interval = 30.0  # seconds
        
    def register_service(self, config: ServiceConfig):
        """Register a service for monitoring"""
        self.services[config.name] = config
        self.service_status[config.name] = ServiceStatus.UNKNOWN
        logger.info(f"Registered service: {config.name}")
    
    async def check_service_health(self, service_name: str) -> ServiceStatus:
        """Check health of a specific service"""
        if service_name not in self.services:
            logger.error(f"Service {service_name} not registered")
            return ServiceStatus.UNKNOWN
            
        config = self.services[service_name]
        
        try:
            import aiohttp
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=config.timeout)) as session:
                async with session.get(f"{config.url}{config.health_endpoint}") as response:
                    if response.status == 200:
                        self.service_status[service_name] = ServiceStatus.HEALTHY
                        logger.debug(f"Service {service_name} is healthy")
                    else:
                        self.service_status[service_name] = ServiceStatus.DEGRADED
                        logger.warning(f"Service {service_name} returned status {response.status}")
                        
        except Exception as e:
            self.service_status[service_name] = ServiceStatus.UNHEALTHY
            logger.error(f"Service {service_name} health check failed: {e}")
            
            # Try fallback if available
            if config.fallback_handler:
                try:
                    fallback_result = await config.fallback_handler()
                    if fallback_result:
                        self.service_status[service_name] = ServiceStatus.DEGRADED
                        logger.info(f"Service {service_name} using fallback successfully")
                except Exception as fallback_error:
                    logger.error(f"Service {service_name} fallback also failed: {fallback_error}")
        
        self.last_health_check[service_name] = time.time()
        return self.service_status[service_name]
    
    async def health_check_all(self):
        """Check health of all registered services"""
        tasks = []
        for service_name in self.services:
            tasks.append(self.check_service_health(service_name))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    def get_service_status(self, service_name: str) -> Dict[str, Any]:
        """Get detailed status of a service"""
        if service_name not in self.services:
            return {"error": "Service not registered"}
            
        config = self.services[service_name]
        last_check = self.last_health_check.get(service_name, 0)
        
        return {
            "name": service_name,
            "url": config.url,
            "status": self.service_status[service_name].value,
            "last_health_check": last_check,
            "time_since_check": time.time() - last_check if last_check else None,
            "registered": True
        }
    
    def get_all_status(self) -> Dict[str, Any]:
        """Get status of all services"""
        return {
            service_name: self.get_service_status(service_name)
            for service_name in self.services
        }
    
    async def start_monitoring(self):
        """Start continuous health monitoring"""
        logger.info("Starting service health monitoring")
        while True:
            try:
                await self.health_check_all()
                await asyncio.sleep(self.health_check_interval)
            except Exception as e:
                logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(self.health_check_interval)

# Global instance
service_guardian = ServiceGuardian()

# Register core services
service_guardian.register_service(ServiceConfig(
    name="consolidated_api",
    url="http://localhost:8004",
    health_endpoint="/api/system/health",
    timeout=5.0
))

service_guardian.register_service(ServiceConfig(
    name="agentic_platform",
    url="http://localhost:8000",
    health_endpoint="/health",
    timeout=5.0
))

service_guardian.register_service(ServiceConfig(
    name="frontend",
    url="http://localhost:3000",
    health_endpoint="/api/system/health",
    timeout=5.0
))

service_guardian.register_service(ServiceConfig(
    name="tts",
    url="http://localhost:8087",
    health_endpoint="/health",
    timeout=5.0
))

service_guardian.register_service(ServiceConfig(
    name="whisper",
    url="http://localhost:8087",
    health_endpoint="/health",
    timeout=5.0
))
