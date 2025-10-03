#!/usr/bin/env python3
"""
AI Assistant Platform - Simple Frontend Server
A streamlined frontend-only version for demonstration.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def main():
    """Main application entry point."""
    try:
        logger.info("🚀 Starting AI Assistant Platform...")

        # Import and start the FastAPI server
        from src.api.consolidated_api_architecture import create_consolidated_app
        import uvicorn

        logger.info("✅ Backend API initialized")
        logger.info("🌐 Frontend available at: http://localhost:3000")
        logger.info("🔧 Consolidated API available at: http://localhost:8004")

        # Start the server
        config = uvicorn.Config(
            create_consolidated_app(),
            host="127.0.0.1",
            port=8004,
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()

    except KeyboardInterrupt:
        logger.info("👋 Shutting down gracefully...")
    except Exception as e:
        logger.error(f"💥 Application failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())