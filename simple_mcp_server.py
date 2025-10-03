#!/usr/bin/env python3
"""
Simple MCP Server for Agent Tools
Provides HTTP API for agents to access tools
"""

import asyncio
import json
import logging
import subprocess
import os
import sys
import requests
import weaviate
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import aiohttp
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Simple MCP Agent Server",
    description="Tool suite for AI agents",
    version="1.0.0"
)

class ToolRequest(BaseModel):
    tool_name: str
    args: Optional[List[Any]] = []
    kwargs: Optional[Dict[str, Any]] = {}

class MCPTools:
    """Simple MCP Tools implementation"""
    
    def __init__(self):
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def read_file(self, file_path: str) -> Dict[str, Any]:
        """Read file content"""
        try:
            path = Path(file_path)
            if not path.exists():
                return {"success": False, "error": f"File not found: {file_path}"}
            
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                "success": True,
                "content": content,
                "size": len(content),
                "lines": len(content.splitlines()),
                "file_path": str(path)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def write_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Write content to file"""
        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                "success": True,
                "file_path": str(path),
                "bytes_written": len(content.encode('utf-8'))
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def list_directory(self, directory: str = ".") -> Dict[str, Any]:
        """List directory contents"""
        try:
            path = Path(directory)
            if not path.exists():
                return {"success": False, "error": f"Directory not found: {directory}"}
            
            files = []
            for item in path.iterdir():
                files.append({
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else None,
                    "modified": datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                })
            
            return {
                "success": True,
                "directory": str(path),
                "files": files,
                "count": len(files)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def execute_command(self, command: str) -> Dict[str, Any]:
        """Execute system command safely"""
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
            return {"success": False, "error": "Command timed out"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def calculate(self, expression: str) -> Dict[str, Any]:
        """Calculate mathematical expression"""
        try:
            # Safe evaluation
            allowed_chars = set('0123456789+-*/()., ')
            if not all(c in allowed_chars for c in expression):
                return {"success": False, "error": "Invalid characters in expression"}
            
            result = eval(expression)
            return {
                "success": True,
                "expression": expression,
                "result": result,
                "type": type(result).__name__
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def web_search(self, query: str) -> Dict[str, Any]:
        """Perform web search"""
        try:
            # Use DuckDuckGo API
            url = f"https://api.duckduckgo.com/?q={query}&format=json&no_html=1&skip_disambig=1"
            
            async with self.session.get(url) as response:
                data = await response.json()
                
                results = []
                for result in data.get('Results', [])[:5]:
                    results.append({
                        "title": result.get('Text', ''),
                        "url": result.get('FirstURL', ''),
                        "snippet": result.get('Text', '')
                    })
                
                return {
                    "success": True,
                    "query": query,
                    "results": results,
                    "count": len(results)
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def query_rag(self, query: str, k: int = 5) -> Dict[str, Any]:
        """Query RAG system"""
        try:
            async with self.session.post(
                "http://localhost:8000/api/rag/query",
                json={"query": query, "k": k}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "query": query,
                        "results": data.get("results", []),
                        "count": len(data.get("results", []))
                    }
                else:
                    return {"success": False, "error": f"RAG API error: {response.status}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        try:
            import platform
            import psutil
            
            return {
                "success": True,
                "platform": platform.platform(),
                "processor": platform.processor(),
                "python_version": platform.python_version(),
                "cpu_count": psutil.cpu_count(),
                "memory_total": psutil.virtual_memory().total,
                "memory_available": psutil.virtual_memory().available,
                "disk_usage": psutil.disk_usage('/').percent
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

# Initialize tools
mcp_tools = MCPTools()

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Simple MCP Agent Server",
        "version": "1.0.0",
        "tools": [
            "read_file", "write_file", "list_directory", "execute_command",
            "calculate", "web_search", "query_rag", "get_system_info"
        ],
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Simple MCP Agent Server",
        "tools_count": 8,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/tools")
async def list_tools():
    """List all available tools"""
    tools = [
        {"name": "read_file", "description": "Read file content"},
        {"name": "write_file", "description": "Write content to file"},
        {"name": "list_directory", "description": "List directory contents"},
        {"name": "execute_command", "description": "Execute system command"},
        {"name": "calculate", "description": "Calculate mathematical expression"},
        {"name": "web_search", "description": "Perform web search"},
        {"name": "query_rag", "description": "Query RAG system"},
        {"name": "get_system_info", "description": "Get system information"}
    ]
    
    return {
        "success": True,
        "tools": tools,
        "count": len(tools)
    }

@app.post("/execute")
async def execute_tool(request: ToolRequest):
    """Execute a tool"""
    try:
        async with mcp_tools as tools:
            if hasattr(tools, request.tool_name):
                method = getattr(tools, request.tool_name)
                result = await method(*request.args, **request.kwargs)
                return {
                    "success": result.get("success", False),
                    "result": result,
                    "error": result.get("error"),
                    "tool_name": request.tool_name
                }
            else:
                return {
                    "success": False,
                    "result": None,
                    "error": f"Unknown tool: {request.tool_name}",
                    "tool_name": request.tool_name
                }
    except Exception as e:
        logger.error(f"Tool execution error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Specific tool endpoints
@app.post("/tools/file/read")
async def read_file(file_path: str):
    """Read file content"""
    async with mcp_tools as tools:
        result = await tools.read_file(file_path)
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))
        return result

@app.post("/tools/file/write")
async def write_file(file_path: str, content: str):
    """Write content to file"""
    async with mcp_tools as tools:
        result = await tools.write_file(file_path, content)
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))
        return result

@app.post("/tools/file/list")
async def list_files(directory: str = "."):
    """List directory contents"""
    async with mcp_tools as tools:
        result = await tools.list_directory(directory)
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))
        return result

@app.post("/tools/calculate")
async def calculate(expression: str):
    """Calculate mathematical expression"""
    async with mcp_tools as tools:
        result = await tools.calculate(expression)
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))
        return result

@app.post("/tools/web/search")
async def web_search(query: str):
    """Perform web search"""
    async with mcp_tools as tools:
        result = await tools.web_search(query)
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))
        return result

@app.post("/tools/rag/query")
async def rag_query(query: str, k: int = 5):
    """Query RAG system"""
    async with mcp_tools as tools:
        result = await tools.query_rag(query, k)
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))
        return result

@app.post("/tools/command/execute")
async def execute_command(command: str):
    """Execute system command"""
    async with mcp_tools as tools:
        result = await tools.execute_command(command)
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))
        return result

@app.get("/tools/system/info")
async def get_system_info():
    """Get system information"""
    async with mcp_tools as tools:
        result = await tools.get_system_info()
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))
        return result

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
