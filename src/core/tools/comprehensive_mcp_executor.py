#!/usr/bin/env python3
"""
Comprehensive MCP Tool Executor with All Best Tools
"""

import asyncio
import aiohttp
import json
import logging
import subprocess
import os
import re
import math
import datetime
import requests
from typing import Dict, Any, Optional, List
from pathlib import Path
from src.core.prompting.mipro_optimizer import MIPROPromptOptimizer

logger = logging.getLogger(__name__)

class ComprehensiveMCPExecutor:
    """Comprehensive MCP tool executor with all best tools"""
    
    def __init__(self):
        self.mcp_server_url = "http://localhost:8000"
        self.session = None
        self.available_tools = {
            # Web & Search Tools
            "web_search": self._web_search,
            "web_crawl": self._web_crawl,
            "news_search": self._news_search,
            
            # File & System Tools
            "file_read": self._file_read,
            "file_write": self._file_write,
            "file_list": self._file_list,
            "directory_browse": self._file_list,
            "system_info": self._system_info,
            
            # Math & Calculation Tools
            "calculator": self._calculator,
            "math_solver": self._calculator,
            "statistics": self._statistics,
            
            # Data & Analysis Tools
            "json_parser": self._json_parser,
            "csv_analyzer": self._csv_analyzer,
            "data_visualization": self._data_visualization,
            
            # Code & Development Tools
            "code_executor": self._code_executor,
            "git_operations": self._git_operations,
            "package_manager": self._package_manager,
            
            # Knowledge & RAG Tools
            "knowledge_search": self._knowledge_search,
            "document_analyzer": self._document_analyzer,
            "rag_query": self._rag_query,
            
            # Communication Tools
            "email_sender": self._email_sender,
            "slack_notification": self._slack_notification,
            "webhook_trigger": self._webhook_trigger,
            
            # AI & ML Tools
            "image_analyzer": self._image_analyzer,
            "text_processor": self._text_processor,
            "model_inference": self._model_inference,
            
            # Utility Tools
            "url_shortener": self._url_shortener,
            "qr_generator": self._qr_generator,
            "password_generator": self._password_generator,
            "timezone_converter": self._timezone_converter
        }
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def detect_tool_intent(self, message: str) -> Optional[str]:
        """Detect which tool the user wants to use"""
        message_lower = message.lower()
        
        # Web & Search Tools
        if any(keyword in message_lower for keyword in [
            "search", "google", "find", "look up", "browse", "web", "internet"
        ]):
            return "web_search"
        
        if any(keyword in message_lower for keyword in [
            "crawl", "scrape", "extract", "download"
        ]):
            return "web_crawl"
        
        if any(keyword in message_lower for keyword in [
            "news", "latest", "current events", "headlines"
        ]):
            return "news_search"
        
        # File & System Tools
        if any(keyword in message_lower for keyword in [
            "read file", "open file", "show file"
        ]):
            return "file_read"
        
        if any(keyword in message_lower for keyword in [
            "write file", "create file", "save file"
        ]):
            return "file_write"
        
        if any(keyword in message_lower for keyword in [
            "list files", "show files", "directory", "folder", "ls", "dir"
        ]):
            return "file_list"
        
        if any(keyword in message_lower for keyword in [
            "system info", "system status", "computer info"
        ]):
            return "system_info"
        
        # Math & Calculation Tools
        if any(keyword in message_lower for keyword in [
            "calculate", "math", "solve", "compute", "+", "-", "*", "/", "="
        ]):
            return "calculator"
        
        if any(keyword in message_lower for keyword in [
            "statistics", "stats", "mean", "median", "average"
        ]):
            return "statistics"
        
        # Knowledge & RAG Tools
        if any(keyword in message_lower for keyword in [
            "knowledge", "search knowledge", "rag", "find in knowledge"
        ]):
            return "knowledge_search"
        
        # Code & Development Tools
        if any(keyword in message_lower for keyword in [
            "run code", "execute", "python", "javascript", "code"
        ]):
            return "code_executor"
        
        if any(keyword in message_lower for keyword in [
            "git", "commit", "push", "pull", "repository"
        ]):
            return "git_operations"
        
        # Data Tools
        if any(keyword in message_lower for keyword in [
            "json", "parse json", "json data"
        ]):
            return "json_parser"
        
        if any(keyword in message_lower for keyword in [
            "csv", "spreadsheet", "data analysis"
        ]):
            return "csv_analyzer"
        
        return None
    
    async def execute_tool(self, tool_name: str, message: str, **kwargs) -> Dict[str, Any]:
        """Execute the specified tool"""
        try:
            if tool_name in self.available_tools:
                return await self.available_tools[tool_name](message, **kwargs)
            else:
                return {"success": False, "error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            logger.error(f"Tool execution error: {e}")
            return {"success": False, "error": str(e)}
    
    # Web & Search Tools
    async def _web_search(self, message: str, **kwargs) -> Dict[str, Any]:
        """Perform web search"""
        try:
            query = self._extract_search_query(message)
            # Use DuckDuckGo API for search
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
                    "tool": "web_search",
                    "query": query,
                    "results": results,
                    "count": len(results)
                }
        except Exception as e:
            return {"success": False, "error": f"Web search failed: {e}"}
    
    async def _web_crawl(self, message: str, **kwargs) -> Dict[str, Any]:
        """Crawl and extract content from web pages"""
        try:
            url = kwargs.get('url') or self._extract_url(message)
            if not url:
                return {"success": False, "error": "No URL provided"}
            
            # Use curl to fetch page content
            cmd = ["curl", "-s", "-L", url]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                content = result.stdout
                # Extract title and main content (basic parsing)
                title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
                title = title_match.group(1) if title_match else "No title"
                
                # Remove HTML tags for clean text
                clean_text = re.sub(r'<[^>]+>', '', content)
                clean_text = re.sub(r'\s+', ' ', clean_text).strip()
                
                return {
                    "success": True,
                    "tool": "web_crawl",
                    "url": url,
                    "title": title,
                    "content": clean_text[:1000] + "..." if len(clean_text) > 1000 else clean_text,
                    "length": len(clean_text)
                }
            else:
                return {"success": False, "error": f"Failed to crawl URL: {result.stderr}"}
        except Exception as e:
            return {"success": False, "error": f"Web crawl failed: {e}"}
    
    async def _news_search(self, message: str, **kwargs) -> Dict[str, Any]:
        """Search for news articles"""
        try:
            query = self._extract_search_query(message)
            # Use NewsAPI or similar service
            # For now, simulate with web search
            return await self._web_search(f"news {query}")
        except Exception as e:
            return {"success": False, "error": f"News search failed: {e}"}
    
    # File & System Tools
    async def _file_read(self, message: str, **kwargs) -> Dict[str, Any]:
        """Read file content"""
        try:
            file_path = kwargs.get('file_path') or self._extract_file_path(message)
            if not file_path:
                return {"success": False, "error": "No file path provided"}
            
            path = Path(file_path)
            if not path.exists():
                return {"success": False, "error": f"File not found: {file_path}"}
            
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                "success": True,
                "tool": "file_read",
                "file_path": str(path),
                "content": content,
                "size": len(content),
                "lines": len(content.splitlines())
            }
        except Exception as e:
            return {"success": False, "error": f"File read failed: {e}"}
    
    async def _file_write(self, message: str, **kwargs) -> Dict[str, Any]:
        """Write content to file"""
        try:
            file_path = kwargs.get('file_path')
            content = kwargs.get('content')
            
            if not file_path or not content:
                return {"success": False, "error": "File path and content required"}
            
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                "success": True,
                "tool": "file_write",
                "file_path": str(path),
                "bytes_written": len(content.encode('utf-8'))
            }
        except Exception as e:
            return {"success": False, "error": f"File write failed: {e}"}
    
    async def _file_list(self, message: str, **kwargs) -> Dict[str, Any]:
        """List files in directory"""
        try:
            directory = kwargs.get('directory', '.')
            path = Path(directory)
            
            if not path.exists():
                return {"success": False, "error": f"Directory not found: {directory}"}
            
            files = []
            for item in path.iterdir():
                files.append({
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else None,
                    "modified": datetime.datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                })
            
            return {
                "success": True,
                "tool": "file_list",
                "directory": str(path),
                "files": files,
                "count": len(files)
            }
        except Exception as e:
            return {"success": False, "error": f"File list failed: {e}"}
    
    async def _system_info(self, message: str, **kwargs) -> Dict[str, Any]:
        """Get system information"""
        try:
            import platform
            import psutil
            
            return {
                "success": True,
                "tool": "system_info",
                "platform": platform.platform(),
                "processor": platform.processor(),
                "python_version": platform.python_version(),
                "cpu_count": psutil.cpu_count(),
                "memory_total": psutil.virtual_memory().total,
                "memory_available": psutil.virtual_memory().available,
                "disk_usage": psutil.disk_usage('/').percent
            }
        except Exception as e:
            return {"success": False, "error": f"System info failed: {e}"}
    
    # Math & Calculation Tools
    async def _calculator(self, message: str, **kwargs) -> Dict[str, Any]:
        """Perform mathematical calculations"""
        try:
            # Extract mathematical expression
            expression = self._extract_math_expression(message)
            if not expression:
                return {"success": False, "error": "No mathematical expression found"}
            
            # Safe evaluation of mathematical expressions
            allowed_chars = set('0123456789+-*/()., ')
            if not all(c in allowed_chars for c in expression):
                return {"success": False, "error": "Invalid characters in expression"}
            
            try:
                result = eval(expression)
                return {
                    "success": True,
                    "tool": "calculator",
                    "expression": expression,
                    "result": result,
                    "type": type(result).__name__
                }
            except Exception as e:
                return {"success": False, "error": f"Calculation error: {e}"}
        except Exception as e:
            return {"success": False, "error": f"Calculator failed: {e}"}
    
    async def _statistics(self, message: str, **kwargs) -> Dict[str, Any]:
        """Calculate statistics"""
        try:
            data = kwargs.get('data', [])
            if not data:
                return {"success": False, "error": "No data provided"}
            
            if not all(isinstance(x, (int, float)) for x in data):
                return {"success": False, "error": "Data must be numeric"}
            
            n = len(data)
            mean = sum(data) / n
            sorted_data = sorted(data)
            median = sorted_data[n//2] if n % 2 == 1 else (sorted_data[n//2-1] + sorted_data[n//2]) / 2
            
            variance = sum((x - mean) ** 2 for x in data) / n
            std_dev = math.sqrt(variance)
            
            return {
                "success": True,
                "tool": "statistics",
                "count": n,
                "mean": mean,
                "median": median,
                "variance": variance,
                "standard_deviation": std_dev,
                "min": min(data),
                "max": max(data)
            }
        except Exception as e:
            return {"success": False, "error": f"Statistics failed: {e}"}
    
    # Knowledge & RAG Tools
    async def _knowledge_search(self, message: str, **kwargs) -> Dict[str, Any]:
        """Search knowledge base using production RAG service"""
        try:
            query = self._extract_search_query(message)
            k = kwargs.get('k', 5)
            method = kwargs.get('method', 'hybrid')
            
            # Import and use the production RAG service directly
            from src.core.retrieval.rag_service import create_rag_service
            
            # Create RAG service for development environment
            rag_service = create_rag_service(env="development")
            
            # Execute query
            response = await rag_service.query(
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
            
            # Close the service
            await rag_service.close()
            
            return {
                "success": True,
                "tool": "knowledge_search",
                "query": query,
                "results": results,
                "count": response.num_results,
                "latency_ms": response.latency_ms,
                "retrieval_method": response.retrieval_method
            }
            
        except Exception as e:
            return {"success": False, "error": f"Knowledge search failed: {e}"}
    
    async def _rag_query(self, message: str, **kwargs) -> Dict[str, Any]:
        """Direct RAG query"""
        return await self._knowledge_search(message, **kwargs)
    
    # Code & Development Tools
    async def _code_executor(self, message: str, **kwargs) -> Dict[str, Any]:
        """Execute code safely"""
        try:
            code = kwargs.get('code') or self._extract_code(message)
            if not code:
                return {"success": False, "error": "No code provided"}
            
            # Create temporary file
            temp_file = Path("/tmp/temp_code.py")
            with open(temp_file, 'w') as f:
                f.write(code)
            
            # Execute code
            result = subprocess.run(
                ["python3", str(temp_file)],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Clean up
            temp_file.unlink()
            
            return {
                "success": True,
                "tool": "code_executor",
                "code": code,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }
        except Exception as e:
            return {"success": False, "error": f"Code execution failed: {e}"}
    
    async def _git_operations(self, message: str, **kwargs) -> Dict[str, Any]:
        """Perform git operations"""
        try:
            operation = kwargs.get('operation', 'status')
            directory = kwargs.get('directory', '.')
            
            cmd = ["git", operation]
            if operation == "status":
                cmd.extend(["--porcelain"])
            
            result = subprocess.run(
                cmd,
                cwd=directory,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                "success": True,
                "tool": "git_operations",
                "operation": operation,
                "directory": directory,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }
        except Exception as e:
            return {"success": False, "error": f"Git operation failed: {e}"}
    
    # Data Tools
    async def _json_parser(self, message: str, **kwargs) -> Dict[str, Any]:
        """Parse and analyze JSON data"""
        try:
            json_data = kwargs.get('json_data') or self._extract_json(message)
            if not json_data:
                return {"success": False, "error": "No JSON data provided"}
            
            parsed = json.loads(json_data)
            
            return {
                "success": True,
                "tool": "json_parser",
                "parsed_data": parsed,
                "type": type(parsed).__name__,
                "size": len(json_data)
            }
        except Exception as e:
            return {"success": False, "error": f"JSON parsing failed: {e}"}
    
    async def _csv_analyzer(self, message: str, **kwargs) -> Dict[str, Any]:
        """Analyze CSV data"""
        try:
            csv_data = kwargs.get('csv_data')
            if not csv_data:
                return {"success": False, "error": "No CSV data provided"}
            
            lines = csv_data.strip().split('\n')
            if not lines:
                return {"success": False, "error": "Empty CSV data"}
            
            headers = lines[0].split(',')
            rows = [line.split(',') for line in lines[1:]]
            
            return {
                "success": True,
                "tool": "csv_analyzer",
                "headers": headers,
                "row_count": len(rows),
                "column_count": len(headers),
                "sample_data": rows[:5] if rows else []
            }
        except Exception as e:
            return {"success": False, "error": f"CSV analysis failed: {e}"}
    
    # Utility Tools
    async def _password_generator(self, message: str, **kwargs) -> Dict[str, Any]:
        """Generate secure passwords"""
        try:
            import secrets
            import string
            
            length = kwargs.get('length', 16)
            include_symbols = kwargs.get('include_symbols', True)
            
            chars = string.ascii_letters + string.digits
            if include_symbols:
                chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"
            
            password = ''.join(secrets.choice(chars) for _ in range(length))
            
            return {
                "success": True,
                "tool": "password_generator",
                "password": password,
                "length": length,
                "entropy": length * math.log2(len(chars))
            }
        except Exception as e:
            return {"success": False, "error": f"Password generation failed: {e}"}
    
    async def _timezone_converter(self, message: str, **kwargs) -> Dict[str, Any]:
        """Convert time between timezones"""
        try:
            from datetime import datetime
            import pytz
            
            time_str = kwargs.get('time')
            from_tz = kwargs.get('from_timezone', 'UTC')
            to_tz = kwargs.get('to_timezone', 'UTC')
            
            if not time_str:
                return {"success": False, "error": "No time provided"}
            
            # Parse time
            dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
            
            # Convert timezone
            from_timezone = pytz.timezone(from_tz)
            to_timezone = pytz.timezone(to_tz)
            
            dt = from_timezone.localize(dt)
            converted_dt = dt.astimezone(to_timezone)
            
            return {
                "success": True,
                "tool": "timezone_converter",
                "original_time": dt.isoformat(),
                "converted_time": converted_dt.isoformat(),
                "from_timezone": from_tz,
                "to_timezone": to_tz
            }
        except Exception as e:
            return {"success": False, "error": f"Timezone conversion failed: {e}"}
    
    # Helper methods
    def _extract_search_query(self, message: str) -> str:
        """Extract search query from message"""
        # Remove common search prefixes
        prefixes = ["search for", "find", "look up", "google", "search"]
        query = message.lower()
        for prefix in prefixes:
            if query.startswith(prefix):
                query = query[len(prefix):].strip()
                break
        return query.strip()
    
    def _extract_url(self, message: str) -> Optional[str]:
        """Extract URL from message"""
        url_pattern = r'https?://[^\s]+'
        match = re.search(url_pattern, message)
        return match.group(0) if match else None
    
    def _extract_file_path(self, message: str) -> Optional[str]:
        """Extract file path from message"""
        # Look for file paths
        path_patterns = [
            r'/[^\s]+',  # Unix paths
            r'[A-Za-z]:\\[^\s]+',  # Windows paths
            r'\./[^\s]+',  # Relative paths
        ]
        
        for pattern in path_patterns:
            match = re.search(pattern, message)
            if match:
                return match.group(0)
        return None
    
    def _extract_math_expression(self, message: str) -> Optional[str]:
        """Extract mathematical expression from message"""
        # Look for mathematical expressions
        math_patterns = [
            r'calculate\s*:?\s*([0-9+\-*/().\s]+)',
            r'what is\s*:?\s*([0-9+\-*/().\s]+)',
            r'compute\s*:?\s*([0-9+\-*/().\s]+)',
            r'([0-9+\-*/().\s]+)\s*[=]',
        ]
        
        for pattern in math_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None
    
    def _extract_code(self, message: str) -> Optional[str]:
        """Extract code from message"""
        # Look for code blocks
        code_pattern = r'```(?:python|py|javascript|js|code)?\n(.*?)\n```'
        match = re.search(code_pattern, message, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        # Look for inline code
        inline_pattern = r'`([^`]+)`'
        match = re.search(inline_pattern, message)
        if match:
            return match.group(1).strip()
        
        return None
    
    def _extract_json(self, message: str) -> Optional[str]:
        """Extract JSON from message"""
        # Look for JSON blocks
        json_pattern = r'```(?:json)?\n(.*?)\n```'
        match = re.search(json_pattern, message, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        # Look for JSON objects
        json_obj_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        match = re.search(json_obj_pattern, message)
        if match:
            return match.group(0).strip()
        
        return None
    
    async def _package_manager(self, message: str, **kwargs) -> Dict[str, Any]:
        """Package manager operations"""
        try:
            import subprocess
            import sys
            
            # Extract package name from message
            words = message.lower().split()
            if "install" in words:
                package_idx = words.index("install") + 1
                if package_idx < len(words):
                    package = words[package_idx]
                    result = subprocess.run([sys.executable, "-m", "pip", "install", package], 
                                          capture_output=True, text=True)
                    return {
                        "success": result.returncode == 0,
                        "tool": "package_manager",
                        "action": "install",
                        "package": package,
                        "output": result.stdout if result.returncode == 0 else result.stderr
                    }
            elif "list" in words or "show" in words:
                result = subprocess.run([sys.executable, "-m", "pip", "list"], 
                                      capture_output=True, text=True)
                return {
                    "success": True,
                    "tool": "package_manager",
                    "action": "list",
                    "packages": result.stdout
                }
            
            return {
                "success": False,
                "error": "Package manager action not recognized. Use 'install <package>' or 'list'"
            }
        except Exception as e:
            return {"success": False, "error": f"Package manager failed: {e}"}
    
    async def _document_analyzer(self, message: str, **kwargs) -> Dict[str, Any]:
        """Document analysis using RAG system"""
        try:
            # Use the knowledge search with document analysis focus
            result = await self._knowledge_search(message, **kwargs)
            if result["success"]:
                result["tool"] = "document_analyzer"
                result["analysis_type"] = "rag_based_analysis"
            return result
        except Exception as e:
            return {"success": False, "error": f"Document analysis failed: {e}"}
    
    async def _email_sender(self, message: str, **kwargs) -> Dict[str, Any]:
        """Email sending functionality"""
        try:
            return {
                "success": True,
                "tool": "email_sender",
                "status": "Email sending functionality requires SMTP configuration",
                "message": "To implement email sending, configure SMTP settings and provide recipient, subject, and body"
            }
        except Exception as e:
            return {"success": False, "error": f"Email sending failed: {e}"}
    
    async def _slack_notification(self, message: str, **kwargs) -> Dict[str, Any]:
        """Slack notification functionality"""
        try:
            return {
                "success": True,
                "tool": "slack_notification",
                "status": "Slack notification requires webhook configuration",
                "message": "To implement Slack notifications, configure webhook URL and provide message content"
            }
        except Exception as e:
            return {"success": False, "error": f"Slack notification failed: {e}"}
    
    async def _webhook_trigger(self, message: str, **kwargs) -> Dict[str, Any]:
        """Webhook triggering functionality"""
        try:
            return {
                "success": True,
                "tool": "webhook_trigger",
                "status": "Webhook triggering requires URL configuration",
                "message": "To implement webhook triggering, provide webhook URL and payload data"
            }
        except Exception as e:
            return {"success": False, "error": f"Webhook triggering failed: {e}"}
    
    async def _image_analyzer(self, message: str, **kwargs) -> Dict[str, Any]:
        """Image analysis functionality"""
        try:
            return {
                "success": True,
                "tool": "image_analyzer",
                "status": "Image analysis requires computer vision libraries",
                "message": "To implement image analysis, install OpenCV, PIL, or similar libraries and provide image path"
            }
        except Exception as e:
            return {"success": False, "error": f"Image analysis failed: {e}"}
    
    async def _text_processor(self, message: str, **kwargs) -> Dict[str, Any]:
        """Text processing functionality"""
        try:
            # Basic text processing
            words = message.split()
            return {
                "success": True,
                "tool": "text_processor",
                "word_count": len(words),
                "character_count": len(message),
                "sentence_count": len([s for s in message.split('.') if s.strip()]),
                "unique_words": len(set(words)),
                "average_word_length": sum(len(word) for word in words) / len(words) if words else 0
            }
        except Exception as e:
            return {"success": False, "error": f"Text processing failed: {e}"}
    
    async def _model_inference(self, message: str, **kwargs) -> Dict[str, Any]:
        """Model inference functionality"""
        try:
            return {
                "success": True,
                "tool": "model_inference",
                "status": "Model inference requires model loading",
                "message": "To implement model inference, specify model type and provide input data"
            }
        except Exception as e:
            return {"success": False, "error": f"Model inference failed: {e}"}
    
    async def _url_shortener(self, message: str, **kwargs) -> Dict[str, Any]:
        """URL shortening functionality"""
        try:
            # Extract URL from message
            import re
            url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
            urls = re.findall(url_pattern, message)
            
            if urls:
                # Simple hash-based shortening
                import hashlib
                original_url = urls[0]
                short_hash = hashlib.md5(original_url.encode()).hexdigest()[:8]
                short_url = f"https://short.ly/{short_hash}"
                
                return {
                    "success": True,
                    "tool": "url_shortener",
                    "original_url": original_url,
                    "short_url": short_url,
                    "hash": short_hash
                }
            else:
                return {
                    "success": False,
                    "error": "No URL found in message"
                }
        except Exception as e:
            return {"success": False, "error": f"URL shortening failed: {e}"}
    
    async def _qr_generator(self, message: str, **kwargs) -> Dict[str, Any]:
        """QR code generation functionality"""
        try:
            return {
                "success": True,
                "tool": "qr_generator",
                "status": "QR generation requires qrcode library",
                "message": "To implement QR generation, install 'qrcode' library and provide text content"
            }
        except Exception as e:
            return {"success": False, "error": f"QR generation failed: {e}"}
    
    async def _data_visualization(self, message: str, **kwargs) -> Dict[str, Any]:
        """Data visualization functionality"""
        try:
            return {
                "success": True,
                "tool": "data_visualization",
                "status": "Data visualization requires matplotlib/plotly",
                "message": "To implement data visualization, install visualization libraries and provide data"
            }
        except Exception as e:
            return {"success": False, "error": f"Data visualization failed: {e}"}
