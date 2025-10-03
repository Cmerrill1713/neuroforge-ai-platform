#!/usr/bin/env python3
"""
Enhanced Agent Selector for Intelligent Agent Routing
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class AgentSelection:
    """Result of agent selection"""
    agent_name: str
    confidence: float
    reasoning: str
    metadata: Dict[str, Any]
    timestamp: datetime

class EnhancedAgentSelector:
    """
    Enhanced agent selector with intelligent routing capabilities
    """
    
    def __init__(self):
        self.agent_registry = {}
        self.selection_history = []
        self.logger = logging.getLogger(__name__)
        logger.info("EnhancedAgentSelector initialized")
    
    def register_agent(self, name: str, capabilities: List[str], metadata: Dict[str, Any] = None):
        """Register an agent with its capabilities"""
        self.agent_registry[name] = {
            "capabilities": capabilities,
            "metadata": metadata or {},
            "usage_count": 0,
            "success_rate": 1.0
        }
        logger.info(f"Registered agent: {name} with capabilities: {capabilities}")
    
    def select_agent(self, task_description: str, context: Dict[str, Any] = None) -> AgentSelection:
        """Select the best agent for a given task"""
        context = context or {}
        
        # Simple rule-based selection for now
        task_lower = task_description.lower()
        
        if any(keyword in task_lower for keyword in ["code", "programming", "debug", "script"]):
            agent_name = "coding"
            confidence = 0.9
            reasoning = "Task appears to be programming-related"
        elif any(keyword in task_lower for keyword in ["analyze", "research", "search", "find"]):
            agent_name = "research"
            confidence = 0.8
            reasoning = "Task appears to be research/analysis-related"
        elif any(keyword in task_lower for keyword in ["creative", "write", "generate", "story"]):
            agent_name = "creative"
            confidence = 0.8
            reasoning = "Task appears to be creative writing-related"
        else:
            agent_name = "general"
            confidence = 0.7
            reasoning = "Using general agent for unspecified task"
        
        # Update usage count
        if agent_name in self.agent_registry:
            self.agent_registry[agent_name]["usage_count"] += 1
        
        selection = AgentSelection(
            agent_name=agent_name,
            confidence=confidence,
            reasoning=reasoning,
            metadata={
                "task_description": task_description,
                "context": context,
                "available_agents": list(self.agent_registry.keys())
            },
            timestamp=datetime.now()
        )
        
        self.selection_history.append(selection)
        logger.info(f"Selected agent: {agent_name} (confidence: {confidence})")
        
        return selection
    
    def get_agent_stats(self) -> Dict[str, Any]:
        """Get statistics about agent usage"""
        return {
            "total_selections": len(self.selection_history),
            "agent_registry": self.agent_registry,
            "recent_selections": [
                {
                    "agent": sel.agent_name,
                    "confidence": sel.confidence,
                    "timestamp": sel.timestamp.isoformat()
                }
                for sel in self.selection_history[-10:]  # Last 10 selections
            ]
        }
    
    def update_success_rate(self, agent_name: str, success: bool):
        """Update the success rate for an agent"""
        if agent_name in self.agent_registry:
            current_rate = self.agent_registry[agent_name]["success_rate"]
            usage_count = self.agent_registry[agent_name]["usage_count"]
            
            # Simple moving average
            if success:
                new_rate = (current_rate * (usage_count - 1) + 1.0) / usage_count
            else:
                new_rate = (current_rate * (usage_count - 1) + 0.0) / usage_count
            
            self.agent_registry[agent_name]["success_rate"] = new_rate
            logger.info(f"Updated {agent_name} success rate to {new_rate:.2f}")
