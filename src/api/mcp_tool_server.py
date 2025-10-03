#!/usr/bin/env python3
"""
MCP Server Integration for Comprehensive Tool Suite
"""

import asyncio
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import json

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.tools.comprehensive_mcp_executor import ComprehensiveMCPExecutor

logger = logging.getLogger(__name__)

app = FastAPI(title="MCP Tool Server", version="1.0.0")

class ToolRequest(BaseModel):
    tool_name: str
    message: str
    parameters: Optional[Dict[str, Any]] = {}

class ToolResponse(BaseModel):
    success: bool
    tool: str
    result: Any
    error: Optional[str] = None

class MCPToolServer:
    """MCP Tool Server for comprehensive tool execution"""
    
    def __init__(self):
        self.executor = ComprehensiveMCPExecutor()
        self.available_tools = [
            # Web & Search Tools
            "web_search", "web_crawl", "news_search",
            
            # File & System Tools
            "file_read", "file_write", "file_list", "directory_browse", "system_info",
            
            # Math & Calculation Tools
            "calculator", "math_solver", "statistics",
            
            # Data & Analysis Tools
            "json_parser", "csv_analyzer", "data_visualization",
            
            # Code & Development Tools
            "code_executor", "git_operations", "package_manager",
            
            # Knowledge & RAG Tools
            "knowledge_search", "document_analyzer", "rag_query",
            
            # Communication Tools
            "email_sender", "slack_notification", "webhook_trigger",
            
            # AI & ML Tools
            "image_analyzer", "text_processor", "model_inference",
            
            # Utility Tools
            "url_shortener", "qr_generator", "password_generator", "timezone_converter"
        ]
    
    async def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of available tools"""
        return [
            {
                "name": tool,
                "description": self._get_tool_description(tool),
                "category": self._get_tool_category(tool),
                "status": "available"
            }
            for tool in self.available_tools
        ]
    
    async def execute_tool(self, tool_name: str, message: str, **kwargs) -> Dict[str, Any]:
        """Execute a tool"""
        try:
            async with self.executor as executor:
                result = await executor.execute_tool(tool_name, message, **kwargs)
                return result
        except Exception as e:
            logger.error(f"Tool execution error: {e}")
            return {"success": False, "error": str(e)}
    
    def _get_tool_description(self, tool_name: str) -> str:
        """Get tool description"""
        descriptions = {
            "web_search": "Search the web for information",
            "web_crawl": "Crawl and extract content from web pages",
            "news_search": "Search for news articles",
            "file_read": "Read content from files",
            "file_write": "Write content to files",
            "file_list": "List files in directories",
            "system_info": "Get system information",
            "calculator": "Perform mathematical calculations",
            "statistics": "Calculate statistical measures",
            "knowledge_search": "Search knowledge base",
            "code_executor": "Execute code safely",
            "git_operations": "Perform git operations",
            "json_parser": "Parse and analyze JSON data",
            "csv_analyzer": "Analyze CSV data",
            "password_generator": "Generate secure passwords",
            "timezone_converter": "Convert time between timezones"
        }
        return descriptions.get(tool_name, "Tool description not available")
    
    def _get_tool_category(self, tool_name: str) -> str:
        """Get tool category"""
        categories = {
            "web_search": "Web & Search",
            "web_crawl": "Web & Search",
            "news_search": "Web & Search",
            "file_read": "File & System",
            "file_write": "File & System",
            "file_list": "File & System",
            "system_info": "File & System",
            "calculator": "Math & Calculation",
            "statistics": "Math & Calculation",
            "knowledge_search": "Knowledge & RAG",
            "code_executor": "Code & Development",
            "git_operations": "Code & Development",
            "json_parser": "Data & Analysis",
            "csv_analyzer": "Data & Analysis",
            "password_generator": "Utility",
            "timezone_converter": "Utility"
        }
        return categories.get(tool_name, "Other")

# Initialize MCP server
mcp_server = MCPToolServer()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "MCP Tool Server"}

@app.get("/tools")
async def get_tools():
    """Get available tools"""
    try:
        tools = await mcp_server.get_available_tools()
        return {
            "success": True,
            "tools": tools,
            "count": len(tools)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/execute")
async def execute_tool(request: ToolRequest):
    """Execute a tool"""
    try:
        result = await mcp_server.execute_tool(
            request.tool_name,
            request.message,
            **request.parameters
        )
        return ToolResponse(
            success=result.get("success", False),
            tool=request.tool_name,
            result=result,
            error=result.get("error")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/detect-and-execute")
async def detect_and_execute(message: str):
    """Detect tool intent and execute"""
    try:
        async with mcp_server.executor as executor:
            tool_name = await executor.detect_tool_intent(message)
            if tool_name:
                result = await executor.execute_tool(tool_name, message)
                return {
                    "success": True,
                    "detected_tool": tool_name,
                    "result": result
                }
            else:
                return {
                    "success": False,
                    "message": "No tool intent detected",
                    "suggestion": "Try being more specific about what you want to do"
                }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/servers")
async def get_servers():
    """Get MCP server information"""
    try:
        tools = await mcp_server.get_available_tools()
        return {
            "servers": [
                {
                    "name": "comprehensive_tools",
                    "status": "active",
                    "tools": len(tools),
                    "description": "Comprehensive MCP tool suite with all best tools"
                }
            ],
            "total_servers": 1,
            "total_tools": len(tools)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
