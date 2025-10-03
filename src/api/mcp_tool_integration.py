#!/usr/bin/env python3
"""
MCP Tool Integration for Chat AI
Connects the AI on port 8004 to the MCP tools on port 8000
"""

import aiohttp
import logging
import re
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class MCPToolExecutor:
    """Execute MCP tools from port 8000 Agentic Engineering Platform"""
    
    def __init__(self, mcp_base_url: str = "http://localhost:8000"):
        self.mcp_base_url = mcp_base_url
        self.available_tools = {
            "web_search": self._web_search,
            "web_crawl": self._web_crawl,
            "knowledge_search": self._knowledge_search,
            "code_assist": self._code_assist,
            "calculator": self._calculator
        }
    
    async def detect_tool_intent(self, message: str) -> Optional[str]:
        """Detect which tool the user wants to use"""
        message_lower = message.lower()
        
        # Web search patterns
        if any(keyword in message_lower for keyword in [
            "search", "google", "find", "look up", "browse", "surf"
        ]):
            return "web_search"
        
        # Calculation patterns
        if re.search(r'(?:calculate|compute|what is|what\'s)\s*:?\s*([0-9+\-*/().\s]+)', message_lower):
            return "calculator"
        
        # Knowledge search patterns
        if any(keyword in message_lower for keyword in [
            "knowledge", "documentation", "docs", "explain"
        ]):
            return "knowledge_search"
        
        # Code assistance patterns
        if any(keyword in message_lower for keyword in [
            "code", "function", "class", "debug", "fix code"
        ]):
            return "code_assist"
        
        return None
    
    async def execute_tool(self, tool_name: str, message: str) -> Dict[str, Any]:
        """Execute a specific tool"""
        if tool_name not in self.available_tools:
            return {
                "success": False,
                "error": f"Tool '{tool_name}' not found",
                "result": None
            }
        
        try:
            result = await self.available_tools[tool_name](message)
            return {
                "success": True,
                "error": None,
                "result": result,
                "tool_used": tool_name
            }
        except Exception as e:
            logger.error(f"Tool {tool_name} failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "result": None,
                "tool_used": tool_name
            }
    
    async def _web_search(self, query: str) -> str:
        """Search the web using MCP web crawler"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.mcp_base_url}/web-crawler/search",
                    json={"query": query, "max_results": 5},
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = data.get("results", [])
                        if results:
                            summary = f"Found {len(results)} results:\n"
                            for i, result in enumerate(results[:3], 1):
                                summary += f"{i}. {result.get('title', 'No title')}\n"
                                summary += f"   {result.get('snippet', 'No snippet')}\n"
                            return summary
                        return "No results found."
                    elif response.status == 404:
                        return "Web search tool not available on MCP server."
                    else:
                        return f"Search failed: HTTP {response.status}"
        except asyncio.TimeoutError:
            return "Web search timed out."
        except Exception as e:
            logger.error(f"Web search error: {e}")
            return f"Web search error: {str(e)}"
    
    async def _web_crawl(self, url: str) -> str:
        """Crawl a specific URL"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.mcp_base_url}/web-crawler/crawl",
                    json={"url": url},
                    timeout=aiohttp.ClientTimeout(total=15)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return f"Crawled: {data.get('title', 'No title')}\n{data.get('content', 'No content')[:500]}..."
                    return f"Crawl failed: HTTP {response.status}"
        except Exception as e:
            logger.error(f"Web crawl error: {e}")
            return f"Web crawl error: {str(e)}"
    
    async def _knowledge_search(self, query: str) -> str:
        """Search the knowledge graph"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.mcp_base_url}/knowledge-graph/search",
                    json={"query": query, "limit": 5},
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = data.get("results", [])
                        if results:
                            summary = f"Found {len(results)} knowledge items:\n"
                            for i, item in enumerate(results[:3], 1):
                                summary += f"{i}. {item.get('title', 'No title')}\n"
                                summary += f"   {item.get('summary', 'No summary')}\n"
                            return summary
                        return "No knowledge found."
                    return f"Knowledge search failed: HTTP {response.status}"
        except Exception as e:
            logger.error(f"Knowledge search error: {e}")
            return f"Knowledge search error: {str(e)}"
    
    async def _code_assist(self, request: str) -> str:
        """Get code assistance from MCP code assistant"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.mcp_base_url}/code-assistant/assist",
                    json={"request": request},
                    timeout=aiohttp.ClientTimeout(total=15)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("response", "No response from code assistant")
                    return f"Code assist failed: HTTP {response.status}"
        except Exception as e:
            logger.error(f"Code assist error: {e}")
            return f"Code assist error: {str(e)}"
    
    async def _calculator(self, expression: str) -> str:
        """Calculate mathematical expressions"""
        calc_pattern = r'(?:calculate|compute|what is|what\'s)\s*:?\s*([0-9+\-*/().\s]+)'
        match = re.search(calc_pattern, expression.lower())
        
        if match:
            math_expr = match.group(1).strip()
            try:
                result = eval(math_expr, {"__builtins__": {}}, {})
                return f"The calculation {math_expr} = {result}"
            except Exception as e:
                return f"Calculation error: {str(e)}"
        
        return "Could not parse calculation"

# Global instance
mcp_tool_executor = MCPToolExecutor()




