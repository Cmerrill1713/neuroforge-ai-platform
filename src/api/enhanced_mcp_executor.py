#!/usr/bin/env python3
"""
Enhanced MCP Tool Executor - Actually functional tools
Implements real tool execution instead of simulated responses
"""

import asyncio
import aiohttp
import json
import logging
import subprocess
import os
import re
import math
import requests
from typing import Dict, Any, Optional, List
from pathlib import Path
import urllib.parse
import tempfile

logger = logging.getLogger(__name__)

class EnhancedMCPExecutor:
    """Enhanced MCP tool executor with actually functional tools"""
    
    def __init__(self):
        self.available_tools = {
            # Web & Search Tools
            "web_search": self._web_search,
            "web_browse": self._web_browse,
            
            # File & System Tools
            "file_list": self._file_list,
            "file_read": self._file_read,
            "file_write": self._file_write,
            "directory_browse": self._directory_browse,
            
            # Math & Calculation Tools
            "calculator": self._calculator,
            "math_solver": self._calculator,
            
            # Knowledge & RAG Tools
            "knowledge_search": self._knowledge_search,
            "rag_query": self._rag_query,
            
            # System Tools
            "system_info": self._system_info,
            "process_list": self._process_list,
            
            # Utility Tools
            "url_shortener": self._url_shortener,
            "text_processor": self._text_processor
        }
    
    async def detect_tool_intent(self, message: str) -> Optional[str]:
        """Detect what tool the user wants to use"""
        message_lower = message.lower()
        
        # Web search patterns
        if any(keyword in message_lower for keyword in [
            "search", "google", "find", "look up", "browse", "web search",
            "latest news", "current events", "what's happening"
        ]):
            return "web_search"
        
        # File operations patterns
        if any(keyword in message_lower for keyword in [
            "list files", "show files", "directory", "folder", "ls", "dir",
            "file operations", "browse files", "what files"
        ]):
            return "file_list"
        
        # Calculator patterns
        if any(keyword in message_lower for keyword in [
            "calculate", "math", "solve", "compute", "what is", "what's",
            "+", "-", "*", "/", "=", "plus", "minus", "times", "divided"
        ]):
            return "calculator"
        
        # Knowledge search patterns
        if any(keyword in message_lower for keyword in [
            "knowledge", "documentation", "docs", "search knowledge",
            "find in knowledge", "look up in knowledge"
        ]):
            return "knowledge_search"
        
        # System info patterns
        if any(keyword in message_lower for keyword in [
            "system info", "system information", "system status", "system health"
        ]):
            return "system_info"
        
        return None
    
    async def execute_tool(self, tool_name: str, message: str, **kwargs) -> Dict[str, Any]:
        """Execute the specified tool"""
        if tool_name not in self.available_tools:
            return {
                "success": False,
                "error": f"Tool '{tool_name}' not available",
                "available_tools": list(self.available_tools.keys())
            }
        
        try:
            result = await self.available_tools[tool_name](message, **kwargs)
            return {
                "success": True,
                "tool_used": tool_name,
                "result": result,
                "timestamp": asyncio.get_event_loop().time()
            }
        except Exception as e:
            logger.error(f"Tool execution error for {tool_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool_used": tool_name
            }
    
    async def _web_search(self, message: str, **kwargs) -> str:
        """Perform actual web search using DuckDuckGo"""
        try:
            # Extract search query from message
            search_query = self._extract_search_query(message)
            
            # Use DuckDuckGo instant answer API
            search_url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(search_query)}&format=json&no_html=1&skip_disambig=1"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(search_url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Extract results
                        results = []
                        
                        # Abstract (instant answer)
                        if data.get('Abstract'):
                            results.append(f"**{data['Abstract']}**")
                        
                        # Related topics
                        if data.get('RelatedTopics'):
                            for topic in data['RelatedTopics'][:3]:
                                if isinstance(topic, dict) and topic.get('Text'):
                                    results.append(f"• {topic['Text'][:200]}...")
                        
                        # Definition
                        if data.get('Definition'):
                            results.append(f"**Definition:** {data['Definition']}")
                        
                        if results:
                            return f"Web search results for '{search_query}':\n\n" + "\n\n".join(results)
                        else:
                            return f"No specific results found for '{search_query}'. You may want to try a more specific search query."
                    else:
                        return f"Web search failed with status {response.status}"
                        
        except Exception as e:
            return f"Web search error: {str(e)}"
    
    async def _web_browse(self, message: str, **kwargs) -> str:
        """Browse a specific URL"""
        try:
            # Extract URL from message
            url_match = re.search(r'https?://[^\s]+', message)
            if not url_match:
                return "No URL found in message. Please provide a URL to browse."
            
            url = url_match.group(0)
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        content = await response.text()
                        # Extract title and first paragraph
                        title_match = re.search(r'<title[^>]*>(.*?)</title>', content, re.IGNORECASE)
                        title = title_match.group(1) if title_match else "No title found"
                        
                        # Extract first paragraph
                        p_match = re.search(r'<p[^>]*>(.*?)</p>', content, re.IGNORECASE | re.DOTALL)
                        if p_match:
                            paragraph = re.sub(r'<[^>]+>', '', p_match.group(1))[:500]
                        else:
                            paragraph = "No content preview available."
                        
                        return f"**URL:** {url}\n**Title:** {title}\n**Preview:** {paragraph}..."
                    else:
                        return f"Failed to browse URL {url}: HTTP {response.status}"
                        
        except Exception as e:
            return f"Web browsing error: {str(e)}"
    
    async def _file_list(self, message: str, **kwargs) -> str:
        """List files in current directory"""
        try:
            # Extract directory from message or use current directory
            directory = self._extract_directory(message) or "."
            
            if not os.path.exists(directory):
                return f"Directory '{directory}' does not exist."
            
            if not os.path.isdir(directory):
                return f"'{directory}' is not a directory."
            
            # List files and directories
            items = []
            try:
                for item in sorted(os.listdir(directory)):
                    item_path = os.path.join(directory, item)
                    if os.path.isdir(item_path):
                        items.append(f"📁 {item}/")
                    else:
                        size = os.path.getsize(item_path)
                        size_str = self._format_file_size(size)
                        items.append(f"📄 {item} ({size_str})")
                
                if items:
                    return f"Files in '{directory}':\n" + "\n".join(items[:20])  # Limit to 20 items
                else:
                    return f"Directory '{directory}' is empty."
                    
            except PermissionError:
                return f"Permission denied to list directory '{directory}'."
                
        except Exception as e:
            return f"File listing error: {str(e)}"
    
    async def _file_read(self, message: str, **kwargs) -> str:
        """Read contents of a file"""
        try:
            # Extract file path from message
            file_path = self._extract_file_path(message)
            if not file_path:
                return "No file path found in message."
            
            if not os.path.exists(file_path):
                return f"File '{file_path}' does not exist."
            
            if not os.path.isfile(file_path):
                return f"'{file_path}' is not a file."
            
            # Check file size (limit to 1MB for safety)
            file_size = os.path.getsize(file_path)
            if file_size > 1024 * 1024:  # 1MB
                return f"File '{file_path}' is too large ({self._format_file_size(file_size)}). Maximum size is 1MB."
            
            # Read file
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Limit content length
                if len(content) > 5000:
                    content = content[:5000] + "\n... (truncated)"
                
                return f"Contents of '{file_path}':\n\n{content}"
                
            except UnicodeDecodeError:
                return f"File '{file_path}' contains binary data and cannot be displayed as text."
                
        except Exception as e:
            return f"File reading error: {str(e)}"
    
    async def _file_write(self, message: str, content: str = None, **kwargs) -> str:
        """Write content to a file"""
        try:
            if not content:
                return "No content provided to write."
            
            # Extract file path from message
            file_path = self._extract_file_path(message)
            if not file_path:
                return "No file path found in message."
            
            # Create directory if it doesn't exist
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
            
            # Write file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return f"Successfully wrote {len(content)} characters to '{file_path}'."
            
        except Exception as e:
            return f"File writing error: {str(e)}"
    
    async def _directory_browse(self, message: str, **kwargs) -> str:
        """Browse directory structure"""
        return await self._file_list(message, **kwargs)
    
    async def _calculator(self, message: str, **kwargs) -> str:
        """Perform mathematical calculations"""
        try:
            # Extract mathematical expression
            expression = self._extract_math_expression(message)
            if not expression:
                return "No mathematical expression found in message."
            
            # Safe evaluation (only allow basic math operations)
            allowed_chars = set('0123456789+-*/()., ')
            if not all(c in allowed_chars for c in expression):
                return f"Invalid characters in expression: {expression}. Only numbers and basic operators (+, -, *, /, parentheses) are allowed."
            
            # Evaluate expression
            try:
                result = eval(expression, {"__builtins__": {}}, {
                    "abs": abs, "round": round, "min": min, "max": max,
                    "sum": sum, "pow": pow, "sqrt": math.sqrt
                })
                
                return f"**Calculation:** {expression}\n**Result:** {result}"
                
            except ZeroDivisionError:
                return "Error: Division by zero"
            except Exception as calc_error:
                return f"Calculation error: {str(calc_error)}"
                
        except Exception as e:
            return f"Calculator error: {str(e)}"
    
    async def _knowledge_search(self, message: str, **kwargs) -> str:
        """Search the knowledge base using the enhanced RAG system"""
        try:
            # Extract search query
            query = self._extract_search_query(message)
            
            # Call the enhanced RAG API
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "http://localhost:8004/api/rag/enhanced/search",
                    json={
                        "query_text": query,
                        "top_k": 5,
                        "deduplicate": True,
                        "use_hybrid_search": False,
                        "min_confidence": 0.3
                    },
                    timeout=10
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = data.get('results', [])
                        
                        if results:
                            formatted_results = []
                            for i, result in enumerate(results[:3], 1):
                                content = result.get('content', '')[:300]
                                score = result.get('score', 0)
                                formatted_results.append(f"{i}. (Score: {score:.3f}) {content}...")
                            
                            return f"Knowledge search results for '{query}':\n\n" + "\n\n".join(formatted_results)
                        else:
                            return f"No results found in knowledge base for '{query}'."
                    else:
                        return f"Knowledge search failed with status {response.status}"
                        
        except Exception as e:
            return f"Knowledge search error: {str(e)}"
    
    async def _rag_query(self, message: str, **kwargs) -> str:
        """Query the RAG system"""
        return await self._knowledge_search(message, **kwargs)
    
    async def _system_info(self, message: str, **kwargs) -> str:
        """Get system information"""
        try:
            import platform
            import psutil
            
            info = {
                "Platform": platform.system(),
                "Architecture": platform.architecture()[0],
                "Python Version": platform.python_version(),
                "CPU Count": psutil.cpu_count(),
                "Memory": f"{psutil.virtual_memory().total // (1024**3)} GB",
                "Disk Usage": f"{psutil.disk_usage('/').percent:.1f}%",
                "Current Directory": os.getcwd()
            }
            
            formatted_info = "\n".join([f"**{key}:** {value}" for key, value in info.items()])
            return f"**System Information:**\n\n{formatted_info}"
            
        except Exception as e:
            return f"System info error: {str(e)}"
    
    async def _process_list(self, message: str, **kwargs) -> str:
        """List running processes"""
        try:
            import psutil
            
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Sort by CPU usage
            processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
            
            # Format top 10 processes
            formatted_procs = []
            for proc in processes[:10]:
                formatted_procs.append(
                    f"PID {proc['pid']}: {proc['name']} (CPU: {proc['cpu_percent']:.1f}%, Memory: {proc['memory_percent']:.1f}%)"
                )
            
            return f"**Top 10 Processes by CPU Usage:**\n\n" + "\n".join(formatted_procs)
            
        except Exception as e:
            return f"Process list error: {str(e)}"
    
    async def _url_shortener(self, message: str, **kwargs) -> str:
        """Shorten a URL (mock implementation)"""
        url_match = re.search(r'https?://[^\s]+', message)
        if not url_match:
            return "No URL found in message."
        
        original_url = url_match.group(0)
        # Mock shortening (in real implementation, use a service like bit.ly)
        short_code = hash(original_url) % 1000000
        short_url = f"https://short.ly/{short_code}"
        
        return f"**Original URL:** {original_url}\n**Shortened URL:** {short_url}"
    
    async def _text_processor(self, message: str, **kwargs) -> str:
        """Process text (word count, character count, etc.)"""
        text = message.strip()
        
        word_count = len(text.split())
        char_count = len(text)
        char_count_no_spaces = len(text.replace(' ', ''))
        
        return f"**Text Analysis:**\n\n**Text:** {text}\n**Word Count:** {word_count}\n**Character Count:** {char_count}\n**Character Count (no spaces):** {char_count_no_spaces}"
    
    # Helper methods
    def _extract_search_query(self, message: str) -> str:
        """Extract search query from message"""
        # Remove common search prefixes
        prefixes = ["search for", "find", "look up", "google", "search", "what is", "what's"]
        query = message.lower()
        
        for prefix in prefixes:
            if query.startswith(prefix):
                query = query[len(prefix):].strip()
                break
        
        return query.strip()
    
    def _extract_directory(self, message: str) -> Optional[str]:
        """Extract directory path from message"""
        # Look for directory patterns
        dir_patterns = [
            r"in\s+([^\s]+)",
            r"directory\s+([^\s]+)",
            r"folder\s+([^\s]+)",
            r"path\s+([^\s]+)"
        ]
        
        for pattern in dir_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_file_path(self, message: str) -> Optional[str]:
        """Extract file path from message"""
        # Look for file path patterns
        path_patterns = [
            r"file\s+([^\s]+)",
            r"path\s+([^\s]+)",
            r"([/\w.-]+\.[\w]+)"  # Pattern for file.ext
        ]
        
        for pattern in path_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_math_expression(self, message: str) -> Optional[str]:
        """Extract mathematical expression from message"""
        # Look for math expressions
        math_patterns = [
            r"calculate\s+(.+)",
            r"compute\s+(.+)",
            r"what\s+is\s+(.+)",
            r"what's\s+(.+)",
            r"([0-9+\-*/().\s]+)"  # Direct math expression
        ]
        
        for pattern in math_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                expr = match.group(1).strip()
                # Basic validation
                if any(op in expr for op in ['+', '-', '*', '/']) or any(c.isdigit() for c in expr):
                    return expr
        
        return None
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tools"""
        return list(self.available_tools.keys())
    
    def get_tool_info(self, tool_name: str) -> Dict[str, Any]:
        """Get information about a specific tool"""
        if tool_name not in self.available_tools:
            return {"error": f"Tool '{tool_name}' not found"}
        
        descriptions = {
            "web_search": "Search the web using DuckDuckGo",
            "web_browse": "Browse and preview a specific URL",
            "file_list": "List files and directories",
            "file_read": "Read contents of a file",
            "file_write": "Write content to a file",
            "directory_browse": "Browse directory structure",
            "calculator": "Perform mathematical calculations",
            "knowledge_search": "Search the knowledge base",
            "rag_query": "Query the RAG system",
            "system_info": "Get system information",
            "process_list": "List running processes",
            "url_shortener": "Shorten a URL",
            "text_processor": "Analyze text (word count, etc.)"
        }
        
        return {
            "name": tool_name,
            "description": descriptions.get(tool_name, "No description available"),
            "status": "available"
        }

# Global instance
enhanced_mcp_executor = EnhancedMCPExecutor()
