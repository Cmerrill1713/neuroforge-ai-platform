#!/usr/bin/env python3
"""
Integrated MCP Server
Combines RAG, file operations, web search, and other tools
"""

import asyncio
import json
import sys
import logging
import os
import subprocess
import requests
from typing import Dict, Any, List, Optional
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.retrieval.rag_service import create_rag_service

logger = logging.getLogger(__name__)

class IntegratedMCPServer:
    """Integrated MCP Server with RAG and other tools"""
    
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
    
    # RAG Operations
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
    
    # File Operations
    async def read_file(self, file_path: str) -> Dict[str, Any]:
        """Read file content"""
        try:
            path = Path(file_path)
            if not path.exists():
                return {
                    "success": False,
                    "error": f"File not found: {file_path}"
                }
            
            content = path.read_text(encoding='utf-8')
            return {
                "success": True,
                "file_path": file_path,
                "content": content,
                "size": len(content)
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to read file: {e}"
            }
    
    async def write_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Write content to file"""
        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding='utf-8')
            
            return {
                "success": True,
                "file_path": file_path,
                "size": len(content)
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to write file: {e}"
            }
    
    async def list_directory(self, directory: str = ".") -> Dict[str, Any]:
        """List directory contents"""
        try:
            path = Path(directory)
            if not path.exists():
                return {
                    "success": False,
                    "error": f"Directory not found: {directory}"
                }
            
            items = []
            for item in path.iterdir():
                items.append({
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else None
                })
            
            return {
                "success": True,
                "directory": str(path.absolute()),
                "items": items,
                "count": len(items)
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to list directory: {e}"
            }
    
    # Web Operations
    async def web_search(self, query: str) -> Dict[str, Any]:
        """Perform web search (placeholder)"""
        try:
            # This is a placeholder - in a real implementation you'd use
            # a web search API like Google, Bing, or DuckDuckGo
            return {
                "success": True,
                "query": query,
                "results": [
                    {
                        "title": f"Search result for: {query}",
                        "url": "https://example.com",
                        "snippet": f"This is a placeholder result for the query: {query}"
                    }
                ],
                "count": 1,
                "note": "This is a placeholder web search implementation"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Web search failed: {e}"
            }
    
    # System Operations
    async def execute_command(self, command: str) -> Dict[str, Any]:
        """Execute system command"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                "success": True,
                "command": command,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Command timed out"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Command execution failed: {e}"
            }
    
    async def get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        try:
            import platform
            import psutil
            
            return {
                "success": True,
                "platform": platform.platform(),
                "system": platform.system(),
                "processor": platform.processor(),
                "memory": {
                    "total": psutil.virtual_memory().total,
                    "available": psutil.virtual_memory().available,
                    "percent": psutil.virtual_memory().percent
                },
                "disk": {
                    "total": psutil.disk_usage('/').total,
                    "free": psutil.disk_usage('/').free,
                    "percent": psutil.disk_usage('/').percent
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get system info: {e}"
            }
    
    # Utility Operations
    async def calculate(self, expression: str) -> Dict[str, Any]:
        """Calculate mathematical expression"""
        try:
            # Safe evaluation of mathematical expressions
            import ast
            import operator
            
            # Define allowed operations
            operators = {
                ast.Add: operator.add,
                ast.Sub: operator.sub,
                ast.Mult: operator.mul,
                ast.Div: operator.truediv,
                ast.Pow: operator.pow,
                ast.USub: operator.neg,
            }
            
            def eval_expr(node):
                if isinstance(node, ast.Expression):
                    return eval_expr(node.body)
                elif isinstance(node, ast.Constant):
                    return node.value
                elif isinstance(node, ast.BinOp):
                    return operators[type(node.op)](eval_expr(node.left), eval_expr(node.right))
                elif isinstance(node, ast.UnaryOp):
                    return operators[type(node.op)](eval_expr(node.operand))
                else:
                    raise TypeError(node)
            
            tree = ast.parse(expression, mode='eval')
            result = eval_expr(tree)
            
            return {
                "success": True,
                "expression": expression,
                "result": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Calculation failed: {e}"
            }

async def main():
    """Main MCP server loop"""
    server = IntegratedMCPServer()
    
    while True:
        try:
            # Read MCP request
            request = json.loads(sys.stdin.readline())
            method = request.get("method")
            params = request.get("params", {})
            request_id = request.get("id")
            
            # Route to appropriate method
            if method == "query_rag":
                query = params.get("query", "")
                k = params.get("k", 5)
                method_param = params.get("method", "hybrid")
                result = await server.query_rag(query, k, method_param)
            
            elif method == "get_rag_metrics":
                result = await server.get_rag_metrics()
            
            elif method == "read_file":
                file_path = params.get("file_path", "")
                result = await server.read_file(file_path)
            
            elif method == "write_file":
                file_path = params.get("file_path", "")
                content = params.get("content", "")
                result = await server.write_file(file_path, content)
            
            elif method == "list_directory":
                directory = params.get("directory", ".")
                result = await server.list_directory(directory)
            
            elif method == "web_search":
                query = params.get("query", "")
                result = await server.web_search(query)
            
            elif method == "execute_command":
                command = params.get("command", "")
                result = await server.execute_command(command)
            
            elif method == "get_system_info":
                result = await server.get_system_info()
            
            elif method == "calculate":
                expression = params.get("expression", "")
                result = await server.calculate(expression)
            
            else:
                result = {
                    "success": False,
                    "error": f"Method not found: {method}"
                }
            
            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": result
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

