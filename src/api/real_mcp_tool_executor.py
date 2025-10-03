#!/usr/bin/env python3
"""
Real MCP Tool Executor - Actually executes tools instead of returning code
"""

import asyncio
import aiohttp
import json
import logging
import subprocess
import os
import re
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class RealMCPToolExecutor:
    """Executes real tools instead of returning code"""
    
    def __init__(self):
        self.mcp_server_url = "http://localhost:8000"
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def detect_tool_intent(self, message: str) -> Optional[str]:
        """Detect what tool the user wants to use"""
        message_lower = message.lower()
        
        # Web browsing detection
        if any(keyword in message_lower for keyword in [
            "search", "browse", "web", "google", "look up", "find information",
            "latest news", "current events", "what's happening"
        ]):
            return "web_browse"
        
        # File operations detection
        if any(keyword in message_lower for keyword in [
            "list files", "show files", "directory", "folder", "ls", "dir",
            "file operations", "browse files"
        ]):
            return "file_operations"
        
        # Calculator detection
        if any(keyword in message_lower for keyword in [
            "calculate", "math", "solve", "compute", "+", "-", "*", "/", "="
        ]):
            return "calculator"
        
        # Knowledge search detection
        if any(keyword in message_lower for keyword in [
            "search knowledge", "knowledge base", "find in knowledge",
            "look up in knowledge", "search documents"
        ]):
            return "knowledge_search"
        
        return None
    
    async def execute_tool(self, tool_type: str, message: str) -> Dict[str, Any]:
        """Execute the actual tool"""
        try:
            if tool_type == "web_browse":
                return await self._execute_web_browse(message)
            elif tool_type == "file_operations":
                return await self._execute_file_operations(message)
            elif tool_type == "calculator":
                return await self._execute_calculator(message)
            elif tool_type == "knowledge_search":
                return await self._execute_knowledge_search(message)
            else:
                return {"success": False, "error": f"Unknown tool type: {tool_type}"}
        except Exception as e:
            logger.error(f"Tool execution error: {e}")
            return {"success": False, "error": str(e)}
    
    async def _execute_web_browse(self, message: str) -> Dict[str, Any]:
        """Actually browse the web"""
        try:
            # Extract search query from message
            search_query = self._extract_search_query(message)
            
            # Use curl to search (simple web search simulation)
            cmd = [
                "curl", "-s", 
                f"https://www.google.com/search?q={search_query}",
                "--user-agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                # Extract title and snippet from HTML (basic parsing)
                content = result.stdout
                titles = re.findall(r'<h3[^>]*>([^<]+)</h3>', content)
                snippets = re.findall(r'<span[^>]*>([^<]{50,200})</span>', content)
                
                results = []
                for i, title in enumerate(titles[:3]):
                    snippet = snippets[i] if i < len(snippets) else "No description available"
                    results.append({
                        "title": title,
                        "snippet": snippet,
                        "url": f"https://www.google.com/search?q={search_query}"
                    })
                
                return {
                    "success": True,
                    "tool_used": "web_browse",
                    "result": f"Web search results for '{search_query}':\n" + 
                             "\n".join([f"• {r['title']}: {r['snippet']}" for r in results])
                }
            else:
                return {
                    "success": False,
                    "error": f"Web search failed: {result.stderr}"
                }
                
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Web search timed out"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Web browse error: {str(e)}"
            }
    
    async def _execute_file_operations(self, message: str) -> Dict[str, Any]:
        """Actually list files in current directory"""
        try:
            # Get current directory
            current_dir = os.getcwd()
            
            # List files using ls command
            cmd = ["ls", "-la", current_dir]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                files = result.stdout.strip().split('\n')
                file_list = []
                
                for line in files[1:]:  # Skip total line
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 9:
                            file_info = {
                                "permissions": parts[0],
                                "size": parts[4],
                                "date": f"{parts[5]} {parts[6]} {parts[7]}",
                                "name": " ".join(parts[8:])
                            }
                            file_list.append(file_info)
                
                return {
                    "success": True,
                    "tool_used": "file_operations",
                    "result": f"Files in {current_dir}:\n" + 
                             "\n".join([f"• {f['name']} ({f['size']} bytes, {f['date']})" for f in file_list[:10]])
                }
            else:
                return {
                    "success": False,
                    "error": f"File listing failed: {result.stderr}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"File operations error: {str(e)}"
            }
    
    async def _execute_calculator(self, message: str) -> Dict[str, Any]:
        """Actually solve mathematical expressions"""
        try:
            # Extract mathematical expression
            math_expr = self._extract_math_expression(message)
            
            if not math_expr:
                return {
                    "success": False,
                    "error": "No mathematical expression found"
                }
            
            # Use Python to evaluate the expression safely
            try:
                # Replace common math symbols
                math_expr = math_expr.replace('×', '*').replace('÷', '/')
                
                # Evaluate the expression
                result = eval(math_expr)
                
                return {
                    "success": True,
                    "tool_used": "calculator",
                    "result": f"Calculation: {math_expr} = {result}"
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Calculation error: {str(e)}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Calculator error: {str(e)}"
            }
    
    async def _execute_knowledge_search(self, message: str) -> Dict[str, Any]:
        """Actually search the knowledge base"""
        try:
            # Extract search query
            search_query = self._extract_search_query(message)
            
            # Search knowledge base files
            knowledge_dir = Path("/Users/christianmerrill/Prompt Engineering/knowledge_base")
            
            if not knowledge_dir.exists():
                return {
                    "success": False,
                    "error": "Knowledge base directory not found"
                }
            
            results = []
            for file_path in knowledge_dir.glob("*.json"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Search in content
                    content = str(data).lower()
                    if search_query.lower() in content:
                        results.append({
                            "file": file_path.name,
                            "title": data.get("title", file_path.stem),
                            "preview": str(data)[:200] + "..."
                        })
                except Exception as e:
                    logger.warning(f"Error reading {file_path}: {e}")
                    continue
            
            if results:
                return {
                    "success": True,
                    "tool_used": "knowledge_search",
                    "result": f"Knowledge base search results for '{search_query}':\n" + 
                             "\n".join([f"• {r['title']} ({r['file']}): {r['preview']}" for r in results[:5]])
                }
            else:
                return {
                    "success": True,
                    "tool_used": "knowledge_search",
                    "result": f"No results found for '{search_query}' in knowledge base"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Knowledge search error: {str(e)}"
            }
    
    def _extract_search_query(self, message: str) -> str:
        """Extract search query from message"""
        # Remove common prefixes
        prefixes = [
            "search for", "look up", "find", "browse", "google",
            "web search", "search the web", "find information about"
        ]
        
        query = message.lower()
        for prefix in prefixes:
            if query.startswith(prefix):
                query = query[len(prefix):].strip()
                break
        
        # Remove quotes and clean up
        query = query.strip('"\'')
        return query if query else message
    
    def _extract_math_expression(self, message: str) -> Optional[str]:
        """Extract mathematical expression from message"""
        # Look for patterns like "15 * 23 + 45" or "calculate 15 * 23 + 45"
        patterns = [
            r'(\d+(?:\.\d+)?\s*[+\-*/]\s*\d+(?:\.\d+)?(?:\s*[+\-*/]\s*\d+(?:\.\d+)?)*)',
            r'calculate\s+(\d+(?:\.\d+)?\s*[+\-*/]\s*\d+(?:\.\d+)?(?:\s*[+\-*/]\s*\d+(?:\.\d+)?)*)',
            r'solve\s+(\d+(?:\.\d+)?\s*[+\-*/]\s*\d+(?:\.\d+)?(?:\s*[+\-*/]\s*\d+(?:\.\d+)?)*)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message)
            if match:
                return match.group(1)
        
        return None

# Global instance
real_mcp_tool_executor = RealMCPToolExecutor()
