#!/usr/bin/env python3
"""
Production-Ready Chat Backend
Enhanced with security, monitoring, and production features
"""

import asyncio
import aiohttp
import json
import logging
import sys
import os
import time
import hashlib
import secrets
import psutil
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from collections import defaultdict, deque
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Request, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, validator
import uvicorn

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import centralized configuration
try:
    from src.core.config.env_config import get_config
except ImportError:
    # Fallback configuration if env_config not available
    def get_config():
        class Config:
            def get(self, key, default=None):
                import os
                return os.getenv(key, default)
            def get_int(self, key, default=0):
                import os
                try:
                    return int(os.getenv(key, default))
                except (ValueError, TypeError):
                    return default
            def get_float(self, key, default=0.0):
                import os
                try:
                    return float(os.getenv(key, default))
                except (ValueError, TypeError):
                    return default
            def get_list(self, key, default=None):
                import os
                value = os.getenv(key)
                if value:
                    return [item.strip() for item in value.split(',')]
                return default if default is not None else []
        return Config()

# Import production modules
from production_security_middleware import create_production_middleware_stack
from production_monitoring import initialize_monitor, get_monitor

# Get configuration
config = get_config()

# Setup logging with configurable level
log_level = getattr(logging, config.get('LOG_LEVEL', 'INFO').upper(), logging.INFO)
logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/production.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Create FastAPI app with production settings
app = FastAPI(
    title="NeuroForge Production API",
    version="3.0.0",
    description="Production-ready AI chat backend with comprehensive security and monitoring",
    docs_url="/docs" if config.get('ENABLE_DOCS', 'true').lower() == 'true' else None,
    redoc_url="/redoc" if config.get('ENABLE_DOCS', 'true').lower() == 'true' else None
)

# Security configuration
security = HTTPBearer(auto_error=False)

# Rate limiting storage
rate_limits = defaultdict(list)
blocked_ips = set()

# Request metrics
request_metrics = {
    'total_requests': 0,
    'successful_requests': 0,
    'failed_requests': 0,
    'response_times': deque(maxlen=1000),
    'error_counts': defaultdict(int)
}

class ChatRequest(BaseModel):
    message: str
    agent: Optional[str] = "general"
    session_id: Optional[str] = None
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 500
    show_browser_windows: Optional[bool] = False
    
    @validator('message')
    def validate_message(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Message cannot be empty')
        if len(v) > 10000:
            raise ValueError('Message too long')
        return v.strip()
    
    @validator('temperature')
    def validate_temperature(cls, v):
        if not 0.0 <= v <= 2.0:
            raise ValueError('Temperature must be between 0.0 and 2.0')
        return v

class SystemMetrics(BaseModel):
    timestamp: str
    uptime: float
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time: float
    error_rate: float
    active_connections: int

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    uptime: float
    services: Dict[str, str]
    metrics: Dict[str, Any]

# Production middleware stack
create_production_middleware_stack(app, {
    'RATE_LIMIT_REQUESTS': config.get_int('RATE_LIMIT_REQUESTS', 100),
    'RATE_LIMIT_HOUR': config.get_int('RATE_LIMIT_HOUR', 1000),
    'BLOCK_DURATION': config.get_int('BLOCK_DURATION', 60),
    'API_KEYS': config.get('API_KEYS', ''),
    'ALLOWED_HOSTS': config.get_list('ALLOWED_HOSTS', ['localhost', '127.0.0.1'])
})

# CORS middleware with production settings
cors_origins = config.get_list('CORS_ORIGINS', ["http://localhost:3000"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Initialize monitoring
monitor = initialize_monitor({
    'SMTP_SERVER': config.get('SMTP_SERVER', ''),
    'SMTP_PORT': config.get_int('SMTP_PORT', 587),
    'EMAIL_USERNAME': config.get('EMAIL_USERNAME', ''),
    'EMAIL_PASSWORD': config.get('EMAIL_PASSWORD', ''),
    'ALERT_EMAILS': config.get_list('ALERT_EMAILS', [])
})

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """Collect request metrics"""
    start_time = time.time()
    request_metrics['total_requests'] += 1
    
    try:
        response = await call_next(request)
        request_metrics['successful_requests'] += 1
        
        # Log successful requests
        if response.status_code >= 200 and response.status_code < 300:
            logger.info(f"Request successful: {request.method} {request.url.path} - {response.status_code}")
        
        return response
    except Exception as e:
        request_metrics['failed_requests'] += 1
        request_metrics['error_counts'][str(type(e).__name__)] += 1
        logger.error(f"Request failed: {request.method} {request.url.path} - {str(e)}")
        raise
    finally:
        response_time = time.time() - start_time
        request_metrics['response_times'].append(response_time)

def get_system_metrics() -> SystemMetrics:
    """Get current system metrics"""
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    avg_response_time = (
        sum(request_metrics['response_times']) / len(request_metrics['response_times'])
        if request_metrics['response_times'] else 0
    )
    
    error_rate = (
        (request_metrics['failed_requests'] / request_metrics['total_requests'] * 100)
        if request_metrics['total_requests'] > 0 else 0
    )
    
    return SystemMetrics(
        timestamp=datetime.utcnow().isoformat(),
        uptime=time.time() - psutil.boot_time(),
        cpu_percent=cpu_percent,
        memory_percent=memory.percent,
        disk_percent=disk.percent,
        total_requests=request_metrics['total_requests'],
        successful_requests=request_metrics['successful_requests'],
        failed_requests=request_metrics['failed_requests'],
        avg_response_time=avg_response_time,
        error_rate=error_rate,
        active_connections=1  # Simplified for now
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Comprehensive health check endpoint"""
    services = {}
    
    # Check backend services
    service_urls = {
        'rag_service': config.get('RAG_SERVICE_URL', 'http://localhost:8005'),
        'tts_service': config.get('TTS_SERVICE_URL', 'http://localhost:8087'),
        'ollama': config.get('OLLAMA_URL', 'http://localhost:11434')
    }
    
    for service_name, url in service_urls.items():
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=2)) as session:
                async with session.get(f"{url}/health") as response:
                    services[service_name] = "healthy" if response.status == 200 else "unhealthy"
        except Exception:
            services[service_name] = "unhealthy"
    
    # Determine overall status
    unhealthy_services = [s for s in services.values() if s != "healthy"]
    overall_status = "healthy" if not unhealthy_services else "degraded"
    
    metrics = get_system_metrics()
    
    return HealthResponse(
        status=overall_status,
        timestamp=datetime.utcnow().isoformat(),
        version="3.0.0",
        uptime=metrics.uptime,
        services=services,
        metrics=metrics.dict()
    )

@app.get("/api/system/metrics", response_model=SystemMetrics)
async def get_metrics():
    """Get detailed system metrics"""
    return get_system_metrics()

@app.get("/api/system/status")
async def system_status():
    """Get system status with monitoring integration"""
    monitor_instance = get_monitor()
    if monitor_instance:
        health_status = monitor_instance.get_health_status()
        return {
            "status": health_status['status'],
            "message": health_status['message'],
            "active_alerts": health_status['active_alerts'],
            "services_healthy": health_status['services_healthy'],
            "last_check": health_status['last_check']
        }
    else:
        return {"status": "monitoring_disabled", "message": "Monitoring not initialized"}

@app.post("/api/chat")
async def chat(request: ChatRequest, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Enhanced chat endpoint with production features"""
    
    # API key validation (if configured)
    if config.get('API_KEYS'):
        if not credentials or credentials.credentials not in config.get_list('API_KEYS'):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key"
            )
    
    try:
        # Get RAG context first
        rag_context = ""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                async with session.post(f"{config.get('RAG_SERVICE_URL', 'http://localhost:8005')}/api/rag/query", json={
                    "query_text": request.message,
                    "k": 5,
                    "method": "hybrid"
                }) as response:
                    if response.status == 200:
                        rag_data = await response.json()
                        if rag_data.get('results'):
                            rag_context = "\n\nRelevant context:\n" + "\n".join([r['text'] for r in rag_data['results'][:3]])
        except Exception as e:
            logger.warning(f"RAG query failed: {e}")
        
        # Generate AI response using Ollama
        ollama_url = f"{config.get('OLLAMA_URL', 'http://localhost:11434')}/api/generate"
        
        # Enhanced prompt with context
        prompt = f"""You are NeuroForge AI Assistant, a helpful and knowledgeable AI assistant.
        
User question: {request.message}
{rag_context}

Please provide a helpful, accurate response. Be conversational and natural.
If you used context information, acknowledge it naturally in your response.
"""
        
        payload = {
            "model": config.get('OLLAMA_MODEL', 'qwen2.5:7b'),
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": request.temperature,
                "max_tokens": request.max_tokens,
                "top_p": 0.9
            }
        }
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
            async with session.post(ollama_url, json=payload) as response:
                if response.status == 200:
                    ollama_data = await response.json()
                    ai_response = ollama_data.get('response', 'I apologize, but I could not generate a response.')
                    
                    # Log successful chat
                    logger.info(f"Chat successful: {len(request.message)} chars input, {len(ai_response)} chars output")
                    
                    return {
                        "response": ai_response,
                        "timestamp": datetime.utcnow().isoformat(),
                        "agent_used": request.agent,
                        "rag_used": bool(rag_context),
                        "performance_metrics": {
                            "model": config.get('OLLAMA_MODEL', 'qwen2.5:7b'),
                            "temperature": request.temperature,
                            "max_tokens": request.max_tokens,
                            "context_length": len(rag_context)
                        }
                    }
                else:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="AI model service unavailable"
                    )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@app.post("/api/voice/synthesize")
async def synthesize_speech(text: str = Form(...), voice: str = Form("natural")):
    """Enhanced voice synthesis with error handling"""
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
            async with session.post(f"{config.get('TTS_SERVICE_URL', 'http://localhost:8087')}/synthesize", 
                                  json={"text": text, "voice": voice}) as response:
                if response.status == 200:
                    audio_data = await response.read()
                    
                    # Create temporary file
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.aiff') as temp_file:
                        temp_file.write(audio_data)
                        temp_file_path = temp_file.name
                    
                    return FileResponse(
                        temp_file_path,
                        media_type="audio/aiff",
                        filename="speech.aiff"
                    )
                else:
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail="TTS service unavailable"
                    )
    except Exception as e:
        logger.error(f"Voice synthesis error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Voice synthesis failed"
        )

# Additional production endpoints
@app.get("/api/system/logs")
async def get_logs(lines: int = 100):
    """Get recent application logs"""
    try:
        log_file = "logs/production.log"
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                log_lines = f.readlines()
                recent_lines = log_lines[-lines:] if len(log_lines) > lines else log_lines
                return {"logs": recent_lines}
        else:
            return {"logs": ["No log file found"]}
    except Exception as e:
        logger.error(f"Log retrieval error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve logs"
        )

@app.post("/api/system/restart")
async def restart_system(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Restart system (admin only)"""
    if not credentials or credentials.credentials not in config.get_list('API_KEYS'):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin access required"
        )
    
    logger.warning("System restart requested")
    # In production, this would trigger a proper restart mechanism
    return {"message": "Restart initiated", "timestamp": datetime.utcnow().isoformat()}

@app.get("/")
async def root():
    """Root endpoint with system information"""
    return {
        "service": "NeuroForge Production API",
        "version": "3.0.0",
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat(),
        "docs": "/docs" if config.get('ENABLE_DOCS', 'true').lower() == 'true' else "disabled"
    }

if __name__ == "__main__":
    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)
    
    # Start the server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=config.get_int('CONSOLIDATED_API_PORT', 8004),
        log_level=log_level.lower(),
        access_log=True
    )
