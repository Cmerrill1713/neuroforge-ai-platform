#!/usr/bin/env python3
"""
Intelligent Model Router for NeuroForge
Uses grading system performance data to intelligently route tasks to optimal models
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class TaskType(str, Enum):
    """Task types for intelligent routing"""
    SIMPLE_CHAT = "simple_chat"
    COMPLEX_REASONING = "complex_reasoning"
    CODE_GENERATION = "code_generation"
    CODE_ANALYSIS = "code_analysis"
    VISION_ANALYSIS = "vision_analysis"
    MULTIMODAL = "multimodal"
    FAST_RESPONSE = "fast_response"
    CREATIVE_WRITING = "creative_writing"
    ANALYSIS = "analysis"
    TRANSLATION = "translation"
    SUMMARIZATION = "summarization"

class ModelCapability(str, Enum):
    """Model capabilities for routing decisions"""
    SPEED = "speed"
    ACCURACY = "accuracy"
    MEMORY_EFFICIENCY = "memory_efficiency"
    MULTIMODAL = "multimodal"
    CODING = "coding"
    REASONING = "reasoning"
    CREATIVITY = "creativity"
    VISION_ONLY = "vision_only"  # For models that only work with images/video

@dataclass
class ModelPerformanceProfile:
    """Performance profile for a model based on grading data"""
    model_name: str
    task_type: TaskType
    avg_accuracy: float
    avg_response_time: float
    avg_grade: str
    success_rate: float
    memory_usage: float
    last_updated: datetime
    sample_count: int

@dataclass
class TaskRequirements:
    """Requirements for a specific task"""
    task_type: TaskType
    max_response_time: float = 5.0  # seconds
    min_accuracy: float = 0.7
    max_memory_usage: float = 8.0  # GB
    requires_multimodal: bool = False
    requires_coding: bool = False
    requires_creativity: bool = False
    priority: int = 5  # 1-10, higher = more important

class IntelligentModelRouter:
    """
    Intelligent model router that uses grading system data to select optimal models
    """
    
    def __init__(self, adaptive_system=None, model_manager=None):
        self.adaptive_system = adaptive_system
        self.model_manager = model_manager
        self.performance_profiles: Dict[str, Dict[TaskType, ModelPerformanceProfile]] = {}
        self.routing_history: List[Dict[str, Any]] = []
        
        # Model capability mappings - Updated with all available models
        self.model_capabilities = {
            # TEXT MODELS (Ollama)
            "qwen2.5:72b": {
                ModelCapability.SPEED: 0.3,  # Slow but powerful
                ModelCapability.ACCURACY: 0.95,
                ModelCapability.MEMORY_EFFICIENCY: 0.2,  # High memory usage
                ModelCapability.REASONING: 0.95,
                ModelCapability.CREATIVITY: 0.9,
                ModelCapability.CODING: 0.85
            },
            "qwen2.5:14b": {
                ModelCapability.SPEED: 0.6,
                ModelCapability.ACCURACY: 0.9,
                ModelCapability.MEMORY_EFFICIENCY: 0.5,
                ModelCapability.REASONING: 0.85,
                ModelCapability.CREATIVITY: 0.8,
                ModelCapability.CODING: 0.8
            },
            "qwen2.5:7b": {
                ModelCapability.SPEED: 0.8,
                ModelCapability.ACCURACY: 0.85,
                ModelCapability.MEMORY_EFFICIENCY: 0.7,
                ModelCapability.REASONING: 0.75,
                ModelCapability.CREATIVITY: 0.8,
                ModelCapability.CODING: 0.8
            },
            "mistral:7b": {
                ModelCapability.SPEED: 0.8,
                ModelCapability.ACCURACY: 0.8,
                ModelCapability.MEMORY_EFFICIENCY: 0.7,
                ModelCapability.REASONING: 0.7,
                ModelCapability.CREATIVITY: 0.75,
                ModelCapability.CODING: 0.9  # Specialized for coding
            },
            "llama3.2:3b": {
                ModelCapability.SPEED: 0.95,  # Fastest
                ModelCapability.ACCURACY: 0.7,
                ModelCapability.MEMORY_EFFICIENCY: 0.9,
                ModelCapability.REASONING: 0.6,
                ModelCapability.CREATIVITY: 0.7,
                ModelCapability.CODING: 0.6
            },
            # VISION MODELS
            "apple-FastVLM-7B": {
                ModelCapability.SPEED: 0.6,
                ModelCapability.ACCURACY: 0.95,
                ModelCapability.MEMORY_EFFICIENCY: 0.4,
                ModelCapability.MULTIMODAL: 0.95,
                ModelCapability.VISION_ONLY: 1.0,  # VISION-ONLY - NEVER for text
                ModelCapability.REASONING: 0.8
            },
            "llava:7b": {
                ModelCapability.SPEED: 0.7,
                ModelCapability.ACCURACY: 0.8,
                ModelCapability.MEMORY_EFFICIENCY: 0.6,
                ModelCapability.MULTIMODAL: 0.9,
                ModelCapability.REASONING: 0.7,
                ModelCapability.CREATIVITY: 0.75
            },
            # HRM MODELS
            "hrm-official": {
                ModelCapability.SPEED: 0.6,
                ModelCapability.ACCURACY: 0.95,
                ModelCapability.MEMORY_EFFICIENCY: 0.8,
                ModelCapability.REASONING: 0.98,  # Excellent for hierarchical reasoning
                ModelCapability.CREATIVITY: 0.9,
                ModelCapability.CODING: 0.7
            }
        }
        
        # Task type to capability mapping
        self.task_capability_requirements = {
            TaskType.SIMPLE_CHAT: [ModelCapability.SPEED, ModelCapability.ACCURACY],
            TaskType.COMPLEX_REASONING: [ModelCapability.REASONING, ModelCapability.ACCURACY, ModelCapability.CREATIVITY],
            TaskType.CODE_GENERATION: [ModelCapability.CODING, ModelCapability.ACCURACY],
            TaskType.CODE_ANALYSIS: [ModelCapability.CODING, ModelCapability.REASONING],
            TaskType.VISION_ANALYSIS: [ModelCapability.MULTIMODAL, ModelCapability.ACCURACY],
            TaskType.MULTIMODAL: [ModelCapability.MULTIMODAL, ModelCapability.ACCURACY],
            TaskType.FAST_RESPONSE: [ModelCapability.SPEED, ModelCapability.MEMORY_EFFICIENCY],
            TaskType.CREATIVE_WRITING: [ModelCapability.CREATIVITY, ModelCapability.ACCURACY],
            TaskType.ANALYSIS: [ModelCapability.REASONING, ModelCapability.ACCURACY],
            TaskType.TRANSLATION: [ModelCapability.ACCURACY, ModelCapability.SPEED],
            TaskType.SUMMARIZATION: [ModelCapability.ACCURACY, ModelCapability.SPEED]
        }

    def update_performance_profile(self, model_name: str, task_type: TaskType, 
                                 accuracy: float, response_time: float, 
                                 grade: str, memory_usage: float = 0.0):
        """Update performance profile based on grading system data"""
        if model_name not in self.performance_profiles:
            self.performance_profiles[model_name] = {}
        
        if task_type not in self.performance_profiles[model_name]:
            self.performance_profiles[model_name][task_type] = ModelPerformanceProfile(
                model_name=model_name,
                task_type=task_type,
                avg_accuracy=accuracy,
                avg_response_time=response_time,
                avg_grade=grade,
                success_rate=1.0 if accuracy > 0.7 else 0.0,
                memory_usage=memory_usage,
                last_updated=datetime.now(),
                sample_count=1
            )
        else:
            # Update existing profile with weighted average
            profile = self.performance_profiles[model_name][task_type]
            weight = 0.1  # Learning rate
            
            profile.avg_accuracy = (1 - weight) * profile.avg_accuracy + weight * accuracy
            profile.avg_response_time = (1 - weight) * profile.avg_response_time + weight * response_time
            profile.success_rate = (1 - weight) * profile.success_rate + weight * (1.0 if accuracy > 0.7 else 0.0)
            profile.memory_usage = (1 - weight) * profile.memory_usage + weight * memory_usage
            profile.last_updated = datetime.now()
            profile.sample_count += 1
            
            # Update grade based on accuracy
            if accuracy >= 0.9:
                profile.avg_grade = "A+"
            elif accuracy >= 0.8:
                profile.avg_grade = "A"
            elif accuracy >= 0.7:
                profile.avg_grade = "B"
            elif accuracy >= 0.6:
                profile.avg_grade = "C"
            else:
                profile.avg_grade = "D"

    def select_optimal_model(self, task_requirements: TaskRequirements, 
                           available_models: List[str]) -> Tuple[str, Dict[str, Any]]:
        """
        Select optimal model based on task requirements and performance history
        
        Returns:
            Tuple of (selected_model_name, selection_reasoning)
        """
        if not available_models:
            return "default-chat", {"reason": "No models available", "fallback": True}
        
        # Score each model for this task
        model_scores = {}
        reasoning = {}
        
        for model_name in available_models:
            score = 0.0
            score_breakdown = {}
            
            # 1. Performance history score (40% weight)
            perf_score = self._calculate_performance_score(model_name, task_requirements.task_type)
            score += perf_score * 0.4
            score_breakdown["performance"] = perf_score
            
            # 2. Capability match score (30% weight)
            cap_score = self._calculate_capability_score(model_name, task_requirements)
            score += cap_score * 0.3
            score_breakdown["capabilities"] = cap_score
            
            # 3. Resource efficiency score (20% weight)
            resource_score = self._calculate_resource_score(model_name, task_requirements)
            score += resource_score * 0.2
            score_breakdown["resources"] = resource_score
            
            # 4. Recent performance bonus (10% weight)
            recent_bonus = self._calculate_recent_performance_bonus(model_name, task_requirements.task_type)
            score += recent_bonus * 0.1
            score_breakdown["recent_performance"] = recent_bonus
            
            model_scores[model_name] = score
            reasoning[model_name] = {
                "score": score,
                "breakdown": score_breakdown,
                "final_score": score
            }
        
        # Select best model
        best_model = max(model_scores.keys(), key=lambda k: model_scores[k])
        
        # Log selection
        logger.info(f"Selected model: {best_model} (score: {model_scores[best_model]:.3f})")
        logger.info(f"Selection reasoning: {reasoning[best_model]}")
        
        # Record routing decision
        self.routing_history.append({
            "timestamp": datetime.now(),
            "task_type": task_requirements.task_type,
            "selected_model": best_model,
            "all_scores": model_scores,
            "reasoning": reasoning[best_model]
        })
        
        return best_model, reasoning[best_model]

    def _calculate_performance_score(self, model_name: str, task_type: TaskType) -> float:
        """Calculate performance score based on historical data"""
        if model_name not in self.performance_profiles:
            return 0.5  # Default score for unknown models
        
        if task_type not in self.performance_profiles[model_name]:
            return 0.5  # Default score for unknown task types
        
        profile = self.performance_profiles[model_name][task_type]
        
        # Convert grade to numeric score
        grade_scores = {"A+": 1.0, "A": 0.9, "B": 0.8, "C": 0.6, "D": 0.4, "F": 0.2}
        grade_score = grade_scores.get(profile.avg_grade, 0.5)
        
        # Weight by sample count (more samples = more reliable)
        reliability_weight = min(profile.sample_count / 10.0, 1.0)
        
        return grade_score * reliability_weight

    def _calculate_capability_score(self, model_name: str, task_requirements: TaskRequirements) -> float:
        """Calculate how well model capabilities match task requirements"""
        if model_name not in self.model_capabilities:
            return 0.5
        
        model_caps = self.model_capabilities[model_name]
        required_caps = self.task_capability_requirements.get(task_requirements.task_type, [])
        
        if not required_caps:
            return 0.5
        
        # Exclude vision-only models from text-only tasks
        if (model_caps.get(ModelCapability.VISION_ONLY, 0) > 0.5 and 
            task_requirements.task_type not in [TaskType.VISION_ANALYSIS, TaskType.MULTIMODAL]):
            return 0.0  # Vision-only models can't handle text-only tasks
        
        # Calculate average capability score for required capabilities
        capability_scores = []
        for cap in required_caps:
            if cap in model_caps:
                capability_scores.append(model_caps[cap])
            else:
                capability_scores.append(0.0)  # Missing capability
        
        return sum(capability_scores) / len(capability_scores) if capability_scores else 0.5

    def _calculate_resource_score(self, model_name: str, task_requirements: TaskRequirements) -> float:
        """Calculate resource efficiency score"""
        if model_name not in self.model_capabilities:
            return 0.5
        
        model_caps = self.model_capabilities[model_name]
        
        # Speed score (higher is better)
        speed_score = model_caps.get(ModelCapability.SPEED, 0.5)
        
        # Memory efficiency score (higher is better)
        memory_score = model_caps.get(ModelCapability.MEMORY_EFFICIENCY, 0.5)
        
        # Check if model meets resource requirements
        meets_speed_req = speed_score >= (1.0 - task_requirements.max_response_time / 10.0)
        meets_memory_req = memory_score >= (1.0 - task_requirements.max_memory_usage / 16.0)
        
        base_score = (speed_score + memory_score) / 2
        
        # Apply requirement penalties
        if not meets_speed_req:
            base_score *= 0.7
        if not meets_memory_req:
            base_score *= 0.8
        
        return base_score

    def _calculate_recent_performance_bonus(self, model_name: str, task_type: TaskType) -> float:
        """Calculate bonus for recent good performance"""
        if model_name not in self.performance_profiles:
            return 0.0
        
        if task_type not in self.performance_profiles[model_name]:
            return 0.0
        
        profile = self.performance_profiles[model_name][task_type]
        
        # Check if performance data is recent (within last hour)
        time_diff = datetime.now() - profile.last_updated
        if time_diff > timedelta(hours=1):
            return 0.0
        
        # Bonus based on recent accuracy
        if profile.avg_accuracy >= 0.9:
            return 0.2
        elif profile.avg_accuracy >= 0.8:
            return 0.1
        else:
            return 0.0

    def get_routing_recommendations(self, task_requirements: TaskRequirements) -> Dict[str, Any]:
        """Get routing recommendations for a task"""
        available_models = list(self.model_capabilities.keys())
        
        # Get top 3 recommendations
        model_scores = {}
        for model_name in available_models:
            perf_score = self._calculate_performance_score(model_name, task_requirements.task_type)
            cap_score = self._calculate_capability_score(model_name, task_requirements)
            resource_score = self._calculate_resource_score(model_name, task_requirements)
            recent_bonus = self._calculate_recent_performance_bonus(model_name, task_requirements.task_type)
            
            total_score = (perf_score * 0.4 + cap_score * 0.3 + resource_score * 0.2 + recent_bonus * 0.1)
            model_scores[model_name] = total_score
        
        # Sort by score
        sorted_models = sorted(model_scores.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "task_type": task_requirements.task_type,
            "recommendations": [
                {
                    "model": model,
                    "score": score,
                    "reasoning": f"Performance: {self._calculate_performance_score(model, task_requirements.task_type):.2f}, "
                               f"Capabilities: {self._calculate_capability_score(model, task_requirements):.2f}, "
                               f"Resources: {self._calculate_resource_score(model, task_requirements):.2f}"
                }
                for model, score in sorted_models[:3]
            ],
            "routing_history_count": len(self.routing_history)
        }

    def detect_task_type(self, message: str, context: Dict[str, Any] = None) -> TaskType:
        """Detect task type from message content"""
        message_lower = message.lower()
        
        # Vision/multimodal detection
        if any(keyword in message_lower for keyword in ["image", "picture", "photo", "visual", "see", "look at"]):
            return TaskType.VISION_ANALYSIS
        
        # Coding detection
        if any(keyword in message_lower for keyword in ["code", "function", "program", "debug", "algorithm", "script", "python", "javascript"]):
            return TaskType.CODE_GENERATION
        
        # Analysis detection
        if any(keyword in message_lower for keyword in ["analyze", "analysis", "evaluate", "assess", "compare", "review"]):
            return TaskType.ANALYSIS
        
        # Creative writing detection
        if any(keyword in message_lower for keyword in ["write", "story", "creative", "poem", "essay", "narrative"]):
            return TaskType.CREATIVE_WRITING
        
        # Fast response detection
        if any(keyword in message_lower for keyword in ["quick", "fast", "brief", "summary", "tl;dr"]):
            return TaskType.FAST_RESPONSE
        
        # Complex reasoning detection
        if any(keyword in message_lower for keyword in ["explain", "how does", "why", "complex", "detailed", "comprehensive"]):
            return TaskType.COMPLEX_REASONING
        
        # Default to simple chat
        return TaskType.SIMPLE_CHAT

# Global instance
_intelligent_router: Optional[IntelligentModelRouter] = None

def get_intelligent_router() -> IntelligentModelRouter:
    """Get the global intelligent router instance"""
    global _intelligent_router
    if _intelligent_router is None:
        _intelligent_router = IntelligentModelRouter()
    return _intelligent_router
