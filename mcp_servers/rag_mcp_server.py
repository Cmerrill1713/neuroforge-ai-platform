#!/usr/bin/env python3
"""
RAG MCP Server
Provides RAG functionality through MCP protocol
"""

import asyncio
import json
import sys
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.retrieval.rag_service import create_rag_service

logger = logging.getLogger(__name__)

class RAGMCPServer:
    """MCP Server for RAG operations"""
    
    def __init__(self):
        self.rag_service = None
        self._initialize_rag_service()
    
    def _initialize_rag_service(self):
        """Initialize the RAG service"""
        try:
            # Create RAG service for development environment
            self.rag_service = create_rag_service(env="development")
            logger.info("✅ RAG service initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize RAG service: {e}")
            self.rag_service = None
    
    async def query_rag(self, query: str, k: int = 5, method: str = "hybrid") -> Dict[str, Any]:
        """Query the RAG system"""
        if not self.rag_service:
            return {
                "success": False,
                "error": "RAG service not initialized"
            }
        
        try:
            # Execute query
            response = await self.rag_service.query(
                query_text=query,
                k=k,
                method=method,
                rerank=True
            )
            
            # Format results
            results = []
            for r in response.results:
                results.append({
                    "id": r.id,
                    "text": r.text,
                    "score": r.score,
                    "metadata": r.metadata
                })
            
            return {
                "success": True,
                "query": response.query,
                "results": results,
                "num_results": response.num_results,
                "latency_ms": response.latency_ms,
                "retrieval_method": response.retrieval_method,
                "metadata": response.metadata
            }
            
        except Exception as e:
            logger.error(f"RAG query failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_rag_metrics(self) -> Dict[str, Any]:
        """Get RAG system metrics"""
        if not self.rag_service:
            return {
                "success": False,
                "error": "RAG service not initialized"
            }
        
        try:
            metrics = await self.rag_service.get_metrics()
            return {
                "success": True,
                "metrics": metrics
            }
        except Exception as e:
            logger.error(f"Failed to get metrics: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def query_with_context(self, query: str, k: int = 5) -> Dict[str, Any]:
        """Query RAG and return formatted context"""
        if not self.rag_service:
            return {
                "success": False,
                "error": "RAG service not initialized"
            }
        
        try:
            context = await self.rag_service.query_with_context(
                query_text=query,
                k=k,
                method="hybrid"
            )
            
            return {
                "success": True,
                "query": query,
                "context": context,
                "k": k
            }
            
        except Exception as e:
            logger.error(f"Context query failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

async def main():
    """Main MCP server loop"""
    server = RAGMCPServer()
    
    while True:
        try:
            # Read MCP request
            request = json.loads(sys.stdin.readline())
            method = request.get("method")
            params = request.get("params", {})
            request_id = request.get("id")
            
            if method == "query_rag":
                query = params.get("query", "")
                k = params.get("k", 5)
                method = params.get("method", "hybrid")
                
                result = await server.query_rag(query, k, method)
                
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": result
                }
            
            elif method == "get_metrics":
                result = await server.get_rag_metrics()
                
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": result
                }
            
            elif method == "query_with_context":
                query = params.get("query", "")
                k = params.get("k", 5)
                
                result = await server.query_with_context(query, k)
                
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": result
                }
            
            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
            
            print(json.dumps(response))
            sys.stdout.flush()
            
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": request.get("id") if "request" in locals() else None,
                "error": {
                    "code": -32603,
                    "message": str(e)
                }
            }
            print(json.dumps(error_response))
            sys.stdout.flush()

if __name__ == "__main__":
    asyncio.run(main())

