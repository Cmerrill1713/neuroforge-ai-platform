#!/usr/bin/env python3
"""
Knowledge Base MCP Server
Provides access to the knowledge base through MCP protocol
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class KnowledgeBaseMCPServer:
    """MCP Server for Knowledge Base operations"""
    
    def __init__(self):
        self.knowledge_dir = Path("/Users/christianmerrill/Prompt Engineering/knowledge_base")
        self.tools = {
            "search_knowledge": {
                "name": "search_knowledge",
                "description": "Search the knowledge base for relevant information",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "limit": {"type": "integer", "description": "Maximum number of results", "default": 5}
                    },
                    "required": ["query"]
                }
            },
            "get_knowledge_stats": {
                "name": "get_knowledge_stats",
                "description": "Get statistics about the knowledge base",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            "list_documents": {
                "name": "list_documents",
                "description": "List documents in the knowledge base",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "offset": {"type": "integer", "description": "Offset for pagination", "default": 0},
                        "limit": {"type": "integer", "description": "Maximum number of documents", "default": 10}
                    }
                }
            }
        }
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP requests"""
        try:
            method = request.get("method")
            params = request.get("params", {})
            
            if method == "tools/list":
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "tools": list(self.tools.values())
                    }
                }
            
            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                if tool_name == "search_knowledge":
                    result = await self.search_knowledge(arguments.get("query", ""), arguments.get("limit", 5))
                elif tool_name == "get_knowledge_stats":
                    result = await self.get_knowledge_stats()
                elif tool_name == "list_documents":
                    result = await self.list_documents(arguments.get("offset", 0), arguments.get("limit", 10))
                else:
                    return {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "error": {
                            "code": -32601,
                            "message": f"Unknown tool: {tool_name}"
                        }
                    }
                
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(result, indent=2)
                            }
                        ]
                    }
                }
            
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {
                        "code": -32601,
                        "message": f"Unknown method: {method}"
                    }
                }
        
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
    
    async def search_knowledge(self, query: str, limit: int = 5) -> Dict[str, Any]:
        """Search the knowledge base"""
        try:
            if not self.knowledge_dir.exists():
                return {"results": [], "total": 0, "error": "Knowledge base not found"}
            
            json_files = list(self.knowledge_dir.glob("*.json"))
            results = []
            
            for file_path in json_files[:limit]:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                    # Enhanced text search
                    content = str(data).lower()
                    query_lower = query.lower()
                    
                    # Search in multiple fields
                    searchable_text = " ".join([
                        str(data.get("title", "")),
                        str(data.get("content", "")),
                        str(data.get("text", "")),
                        str(data.get("description", "")),
                        str(data)
                    ]).lower()
                    
                    if query_lower in searchable_text:
                        results.append({
                            "source": data.get("source", "unknown"),
                            "url": data.get("url", ""),
                            "title": data.get("title", file_path.stem),
                            "content_preview": str(data)[:200] + "...",
                            "filename": file_path.name
                        })
                except Exception as e:
                    logger.warning(f"Error reading {file_path}: {e}")
                    continue
            
            return {
                "results": results,
                "total": len(results),
                "query": query,
                "limit": limit
            }
        
        except Exception as e:
            logger.error(f"Error searching knowledge: {e}")
            return {"results": [], "total": 0, "error": str(e)}
    
    async def get_knowledge_stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics"""
        try:
            if not self.knowledge_dir.exists():
                return {
                    "total_documents": 0,
                    "total_chunks": 0,
                    "last_updated": datetime.now().isoformat(),
                    "index_size": 0,
                    "status": "not_found"
                }
            
            json_files = list(self.knowledge_dir.glob("*.json"))
            total_docs = len(json_files)
            total_size = sum(f.stat().st_size for f in json_files if f.exists())
            
            return {
                "total_documents": total_docs,
                "total_chunks": total_docs * 5,  # Estimate
                "last_updated": datetime.now().isoformat(),
                "index_size": total_size,
                "status": "operational" if total_docs > 0 else "empty"
            }
        
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {
                "total_documents": 0,
                "total_chunks": 0,
                "last_updated": datetime.now().isoformat(),
                "index_size": 0,
                "status": "error"
            }
    
    async def list_documents(self, offset: int = 0, limit: int = 10) -> Dict[str, Any]:
        """List documents in the knowledge base"""
        try:
            if not self.knowledge_dir.exists():
                return {"documents": [], "total": 0}
            
            json_files = list(self.knowledge_dir.glob("*.json"))
            total = len(json_files)
            
            start = offset
            end = min(offset + limit, total)
            paginated_files = json_files[start:end]
            
            documents = []
            for file_path in paginated_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        documents.append({
                            "filename": file_path.name,
                            "size": file_path.stat().st_size,
                            "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                            "source": data.get("source", "unknown"),
                            "url": data.get("url", ""),
                            "title": data.get("title", file_path.stem)
                        })
                except Exception as e:
                    logger.warning(f"Error reading {file_path}: {e}")
                    documents.append({
                        "filename": file_path.name,
                        "size": file_path.stat().st_size,
                        "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                        "source": "unknown",
                        "url": "",
                        "title": file_path.stem
                    })
            
            return {
                "documents": documents,
                "total": total,
                "offset": offset,
                "limit": limit
            }
        
        except Exception as e:
            logger.error(f"Error listing documents: {e}")
            return {"documents": [], "total": 0, "error": str(e)}

async def main():
    """Main MCP server loop"""
    server = KnowledgeBaseMCPServer()
    logger.info("🚀 Starting Knowledge Base MCP Server...")
    
    try:
        while True:
            # Read JSON-RPC request from stdin
            line = await asyncio.get_event_loop().run_in_executor(None, input)
            if not line:
                break
            
            try:
                request = json.loads(line)
                response = await server.handle_request(request)
                print(json.dumps(response))
            except json.JSONDecodeError:
                logger.error("Invalid JSON received")
            except Exception as e:
                logger.error(f"Error processing request: {e}")
    
    except KeyboardInterrupt:
        logger.info("Shutting down MCP server...")

if __name__ == "__main__":
    asyncio.run(main())
