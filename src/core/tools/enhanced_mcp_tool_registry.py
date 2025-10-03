#!/usr/bin/env python3
"""
Enhanced MCP Tool Registry
Comprehensive tool discovery, registration, and management system
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional, Callable, Type
from dataclasses import dataclass, field
from datetime import datetime
import inspect
import importlib
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class ToolMetadata:
    """Metadata for a registered tool"""
    name: str
    description: str
    category: str
    version: str = "1.0.0"
    author: str = "System"
    tags: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    return_type: str = "Dict[str, Any]"
    async_function: bool = False
    dependencies: List[str] = field(default_factory=list)
    examples: List[Dict[str, Any]] = field(default_factory=list)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    last_used: Optional[datetime] = None
    usage_count: int = 0
    success_rate: float = 0.0
    avg_latency_ms: float = 0.0

@dataclass
class ToolCapability:
    """Tool capability definition"""
    name: str
    description: str
    input_types: List[str]
    output_types: List[str]
    complexity: str  # "low", "medium", "high"
    resource_requirements: Dict[str, Any]

class EnhancedMCPToolRegistry:
    """Enhanced MCP tool registry with discovery, registration, and management"""
    
    def __init__(self):
        self.tools: Dict[str, ToolMetadata] = {}
        self.tool_functions: Dict[str, Callable] = {}
        self.capabilities: Dict[str, ToolCapability] = {}
        self.categories: Dict[str, List[str]] = {}
        self.performance_history: Dict[str, List[Dict[str, Any]]] = {}
        
        # Auto-discovery paths
        self.discovery_paths = [
            "src.core.tools",
            "src.api.tools", 
            "src.core.mcp",
            "mcp_servers"
        ]
        
        logger.info("🔧 Enhanced MCP Tool Registry initialized")
    
    async def execute_tool(self, name: str, *args, **kwargs) -> Any:
        """Execute a registered tool"""
        if name not in self.tools:
            raise ValueError(f"Tool '{name}' not found")
        
        if name not in self.tool_functions:
            raise ValueError(f"Tool function for '{name}' not found")
        
        function = self.tool_functions[name]
        metadata = self.tools[name]
        
        # Track execution
        start_time = datetime.now()
        
        try:
            if metadata.async_function:
                result = await function(*args, **kwargs)
            else:
                result = function(*args, **kwargs)
            
            # Update metrics
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            metadata.usage_count += 1
            metadata.last_used = datetime.now()
            metadata.avg_latency_ms = (metadata.avg_latency_ms * (metadata.usage_count - 1) + execution_time) / metadata.usage_count
            
            # Record performance
            if name not in self.performance_history:
                self.performance_history[name] = []
            
            self.performance_history[name].append({
                "timestamp": start_time.isoformat(),
                "execution_time_ms": execution_time,
                "success": True,
                "args_count": len(args),
                "kwargs_count": len(kwargs)
            })
            
            logger.info(f"✅ Tool '{name}' executed successfully in {execution_time:.2f}ms")
            return result
            
        except Exception as e:
            # Update error metrics
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            metadata.usage_count += 1
            metadata.last_used = datetime.now()
            
            # Record failure
            if name not in self.performance_history:
                self.performance_history[name] = []
            
            self.performance_history[name].append({
                "timestamp": start_time.isoformat(),
                "execution_time_ms": execution_time,
                "success": False,
                "error": str(e),
                "args_count": len(args),
                "kwargs_count": len(kwargs)
            })
            
            logger.error(f"❌ Tool '{name}' execution failed: {e}")
            raise e
    
    def register_tool(
        self,
        name: str,
        function: Callable,
        metadata: ToolMetadata,
        capability: Optional[ToolCapability] = None
    ):
        """Register a tool with metadata and capability"""
        self.tools[name] = metadata
        self.tool_functions[name] = function
        
        if capability:
            self.capabilities[name] = capability
        
        # Add to category
        if metadata.category not in self.categories:
            self.categories[metadata.category] = []
        self.categories[metadata.category].append(name)
        
        logger.info(f"✅ Registered tool: {name} ({metadata.category})")
    
    def discover_tools(self) -> List[str]:
        """Auto-discover tools in the codebase"""
        discovered = []
        
        for path in self.discovery_paths:
            try:
                module = importlib.import_module(path)
                discovered.extend(self._scan_module_for_tools(module))
            except ImportError:
                logger.warning(f"Could not import {path}")
        
        logger.info(f"🔍 Discovered {len(discovered)} tools")
        return discovered
    
    def _scan_module_for_tools(self, module) -> List[str]:
        """Scan a module for tool functions"""
        tools = []
        
        for name, obj in inspect.getmembers(module):
            if inspect.isfunction(obj) or inspect.ismethod(obj):
                # Check for tool indicators
                if (name.startswith('_') and name.endswith('_tool')) or \
                   name.startswith('tool_') or \
                   hasattr(obj, '__tool_metadata__'):
                    tools.append(f"{module.__name__}.{name}")
        
        return tools
    
    def get_tool_info(self, name: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive tool information"""
        if name not in self.tools:
            return None
        
        metadata = self.tools[name]
        capability = self.capabilities.get(name)
        
        info = {
            "name": name,
            "description": metadata.description,
            "category": metadata.category,
            "version": metadata.version,
            "author": metadata.author,
            "tags": metadata.tags,
            "parameters": metadata.parameters,
            "return_type": metadata.return_type,
            "async_function": metadata.async_function,
            "dependencies": metadata.dependencies,
            "examples": metadata.examples,
            "performance_metrics": metadata.performance_metrics,
            "usage_stats": {
                "usage_count": metadata.usage_count,
                "success_rate": metadata.success_rate,
                "avg_latency_ms": metadata.avg_latency_ms,
                "last_used": metadata.last_used.isoformat() if metadata.last_used else None
            }
        }
        
        if capability:
            info["capability"] = {
                "name": capability.name,
                "description": capability.description,
                "input_types": capability.input_types,
                "output_types": capability.output_types,
                "complexity": capability.complexity,
                "resource_requirements": capability.resource_requirements
            }
        
        return info
    
    def search_tools(self, query: str) -> List[Dict[str, Any]]:
        """Search tools by name, description, or tags"""
        results = []
        query_lower = query.lower()
        
        for name, metadata in self.tools.items():
            # Search in name, description, and tags
            if (query_lower in name.lower() or
                query_lower in metadata.description.lower() or
                any(query_lower in tag.lower() for tag in metadata.tags)):
                
                results.append(self.get_tool_info(name))
        
        return results
    
    def get_tool_recommendations(self, context: str, max_tools: int = 5) -> List[Dict[str, Any]]:
        """Get tool recommendations based on context"""
        # Simple keyword-based recommendation
        context_lower = context.lower()
        recommendations = []
        
        # Define context patterns
        patterns = {
            "web_search": ["search", "find", "look up", "google", "web", "internet"],
            "file_operations": ["file", "read", "write", "save", "open", "directory"],
            "calculations": ["calculate", "math", "compute", "solve", "formula"],
            "knowledge_search": ["knowledge", "rag", "search knowledge", "find in knowledge"],
            "system_info": ["system", "info", "status", "health", "metrics"],
            "code_execution": ["code", "run", "execute", "script", "program"],
            "data_analysis": ["analyze", "data", "csv", "json", "statistics"],
            "communication": ["email", "notification", "message", "send"]
        }
        
        for tool_name, metadata in self.tools.items():
            score = 0
            
            # Check category relevance
            for pattern_category, keywords in patterns.items():
                if pattern_category in metadata.category.lower():
                    for keyword in keywords:
                        if keyword in context_lower:
                            score += 1
            
            # Check description relevance
            for keyword in context_lower.split():
                if keyword in metadata.description.lower():
                    score += 0.5
            
            if score > 0:
                tool_info = self.get_tool_info(tool_name)
                tool_info["relevance_score"] = score
                recommendations.append(tool_info)
        
        # Sort by relevance score and return top results
        recommendations.sort(key=lambda x: x["relevance_score"], reverse=True)
        return recommendations[:max_tools]
    
    def get_tools_by_category(self, category: str) -> List[str]:
        """Get tools by category"""
        return [name for name, metadata in self.tools.items() if metadata.category == category]
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for all tools"""
        metrics = {}
        for name, metadata in self.tools.items():
            metrics[name] = {
                'usage_count': metadata.usage_count,
                'avg_latency_ms': metadata.avg_latency_ms,
                'last_used': metadata.last_used.isoformat() if metadata.last_used else None,
                'success_rate': self._calculate_success_rate(name)
            }
        return metrics
    
    def _calculate_success_rate(self, tool_name: str) -> float:
        """Calculate success rate for a tool"""
        if tool_name not in self.performance_history:
            return 0.0
        
        history = self.performance_history[tool_name]
        if not history:
            return 0.0
        
        successful = sum(1 for entry in history if entry.get('success', False))
        return successful / len(history)
    
    def update_tool_performance(self, name: str, success: bool, latency_ms: float):
        """Update tool performance metrics"""
        if name not in self.tools:
            return
        
        metadata = self.tools[name]
        metadata.usage_count += 1
        metadata.last_used = datetime.now()
        
        # Update success rate
        if metadata.usage_count == 1:
            metadata.success_rate = 1.0 if success else 0.0
        else:
            # Exponential moving average
            alpha = 0.1
            metadata.success_rate = alpha * (1.0 if success else 0.0) + (1 - alpha) * metadata.success_rate
        
        # Update average latency
        if metadata.usage_count == 1:
            metadata.avg_latency_ms = latency_ms
        else:
            # Exponential moving average
            alpha = 0.1
            metadata.avg_latency_ms = alpha * latency_ms + (1 - alpha) * metadata.avg_latency_ms
        
        # Store in performance history
        if name not in self.performance_history:
            self.performance_history[name] = []
        
        self.performance_history[name].append({
            "timestamp": datetime.now().isoformat(),
            "success": success,
            "latency_ms": latency_ms
        })
        
        # Keep only last 100 entries
        if len(self.performance_history[name]) > 100:
            self.performance_history[name] = self.performance_history[name][-100:]
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get comprehensive system metrics"""
        total_tools = len(self.tools)
        total_usage = sum(metadata.usage_count for metadata in self.tools.values())
        
        # Calculate average metrics
        if total_tools > 0:
            avg_success_rate = sum(metadata.success_rate for metadata in self.tools.values()) / total_tools
            avg_latency = sum(metadata.avg_latency_ms for metadata in self.tools.values()) / total_tools
        else:
            avg_success_rate = 0.0
            avg_latency = 0.0
        
        # Category breakdown
        category_stats = {}
        for category, tools in self.categories.items():
            category_usage = sum(self.tools[tool].usage_count for tool in tools)
            category_stats[category] = {
                "tool_count": len(tools),
                "total_usage": category_usage,
                "tools": tools
            }
        
        return {
            "total_tools": total_tools,
            "total_usage": total_usage,
            "avg_success_rate": avg_success_rate,
            "avg_latency_ms": avg_latency,
            "categories": category_stats,
            "top_tools": self._get_top_tools(),
            "recent_activity": self._get_recent_activity()
        }
    
    def _get_top_tools(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top performing tools"""
        tools_with_metrics = []
        
        for name, metadata in self.tools.items():
            if metadata.usage_count > 0:
                tools_with_metrics.append({
                    "name": name,
                    "usage_count": metadata.usage_count,
                    "success_rate": metadata.success_rate,
                    "avg_latency_ms": metadata.avg_latency_ms,
                    "category": metadata.category
                })
        
        # Sort by usage count
        tools_with_metrics.sort(key=lambda x: x["usage_count"], reverse=True)
        return tools_with_metrics[:limit]
    
    def _get_recent_activity(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent tool activity"""
        recent_activity = []
        cutoff_time = datetime.now().timestamp() - (hours * 3600)
        
        for name, history in self.performance_history.items():
            recent_entries = [
                entry for entry in history
                if datetime.fromisoformat(entry["timestamp"]).timestamp() > cutoff_time
            ]
            
            if recent_entries:
                recent_activity.append({
                    "tool_name": name,
                    "recent_usage": len(recent_entries),
                    "recent_success_rate": sum(1 for entry in recent_entries if entry["success"]) / len(recent_entries),
                    "recent_avg_latency": sum(entry["latency_ms"] for entry in recent_entries) / len(recent_entries)
                })
        
        # Sort by recent usage
        recent_activity.sort(key=lambda x: x["recent_usage"], reverse=True)
        return recent_activity

# Global registry instance
enhanced_tool_registry = EnhancedMCPToolRegistry()

def register_tool(
    name: str,
    description: str,
    category: str,
    function: Callable,
    **kwargs
):
    """Decorator for registering tools"""
    metadata = ToolMetadata(
        name=name,
        description=description,
        category=category,
        **kwargs
    )
    
    enhanced_tool_registry.register_tool(name, function, metadata)
    return function

def main():
    """Main function for testing"""
    # Example tool registration
    @register_tool(
        name="example_tool",
        description="An example tool for demonstration",
        category="examples",
        tags=["demo", "test"],
        async_function=True
    )
    async def example_tool(query: str) -> Dict[str, Any]:
        """Example tool implementation"""
        return {
            "success": True,
            "result": f"Processed: {query}",
            "timestamp": datetime.now().isoformat()
        }
    
    # Test registry functionality
    print("🔧 Enhanced MCP Tool Registry Test")
    print(f"Total tools: {len(enhanced_tool_registry.tools)}")
    print(f"Categories: {list(enhanced_tool_registry.categories.keys())}")
    
    # Test search
    results = enhanced_tool_registry.search_tools("example")
    print(f"Search results: {len(results)}")
    
    # Test recommendations
    recommendations = enhanced_tool_registry.get_tool_recommendations("I need to search for something")
    print(f"Recommendations: {len(recommendations)}")
    
    # Test metrics
    metrics = enhanced_tool_registry.get_system_metrics()
    print(f"System metrics: {metrics}")

if __name__ == "__main__":
    main()
