#!/usr/bin/env python3
"""
MCP Tool Registry System for Agentic LLM Core v0.1

This module implements the MCP tool registry with:
- Tool registration and discovery
- Schema validation and versioning
- Tool metadata management
- Capability indexing
- Health monitoring

Complies with:
- Agentic LLM Core Constitution (prompt_engineering/.specify/memory/constitution.md)
- System Specification: Agentic LLM Core v0.1 (specs/system.md)
- Architecture Plan: Agentic LLM Core v0.1 (plans/architecture.md)
- Milestone 2: Tool Integration System (plans/milestones.md)

Created: 2024-09-25
Status: Implementation Phase
"""

import asyncio
import logging
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Union, Callable, Set
from pathlib import Path
import json
import hashlib
import threading
from collections import defaultdict

from pydantic import BaseModel, Field, validator, ValidationError
from pydantic_ai import Agent, Tool

from ..models.contracts import ToolCall, ToolResult, ToolSchema
from ..schemas.input_schemas import ProcessedInput
from ..engines.qwen3_omni_engine import ContextAnalysis

logger = logging.getLogger(__name__)

# ============================================================================
# Data Models
# ============================================================================

class ToolCategory(str, Enum):
    """Tool categories for organization."""
    FILE_SYSTEM = "file_system"
    DATABASE = "database"
    WEB = "web"
    TEXT_PROCESSING = "text_processing"
    DATA_ANALYSIS = "data_analysis"
    UTILITY = "utility"
    CUSTOM = "custom"

class ToolStatus(str, Enum):
    """Tool status states."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEPRECATED = "deprecated"
    MAINTENANCE = "maintenance"
    ERROR = "error"

class ToolVersion(BaseModel):
    """Tool version information."""
    version: str = Field(..., description="Version string (e.g., '1.0.0')")
    release_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    changelog: str = Field(default="", description="Version changelog")
    breaking_changes: bool = Field(default=False, description="Whether this version has breaking changes")
    deprecated: bool = Field(default=False, description="Whether this version is deprecated")
    schema_hash: str = Field(..., description="Hash of the tool schema")

class ToolMetadata(BaseModel):
    """Comprehensive tool metadata."""
    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    category: ToolCategory = Field(..., description="Tool category")
    version: str = Field(default="1.0.0", description="Current version")
    author: str = Field(default="", description="Tool author")
    license: str = Field(default="", description="Tool license")
    tags: List[str] = Field(default_factory=list, description="Tool tags")
    capabilities: List[str] = Field(default_factory=list, description="Tool capabilities")
    dependencies: List[str] = Field(default_factory=list, description="Tool dependencies")
    status: ToolStatus = Field(default=ToolStatus.ACTIVE, description="Tool status")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_used: Optional[datetime] = Field(None, description="Last usage timestamp")
    usage_count: int = Field(default=0, description="Total usage count")
    success_rate: float = Field(default=0.0, description="Success rate (0.0-1.0)")
    average_execution_time: float = Field(default=0.0, description="Average execution time in seconds")
    error_count: int = Field(default=0, description="Total error count")
    health_score: float = Field(default=1.0, description="Health score (0.0-1.0)")

class ToolRegistration(BaseModel):
    """Tool registration information."""
    tool_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    metadata: ToolMetadata = Field(..., description="Tool metadata")
    schema: ToolSchema = Field(..., description="Tool schema")
    implementation: Any = Field(..., description="Tool implementation")
    version_history: List[ToolVersion] = Field(default_factory=list, description="Version history")
    registered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    registered_by: str = Field(default="system", description="Who registered the tool")

class ToolDiscoveryResult(BaseModel):
    """Result of tool discovery operation."""
    tools: List[ToolRegistration] = Field(..., description="Discovered tools")
    total_count: int = Field(..., description="Total number of tools found")
    discovery_time: float = Field(..., description="Discovery time in seconds")
    criteria_used: Dict[str, Any] = Field(..., description="Discovery criteria")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SchemaValidationResult(BaseModel):
    """Result of schema validation."""
    valid: bool = Field(..., description="Whether schema is valid")
    errors: List[str] = Field(default_factory=list, description="Validation errors")
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")
    schema_hash: str = Field(..., description="Hash of the validated schema")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ToolHealthReport(BaseModel):
    """Tool health report."""
    tool_id: str = Field(..., description="Tool identifier")
    status: ToolStatus = Field(..., description="Current status")
    health_score: float = Field(..., description="Health score (0.0-1.0)")
    last_check: datetime = Field(..., description="Last health check timestamp")
    issues: List[str] = Field(default_factory=list, description="Health issues")
    recommendations: List[str] = Field(default_factory=list, description="Health recommendations")
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Health metrics")

# ============================================================================
# Tool Registry Implementation
# ============================================================================

class MCPToolRegistry:
    """Advanced MCP tool registry with comprehensive management capabilities."""
    
    def __init__(self, max_tools: int = 1000, enable_health_monitoring: bool = True):
        self.max_tools = max_tools
        self.enable_health_monitoring = enable_health_monitoring
        
        # Core storage
        self.tools: Dict[str, ToolRegistration] = {}
        self.schemas: Dict[str, ToolSchema] = {}
        self.implementations: Dict[str, Any] = {}
        
        # Indexing
        self.capabilities_index: Dict[str, Set[str]] = defaultdict(set)
        self.category_index: Dict[ToolCategory, Set[str]] = defaultdict(set)
        self.tag_index: Dict[str, Set[str]] = defaultdict(set)
        self.status_index: Dict[ToolStatus, Set[str]] = defaultdict(set)
        
        # Version management
        self.version_history: Dict[str, List[ToolVersion]] = defaultdict(list)
        self.schema_versions: Dict[str, Dict[str, ToolSchema]] = defaultdict(dict)
        
        # Health monitoring
        self.health_reports: Dict[str, ToolHealthReport] = {}
        self.health_check_interval = 300  # 5 minutes
        self._health_monitor_task = None
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Logging
        self.logger = logging.getLogger(f"{__name__}.registry")
        
        # Start health monitoring if enabled
        if self.enable_health_monitoring:
            self._start_health_monitoring()
    
    def register_tool(self, 
                     metadata: ToolMetadata, 
                     schema: ToolSchema, 
                     implementation: Any,
                     version: str = "1.0.0") -> bool:
        """Register a tool with comprehensive validation and indexing."""
        try:
            with self._lock:
                # Check if registry is full
                if len(self.tools) >= self.max_tools:
                    self.logger.error(f"Registry is full (max {self.max_tools} tools)")
                    return False
                
                # Validate schema
                validation_result = self._validate_schema(schema)
                if not validation_result.valid:
                    self.logger.error(f"Schema validation failed for {metadata.name}: {validation_result.errors}")
                    return False
                
                # Check for name conflicts
                if metadata.name in self.tools:
                    self.logger.warning(f"Tool {metadata.name} already exists, updating...")
                    return self._update_tool(metadata, schema, implementation, version)
                
                # Create tool registration
                tool_registration = ToolRegistration(
                    metadata=metadata,
                    schema=schema,
                    implementation=implementation
                )
                
                # Add version to history
                tool_version = ToolVersion(
                    version=version,
                    schema_hash=validation_result.schema_hash
                )
                tool_registration.version_history.append(tool_version)
                
                # Store tool
                self.tools[tool_registration.tool_id] = tool_registration
                self.schemas[metadata.name] = schema
                self.implementations[metadata.name] = implementation
                
                # Update indexes
                self._update_indexes(tool_registration)
                
                # Store version history
                self.version_history[metadata.name].append(tool_version)
                self.schema_versions[metadata.name][version] = schema
                
                self.logger.info(f"Successfully registered tool: {metadata.name} v{version}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to register tool {metadata.name}: {e}")
            return False
    
    def unregister_tool(self, tool_name: str) -> bool:
        """Unregister a tool and clean up all references."""
        try:
            with self._lock:
                # Find tool by name
                tool_id = None
                for tid, tool in self.tools.items():
                    if tool.metadata.name == tool_name:
                        tool_id = tid
                        break
                
                if not tool_id:
                    self.logger.warning(f"Tool {tool_name} not found for unregistration")
                    return False
                
                # Remove from storage
                del self.tools[tool_id]
                del self.schemas[tool_name]
                del self.implementations[tool_name]
                
                # Clean up indexes
                self._cleanup_indexes(tool_name)
                
                # Clean up version history
                if tool_name in self.version_history:
                    del self.version_history[tool_name]
                if tool_name in self.schema_versions:
                    del self.schema_versions[tool_name]
                
                # Clean up health reports
                if tool_name in self.health_reports:
                    del self.health_reports[tool_name]
                
                self.logger.info(f"Successfully unregistered tool: {tool_name}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to unregister tool {tool_name}: {e}")
            return False
    
    def get_tool(self, tool_name: str) -> Optional[ToolRegistration]:
        """Get a tool registration by name."""
        with self._lock:
            for tool in self.tools.values():
                if tool.metadata.name == tool_name:
                    return tool
            return None
    
    def get_tool_implementation(self, tool_name: str) -> Optional[Any]:
        """Get tool implementation by name."""
        with self._lock:
            return self.implementations.get(tool_name)
    
    def get_tool_schema(self, tool_name: str, version: Optional[str] = None) -> Optional[ToolSchema]:
        """Get tool schema by name and optional version."""
        with self._lock:
            if version:
                return self.schema_versions.get(tool_name, {}).get(version)
            else:
                return self.schemas.get(tool_name)
    
    def discover_tools(self, 
                      criteria: Optional[Dict[str, Any]] = None) -> ToolDiscoveryResult:
        """Discover tools based on criteria."""
        start_time = time.time()
        
        try:
            with self._lock:
                discovered_tools = []
                
                # Default criteria
                if not criteria:
                    criteria = {}
                
                # Filter by status
                status_filter = criteria.get('status', [ToolStatus.ACTIVE])
                if not isinstance(status_filter, list):
                    status_filter = [status_filter]
                
                # Filter by category
                category_filter = criteria.get('category', [])
                if not isinstance(category_filter, list):
                    category_filter = [category_filter]
                
                # Filter by capabilities
                capability_filter = criteria.get('capabilities', [])
                if not isinstance(capability_filter, list):
                    capability_filter = [capability_filter]
                
                # Filter by tags
                tag_filter = criteria.get('tags', [])
                if not isinstance(tag_filter, list):
                    tag_filter = [tag_filter]
                
                # Filter by health score
                min_health_score = criteria.get('min_health_score', 0.0)
                
                # Discover tools
                for tool in self.tools.values():
                    # Check status
                    if tool.metadata.status not in status_filter:
                        continue
                    
                    # Check category
                    if category_filter and tool.metadata.category not in category_filter:
                        continue
                    
                    # Check capabilities
                    if capability_filter:
                        tool_capabilities = set(tool.metadata.capabilities)
                        if not any(cap in tool_capabilities for cap in capability_filter):
                            continue
                    
                    # Check tags
                    if tag_filter:
                        tool_tags = set(tool.metadata.tags)
                        if not any(tag in tool_tags for tag in tag_filter):
                            continue
                    
                    # Check health score
                    if tool.metadata.health_score < min_health_score:
                        continue
                    
                    discovered_tools.append(tool)
                
                # Sort by relevance
                sort_by = criteria.get('sort_by', 'health_score')
                reverse = criteria.get('reverse', True)
                
                if sort_by == 'health_score':
                    discovered_tools.sort(key=lambda t: t.metadata.health_score, reverse=reverse)
                elif sort_by == 'usage_count':
                    discovered_tools.sort(key=lambda t: t.metadata.usage_count, reverse=reverse)
                elif sort_by == 'success_rate':
                    discovered_tools.sort(key=lambda t: t.metadata.success_rate, reverse=reverse)
                elif sort_by == 'name':
                    discovered_tools.sort(key=lambda t: t.metadata.name, reverse=reverse)
                
                # Limit results
                limit = criteria.get('limit', 100)
                if limit > 0:
                    discovered_tools = discovered_tools[:limit]
                
                discovery_time = time.time() - start_time
                
                return ToolDiscoveryResult(
                    tools=discovered_tools,
                    total_count=len(discovered_tools),
                    discovery_time=discovery_time,
                    criteria_used=criteria if isinstance(criteria, dict) else criteria.model_dump() if hasattr(criteria, 'model_dump') else {}
                )
                
        except Exception as e:
            self.logger.error(f"Tool discovery failed: {e}")
            return ToolDiscoveryResult(
                tools=[],
                total_count=0,
                discovery_time=time.time() - start_time,
                criteria_used=criteria if isinstance(criteria, dict) else criteria.model_dump() if hasattr(criteria, 'model_dump') else {}
            )
    
    def get_tools_by_capability(self, capability: str) -> List[ToolRegistration]:
        """Get tools that provide a specific capability."""
        with self._lock:
            tool_names = self.capabilities_index.get(capability, set())
            return [self.tools[tid] for tid in self.tools.keys() 
                   if self.tools[tid].metadata.name in tool_names]
    
    def get_tools_by_category(self, category: ToolCategory) -> List[ToolRegistration]:
        """Get tools in a specific category."""
        with self._lock:
            tool_names = self.category_index.get(category, set())
            return [self.tools[tid] for tid in self.tools.keys() 
                   if self.tools[tid].metadata.name in tool_names]
    
    def get_tools_by_status(self, status: ToolStatus) -> List[ToolRegistration]:
        """Get tools with a specific status."""
        with self._lock:
            tool_names = self.status_index.get(status, set())
            return [self.tools[tid] for tid in self.tools.keys() 
                   if self.tools[tid].metadata.name in tool_names]
    
    def update_tool_usage(self, tool_name: str, success: bool, execution_time: float):
        """Update tool usage statistics."""
        try:
            with self._lock:
                tool = self.get_tool(tool_name)
                if not tool:
                    return
                
                # Update usage statistics
                tool.metadata.usage_count += 1
                tool.metadata.last_used = datetime.now(timezone.utc)
                tool.metadata.updated_at = datetime.now(timezone.utc)
                
                # Update success rate
                if success:
                    current_successes = tool.metadata.success_rate * (tool.metadata.usage_count - 1)
                    tool.metadata.success_rate = (current_successes + 1) / tool.metadata.usage_count
                else:
                    tool.metadata.error_count += 1
                    current_successes = tool.metadata.success_rate * (tool.metadata.usage_count - 1)
                    tool.metadata.success_rate = current_successes / tool.metadata.usage_count
                
                # Update average execution time
                current_total_time = tool.metadata.average_execution_time * (tool.metadata.usage_count - 1)
                tool.metadata.average_execution_time = (current_total_time + execution_time) / tool.metadata.usage_count
                
                # Update health score
                tool.metadata.health_score = self._calculate_health_score(tool)
                
        except Exception as e:
            self.logger.error(f"Failed to update tool usage for {tool_name}: {e}")
    
    def _validate_schema(self, schema: ToolSchema) -> SchemaValidationResult:
        """Validate tool schema with comprehensive checks."""
        try:
            errors = []
            warnings = []
            
            # Basic validation
            if not schema.input_schema:
                errors.append("Input schema is required")
            
            if not schema.output_schema:
                errors.append("Output schema is required")
            
            # Additional validation logic can be added here
            # For example, checking for required fields, data types, etc.
            
            # Generate schema hash
            schema_str = json.dumps(schema.dict(), sort_keys=True)
            schema_hash = hashlib.sha256(schema_str.encode()).hexdigest()
            
            return SchemaValidationResult(
                valid=len(errors) == 0,
                errors=errors,
                warnings=warnings,
                schema_hash=schema_hash
            )
            
        except Exception as e:
            return SchemaValidationResult(
                valid=False,
                errors=[f"Schema validation error: {str(e)}"],
                schema_hash=""
            )
    
    def _update_tool(self, 
                    metadata: ToolMetadata, 
                    schema: ToolSchema, 
                    implementation: Any,
                    version: str) -> bool:
        """Update an existing tool."""
        try:
            # Find existing tool
            existing_tool = self.get_tool(metadata.name)
            if not existing_tool:
                return False
            
            # Validate new schema
            validation_result = self._validate_schema(schema)
            if not validation_result.valid:
                self.logger.error(f"Schema validation failed for update: {validation_result.errors}")
                return False
            
            # Update tool
            existing_tool.metadata = metadata
            existing_tool.schema = schema
            existing_tool.implementation = implementation
            existing_tool.metadata.updated_at = datetime.now(timezone.utc)
            
            # Add new version
            tool_version = ToolVersion(
                version=version,
                schema_hash=validation_result.schema_hash
            )
            existing_tool.version_history.append(tool_version)
            
            # Update storage
            self.schemas[metadata.name] = schema
            self.implementations[metadata.name] = implementation
            
            # Update indexes
            self._cleanup_indexes(metadata.name)
            self._update_indexes(existing_tool)
            
            # Store version history
            self.version_history[metadata.name].append(tool_version)
            self.schema_versions[metadata.name][version] = schema
            
            self.logger.info(f"Successfully updated tool: {metadata.name} v{version}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update tool {metadata.name}: {e}")
            return False
    
    def _update_indexes(self, tool_registration: ToolRegistration):
        """Update all indexes for a tool."""
        tool_name = tool_registration.metadata.name
        
        # Update capabilities index
        for capability in tool_registration.metadata.capabilities:
            self.capabilities_index[capability].add(tool_name)
        
        # Update category index
        self.category_index[tool_registration.metadata.category].add(tool_name)
        
        # Update tag index
        for tag in tool_registration.metadata.tags:
            self.tag_index[tag].add(tool_name)
        
        # Update status index
        self.status_index[tool_registration.metadata.status].add(tool_name)
    
    def _cleanup_indexes(self, tool_name: str):
        """Clean up all indexes for a tool."""
        # Remove from capabilities index
        for capability, tools in self.capabilities_index.items():
            tools.discard(tool_name)
        
        # Remove from category index
        for category, tools in self.category_index.items():
            tools.discard(tool_name)
        
        # Remove from tag index
        for tag, tools in self.tag_index.items():
            tools.discard(tool_name)
        
        # Remove from status index
        for status, tools in self.status_index.items():
            tools.discard(tool_name)
    
    def _calculate_health_score(self, tool: ToolRegistration) -> float:
        """Calculate health score for a tool."""
        try:
            score = 1.0
            
            # Factor in success rate
            score *= tool.metadata.success_rate
            
            # Factor in error rate
            if tool.metadata.usage_count > 0:
                error_rate = tool.metadata.error_count / tool.metadata.usage_count
                score *= (1.0 - error_rate)
            
            # Factor in execution time (penalize very slow tools)
            if tool.metadata.average_execution_time > 10.0:  # 10 seconds
                score *= 0.8
            elif tool.metadata.average_execution_time > 5.0:  # 5 seconds
                score *= 0.9
            
            # Factor in status
            if tool.metadata.status == ToolStatus.ERROR:
                score *= 0.1
            elif tool.metadata.status == ToolStatus.MAINTENANCE:
                score *= 0.5
            elif tool.metadata.status == ToolStatus.DEPRECATED:
                score *= 0.3
            
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            self.logger.error(f"Failed to calculate health score for {tool.metadata.name}: {e}")
            return 0.0
    
    def _start_health_monitoring(self):
        """Start health monitoring background task."""
        if self._health_monitor_task is None or self._health_monitor_task.done():
            self._health_monitor_task = asyncio.create_task(self._health_monitor_loop())
    
    async def _health_monitor_loop(self):
        """Health monitoring background loop."""
        while True:
            try:
                await asyncio.sleep(self.health_check_interval)
                await self._perform_health_checks()
            except Exception as e:
                self.logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    async def _perform_health_checks(self):
        """Perform health checks on all tools."""
        try:
            with self._lock:
                for tool in self.tools.values():
                    health_report = await self._check_tool_health(tool)
                    self.health_reports[tool.metadata.name] = health_report
                    
                    # Update tool health score
                    tool.metadata.health_score = health_report.health_score
                    
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
    
    async def _check_tool_health(self, tool: ToolRegistration) -> ToolHealthReport:
        """Check health of a specific tool."""
        try:
            issues = []
            recommendations = []
            
            # Check success rate
            if tool.metadata.success_rate < 0.8:
                issues.append(f"Low success rate: {tool.metadata.success_rate:.2%}")
                recommendations.append("Investigate and fix tool implementation issues")
            
            # Check error count
            if tool.metadata.error_count > 10:
                issues.append(f"High error count: {tool.metadata.error_count}")
                recommendations.append("Review error logs and fix underlying issues")
            
            # Check execution time
            if tool.metadata.average_execution_time > 5.0:
                issues.append(f"Slow execution: {tool.metadata.average_execution_time:.2f}s")
                recommendations.append("Optimize tool performance")
            
            # Check last usage
            if tool.metadata.last_used:
                days_since_use = (datetime.now(timezone.utc) - tool.metadata.last_used).days
                if days_since_use > 30:
                    issues.append(f"Not used in {days_since_use} days")
                    recommendations.append("Consider deprecating if no longer needed")
            
            # Check status
            if tool.metadata.status == ToolStatus.ERROR:
                issues.append("Tool status is ERROR")
                recommendations.append("Fix tool implementation and update status")
            
            # Calculate health score
            health_score = self._calculate_health_score(tool)
            
            return ToolHealthReport(
                tool_id=tool.tool_id,
                status=tool.metadata.status,
                health_score=health_score,
                last_check=datetime.now(timezone.utc),
                issues=issues,
                recommendations=recommendations,
                metrics={
                    "usage_count": tool.metadata.usage_count,
                    "success_rate": tool.metadata.success_rate,
                    "error_count": tool.metadata.error_count,
                    "average_execution_time": tool.metadata.average_execution_time
                }
            )
            
        except Exception as e:
            self.logger.error(f"Health check failed for {tool.metadata.name}: {e}")
            return ToolHealthReport(
                tool_id=tool.tool_id,
                status=ToolStatus.ERROR,
                health_score=0.0,
                last_check=datetime.now(timezone.utc),
                issues=[f"Health check error: {str(e)}"],
                recommendations=["Fix health check implementation"]
            )
    
    def get_registry_status(self) -> Dict[str, Any]:
        """Get comprehensive registry status."""
        try:
            with self._lock:
                status = {
                    "total_tools": len(self.tools),
                    "tools_by_status": {
                        status.value: len(tools) 
                        for status, tools in self.status_index.items()
                    },
                    "tools_by_category": {
                        category.value: len(tools) 
                        for category, tools in self.category_index.items()
                    },
                    "total_capabilities": len(self.capabilities_index),
                    "health_monitoring_enabled": self.enable_health_monitoring,
                    "health_reports": len(self.health_reports),
                    "average_health_score": 0.0,
                    "tools": {}
                }
                
                # Calculate average health score
                if self.tools:
                    total_health = sum(tool.metadata.health_score for tool in self.tools.values())
                    status["average_health_score"] = total_health / len(self.tools)
                
                # Add tool details
                for tool in self.tools.values():
                    status["tools"][tool.metadata.name] = {
                        "category": tool.metadata.category.value,
                        "status": tool.metadata.status.value,
                        "version": tool.metadata.version,
                        "health_score": tool.metadata.health_score,
                        "usage_count": tool.metadata.usage_count,
                        "success_rate": tool.metadata.success_rate,
                        "capabilities": tool.metadata.capabilities,
                        "tags": tool.metadata.tags
                    }
                
                return status
                
        except Exception as e:
            self.logger.error(f"Failed to get registry status: {e}")
            return {"error": str(e)}
    
    def get_health_reports(self) -> Dict[str, ToolHealthReport]:
        """Get all health reports."""
        with self._lock:
            return self.health_reports.copy()
    
    def get_tool_health_report(self, tool_name: str) -> Optional[ToolHealthReport]:
        """Get health report for a specific tool."""
        with self._lock:
            return self.health_reports.get(tool_name)
    
    async def shutdown(self):
        """Shutdown the registry and cleanup resources."""
        try:
            # Stop health monitoring
            if self._health_monitor_task and not self._health_monitor_task.done():
                self._health_monitor_task.cancel()
                try:
                    await self._health_monitor_task
                except asyncio.CancelledError:
                    pass
            
            # Clear all data
            with self._lock:
                self.tools.clear()
                self.schemas.clear()
                self.implementations.clear()
                self.capabilities_index.clear()
                self.category_index.clear()
                self.tag_index.clear()
                self.status_index.clear()
                self.version_history.clear()
                self.schema_versions.clear()
                self.health_reports.clear()
            
            self.logger.info("Tool registry shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Registry shutdown error: {e}")

# ============================================================================
# Factory Functions
# ============================================================================

def create_tool_registry(max_tools: int = 1000, enable_health_monitoring: bool = True) -> MCPToolRegistry:
    """Create a new tool registry with specified configuration."""
    return MCPToolRegistry(max_tools, enable_health_monitoring)

def create_tool_metadata(name: str, 
                        description: str, 
                        category: ToolCategory,
                        capabilities: List[str] = None,
                        tags: List[str] = None,
                        author: str = "",
                        license: str = "") -> ToolMetadata:
    """Create tool metadata with default values."""
    return ToolMetadata(
        name=name,
        description=description,
        category=category,
        capabilities=capabilities or [],
        tags=tags or [],
        author=author,
        license=license
    )

# ============================================================================
# Export all classes and functions
# ============================================================================

__all__ = [
    # Enums
    "ToolCategory",
    "ToolStatus",
    
    # Data Models
    "ToolVersion",
    "ToolMetadata",
    "ToolRegistration",
    "ToolDiscoveryResult",
    "SchemaValidationResult",
    "ToolHealthReport",
    
    # Implementation
    "MCPToolRegistry",
    
    # Factory Functions
    "create_tool_registry",
    "create_tool_metadata",
]
