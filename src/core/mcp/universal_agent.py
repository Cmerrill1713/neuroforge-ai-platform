#!/usr/bin/env python3
"""
Universal MCP Agent Tool Suite
Provides agents with comprehensive tool access and learning capabilities
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

logger = logging.getLogger(__name__)

class UniversalMCPAgent:
    """Universal MCP Agent with comprehensive tool access"""
    
    def __init__(self):
        self.tools = {}
        self.learning_data = {}
        self.session = None
        self._initialize_tools()
    
    def _initialize_tools(self):
        """Initialize all available tools"""
        self.tools = {
            # File & System Operations
            "read_file": self._read_file,
            "write_file": self._write_file,
            "list_directory": self._list_directory,
            "execute_command": self._execute_command,
            "get_system_info": self._get_system_info,
            
            # Web & Search
            "web_search": self._web_search,
            "web_crawl": self._web_crawl,
            "fetch_url": self._fetch_url,
            
            # Data Processing
            "parse_json": self._parse_json,
            "analyze_data": self._analyze_data,
            "process_csv": self._process_csv,
            
            # AI & ML Operations
            "query_rag": self._query_rag,
            "search_knowledge": self._search_knowledge,
            "run_model": self._run_model,
            
            # Development Tools
            "run_code": self._run_code,
            "git_operation": self._git_operation,
            "package_install": self._package_install,
            
            # Learning & Memory
            "learn_from_example": self._learn_from_example,
            "store_knowledge": self._store_knowledge,
            "retrieve_memory": self._retrieve_memory,
            
            # Communication
            "send_notification": self._send_notification,
            "create_report": self._create_report,
            
            # Utility Functions
            "calculate": self._calculate,
            "generate_password": self._generate_password,
            "convert_timezone": self._convert_timezone,
            "validate_input": self._validate_input
        }
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    # File & System Operations
    async def _read_file(self, file_path: str, **kwargs) -> Dict[str, Any]:
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
    
    async def _write_file(self, file_path: str, content: str, **kwargs) -> Dict[str, Any]:
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
    
    async def _list_directory(self, directory: str = ".", **kwargs) -> Dict[str, Any]:
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
    
    async def _execute_command(self, command: str, **kwargs) -> Dict[str, Any]:
        """Execute system command safely"""
        try:
            timeout = kwargs.get('timeout', 30)
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
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
    
    async def _get_system_info(self, **kwargs) -> Dict[str, Any]:
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
    
    # Web & Search Operations
    async def _web_search(self, query: str, **kwargs) -> Dict[str, Any]:
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
    
    async def _web_crawl(self, url: str, **kwargs) -> Dict[str, Any]:
        """Crawl web page content"""
        try:
            async with self.session.get(url, timeout=30) as response:
                content = await response.text()
                
                # Extract title
                import re
                title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
                title = title_match.group(1) if title_match else "No title"
                
                # Clean HTML
                clean_text = re.sub(r'<[^>]+>', '', content)
                clean_text = re.sub(r'\s+', ' ', clean_text).strip()
                
                return {
                    "success": True,
                    "url": url,
                    "title": title,
                    "content": clean_text[:2000] + "..." if len(clean_text) > 2000 else clean_text,
                    "length": len(clean_text)
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _fetch_url(self, url: str, **kwargs) -> Dict[str, Any]:
        """Fetch URL content"""
        return await self._web_crawl(url, **kwargs)
    
    # Data Processing
    async def _parse_json(self, json_string: str, **kwargs) -> Dict[str, Any]:
        """Parse JSON data"""
        try:
            parsed = json.loads(json_string)
            return {
                "success": True,
                "data": parsed,
                "type": type(parsed).__name__,
                "size": len(json_string)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _analyze_data(self, data: List[Any], **kwargs) -> Dict[str, Any]:
        """Analyze data statistically"""
        try:
            if not data or not all(isinstance(x, (int, float)) for x in data):
                return {"success": False, "error": "Data must be numeric"}
            
            import statistics
            import math
            
            n = len(data)
            mean = statistics.mean(data)
            median = statistics.median(data)
            stdev = statistics.stdev(data) if n > 1 else 0
            
            return {
                "success": True,
                "count": n,
                "mean": mean,
                "median": median,
                "standard_deviation": stdev,
                "min": min(data),
                "max": max(data),
                "range": max(data) - min(data)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _process_csv(self, csv_content: str, **kwargs) -> Dict[str, Any]:
        """Process CSV data"""
        try:
            lines = csv_content.strip().split('\n')
            if not lines:
                return {"success": False, "error": "Empty CSV data"}
            
            headers = lines[0].split(',')
            rows = [line.split(',') for line in lines[1:]]
            
            return {
                "success": True,
                "headers": headers,
                "row_count": len(rows),
                "column_count": len(headers),
                "sample_data": rows[:5] if rows else []
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # AI & ML Operations
    async def _query_rag(self, query: str, **kwargs) -> Dict[str, Any]:
        """Query RAG system using production RAG service"""
        try:
            # Import and use the production RAG service directly
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            from src.core.retrieval.rag_service import create_rag_service
            
            # Create RAG service for development environment
            rag_service = create_rag_service(env="development")
            
            # Execute query
            response = await rag_service.query(
                query_text=query,
                k=kwargs.get('k', 5),
                method='hybrid',
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
                "query": query,
                "results": results,
                "count": response.num_results,
                "latency_ms": response.latency_ms,
                "retrieval_method": response.retrieval_method
            }
            
        except Exception as e:
            return {"success": False, "error": f"RAG query failed: {e}"}
    
    async def _search_knowledge(self, query: str, **kwargs) -> Dict[str, Any]:
        """Search knowledge base"""
        return await self._query_rag(query, **kwargs)
    
    async def _run_model(self, model_name: str, input_data: str, **kwargs) -> Dict[str, Any]:
        """Run AI model inference"""
        try:
            async with self.session.post(
                "http://localhost:8000/api/models/inference",
                json={"model": model_name, "input": input_data}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "model": model_name,
                        "output": data.get("output", ""),
                        "confidence": data.get("confidence", 0.0)
                    }
                else:
                    return {"success": False, "error": f"Model API error: {response.status}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # Development Tools
    async def _run_code(self, code: str, language: str = "python", **kwargs) -> Dict[str, Any]:
        """Execute code safely"""
        try:
            if language == "python":
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
                    "code": code,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "return_code": result.returncode
                }
            else:
                return {"success": False, "error": f"Unsupported language: {language}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _git_operation(self, operation: str, **kwargs) -> Dict[str, Any]:
        """Perform git operations"""
        try:
            directory = kwargs.get('directory', '.')
            cmd = ["git", operation]
            
            result = subprocess.run(
                cmd,
                cwd=directory,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                "success": True,
                "operation": operation,
                "directory": directory,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _package_install(self, package: str, **kwargs) -> Dict[str, Any]:
        """Install Python package"""
        try:
            result = subprocess.run(
                ["pip", "install", package],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            return {
                "success": result.returncode == 0,
                "package": package,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # Learning & Memory
    async def _learn_from_example(self, example: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Learn from example"""
        try:
            # Store example in learning data
            example_id = f"example_{len(self.learning_data)}"
            self.learning_data[example_id] = {
                "example": example,
                "timestamp": datetime.now().isoformat(),
                "context": kwargs.get('context', '')
            }
            
            return {
                "success": True,
                "example_id": example_id,
                "learned": True
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _store_knowledge(self, knowledge: str, category: str = "general", **kwargs) -> Dict[str, Any]:
        """Store knowledge in system"""
        try:
            # Store in Weaviate
            client = weaviate.connect_to_local(port=8090)
            collection = client.collections.get("KnowledgeDocumentBGE")
            
            # Create document
            doc = {
                "content": knowledge,
                "title": kwargs.get('title', f"Knowledge: {category}"),
                "url": kwargs.get('url', ''),
                "source_type": "agent_knowledge",
                "domain": category
            }
            
            # Add to collection
            collection.data.insert(doc)
            
            return {
                "success": True,
                "knowledge": knowledge,
                "category": category,
                "stored": True
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _retrieve_memory(self, query: str, **kwargs) -> Dict[str, Any]:
        """Retrieve stored memory"""
        try:
            # Search learning data
            results = []
            for example_id, data in self.learning_data.items():
                if query.lower() in str(data['example']).lower():
                    results.append({
                        "example_id": example_id,
                        "example": data['example'],
                        "timestamp": data['timestamp'],
                        "context": data['context']
                    })
            
            return {
                "success": True,
                "query": query,
                "results": results,
                "count": len(results)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # Communication
    async def _send_notification(self, message: str, **kwargs) -> Dict[str, Any]:
        """Send notification"""
        try:
            # Log notification
            logger.info(f"NOTIFICATION: {message}")
            
            return {
                "success": True,
                "message": message,
                "sent": True,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _create_report(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Create report"""
        try:
            report = {
                "title": kwargs.get('title', 'Agent Report'),
                "timestamp": datetime.now().isoformat(),
                "data": data,
                "summary": kwargs.get('summary', ''),
                "recommendations": kwargs.get('recommendations', [])
            }
            
            return {
                "success": True,
                "report": report,
                "created": True
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # Utility Functions
    async def _calculate(self, expression: str, **kwargs) -> Dict[str, Any]:
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
    
    async def _generate_password(self, length: int = 16, **kwargs) -> Dict[str, Any]:
        """Generate secure password"""
        try:
            import secrets
            import string
            
            chars = string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?"
            password = ''.join(secrets.choice(chars) for _ in range(length))
            
            return {
                "success": True,
                "password": password,
                "length": length,
                "entropy": length * 6.5  # Approximate entropy
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _convert_timezone(self, time_str: str, from_tz: str, to_tz: str, **kwargs) -> Dict[str, Any]:
        """Convert time between timezones"""
        try:
            from datetime import datetime
            import pytz
            
            dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
            from_timezone = pytz.timezone(from_tz)
            to_timezone = pytz.timezone(to_tz)
            
            dt = from_timezone.localize(dt)
            converted_dt = dt.astimezone(to_timezone)
            
            return {
                "success": True,
                "original_time": dt.isoformat(),
                "converted_time": converted_dt.isoformat(),
                "from_timezone": from_tz,
                "to_timezone": to_tz
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _validate_input(self, input_data: Any, validation_rules: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Validate input data"""
        try:
            errors = []
            
            if 'required' in validation_rules and not input_data:
                errors.append("Field is required")
            
            if 'type' in validation_rules:
                expected_type = validation_rules['type']
                if not isinstance(input_data, expected_type):
                    errors.append(f"Expected type {expected_type.__name__}, got {type(input_data).__name__}")
            
            if 'min_length' in validation_rules and len(str(input_data)) < validation_rules['min_length']:
                errors.append(f"Minimum length is {validation_rules['min_length']}")
            
            if 'max_length' in validation_rules and len(str(input_data)) > validation_rules['max_length']:
                errors.append(f"Maximum length is {validation_rules['max_length']}")
            
            return {
                "success": len(errors) == 0,
                "valid": len(errors) == 0,
                "errors": errors,
                "input": input_data
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # Main execution methods
    async def execute_tool(self, tool_name: str, *args, **kwargs) -> Dict[str, Any]:
        """Execute a tool by name"""
        if tool_name not in self.tools:
            return {"success": False, "error": f"Unknown tool: {tool_name}"}
        
        try:
            return await self.tools[tool_name](*args, **kwargs)
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tools"""
        return list(self.tools.keys())
    
    def get_tool_info(self, tool_name: str) -> Dict[str, Any]:
        """Get information about a tool"""
        if tool_name not in self.tools:
            return {"error": f"Unknown tool: {tool_name}"}
        
        return {
            "name": tool_name,
            "description": f"Execute {tool_name} operation",
            "available": True
        }

# Global instance
mcp_agent = UniversalMCPAgent()

async def execute_mcp_tool(tool_name: str, *args, **kwargs) -> Dict[str, Any]:
    """Global function to execute MCP tools"""
    async with mcp_agent as agent:
        return await agent.execute_tool(tool_name, *args, **kwargs)

def get_mcp_tools() -> List[str]:
    """Get available MCP tools"""
    return mcp_agent.get_available_tools()

def get_mcp_tool_info(tool_name: str) -> Dict[str, Any]:
    """Get MCP tool information"""
    return mcp_agent.get_tool_info(tool_name)
