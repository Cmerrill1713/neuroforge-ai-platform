#!/usr/bin/env python3
"""
FastAPI Web Server for Agentic LLM Core
Provides REST API and WebSocket endpoints for frontend integration
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import uuid

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import HTMLResponse
    from pydantic import BaseModel
    from enhanced_agent_selection import EnhancedAgentSelector
    from core.knowledge.simple_knowledge_base import SimpleKnowledgeBase
    from src.core.security.sanitizer import sanitize_user_text
    from src.core.assessment.response_reviewer import evaluate_response
    from src.core.logging.event_tracker import log_event
except ImportError as e:
    print(f"❌ Missing dependencies: {e}")
    print("Install with: pip install fastapi uvicorn websockets")
    sys.exit(1)

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Pydantic models for API
class ChatRequest(BaseModel):
    """Chat request model."""
    message: str
    task_type: str = "text_generation"
    input_type: str = "text"
    latency_requirement: int = 1000
    max_tokens: int = 1024
    temperature: float = 0.7
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    """Chat response model."""
    response: str
    agent_name: str
    task_complexity: float
    use_parallel_reasoning: bool
    reasoning_mode: Optional[str]
    processing_time: float
    confidence: float
    reasoning_paths: Optional[List[Dict[str, Any]]] = None
    timestamp: str
    fallback_used: bool = False
    model_name: Optional[str] = None
    request_id: Optional[str] = None
    review_required: bool = False
    review_reasons: Optional[Dict[str, Any]] = None
    security_flags: int = 0

class AgentStatus(BaseModel):
    """Agent status model."""
    agent_name: str
    is_active: bool
    current_task: Optional[str] = None
    performance_metrics: Dict[str, Any]

class KnowledgeSearchRequest(BaseModel):
    """Knowledge base search request."""
    query: str
    limit: int = 10

class KnowledgeSearchResponse(BaseModel):
    """Knowledge base search response."""
    query: str
    results: List[Dict[str, Any]]
    total_found: int

# Initialize FastAPI app
app = FastAPI(
    title="Agentic LLM Core API",
    description="REST API for Agentic LLM Core with parallel reasoning capabilities",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
enhanced_selector = None
knowledge_base = None
active_connections: List[WebSocket] = []

@app.on_event("startup")
async def startup_event():
    """Initialize system components on startup."""
    global enhanced_selector, knowledge_base
    
    logger.info("🚀 Starting Agentic LLM Core API Server")
    
    try:
        # Initialize enhanced agent selector
        logger.info("📡 Initializing Enhanced Agent Selection...")
        enhanced_selector = EnhancedAgentSelector()
        logger.info("✅ Enhanced Agent Selection ready")
        
        # Initialize knowledge base
        logger.info("📚 Initializing Knowledge Base...")
        knowledge_base = SimpleKnowledgeBase()
        logger.info("✅ Knowledge Base ready")
        
        logger.info("🎉 API Server initialization complete!")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Agentic LLM Core API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "chat": "/api/chat",
            "agents": "/api/agents",
            "knowledge": "/api/knowledge/search",
            "websocket": "/ws/chat",
            "docs": "/docs"
        }
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Main chat endpoint with enhanced agent selection."""
    
    if not enhanced_selector:
        raise HTTPException(status_code=503, detail="System not initialized")
    request_id = str(uuid.uuid4())

    try:
        start_time = datetime.now()
        
        sanitized = sanitize_user_text(request.message)
        if sanitized.flags:
            log_event(
                "security_flag",
                {
                    "request_id": request_id,
                    "flags": sanitized.flags,
                }
            )

        # Convert to task request format
        task_request = {
            "task_type": request.task_type,
            "content": sanitized.text,
            "latency_requirement": request.latency_requirement,
            "input_type": request.input_type,
            "max_tokens": request.max_tokens,
            "temperature": request.temperature
        }
        
        # Get enhanced agent selection result
        result = await enhanced_selector.select_best_agent_with_reasoning(task_request)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Extract response content
        response_content = request.message  # Default fallback
        model_name = None
        fallback_used = False
        
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
                    prompt=sanitized.text,
                    max_tokens=request.max_tokens,
                    temperature=request.temperature
                )
                response_content = ai_response.content
                model_name = ai_response.model
                fallback_used = bool(ai_response.metadata.get("fallback_used"))
        except Exception as e:
            logger.warning(f"Failed to generate AI response: {e}, falling back to echo")
        
        # Check for parallel reasoning result
        if result.get('parallel_reasoning_result'):
            pr_result = result['parallel_reasoning_result']
            if pr_result.best_path:
                response_content = pr_result.best_path.content
            elif pr_result.summary:
                response_content = pr_result.summary
        
        # Prepare reasoning paths for response
        reasoning_paths = None
        if result.get('parallel_reasoning_result'):
            pr_result = result['parallel_reasoning_result']
            reasoning_paths = [
                {
                    "path_id": path.path_id,
                    "reasoning_type": path.reasoning_type,
                    "confidence": path.confidence,
                    "content": path.content[:200] + "..." if len(path.content) > 200 else path.content
                }
                for path in pr_result.paths
            ]
        
        confidence_value = result['parallel_reasoning_result'].best_path.confidence if result.get('parallel_reasoning_result') and result['parallel_reasoning_result'].best_path else 0.8
        review = evaluate_response(
            confidence=confidence_value,
            fallback_used=fallback_used,
            security_flags=len(sanitized.flags)
        )

        chat_response = ChatResponse(
            response=response_content,
            agent_name=result['selected_agent']['agent_name'],
            task_complexity=result['task_complexity'],
            use_parallel_reasoning=result['use_parallel_reasoning'],
            reasoning_mode=result['reasoning_mode'],
            processing_time=processing_time,
            confidence=confidence_value,
            reasoning_paths=reasoning_paths,
            timestamp=datetime.now().isoformat(),
            fallback_used=fallback_used,
            model_name=model_name,
            request_id=request_id,
            review_required=review.requires_human_review,
            review_reasons=review.reasons,
            security_flags=len(sanitized.flags)
        )
        log_event(
            "chat_response",
            {
                "request_id": request_id,
                "task_type": request.task_type,
                "agent": chat_response.agent_name,
                "model": chat_response.model_name,
                "fallback_used": chat_response.fallback_used,
                "processing_time": chat_response.processing_time,
                "confidence": chat_response.confidence,
                "parallel_reasoning": chat_response.use_parallel_reasoning,
                "review_required": chat_response.review_required,
                "security_flags": chat_response.security_flags,
            }
        )
        return chat_response
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        log_event(
            "chat_error",
            {
                "request_id": request_id,
                "task_type": request.task_type,
                "error": str(e),
            }
        )
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/agents")
async def get_agents():
    """Get available agents and their status."""
    
    if not enhanced_selector:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    try:
        agents = []
        for profile in enhanced_selector.agent_manager.registry._profiles.values():
            agents.append({
                "name": profile.name,
                "task_types": profile.task_types,
                "priority": profile.priority,
                "tags": profile.tags,
                "model_preferences": profile.model_preferences
            })
        
        return {
            "agents": agents,
            "total": len(agents)
        }
        
    except Exception as e:
        logger.error(f"Get agents error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/knowledge/search", response_model=KnowledgeSearchResponse)
async def search_knowledge(request: KnowledgeSearchRequest):
    """Search the knowledge base."""
    
    if not knowledge_base:
        raise HTTPException(status_code=503, detail="Knowledge base not initialized")
    
    try:
        # Search entries
        entries = knowledge_base.search(request.query, limit=request.limit)
        
        # Search content
        content_results = knowledge_base.search_content(request.query)
        
        # Combine results
        results = []
        
        # Add entry results
        for entry_result in entries:
            results.append({
                "type": "entry",
                "title": entry_result["entry"]["title"],
                "score": entry_result["score"],
                "content": entry_result["entry"]["title"]
            })
        
        # Add content results
        for content_result in content_results[:request.limit]:
            results.append({
                "type": "content",
                "title": f"Content match in {content_result.get('entry_title', 'Unknown')}",
                "score": 0.8,  # Default score for content matches
                "content": content_result["context"][:200] + "..." if len(content_result["context"]) > 200 else content_result["context"]
            })
        
        return KnowledgeSearchResponse(
            query=request.query,
            results=results,
            total_found=len(results)
        )
        
    except Exception as e:
        logger.error(f"Knowledge search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """WebSocket endpoint for real-time chat."""
    
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Process chat request
            request = ChatRequest(**message_data)
            
            # Get chat response
            response = await chat_endpoint(request)
            
            # Send response
            await websocket.send_text(response.json())
            
    except WebSocketDisconnect:
        active_connections.remove(websocket)
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close()

@app.get("/api/metrics")
async def get_metrics():
    """Get system performance metrics."""
    
    if not enhanced_selector:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    try:
        # Get parallel reasoning stats
        pr_stats = enhanced_selector.parallel_engine.get_performance_stats()
        
        # Get agent registry stats
        agent_count = len(enhanced_selector.agent_manager.registry._profiles)
        
        # Get knowledge base stats
        kb_stats = {
            "total_entries": len(knowledge_base.index["entries"]),
            "searchable_content": True
        }
        
        return {
            "parallel_reasoning": pr_stats,
            "agents": {
                "total": agent_count,
                "active": agent_count  # All agents are considered active
            },
            "knowledge_base": kb_stats,
            "websocket_connections": len(active_connections),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Metrics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Serve static files (for frontend)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Simple HTML page for testing
@app.get("/test", response_class=HTMLResponse)
async def test_page():
    """Simple test page for API testing."""
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Agentic LLM Core - Test Page</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .container { max-width: 800px; margin: 0 auto; }
            .chat-box { border: 1px solid #ccc; padding: 20px; margin: 20px 0; }
            .message { margin: 10px 0; padding: 10px; border-radius: 5px; }
            .user { background-color: #e3f2fd; }
            .assistant { background-color: #f3e5f5; }
            input[type="text"] { width: 70%; padding: 10px; }
            button { padding: 10px 20px; margin-left: 10px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 Agentic LLM Core - Test Interface</h1>
            
            <div class="chat-box">
                <h3>Chat Interface</h3>
                <div id="messages"></div>
                <div>
                    <input type="text" id="messageInput" placeholder="Type your message..." />
                    <button onclick="sendMessage()">Send</button>
                </div>
            </div>
            
            <div class="chat-box">
                <h3>System Status</h3>
                <div id="status">Loading...</div>
            </div>
        </div>
        
        <script>
            async function sendMessage() {
                const input = document.getElementById('messageInput');
                const message = input.value.trim();
                if (!message) return;
                
                // Add user message
                addMessage('user', message);
                input.value = '';
                
                try {
                    const response = await fetch('/api/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            message: message,
                            task_type: 'text_generation',
                            latency_requirement: 1000
                        })
                    });
                    
                    const data = await response.json();
                    addMessage('assistant', data.response);
                    updateStatus(data);
                    
                } catch (error) {
                    addMessage('assistant', 'Error: ' + error.message);
                }
            }
            
            function addMessage(type, content) {
                const messages = document.getElementById('messages');
                const messageDiv = document.createElement('div');
                messageDiv.className = 'message ' + type;
                messageDiv.textContent = content;
                messages.appendChild(messageDiv);
                messages.scrollTop = messages.scrollHeight;
            }
            
            function updateStatus(data) {
                const status = document.getElementById('status');
                status.innerHTML = `
                    <strong>Agent:</strong> ${data.agent_name}<br>
                    <strong>Complexity:</strong> ${data.task_complexity.toFixed(3)}<br>
                    <strong>Parallel Reasoning:</strong> ${data.use_parallel_reasoning}<br>
                    <strong>Processing Time:</strong> ${data.processing_time.toFixed(2)}s<br>
                    <strong>Confidence:</strong> ${data.confidence.toFixed(3)}
                `;
            }
            
            // Load initial status
            fetch('/api/metrics')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('status').innerHTML = `
                        <strong>System Status:</strong> Running<br>
                        <strong>Agents:</strong> ${data.agents.total}<br>
                        <strong>Knowledge Base:</strong> ${data.knowledge_base.total_entries} entries<br>
                        <strong>WebSocket Connections:</strong> ${data.websocket_connections}
                    `;
                })
                .catch(error => {
                    document.getElementById('status').innerHTML = 'Error loading status';
                });
            
            // Enter key support
            document.getElementById('messageInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            });
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting Agentic LLM Core API Server")
    print("📡 API Documentation: http://localhost:8000/docs")
    print("🧪 Test Interface: http://localhost:8000/test")
    print("🔌 WebSocket: ws://localhost:8000/ws/chat")
    
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
