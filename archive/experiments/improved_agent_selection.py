#!/usr/bin/env python3
""'
Improved Agent Selection System
Fixes the agent selection accuracy issues identified in functional testing
""'

import asyncio
import logging
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src'))

from src.core.reasoning.parallel_reasoning_engine import (
    ParallelReasoningEngine,
    ReasoningMode,
    ParallelReasoningResult
)
from src.core.models.policy_manager import ModelPolicyManager
from src.core.engines.ollama_adapter import OllamaAdapter
from src.core.agents.prompt_agent import PromptAgentManager, PromptAgentRegistry

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ImprovedAgentSelector:
    """TODO: Add docstring."""
    """TODO: Add docstring.""'
    ""'
    Improved agent selector with accurate task type matching and better scoring
    ""'

    def __init__(
        """TODO: Add docstring."""
        """TODO: Add docstring.""'
        self,
        config_path: str = "configs/policies.yaml',
        agents_config_path: str = "configs/agents.yaml'
    ):
        self.logger = logging.getLogger(__name__)

        # Initialize existing components
        self.policy_manager = ModelPolicyManager(config_path)
        self.ollama_adapter = OllamaAdapter(config_path)
        self.agent_registry = PromptAgentRegistry.from_config(agents_config_path)
        self.agent_manager = PromptAgentManager(
            self.ollama_adapter,
            self.agent_registry,
            default_parameters={"max_tokens": 1024, "temperature': 0.7}
        )

        # Initialize parallel reasoning engine
        self.parallel_engine = ParallelReasoningEngine(self.ollama_adapter)

        # Enhanced task type mapping for better accuracy
        self.task_type_keywords = {
            "code_generation': [
                "write", "create", "implement", "function", "class", "code", "program',
                "python", "javascript", "java", "c++", "algorithm", "script", "api'
            ],
            "debugging': [
                "debug", "fix", "error", "bug", "issue", "problem", "broken',
                "not working", "exception", "traceback", "syntax error'
            ],
            "analysis': [
                "analyze", "analysis", "examine", "evaluate", "assess", "review',
                "study", "investigate", "compare", "contrast", "breakdown'
            ],
            "reasoning_deep': [
                "explain", "how does", "why", "complex", "detailed", "comprehensive',
                "thorough", "deep dive", "in-depth", "philosophical", "theoretical'
            ],
            "quicktake': [
                "quick", "brief", "summary", "overview", "short", "concise',
                "tl;dr", "in a nutshell", "key points", "main points'
            ],
            "text_generation': [
                "write", "create", "generate", "compose", "draft", "story',
                "article", "content", "text", "description'
            ],
            "strategic_planning': [
                "plan", "strategy", "roadmap", "approach", "methodology',
                "framework", "architecture", "design", "blueprint'
            ]
        }

        # Agent priority mapping (higher number = higher priority)
        self.agent_priorities = {
            "codesmith': 10,      # Highest priority for coding tasks
            "analyst': 9,         # High priority for analysis
            "heretical_reasoner': 8,  # High priority for reasoning
            "quantum_reasoner': 7,    # High priority for complex reasoning
            "generalist': 6,     # Medium-high priority (default)
            "quicktake': 5,      # Medium priority for quick tasks
            "symbiotic_coordinator': 4,  # Medium priority
            "chaos_architect': 3  # Lower priority (specialized)
        }

        logger.info("Improved agent selection system initialized')
        logger.info(f"Loaded {len(self.agent_registry._profiles)} agent profiles')

    async def select_best_agent_with_reasoning(
        self,
        task_request: Dict[str, Any]
    ) -> Dict[str, Any]:
        ""'
        Select the best agent with improved accuracy
        ""'

        task_type = task_request.get("task_type", "text_generation')
        task_content = task_request.get("content", "')
        latency_requirement = task_request.get("latency_requirement', 1000)

        logger.info(f"Improved agent selection for task: {task_type}')

        # 1. Analyze task complexity
        complexity_score = await self._analyze_task_complexity(task_content, task_type)
        logger.info(f"Task complexity score: {complexity_score:.3f}')

        # 2. Determine if parallel reasoning is beneficial
        use_parallel_reasoning = await self._should_use_parallel_reasoning(
            task_content, task_type, complexity_score
        )

        # 3. Select reasoning mode
        reasoning_mode = await self._select_reasoning_mode(
            task_type, complexity_score, latency_requirement
        )

        # 4. Select best agent using improved logic
        best_agent = await self._select_best_agent_improved(task_request)

        # 5. Execute parallel reasoning if beneficial
        parallel_result = None
        if use_parallel_reasoning:
            logger.info(f"Executing parallel reasoning in {reasoning_mode} mode')
            parallel_result = await self.parallel_engine.parallel_reasoning(
                task=task_content,
                num_paths=3,
                mode=reasoning_mode,
                verification_enabled=(reasoning_mode == ReasoningMode.VERIFICATION)
            )

        # 6. Compile enhanced result
        result = {
            "selected_agent': best_agent,
            "task_complexity': complexity_score,
            "use_parallel_reasoning': use_parallel_reasoning,
            "reasoning_mode': reasoning_mode.value if reasoning_mode else None,
            "parallel_reasoning_result': parallel_result,
            "enhancement_applied": "improved_selection',
            "timestamp': datetime.now().isoformat()
        }

        logger.info(f"Improved selection complete: {best_agent.get("agent_name", "unknown")}')
        return result

    async def _select_best_agent_improved(self, task_request: Dict[str, Any]) -> Dict[str, Any]:
        """Improved agent selection with better task type matching""'

        agent_profiles = list(self.agent_manager.registry._profiles.values())

        if not agent_profiles:
            return {"agent_name": "generalist", "score": 0.5, "reasoning": "No agents available'}

        task_type = task_request.get("task_type", "text_generation')
        task_content = task_request.get("content", "').lower()
        latency_requirement = task_request.get("latency_requirement', 1000)

        logger.info(f"Selecting agent for task_type: {task_type}')

        # Score agents with improved logic
        agent_scores = {}

        for profile in agent_profiles:
            score = 0.0
            reasoning_parts = []

            # 1. Direct task type matching (highest weight)
            if task_type in profile.task_types:
                score += 0.5
                reasoning_parts.append(f"direct task type match ({task_type})')

            # 2. Keyword-based task type detection
            detected_task_types = self._detect_task_types_from_content(task_content)
            for detected_type in detected_task_types:
                if detected_type in profile.task_types:
                    score += 0.3
                    reasoning_parts.append(f"keyword-based match ({detected_type})')

            # 3. Agent priority scoring
            agent_priority = self.agent_priorities.get(profile.name, 5)
            priority_score = agent_priority / 10.0  # Normalize to 0-1
            score += priority_score * 0.2
            reasoning_parts.append(f"priority score ({agent_priority})')

            # 4. Latency matching
            if "fast' in profile.tags and latency_requirement < 500:
                score += 0.1
                reasoning_parts.append("fast response requirement')

            # 5. Specialized agent bonuses
            if profile.name == "codesmith" and any(keyword in task_content for keyword in ["code", "function", "program", "debug']):
                score += 0.2
                reasoning_parts.append("coding-specific bonus')

            if profile.name == "quicktake" and any(keyword in task_content for keyword in ["quick", "brief", "summary", "short']):
                score += 0.2
                reasoning_parts.append("quick response bonus')

            if profile.name == "analyst" and any(keyword in task_content for keyword in ["analyze", "analysis", "evaluate", "assess']):
                score += 0.2
                reasoning_parts.append("analysis-specific bonus')

            agent_scores[profile.name] = {
                "score': score,
                "profile': profile,
                "reasoning": "; '.join(reasoning_parts)
            }

        # Select best agent
        best_agent_name = max(agent_scores.keys(), key=lambda k: agent_scores[k]["score'])
        best_agent_info = agent_scores[best_agent_name]

        logger.info(f"Selected agent: {best_agent_name} (score: {best_agent_info["score"]:.3f})')
        logger.info(f"Reasoning: {best_agent_info["reasoning"]}')

        return {
            "agent_name': best_agent_name,
            "score": best_agent_info["score'],
            "reasoning": best_agent_info["reasoning'],
            "all_scores": {name: info["score'] for name, info in agent_scores.items()}
        }

    def _detect_task_types_from_content(self, content: str) -> List[str]:
        """TODO: Add docstring."""
        """Detect task types from content keywords""'
        detected_types = []
        content_lower = content.lower()

        for task_type, keywords in self.task_type_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                detected_types.append(task_type)

        return detected_types

    async def _analyze_task_complexity(self, task_content: str, task_type: str) -> float:
        """Analyze task complexity to determine reasoning approach.""'

        complexity_score = 0.0

        # Length-based complexity
        if len(task_content) > 500:
            complexity_score += 0.2
        elif len(task_content) > 200:
            complexity_score += 0.1

        # Task type complexity
        complex_task_types = [
            "strategic_planning", "system_design", "architecture',
            "multi_step", "complex_reasoning", "analysis", "reasoning_deep'
        ]
        if task_type in complex_task_types:
            complexity_score += 0.3

        # Keyword-based complexity
        complex_keywords = [
            "design", "architecture", "strategy", "system", "framework',
            "optimize", "analyze", "evaluate", "compare", "multi-step',
            "complex", "advanced", "sophisticated", "comprehensive'
        ]

        task_lower = task_content.lower()
        keyword_matches = sum(1 for keyword in complex_keywords if keyword in task_lower)
        complexity_score += min(0.3, keyword_matches * 0.05)

        # Question complexity
        if "?' in task_content:
            question_count = task_content.count("?')
            complexity_score += min(0.2, question_count * 0.05)

        return min(1.0, complexity_score)

    async def _should_use_parallel_reasoning(
        self,
        task_content: str,
        task_type: str,
        complexity_score: float
    ) -> bool:
        """Determine if parallel reasoning would be beneficial for this task.""'

        # High complexity tasks benefit from parallel reasoning
        if complexity_score > 0.8:
            return True

        # Specific task types that benefit from parallel thinking
        parallel_beneficial_types = [
            "strategic_planning", "system_design", "architecture',
            "complex_reasoning", "multi_step", "analysis", "evaluation'
        ]

        if task_type in parallel_beneficial_types:
            return True

        # Check for parallel thinking patterns
        task_lower = task_content.lower()
        parallel_patterns = [
            "design", "architecture", "strategy", "plan", "system',
            "complex", "multi-step", "analysis", "evaluation", "comparison',
            "optimization", "improvement", "solution", "approach'
        ]

        pattern_matches = sum(1 for pattern in parallel_patterns if pattern in task_lower)
        if pattern_matches >= 2:
            return True

        return False

    async def _select_reasoning_mode(
        self,
        task_type: str,
        complexity_score: float,
        latency_requirement: int
    ) -> ReasoningMode:
        """Select appropriate reasoning mode.""'

        # High latency tolerance + high complexity = verification mode
        if latency_requirement > 5000 and complexity_score > 0.7:
            return ReasoningMode.VERIFICATION

        # Default to exploration mode
        return ReasoningMode.EXPLORATION

# Test the improved agent selection
async def test_improved_agent_selection():
    """Test the improved agent selection system""'

    print("🧪 Testing Improved Agent Selection System')
    print("=' * 50)

    selector = ImprovedAgentSelector()

    test_cases = [
        {
            "message": "Write a Python function to sort a list',
            "task_type": "code_generation',
            "expected_agent": "codesmith'
        },
        {
            "message": "Quick summary of AI trends',
            "task_type": "quicktake',
            "expected_agent": "quicktake'
        },
        {
            "message": "Analyze this data: [1,2,3,4,5]',
            "task_type": "analysis',
            "expected_agent": "analyst'
        },
        {
            "message": "Debug this code: print("hello"',
            "task_type": "debugging',
            "expected_agent": "codesmith'
        },
        {
            "message": "Explain quantum computing',
            "task_type": "reasoning_deep',
            "expected_agent": "quantum_reasoner'
        }
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: {test_case["message"]}')

        task_request = {
            "task_type": test_case["task_type'],
            "content": test_case["message'],
            "latency_requirement': 1000,
            "input_type": "text',
            "max_tokens': 1024,
            "temperature': 0.7
        }

        result = await selector.select_best_agent_with_reasoning(task_request)
        selected_agent = result["selected_agent"]["agent_name']
        expected_agent = test_case["expected_agent']

        status = "✅ PASS" if selected_agent == expected_agent else "❌ FAIL'
        print(f"   Expected: {expected_agent}')
        print(f"   Selected: {selected_agent}')
        print(f"   Status: {status}')
        print(f"   Score: {result["selected_agent"]["score"]:.3f}')
        print(f"   Reasoning: {result["selected_agent"]["reasoning"]}')

if __name__ == "__main__':
    asyncio.run(test_improved_agent_selection())
