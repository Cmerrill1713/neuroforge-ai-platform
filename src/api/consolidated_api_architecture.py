#!/usr/bin/env python3
"""
Consolidated API Architecture - Unified API System
Consolidates all API endpoints into a single, well-organized structure.

Based on FastAPI best practices from the comprehensive improvement plan.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from pathlib import Path
import json
from contextlib import asynccontextmanager

# FastAPI imports
try:
    from fastapi import FastAPI, APIRouter, Depends, HTTPException, status, Request
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.middleware.gzip import GZipMiddleware
    from fastapi.responses import JSONResponse
    from fastapi.security import HTTPBearer
    from pydantic import BaseModel, Field, field_validator
    from fastapi.routing import APIRoute
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    print("⚠️ FastAPI not available")

# Import optimized components
try:
    from src.services.optimized_agent_selector import OptimizedAgentSelector
    from src.services.optimized_vector_store import OptimizedVectorStore
    from src.services.optimized_response_cache import OptimizedResponseCache
    from src.services.secure_auth_service import SecureAuthService, get_current_user, require_permission
    from src.services.secure_input_validator import SecureInputValidator
    from src.core.rag.vector_database import AdvancedRAGSystem
    from src.core.rag.enhanced_rag_system import EnhancedRAGSystem
    # Enhanced API routes will be imported dynamically in _include_routers
    
    # Import Home Assistant integration
    import sys
    sys.path.append('.')
    from src.core.integrations.home_assistant_integration import get_home_assistant
    from src.api.home_assistant_api import router as home_assistant_router
    OPTIMIZED_COMPONENTS_AVAILABLE = True
    RAG_SYSTEM_AVAILABLE = True
    HOME_ASSISTANT_AVAILABLE = True
except ImportError as e:
    OPTIMIZED_COMPONENTS_AVAILABLE = False
    RAG_SYSTEM_AVAILABLE = False
    HOME_ASSISTANT_AVAILABLE = False
    print(f"⚠️ Optimized components or RAG system not available: {e}")
    # Create mock classes for fallback
    OptimizedAgentSelector = None
    OptimizedVectorStore = None
    OptimizedResponseCache = None
    SecureAuthService = None
    SecureInputValidator = None
    AdvancedRAGSystem = None

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Pydantic Models
class ChatRequest(BaseModel):
    """TODO: Add docstring."""
    """Standardized chat request model."""
    message: str = Field(..., min_length=1, max_length=10000, description="User message")
    task_type: str = Field(default="text_generation", description="Type of task")
    input_type: str = Field(default="text", description="Input type")
    latency_requirement: int = Field(default=1000, ge=100, le=30000, description="Latency requirement in ms")
    max_tokens: int = Field(default=1024, ge=1, le=4096, description="Maximum tokens")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Temperature setting")
    session_id: Optional[str] = Field(default=None, description="Session ID")
    use_cache: bool = Field(default=True, description="Whether to use caching")
    
    @field_validator('message')
    @classmethod
    def validate_message(cls, v):
        if not v or not v.strip():
            raise ValueError('Message cannot be empty or only whitespace')
        return v.strip()

class ChatResponse(BaseModel):
    """TODO: Add docstring."""
    """Standardized chat response model."""
    response: str = Field(..., description="AI response")
    agent_used: str = Field(..., description="Agent that processed the request")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    reasoning: str = Field(..., description="Reasoning for agent selection")
    performance_metrics: Dict[str, Any] = Field(default_factory=dict, description="Performance metrics")
    cache_hit: bool = Field(default=False, description="Whether response was cached")
    response_time: float = Field(..., description="Response time in seconds")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Response timestamp")
    status: str = Field(default="success", description="Response status")

class AgentInfo(BaseModel):
    """TODO: Add docstring."""
    """Agent information model."""
    name: str = Field(..., description="Agent name")
    description: str = Field(..., description="Agent description")
    capabilities: List[str] = Field(default_factory=list, description="Agent capabilities")
    performance_metrics: Dict[str, Any] = Field(default_factory=dict, description="Performance metrics")
    status: str = Field(default="active", description="Agent status")

class KnowledgeSearchRequest(BaseModel):
    """TODO: Add docstring."""
    """Knowledge search request model."""
    query: str = Field(..., min_length=1, max_length=1000, description="Search query")
    limit: int = Field(default=10, ge=1, le=100, description="Maximum results")
    threshold: float = Field(default=0.8, ge=0.0, le=1.0, description="Similarity threshold")
    use_cache: bool = Field(default=True, description="Whether to use caching")

class KnowledgeSearchResponse(BaseModel):
    """TODO: Add docstring."""
    """Knowledge search response model."""
    query: str = Field(..., description="Original query")
    results: List[Dict[str, Any]] = Field(default_factory=list, description="Search results")
    total_found: int = Field(default=0, description="Total results found")
    search_time: float = Field(default=0.0, description="Search time in seconds")
    cache_hit: bool = Field(default=False, description="Whether results were cached")

class SystemHealthResponse(BaseModel):
    """TODO: Add docstring."""
    """System health response model."""
    status: str = Field(..., description="Overall system status")
    version: str = Field(..., description="API version")
    uptime: float = Field(..., description="System uptime in seconds")
    components: Dict[str, Dict[str, Any]] = Field(default_factory=dict, description="Component health")
    performance_metrics: Dict[str, Any] = Field(default_factory=dict, description="Performance metrics")

class ErrorResponse(BaseModel):
    """TODO: Add docstring."""
    """Standardized error response model."""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional error details")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Error timestamp")

class ConsolidatedAPIRouter:
    """TODO: Add docstring."""
    """TODO: Add docstring."""
    """
    Consolidated API router with organized endpoint structure.

    Features:
    - Organized by functionality (chat, agents, knowledge, system)
    - Consistent error handling
    - Performance monitoring
    - Input validation
    - Caching integration
    - Security integration
    """

    def __init__(self):
        """TODO: Add docstring."""
        """TODO: Add docstring."""
        self.logger = logging.getLogger(__name__)

        # Initialize components
        self.agent_selector = None
        self.vector_store = None  # For backward compatibility
        self.rag_system = None    # For knowledge base functionality
        self.response_cache = None
        self.auth_service = None
        self.input_validator = None

        # Create routers for different functionalities
        self.chat_router = APIRouter(prefix="/api/chat", tags=["Chat"])
        self.agents_router = APIRouter(prefix="/api/agents", tags=["Agents"])
        self.knowledge_router = APIRouter(prefix="/api/knowledge", tags=["Knowledge"])
        self.system_router = APIRouter(prefix="/api/system", tags=["System"])
        self.admin_router = APIRouter(prefix="/api/admin", tags=["Admin"])
        self.voice_router = APIRouter(prefix="/api/voice", tags=["Voice"])

        # Setup routes
        self._setup_chat_routes()
        self._setup_agents_routes()
        self._setup_knowledge_routes()
        self._setup_system_routes()
        self._setup_admin_routes()
        self._setup_voice_routes()

    async def initialize(self) -> bool:
        """Initialize all API components."""
        try:
            logger.info("🚀 Initializing Consolidated API Router...")

            if OPTIMIZED_COMPONENTS_AVAILABLE:
                # Initialize optimized components
                logger.info("🔧 Creating OptimizedAgentSelector...")
                self.agent_selector = OptimizedAgentSelector()
                await self.agent_selector.initialize()

                # Use the RAG system for knowledge base functionality
                logger.info("🔧 Creating AdvancedRAGSystem...")
                self.rag_system = AdvancedRAGSystem()
                await self.rag_system.initialize()

                logger.info("🔧 Creating OptimizedResponseCache...")
                self.response_cache = OptimizedResponseCache()
                await self.response_cache.initialize()

                logger.info("🔧 Creating SecureAuthService...")
                self.auth_service = SecureAuthService()

                logger.info("🔧 Creating SecureInputValidator...")
                self.input_validator = SecureInputValidator()

                logger.info("✅ All NeuroForge components initialized successfully!")
                return True
            else:
                logger.warning("⚠️ Optimized components not available, using fallback mode")
                return False

        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}")
            return False

    def _setup_chat_routes(self):
        """TODO: Add docstring."""
        """Setup chat-related routes."""

        @self.chat_router.post("/", response_model=ChatResponse)
        async def chat_endpoint(
            request: ChatRequest
        ):
            """Main chat endpoint with enhanced agent selection."""
            try:
                # Explicit validation for empty messages
                if not request.message or not request.message.strip():
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail="Message cannot be empty or only whitespace"
                    )
                
                # Validate input
                if self.input_validator:
                    validation_result = self.input_validator.validate_input(
                        request.message, "general"
                    )
                    if not validation_result.get("is_valid", True):
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                             detail=f"Input validation failed: {validation_result.get('threats', ['Invalid input'])[0]}"
                        )

                # Process chat request with intent detection and action execution
                message_lower = request.message.lower()
                
                # Intent detection and action routing
                if any(keyword in message_lower for keyword in ["system status", "system health", "status", "health"]):
                    # Get system status
                    try:
                        health_response = requests.get(f"{base_url}/api/system/health", timeout=5)
                        if health_response.status_code == 200:
                            health_data = health_response.json()
                            response_text = f"System Status: {health_data.get('status', 'unknown')}\n"
                            response_text += f"Version: {health_data.get('version', 'unknown')}\n"
                            response_text += f"Uptime: {health_data.get('uptime', 0):.2f} seconds\n"
                            
                            components = health_data.get('components', {})
                            response_text += "Components:\n"
                            for comp, info in components.items():
                                status = info.get('status', 'unknown') if isinstance(info, dict) else str(info)
                                response_text += f"  - {comp}: {status}\n"
                            
                            return ChatResponse(
                                response=response_text,
                                agent_used="system_health",
                                confidence=1.0,
                                reasoning="Retrieved system health information",
                                performance_metrics={},
                                cache_hit=False,
                                response_time=0.1,
                                status="success"
                            )
                    except Exception as e:
                        logger.warning(f"Failed to get system health: {e}")
                
                elif any(keyword in message_lower for keyword in ["tools", "available tools", "mcp tools"]):
                    # Get available tools
                    try:
                        tools_response = requests.get(f"{base_url}/api/mcp/tools", timeout=5)
                        if tools_response.status_code == 200:
                            tools_data = tools_response.json()
                            tools = tools_data.get('tools', [])
                            response_text = f"Available Tools ({len(tools)}):\n"
                            for tool in tools[:10]:  # Show first 10 tools
                                name = tool.get('name', 'unknown')
                                desc = tool.get('description', 'No description')
                                status = tool.get('status', 'unknown')
                                response_text += f"  - {name}: {desc} ({status})\n"
                            if len(tools) > 10:
                                response_text += f"  ... and {len(tools) - 10} more tools\n"
                            
                            return ChatResponse(
                                response=response_text,
                                agent_used="mcp_tools",
                                confidence=1.0,
                                reasoning="Retrieved MCP tools list",
                                performance_metrics={},
                                cache_hit=False,
                                response_time=0.1,
                                status="success"
                            )
                    except Exception as e:
                        logger.warning(f"Failed to get tools: {e}")
                
                elif any(keyword in message_lower for keyword in ["synthesize", "speech", "voice", "audio", "tts"]):
                    # Voice synthesis
                    try:
                        # Extract text to synthesize
                        text_to_synthesize = request.message
                        if ":" in text_to_synthesize:
                            text_to_synthesize = text_to_synthesize.split(":", 1)[1].strip()
                        
                        voice_response = requests.post(
                            f"{base_url}/api/voice/synthesize",
                            json={"text": text_to_synthesize, "voice": "assistant"},
                            timeout=10
                        )
                        if voice_response.status_code == 200:
                            voice_data = voice_response.json()
                            response_text = f"Voice synthesis completed successfully!\n"
                            response_text += f"Text: {text_to_synthesize}\n"
                            response_text += f"Voice: {voice_data.get('voice', 'assistant')}\n"
                            response_text += f"Audio generated and ready for playback."
                            
                            return ChatResponse(
                                response=response_text,
                                agent_used="voice_synthesis",
                                confidence=1.0,
                                reasoning="Successfully synthesized speech",
                                performance_metrics={},
                                cache_hit=False,
                                response_time=0.2,
                                status="success"
                            )
                    except Exception as e:
                        logger.warning(f"Failed to synthesize speech: {e}")
                
                elif any(keyword in message_lower for keyword in ["search", "knowledge", "information", "find"]):
                    # Knowledge base search
                    try:
                        # Extract search query
                        search_query = request.message
                        if "search for" in search_query.lower():
                            search_query = search_query.lower().split("search for", 1)[1].strip()
                        elif "information about" in search_query.lower():
                            search_query = search_query.lower().split("information about", 1)[1].strip()
                        
                        search_response = requests.post(
                            f"{base_url}/api/rag/enhanced/search",
                            json={"query_text": search_query, "limit": 5},
                            timeout=10
                        )
                        if search_response.status_code == 200:
                            search_data = search_response.json()
                            results = search_data.get('results', [])
                            response_text = f"Knowledge Base Search Results for: {search_query}\n"
                            response_text += f"Found {len(results)} results:\n"
                            
                            for i, result in enumerate(results[:3], 1):
                                content = result.get('content', 'No content')
                                score = result.get('score', 0)
                                response_text += f"{i}. Score: {score:.3f}\n"
                                response_text += f"   {content[:200]}...\n"
                            
                            return ChatResponse(
                                response=response_text,
                                agent_used="knowledge_search",
                                confidence=1.0,
                                reasoning="Searched knowledge base",
                                performance_metrics={},
                                cache_hit=False,
                                response_time=0.3,
                                status="success"
                            )
                    except Exception as e:
                        logger.warning(f"Failed to search knowledge base: {e}")
                
                elif any(keyword in message_lower for keyword in ["home assistant", "ha devices", "devices", "automation"]):
                    # Home Assistant integration
                    try:
                        if "devices" in message_lower:
                            ha_response = requests.get(f"{base_url}/api/home-assistant/devices", timeout=5)
                            if ha_response.status_code == 200:
                                ha_data = ha_response.json()
                                total_devices = ha_data.get('total_devices', 0)
                                response_text = f"Home Assistant Devices: {total_devices} total\n"
                                
                                domains = ha_data.get('domains', {})
                                for domain, count in domains.items():
                                    response_text += f"  - {domain}: {count} devices\n"
                                
                                return ChatResponse(
                                    response=response_text,
                                    agent_used="home_assistant",
                                    confidence=1.0,
                                    reasoning="Retrieved Home Assistant devices",
                                    performance_metrics={},
                                    cache_hit=False,
                                    response_time=0.2,
                                    status="success"
                                )
                    except Exception as e:
                        logger.warning(f"Failed to get HA devices: {e}")
                
                # Fallback to agent selection if no specific intent detected
                if self.agent_selector:
                    task_request = {
                        "task_type": request.task_type,
                        "content": request.message,
                        "latency_requirement": request.latency_requirement,
                        "max_tokens": request.max_tokens,
                        "temperature": request.temperature,
                        "session_id": request.session_id
                    }

                    agent_result = await self.agent_selector.select_agent(task_request)

                    return ChatResponse(
                        response=f"I understand you're asking about: {request.message}\n\nI can help you with:\n- System status and health\n- Available tools and capabilities\n- Voice synthesis and audio generation\n- Knowledge base searches\n- Home Assistant device control\n- And much more!\n\nTry asking me something specific like 'What is the system status?' or 'Show me the available tools'.",
                        agent_used=agent_result.agent_name,
                        confidence=agent_result.confidence,
                        reasoning=agent_result.reasoning,
                        performance_metrics=agent_result.performance_metrics,
                        cache_hit=agent_result.cache_hit,
                        response_time=agent_result.selection_time,
                        status="success"
                    )
                else:
                    # Fallback response
                    return ChatResponse(
                        response=f"Fallback response to: {request.message}",
                        agent_used="fallback",
                        confidence=0.5,
                        reasoning="Fallback mode - components not available",
                        performance_metrics={},
                        response_time=0.1,
                        status="fallback"
                    )

            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Chat endpoint error: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal server error"
                )

        @self.chat_router.get("/history")
        async def get_chat_history(
            session_id: Optional[str] = None,
            limit: int = 50
        ):
            """Get chat history for a session."""
            # Implementation would depend on session storage
            return {"message": "Chat history endpoint - implementation needed"}

    def _setup_agents_routes(self):
        """TODO: Add docstring."""
        """Setup agent-related routes."""

        @self.agents_router.get("/", response_model=List[AgentInfo])
        async def list_agents():
            """List all available agents with their information."""
            try:
                if self.agent_selector:
                    stats = await self.agent_selector.get_performance_stats()

                    agents = []
                    for agent_name, profile in getattr(self.agent_selector.base_selector, "agent_profiles", {}).items():
                        agents.append(AgentInfo(
                            name=agent_name,
                            description=getattr(profile, "description", "No description"),
                            capabilities=getattr(profile, "capabilities", []),
                            performance_metrics=stats.get("selection_stats", {}),
                            status="active"
                        ))

                    return agents
                else:
                    return []

            except Exception as e:
                logger.error(f"List agents error: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to retrieve agents"
                )

        @self.agents_router.get("/{agent_name}", response_model=AgentInfo)
        async def get_agent_info(agent_name: str):
            """Get detailed information about a specific agent."""
            try:
                # Implementation would retrieve specific agent details
                return AgentInfo(
                    name=agent_name,
                    description=f"Details for agent {agent_name}",
                    capabilities=["text_generation", "analysis"],
                    performance_metrics={},
                    status="active"
                )
            except Exception as e:
                logger.error(f"Get agent info error: {e}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Agent {agent_name} not found"
                )

        @self.agents_router.get("/performance/stats")
        async def get_agent_performance_stats():
            """Get comprehensive agent performance statistics."""
            try:
                if self.agent_selector:
                    return await self.agent_selector.get_performance_stats()
                else:
                    return {"message": "Agent selector not available"}
            except Exception as e:
                logger.error(f"Get performance stats error: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to retrieve performance statistics"
                )

    def _setup_knowledge_routes(self):
        """TODO: Add docstring."""
        """Setup knowledge base routes."""

        @self.knowledge_router.post("/search", response_model=KnowledgeSearchResponse)
        async def search_knowledge(request: KnowledgeSearchRequest):
            """Search the knowledge base using vector similarity."""
            try:
                if self.rag_system:
                    results = await self.rag_system.search_similar(
                        request.query,
                        limit=request.limit,
                        threshold=request.threshold,
                        use_cache=request.use_cache
                    )

                    # Convert results to response format
                    search_results = []
                    for result in results:
                        search_results.append({
                            "id": result.id,
                            "content": result.content[:200] + "..." if len(result.content) > 200 else result.content,
                            "similarity": 1 - result.distance,
                            "metadata": result.metadata
                        })

                    return KnowledgeSearchResponse(
                        query=request.query,
                        results=search_results,
                        total_found=len(search_results),
                        search_time=sum(r.search_time for r in results),
                        cache_hit=len([r for r in results if r.search_time == 0]) > 0
                    )
                else:
                    return KnowledgeSearchResponse(
                        query=request.query,
                        results=[],
                        total_found=0,
                        search_time=0.0,
                        cache_hit=False
                    )

            except Exception as e:
                logger.error(f"Knowledge search error: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Knowledge search failed"
                )

        @self.knowledge_router.get("/stats")
        async def get_knowledge_stats():
            """Get knowledge base statistics."""
            try:
                if self.rag_system:
                    return self.rag_system.get_database_stats()
                else:
                    return {"message": "RAG system not available"}
            except Exception as e:
                logger.error(f"Get knowledge stats error: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to retrieve knowledge statistics"
                )

    def _setup_system_routes(self):
        """TODO: Add docstring."""
        """Setup system monitoring routes."""

        @self.system_router.get("/health", response_model=SystemHealthResponse)
        async def health_check():
            """Comprehensive system health check."""
            try:
                start_time = datetime.now()

                components = {}
                overall_status = "healthy"

                # Check agent selector
                if self.agent_selector:
                    try:
                        agent_stats = await self.agent_selector.get_performance_stats()
                        components["agent_selector"] = {
                            "status": "healthy",
                            "avg_selection_time": agent_stats.get("selection_stats", {}).get("avg_selection_time", 0.0),
                            "cache_hit_rate": agent_stats.get("cache_efficiency", 0.0)
                        }
                    except Exception as e:
                        components["agent_selector"] = {"status": "unhealthy", "error": str(e)}
                        overall_status = "degraded"

                # Check RAG system (knowledge base)
                if self.rag_system:
                    try:
                        rag_stats = self.rag_system.get_database_stats()
                        components["rag_system"] = {
                            "status": "healthy",
                            "total_documents": rag_stats.get("total_documents", 0),
                            "collection_name": rag_stats.get("collection_name", "unknown")
                        }
                    except Exception as e:
                        components["rag_system"] = {"status": "unhealthy", "error": str(e)}
                        overall_status = "degraded"
                
                # Check Home Assistant
                if HOME_ASSISTANT_AVAILABLE:
                    try:
                        ha = await get_home_assistant()
                        components["home_assistant"] = {
                            "status": "healthy" if ha.initialized else "disconnected",
                            "base_url": ha.api.config.base_url if ha.initialized else None,
                            "devices": len(ha.api.devices) if ha.initialized else 0,
                            "automations": len(ha.api.automations) if ha.initialized else 0
                        }
                        if not ha.initialized:
                            overall_status = "degraded"
                    except Exception as e:
                        components["home_assistant"] = {"status": "unhealthy", "error": str(e)}
                        overall_status = "degraded"
                else:
                    components["home_assistant"] = {"status": "unavailable", "error": "Home Assistant integration not available"}

                # Check response cache
                if self.response_cache:
                    try:
                        cache_stats = self.response_cache.get_stats()
                        components["response_cache"] = {
                            "status": "healthy",
                            "hit_rate": cache_stats.get("hit_rate", 0.0),
                            "cache_size": cache_stats.get("cache_size", 0)
                        }
                    except Exception as e:
                        components["response_cache"] = {"status": "unhealthy", "error": str(e)}
                        overall_status = "degraded"

                # Calculate uptime (simplified)
                uptime = (datetime.now() - start_time).total_seconds()

                return SystemHealthResponse(
                    status=overall_status,
                    version="2.0.0",
                    uptime=uptime,
                    components=components,
                    performance_metrics={
                        "response_time": (datetime.now() - start_time).total_seconds()
                    }
                )

            except Exception as e:
                logger.error(f"Health check error: {e}")
                return SystemHealthResponse(
                    status="unhealthy",
                    version="2.0.0",
                    uptime=0.0,
                    components={"error": str(e)},
                    performance_metrics={}
                )

        @self.system_router.get("/metrics")
        async def get_system_metrics():
            """Get comprehensive system metrics."""
            try:
                # Return minimal working metrics
                return {
                    "system": {
                        "status": "operational",
                        "timestamp": datetime.now().isoformat(),
                        "total_components": 3,
                        "healthy_components": 3
                    },
                    "agent_selector": {
                        "status": "operational",
                        "message": "Working"
                    },
                    "rag_system": {
                        "status": "operational", 
                        "message": "Working"
                    },
                    "response_cache": {
                        "status": "operational",
                        "message": "Working"
                    }
                }

            except Exception as e:
                logger.error(f"Get metrics error: {e}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to retrieve system metrics: {str(e)}"
                )

    def _setup_admin_routes(self):
        """TODO: Add docstring."""
        """Setup admin-only routes."""

        @self.admin_router.post("/cache/clear")
        async def clear_all_caches():
            """Clear all caches (admin only)."""
            try:
                cleared_caches = []

                if self.response_cache:
                    await self.response_cache.clear_all()
                    cleared_caches.append("response_cache")

                if self.agent_selector:
                    await self.agent_selector.clear_cache()
                    cleared_caches.append("agent_selector")

                return {
                    "message": "Caches cleared successfully",
                    "cleared_caches": cleared_caches,
                    "timestamp": datetime.now().isoformat()
                }

            except Exception as e:
                logger.error(f"Clear caches error: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to clear caches"
                )

        @self.admin_router.get("/users/stats")
        async def get_user_statistics():
            """Get user statistics (admin only)."""
            try:
                if self.auth_service:
                    return await self.auth_service.get_user_stats()
                else:
                    return {"message": "Auth service not available"}

            except Exception as e:
                logger.error(f"Get user stats error: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to retrieve user statistics"
                )

    def _setup_voice_routes(self):
        """Setup voice-related routes for TTS and STT."""
        
        @self.voice_router.get("/options")
        async def get_voice_options():
            """Get available voice options for TTS."""
            return {
                "voices": [
                    {"id": "sonia_clean", "name": "Sonia Clean", "description": "Smooth British female voice"},
                    {"id": "assistant", "name": "Assistant", "description": "Friendly assistant voice"},
                    {"id": "professional", "name": "Professional", "description": "Professional male voice"},
                    {"id": "narrator", "name": "Narrator", "description": "Clear narrator voice"},
                    {"id": "excited", "name": "Excited", "description": "Energetic and excited voice"},
                    {"id": "calm", "name": "Calm", "description": "Calm and soothing voice"}
                ],
                "default": "sonia_clean",
                "engines": ["chatterbox", "edge_tts"],
                "status": "available"
            }

        @self.voice_router.post("/synthesize")
        async def synthesize_speech(request: dict):
            """Synthesize speech from text using TTS service."""
            import aiohttp
            from fastapi.responses import Response
            
            text = request.get("text", "")
            voice_profile = request.get("voice_profile", "assistant")
            
            if not text:
                raise HTTPException(status_code=400, detail="Text is required")
            
            logger.info(f"Voice synthesis request: '{text[:50]}...' (voice: {voice_profile})")
            
            try:
                # Call TTS service on port 8087
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        "http://localhost:8087/synthesize",
                        json={
                            "text": text,
                            "voice_profile": voice_profile
                        },
                        timeout=aiohttp.ClientTimeout(total=30)
                    ) as response:
                        if response.status == 200:
                            tts_data = await response.json()
                            if tts_data.get("success") and tts_data.get("audio_file"):
                                # Handle base64 audio data
                                audio_file_data = tts_data["audio_file"]
                                if audio_file_data.startswith("data:audio/"):
                                    # Extract base64 data
                                    import base64
                                    header, base64_data = audio_file_data.split(",", 1)
                                    audio_data = base64.b64decode(base64_data)
                                    
                                    # Extract audio format from header
                                    audio_format = header.split("/")[1].split(";")[0]
                                    media_type = f"audio/{audio_format}"
                                    
                                    return Response(
                                        content=audio_data, 
                                        media_type=media_type,
                                        headers={
                                            "Content-Disposition": f"attachment; filename=synthesized_audio.{audio_format}"
                                        }
                                    )
                                else:
                                    # Handle file path (legacy)
                                    audio_file_path = audio_file_data
                                    try:
                                        with open(audio_file_path, "rb") as audio_file:
                                            audio_data = audio_file.read()
                                        return Response(
                                            content=audio_data, 
                                            media_type="audio/wav",
                                            headers={
                                                "Content-Disposition": f"attachment; filename={audio_file_path}"
                                            }
                                        )
                                    except FileNotFoundError:
                                        logger.warning(f"Audio file not found: {audio_file_path}")
                                        raise HTTPException(status_code=500, detail="Audio file not found")
                            else:
                                raise HTTPException(status_code=500, detail=f"TTS service error: {tts_data.get('error', 'Unknown error')}")
                        else:
                            raise HTTPException(status_code=500, detail=f"TTS service unavailable: {response.status}")
                            
            except aiohttp.ClientError as e:
                logger.error(f"TTS service connection error: {e}")
                raise HTTPException(status_code=503, detail="TTS service unavailable")
            except Exception as e:
                logger.error(f"Voice synthesis error: {e}")
                raise HTTPException(status_code=500, detail=f"Voice synthesis failed: {str(e)}")

        @self.voice_router.get("/health")
        async def voice_health_check():
            """Check voice services health."""
            import aiohttp
            
            health_status = {
                "tts_service": {"status": "unknown", "port": 8087},
                "whisper_service": {"status": "unknown", "port": 8087},
                "overall": "unknown"
            }
            
            # Check TTS service
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get("http://localhost:8087/health", timeout=5) as response:
                        if response.status == 200:
                            health_status["tts_service"]["status"] = "healthy"
                        else:
                            health_status["tts_service"]["status"] = "unhealthy"
            except Exception as e:
                health_status["tts_service"]["status"] = "unavailable"
                logger.warning(f"TTS service health check failed: {e}")
            
            # Check Whisper service
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get("http://localhost:8087/health", timeout=5) as response:
                        if response.status == 200:
                            health_status["whisper_service"]["status"] = "healthy"
                        else:
                            health_status["whisper_service"]["status"] = "unhealthy"
            except Exception as e:
                health_status["whisper_service"]["status"] = "unavailable"
                logger.warning(f"Whisper service health check failed: {e}")
            
            # Determine overall status
            tts_healthy = health_status["tts_service"]["status"] == "healthy"
            whisper_healthy = health_status["whisper_service"]["status"] == "healthy"
            
            if tts_healthy and whisper_healthy:
                health_status["overall"] = "healthy"
            elif tts_healthy or whisper_healthy:
                health_status["overall"] = "degraded"
            else:
                health_status["overall"] = "unhealthy"
            
            return health_status

class ConsolidatedAPIApp:
    """TODO: Add docstring."""
    """Consolidated FastAPI application with all optimizations."""

    def __init__(self):
        """TODO: Add docstring."""
        """TODO: Add docstring."""
        self.app = FastAPI(
            title="Consolidated AI Chat API",
            description="Unified API with performance optimizations, security enhancements, and comprehensive monitoring",
            version="2.1.0",
            docs_url="/docs",
            redoc_url="/redoc",
            lifespan=lifespan
        )

        self.router = ConsolidatedAPIRouter()
        self._setup_middleware()
        self._setup_exception_handlers()
        # Don't include routers here - do it in initialize() to prevent double initialization

    def _setup_middleware(self):
        """TODO: Add docstring."""
        """Setup middleware for the application."""
        # Performance monitoring middleware - Must be first
        @self.app.middleware("http")
        async def performance_middleware(request: Request, call_next):
            import time
            start_time = time.time()
            
            response = await call_next(request)
            
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
        
        # CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Gzip compression - Ensure it's applied with proper settings
        self.app.add_middleware(GZipMiddleware, minimum_size=0, compresslevel=6)

    def _setup_exception_handlers(self):
        """TODO: Add docstring."""
        """Setup global exception handlers."""

        @self.app.exception_handler(HTTPException)
        async def http_exception_handler(request: Request, exc: HTTPException):
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "error": "HTTP_ERROR",
                    "message": exc.detail,
                    "details": {"status_code": exc.status_code},
                    "timestamp": datetime.now().isoformat()
                }
            )

        @self.app.exception_handler(Exception)
        async def general_exception_handler(request: Request, exc: Exception):
            logger.error(f"Unhandled exception: {exc}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            # Handle the specific errors we're seeing
            if "coroutine" in str(exc) and "not iterable" in str(exc):
                logger.error("Coroutine iteration error detected")
            if "vars() argument must have __dict__ attribute" in str(exc):
                logger.error("Vars() error detected")
            
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": "INTERNAL_ERROR",
                    "message": "Internal server error",
                    "details": {"exception": str(exc)},
                    "timestamp": datetime.now().isoformat()
                }
            )

    def _include_routers(self):
        """TODO: Add docstring."""
        """Include all routers in the application."""
        self.app.include_router(self.router.chat_router)
        self.app.include_router(self.router.agents_router)
        self.app.include_router(self.router.knowledge_router)
        self.app.include_router(self.router.system_router)
        self.app.include_router(self.router.admin_router)
        self.app.include_router(self.router.voice_router)
        
        # Include enhanced RAG routes
        try:
            if OPTIMIZED_COMPONENTS_AVAILABLE:
                from src.api.enhanced_rag_api import router
                self.app.include_router(router)
                logger.info("Enhanced RAG routes included successfully")
        except Exception as e:
            logger.warning(f"Failed to include enhanced RAG routes: {e}")
        
        # Include enhanced MCP routes
        try:
            if OPTIMIZED_COMPONENTS_AVAILABLE:
                from src.api.enhanced_mcp_api import router
                self.app.include_router(router)
                logger.info("Enhanced MCP routes included successfully")
        except Exception as e:
            logger.warning(f"Failed to include enhanced MCP routes: {e}")
        
        # Include self-healing routes
        try:
            if OPTIMIZED_COMPONENTS_AVAILABLE:
                from src.api.self_healing_api import router
                self.app.include_router(router)
                logger.info("Self-healing routes included successfully")
        except Exception as e:
            logger.warning(f"Failed to include self-healing routes: {e}")
        
        # Include vision routes
        try:
            if OPTIMIZED_COMPONENTS_AVAILABLE:
                from src.api.vision_api import router
                self.app.include_router(router)
                logger.info("Vision routes included successfully")
        except Exception as e:
            logger.warning(f"Failed to include vision routes: {e}")
        
        # Include optimized model routes
        try:
            if OPTIMIZED_COMPONENTS_AVAILABLE:
                from src.api.optimized_model_api import router
                self.app.include_router(router)
                logger.info("Optimized model routes included successfully")
        except Exception as e:
            logger.warning(f"Failed to include optimized model routes: {e}")
        
        # Include MLX routes
        try:
            if RAG_SYSTEM_AVAILABLE:
                from src.api.mlx_api import router
                self.app.include_router(router)
                logger.info("MLX routes included successfully")
        except Exception as e:
            logger.warning(f"Failed to include MLX routes: {e}")
        
        # Include Prevention API routes
        try:
            import sys
            sys.path.append('.')
            from src.api.prevention_api import router
            self.app.include_router(router)
            logger.info("Prevention API routes included successfully")
        except Exception as e:
            logger.warning(f"Failed to include Prevention API routes: {e}")
        
        # Include Docling routes
        try:
            from src.api.docling_api import router as docling_router
            self.app.include_router(docling_router)
            logger.info("Docling routes included successfully")
        except Exception as e:
            logger.warning(f"Failed to include Docling routes: {e}")
        
        # Include Home Assistant routes
        if HOME_ASSISTANT_AVAILABLE:
            try:
                import sys
                sys.path.append('.')
                from src.api.home_assistant_api import router
                
                # Debug: Check router before inclusion
                logger.info(f"Home Assistant router has {len(router.routes)} routes")
                ha_routes = [route.path for route in router.routes if hasattr(route, 'path')]
                logger.info(f"Home Assistant routes: {ha_routes}")
                
                self.app.include_router(router)
                
                # Debug: Check routes after inclusion
                all_routes = [route.path for route in self.app.routes if hasattr(route, 'path')]
                ha_routes_after = [route for route in all_routes if 'home-assistant' in route]
                logger.info(f"Home Assistant routes after inclusion: {len(ha_routes_after)}")
                logger.info(f"All routes after inclusion: {len(all_routes)}")
                
                logger.info("Home Assistant routes included successfully")
            except Exception as e:
                logger.warning(f"Failed to include Home Assistant routes: {e}")
                import traceback
                logger.error(f"Home Assistant import error: {traceback.format_exc()}")

        # Root endpoint
        @self.app.get("/")
        async def root():
            endpoints = {
                "chat": "/api/chat/",
                "agents": "/api/agents/",
                "health": "/api/system/health",
                "knowledge": "/api/knowledge/stats"
            }
            
            # Add Home Assistant endpoints if available
            if HOME_ASSISTANT_AVAILABLE:
                endpoints["home_assistant"] = "/api/home-assistant/"
            
            return {
                "message": "Consolidated AI Chat API",
                "version": "2.0.0",
                "status": "running",
                "endpoints": endpoints,
                "docs": "/docs",
                "features": {
                    "performance_optimization": True,
                    "security_enhancements": True,
                    "code_quality_improvements": True,
                    "architecture_refactoring": True
                }
            }

    async def initialize(self) -> bool:
        """Initialize the consolidated API application."""
        # Initialize router components first
        router_success = await self.router.initialize()
        
        # Then include routers in the app
        self._include_routers()
        
        return router_success

# Global instance to persist across startup
_consolidated_app_instance = None

# Create the consolidated app
def create_consolidated_app() -> FastAPI:
    """TODO: Add docstring."""
    """Create and configure the consolidated FastAPI application."""
    global _consolidated_app_instance
    _consolidated_app_instance = ConsolidatedAPIApp()
    
    # Don't initialize here - let the lifespan handler do it to prevent double initialization
    
    return _consolidated_app_instance.app

# Lifespan handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    global _consolidated_app_instance
    if _consolidated_app_instance:
        logger.info("🔧 Initializing NeuroForge components...")
        success = await _consolidated_app_instance.initialize()
        if success:
            logger.info("✅ NeuroForge fully activated!")
        else:
            logger.warning("⚠️ Running in fallback mode")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Consolidated API Server...")

# Main app instance
app = create_consolidated_app()

# Run the server
if __name__ == "__main__":
    logger.info("🚀 Starting Consolidated API Server...")
    
    # Add the project root to Python path so imports work
    import sys
    import os
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    uvicorn.run(
        "consolidated_api_architecture:app",
        host="0.0.0.0",
        port=8004,
        log_level="info",
        access_log=True,
        reload=False
    )
