#!/usr/bin/env python3
"""
MCP Server for Universal Agent Tools
Provides HTTP API for agents to access all tools
"""

import asyncio
import json
import logging
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import uvicorn
from src.core.prompting.mipro_optimizer import MIPROPromptOptimizer

from ..core.mcp.universal_agent import UniversalMCPAgent, execute_mcp_tool, get_mcp_tools, get_mcp_tool_info

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Universal MCP Agent Server",
    description="Comprehensive tool suite for AI agents",
    version="1.0.0"
)

# Pydantic models
class ToolRequest(BaseModel):
    tool_name: str
    args: Optional[List[Any]] = []
    kwargs: Optional[Dict[str, Any]] = {}

class ToolResponse(BaseModel):
    success: bool
    result: Any
    error: Optional[str] = None
    tool_name: str

class LearningRequest(BaseModel):
    example: Dict[str, Any]
    context: Optional[str] = ""

class KnowledgeRequest(BaseModel):
    knowledge: str
    category: str = "general"
    title: Optional[str] = None
    url: Optional[str] = None

# Initialize MCP agent
mcp_agent = UniversalMCPAgent()

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Universal MCP Agent Server",
        "version": "1.0.0",
        "tools_available": len(get_mcp_tools()),
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Universal MCP Agent Server",
        "tools_count": len(get_mcp_tools()),
        "timestamp": "2025-01-01T00:00:00Z"
    }

@app.get("/tools")
async def list_tools():
    """List all available tools"""
    tools = get_mcp_tools()
    tool_info = []
    
    for tool in tools:
        info = get_mcp_tool_info(tool)
        tool_info.append(info)
    
    return {
        "success": True,
        "tools": tool_info,
        "count": len(tools)
    }

@app.get("/tools/{tool_name}")
async def get_tool_info(tool_name: str):
    """Get information about a specific tool"""
    info = get_mcp_tool_info(tool_name)
    if "error" in info:
        raise HTTPException(status_code=404, detail=info["error"])
    
    return {
        "success": True,
        "tool_info": info
    }

@app.post("/execute")
async def execute_tool(request: ToolRequest):
    """Execute a tool"""
    try:
        result = await execute_mcp_tool(
            request.tool_name,
            *request.args,
            **request.kwargs
        )
        
        return ToolResponse(
            success=result.get("success", False),
            result=result,
            error=result.get("error"),
            tool_name=request.tool_name
        )
    except Exception as e:
        logger.error(f"Tool execution error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Specific tool endpoints for common operations
@app.post("/tools/file/read")
async def read_file(file_path: str):
    """Read file content"""
    result = await execute_mcp_tool("read_file", file_path)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result

@app.post("/tools/file/write")
async def write_file(file_path: str, content: str):
    """Write content to file"""
    result = await execute_mcp_tool("write_file", file_path, content)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result

@app.post("/tools/file/list")
async def list_files(directory: str = "."):
    """List directory contents"""
    result = await execute_mcp_tool("list_directory", directory)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result

@app.post("/tools/web/search")
async def web_search(query: str):
    """Perform web search"""
    result = await execute_mcp_tool("web_search", query)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result

@app.post("/tools/web/crawl")
async def web_crawl(url: str):
    """Crawl web page"""
    result = await execute_mcp_tool("web_crawl", url)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result

@app.post("/tools/calculate")
async def calculate(expression: str):
    """Calculate mathematical expression"""
    result = await execute_mcp_tool("calculate", expression)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result

@app.post("/tools/rag/query")
async def rag_query(query: str, k: int = 5):
    """Query RAG system"""
    result = await execute_mcp_tool("query_rag", query, k=k)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result

@app.post("/tools/knowledge/search")
async def search_knowledge(query: str, k: int = 5):
    """Search knowledge base"""
    result = await execute_mcp_tool("search_knowledge", query, k=k)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result

@app.post("/tools/command/execute")
async def execute_command(command: str, timeout: int = 30):
    """Execute system command"""
    result = await execute_mcp_tool("execute_command", command, timeout=timeout)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result

@app.post("/tools/code/run")
async def run_code(code: str, language: str = "python"):
    """Execute code"""
    result = await execute_mcp_tool("run_code", code, language=language)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result

@app.post("/tools/git/operation")
async def git_operation(operation: str, directory: str = "."):
    """Perform git operation"""
    result = await execute_mcp_tool("git_operation", operation, directory=directory)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result

@app.post("/tools/learn")
async def learn_from_example(request: LearningRequest):
    """Learn from example"""
    result = await execute_mcp_tool(
        "learn_from_example",
        request.example,
        context=request.context
    )
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result

@app.post("/tools/knowledge/store")
async def store_knowledge(request: KnowledgeRequest):
    """Store knowledge"""
    result = await execute_mcp_tool(
        "store_knowledge",
        request.knowledge,
        category=request.category,
        title=request.title,
        url=request.url
    )
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result

@app.post("/tools/memory/retrieve")
async def retrieve_memory(query: str):
    """Retrieve stored memory"""
    result = await execute_mcp_tool("retrieve_memory", query)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result

@app.post("/tools/analyze/data")
async def analyze_data(data: List[Any]):
    """Analyze data statistically"""
    result = await execute_mcp_tool("analyze_data", data)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result

@app.post("/tools/parse/json")
async def parse_json(json_string: str):
    """Parse JSON data"""
    result = await execute_mcp_tool("parse_json", json_string)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result

@app.post("/tools/generate/password")
async def generate_password(length: int = 16):
    """Generate secure password"""
    result = await execute_mcp_tool("generate_password", length=length)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result

@app.post("/tools/convert/timezone")
async def convert_timezone(time_str: str, from_tz: str, to_tz: str):
    """Convert time between timezones"""
    result = await execute_mcp_tool("convert_timezone", time_str, from_tz, to_tz)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result

@app.get("/tools/system/info")
async def get_system_info():
    """Get system information"""
    result = await execute_mcp_tool("get_system_info")
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result

@app.post("/tools/validate/input")
async def validate_input(input_data: Any, validation_rules: Dict[str, Any]):
    """Validate input data"""
    result = await execute_mcp_tool("validate_input", input_data, validation_rules)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result

@app.post("/tools/notification/send")
async def send_notification(message: str):
    """Send notification"""
    result = await execute_mcp_tool("send_notification", message)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result

@app.post("/tools/report/create")
async def create_report(data: Dict[str, Any], title: str = "Agent Report", summary: str = "", recommendations: List[str] = []):
    """Create report"""
    result = await execute_mcp_tool(
        "create_report",
        data,
        title=title,
        summary=summary,
        recommendations=recommendations
    )
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result

# Batch operations
@app.post("/tools/batch/execute")
async def batch_execute(requests: List[ToolRequest]):
    """Execute multiple tools in batch"""
    results = []
    
    for request in requests:
        try:
            result = await execute_mcp_tool(
                request.tool_name,
                *request.args,
                **request.kwargs
            )
            results.append({
                "tool_name": request.tool_name,
                "success": result.get("success", False),
                "result": result,
                "error": result.get("error")
            })
        except Exception as e:
            results.append({
                "tool_name": request.tool_name,
                "success": False,
                "result": None,
                "error": str(e)
            })
    
    return {
        "success": True,
        "results": results,
        "count": len(results)
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
