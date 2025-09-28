"""
Tests for Agent Planner

Comprehensive test suite for the agent planner including:
- Planning input validation and processing
- TaskGraph generation and optimization
- Budget and latency policy enforcement
- Multiple planning strategies
- Performance and error handling

Created: 2024-09-24
Status: Draft
"""

import asyncio
import pytest
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any
from unittest.mock import Mock, AsyncMock, patch

from src.core.runtime.planner import (
    # Input models
    PlanningInput,
    PlanningPolicy,
    PlanningContext,
    
    # Output models
    PlanningResult,
    TaskEstimate,
    
    # Strategies
    PlanningStrategy,
    SequentialPlanningStrategy,
    ParallelPlanningStrategy,
    OptimizedPlanningStrategy,
    
    # Main planner
    AgentPlanner,
    
    # Factory functions
    create_agent_planner,
    create_planning_input,
    create_planning_policy,
    create_planning_context,
)

from src.core.models.contracts import ToolSpec, ToolParameter


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def sample_specifications():
    """Sample specifications for testing."""
    return {
        "system_name": "Agentic LLM Core",
        "version": "0.1.0",
        "capabilities": ["text_generation", "image_processing", "data_analysis"],
        "constraints": {
            "max_concurrent_tasks": 10,
            "memory_limit": "8GB",
            "cpu_limit": "4 cores"
        }
    }


@pytest.fixture
def sample_features():
    """Sample features for testing."""
    return [
        "text_generation",
        "image_processing",
        "data_analysis",
        "search",
        "summarization",
        "translation"
    ]


@pytest.fixture
def sample_user_intent():
    """Sample user intent for testing."""
    return "Analyze the provided documents and generate a comprehensive summary with key insights"


@pytest.fixture
def sample_tool_specs():
    """Sample tool specifications for testing."""
    return [
        ToolSpec(
            name="search_tool",
            description="Search for information",
            parameters=[
                ToolParameter(name="query", type="str", description="Search query"),
                ToolParameter(name="limit", type="int", description="Result limit", default=10)
            ],
            returns={"results": "list"},
            category="search"
        ),
        ToolSpec(
            name="analysis_tool",
            description="Analyze data",
            parameters=[
                ToolParameter(name="data", type="list", description="Data to analyze"),
                ToolParameter(name="method", type="str", description="Analysis method")
            ],
            returns={"insights": "dict"},
            category="analysis"
        ),
        ToolSpec(
            name="generation_tool",
            description="Generate content",
            parameters=[
                ToolParameter(name="prompt", type="str", description="Generation prompt"),
                ToolParameter(name="max_length", type="int", description="Maximum length", default=1000)
            ],
            returns={"content": "str"},
            category="generation"
        )
    ]


@pytest.fixture
def sample_planning_input(sample_specifications, sample_features, sample_user_intent):
    """Sample planning input for testing."""
    return PlanningInput(
        specifications=sample_specifications,
        features=sample_features,
        user_intent=sample_user_intent,
        context={"user_id": "test_user", "session_id": "test_session"},
        constraints={"time_limit": 300}
    )


@pytest.fixture
def sample_planning_policy():
    """Sample planning policy for testing."""
    return PlanningPolicy(
        budget_limit=100.0,
        latency_limit=60.0,
        priority="balanced",
        optimization_target="efficiency",
        parallel_execution=True
    )


@pytest.fixture
def sample_planning_context(sample_tool_specs):
    """Sample planning context for testing."""
    return PlanningContext(
        available_tools=sample_tool_specs,
        system_capabilities={"cpu": 4.0, "memory": 8.0, "gpu": 1.0},
        historical_performance={"search_tool": 0.5, "analysis_tool": 1.2, "generation_tool": 2.0},
        current_load={"cpu": 0.3, "memory": 0.4, "gpu": 0.1},
        user_preferences={"quality": "high", "speed": "medium"}
    )


# ============================================================================
# Input Model Tests
# ============================================================================

class TestPlanningInput:
    """Test PlanningInput model."""
    
    def test_valid_planning_input(self, sample_planning_input):
        """Test valid planning input creation."""
        assert sample_planning_input.specifications is not None
        assert len(sample_planning_input.features) > 0
        assert sample_planning_input.user_intent is not None
        assert sample_planning_input.context is not None
        assert sample_planning_input.constraints is not None
    
    def test_planning_input_validation(self):
        """Test planning input validation."""
        # Valid input
        valid_input = PlanningInput(
            specifications={"test": "spec"},
            features=["feature1", "feature2"],
            user_intent="Test intent"
        )
        assert valid_input.user_intent == "Test intent"
        
        # Empty features
        with pytest.raises(ValueError):
            PlanningInput(
                specifications={"test": "spec"},
                features=[],
                user_intent="Test intent"
            )
        
        # Empty user intent
        with pytest.raises(ValueError):
            PlanningInput(
                specifications={"test": "spec"},
                features=["feature1"],
                user_intent=""
            )
        
        # Whitespace-only user intent
        with pytest.raises(ValueError):
            PlanningInput(
                specifications={"test": "spec"},
                features=["feature1"],
                user_intent="   "
            )


class TestPlanningPolicy:
    """Test PlanningPolicy model."""
    
    def test_valid_planning_policy(self, sample_planning_policy):
        """Test valid planning policy creation."""
        assert sample_planning_policy.budget_limit == 100.0
        assert sample_planning_policy.latency_limit == 60.0
        assert sample_planning_policy.priority == "balanced"
        assert sample_planning_policy.optimization_target == "efficiency"
        assert sample_planning_policy.parallel_execution is True
    
    def test_planning_policy_defaults(self):
        """Test planning policy defaults."""
        policy = PlanningPolicy()
        assert policy.budget_limit is None
        assert policy.latency_limit is None
        assert policy.priority == "balanced"
        assert policy.optimization_target == "efficiency"
        assert policy.parallel_execution is True
    
    def test_planning_policy_validation(self):
        """Test planning policy validation."""
        # Valid policy
        valid_policy = PlanningPolicy(
            budget_limit=50.0,
            latency_limit=30.0,
            priority="speed",
            optimization_target="cost"
        )
        assert valid_policy.priority == "speed"
        assert valid_policy.optimization_target == "cost"
        
        # Invalid priority
        with pytest.raises(ValueError):
            PlanningPolicy(priority="invalid")
        
        # Invalid optimization target
        with pytest.raises(ValueError):
            PlanningPolicy(optimization_target="invalid")
        
        # Negative budget
        with pytest.raises(ValueError):
            PlanningPolicy(budget_limit=-10.0)
        
        # Negative latency
        with pytest.raises(ValueError):
            PlanningPolicy(latency_limit=-5.0)


class TestPlanningContext:
    """Test PlanningContext model."""
    
    def test_valid_planning_context(self, sample_planning_context):
        """Test valid planning context creation."""
        assert len(sample_planning_context.available_tools) > 0
        assert sample_planning_context.system_capabilities is not None
        assert sample_planning_context.historical_performance is not None
        assert sample_planning_context.current_load is not None
        assert sample_planning_context.user_preferences is not None
    
    def test_planning_context_defaults(self):
        """Test planning context defaults."""
        context = PlanningContext()
        assert context.available_tools == []
        assert context.system_capabilities == {}
        assert context.historical_performance == {}
        assert context.current_load == {}
        assert context.user_preferences == {}
    
    def test_planning_context_validation(self):
        """Test planning context validation."""
        # Valid context
        valid_context = PlanningContext(
            historical_performance={"tool1": 1.0, "tool2": 2.0},
            current_load={"cpu": 0.5, "memory": 0.6}
        )
        assert valid_context.historical_performance["tool1"] == 1.0
        
        # Negative performance metric
        with pytest.raises(ValueError):
            PlanningContext(historical_performance={"tool1": -1.0})


# ============================================================================
# Output Model Tests
# ============================================================================

class TestPlanningResult:
    """Test PlanningResult model."""
    
    def test_planning_result_creation(self):
        """Test planning result creation."""
        from src.core.models.contracts import TaskGraph, Task
        
        # Create a simple task graph
        task = Task(
            task_id="test_task",
            name="Test Task",
            description="A test task",
            input_data={"test": "data"}
        )
        
        task_graph = TaskGraph(
            graph_id="test_graph",
            name="Test Graph",
            description="A test graph",
            tasks=[task],
            entry_points=[task.task_id],
            exit_points=[task.task_id]
        )
        
        result = PlanningResult(
            task_graph=task_graph,
            estimated_cost=10.0,
            estimated_latency=5.0,
            confidence_score=0.8,
            reasoning="Test reasoning"
        )
        
        assert result.task_graph == task_graph
        assert result.estimated_cost == 10.0
        assert result.estimated_latency == 5.0
        assert result.confidence_score == 0.8
        assert result.reasoning == "Test reasoning"
    
    def test_planning_result_validation(self):
        """Test planning result validation."""
        from src.core.models.contracts import TaskGraph, Task
        
        task = Task(task_id="test", name="Test", description="Test")
        task_graph = TaskGraph(graph_id="test", name="Test", tasks=[task])
        
        # Valid result
        valid_result = PlanningResult(
            task_graph=task_graph,
            confidence_score=0.5
        )
        assert valid_result.confidence_score == 0.5
        
        # Invalid confidence score
        with pytest.raises(ValueError):
            PlanningResult(
                task_graph=task_graph,
                confidence_score=1.5
            )


class TestTaskEstimate:
    """Test TaskEstimate model."""
    
    def test_task_estimate_creation(self):
        """Test task estimate creation."""
        estimate = TaskEstimate(
            task_id="test_task",
            estimated_cost=5.0,
            estimated_latency=2.0,
            resource_requirements={"cpu": 1.0, "memory": 0.5},
            dependencies=["dep1", "dep2"],
            priority=3,
            risk_level="medium"
        )
        
        assert estimate.task_id == "test_task"
        assert estimate.estimated_cost == 5.0
        assert estimate.estimated_latency == 2.0
        assert estimate.resource_requirements == {"cpu": 1.0, "memory": 0.5}
        assert estimate.dependencies == ["dep1", "dep2"]
        assert estimate.priority == 3
        assert estimate.risk_level == "medium"
    
    def test_task_estimate_defaults(self):
        """Test task estimate defaults."""
        estimate = TaskEstimate(task_id="test_task")
        
        assert estimate.estimated_cost == 0.0
        assert estimate.estimated_latency == 0.0
        assert estimate.resource_requirements == {}
        assert estimate.dependencies == []
        assert estimate.priority == 1
        assert estimate.risk_level == "low"
    
    def test_task_estimate_validation(self):
        """Test task estimate validation."""
        # Valid estimate
        valid_estimate = TaskEstimate(
            task_id="test",
            priority=5,
            risk_level="high"
        )
        assert valid_estimate.priority == 5
        assert valid_estimate.risk_level == "high"
        
        # Invalid priority
        with pytest.raises(ValueError):
            TaskEstimate(task_id="test", priority=0)
        
        # Invalid risk level
        with pytest.raises(ValueError):
            TaskEstimate(task_id="test", risk_level="invalid")


# ============================================================================
# Strategy Tests
# ============================================================================

class TestSequentialPlanningStrategy:
    """Test SequentialPlanningStrategy."""
    
    @pytest.fixture
    def strategy(self):
        """Create sequential planning strategy."""
        return SequentialPlanningStrategy()
    
    def test_strategy_name(self, strategy):
        """Test strategy name."""
        assert strategy.get_strategy_name() == "sequential"
    
    @pytest.mark.asyncio
    async def test_plan_generation(self, strategy, sample_planning_input, sample_planning_policy, sample_planning_context):
        """Test plan generation."""
        result = await strategy.plan(sample_planning_input, sample_planning_policy, sample_planning_context)
        
        assert isinstance(result, PlanningResult)
        assert result.task_graph is not None
        assert len(result.task_graph.tasks) > 0
        assert result.estimated_cost >= 0
        assert result.estimated_latency >= 0
        assert 0.0 <= result.confidence_score <= 1.0
        assert result.reasoning is not None
    
    @pytest.mark.asyncio
    async def test_sequential_dependencies(self, strategy, sample_planning_input, sample_planning_policy, sample_planning_context):
        """Test that sequential strategy creates proper dependencies."""
        result = await strategy.plan(sample_planning_input, sample_planning_policy, sample_planning_context)
        
        tasks = result.task_graph.tasks
        if len(tasks) > 1:
            # Check that tasks have sequential dependencies
            for i in range(1, len(tasks)):
                assert tasks[i].dependencies == [tasks[i-1].task_id]
    
    @pytest.mark.asyncio
    async def test_intent_analysis(self, strategy, sample_features):
        """Test intent analysis."""
        intents = [
            "Search for information about AI",
            "Analyze the data and provide insights",
            "Generate a summary of the document",
            "Create a report based on the analysis"
        ]
        
        for intent in intents:
            tasks = await strategy._analyze_intent(intent, sample_features)
            assert len(tasks) > 0
            assert all("name" in task for task in tasks)
            assert all("description" in task for task in tasks)


class TestParallelPlanningStrategy:
    """Test ParallelPlanningStrategy."""
    
    @pytest.fixture
    def strategy(self):
        """Create parallel planning strategy."""
        return ParallelPlanningStrategy()
    
    def test_strategy_name(self, strategy):
        """Test strategy name."""
        assert strategy.get_strategy_name() == "parallel"
    
    @pytest.mark.asyncio
    async def test_plan_generation(self, strategy, sample_planning_input, sample_planning_policy, sample_planning_context):
        """Test plan generation."""
        result = await strategy.plan(sample_planning_input, sample_planning_policy, sample_planning_context)
        
        assert isinstance(result, PlanningResult)
        assert result.task_graph is not None
        assert len(result.task_graph.tasks) > 0
        assert result.estimated_cost >= 0
        assert result.estimated_latency >= 0
        assert 0.0 <= result.confidence_score <= 1.0
    
    @pytest.mark.asyncio
    async def test_parallel_groups(self, strategy, sample_planning_context):
        """Test parallel group creation."""
        from src.core.models.contracts import Task
        
        # Create test tasks
        tasks = [
            Task(task_id="task1", name="Task 1", description="Task 1", required_tools=["tool1"]),
            Task(task_id="task2", name="Task 2", description="Task 2", required_tools=["tool2"]),
            Task(task_id="task3", name="Task 3", description="Task 3", required_tools=["tool1"])
        ]
        
        groups = await strategy._create_parallel_groups(tasks, sample_planning_context)
        
        assert len(groups) > 0
        assert all(len(group) > 0 for group in groups)
        
        # Check that tasks with conflicting tools are in different groups
        tool1_tasks = [task for group in groups for task in group if "tool1" in task.required_tools]
        assert len(tool1_tasks) <= 1  # Should be at most one per group
    
    @pytest.mark.asyncio
    async def test_resource_conflict_detection(self, strategy):
        """Test resource conflict detection."""
        from src.core.models.contracts import Task
        
        # Create tasks with resource requirements
        task1 = Task(
            task_id="task1",
            name="Task 1",
            description="Task 1",
            metadata={"resource_requirements": {"cpu": 3.0, "memory": 1.0}}
        )
        
        task2 = Task(
            task_id="task2",
            name="Task 2",
            description="Task 2",
            metadata={"resource_requirements": {"cpu": 2.0, "memory": 1.5}}
        )
        
        # Should conflict (total CPU > 4.0)
        can_parallel = strategy._can_run_parallel(task1, [task2], PlanningContext())
        assert can_parallel is False


class TestOptimizedPlanningStrategy:
    """Test OptimizedPlanningStrategy."""
    
    @pytest.fixture
    def strategy(self):
        """Create optimized planning strategy."""
        return OptimizedPlanningStrategy()
    
    def test_strategy_name(self, strategy):
        """Test strategy name."""
        assert strategy.get_strategy_name() == "optimized"
    
    @pytest.mark.asyncio
    async def test_plan_generation(self, strategy, sample_planning_input, sample_planning_policy, sample_planning_context):
        """Test plan generation."""
        result = await strategy.plan(sample_planning_input, sample_planning_policy, sample_planning_context)
        
        assert isinstance(result, PlanningResult)
        assert result.task_graph is not None
        assert len(result.task_graph.tasks) > 0
        assert result.estimated_cost >= 0
        assert result.estimated_latency >= 0
        assert 0.0 <= result.confidence_score <= 1.0
    
    @pytest.mark.asyncio
    async def test_plan_evaluation(self, strategy, sample_planning_policy):
        """Test plan evaluation."""
        from src.core.models.contracts import TaskGraph, Task
        
        # Create test plans
        task = Task(task_id="test", name="Test", description="Test")
        task_graph = TaskGraph(graph_id="test", name="Test", tasks=[task])
        
        plan1 = PlanningResult(
            task_graph=task_graph,
            estimated_cost=50.0,
            estimated_latency=30.0,
            confidence_score=0.8
        )
        
        plan2 = PlanningResult(
            task_graph=task_graph,
            estimated_cost=80.0,
            estimated_latency=40.0,
            confidence_score=0.6
        )
        
        # Evaluate plans
        score1 = await strategy._evaluate_plan(plan1, sample_planning_policy)
        score2 = await strategy._evaluate_plan(plan2, sample_planning_policy)
        
        assert score1 > score2  # Plan1 should score higher (lower cost, lower latency, higher confidence)
    
    @pytest.mark.asyncio
    async def test_optimization_targets(self, strategy, sample_planning_context):
        """Test different optimization targets."""
        from src.core.models.contracts import TaskGraph, Task
        
        task = Task(task_id="test", name="Test", description="Test")
        task_graph = TaskGraph(graph_id="test", name="Test", tasks=[task])
        
        original_plan = PlanningResult(
            task_graph=task_graph,
            estimated_cost=100.0,
            estimated_latency=60.0,
            confidence_score=0.7
        )
        
        # Test cost optimization
        cost_optimized = await strategy._optimize_for_cost(original_plan, sample_planning_context)
        assert cost_optimized.estimated_cost < original_plan.estimated_cost
        
        # Test speed optimization
        speed_optimized = await strategy._optimize_for_speed(original_plan, sample_planning_context)
        assert speed_optimized.estimated_latency < original_plan.estimated_latency
        
        # Test quality optimization
        quality_optimized = await strategy._optimize_for_quality(original_plan, sample_planning_context)
        assert quality_optimized.confidence_score >= original_plan.confidence_score
        
        # Test efficiency optimization
        efficiency_optimized = await strategy._optimize_for_efficiency(original_plan, sample_planning_context)
        assert efficiency_optimized.estimated_cost < original_plan.estimated_cost
        assert efficiency_optimized.estimated_latency < original_plan.estimated_latency


# ============================================================================
# Agent Planner Tests
# ============================================================================

class TestAgentPlanner:
    """Test AgentPlanner."""
    
    @pytest.fixture
    def planner(self):
        """Create agent planner."""
        return AgentPlanner()
    
    def test_planner_initialization(self, planner):
        """Test planner initialization."""
        assert len(planner.strategies) == 3
        assert "sequential" in planner.strategies
        assert "parallel" in planner.strategies
        assert "optimized" in planner.strategies
        assert planner.total_plans_generated == 0
        assert planner.successful_plans == 0
        assert planner.failed_plans == 0
    
    @pytest.mark.asyncio
    async def test_plan_generation(self, planner, sample_planning_input, sample_planning_policy, sample_planning_context):
        """Test plan generation."""
        result = await planner.plan(sample_planning_input, sample_planning_policy, sample_planning_context)
        
        assert isinstance(result, PlanningResult)
        assert result.task_graph is not None
        assert planner.total_plans_generated == 1
        assert planner.successful_plans == 1
        assert planner.failed_plans == 0
    
    @pytest.mark.asyncio
    async def test_strategy_selection(self, planner, sample_planning_policy):
        """Test strategy selection."""
        # Speed priority should select parallel
        speed_policy = PlanningPolicy(priority="speed")
        strategy = planner._select_strategy(speed_policy)
        assert strategy == "parallel"
        
        # Quality priority should select optimized
        quality_policy = PlanningPolicy(priority="quality")
        strategy = planner._select_strategy(quality_policy)
        assert strategy == "optimized"
        
        # Balanced priority should select optimized
        balanced_policy = PlanningPolicy(priority="balanced")
        strategy = planner._select_strategy(balanced_policy)
        assert strategy == "optimized"
    
    @pytest.mark.asyncio
    async def test_specific_strategy(self, planner, sample_planning_input, sample_planning_policy, sample_planning_context):
        """Test planning with specific strategy."""
        result = await planner.plan(
            sample_planning_input,
            sample_planning_policy,
            sample_planning_context,
            strategy="sequential"
        )
        
        assert isinstance(result, PlanningResult)
        assert "Sequential" in result.task_graph.name
    
    @pytest.mark.asyncio
    async def test_invalid_strategy(self, planner, sample_planning_input, sample_planning_policy, sample_planning_context):
        """Test planning with invalid strategy."""
        with pytest.raises(ValueError):
            await planner.plan(
                sample_planning_input,
                sample_planning_policy,
                sample_planning_context,
                strategy="invalid_strategy"
            )
    
    @pytest.mark.asyncio
    async def test_policy_validation(self, planner, sample_planning_input, sample_planning_context):
        """Test policy validation."""
        # Create policy with limits
        policy = PlanningPolicy(budget_limit=10.0, latency_limit=5.0)
        
        # Mock a result that exceeds limits
        with patch.object(planner.strategies["optimized"], 'plan') as mock_plan:
            mock_result = PlanningResult(
                task_graph=sample_planning_input,  # Using input as mock graph
                estimated_cost=15.0,  # Exceeds budget
                estimated_latency=8.0,  # Exceeds latency
                confidence_score=0.8
            )
            mock_plan.return_value = mock_result
            
            result = await planner.plan(sample_planning_input, policy, sample_planning_context)
            
            # Should still return result but with warnings logged
            assert isinstance(result, PlanningResult)
    
    @pytest.mark.asyncio
    async def test_alternative_generation(self, planner, sample_planning_input, sample_planning_policy, sample_planning_context):
        """Test alternative plan generation."""
        alternatives = await planner.generate_alternatives(
            sample_planning_input,
            sample_planning_policy,
            sample_planning_context,
            num_alternatives=2
        )
        
        assert len(alternatives) <= 2
        assert all(isinstance(alt, PlanningResult) for alt in alternatives)
    
    def test_statistics(self, planner):
        """Test planner statistics."""
        # Update statistics
        planner.total_plans_generated = 10
        planner.successful_plans = 8
        planner.failed_plans = 2
        
        stats = planner.get_statistics()
        
        assert stats["total_plans_generated"] == 10
        assert stats["successful_plans"] == 8
        assert stats["failed_plans"] == 2
        assert stats["success_rate"] == 80.0
        assert "sequential" in stats["available_strategies"]
        assert "parallel" in stats["available_strategies"]
        assert "optimized" in stats["available_strategies"]
    
    def test_custom_strategy_registration(self, planner):
        """Test custom strategy registration."""
        class CustomStrategy(PlanningStrategy):
            async def plan(self, input_data, policy, context):
                return PlanningResult(
                    task_graph=input_data,  # Using input as mock graph
                    estimated_cost=0.0,
                    estimated_latency=0.0,
                    confidence_score=1.0
                )
            
            def get_strategy_name(self):
                return "custom"
        
        custom_strategy = CustomStrategy()
        planner.register_strategy("custom", custom_strategy)
        
        assert "custom" in planner.strategies
        assert planner.strategies["custom"] == custom_strategy


# ============================================================================
# Factory Function Tests
# ============================================================================

class TestFactoryFunctions:
    """Test factory functions."""
    
    def test_create_agent_planner(self):
        """Test create_agent_planner function."""
        planner = create_agent_planner()
        
        assert isinstance(planner, AgentPlanner)
        assert len(planner.strategies) == 3
    
    def test_create_planning_input(self, sample_specifications, sample_features, sample_user_intent):
        """Test create_planning_input function."""
        input_data = create_planning_input(
            specifications=sample_specifications,
            features=sample_features,
            user_intent=sample_user_intent,
            context={"test": "context"},
            constraints={"test": "constraint"}
        )
        
        assert isinstance(input_data, PlanningInput)
        assert input_data.specifications == sample_specifications
        assert input_data.features == sample_features
        assert input_data.user_intent == sample_user_intent
        assert input_data.context == {"test": "context"}
        assert input_data.constraints == {"test": "constraint"}
    
    def test_create_planning_policy(self):
        """Test create_planning_policy function."""
        policy = create_planning_policy(
            budget_limit=50.0,
            latency_limit=30.0,
            priority="speed",
            optimization_target="cost",
            parallel_execution=False
        )
        
        assert isinstance(policy, PlanningPolicy)
        assert policy.budget_limit == 50.0
        assert policy.latency_limit == 30.0
        assert policy.priority == "speed"
        assert policy.optimization_target == "cost"
        assert policy.parallel_execution is False
    
    def test_create_planning_context(self, sample_tool_specs):
        """Test create_planning_context function."""
        context = create_planning_context(
            available_tools=sample_tool_specs,
            system_capabilities={"cpu": 4.0},
            historical_performance={"tool1": 1.0},
            current_load={"cpu": 0.5},
            user_preferences={"quality": "high"}
        )
        
        assert isinstance(context, PlanningContext)
        assert context.available_tools == sample_tool_specs
        assert context.system_capabilities == {"cpu": 4.0}
        assert context.historical_performance == {"tool1": 1.0}
        assert context.current_load == {"cpu": 0.5}
        assert context.user_preferences == {"quality": "high"}


# ============================================================================
# Integration Tests
# ============================================================================

class TestPlannerIntegration:
    """Integration tests for the planner."""
    
    @pytest.mark.asyncio
    async def test_end_to_end_planning(self):
        """Test end-to-end planning process."""
        # Create comprehensive input
        specifications = {
            "system": "Agentic LLM Core",
            "version": "0.1.0",
            "capabilities": ["text_generation", "image_processing", "data_analysis"]
        }
        
        features = ["text_generation", "image_processing", "data_analysis", "search", "summarization"]
        
        user_intent = "Analyze the provided documents, search for additional information, and generate a comprehensive summary with key insights and recommendations"
        
        input_data = create_planning_input(
            specifications=specifications,
            features=features,
            user_intent=user_intent,
            context={"user_id": "test_user", "session_id": "test_session"},
            constraints={"time_limit": 300, "quality": "high"}
        )
        
        policy = create_planning_policy(
            budget_limit=100.0,
            latency_limit=60.0,
            priority="balanced",
            optimization_target="efficiency"
        )
        
        context = create_planning_context(
            available_tools=[
                ToolSpec(name="search_tool", description="Search tool"),
                ToolSpec(name="analysis_tool", description="Analysis tool"),
                ToolSpec(name="generation_tool", description="Generation tool")
            ],
            system_capabilities={"cpu": 4.0, "memory": 8.0},
            historical_performance={"search_tool": 0.5, "analysis_tool": 1.2, "generation_tool": 2.0},
            current_load={"cpu": 0.3, "memory": 0.4},
            user_preferences={"quality": "high", "speed": "medium"}
        )
        
        # Create planner and generate plan
        planner = create_agent_planner()
        result = await planner.plan(input_data, policy, context)
        
        # Validate result
        assert isinstance(result, PlanningResult)
        assert result.task_graph is not None
        assert len(result.task_graph.tasks) > 0
        assert result.estimated_cost >= 0
        assert result.estimated_latency >= 0
        assert 0.0 <= result.confidence_score <= 1.0
        assert result.reasoning is not None
        
        # Validate task graph structure
        task_graph = result.task_graph
        assert task_graph.graph_id is not None
        assert task_graph.name is not None
        assert task_graph.description is not None
        assert len(task_graph.tasks) > 0
        assert len(task_graph.entry_points) > 0
        assert len(task_graph.exit_points) > 0
        
        # Validate tasks
        for task in task_graph.tasks:
            assert task.task_id is not None
            assert task.name is not None
            assert task.description is not None
            assert task.status == TaskStatus.PENDING
    
    @pytest.mark.asyncio
    async def test_multiple_strategies_comparison(self):
        """Test comparison of multiple strategies."""
        # Create common input
        input_data = create_planning_input(
            specifications={"test": "spec"},
            features=["feature1", "feature2"],
            user_intent="Test user intent for comparison"
        )
        
        policy = create_planning_policy(
            budget_limit=50.0,
            latency_limit=30.0,
            priority="balanced"
        )
        
        context = create_planning_context()
        
        # Generate plans with different strategies
        planner = create_agent_planner()
        
        sequential_result = await planner.plan(input_data, policy, context, strategy="sequential")
        parallel_result = await planner.plan(input_data, policy, context, strategy="parallel")
        optimized_result = await planner.plan(input_data, policy, context, strategy="optimized")
        
        # All results should be valid
        assert isinstance(sequential_result, PlanningResult)
        assert isinstance(parallel_result, PlanningResult)
        assert isinstance(optimized_result, PlanningResult)
        
        # Results should have different characteristics
        assert sequential_result.task_graph.name != parallel_result.task_graph.name
        assert parallel_result.task_graph.name != optimized_result.task_graph.name


# ============================================================================
# Performance Tests
# ============================================================================

class TestPlannerPerformance:
    """Performance tests for the planner."""
    
    @pytest.mark.asyncio
    async def test_planning_performance(self):
        """Test planning performance."""
        import time
        
        # Create complex input
        specifications = {"system": "test", "capabilities": ["cap1", "cap2", "cap3"]}
        features = ["feature1", "feature2", "feature3", "feature4", "feature5"]
        user_intent = "Complex user intent that requires multiple tasks and analysis"
        
        input_data = create_planning_input(
            specifications=specifications,
            features=features,
            user_intent=user_intent
        )
        
        policy = create_planning_policy()
        context = create_planning_context()
        
        planner = create_agent_planner()
        
        # Measure planning time
        start_time = time.time()
        result = await planner.plan(input_data, policy, context)
        end_time = time.time()
        
        planning_time = end_time - start_time
        
        # Should complete within reasonable time
        assert planning_time < 5.0  # Should complete within 5 seconds
        assert isinstance(result, PlanningResult)
    
    @pytest.mark.asyncio
    async def test_concurrent_planning(self):
        """Test concurrent planning performance."""
        # Create multiple planning requests
        requests = []
        for i in range(5):
            input_data = create_planning_input(
                specifications={"test": f"spec_{i}"},
                features=["feature1", "feature2"],
                user_intent=f"User intent {i}"
            )
            requests.append((input_data, create_planning_policy(), create_planning_context()))
        
        planner = create_agent_planner()
        
        # Execute planning requests concurrently
        start_time = time.time()
        results = await asyncio.gather(*[
            planner.plan(input_data, policy, context)
            for input_data, policy, context in requests
        ])
        end_time = time.time()
        
        total_time = end_time - start_time
        
        # All results should be valid
        assert len(results) == 5
        assert all(isinstance(result, PlanningResult) for result in results)
        
        # Should complete within reasonable time
        assert total_time < 10.0  # Should complete within 10 seconds


# ============================================================================
# Error Handling Tests
# ============================================================================

class TestPlannerErrorHandling:
    """Error handling tests for the planner."""
    
    @pytest.mark.asyncio
    async def test_invalid_input_handling(self):
        """Test handling of invalid input."""
        planner = create_agent_planner()
        
        # Test with invalid input
        with pytest.raises(ValueError):
            invalid_input = create_planning_input(
                specifications={"test": "spec"},
                features=[],  # Empty features should fail
                user_intent="Test intent"
            )
    
    @pytest.mark.asyncio
    async def test_planning_failure_handling(self):
        """Test handling of planning failures."""
        planner = create_agent_planner()
        
        # Mock strategy to raise exception
        with patch.object(planner.strategies["optimized"], 'plan', side_effect=Exception("Planning failed")):
            input_data = create_planning_input(
                specifications={"test": "spec"},
                features=["feature1"],
                user_intent="Test intent"
            )
            
            with pytest.raises(Exception):
                await planner.plan(input_data, create_planning_policy(), create_planning_context())
            
            # Should update failure statistics
            assert planner.failed_plans > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
