"""
Agent Planner for Agentic LLM Core v0.1

This module provides an intelligent agent planner that takes specifications, features,
and user intent to generate optimized TaskGraphs with budget and latency policies.

Created: 2024-09-24
Status: Draft
"""

from __future__ import annotations

import logging
import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel, Field, field_validator

from ..models.contracts import Task, TaskGraph, ToolSpec


# ============================================================================
# Planning Input Models
# ============================================================================

class PlanningInput(BaseModel):
    """Input for the agent planner."""
    specifications: Dict[str, Any] = Field(..., description="System specifications and requirements")
    features: List[str] = Field(..., description="Available features and capabilities")
    user_intent: str = Field(..., description="User's intent and goals")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context information")
    constraints: Optional[Dict[str, Any]] = Field(None, description="Planning constraints")
    
    @field_validator('features')
    @classmethod
    def validate_features(cls, v):
        if not v:
            raise ValueError("Features list cannot be empty")
        return v
    
    @field_validator('user_intent')
    @classmethod
    def validate_user_intent(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError("User intent cannot be empty")
        return v.strip()


class PlanningPolicy(BaseModel):
    """Planning policy configuration."""
    budget_limit: Optional[float] = Field(None, ge=0, description="Maximum budget in currency units")
    latency_limit: Optional[float] = Field(None, ge=0, description="Maximum latency in seconds")
    priority: str = Field(default="balanced", description="Planning priority: speed, quality, balanced")
    optimization_target: str = Field(default="efficiency", description="Optimization target: cost, speed, quality, efficiency")
    parallel_execution: bool = Field(default=True, description="Allow parallel task execution")
    resource_constraints: Dict[str, Any] = Field(default_factory=dict, description="Resource constraints")
    
    @field_validator('priority')
    @classmethod
    def validate_priority(cls, v):
        allowed_priorities = ['speed', 'quality', 'balanced']
        if v not in allowed_priorities:
            raise ValueError(f"Priority must be one of: {allowed_priorities}")
        return v
    
    @field_validator('optimization_target')
    @classmethod
    def validate_optimization_target(cls, v):
        allowed_targets = ['cost', 'speed', 'quality', 'efficiency']
        if v not in allowed_targets:
            raise ValueError(f"Optimization target must be one of: {allowed_targets}")
        return v


class PlanningContext(BaseModel):
    """Context for planning decisions."""
    available_tools: List[ToolSpec] = Field(default_factory=list, description="Available tools")
    system_capabilities: Dict[str, Any] = Field(default_factory=dict, description="System capabilities")
    historical_performance: Dict[str, float] = Field(default_factory=dict, description="Historical performance metrics")
    current_load: Dict[str, float] = Field(default_factory=dict, description="Current system load")
    user_preferences: Dict[str, Any] = Field(default_factory=dict, description="User preferences")
    
    @field_validator('historical_performance')
    @classmethod
    def validate_performance_metrics(cls, v):
        for key, value in v.items():
            if not isinstance(value, (int, float)) or value < 0:
                raise ValueError(f"Performance metric {key} must be a non-negative number")
        return v


# ============================================================================
# Planning Output Models
# ============================================================================

class PlanningResult(BaseModel):
    """Result of the planning process."""
    task_graph: TaskGraph = Field(..., description="Generated task graph")
    planning_metadata: Dict[str, Any] = Field(default_factory=dict, description="Planning metadata")
    estimated_cost: float = Field(default=0.0, ge=0, description="Estimated total cost")
    estimated_latency: float = Field(default=0.0, ge=0, description="Estimated total latency")
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Planning confidence")
    alternatives: List[TaskGraph] = Field(default_factory=list, description="Alternative plans")
    reasoning: str = Field(default="", description="Planning reasoning and rationale")
    
    @field_validator('confidence_score')
    @classmethod
    def validate_confidence(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError("Confidence score must be between 0.0 and 1.0")
        return v


class TaskEstimate(BaseModel):
    """Estimate for a single task."""
    task_id: str = Field(..., description="Task ID")
    estimated_cost: float = Field(default=0.0, ge=0, description="Estimated cost")
    estimated_latency: float = Field(default=0.0, ge=0, description="Estimated latency")
    resource_requirements: Dict[str, Any] = Field(default_factory=dict, description="Resource requirements")
    dependencies: List[str] = Field(default_factory=list, description="Task dependencies")
    priority: int = Field(default=1, ge=1, le=10, description="Task priority (1-10)")
    risk_level: str = Field(default="low", description="Risk level: low, medium, high")
    
    @field_validator('risk_level')
    @classmethod
    def validate_risk_level(cls, v):
        allowed_levels = ['low', 'medium', 'high']
        if v not in allowed_levels:
            raise ValueError(f"Risk level must be one of: {allowed_levels}")
        return v


# ============================================================================
# Planning Strategies
# ============================================================================

class PlanningStrategy(ABC):
    """Abstract base class for planning strategies."""
    
    @abstractmethod
    async def plan(self, input_data: PlanningInput, policy: PlanningPolicy, context: PlanningContext) -> PlanningResult:
        """Generate a plan based on input, policy, and context."""
        pass
    
    @abstractmethod
    def get_strategy_name(self) -> str:
        """Get the name of this planning strategy."""
        pass


class SequentialPlanningStrategy(PlanningStrategy):
    """Sequential planning strategy - tasks executed one after another."""
    
    def get_strategy_name(self) -> str:
        return "sequential"
    
    async def plan(self, input_data: PlanningInput, policy: PlanningPolicy, context: PlanningContext) -> PlanningResult:
        """Generate a sequential plan."""
        tasks = await self._generate_tasks(input_data, context)
        
        # Create sequential dependencies
        for i in range(1, len(tasks)):
            tasks[i].dependencies = [tasks[i-1].task_id]
        
        # Create task graph
        task_graph = TaskGraph(
            graph_id=str(uuid.uuid4()),
            name=f"Sequential Plan: {input_data.user_intent[:50]}",
            description=f"Sequential execution plan for: {input_data.user_intent}",
            tasks=tasks,
            entry_points=[tasks[0].task_id] if tasks else [],
            exit_points=[tasks[-1].task_id] if tasks else []
        )
        
        # Calculate estimates
        estimates = await self._calculate_estimates(tasks, context)
        total_cost = sum(est.estimated_cost for est in estimates)
        total_latency = sum(est.estimated_latency for est in estimates)
        
        return PlanningResult(
            task_graph=task_graph,
            estimated_cost=total_cost,
            estimated_latency=total_latency,
            confidence_score=0.8,
            reasoning="Sequential execution ensures proper dependency handling but may be slower"
        )
    
    async def _generate_tasks(self, input_data: PlanningInput, context: PlanningContext) -> List[Task]:
        """Generate tasks based on input and context."""
        tasks = []
        
        # Analyze user intent to determine required tasks
        intent_tasks = await self._analyze_intent(input_data.user_intent, input_data.features)
        
        for i, task_info in enumerate(intent_tasks):
            task = Task(
                task_id=f"task_{i+1}_{uuid.uuid4().hex[:8]}",
                name=task_info["name"],
                description=task_info["description"],
                input_data=task_info.get("input_data", {}),
                required_tools=task_info.get("required_tools", []),
                metadata=task_info.get("metadata", {})
            )
            tasks.append(task)
        
        return tasks
    
    async def _analyze_intent(self, user_intent: str, features: List[str]) -> List[Dict[str, Any]]:
        """Analyze user intent to determine required tasks."""
        # This is a simplified intent analysis
        # In a real implementation, this would use NLP/AI to understand intent
        
        intent_lower = user_intent.lower()
        tasks = []
        
        if "search" in intent_lower or "find" in intent_lower:
            tasks.append({
                "name": "Search Information",
                "description": "Search for relevant information based on user query",
                "required_tools": ["search_tool", "knowledge_base"],
                "input_data": {"query": user_intent},
                "metadata": {"type": "search", "priority": 1}
            })
        
        if "analyze" in intent_lower or "process" in intent_lower:
            tasks.append({
                "name": "Analyze Data",
                "description": "Analyze and process data according to user requirements",
                "required_tools": ["analysis_tool", "data_processor"],
                "input_data": {"analysis_type": "general"},
                "metadata": {"type": "analysis", "priority": 2}
            })
        
        if "generate" in intent_lower or "create" in intent_lower:
            tasks.append({
                "name": "Generate Content",
                "description": "Generate content based on user specifications",
                "required_tools": ["generation_tool", "llm_provider"],
                "input_data": {"content_type": "general"},
                "metadata": {"type": "generation", "priority": 3}
            })
        
        if "summarize" in intent_lower or "summarise" in intent_lower:
            tasks.append({
                "name": "Summarize Information",
                "description": "Create a summary of relevant information",
                "required_tools": ["summarization_tool", "llm_provider"],
                "input_data": {"summary_type": "general"},
                "metadata": {"type": "summarization", "priority": 4}
            })
        
        # Default task if no specific intent detected
        if not tasks:
            tasks.append({
                "name": "Process Request",
                "description": "Process user request using available capabilities",
                "required_tools": ["general_processor"],
                "input_data": {"request": user_intent},
                "metadata": {"type": "general", "priority": 1}
            })
        
        return tasks
    
    async def _calculate_estimates(self, tasks: List[Task], context: PlanningContext) -> List[TaskEstimate]:
        """Calculate estimates for tasks."""
        estimates = []
        
        for task in tasks:
            # Base estimates
            base_cost = 0.1  # Base cost per task
            base_latency = 1.0  # Base latency per task
            
            # Adjust based on task complexity
            complexity_multiplier = len(task.required_tools) * 0.2 + 1.0
            
            # Adjust based on historical performance
            historical_adjustment = context.historical_performance.get(task.name, 1.0)
            
            estimate = TaskEstimate(
                task_id=task.task_id,
                estimated_cost=base_cost * complexity_multiplier,
                estimated_latency=base_latency * complexity_multiplier * historical_adjustment,
                resource_requirements={"cpu": 1.0, "memory": 0.5},
                priority=task.metadata.get("priority", 1),
                risk_level="medium" if complexity_multiplier > 1.5 else "low"
            )
            estimates.append(estimate)
        
        return estimates


class ParallelPlanningStrategy(PlanningStrategy):
    """Parallel planning strategy - tasks executed in parallel where possible."""
    
    def get_strategy_name(self) -> str:
        return "parallel"
    
    async def plan(self, input_data: PlanningInput, policy: PlanningPolicy, context: PlanningContext) -> PlanningResult:
        """Generate a parallel plan."""
        tasks = await self._generate_tasks(input_data, context)
        
        # Analyze dependencies and create parallel groups
        task_groups = await self._create_parallel_groups(tasks, context)
        
        # Create dependencies between groups
        all_tasks = []
        entry_points = []
        exit_points = []
        
        for i, group in enumerate(task_groups):
            for task in group:
                all_tasks.append(task)
            
            # First group has no dependencies
            if i == 0:
                entry_points.extend([task.task_id for task in group])
            else:
                # Depend on previous group
                prev_group_ids = [task.task_id for task in task_groups[i-1]]
                for task in group:
                    task.dependencies = prev_group_ids
            
            # Last group has no dependents
            if i == len(task_groups) - 1:
                exit_points.extend([task.task_id for task in group])
        
        # Create task graph
        task_graph = TaskGraph(
            graph_id=str(uuid.uuid4()),
            name=f"Parallel Plan: {input_data.user_intent[:50]}",
            description=f"Parallel execution plan for: {input_data.user_intent}",
            tasks=all_tasks,
            entry_points=entry_points,
            exit_points=exit_points
        )
        
        # Calculate estimates
        estimates = await self._calculate_estimates(all_tasks, context)
        total_cost = sum(est.estimated_cost for est in estimates)
        
        # Parallel latency is the maximum latency in each group
        group_latencies = []
        for group in task_groups:
            group_estimates = [est for est in estimates if est.task_id in [t.task_id for t in group]]
            group_latency = max(est.estimated_latency for est in group_estimates) if group_estimates else 0
            group_latencies.append(group_latency)
        
        total_latency = sum(group_latencies)
        
        return PlanningResult(
            task_graph=task_graph,
            estimated_cost=total_cost,
            estimated_latency=total_latency,
            confidence_score=0.7,
            reasoning="Parallel execution maximizes efficiency but requires careful dependency management"
        )
    
    async def _generate_tasks(self, input_data: PlanningInput, context: PlanningContext) -> List[Task]:
        """Generate tasks based on input and context."""
        # Similar to sequential strategy but with parallel considerations
        tasks = []
        
        intent_tasks = await self._analyze_intent(input_data.user_intent, input_data.features)
        
        for i, task_info in enumerate(intent_tasks):
            task = Task(
                task_id=f"task_{i+1}_{uuid.uuid4().hex[:8]}",
                name=task_info["name"],
                description=task_info["description"],
                input_data=task_info.get("input_data", {}),
                required_tools=task_info.get("required_tools", []),
                metadata=task_info.get("metadata", {})
            )
            tasks.append(task)
        
        return tasks
    
    async def _analyze_intent(self, user_intent: str, features: List[str]) -> List[Dict[str, Any]]:
        """Analyze user intent to determine required tasks."""
        # Similar to sequential strategy
        return await SequentialPlanningStrategy()._analyze_intent(user_intent, features)
    
    async def _create_parallel_groups(self, tasks: List[Task], context: PlanningContext) -> List[List[Task]]:
        """Create groups of tasks that can run in parallel."""
        groups = []
        current_group = []
        
        for task in tasks:
            # Check if task can run in parallel with current group
            if self._can_run_parallel(task, current_group, context):
                current_group.append(task)
            else:
                # Start new group
                if current_group:
                    groups.append(current_group)
                current_group = [task]
        
        if current_group:
            groups.append(current_group)
        
        return groups
    
    def _can_run_parallel(self, task: Task, group: List[Task], context: PlanningContext) -> bool:
        """Check if a task can run in parallel with a group of tasks."""
        if not group:
            return True
        
        # Check for resource conflicts
        task_resources = self._get_task_resources(task)
        for group_task in group:
            group_resources = self._get_task_resources(group_task)
            if self._has_resource_conflict(task_resources, group_resources):
                return False
        
        # Check for tool conflicts
        task_tools = set(task.required_tools)
        for group_task in group:
            group_tools = set(group_task.required_tools)
            if task_tools & group_tools:  # Intersection
                return False
        
        return True
    
    def _get_task_resources(self, task: Task) -> Dict[str, Any]:
        """Get resource requirements for a task."""
        return task.metadata.get("resource_requirements", {"cpu": 1.0, "memory": 0.5})
    
    def _has_resource_conflict(self, resources1: Dict[str, Any], resources2: Dict[str, Any]) -> bool:
        """Check if two resource requirements conflict."""
        # Simple conflict detection - in practice, this would be more sophisticated
        total_cpu = resources1.get("cpu", 0) + resources2.get("cpu", 0)
        total_memory = resources1.get("memory", 0) + resources2.get("memory", 0)
        
        return total_cpu > 4.0 or total_memory > 2.0  # Arbitrary limits
    
    async def _calculate_estimates(self, tasks: List[Task], context: PlanningContext) -> List[TaskEstimate]:
        """Calculate estimates for tasks."""
        return await SequentialPlanningStrategy()._calculate_estimates(tasks, context)


class OptimizedPlanningStrategy(PlanningStrategy):
    """Optimized planning strategy - balances cost, speed, and quality."""
    
    def get_strategy_name(self) -> str:
        return "optimized"
    
    async def plan(self, input_data: PlanningInput, policy: PlanningPolicy, context: PlanningContext) -> PlanningResult:
        """Generate an optimized plan."""
        # Generate multiple candidate plans
        sequential_plan = await SequentialPlanningStrategy().plan(input_data, policy, context)
        parallel_plan = await ParallelPlanningStrategy().plan(input_data, policy, context)
        
        # Evaluate plans against policy
        candidates = [
            (sequential_plan, "sequential"),
            (parallel_plan, "parallel")
        ]
        
        # Select best plan based on policy
        best_plan = await self._select_best_plan(candidates, policy)
        
        # Optimize the selected plan
        optimized_plan = await self._optimize_plan(best_plan, policy, context)
        
        return optimized_plan
    
    async def _select_best_plan(self, candidates: List[Tuple[PlanningResult, str]], policy: PlanningPolicy) -> PlanningResult:
        """Select the best plan based on policy."""
        best_score = -1
        best_plan = None
        
        for plan, strategy_name in candidates:
            score = await self._evaluate_plan(plan, policy)
            if score > best_score:
                best_score = score
                best_plan = plan
        
        return best_plan or candidates[0][0]
    
    async def _evaluate_plan(self, plan: PlanningResult, policy: PlanningPolicy) -> float:
        """Evaluate a plan against the policy."""
        score = 0.0
        
        # Cost evaluation
        if policy.budget_limit:
            cost_ratio = plan.estimated_cost / policy.budget_limit
            score += (1.0 - min(cost_ratio, 1.0)) * 0.4
        
        # Latency evaluation
        if policy.latency_limit:
            latency_ratio = plan.estimated_latency / policy.latency_limit
            score += (1.0 - min(latency_ratio, 1.0)) * 0.4
        
        # Confidence evaluation
        score += plan.confidence_score * 0.2
        
        return score
    
    async def _optimize_plan(self, plan: PlanningResult, policy: PlanningPolicy, context: PlanningContext) -> PlanningResult:
        """Optimize a plan based on policy."""
        # Apply optimizations based on policy
        if policy.optimization_target == "cost":
            plan = await self._optimize_for_cost(plan, context)
        elif policy.optimization_target == "speed":
            plan = await self._optimize_for_speed(plan, context)
        elif policy.optimization_target == "quality":
            plan = await self._optimize_for_quality(plan, context)
        else:  # efficiency
            plan = await self._optimize_for_efficiency(plan, context)
        
        return plan
    
    async def _optimize_for_cost(self, plan: PlanningResult, context: PlanningContext) -> PlanningResult:
        """Optimize plan for cost."""
        # Reduce task complexity where possible
        optimized_tasks = []
        for task in plan.task_graph.tasks:
            if len(task.required_tools) > 1:
                # Try to reduce tool requirements
                simplified_task = Task(
                    task_id=task.task_id,
                    name=task.name,
                    description=task.description,
                    input_data=task.input_data,
                    required_tools=task.required_tools[:1],  # Use only first tool
                    metadata=task.metadata
                )
                optimized_tasks.append(simplified_task)
            else:
                optimized_tasks.append(task)
        
        # Update task graph
        plan.task_graph.tasks = optimized_tasks
        plan.estimated_cost *= 0.8  # Assume 20% cost reduction
        plan.reasoning += " Optimized for cost reduction."
        
        return plan
    
    async def _optimize_for_speed(self, plan: PlanningResult, context: PlanningContext) -> PlanningResult:
        """Optimize plan for speed."""
        # Increase parallelism where possible
        plan.estimated_latency *= 0.7  # Assume 30% speed improvement
        plan.reasoning += " Optimized for speed improvement."
        
        return plan
    
    async def _optimize_for_quality(self, plan: PlanningResult, context: PlanningContext) -> PlanningResult:
        """Optimize plan for quality."""
        # Add quality assurance tasks
        plan.confidence_score = min(plan.confidence_score + 0.1, 1.0)
        plan.reasoning += " Optimized for quality assurance."
        
        return plan
    
    async def _optimize_for_efficiency(self, plan: PlanningResult, context: PlanningContext) -> PlanningResult:
        """Optimize plan for efficiency."""
        # Balance cost and speed
        plan.estimated_cost *= 0.9
        plan.estimated_latency *= 0.8
        plan.reasoning += " Optimized for efficiency."
        
        return plan


# ============================================================================
# Main Agent Planner
# ============================================================================

class AgentPlanner:
    """Main agent planner that orchestrates planning strategies."""
    
    def __init__(self):
        self.strategies: Dict[str, PlanningStrategy] = {
            "sequential": SequentialPlanningStrategy(),
            "parallel": ParallelPlanningStrategy(),
            "optimized": OptimizedPlanningStrategy()
        }
        self.logger = logging.getLogger(__name__)
        
        # Statistics
        self.total_plans_generated = 0
        self.successful_plans = 0
        self.failed_plans = 0
    
    async def plan(
        self,
        input_data: PlanningInput,
        policy: PlanningPolicy,
        context: PlanningContext,
        strategy: Optional[str] = None
    ) -> PlanningResult:
        """Generate a plan based on input, policy, and context."""
        try:
            # Select strategy
            if strategy is None:
                strategy = self._select_strategy(policy)
            
            if strategy not in self.strategies:
                raise ValueError(f"Unknown strategy: {strategy}")
            
            # Generate plan
            self.logger.info(f"Generating plan using {strategy} strategy")
            result = await self.strategies[strategy].plan(input_data, policy, context)
            
            # Update statistics
            self.total_plans_generated += 1
            self.successful_plans += 1
            
            # Validate against policy constraints
            result = await self._validate_against_policy(result, policy)
            
            self.logger.info(f"Plan generated successfully. Cost: {result.estimated_cost}, Latency: {result.estimated_latency}")
            
            return result
            
        except Exception as e:
            self.failed_plans += 1
            self.logger.error(f"Planning failed: {e}")
            raise
    
    def _select_strategy(self, policy: PlanningPolicy) -> str:
        """Select the best strategy based on policy."""
        if policy.priority == "speed":
            return "parallel"
        elif policy.priority == "quality":
            return "optimized"
        else:  # balanced
            return "optimized"
    
    async def _validate_against_policy(self, result: PlanningResult, policy: PlanningPolicy) -> PlanningResult:
        """Validate plan against policy constraints."""
        # Check budget constraint
        if policy.budget_limit and result.estimated_cost > policy.budget_limit:
            self.logger.warning(f"Plan exceeds budget limit: {result.estimated_cost} > {policy.budget_limit}")
            # Could implement cost reduction here
        
        # Check latency constraint
        if policy.latency_limit and result.estimated_latency > policy.latency_limit:
            self.logger.warning(f"Plan exceeds latency limit: {result.estimated_latency} > {policy.latency_limit}")
            # Could implement latency reduction here
        
        return result
    
    async def generate_alternatives(
        self,
        input_data: PlanningInput,
        policy: PlanningPolicy,
        context: PlanningContext,
        num_alternatives: int = 3
    ) -> List[PlanningResult]:
        """Generate alternative plans."""
        alternatives = []
        
        for strategy_name in self.strategies.keys():
            try:
                result = await self.strategies[strategy_name].plan(input_data, policy, context)
                alternatives.append(result)
                
                if len(alternatives) >= num_alternatives:
                    break
                    
            except Exception as e:
                self.logger.warning(f"Failed to generate alternative with {strategy_name}: {e}")
                continue
        
        return alternatives
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get planner statistics."""
        success_rate = (self.successful_plans / self.total_plans_generated * 100) if self.total_plans_generated > 0 else 0
        
        return {
            "total_plans_generated": self.total_plans_generated,
            "successful_plans": self.successful_plans,
            "failed_plans": self.failed_plans,
            "success_rate": success_rate,
            "available_strategies": list(self.strategies.keys())
        }
    
    def register_strategy(self, name: str, strategy: PlanningStrategy) -> None:
        """Register a custom planning strategy."""
        self.strategies[name] = strategy
        self.logger.info(f"Registered custom strategy: {name}")


# ============================================================================
# Factory Functions
# ============================================================================

def create_agent_planner() -> AgentPlanner:
    """Create an agent planner with default strategies."""
    return AgentPlanner()


def create_planning_input(
    specifications: Dict[str, Any],
    features: List[str],
    user_intent: str,
    context: Optional[Dict[str, Any]] = None,
    constraints: Optional[Dict[str, Any]] = None
) -> PlanningInput:
    """Create a planning input with the given parameters."""
    return PlanningInput(
        specifications=specifications,
        features=features,
        user_intent=user_intent,
        context=context,
        constraints=constraints
    )


def create_planning_policy(
    budget_limit: Optional[float] = None,
    latency_limit: Optional[float] = None,
    priority: str = "balanced",
    optimization_target: str = "efficiency",
    parallel_execution: bool = True
) -> PlanningPolicy:
    """Create a planning policy with the given parameters."""
    return PlanningPolicy(
        budget_limit=budget_limit,
        latency_limit=latency_limit,
        priority=priority,
        optimization_target=optimization_target,
        parallel_execution=parallel_execution
    )


def create_planning_context(
    available_tools: Optional[List[ToolSpec]] = None,
    system_capabilities: Optional[Dict[str, Any]] = None,
    historical_performance: Optional[Dict[str, float]] = None,
    current_load: Optional[Dict[str, float]] = None,
    user_preferences: Optional[Dict[str, Any]] = None
) -> PlanningContext:
    """Create a planning context with the given parameters."""
    return PlanningContext(
        available_tools=available_tools or [],
        system_capabilities=system_capabilities or {},
        historical_performance=historical_performance or {},
        current_load=current_load or {},
        user_preferences=user_preferences or {}
    )


# ============================================================================
# Export all classes and functions
# ============================================================================

__all__ = [
    # Input models
    "PlanningInput",
    "PlanningPolicy",
    "PlanningContext",
    
    # Output models
    "PlanningResult",
    "TaskEstimate",
    
    # Strategies
    "PlanningStrategy",
    "SequentialPlanningStrategy",
    "ParallelPlanningStrategy",
    "OptimizedPlanningStrategy",
    
    # Main planner
    "AgentPlanner",
    
    # Factory functions
    "create_agent_planner",
    "create_planning_input",
    "create_planning_policy",
    "create_planning_context",
]
