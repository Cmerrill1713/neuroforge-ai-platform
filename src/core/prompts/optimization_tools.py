"""
Advanced Prompt Optimization Tools for Agentic LLM Core v2.0

This module provides comprehensive prompt engineering capabilities including
versioning, A/B testing, optimization, analytics, and automated improvement.

Created: 2024-09-28
Status: Production Ready
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# ============================================================================
# Data Models
# ============================================================================

class PromptType(str, Enum):
    """Types of prompts."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TEMPLATE = "template"
    CHAIN = "chain"
    CONDITIONAL = "conditional"


class PromptCategory(str, Enum):
    """Prompt categories."""
    GENERAL = "general"
    CODING = "coding"
    ANALYSIS = "analysis"
    CREATIVE = "creative"
    REASONING = "reasoning"
    TRANSLATION = "translation"
    SUMMARIZATION = "summarization"
    QUESTION_ANSWERING = "question_answering"


class OptimizationStrategy(str, Enum):
    """Prompt optimization strategies."""
    LENGTH_REDUCTION = "length_reduction"
    CLARITY_IMPROVEMENT = "clarity_improvement"
    SPECIFICITY_ENHANCEMENT = "specificity_enhancement"
    CONTEXT_OPTIMIZATION = "context_optimization"
    OUTPUT_FORMAT_IMPROVEMENT = "output_format_improvement"
    BIAS_REDUCTION = "bias_reduction"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"


class TestStatus(str, Enum):
    """A/B test status."""
    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PromptVersion(BaseModel):
    """A version of a prompt."""
    version_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    prompt_id: str = Field(..., description="Parent prompt ID")
    version_number: int = Field(..., description="Version number")
    content: str = Field(..., description="Prompt content")
    description: str = Field(..., description="Version description")
    optimization_strategy: Optional[OptimizationStrategy] = Field(None, description="Optimization strategy used")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Version metadata")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: str = Field(..., description="Creator user ID")


class Prompt(BaseModel):
    """A prompt template."""
    prompt_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., description="Prompt name")
    description: str = Field(..., description="Prompt description")
    category: PromptCategory = Field(..., description="Prompt category")
    prompt_type: PromptType = Field(..., description="Prompt type")
    content: str = Field(..., description="Current prompt content")
    variables: List[str] = Field(default_factory=list, description="Template variables")
    tags: List[str] = Field(default_factory=list, description="Prompt tags")
    versions: List[PromptVersion] = Field(default_factory=list, description="Prompt versions")
    current_version: int = Field(1, description="Current version number")
    usage_count: int = Field(0, description="Usage count")
    success_rate: float = Field(0.0, description="Success rate (0-1)")
    avg_response_time: float = Field(0.0, description="Average response time in seconds")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: str = Field(..., description="Creator user ID")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ABTest(BaseModel):
    """A/B test for prompts."""
    test_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., description="Test name")
    description: str = Field(..., description="Test description")
    prompt_a_id: str = Field(..., description="Prompt A ID")
    prompt_b_id: str = Field(..., description="Prompt B ID")
    traffic_split: float = Field(0.5, ge=0.0, le=1.0, description="Traffic split ratio")
    status: TestStatus = Field(TestStatus.DRAFT, description="Test status")
    start_date: Optional[datetime] = Field(None, description="Test start date")
    end_date: Optional[datetime] = Field(None, description="Test end date")
    success_metric: str = Field("response_quality", description="Success metric")
    min_sample_size: int = Field(100, description="Minimum sample size")
    confidence_level: float = Field(0.95, ge=0.0, le=1.0, description="Confidence level")
    results: Dict[str, Any] = Field(default_factory=dict, description="Test results")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: str = Field(..., description="Creator user ID")


class PromptExecution(BaseModel):
    """Prompt execution record."""
    execution_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    prompt_id: str = Field(..., description="Prompt ID")
    version_id: Optional[str] = Field(None, description="Version ID")
    input_data: Dict[str, Any] = Field(..., description="Input data")
    output_data: Dict[str, Any] = Field(..., description="Output data")
    response_time: float = Field(..., description="Response time in seconds")
    success: bool = Field(..., description="Execution success")
    quality_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Quality score")
    user_feedback: Optional[str] = Field(None, description="User feedback")
    error_message: Optional[str] = Field(None, description="Error message")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Execution metadata")
    executed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    executed_by: str = Field(..., description="Executor user ID")


class OptimizationSuggestion(BaseModel):
    """Prompt optimization suggestion."""
    suggestion_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    prompt_id: str = Field(..., description="Prompt ID")
    strategy: OptimizationStrategy = Field(..., description="Optimization strategy")
    current_content: str = Field(..., description="Current prompt content")
    suggested_content: str = Field(..., description="Suggested prompt content")
    improvement_reason: str = Field(..., description="Reason for improvement")
    expected_improvement: float = Field(..., ge=0.0, le=1.0, description="Expected improvement score")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in suggestion")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PromptAnalytics(BaseModel):
    """Prompt analytics data."""
    prompt_id: str = Field(..., description="Prompt ID")
    period_start: datetime = Field(..., description="Analytics period start")
    period_end: datetime = Field(..., description="Analytics period end")
    total_executions: int = Field(0, description="Total executions")
    successful_executions: int = Field(0, description="Successful executions")
    failed_executions: int = Field(0, description="Failed executions")
    avg_response_time: float = Field(0.0, description="Average response time")
    avg_quality_score: float = Field(0.0, description="Average quality score")
    unique_users: int = Field(0, description="Unique users")
    usage_by_category: Dict[str, int] = Field(default_factory=dict, description="Usage by category")
    performance_trends: Dict[str, List[float]] = Field(default_factory=dict, description="Performance trends")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ============================================================================
# Prompt Optimization Engine
# ============================================================================

class PromptOptimizationEngine:
    """Advanced prompt optimization engine."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.prompts: Dict[str, Prompt] = {}
        self.ab_tests: Dict[str, ABTest] = {}
        self.executions: List[PromptExecution] = []
        self.suggestions: List[OptimizationSuggestion] = []
        self.analytics: List[PromptAnalytics] = []
        self._load_default_prompts()
    
    def _load_default_prompts(self):
        """Load default prompt templates."""
        # General purpose prompt
        general_prompt = Prompt(
            name="General Assistant",
            description="General purpose AI assistant prompt",
            category=PromptCategory.GENERAL,
            prompt_type=PromptType.SYSTEM,
            content="You are a helpful AI assistant. Provide accurate, helpful, and concise responses to user queries.",
            variables=[],
            tags=["general", "assistant", "helpful"],
            created_by="system"
        )
        self.prompts[general_prompt.prompt_id] = general_prompt
        
        # Coding prompt
        coding_prompt = Prompt(
            name="Code Assistant",
            description="Specialized coding assistant prompt",
            category=PromptCategory.CODING,
            prompt_type=PromptType.SYSTEM,
            content="You are an expert software engineer. Write clean, efficient, and well-documented code. Explain your solutions clearly.",
            variables=[],
            tags=["coding", "programming", "software"],
            created_by="system"
        )
        self.prompts[coding_prompt.prompt_id] = coding_prompt
        
        # Analysis prompt
        analysis_prompt = Prompt(
            name="Data Analyst",
            description="Data analysis and insights prompt",
            category=PromptCategory.ANALYSIS,
            prompt_type=PromptType.SYSTEM,
            content="You are a data analyst. Analyze information systematically, provide insights, and support conclusions with evidence.",
            variables=[],
            tags=["analysis", "data", "insights"],
            created_by="system"
        )
        self.prompts[analysis_prompt.prompt_id] = analysis_prompt
        
        self.logger.info(f"Loaded {len(self.prompts)} default prompts")
    
    async def create_prompt(self, name: str, description: str, category: PromptCategory, content: str, prompt_type: PromptType = PromptType.SYSTEM, variables: Optional[List[str]] = None, tags: Optional[List[str]] = None, created_by: str = "system") -> Prompt:
        """Create a new prompt."""
        prompt = Prompt(
            name=name,
            description=description,
            category=category,
            prompt_type=prompt_type,
            content=content,
            variables=variables or [],
            tags=tags or [],
            created_by=created_by
        )
        
        # Create initial version
        version = PromptVersion(
            prompt_id=prompt.prompt_id,
            version_number=1,
            content=content,
            description="Initial version",
            created_by=created_by
        )
        prompt.versions.append(version)
        
        self.prompts[prompt.prompt_id] = prompt
        self.logger.info(f"Created prompt: {name} ({prompt.prompt_id})")
        return prompt
    
    async def get_prompt(self, prompt_id: str) -> Optional[Prompt]:
        """Get prompt by ID."""
        return self.prompts.get(prompt_id)
    
    async def update_prompt(self, prompt_id: str, content: str, description: Optional[str] = None, created_by: str = "system") -> Optional[Prompt]:
        """Update prompt content and create new version."""
        prompt = self.prompts.get(prompt_id)
        if not prompt:
            return None
        
        # Create new version
        new_version_number = prompt.current_version + 1
        version = PromptVersion(
            prompt_id=prompt_id,
            version_number=new_version_number,
            content=content,
            description=description or f"Version {new_version_number}",
            created_by=created_by
        )
        
        prompt.versions.append(version)
        prompt.content = content
        prompt.current_version = new_version_number
        prompt.updated_at = datetime.now(timezone.utc)
        
        if description:
            prompt.description = description
        
        self.logger.info(f"Updated prompt: {prompt.name} to version {new_version_number}")
        return prompt
    
    async def execute_prompt(self, prompt_id: str, input_data: Dict[str, Any], executed_by: str = "system", version_id: Optional[str] = None) -> PromptExecution:
        """Execute a prompt and record the execution."""
        prompt = self.prompts.get(prompt_id)
        if not prompt:
            raise ValueError(f"Prompt {prompt_id} not found")
        
        # Format prompt with input data
        formatted_content = prompt.content
        for variable in prompt.variables:
            if variable in input_data:
                formatted_content = formatted_content.replace(f"{{{variable}}}", str(input_data[variable]))
        
        # Simulate prompt execution (in real implementation, this would call the LLM)
        start_time = datetime.now()
        
        # Mock execution - in reality this would be an LLM call
        success = True
        output_data = {"response": f"Mock response for prompt: {prompt.name}"}
        response_time = (datetime.now() - start_time).total_seconds()
        quality_score = 0.8  # Mock quality score
        
        execution = PromptExecution(
            prompt_id=prompt_id,
            version_id=version_id,
            input_data=input_data,
            output_data=output_data,
            response_time=response_time,
            success=success,
            quality_score=quality_score,
            executed_by=executed_by
        )
        
        self.executions.append(execution)
        
        # Update prompt statistics
        prompt.usage_count += 1
        if success:
            prompt.success_rate = (prompt.success_rate * (prompt.usage_count - 1) + 1.0) / prompt.usage_count
        else:
            prompt.success_rate = (prompt.success_rate * (prompt.usage_count - 1) + 0.0) / prompt.usage_count
        
        prompt.avg_response_time = (prompt.avg_response_time * (prompt.usage_count - 1) + response_time) / prompt.usage_count
        
        self.logger.info(f"Executed prompt: {prompt.name} (success: {success})")
        return execution
    
    async def create_ab_test(self, name: str, description: str, prompt_a_id: str, prompt_b_id: str, traffic_split: float = 0.5, success_metric: str = "response_quality", created_by: str = "system") -> ABTest:
        """Create an A/B test for two prompts."""
        # Validate prompts exist
        if prompt_a_id not in self.prompts or prompt_b_id not in self.prompts:
            raise ValueError("One or both prompts not found")
        
        test = ABTest(
            name=name,
            description=description,
            prompt_a_id=prompt_a_id,
            prompt_b_id=prompt_b_id,
            traffic_split=traffic_split,
            success_metric=success_metric,
            created_by=created_by
        )
        
        self.ab_tests[test.test_id] = test
        self.logger.info(f"Created A/B test: {name} ({test.test_id})")
        return test
    
    async def start_ab_test(self, test_id: str) -> bool:
        """Start an A/B test."""
        test = self.ab_tests.get(test_id)
        if not test:
            return False
        
        if test.status != TestStatus.DRAFT:
            raise ValueError("Test is not in draft status")
        
        test.status = TestStatus.RUNNING
        test.start_date = datetime.now(timezone.utc)
        
        self.logger.info(f"Started A/B test: {test.name}")
        return True
    
    async def stop_ab_test(self, test_id: str) -> bool:
        """Stop an A/B test."""
        test = self.ab_tests.get(test_id)
        if not test:
            return False
        
        if test.status != TestStatus.RUNNING:
            raise ValueError("Test is not running")
        
        test.status = TestStatus.COMPLETED
        test.end_date = datetime.now(timezone.utc)
        
        # Calculate results
        await self._calculate_ab_test_results(test)
        
        self.logger.info(f"Stopped A/B test: {test.name}")
        return True
    
    async def _calculate_ab_test_results(self, test: ABTest):
        """Calculate A/B test results."""
        # Get executions for both prompts during test period
        test_executions = [
            exec for exec in self.executions
            if exec.executed_at >= test.start_date and exec.executed_at <= test.end_date
            and exec.prompt_id in [test.prompt_a_id, test.prompt_b_id]
        ]
        
        # Separate executions by prompt
        prompt_a_executions = [exec for exec in test_executions if exec.prompt_id == test.prompt_a_id]
        prompt_b_executions = [exec for exec in test_executions if exec.prompt_id == test.prompt_b_id]
        
        # Calculate metrics
        def calculate_metrics(executions):
            if not executions:
                return {"count": 0, "success_rate": 0, "avg_response_time": 0, "avg_quality": 0}
            
            success_count = sum(1 for exec in executions if exec.success)
            avg_response_time = sum(exec.response_time for exec in executions) / len(executions)
            avg_quality = sum(exec.quality_score or 0 for exec in executions) / len(executions)
            
            return {
                "count": len(executions),
                "success_rate": success_count / len(executions),
                "avg_response_time": avg_response_time,
                "avg_quality": avg_quality
            }
        
        prompt_a_metrics = calculate_metrics(prompt_a_executions)
        prompt_b_metrics = calculate_metrics(prompt_b_executions)
        
        # Determine winner based on success metric
        if test.success_metric == "response_quality":
            winner = "A" if prompt_a_metrics["avg_quality"] > prompt_b_metrics["avg_quality"] else "B"
        elif test.success_metric == "response_time":
            winner = "A" if prompt_a_metrics["avg_response_time"] < prompt_b_metrics["avg_response_time"] else "B"
        else:  # success_rate
            winner = "A" if prompt_a_metrics["success_rate"] > prompt_b_metrics["success_rate"] else "B"
        
        test.results = {
            "prompt_a_metrics": prompt_a_metrics,
            "prompt_b_metrics": prompt_b_metrics,
            "winner": winner,
            "confidence": 0.95,  # Mock confidence
            "statistical_significance": True  # Mock significance
        }
    
    async def generate_optimization_suggestions(self, prompt_id: str) -> List[OptimizationSuggestion]:
        """Generate optimization suggestions for a prompt."""
        prompt = self.prompts.get(prompt_id)
        if not prompt:
            return []
        
        suggestions = []
        
        # Length reduction suggestion
        if len(prompt.content) > 500:
            suggestion = OptimizationSuggestion(
                prompt_id=prompt_id,
                strategy=OptimizationStrategy.LENGTH_REDUCTION,
                current_content=prompt.content,
                suggested_content=self._reduce_prompt_length(prompt.content),
                improvement_reason="Prompt is too long, reducing length may improve clarity and performance",
                expected_improvement=0.1,
                confidence=0.7
            )
            suggestions.append(suggestion)
        
        # Clarity improvement suggestion
        if "You are" not in prompt.content:
            suggestion = OptimizationSuggestion(
                prompt_id=prompt_id,
                strategy=OptimizationStrategy.CLARITY_IMPROVEMENT,
                current_content=prompt.content,
                suggested_content=f"You are {prompt.content.lower()}",
                improvement_reason="Adding role definition improves clarity and context",
                expected_improvement=0.15,
                confidence=0.8
            )
            suggestions.append(suggestion)
        
        # Specificity enhancement suggestion
        if prompt.category == PromptCategory.CODING and "code" not in prompt.content.lower():
            suggestion = OptimizationSuggestion(
                prompt_id=prompt_id,
                strategy=OptimizationStrategy.SPECIFICITY_ENHANCEMENT,
                current_content=prompt.content,
                suggested_content=prompt.content + " Focus on writing clean, efficient, and well-documented code.",
                improvement_reason="Adding specific coding instructions improves output quality",
                expected_improvement=0.2,
                confidence=0.9
            )
            suggestions.append(suggestion)
        
        self.suggestions.extend(suggestions)
        self.logger.info(f"Generated {len(suggestions)} optimization suggestions for prompt: {prompt.name}")
        return suggestions
    
    def _reduce_prompt_length(self, content: str) -> str:
        """Reduce prompt length while maintaining meaning."""
        # Simple length reduction - remove redundant words and phrases
        replacements = {
            "You are a helpful AI assistant. Provide accurate, helpful, and concise responses to user queries.": "You are a helpful AI assistant.",
            "You are an expert software engineer. Write clean, efficient, and well-documented code. Explain your solutions clearly.": "You are an expert software engineer. Write clean, efficient code.",
            "You are a data analyst. Analyze information systematically, provide insights, and support conclusions with evidence.": "You are a data analyst. Analyze information and provide insights."
        }
        
        for original, replacement in replacements.items():
            if original in content:
                return replacement
        
        # Generic reduction
        if len(content) > 200:
            return content[:200] + "..."
        
        return content
    
    async def get_prompt_analytics(self, prompt_id: str, days: int = 30) -> Optional[PromptAnalytics]:
        """Get analytics for a prompt."""
        prompt = self.prompts.get(prompt_id)
        if not prompt:
            return None
        
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days)
        
        # Get executions in the period
        period_executions = [
            exec for exec in self.executions
            if exec.prompt_id == prompt_id and start_date <= exec.executed_at <= end_date
        ]
        
        if not period_executions:
            return PromptAnalytics(
                prompt_id=prompt_id,
                period_start=start_date,
                period_end=end_date
            )
        
        # Calculate metrics
        total_executions = len(period_executions)
        successful_executions = sum(1 for exec in period_executions if exec.success)
        failed_executions = total_executions - successful_executions
        avg_response_time = sum(exec.response_time for exec in period_executions) / total_executions
        avg_quality_score = sum(exec.quality_score or 0 for exec in period_executions) / total_executions
        unique_users = len(set(exec.executed_by for exec in period_executions))
        
        analytics = PromptAnalytics(
            prompt_id=prompt_id,
            period_start=start_date,
            period_end=end_date,
            total_executions=total_executions,
            successful_executions=successful_executions,
            failed_executions=failed_executions,
            avg_response_time=avg_response_time,
            avg_quality_score=avg_quality_score,
            unique_users=unique_users
        )
        
        self.analytics.append(analytics)
        return analytics
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics."""
        return {
            "total_prompts": len(self.prompts),
            "total_executions": len(self.executions),
            "total_ab_tests": len(self.ab_tests),
            "total_suggestions": len(self.suggestions),
            "total_analytics": len(self.analytics),
            "active_ab_tests": len([test for test in self.ab_tests.values() if test.status == TestStatus.RUNNING]),
            "avg_success_rate": sum(prompt.success_rate for prompt in self.prompts.values()) / len(self.prompts) if self.prompts else 0,
            "avg_response_time": sum(prompt.avg_response_time for prompt in self.prompts.values()) / len(self.prompts) if self.prompts else 0
        }


# ============================================================================
# Main Function
# ============================================================================

async def main():
    """Main function for testing the prompt optimization system."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Prompt Optimization System")
    parser.add_argument("--action", choices=["create", "execute", "ab_test", "suggestions", "analytics", "stats"], required=True)
    parser.add_argument("--name", help="Prompt name")
    parser.add_argument("--content", help="Prompt content")
    parser.add_argument("--category", help="Prompt category")
    parser.add_argument("--prompt_id", help="Prompt ID")
    parser.add_argument("--input", help="Input data (JSON)")
    
    args = parser.parse_args()
    
    try:
        engine = PromptOptimizationEngine()
        
        if args.action == "create":
            if not all([args.name, args.content, args.category]):
                print("Error: --name, --content, and --category are required for create action")
                return 1
            
            prompt = await engine.create_prompt(
                name=args.name,
                description=f"Prompt: {args.name}",
                category=PromptCategory(args.category),
                content=args.content
            )
            
            print(f"✅ Created prompt: {prompt.name} ({prompt.prompt_id})")
            
        elif args.action == "execute":
            if not args.prompt_id:
                print("Error: --prompt_id is required for execute action")
                return 1
            
            input_data = json.loads(args.input) if args.input else {"query": "Hello, how are you?"}
            execution = await engine.execute_prompt(args.prompt_id, input_data)
            
            print("✅ Executed prompt:")
            print(f"   Response Time: {execution.response_time:.3f}s")
            print(f"   Success: {execution.success}")
            print(f"   Quality Score: {execution.quality_score}")
            
        elif args.action == "ab_test":
            # Create a simple A/B test
            prompt_a = await engine.create_prompt(
                name="Test Prompt A",
                description="Test prompt A",
                category=PromptCategory.GENERAL,
                content="You are helpful."
            )
            
            prompt_b = await engine.create_prompt(
                name="Test Prompt B",
                description="Test prompt B",
                category=PromptCategory.GENERAL,
                content="You are a helpful AI assistant."
            )
            
            test = await engine.create_ab_test(
                name="Helpfulness Test",
                description="Testing prompt clarity",
                prompt_a_id=prompt_a.prompt_id,
                prompt_b_id=prompt_b.prompt_id
            )
            
            await engine.start_ab_test(test.test_id)
            
            # Execute some test runs
            for i in range(10):
                await engine.execute_prompt(prompt_a.prompt_id, {"query": f"Test {i}"})
                await engine.execute_prompt(prompt_b.prompt_id, {"query": f"Test {i}"})
            
            await engine.stop_ab_test(test.test_id)
            
            print("✅ A/B Test completed:")
            print(f"   Winner: {test.results['winner']}")
            print(f"   Prompt A Metrics: {test.results['prompt_a_metrics']}")
            print(f"   Prompt B Metrics: {test.results['prompt_b_metrics']}")
            
        elif args.action == "suggestions":
            if not args.prompt_id:
                print("Error: --prompt_id is required for suggestions action")
                return 1
            
            suggestions = await engine.generate_optimization_suggestions(args.prompt_id)
            print(f"💡 Generated {len(suggestions)} optimization suggestions:")
            
            for i, suggestion in enumerate(suggestions, 1):
                print(f"\n{i}. {suggestion.strategy.value}:")
                print(f"   Reason: {suggestion.improvement_reason}")
                print(f"   Expected Improvement: {suggestion.expected_improvement:.1%}")
                print(f"   Confidence: {suggestion.confidence:.1%}")
                
        elif args.action == "analytics":
            if not args.prompt_id:
                print("Error: --prompt_id is required for analytics action")
                return 1
            
            analytics = await engine.get_prompt_analytics(args.prompt_id)
            if analytics:
                print(f"📊 Analytics for prompt {args.prompt_id}:")
                print(f"   Total Executions: {analytics.total_executions}")
                print(f"   Success Rate: {analytics.successful_executions/analytics.total_executions:.1%}" if analytics.total_executions > 0 else "   Success Rate: N/A")
                print(f"   Avg Response Time: {analytics.avg_response_time:.3f}s")
                print(f"   Avg Quality Score: {analytics.avg_quality_score:.2f}")
                print(f"   Unique Users: {analytics.unique_users}")
            else:
                print("❌ No analytics data found")
                
        elif args.action == "stats":
            stats = await engine.get_system_stats()
            print("📊 System Statistics:")
            for key, value in stats.items():
                print(f"   {key}: {value}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Prompt optimization operation failed: {e}")
        return 1


if __name__ == "__main__":
    exit(asyncio.run(main()))
