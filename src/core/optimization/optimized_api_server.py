#!/usr/bin/env python3
"""
Optimized API Server with Performance Optimization
Integrates multi-level caching, optimized agent selection, and performance monitoring
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import uvicorn
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import traceback

from src.core.optimization.multi_level_cache import initialize_cache, get_cache
from src.core.optimization.optimized_agent_selector import initialize_agent_selector, get_agent_selector, SelectionCriteria
from src.core.optimization.optimized_vector_store import initialize_vector_store, get_vector_store, VectorQuery
from src.core.optimization.performance_monitor import initialize_performance_monitoring, get_performance_monitor, performance_timer

logger = logging.getLogger(__name__)

# Pydantic models
class ChatRequest(BaseModel):
    message: str
    agent_id: Optional[str] = None
    show_browser_windows: Optional[bool] = False
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    response: str
    agent_used: str
    confidence: float
    response_time_ms: float
    cache_hit: bool
    performance_metrics: Dict[str, Any]

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    performance_score: float
    active_alerts: int
    cache_stats: Dict[str, Any]
    system_metrics: Dict[str, Any]

class OptimizedAPIServer:
    """Optimized API server with comprehensive performance optimization"""
    
    def __init__(self):
        self.app = FastAPI(
            title="Optimized Agentic Platform API",
            description="High-performance API with multi-level caching and optimization",
            version="2.0.0"
        )
        
        self.cache = None
        self.agent_selector = None
        self.vector_store = None
        self.performance_monitor = None
        
        self._setup_middleware()
        self._setup_routes()
    
    def _setup_middleware(self):
        """Setup performance and security middleware"""
        
        # CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Gzip compression
        self.app.add_middleware(GZipMiddleware, minimum_size=1000)
        
        # Performance monitoring middleware
        @self.app.middleware("http")
        async def performance_middleware(request: Request, call_next):
            start_time = time.time()
            
            # Add request ID for tracking
            request_id = f"req_{int(time.time() * 1000)}"
            
            try:
                response = await call_next(request)
                
                # Record performance
                duration_ms = (time.time() - start_time) * 1000
                
                if self.performance_monitor:
                    self.performance_monitor.record_request_time(duration_ms)
                    
                    if response.status_code < 400:
                        self.performance_monitor.record_success(f"{request.method}_{request.url.path}")
                    else:
                        self.performance_monitor.record_error(f"{request.method}_{request.url.path}")
                
                # Add performance headers
                response.headers["X-Response-Time"] = f"{duration_ms:.2f}ms"
                response.headers["X-Request-ID"] = request_id
                
                return response
                
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                
                if self.performance_monitor:
                    self.performance_monitor.record_request_time(duration_ms)
                    self.performance_monitor.record_error(f"{request.method}_{request.url.path}")
                
                logger.error(f"Request failed: {e}")
                raise
    
    def _setup_routes(self):
        """Setup API routes"""
        
        @self.app.get("/")
        async def root():
            return {
                "message": "Optimized Agentic Platform API",
                "version": "2.0.0",
                "status": "operational",
                "timestamp": datetime.now().isoformat()
            }
        
        @self.app.get("/health", response_model=HealthResponse)
        @performance_timer("health_check")
        async def health_check():
            """Comprehensive health check with performance metrics"""
            try:
                health = await self.performance_monitor.get_current_health()
                cache_stats = await self.cache.get_stats()
                
                return HealthResponse(
                    status="healthy" if health.overall_score > 70 else "degraded",
                    timestamp=datetime.now(),
                    performance_score=health.overall_score,
                    active_alerts=len([a for a in await self.performance_monitor.get_alerts() if not a.resolved]),
                    cache_stats=cache_stats.__dict__,
                    system_metrics={
                        "cpu_usage": health.cpu_usage,
                        "memory_usage": health.memory_usage,
                        "response_time_p95": health.response_time_p95,
                        "cache_hit_ratio": health.cache_hit_ratio,
                        "error_rate": health.error_rate
                    }
                )
            except Exception as e:
                logger.error(f"Health check failed: {e}")
                raise HTTPException(status_code=500, detail="Health check failed")
        
        @self.app.post("/api/chat/", response_model=ChatResponse)
        @performance_timer("chat_request")
        async def optimized_chat(request: ChatRequest):
            """Optimized chat endpoint with caching and agent selection"""
            start_time = time.time()
            
            try:
                # Check cache first
                cache_key = f"chat:{hash(request.message)}"
                cached_response = await self.cache.get(cache_key)
                
                if cached_response:
                    logger.debug("Chat cache hit")
                    return ChatResponse(
                        response=cached_response["response"],
                        agent_used=cached_response["agent_used"],
                        confidence=cached_response["confidence"],
                        response_time_ms=(time.time() - start_time) * 1000,
                        cache_hit=True,
                        performance_metrics=cached_response.get("performance_metrics", {})
                    )
                
                # Select optimal agent
                criteria = SelectionCriteria(
                    task_type="chat",
                    complexity="medium",
                    priority="normal",
                    context=request.context or {}
                )
                
                selection_result = await self.agent_selector.select_agent(criteria)
                
                # Simulate AI response (replace with actual AI call)
                ai_response = await self._generate_ai_response(
                    request.message,
                    selection_result.selected_agent,
                    request.context
                )
                
                # Create response
                response_data = {
                    "response": ai_response,
                    "agent_used": selection_result.selected_agent.name,
                    "confidence": selection_result.confidence,
                    "response_time_ms": (time.time() - start_time) * 1000,
                    "cache_hit": False,
                    "performance_metrics": {
                        "agent_selection_time_ms": selection_result.selection_time_ms,
                        "agent_confidence": selection_result.confidence,
                        "agent_reasoning": selection_result.reasoning
                    }
                }
                
                # Cache the response
                await self.cache.set(cache_key, response_data, l1_ttl=300, l2_ttl=3600)
                
                return ChatResponse(**response_data)
                
            except Exception as e:
                logger.error(f"Chat request failed: {e}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                raise HTTPException(status_code=500, detail="Chat request failed")
        
        @self.app.get("/api/performance/stats")
        @performance_timer("performance_stats")
        async def get_performance_stats():
            """Get comprehensive performance statistics"""
            try:
                monitor_stats = await self.performance_monitor.get_performance_summary()
                cache_stats = await self.cache.get_stats()
                agent_stats = await self.agent_selector.get_agent_stats()
                
                return {
                    "monitor_stats": monitor_stats,
                    "cache_stats": cache_stats.__dict__,
                    "agent_stats": agent_stats,
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                logger.error(f"Performance stats failed: {e}")
                raise HTTPException(status_code=500, detail="Failed to get performance stats")
        
        @self.app.get("/api/agents/")
        @performance_timer("list_agents")
        async def list_agents():
            """List available agents with performance metrics"""
            try:
                agent_stats = await self.agent_selector.get_agent_stats()
                return {
                    "agents": agent_stats["agent_performance"],
                    "total_agents": agent_stats["total_agents"],
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                logger.error(f"List agents failed: {e}")
                raise HTTPException(status_code=500, detail="Failed to list agents")
        
        @self.app.post("/api/vector/search")
        @performance_timer("vector_search")
        async def vector_search(query_data: Dict[str, Any]):
            """Optimized vector search endpoint"""
            try:
                vector_query = VectorQuery(
                    query_vector=query_data["vector"],
                    limit=query_data.get("limit", 10),
                    similarity_threshold=query_data.get("threshold", 0.7),
                    filters=query_data.get("filters"),
                    include_metadata=query_data.get("include_metadata", True)
                )
                
                results = await self.vector_store.search_similar(vector_query)
                
                return {
                    "results": [result.__dict__ for result in results],
                    "count": len(results),
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                logger.error(f"Vector search failed: {e}")
                raise HTTPException(status_code=500, detail="Vector search failed")
        
        @self.app.post("/api/optimize/performance")
        @performance_timer("optimize_performance")
        async def optimize_performance():
            """Trigger performance optimization"""
            try:
                # Optimize agent performance
                await self.agent_selector.optimize_agent_performance()
                
                # Optimize vector store
                await self.vector_store.optimize_performance()
                
                # Warm cache with frequently accessed data
                await self._warm_cache()
                
                return {
                    "status": "optimization_complete",
                    "timestamp": datetime.now().isoformat(),
                    "message": "Performance optimization completed successfully"
                }
            except Exception as e:
                logger.error(f"Performance optimization failed: {e}")
                raise HTTPException(status_code=500, detail="Performance optimization failed")
        
        @self.app.get("/api/alerts/")
        @performance_timer("get_alerts")
        async def get_alerts(severity: Optional[str] = None, unresolved_only: bool = True):
            """Get performance alerts"""
            try:
                alerts = await self.performance_monitor.get_alerts(severity, unresolved_only)
                return {
                    "alerts": [alert.__dict__ for alert in alerts],
                    "count": len(alerts),
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                logger.error(f"Get alerts failed: {e}")
                raise HTTPException(status_code=500, detail="Failed to get alerts")
    
    async def _generate_ai_response(
        self,
        message: str,
        agent: Any,
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Generate AI response (placeholder for actual AI integration)"""
        # This would integrate with your actual AI models
        # For now, return a simulated response
        
        response_templates = {
            "Lead Developer": f"As a Lead Developer, I understand you're asking about: {message}. Let me provide a comprehensive technical solution.",
            "Frontend Specialist": f"As a Frontend Specialist, I can help you with: {message}. Here's a modern, responsive approach.",
            "Data Analyst": f"As a Data Analyst, I'll analyze: {message}. Let me break down the data insights for you.",
            "Quick Responder": f"Quick answer for: {message}. Here's the essential information you need.",
            "Lightweight Assistant": f"Simple response to: {message}. Here's a straightforward solution."
        }
        
        return response_templates.get(agent.name, f"Response to: {message}")
    
    async def _warm_cache(self):
        """Warm cache with frequently accessed data"""
        try:
            warmup_data = {
                "common_responses": {
                    "hello": "Hello! How can I help you today?",
                    "help": "I'm here to assist you with various tasks. What would you like to know?",
                    "status": "System is operational and running optimally."
                },
                "agent_profiles": await self.agent_selector.get_agent_stats(),
                "system_health": await self.performance_monitor.get_current_health()
            }
            
            await self.cache.warm_cache(warmup_data)
            logger.info("✅ Cache warmed successfully")
            
        except Exception as e:
            logger.error(f"Cache warming failed: {e}")
    
    async def initialize(self):
        """Initialize all optimization components"""
        logger.info("🚀 Initializing optimized API server...")
        
        try:
            # Initialize cache
            self.cache = await initialize_cache()
            logger.info("✅ Multi-level cache initialized")
            
            # Initialize agent selector
            self.agent_selector = await initialize_agent_selector()
            logger.info("✅ Optimized agent selector initialized")
            
            # Initialize vector store
            self.vector_store = await initialize_vector_store()
            logger.info("✅ Optimized vector store initialized")
            
            # Initialize performance monitoring
            self.performance_monitor = await initialize_performance_monitoring(interval=30.0)
            logger.info("✅ Performance monitoring initialized")
            
            # Warm cache
            await self._warm_cache()
            
            logger.info("🎉 Optimized API server initialization complete!")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize optimized API server: {e}")
            raise
    
    async def shutdown(self):
        """Graceful shutdown"""
        logger.info("Shutting down optimized API server...")
        
        if self.performance_monitor:
            await self.performance_monitor.stop_monitoring()
        
        if self.vector_store:
            await self.vector_store.close()
        
        logger.info("✅ Optimized API server shutdown complete")

# Global server instance
_global_server: Optional[OptimizedAPIServer] = None

def get_optimized_server() -> OptimizedAPIServer:
    """Get global optimized server instance"""
    global _global_server
    if _global_server is None:
        _global_server = OptimizedAPIServer()
    return _global_server

async def create_optimized_server() -> OptimizedAPIServer:
    """Create and initialize optimized server"""
    server = OptimizedAPIServer()
    await server.initialize()
    return server

def run_optimized_server(host: str = "0.0.0.0", port: int = 8007):
    """Run the optimized server"""
    async def startup():
        server = await create_optimized_server()
        return server.app
    
    uvicorn.run(
        "src.core.optimization.optimized_api_server:get_optimized_server().app",
        host=host,
        port=port,
        reload=False,
        workers=1,  # Single worker for optimal performance
        access_log=True,
        log_level="info"
    )

if __name__ == "__main__":
    # Run the optimized server
    run_optimized_server(host="0.0.0.0", port=8007)
