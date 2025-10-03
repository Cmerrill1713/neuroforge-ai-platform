#!/usr/bin/env python3
"""
Evolutionary Optimizer & RAG API Server
Standalone FastAPI server for frontend integration

Runs on port 8000 and provides:
- /api/evolutionary/* - Evolution endpoints
- /api/rag/* - RAG search endpoints
"""

import asyncio
import logging
import sys
from pathlib import Path
from contextlib import asynccontextmanager

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.evolutionary_routes import router as evolutionary_router, set_integration
from src.api.rag_routes import router as rag_router, set_rag_service
from src.core.prompting.dual_backend_integration import DualBackendEvolutionaryIntegration
from src.core.retrieval.rag_service import create_rag_service

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Global instances
evolutionary_integration = None
rag_service = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager"""
    global evolutionary_integration, rag_service
    
    # Startup
    logger.info("="*80)
    logger.info("🚀 EVOLUTIONARY OPTIMIZER & RAG API SERVER")
    logger.info("="*80)
    logger.info("")
    
    try:
        # Initialize evolutionary integration
        logger.info("🧬 Initializing evolutionary optimizer...")
        evolutionary_integration = DualBackendEvolutionaryIntegration()
        await evolutionary_integration.initialize()
        set_integration(evolutionary_integration)
        logger.info("✅ Evolutionary optimizer ready")
        logger.info(f"   Population: {evolutionary_integration.evolutionary.population_size}")
        logger.info(f"   Survivors: {evolutionary_integration.evolutionary.survivors}")
        
        # Initialize RAG service
        logger.info("🔍 Initializing RAG service...")
        rag_service = create_rag_service(env="development")
        set_rag_service(rag_service)
        logger.info("✅ RAG service ready")
        logger.info(f"   Weaviate: {rag_service.weaviate.host}:{rag_service.weaviate.http_port}")
        logger.info(f"   Embedder: {rag_service.embedder_model_name}")
        
        logger.info("")
        logger.info("✅ SERVER READY")
        logger.info("   Frontend: http://localhost:3001")
        logger.info("   API Docs: http://localhost:8000/docs")
        logger.info("")
        logger.info("="*80)
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down server...")
    if rag_service:
        await rag_service.close()
    logger.info("✅ Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Evolutionary Optimizer & RAG API",
    description="Production API for evolutionary prompt optimization and hybrid RAG retrieval",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(evolutionary_router)
app.include_router(rag_router)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Evolutionary Optimizer & RAG API",
        "version": "1.0.0",
        "status": "running",
        "services": {
            "evolutionary_optimizer": evolutionary_integration is not None,
            "rag_service": rag_service is not None
        },
        "endpoints": {
            "evolution": "/api/evolutionary",
            "rag": "/api/rag",
            "docs": "/docs",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "services": {
            "evolutionary": {
                "initialized": evolutionary_integration is not None,
                "ready": evolutionary_integration.rag_service is not None if evolutionary_integration else False
            },
            "rag": {
                "initialized": rag_service is not None,
                "weaviate": rag_service.weaviate.client.is_ready() if rag_service else False
            }
        }
    }


# Run server
if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting server on http://0.0.0.0:8000")
    logger.info("Frontend should be on http://localhost:3001")
    logger.info("")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )

