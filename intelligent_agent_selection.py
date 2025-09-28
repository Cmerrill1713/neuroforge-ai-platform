#!/usr/bin/env python3
"""
Intelligent Agent Selection System with Dynamic Grading
Uses the existing grading/scoring system to select the best agent for each task
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.engines.ollama_adapter import OllamaAdapter
from src.core.agents.prompt_agent import PromptAgentProfile, PromptAgentManager
from src.core.models.policy_manager import ModelPolicyManager, ModelRequest, ModelSelection

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class AgentScore:
    """Agent scoring result"""
    agent_name: str
    agent_profile: PromptAgentProfile
    model_key: str
    score: float
    reasoning: str
    confidence: float
    estimated_latency: float
    estimated_memory: float
    task_match_score: float
    model_performance_score: float
    priority_score: float

@dataclass
class TaskRequest:
    """Task request with context"""
    prompt: str
    task_type: str
    input_type: str = "text"
    latency_requirement: int = 1000
    tags: Optional[List[str]] = None
    context: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

class IntelligentAgentSelector:
    """
    Intelligent agent selection using the existing grading/scoring system.
    
    This system:
    1. Loads agent profiles from configs/agents.yaml
    2. Uses ModelPolicyManager for model routing
    3. Scores agents based on task matching, model performance, and priority
    4. Selects the best agent for each specific task
    """
    
    def __init__(self, config_path: str = "configs/policies.yaml", agents_config_path: str = "configs/agents.yaml"):
        self.config_path = config_path
        self.agents_config_path = agents_config_path
        self.ollama_adapter = OllamaAdapter(config_path)
        self.policy_manager = ModelPolicyManager(config_path)
        self.agent_manager = None
        self.logger = logging.getLogger(__name__)
        
        # Performance tracking
        self.selection_history: List[Tuple[TaskRequest, AgentScore]] = []
        self.performance_stats: Dict[str, Dict[str, float]] = {}
    
    async def initialize(self) -> bool:
        """Initialize the intelligent agent selection system"""
        try:
            # Initialize Ollama adapter
            if not await self.ollama_adapter.check_ollama_status():
                logger.error("Ollama is not running - required for agent selection")
                return False
            
            # Initialize agent manager
            from src.core.agents.prompt_agent import PromptAgentRegistry
            registry = PromptAgentRegistry.from_config(self.agents_config_path)
            self.agent_manager = PromptAgentManager(
                self.ollama_adapter,
                registry,
                default_parameters={"max_tokens": 1024, "temperature": 0.7}
            )
            
            logger.info("Intelligent agent selection system initialized successfully")
            logger.info(f"Loaded {len(registry._profiles)} agent profiles")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize agent selection system: {e}")
            return False
    
    async def select_best_agent(self, task_request: TaskRequest) -> AgentScore:
        """Select the best agent for the given task using intelligent scoring"""
        
        logger.info(f"Selecting best agent for task: {task_request.task_type}")
        
        # Get all available agent profiles
        agent_profiles = list(self.agent_manager.registry._profiles.values())
        
        # Score each agent
        agent_scores = []
        for profile in agent_profiles:
            score = await self._score_agent(profile, task_request)
            agent_scores.append(score)
        
        # Sort by score (highest first)
        agent_scores.sort(key=lambda x: x.score, reverse=True)
        
        # Select the best agent
        best_agent = agent_scores[0]
        
        logger.info(f"Selected agent: {best_agent.agent_name} (score: {best_agent.score:.3f})")
        logger.info(f"Reasoning: {best_agent.reasoning}")
        
        # Track selection
        self.selection_history.append((task_request, best_agent))
        
        return best_agent
    
    async def _score_agent(self, profile: PromptAgentProfile, task_request: TaskRequest) -> AgentScore:
        """Score an agent profile for a specific task"""
        
        # 1. Task matching score (0-1)
        task_match_score = self._calculate_task_match_score(profile, task_request)
        
        # 2. Model performance score (0-1)
        model_performance_score = await self._calculate_model_performance_score(profile, task_request)
        
        # 3. Priority score (0-1, lower priority number = higher score)
        priority_score = self._calculate_priority_score(profile)
        
        # 4. Tag matching bonus (0-0.2)
        tag_bonus = self._calculate_tag_bonus(profile, task_request)
        
        # 5. Latency requirement matching (0-0.3)
        latency_score = self._calculate_latency_score(profile, task_request)
        
        # Calculate weighted total score
        total_score = (
            task_match_score * 0.4 +           # 40% - Task type matching
            model_performance_score * 0.3 +    # 30% - Model performance
            priority_score * 0.2 +            # 20% - Agent priority
            tag_bonus * 0.05 +                # 5% - Tag matching
            latency_score * 0.05              # 5% - Latency matching
        )
        
        # Determine best model for this agent
        model_key = self._select_model_for_agent(profile, task_request)
        
        # Get model performance estimates
        estimated_latency, estimated_memory = await self._get_model_estimates(model_key)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(profile, task_request, {
            'task_match': task_match_score,
            'model_performance': model_performance_score,
            'priority': priority_score,
            'tag_bonus': tag_bonus,
            'latency_score': latency_score
        })
        
        # Calculate confidence
        confidence = min(total_score * 1.2, 1.0)  # Cap at 1.0
        
        return AgentScore(
            agent_name=profile.name,
            agent_profile=profile,
            model_key=model_key,
            score=total_score,
            reasoning=reasoning,
            confidence=confidence,
            estimated_latency=estimated_latency,
            estimated_memory=estimated_memory,
            task_match_score=task_match_score,
            model_performance_score=model_performance_score,
            priority_score=priority_score
        )
    
    def _calculate_task_match_score(self, profile: PromptAgentProfile, task_request: TaskRequest) -> float:
        """Calculate how well the agent matches the task type"""
        
        if not profile.task_types:
            return 0.5  # Neutral score if no task types specified
        
        task_type_lower = task_request.task_type.lower()
        matching_types = [t.lower() for t in profile.task_types if t.lower() == task_type_lower]
        
        if matching_types:
            return 1.0  # Perfect match
        else:
            # Check for partial matches (e.g., "code" matches "code_generation")
            partial_matches = [t for t in profile.task_types if task_type_lower in t.lower() or t.lower() in task_type_lower]
            if partial_matches:
                return 0.7  # Good partial match
            else:
                return 0.2  # Poor match
    
    async def _calculate_model_performance_score(self, profile: PromptAgentProfile, task_request: TaskRequest) -> float:
        """Calculate model performance score based on agent's model preferences"""
        
        if not profile.model_preferences:
            return 0.5  # Neutral score if no preferences
        
        # Get the preferred model for this task
        preferred_model = profile.model_preferences[0]  # First preference
        
        # Check if model is available
        if preferred_model not in self.ollama_adapter.models:
            return 0.3  # Lower score if preferred model not available
        
        # Get model performance data
        model = self.ollama_adapter.models[preferred_model]
        
        # Score based on latency vs requirement
        model_latency = model.performance.get('latency_ms', 1000)
        required_latency = task_request.latency_requirement
        
        if model_latency <= required_latency:
            latency_score = 1.0
        else:
            latency_score = max(0.1, required_latency / model_latency)
        
        # Score based on capabilities
        capabilities = model.capabilities
        task_capabilities = self._get_required_capabilities(task_request.task_type)
        
        capability_score = 0.5
        if task_capabilities:
            matching_capabilities = [c for c in task_capabilities if c in capabilities]
            capability_score = len(matching_capabilities) / len(task_capabilities)
        
        return (latency_score * 0.6 + capability_score * 0.4)
    
    def _calculate_priority_score(self, profile: PromptAgentProfile) -> float:
        """Calculate priority score (lower priority number = higher score)"""
        
        # Convert priority to score (lower priority = higher score)
        max_priority = 100
        if profile.priority <= 0:
            return 1.0
        else:
            return max(0.1, (max_priority - profile.priority) / max_priority)
    
    def _calculate_tag_bonus(self, profile: PromptAgentProfile, task_request: TaskRequest) -> float:
        """Calculate tag matching bonus"""
        
        if not task_request.tags or not profile.tags:
            return 0.0
        
        matching_tags = [tag for tag in task_request.tags if tag in profile.tags]
        if matching_tags:
            return min(0.2, len(matching_tags) * 0.1)
        else:
            return 0.0
    
    def _calculate_latency_score(self, profile: PromptAgentProfile, task_request: TaskRequest) -> float:
        """Calculate latency requirement matching score"""
        
        # Check if agent is optimized for fast responses
        if 'fast' in profile.tags and task_request.latency_requirement < 500:
            return 0.3
        elif 'quick' in profile.tags and task_request.latency_requirement < 1000:
            return 0.2
        else:
            return 0.1
    
    def _select_model_for_agent(self, profile: PromptAgentProfile, task_request: TaskRequest) -> str:
        """Select the best model for this agent and task"""
        
        if not profile.model_preferences:
            # Use intelligent routing
            return self.ollama_adapter._select_model(
                task_request.input_type,
                task_request.task_type,
                task_request.latency_requirement
            )
        
        # Try agent's preferred models in order
        for model_key in profile.model_preferences:
            if model_key in self.ollama_adapter.models:
                return model_key
        
        # Fallback to intelligent routing
        return self.ollama_adapter._select_model(
            task_request.input_type,
            task_request.task_type,
            task_request.latency_requirement
        )
    
    async def _get_model_estimates(self, model_key: str) -> Tuple[float, float]:
        """Get performance estimates for a model"""
        
        if model_key in self.ollama_adapter.models:
            model = self.ollama_adapter.models[model_key]
            latency = model.performance.get('latency_ms', 1000) / 1000.0  # Convert to seconds
            memory = model.performance.get('memory_gb', 4.0)
            return latency, memory
        else:
            return 1.0, 4.0  # Default estimates
    
    def _get_required_capabilities(self, task_type: str) -> List[str]:
        """Get required capabilities for a task type"""
        
        capability_map = {
            'code_generation': ['code_generation', 'instruction_following'],
            'code_analysis': ['code_generation', 'analysis'],
            'debugging': ['code_generation', 'analysis'],
            'refactoring': ['code_generation', 'analysis'],
            'text_generation': ['text_generation', 'instruction_following'],
            'analysis': ['analysis', 'reasoning'],
            'reasoning': ['reasoning', 'mathematical_reasoning'],
            'instruction_following': ['instruction_following'],
            'vision_to_text': ['vision_to_text', 'multimodal_reasoning'],
            'image_analysis': ['vision_to_text', 'multimodal_reasoning']
        }
        
        return capability_map.get(task_type, ['text_generation'])
    
    def _generate_reasoning(self, profile: PromptAgentProfile, task_request: TaskRequest, scores: Dict[str, float]) -> str:
        """Generate human-readable reasoning for the selection"""
        
        reasoning_parts = []
        
        if scores['task_match'] >= 0.8:
            reasoning_parts.append(f"Excellent task match ({scores['task_match']:.1%})")
        elif scores['task_match'] >= 0.5:
            reasoning_parts.append(f"Good task match ({scores['task_match']:.1%})")
        else:
            reasoning_parts.append(f"Weak task match ({scores['task_match']:.1%})")
        
        if scores['model_performance'] >= 0.8:
            reasoning_parts.append(f"high-performing model ({scores['model_performance']:.1%})")
        elif scores['model_performance'] >= 0.5:
            reasoning_parts.append(f"adequate model performance ({scores['model_performance']:.1%})")
        
        if scores['priority'] >= 0.8:
            reasoning_parts.append("high priority agent")
        elif scores['priority'] >= 0.5:
            reasoning_parts.append("medium priority agent")
        
        if scores['tag_bonus'] > 0:
            reasoning_parts.append("tag-matched")
        
        if scores['latency_score'] >= 0.2:
            reasoning_parts.append("latency-optimized")
        
        return f"{profile.name} selected due to: {', '.join(reasoning_parts)}"
    
    async def execute_task(self, task_request: TaskRequest) -> Dict[str, Any]:
        """Execute a task using the best selected agent"""
        
        # Select best agent
        best_agent = await self.select_best_agent(task_request)
        
        # Execute using the agent
        try:
            response = await self.ollama_adapter.generate_response(
                model_key=best_agent.model_key,
                prompt=task_request.prompt,
                max_tokens=best_agent.agent_profile.default_parameters.get('max_tokens', 1024),
                temperature=best_agent.agent_profile.default_parameters.get('temperature', 0.7)
            )
            
            return {
                "success": True,
                "agent_used": best_agent.agent_name,
                "model_used": best_agent.model_key,
                "response": response.content,
                "agent_score": best_agent.score,
                "reasoning": best_agent.reasoning,
                "confidence": best_agent.confidence,
                "processing_time": response.processing_time,
                "tokens_generated": response.tokens_generated
            }
            
        except Exception as e:
            logger.error(f"Task execution failed: {e}")
            return {
                "success": False,
                "agent_used": best_agent.agent_name,
                "model_used": best_agent.model_key,
                "error": str(e),
                "agent_score": best_agent.score,
                "reasoning": best_agent.reasoning
            }
    
    def get_selection_stats(self) -> Dict[str, Any]:
        """Get statistics about agent selections"""
        
        if not self.selection_history:
            return {"total_selections": 0}
        
        # Count agent usage
        agent_usage = {}
        task_type_usage = {}
        
        for task_request, agent_score in self.selection_history:
            agent_name = agent_score.agent_name
            task_type = task_request.task_type
            
            agent_usage[agent_name] = agent_usage.get(agent_name, 0) + 1
            task_type_usage[task_type] = task_type_usage.get(task_type, 0) + 1
        
        # Calculate average scores
        avg_scores = {}
        for agent_name in agent_usage.keys():
            scores = [score.score for _, score in self.selection_history if score.agent_name == agent_name]
            avg_scores[agent_name] = sum(scores) / len(scores) if scores else 0.0
        
        return {
            "total_selections": len(self.selection_history),
            "agent_usage": agent_usage,
            "task_type_usage": task_type_usage,
            "average_scores": avg_scores,
            "most_used_agent": max(agent_usage.items(), key=lambda x: x[1])[0] if agent_usage else None
        }

async def main():
    """Test the intelligent agent selection system"""
    
    logger.info("🧠 Testing Intelligent Agent Selection System")
    logger.info("=" * 60)
    
    selector = IntelligentAgentSelector()
    
    if not await selector.initialize():
        logger.error("❌ Failed to initialize agent selection system")
        return
    
    # Test different task types
    test_tasks = [
        TaskRequest(
            prompt="Write a Python function to calculate fibonacci numbers",
            task_type="code_generation",
            tags=["code", "python"]
        ),
        TaskRequest(
            prompt="Analyze the pros and cons of using local LLMs vs cloud-based LLMs",
            task_type="analysis",
            tags=["analysis", "comparison"]
        ),
        TaskRequest(
            prompt="What is 15 + 27?",
            task_type="simple_reasoning",
            latency_requirement=500,
            tags=["fast", "quick"]
        ),
        TaskRequest(
            prompt="Explain the concept of machine learning in detail",
            task_type="text_generation",
            tags=["explanation", "educational"]
        )
    ]
    
    logger.info(f"Testing {len(test_tasks)} different task types...")
    
    for i, task in enumerate(test_tasks, 1):
        logger.info(f"\n📝 Test {i}: {task.task_type}")
        logger.info(f"   Prompt: {task.prompt[:50]}...")
        
        result = await selector.execute_task(task)
        
        if result["success"]:
            logger.info(f"   ✅ Agent: {result['agent_used']}")
            logger.info(f"   🤖 Model: {result['model_used']}")
            logger.info(f"   📊 Score: {result['agent_score']:.3f}")
            logger.info(f"   💭 Reasoning: {result['reasoning']}")
            logger.info(f"   ⏱️  Time: {result['processing_time']:.3f}s")
        else:
            logger.error(f"   ❌ Failed: {result['error']}")
    
    # Show selection statistics
    logger.info(f"\n📊 Selection Statistics:")
    stats = selector.get_selection_stats()
    for key, value in stats.items():
        logger.info(f"   {key}: {value}")
    
    logger.info(f"\n🎉 Intelligent agent selection testing complete!")

if __name__ == "__main__":
    asyncio.run(main())
