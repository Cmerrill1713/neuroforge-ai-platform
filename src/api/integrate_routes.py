#!/usr/bin/env python3
"""
Integration Guide for Adding Evolution + RAG Routes
Shows how to add the new routes to your existing API servers
"""

# ============================================================================
# Option 1: Add to existing api_server.py
# ============================================================================

INTEGRATION_OPTION_1 = """
# File: src/api/api_server.py

# Add at top with other imports:
from src.api.evolutionary_routes import router as evolutionary_router, set_integration
from src.api.rag_routes import router as rag_router, set_rag_service
from src.core.prompting.dual_backend_integration import DualBackendEvolutionaryIntegration
from src.core.retrieval.rag_service import create_rag_service

# Add global instances (after app creation):
evolutionary_integration = None
rag_service = None

# In lifespan function, after "Startup" comment:
@asynccontextmanager
async def lifespan(app: FastAPI):
    global evolutionary_integration, rag_service
    
    # Startup
    try:
        # ... existing startup code ...
        
        # Initialize evolutionary integration
        logger.info("🧬 Initializing evolutionary optimizer...")
        evolutionary_integration = DualBackendEvolutionaryIntegration()
        await evolutionary_integration.initialize()
        set_integration(evolutionary_integration)
        logger.info("✅ Evolutionary optimizer ready")
        
        # Initialize RAG service
        logger.info("🔍 Initializing RAG service...")
        rag_service = create_rag_service(env="development")
        set_rag_service(rag_service)
        logger.info("✅ RAG service ready")
        
    except Exception as e:
        logger.warning(f"Failed to initialize new services: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down NeuroForge API")

# Add after existing route definitions:
app.include_router(evolutionary_router)
app.include_router(rag_router)
"""

# ============================================================================
# Option 2: Standalone API server (recommended for testing)
# ============================================================================

INTEGRATION_OPTION_2 = """
#!/usr/bin/env python3
# File: src/api/evolutionary_api_server.py

import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.evolutionary_routes import router as evolutionary_router, set_integration
from src.api.rag_routes import router as rag_router, set_rag_service
from src.core.prompting.dual_backend_integration import DualBackendEvolutionaryIntegration
from src.core.retrieval.rag_service import create_rag_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global instances
evolutionary_integration = None
rag_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global evolutionary_integration, rag_service
    
    # Startup
    logger.info("🚀 Starting Evolutionary API Server")
    
    try:
        # Initialize evolutionary integration
        logger.info("🧬 Initializing evolutionary optimizer...")
        evolutionary_integration = DualBackendEvolutionaryIntegration()
        await evolutionary_integration.initialize()
        set_integration(evolutionary_integration)
        logger.info("✅ Evolutionary optimizer ready")
        
        # Initialize RAG service
        logger.info("🔍 Initializing RAG service...")
        rag_service = create_rag_service(env="development")
        set_rag_service(rag_service)
        logger.info("✅ RAG service ready")
        
    except Exception as e:
        logger.error(f"Failed to initialize: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Evolutionary API Server")
    if rag_service:
        await rag_service.close()

# Create app
app = FastAPI(
    title="Evolutionary Optimizer & RAG API",
    description="API for evolutionary prompt optimization and hybrid RAG retrieval",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(evolutionary_router)
app.include_router(rag_router)

# Health check
@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "services": {
            "evolutionary": evolutionary_integration is not None,
            "rag": rag_service is not None
        }
    }

# Run server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
"""

# ============================================================================
# Quick test commands
# ============================================================================

TEST_COMMANDS = """
# Test the new endpoints:

# 1. Health check
curl http://localhost:8000/health

# 2. Get evolution stats
curl http://localhost:8000/api/evolutionary/stats

# 3. Start evolution
curl -X POST http://localhost:8000/api/evolutionary/optimize \\
  -H "Content-Type: application/json" \\
  -d '{"num_generations": 3, "use_mipro": false}'

# 4. RAG query
curl -X POST http://localhost:8000/api/rag/query \\
  -H "Content-Type: application/json" \\
  -d '{"query_text": "machine learning", "k": 5, "method": "vector"}'

# 5. Get RAG metrics
curl http://localhost:8000/api/rag/metrics
"""

if __name__ == "__main__":
    print("="*80)
    print("INTEGRATION GUIDE - Adding Evolution + RAG Routes")
    print("="*80)
    print()
    print("Option 1: Integrate into existing api_server.py")
    print("-"*80)
    print(INTEGRATION_OPTION_1)
    print()
    print("="*80)
    print("Option 2: Standalone server (recommended for testing)")
    print("-"*80)
    print(INTEGRATION_OPTION_2)
    print()
    print("="*80)
    print("Test Commands")
    print("-"*80)
    print(TEST_COMMANDS)

