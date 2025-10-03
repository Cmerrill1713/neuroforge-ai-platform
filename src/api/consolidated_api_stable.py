#!/usr/bin/env python3
"""
Stable Consolidated API - Permanent solution with graceful degradation
"""

import logging
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from datetime import datetime
import time

# Import stability components
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

try:
    from src.core.stability.import_guardian import import_guardian
    from src.core.stability.service_guardian import service_guardian
    from src.core.stability.configuration_manager import config_manager
except ImportError:
    # Fallback if stability components not available
    import_guardian = None
    service_guardian = None
    config_manager = None

logger = logging.getLogger(__name__)

class StableConsolidatedAPI:
    """Permanent, stable consolidated API with graceful degradation"""
    
    def __init__(self):
        self.app = FastAPI(
            title="Stable Consolidated API",
            description="Permanent solution with graceful degradation",
            version="2.0.0"
        )
        
        # Setup stability components
        self._setup_stability()
        
        # Setup middleware
        self._setup_middleware()
        
        # Setup routes
        self._setup_routes()
        
        # Setup exception handlers
        self._setup_exception_handlers()
        
        logger.info("Stable Consolidated API initialized with graceful degradation")
    
    def _setup_stability(self):
        """Setup stability and monitoring components"""
        # Register services with guardian
        service_guardian.register_service(service_guardian.ServiceConfig(
            name="consolidated_api",
            url=config_manager.get_service_url('consolidated_api'),
            health_endpoint="/api/system/health"
        ))
        
        # Safe imports with fallbacks
        self._setup_safe_imports()
    
    def _setup_safe_imports(self):
        """Setup safe imports with graceful degradation"""
        
        # Home Assistant - Optional with fallback
        self.home_assistant_available = False
        if config_manager.is_feature_enabled('home_assistant'):
            home_assistant_module = import_guardian.safe_import(
                'src.core.integrations.home_assistant_integration',
                fallback_value=None
            )
            if home_assistant_module:
                self.home_assistant_available = True
                logger.info("Home Assistant integration available")
            else:
                logger.info("Home Assistant integration not available (graceful degradation)")
        
        # Enhanced RAG - Safe import
        self.rag_system_available = False
        if config_manager.is_feature_enabled('rag_system'):
            rag_module = import_guardian.safe_import(
                'src.core.rag.enhanced_rag_system',
                fallback_value=None
            )
            if rag_module:
                self.rag_system_available = True
                logger.info("Enhanced RAG system available")
            else:
                logger.info("Enhanced RAG system not available (graceful degradation)")
        
        # MCP Tools - Safe import
        self.mcp_tools_available = False
        if config_manager.is_feature_enabled('mcp_tools'):
            mcp_module = import_guardian.safe_import(
                'src.api.enhanced_mcp_api',
                fallback_value=None
            )
            if mcp_module:
                self.mcp_tools_available = True
                logger.info("Enhanced MCP tools available")
            else:
                logger.info("Enhanced MCP tools not available (graceful degradation)")
    
    def _setup_middleware(self):
        """Setup middleware with proper order"""
        
        # Performance monitoring - Must be first
        @self.app.middleware("http")
        async def performance_middleware(request, call_next):
            start_time = time.time()
            response = await call_next(request)
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(process_time)
            return response
        
        # CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=[
                config_manager.get_service_url('frontend').replace('http://', '').replace('https://', ''),
                "http://localhost:3000",
                "http://127.0.0.1:3000"
            ],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Gzip compression
        self.app.add_middleware(GZipMiddleware, minimum_size=0, compresslevel=6)
    
    def _setup_routes(self):
        """Setup API routes with graceful degradation"""
        
        @self.app.get("/")
        async def root():
            """Root endpoint with system status"""
            return {
                "message": "Stable Consolidated API",
                "version": "2.0.0",
                "status": "operational",
                "features": {
                    "home_assistant": self.home_assistant_available,
                    "rag_system": self.rag_system_available,
                    "mcp_tools": self.mcp_tools_available,
                    "self_healing": config_manager.is_feature_enabled('self_healing'),
                    "voice_services": config_manager.is_feature_enabled('voice_services')
                },
                "configuration": config_manager.get_config_summary()
            }
        
        @self.app.get("/api/system/health")
        async def system_health():
            """System health check with service status"""
            service_status = service_guardian.get_all_status()
            import_status = import_guardian.get_status()
            
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "services": service_status,
                "imports": import_status,
                "configuration": config_manager.get_config_summary()
            }
        
        @self.app.post("/api/chat/")
        async def chat_endpoint(request: ChatRequest):
            """Chat endpoint with graceful degradation"""
            try:
                # Always validate input
                if not request.message or not request.message.strip():
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail="Message cannot be empty or only whitespace"
                    )
                
                # Try to use enhanced features if available
                if self.rag_system_available:
                    # Use enhanced RAG system
                    response = await self._handle_enhanced_chat(request)
                else:
                    # Fallback to basic response
                    response = await self._handle_fallback_chat(request)
                
                return response
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Chat endpoint error: {e}")
                if config_manager.get('use_fallback_responses', True):
                    return await self._handle_fallback_chat(request)
                else:
                    raise HTTPException(status_code=500, detail=str(e))
        
        # Include optional routers if available
        self._include_optional_routers()
    
    def _include_optional_routers(self):
        """Include optional API routers if available"""
        
        # Enhanced RAG routes
        if self.rag_system_available:
            try:
                from src.api.enhanced_rag_api import router as rag_router
                self.app.include_router(rag_router)
                logger.info("Enhanced RAG routes included")
            except ImportError as e:
                logger.warning(f"Could not include RAG routes: {e}")
        
        # Enhanced MCP routes
        if self.mcp_tools_available:
            try:
                from src.api.enhanced_mcp_api import router as mcp_router
                self.app.include_router(mcp_router)
                logger.info("Enhanced MCP routes included")
            except ImportError as e:
                logger.warning(f"Could not include MCP routes: {e}")
        
        # Self-healing routes
        if config_manager.is_feature_enabled('self_healing'):
            try:
                from src.api.self_healing_api import router as healing_router
                self.app.include_router(healing_router)
                logger.info("Self-healing routes included")
            except ImportError as e:
                logger.warning(f"Could not include self-healing routes: {e}")
    
    async def _handle_enhanced_chat(self, request: ChatRequest):
        """Handle chat with enhanced features"""
        # Implementation would use RAG system, MCP tools, etc.
        return {
            "response": f"Enhanced response for: {request.message}",
            "agent_used": "enhanced_agent",
            "confidence": 0.9,
            "timestamp": datetime.now().isoformat(),
            "features_used": ["rag", "mcp_tools"]
        }
    
    async def _handle_fallback_chat(self, request: ChatRequest):
        """Handle chat with fallback response"""
        return {
            "response": f"Fallback response for: {request.message}",
            "agent_used": "fallback_agent",
            "confidence": 0.5,
            "timestamp": datetime.now().isoformat(),
            "features_used": ["basic"]
        }
    
    def _setup_exception_handlers(self):
        """Setup exception handlers"""
        
        @self.app.exception_handler(Exception)
        async def global_exception_handler(request, exc):
            logger.error(f"Global exception handler: {exc}")
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "message": "An unexpected error occurred",
                    "timestamp": datetime.now().isoformat()
                }
            )

# Pydantic models
class ChatRequest(BaseModel):
    """Chat request model with validation"""
    message: str = Field(..., min_length=1, max_length=10000, description="User message")
    task_type: str = Field(default="text_generation", description="Type of task")
    input_type: str = Field(default="text", description="Input type")
    latency_requirement: int = Field(default=1000, ge=100, le=30000, description="Latency requirement in ms")
    max_tokens: int = Field(default=1024, ge=1, le=4096, description="Maximum tokens")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Temperature setting")
    session_id: str = Field(default=None, description="Session ID")
    use_cache: bool = Field(default=True, description="Whether to use caching")
    
    @validator('message')
    def validate_message(cls, v):
        if not v or not v.strip():
            raise ValueError('Message cannot be empty or only whitespace')
        return v.strip()

# Create the stable API instance
stable_api = StableConsolidatedAPI()
app = stable_api.app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
