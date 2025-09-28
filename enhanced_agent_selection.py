#!/usr/bin/env python3
"""
Enhanced Intelligent Agent Selection with Parallel Reasoning
Integrates Parallel-R1 insights with our existing agent selection system
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.reasoning.parallel_reasoning_engine import (
    ParallelReasoningEngine, 
    ReasoningMode, 
    ParallelReasoningResult
)
from src.core.models.policy_manager import ModelPolicyManager
from src.core.engines.ollama_adapter import OllamaAdapter
from src.core.agents.prompt_agent import PromptAgentManager, PromptAgentRegistry

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedAgentSelector:
    """
    Enhanced agent selector that incorporates parallel reasoning capabilities.
    
    Based on Parallel-R1 research insights:
    - Detects tasks that benefit from parallel thinking
    - Implements exploration vs verification modes
    - Uses multi-perspective verification for complex tasks
    """
    
    def __init__(
        self, 
        config_path: str = "configs/policies.yaml", 
        agents_config_path: str = "configs/agents.yaml"
    ):
        self.logger = logging.getLogger(__name__)
        
        # Initialize existing components
        self.policy_manager = ModelPolicyManager(config_path)
        self.ollama_adapter = OllamaAdapter(config_path)
        self.agent_registry = PromptAgentRegistry.from_config(agents_config_path)
        self.agent_manager = PromptAgentManager(
            self.ollama_adapter,
            self.agent_registry,
            default_parameters={"max_tokens": 1024, "temperature": 0.7}
        )
        
        # Initialize parallel reasoning engine
        self.parallel_engine = ParallelReasoningEngine(self.ollama_adapter)
        
        # Task complexity thresholds
        self.complexity_thresholds = {
            "simple": 0.3,
            "moderate": 0.6,
            "complex": 0.8
        }
        
        # Parallel thinking task patterns
        self.parallel_thinking_patterns = [
            "design", "architecture", "strategy", "plan", "system",
            "complex", "multi-step", "analysis", "evaluation", "comparison",
            "optimization", "improvement", "solution", "approach"
        ]
        
        logger.info("Enhanced agent selection system initialized")
        logger.info(f"Loaded {len(self.agent_registry._profiles)} agent profiles")
        logger.info("Parallel reasoning engine ready")
        
        # Add agent_profiles property for monitoring endpoints
        self.agent_profiles = self.agent_registry._profiles
    
    async def select_best_agent_with_reasoning(
        self, 
        task_request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Select the best agent and determine if parallel reasoning should be used.
        
        Args:
            task_request: Task request with type, content, requirements, etc.
            
        Returns:
            Dictionary with selected agent, reasoning mode, and parallel reasoning result
        """
        
        task_type = task_request.get("task_type", "text_generation")
        task_content = task_request.get("content", "")
        latency_requirement = task_request.get("latency_requirement", 1000)
        
        logger.info(f"Enhanced agent selection for task: {task_type}")
        
        # 1. Analyze task complexity
        complexity_score = await self._analyze_task_complexity(task_content, task_type)
        logger.info(f"Task complexity score: {complexity_score:.3f}")
        
        # 2. Determine if parallel reasoning is beneficial
        use_parallel_reasoning, timeout = await self._should_use_parallel_reasoning(
            task_content, task_type, complexity_score
        )
        
        # 3. Select reasoning mode
        reasoning_mode = await self._select_reasoning_mode(
            task_type, complexity_score, latency_requirement
        )
        
        # 4. Select best agent using existing system
        best_agent = await self._select_best_agent(task_request)
        
        # 5. Execute parallel reasoning if beneficial with adaptive timeout
        parallel_result = None
        if use_parallel_reasoning:
            logger.info(f"Executing parallel reasoning in {reasoning_mode} mode")
            try:
                # Use adaptive timeout or default to 30 seconds
                adaptive_timeout = timeout if timeout else 30.0
                parallel_result = await asyncio.wait_for(
                    self.parallel_engine.parallel_reasoning(
                        task=task_content,
                        num_paths=3,
                        mode=reasoning_mode,
                        verification_enabled=(reasoning_mode == ReasoningMode.VERIFICATION)
                    ),
                    timeout=adaptive_timeout
                )
                logger.info(f"Parallel reasoning completed successfully")
            except asyncio.TimeoutError:
                logger.warning(f"Parallel reasoning timed out ({adaptive_timeout}s), falling back to standard selection")
                parallel_result = None
                use_parallel_reasoning = False
            except Exception as e:
                logger.error(f"Parallel reasoning failed: {e}, falling back to standard selection")
                parallel_result = None
                use_parallel_reasoning = False
        
        # 6. Compile enhanced result
        result = {
            "selected_agent": best_agent,
            "task_complexity": complexity_score,
            "use_parallel_reasoning": use_parallel_reasoning,
            "reasoning_mode": reasoning_mode.value if reasoning_mode else None,
            "parallel_reasoning_result": parallel_result,
            "enhancement_applied": "parallel_reasoning" if use_parallel_reasoning else "standard",
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Enhanced selection complete: {result['enhancement_applied']}")
        return result
    
    async def _analyze_task_complexity(self, task_content: str, task_type: str) -> float:
        """Analyze task complexity to determine reasoning approach."""
        
        complexity_score = 0.0
        
        # Length-based complexity
        if len(task_content) > 500:
            complexity_score += 0.2
        elif len(task_content) > 200:
            complexity_score += 0.1
        
        # Task type complexity
        complex_task_types = [
            "strategic_planning", "system_design", "architecture", 
            "multi_step", "complex_reasoning", "analysis"
        ]
        if task_type in complex_task_types:
            complexity_score += 0.3
        
        # Keyword-based complexity
        complex_keywords = [
            "design", "architecture", "strategy", "system", "framework",
            "optimize", "analyze", "evaluate", "compare", "multi-step",
            "complex", "advanced", "sophisticated", "comprehensive"
        ]
        
        task_lower = task_content.lower()
        keyword_matches = sum(1 for keyword in complex_keywords if keyword in task_lower)
        complexity_score += min(0.3, keyword_matches * 0.05)
        
        # Question complexity
        if "?" in task_content:
            question_count = task_content.count("?")
            complexity_score += min(0.2, question_count * 0.05)
        
        return min(1.0, complexity_score)
    
    async def _should_use_parallel_reasoning(
        self, 
        task_content: str, 
        task_type: str, 
        complexity_score: float
    ) -> tuple[bool, Optional[float]]:
        """Determine if parallel reasoning would be beneficial for this task with adaptive timeout."""
        
        # Skip parallel reasoning for simple tasks
        simple_keywords = ["hello", "hi", "quick", "brief", "simple", "yes", "no", "test"]
        if any(keyword in task_content.lower() for keyword in simple_keywords):
            return False, None
        
        # High complexity tasks benefit from parallel reasoning
        if complexity_score > self.complexity_thresholds["complex"]:
            return True, 30.0  # 30 second timeout for complex tasks
        
        # Specific task types that benefit from parallel thinking
        parallel_beneficial_types = [
            "strategic_planning", "system_design", "architecture",
            "complex_reasoning", "multi_step", "analysis", "evaluation"
        ]
        
        if task_type in parallel_beneficial_types:
            # Use shorter timeout for analysis tasks
            if task_type == "analysis":
                return True, 20.0  # 20 second timeout
            return True, 30.0  # 30 second timeout
        
        # Check for parallel thinking patterns
        task_lower = task_content.lower()
        pattern_matches = sum(
            1 for pattern in self.parallel_thinking_patterns 
            if pattern in task_lower
        )
        
        if pattern_matches >= 2:
            return True, 25.0  # 25 second timeout
        
        # Multi-step or comparison tasks
        if any(phrase in task_lower for phrase in [
            "compare", "evaluate", "analyze", "design", "create a system",
            "step by step", "multiple approaches", "different strategies"
        ]):
            return True, 25.0  # 25 second timeout
        
        return False, None
    
    async def _select_reasoning_mode(
        self, 
        task_type: str, 
        complexity_score: float, 
        latency_requirement: int
    ) -> Optional[ReasoningMode]:
        """Select appropriate reasoning mode based on task characteristics."""
        
        # High complexity tasks use verification mode
        if complexity_score > self.complexity_thresholds["complex"]:
            return ReasoningMode.VERIFICATION
        
        # Strategic planning tasks use verification
        if task_type in ["strategic_planning", "system_design", "architecture"]:
            return ReasoningMode.VERIFICATION
        
        # Fast response requirements use exploration
        if latency_requirement < 500:
            return ReasoningMode.EXPLORATION
        
        # Moderate complexity uses hybrid approach
        if complexity_score > self.complexity_thresholds["moderate"]:
            return ReasoningMode.HYBRID
        
        # Default to exploration for most tasks
        return ReasoningMode.EXPLORATION
    
    async def _select_best_agent(self, task_request: Dict[str, Any]) -> Dict[str, Any]:
        """Select best agent using improved intelligent selection system."""
        
        # Use existing agent selection logic directly
        agent_profiles = list(self.agent_manager.registry._profiles.values())
        
        if not agent_profiles:
            return {"agent_name": "default", "score": 0.5, "reasoning": "No agents available"}
        
        task_type = task_request.get("task_type", "text_generation")
        task_content = task_request.get("content", "").lower()
        latency_requirement = task_request.get("latency_requirement", 1000)
        
        logger.info(f"Selecting agent for task_type: {task_type}")
        
        # Enhanced task type keyword mapping with better coverage
        task_keywords = {
            "code_generation": ["write", "create", "implement", "function", "class", "code", "program", "python", "javascript", "java", "c++", "algorithm", "script", "api", "develop", "build", "construct"],
            "debugging": ["debug", "fix", "error", "bug", "issue", "problem", "broken", "not working", "exception", "traceback", "syntax error", "troubleshoot", "resolve"],
            "analysis": ["analyze", "analysis", "examine", "evaluate", "assess", "review", "study", "investigate", "compare", "contrast", "breakdown", "interpret", "understand"],
            "reasoning_deep": ["explain", "how does", "why", "complex", "detailed", "comprehensive", "thorough", "deep dive", "in-depth", "philosophical", "theoretical", "reasoning", "logic", "deduce", "infer"],
            "quicktake": ["quick", "brief", "summary", "overview", "short", "concise", "tl;dr", "in a nutshell", "key points", "main points", "fast", "rapid"],
            "strategic_planning": ["plan", "strategy", "roadmap", "approach", "methodology", "framework", "architecture", "design", "blueprint", "organize", "structure", "coordinate"]
        }
        
        # Agent priority mapping (higher number = higher priority)
        agent_priorities = {
            "codesmith": 10,      # Highest priority for coding tasks
            "analyst": 9,         # High priority for analysis
            "heretical_reasoner": 8,  # High priority for reasoning
            "quantum_reasoner": 7,    # High priority for complex reasoning
            "generalist": 6,     # Medium-high priority (default)
            "quicktake": 5,      # Medium priority for quick tasks
            "symbiotic_coordinator": 4,  # Medium priority
            "chaos_architect": 3  # Lower priority (specialized)
        }
        
        # Score agents with improved logic
        agent_scores = {}
        
        for profile in agent_profiles:
            score = 0.0
            reasoning_parts = []
            
            # 1. Direct task type matching (highest weight)
            if task_type in profile.task_types:
                score += 0.5
                reasoning_parts.append(f"direct task type match ({task_type})")
            
            # 2. Keyword-based task type detection
            detected_task_types = []
            for task_type_name, keywords in task_keywords.items():
                if any(keyword in task_content for keyword in keywords):
                    detected_task_types.append(task_type_name)
            
            for detected_type in detected_task_types:
                if detected_type in profile.task_types:
                    score += 0.3
                    reasoning_parts.append(f"keyword-based match ({detected_type})")
            
            # 3. Agent priority scoring
            agent_priority = agent_priorities.get(profile.name, 5)
            priority_score = agent_priority / 10.0  # Normalize to 0-1
            score += priority_score * 0.2
            reasoning_parts.append(f"priority score ({agent_priority})")
            
            # 4. Latency matching
            if 'fast' in profile.tags and latency_requirement < 500:
                score += 0.1
                reasoning_parts.append("fast response requirement")
            
            # 5. Specialized agent bonuses
            if profile.name == "codesmith" and any(keyword in task_content for keyword in ["code", "function", "program", "debug", "python", "javascript", "java", "algorithm"]):
                score += 0.2
                reasoning_parts.append("coding-specific bonus")
            
            if profile.name == "quicktake" and any(keyword in task_content for keyword in ["quick", "brief", "summary", "short", "fast", "rapid", "overview"]):
                score += 0.2
                reasoning_parts.append("quick response bonus")
            
            if profile.name == "analyst" and any(keyword in task_content for keyword in ["analyze", "analysis", "evaluate", "assess", "examine", "review", "study"]):
                score += 0.2
                reasoning_parts.append("analysis-specific bonus")
            
            if profile.name == "heretical_reasoner" and any(keyword in task_content for keyword in ["reasoning", "logic", "deduce", "infer", "complex", "strategic", "plan"]):
                score += 0.2
                reasoning_parts.append("reasoning-specific bonus")
            
            if profile.name == "quantum_reasoner" and any(keyword in task_content for keyword in ["quantum", "complex", "theoretical", "philosophical", "deep", "comprehensive"]):
                score += 0.2
                reasoning_parts.append("quantum-reasoning bonus")
            
            if profile.name == "chaos_architect" and any(keyword in task_content for keyword in ["chaos", "dynamic", "adaptive", "system", "architecture", "design"]):
                score += 0.2
                reasoning_parts.append("chaos-architecture bonus")
            
            agent_scores[profile.name] = {
                "score": score,
                "profile": profile,
                "reasoning": "; ".join(reasoning_parts)
            }
        
        # Select best agent
        best_agent_name = max(agent_scores.keys(), key=lambda k: agent_scores[k]["score"])
        best_agent_info = agent_scores[best_agent_name]
        
        logger.info(f"Selected agent: {best_agent_name} (score: {best_agent_info['score']:.3f})")
        logger.info(f"Reasoning: {best_agent_info['reasoning']}")
        
        return {
            "agent_name": best_agent_name,
            "score": best_agent_info["score"],
            "reasoning": best_agent_info["reasoning"],
            "all_scores": {name: info["score"] for name, info in agent_scores.items()}
        }

# Example usage and testing
async def test_enhanced_agent_selection():
    """Test the enhanced agent selection with parallel reasoning."""
    
    print("🧠 Testing Enhanced Agent Selection with Parallel Reasoning")
    print("=" * 70)
    
    # Initialize enhanced selector
    selector = EnhancedAgentSelector()
    
    # Test cases with different complexity levels
    test_cases = [
        {
            "name": "Simple Task",
            "task_type": "text_generation",
            "content": "Write a simple hello world program in Python",
            "latency_requirement": 500
        },
        {
            "name": "Moderate Task", 
            "task_type": "code_generation",
            "content": "Create a REST API endpoint for user authentication with JWT tokens",
            "latency_requirement": 1000
        },
        {
            "name": "Complex Task",
            "task_type": "strategic_planning", 
            "content": "Design a comprehensive microservices architecture for an e-commerce platform that can handle 1 million concurrent users, with considerations for scalability, security, data consistency, and fault tolerance",
            "latency_requirement": 2000
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i}: {test_case['name']} ---")
        print(f"Task: {test_case['content'][:100]}...")
        
        try:
            result = await selector.select_best_agent_with_reasoning(test_case)
            
            print(f"✅ Selected Agent: {result['selected_agent']['agent_name']}")
            print(f"📊 Task Complexity: {result['task_complexity']:.3f}")
            print(f"🧠 Parallel Reasoning: {result['use_parallel_reasoning']}")
            print(f"🎯 Reasoning Mode: {result['reasoning_mode']}")
            print(f"⚡ Enhancement: {result['enhancement_applied']}")
            
            if result['parallel_reasoning_result']:
                pr_result = result['parallel_reasoning_result']
                print(f"🔄 Generated {len(pr_result.paths)} reasoning paths")
                print(f"🏆 Best path: {pr_result.best_path.reasoning_type} (confidence: {pr_result.best_path.confidence:.3f})")
                print(f"⏱️ Processing time: {pr_result.total_processing_time:.2f}s")
                
                if pr_result.verification:
                    print(f"✅ Verification completed: {len(pr_result.verification)} paths verified")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
    
    # Show performance stats
    stats = selector.parallel_engine.get_performance_stats()
    print(f"\n📊 Parallel Reasoning Performance:")
    print(f"   Total requests: {stats['total_requests']}")
    print(f"   Success rate: {stats['success_rate']:.1%}")
    print(f"   Average improvement: {stats['average_improvement_score']:.3f}")

if __name__ == "__main__":
    asyncio.run(test_enhanced_agent_selection())
