#!/usr/bin/env python3
"""
Enhanced MCP API - Functional tool execution endpoints
Provides actually functional MCP tools instead of simulated responses
"""

import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from datetime import datetime

from .enhanced_mcp_executor import enhanced_mcp_executor

logger = logging.getLogger(__name__)

# Request/response models
class MCPToolRequest(BaseModel):
    """MCP tool execution request"""
    message: str = Field(..., min_length=1, max_length=2000, description="Message containing tool intent")
    tool_name: Optional[str] = Field(None, description="Specific tool to use (auto-detected if not provided)")
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional parameters")

class MCPToolResponse(BaseModel):
    """MCP tool execution response"""
    success: bool
    tool_used: str
    result: str
    execution_time_ms: float
    timestamp: str
    error: Optional[str] = None

class MCPToolInfo(BaseModel):
    """MCP tool information"""
    name: str
    description: str
    status: str
    category: str

class MCPToolsListResponse(BaseModel):
    """List of available MCP tools"""
    tools: List[MCPToolInfo]
    total_tools: int
    timestamp: str

# Create router
router = APIRouter(prefix="/api/mcp", tags=["Enhanced MCP Tools"])

@router.get("/tools", response_model=MCPToolsListResponse)
async def list_mcp_tools():
    """List all available MCP tools with descriptions"""
    try:
        available_tools = enhanced_mcp_executor.get_available_tools()
        
        tool_categories = {
            "web_search": "Web & Search",
            "web_browse": "Web & Search",
            "file_list": "File & System",
            "file_read": "File & System",
            "file_write": "File & System",
            "directory_browse": "File & System",
            "calculator": "Math & Calculation",
            "math_solver": "Math & Calculation",
            "knowledge_search": "Knowledge & RAG",
            "rag_query": "Knowledge & RAG",
            "system_info": "System & Info",
            "process_list": "System & Info",
            "url_shortener": "Utility",
            "text_processor": "Utility"
        }
        
        tools = []
        for tool_name in available_tools:
            tool_info = enhanced_mcp_executor.get_tool_info(tool_name)
            if "error" not in tool_info:
                tools.append(MCPToolInfo(
                    name=tool_name,
                    description=tool_info["description"],
                    status=tool_info["status"],
                    category=tool_categories.get(tool_name, "Other")
                ))
        
        return MCPToolsListResponse(
            tools=tools,
            total_tools=len(tools),
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Failed to list MCP tools: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list tools: {str(e)}")

@router.get("/tools/{tool_name}", response_model=MCPToolInfo)
async def get_mcp_tool_info(tool_name: str):
    """Get information about a specific MCP tool"""
    try:
        tool_info = enhanced_mcp_executor.get_tool_info(tool_name)
        
        if "error" in tool_info:
            raise HTTPException(status_code=404, detail=tool_info["error"])
        
        return MCPToolInfo(
            name=tool_name,
            description=tool_info["description"],
            status=tool_info["status"],
            category="Unknown"  # Could be enhanced to include categories
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get tool info for {tool_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get tool info: {str(e)}")

@router.post("/execute", response_model=MCPToolResponse)
async def execute_mcp_tool(request: MCPToolRequest):
    """Execute an MCP tool based on message intent or specified tool"""
    try:
        import time
        
        start_time = time.time()
        
        # Determine which tool to use
        if request.tool_name:
            # Use specified tool
            tool_to_use = request.tool_name
        else:
            # Auto-detect tool intent
            tool_to_use = await enhanced_mcp_executor.detect_tool_intent(request.message)
            if not tool_to_use:
                return MCPToolResponse(
                    success=False,
                    tool_used="none",
                    result="No tool intent detected in message",
                    execution_time_ms=0.0,
                    timestamp=datetime.now().isoformat(),
                    error="No suitable tool found for this message"
                )
        
        # Execute the tool
        result = await enhanced_mcp_executor.execute_tool(
            tool_to_use, 
            request.message, 
            **request.parameters
        )
        
        execution_time_ms = (time.time() - start_time) * 1000
        
        if result["success"]:
            return MCPToolResponse(
                success=True,
                tool_used=result["tool_used"],
                result=str(result["result"]),
                execution_time_ms=execution_time_ms,
                timestamp=datetime.now().isoformat()
            )
        else:
            return MCPToolResponse(
                success=False,
                tool_used=result.get("tool_used", tool_to_use),
                result="",
                execution_time_ms=execution_time_ms,
                timestamp=datetime.now().isoformat(),
                error=result.get("error", "Unknown error")
            )
        
    except Exception as e:
        logger.error(f"MCP tool execution failed: {e}")
        raise HTTPException(status_code=500, detail=f"Tool execution failed: {str(e)}")

@router.post("/detect-intent")
async def detect_tool_intent(message: str):
    """Detect what tool should be used for a given message"""
    try:
        intent = await enhanced_mcp_executor.detect_tool_intent(message)
        
        return {
            "message": message,
            "detected_tool": intent,
            "has_intent": intent is not None,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Intent detection failed: {e}")
        raise HTTPException(status_code=500, detail=f"Intent detection failed: {str(e)}")

@router.get("/health")
async def mcp_health_check():
    """Health check for MCP tools"""
    try:
        available_tools = enhanced_mcp_executor.get_available_tools()
        
        return {
            "status": "healthy",
            "total_tools": len(available_tools),
            "executor_status": "operational",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"MCP health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# Test endpoint
@router.post("/test")
async def test_mcp_tools():
    """Test all MCP tools with sample inputs"""
    try:
        test_cases = [
            ("web_search", "Search for artificial intelligence news"),
            ("calculator", "Calculate 15 * 23 + 45"),
            ("file_list", "List files in current directory"),
            ("system_info", "Get system information"),
            ("knowledge_search", "Search for machine learning in knowledge base")
        ]
        
        results = []
        for tool_name, test_message in test_cases:
            try:
                result = await enhanced_mcp_executor.execute_tool(tool_name, test_message)
                results.append({
                    "tool": tool_name,
                    "message": test_message,
                    "success": result["success"],
                    "result_length": len(str(result.get("result", ""))),
                    "error": result.get("error")
                })
            except Exception as e:
                results.append({
                    "tool": tool_name,
                    "message": test_message,
                    "success": False,
                    "result_length": 0,
                    "error": str(e)
                })
        
        return {
            "message": "MCP tools test completed",
            "test_results": results,
            "total_tests": len(test_cases),
            "successful_tests": sum(1 for r in results if r["success"]),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"MCP tools test failed: {e}")
        raise HTTPException(status_code=500, detail=f"Test failed: {str(e)}")

# Include the router in the main API
def include_enhanced_mcp_routes(app):
    """Include enhanced MCP routes in the FastAPI app"""
    app.include_router(router)
    logger.info("Enhanced MCP API routes included")
