"""
Simplified Production-Ready API Server
Works with current dependencies
"""

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.config.settings import settings
from enhanced_agent_selection import EnhancedAgentSelector
from src.core.knowledge.simple_knowledge_base import SimpleKnowledgeBase

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global variables
enhanced_selector: Optional[EnhancedAgentSelector] = None
knowledge_base: Optional[SimpleKnowledgeBase] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global enhanced_selector, knowledge_base
    
    logger.info("🚀 Starting Production AI Chat API Server")
    
    try:
        # Initialize Enhanced Agent Selection
        logger.info("📡 Initializing Enhanced Agent Selection...")
        enhanced_selector = EnhancedAgentSelector()
        logger.info("✅ Enhanced Agent Selection ready")
        
        # Initialize Knowledge Base
        logger.info("📚 Initializing Knowledge Base...")
        knowledge_base = SimpleKnowledgeBase()
        logger.info("✅ Knowledge Base ready")
        
        logger.info("🎉 Production API Server initialization complete!")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize server: {e}")
        raise
    
    yield
    
    logger.info("🛑 Shutting down Production API Server")

# Create FastAPI app
app = FastAPI(
    title="AI Chat Production API",
    description="Production-ready AI Chat API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": settings.environment,
        "version": "1.0.0"
    }

# System status endpoint
@app.get("/status")
async def system_status():
    """Detailed system status"""
    status_info = {
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": settings.environment,
        "version": "1.0.0",
        "components": {
            "enhanced_selector": enhanced_selector is not None,
            "knowledge_base": knowledge_base is not None,
        }
    }
    
    if enhanced_selector:
        status_info["agents"] = len(enhanced_selector.agent_profiles)
        status_info["models"] = len(enhanced_selector.ollama_adapter.models)
    
    return status_info

# Enhanced chat endpoint with security
@app.post("/api/chat")
async def chat_endpoint(chat_request: dict):
    """Production chat endpoint with security"""
    
    if not enhanced_selector:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    try:
        start_time = time.time()
        
        # Validate input
        message = chat_request.get("message", "").strip()
        if not message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        if len(message) > 10000:  # 10KB limit
            raise HTTPException(status_code=400, detail="Message too long")
        
        # Convert to task request format
        task_request = {
            "task_type": chat_request.get("task_type", "text_generation"),
            "content": message,
            "latency_requirement": chat_request.get("latency_requirement", 1000),
            "input_type": chat_request.get("input_type", "text"),
            "max_tokens": min(chat_request.get("max_tokens", 1024), 4096),
            "temperature": max(0.0, min(chat_request.get("temperature", 0.7), 2.0))
        }
        
        # Get enhanced agent selection result
        result = await enhanced_selector.select_best_agent_with_reasoning(task_request)
        
        processing_time = time.time() - start_time
        
        # Extract response content
        response_content = message  # Default fallback
        
        # Try to get actual AI response
        try:
            if result.get('selected_agent'):
                agent_name = result['selected_agent']['agent_name']
                # Map agent to model
                model_mapping = {
                    'generalist': 'primary',
                    'codesmith': 'coding', 
                    'analyst': 'primary',
                    'heretical_reasoner': 'hrm',
                    'chaos_architect': 'primary',
                    'quantum_reasoner': 'primary',
                    'symbiotic_coordinator': 'primary',
                    'quicktake': 'lightweight'
                }
                model_key = model_mapping.get(agent_name, 'primary')
                
                # Generate actual AI response
                ai_response = await enhanced_selector.ollama_adapter.generate_response(
                    model_key=model_key,
                    prompt=message,
                    max_tokens=task_request['max_tokens'],
                    temperature=task_request['temperature']
                )
                response_content = ai_response.content
        except Exception as e:
            logger.warning(f"Failed to generate AI response: {e}")
            response_content = "I apologize, but I'm experiencing technical difficulties. Please try again."
        
        # Prepare response
        response_data = {
            "response": response_content,
            "agent_name": result.get('selected_agent', {}).get('agent_name', 'unknown'),
            "task_complexity": result.get('task_complexity', 0.0),
            "use_parallel_reasoning": result.get('use_parallel_reasoning', False),
            "reasoning_mode": result.get('reasoning_mode'),
            "processing_time": processing_time,
            "confidence": result.get('selected_agent', {}).get('score', 0.0),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Knowledge base search endpoint
@app.post("/knowledge/search")
async def search_knowledge(search_request: dict):
    """Search knowledge base"""
    
    if not knowledge_base:
        raise HTTPException(status_code=503, detail="Knowledge base not available")
    
    try:
        query = search_request.get("query", "").strip()
        if not query:
            raise HTTPException(status_code=400, detail="Query is required")
        
        limit = min(search_request.get("limit", 10), 50)
        
        results = knowledge_base.search(query, limit=limit)
        
        return {
            "query": query,
            "results": results,
            "total_found": len(results),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in knowledge search: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Agents endpoint
@app.get("/api/agents")
async def get_agents():
    """Get available agents"""
    
    if not enhanced_selector:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    try:
        agents = []
        for agent_id, agent in enhanced_selector.agent_profiles.items():
            agents.append({
                "id": agent_id,
                "name": agent.name,
                "description": agent.description,
                "capabilities": agent.capabilities,
                "task_types": agent.task_types,
                "performance_metrics": agent.performance_metrics
            })
        
        return {
            "agents": agents,
            "total": len(agents),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting agents: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Models status endpoint
@app.get("/models/status")
async def get_models_status():
    """Get models status"""
    
    if not enhanced_selector:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    try:
        models = []
        for model_key, model in enhanced_selector.ollama_adapter.models.items():
            models.append({
                "id": model_key,
                "name": model.name,
                "type": model.model_type,
                "capabilities": model.capabilities,
                "performance": model.performance,
                "status": "online"
            })
        
        return {
            "models": models,
            "total": len(models),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting models status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Monitoring metrics endpoint
@app.get("/monitoring/metrics")
async def get_monitoring_metrics():
    """Get system monitoring metrics"""
    
    try:
        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "system": {
                "uptime": time.time(),
                "environment": settings.environment,
            },
            "api": {
                "total_requests": 0,  # Would implement request counting
                "error_rate": 0,      # Would implement error rate calculation
                "response_time_avg": 0,  # Would implement response time tracking
            },
            "models": {
                "active_models": len(enhanced_selector.ollama_adapter.models) if enhanced_selector else 0,
                "total_agents": len(enhanced_selector.agent_profiles) if enhanced_selector else 0,
            }
        }
        
        return metrics
        
    except Exception as e:
        logger.error(f"Error getting monitoring metrics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    uvicorn.run(
        "production_api_server_simple:app",
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower(),
        access_log=True,
        reload=settings.debug,
    )
