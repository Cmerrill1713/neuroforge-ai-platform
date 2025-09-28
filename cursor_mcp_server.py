#!/usr/bin/env python3
"""
Cursor MCP Server for Agentic LLM Core
Provides tools directly to Cursor via MCP protocol
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.engines.ollama_adapter import OllamaAdapter
from src.core.agents.prompt_agent import PromptAgentManager, PromptAgentRegistry
from src.core.reasoning.parallel_reasoning_engine import ParallelReasoningEngine, ReasoningMode
from src.core.knowledge.simple_knowledge_base import SimpleKnowledgeBase

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CursorMCPServer:
    """
    MCP Server for Cursor integration.
    Provides Agentic LLM Core tools directly to Cursor.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.ollama_adapter = None
        self.agent_manager = None
        self.parallel_engine = None
        self.knowledge_base = None
        
        # Tool registry
        self.tools = {}
        self._register_tools()
    
    async def initialize(self):
        """Initialize all components."""
        try:
            self.logger.info("🚀 Initializing Cursor MCP Server...")
            
            # Initialize Ollama adapter
            self.ollama_adapter = OllamaAdapter("configs/policies.yaml")
            self.logger.info("✅ Ollama adapter ready")
            
            # Initialize agent manager
            self.agent_manager = PromptAgentManager(
                self.ollama_adapter,
                PromptAgentRegistry.from_config("configs/agents.yaml"),
                default_parameters={"max_tokens": 1024, "temperature": 0.7}
            )
            self.logger.info("✅ Agent manager ready")
            
            # Initialize parallel reasoning engine
            self.parallel_engine = ParallelReasoningEngine(self.ollama_adapter)
            self.logger.info("✅ Parallel reasoning engine ready")
            
            # Initialize knowledge base
            self.knowledge_base = SimpleKnowledgeBase()
            self.logger.info("✅ Knowledge base ready")
            
            self.logger.info("🎉 Cursor MCP Server initialized successfully!")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize: {e}")
            return False
    
    def _register_tools(self):
        """Register all available tools."""
        
        self.tools = {
            # Chat and Generation Tools
            "chat": {
                "name": "chat",
                "description": "Chat with the Agentic LLM Core using intelligent agent selection",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "message": {"type": "string", "description": "User message"},
                        "task_type": {"type": "string", "default": "text_generation", "description": "Type of task"},
                        "use_parallel_reasoning": {"type": "boolean", "default": False, "description": "Use parallel reasoning"}
                    },
                    "required": ["message"]
                }
            },
            
            "generate_text": {
                "name": "generate_text",
                "description": "Generate text using Ollama models",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "prompt": {"type": "string", "description": "Text prompt"},
                        "model": {"type": "string", "default": "primary", "description": "Model to use"},
                        "max_tokens": {"type": "integer", "default": 1024, "description": "Maximum tokens"},
                        "temperature": {"type": "number", "default": 0.7, "description": "Temperature"}
                    },
                    "required": ["prompt"]
                }
            },
            
            "generate_code": {
                "name": "generate_code",
                "description": "Generate code using specialized coding agents",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "description": {"type": "string", "description": "Code description"},
                        "language": {"type": "string", "default": "python", "description": "Programming language"},
                        "framework": {"type": "string", "description": "Framework or library"}
                    },
                    "required": ["description"]
                }
            },
            
            # Parallel Reasoning Tools
            "parallel_reason": {
                "name": "parallel_reason",
                "description": "Use parallel reasoning for complex problems",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "task": {"type": "string", "description": "Task description"},
                        "mode": {"type": "string", "default": "exploration", "enum": ["exploration", "verification", "hybrid"]},
                        "num_paths": {"type": "integer", "default": 3, "description": "Number of reasoning paths"}
                    },
                    "required": ["task"]
                }
            },
            
            # Knowledge Base Tools
            "search_knowledge": {
                "name": "search_knowledge",
                "description": "Search the knowledge base for information",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "limit": {"type": "integer", "default": 5, "description": "Maximum results"}
                    },
                    "required": ["query"]
                }
            },
            
            "get_knowledge_entry": {
                "name": "get_knowledge_entry",
                "description": "Get a specific knowledge base entry",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "entry_id": {"type": "string", "description": "Entry ID"}
                    },
                    "required": ["entry_id"]
                }
            },
            
            # Agent Management Tools
            "list_agents": {
                "name": "list_agents",
                "description": "List available agents and their capabilities",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            
            "get_agent_status": {
                "name": "get_agent_status",
                "description": "Get status of a specific agent",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "agent_name": {"type": "string", "description": "Agent name"}
                    },
                    "required": ["agent_name"]
                }
            },
            
            # System Tools
            "get_system_metrics": {
                "name": "get_system_metrics",
                "description": "Get system performance metrics",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            
            "check_model_status": {
                "name": "check_model_status",
                "description": "Check status of Ollama models",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            }
        }
    
    async def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool calls from Cursor."""
        
        try:
            self.logger.info(f"🔧 Handling tool call: {tool_name}")
            
            if tool_name == "chat":
                return await self._handle_chat(arguments)
            elif tool_name == "generate_text":
                return await self._handle_generate_text(arguments)
            elif tool_name == "generate_code":
                return await self._handle_generate_code(arguments)
            elif tool_name == "parallel_reason":
                return await self._handle_parallel_reason(arguments)
            elif tool_name == "search_knowledge":
                return await self._handle_search_knowledge(arguments)
            elif tool_name == "get_knowledge_entry":
                return await self._handle_get_knowledge_entry(arguments)
            elif tool_name == "list_agents":
                return await self._handle_list_agents(arguments)
            elif tool_name == "get_agent_status":
                return await self._handle_get_agent_status(arguments)
            elif tool_name == "get_system_metrics":
                return await self._handle_get_system_metrics(arguments)
            elif tool_name == "check_model_status":
                return await self._handle_check_model_status(arguments)
            else:
                return {"error": f"Unknown tool: {tool_name}"}
                
        except Exception as e:
            self.logger.error(f"Tool call error for {tool_name}: {e}")
            return {"error": str(e)}
    
    async def _handle_chat(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle chat requests."""
        
        message = args["message"]
        task_type = args.get("task_type", "text_generation")
        use_parallel_reasoning = args.get("use_parallel_reasoning", False)
        
        # Create task request
        task_request = {
            "task_type": task_type,
            "content": message,
            "latency_requirement": 1000
        }
        
        # Select best agent
        agent_profiles = list(self.agent_manager.registry._profiles.values())
        best_agent = None
        best_score = -1
        
        for profile in agent_profiles:
            score = 0.0
            if task_type in profile.task_types:
                score += 0.4
            if profile.priority > best_score:
                best_score = profile.priority
                best_agent = profile
        
        if not best_agent:
            best_agent = agent_profiles[0] if agent_profiles else None
        
        # Generate response
        if use_parallel_reasoning:
            # Use parallel reasoning
            reasoning_result = await self.parallel_engine.parallel_reason(
                task=message,
                mode=ReasoningMode.EXPLORATION,
                num_paths=3
            )
            
            response_content = reasoning_result["best_path"]["content"] if reasoning_result["best_path"] else message
        else:
            # Simple response
            response_content = f"Response to: {message}"
        
        return {
            "response": response_content,
            "agent_name": best_agent.name if best_agent else "default",
            "task_type": task_type,
            "use_parallel_reasoning": use_parallel_reasoning,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _handle_generate_text(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle text generation."""
        
        prompt = args["prompt"]
        model = args.get("model", "primary")
        max_tokens = args.get("max_tokens", 1024)
        temperature = args.get("temperature", 0.7)
        
        try:
            response = await self.ollama_adapter.generate_response(
                model_key=model,
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return {
                "generated_text": response.content,
                "model_used": model,
                "tokens_generated": getattr(response, 'tokens_used', 0),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": f"Text generation failed: {e}"}
    
    async def _handle_generate_code(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle code generation."""
        
        description = args["description"]
        language = args.get("language", "python")
        framework = args.get("framework", "")
        
        # Create coding prompt
        prompt = f"""Generate {language} code for: {description}
        
        Framework: {framework if framework else 'Standard library'}
        
        Requirements:
        - Clean, readable code
        - Proper error handling
        - Comments explaining key parts
        - Follow best practices for {language}
        """
        
        try:
            response = await self.ollama_adapter.generate_response(
                model_key="primary",
                prompt=prompt,
                max_tokens=2048,
                temperature=0.3
            )
            
            return {
                "generated_code": response.content,
                "language": language,
                "framework": framework,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": f"Code generation failed: {e}"}
    
    async def _handle_parallel_reason(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle parallel reasoning requests."""
        
        task = args["task"]
        mode_str = args.get("mode", "exploration")
        num_paths = args.get("num_paths", 3)
        
        try:
            mode = ReasoningMode(mode_str)
            result = await self.parallel_engine.parallel_reason(
                task=task,
                mode=mode,
                num_paths=num_paths
            )
            
            return {
                "task": task,
                "mode": mode_str,
                "paths_generated": result["paths_generated"],
                "best_path": result["best_path"],
                "all_paths": result["all_paths"],
                "processing_time": result["processing_time"],
                "success": result["success"],
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": f"Parallel reasoning failed: {e}"}
    
    async def _handle_search_knowledge(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle knowledge base search."""
        
        query = args["query"]
        limit = args.get("limit", 5)
        
        try:
            # Search entries
            entries = self.knowledge_base.search(query, limit=limit)
            
            # Search content
            content_results = self.knowledge_base.search_content(query)
            
            return {
                "query": query,
                "entries_found": len(entries),
                "content_matches": len(content_results),
                "entries": entries,
                "content_results": content_results[:limit],
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": f"Knowledge search failed: {e}"}
    
    async def _handle_get_knowledge_entry(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle getting specific knowledge entry."""
        
        entry_id = args["entry_id"]
        
        try:
            entry = self.knowledge_base.get_entry(entry_id)
            
            if entry:
                return {
                    "entry_id": entry_id,
                    "title": entry.get("title", ""),
                    "content": entry.get("content", ""),
                    "authors": entry.get("authors", []),
                    "keywords": entry.get("keywords", []),
                    "created_at": entry.get("created_at", ""),
                    "found": True,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "entry_id": entry_id,
                    "found": False,
                    "error": "Entry not found",
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            return {"error": f"Failed to get entry: {e}"}
    
    async def _handle_list_agents(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle listing agents."""
        
        try:
            agents = []
            for profile in self.agent_manager.registry._profiles.values():
                agents.append({
                    "name": profile.name,
                    "task_types": profile.task_types,
                    "priority": profile.priority,
                    "tags": profile.tags,
                    "model_preferences": profile.model_preferences
                })
            
            return {
                "agents": agents,
                "total": len(agents),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": f"Failed to list agents: {e}"}
    
    async def _handle_get_agent_status(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle getting agent status."""
        
        agent_name = args["agent_name"]
        
        try:
            profile = self.agent_manager.registry.get_agent_profile(agent_name)
            
            if profile:
                return {
                    "agent_name": agent_name,
                    "status": "available",
                    "task_types": profile.task_types,
                    "priority": profile.priority,
                    "tags": profile.tags,
                    "model_preferences": profile.model_preferences,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "agent_name": agent_name,
                    "status": "not_found",
                    "error": "Agent not found",
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            return {"error": f"Failed to get agent status: {e}"}
    
    async def _handle_get_system_metrics(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle getting system metrics."""
        
        try:
            # Get parallel reasoning stats
            pr_stats = self.parallel_engine.get_performance_metrics()
            
            # Get agent count
            agent_count = len(self.agent_manager.registry._profiles)
            
            # Get knowledge base stats
            kb_stats = {
                "total_entries": len(self.knowledge_base.index["entries"]),
                "searchable_content": True
            }
            
            return {
                "parallel_reasoning": pr_stats,
                "agents": {
                    "total": agent_count,
                    "active": agent_count
                },
                "knowledge_base": kb_stats,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": f"Failed to get metrics: {e}"}
    
    async def _handle_check_model_status(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle checking model status."""
        
        try:
            # Check Ollama status
            status = await self.ollama_adapter.check_ollama_status()
            
            return {
                "ollama_status": status,
                "models_available": True,  # Simplified for now
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": f"Failed to check model status: {e}"}
    
    def get_tools_list(self) -> List[Dict[str, Any]]:
        """Get list of available tools for Cursor."""
        return list(self.tools.values())

# MCP Server Protocol Implementation
async def main():
    """Main function for MCP server."""
    
    print("🚀 Starting Cursor MCP Server for Agentic LLM Core")
    print("=" * 60)
    
    # Initialize server
    server = CursorMCPServer()
    
    if not await server.initialize():
        print("❌ Failed to initialize MCP server")
        return
    
    print("✅ MCP Server ready!")
    print("\n📋 Available Tools:")
    
    for tool in server.get_tools_list():
        print(f"   🔧 {tool['name']}: {tool['description']}")
    
    print(f"\n🎯 Total Tools: {len(server.get_tools_list())}")
    print("\n💡 To use with Cursor:")
    print("   1. Add this server to your Cursor MCP configuration")
    print("   2. Use tools like 'chat', 'generate_code', 'parallel_reason'")
    print("   3. Access knowledge base with 'search_knowledge'")
    
    # Keep server running
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Shutting down MCP server...")

if __name__ == "__main__":
    asyncio.run(main())
