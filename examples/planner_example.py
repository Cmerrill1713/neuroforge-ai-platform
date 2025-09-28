"""
Agent Planner Example

This example demonstrates how to use the agent planner to generate optimized
TaskGraphs based on specifications, features, and user intent with budget and
latency policies.

Created: 2024-09-24
Status: Draft
"""

import asyncio
import logging
from typing import Dict, Any, List

from src.core.runtime.planner import (
    create_agent_planner,
    create_planning_input,
    create_planning_policy,
    create_planning_context,
    PlanningInput,
    PlanningPolicy,
    PlanningContext
)

from src.core.models.contracts import ToolSpec, ToolParameter


# ============================================================================
# Example Usage
# ============================================================================

async def main():
    """Main example function."""
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    logger.info("Starting Agent Planner Example")
    
    try:
        # 1. Create comprehensive specifications
        logger.info("Creating system specifications...")
        specifications = {
            "system_name": "Agentic LLM Core v0.1",
            "version": "0.1.0",
            "architecture": "Local-first, Pipeline-based",
            "capabilities": [
                "text_generation",
                "image_processing", 
                "document_analysis",
                "data_extraction",
                "summarization",
                "translation",
                "question_answering",
                "code_generation"
            ],
            "constraints": {
                "max_concurrent_tasks": 10,
                "memory_limit": "8GB",
                "cpu_limit": "4 cores",
                "response_time_limit": "30 seconds",
                "offline_mode": True
            },
            "performance_targets": {
                "latency_threshold": 200,  # ms
                "throughput_target": 100,  # requests/minute
                "accuracy_threshold": 0.95
            }
        }
        
        # 2. Define available features
        logger.info("Defining available features...")
        features = [
            "text_generation",
            "image_processing",
            "document_analysis", 
            "data_extraction",
            "summarization",
            "translation",
            "question_answering",
            "code_generation",
            "vector_search",
            "knowledge_retrieval",
            "multimodal_processing",
            "batch_processing"
        ]
        
        # 3. Create planning context with tools
        logger.info("Creating planning context...")
        available_tools = [
            ToolSpec(
                name="qwen3_complete",
                description="Qwen3 text completion",
                parameters=[
                    ToolParameter(name="prompt", type="str", description="Input prompt"),
                    ToolParameter(name="max_tokens", type="int", description="Maximum tokens", default=1000),
                    ToolParameter(name="temperature", type="float", description="Sampling temperature", default=0.7)
                ],
                returns={"text": "str", "tokens_used": "int"},
                category="generation"
            ),
            ToolSpec(
                name="qwen3_embed",
                description="Qwen3 text embedding",
                parameters=[
                    ToolParameter(name="texts", type="list", description="Texts to embed"),
                    ToolParameter(name="normalize", type="bool", description="Normalize embeddings", default=True)
                ],
                returns={"embeddings": "list", "dimension": "int"},
                category="embedding"
            ),
            ToolSpec(
                name="qwen3_vision",
                description="Qwen3 vision-to-text",
                parameters=[
                    ToolParameter(name="image_data", type="bytes", description="Image data"),
                    ToolParameter(name="prompt", type="str", description="Vision prompt", default="Describe this image")
                ],
                returns={"text": "str", "confidence": "float"},
                category="vision"
            ),
            ToolSpec(
                name="vector_search",
                description="Vector similarity search",
                parameters=[
                    ToolParameter(name="query_vector", type="list", description="Query vector"),
                    ToolParameter(name="limit", type="int", description="Result limit", default=10),
                    ToolParameter(name="filter_metadata", type="dict", description="Metadata filter")
                ],
                returns={"results": "list", "scores": "list"},
                category="search"
            ),
            ToolSpec(
                name="document_processor",
                description="Document processing and analysis",
                parameters=[
                    ToolParameter(name="document_path", type="str", description="Path to document"),
                    ToolParameter(name="extract_text", type="bool", description="Extract text", default=True),
                    ToolParameter(name="extract_metadata", type="bool", description="Extract metadata", default=True)
                ],
                returns={"text": "str", "metadata": "dict", "pages": "int"},
                category="processing"
            ),
            ToolSpec(
                name="mcp_tool_executor",
                description="MCP tool execution",
                parameters=[
                    ToolParameter(name="tool_name", type="str", description="Tool name"),
                    ToolParameter(name="parameters", type="dict", description="Tool parameters")
                ],
                returns={"result": "any", "success": "bool"},
                category="execution"
            )
        ]
        
        context = create_planning_context(
            available_tools=available_tools,
            system_capabilities={
                "cpu": 4.0,
                "memory": 8.0,
                "gpu": 1.0,
                "storage": 100.0
            },
            historical_performance={
                "qwen3_complete": 0.5,  # 500ms average
                "qwen3_embed": 0.2,     # 200ms average
                "qwen3_vision": 1.0,    # 1s average
                "vector_search": 0.1,   # 100ms average
                "document_processor": 2.0,  # 2s average
                "mcp_tool_executor": 0.3    # 300ms average
            },
            current_load={
                "cpu": 0.3,
                "memory": 0.4,
                "gpu": 0.1,
                "storage": 0.2
            },
            user_preferences={
                "quality": "high",
                "speed": "medium",
                "cost": "low",
                "reliability": "high"
            }
        )
        
        # 4. Create agent planner
        logger.info("Creating agent planner...")
        planner = create_agent_planner()
        
        # 5. Example 1: Document Analysis Request
        logger.info("Example 1: Document Analysis Request")
        await example_document_analysis(planner, specifications, features, context)
        
        # 6. Example 2: Multimodal Processing Request
        logger.info("Example 2: Multimodal Processing Request")
        await example_multimodal_processing(planner, specifications, features, context)
        
        # 7. Example 3: Research and Summarization Request
        logger.info("Example 3: Research and Summarization Request")
        await example_research_summarization(planner, specifications, features, context)
        
        # 8. Example 4: Budget-Constrained Request
        logger.info("Example 4: Budget-Constrained Request")
        await example_budget_constrained(planner, specifications, features, context)
        
        # 9. Example 5: Speed-Optimized Request
        logger.info("Example 5: Speed-Optimized Request")
        await example_speed_optimized(planner, specifications, features, context)
        
        # 10. Generate alternative plans
        logger.info("Generating alternative plans...")
        await example_alternative_plans(planner, specifications, features, context)
        
        # 11. Show planner statistics
        logger.info("Planner Statistics:")
        stats = planner.get_statistics()
        for key, value in stats.items():
            logger.info(f"  {key}: {value}")
        
        logger.info("Agent Planner Example completed successfully!")
        
    except Exception as e:
        logger.error(f"Example failed: {e}")
        raise


async def example_document_analysis(planner, specifications, features, context):
    """Example: Document analysis request."""
    logger = logging.getLogger(__name__)
    
    user_intent = "Analyze the uploaded PDF document, extract key information, and generate a structured summary with insights and recommendations"
    
    input_data = create_planning_input(
        specifications=specifications,
        features=features,
        user_intent=user_intent,
        context={
            "document_type": "PDF",
            "document_size": "5MB",
            "user_id": "analyst_001",
            "session_id": "doc_analysis_001"
        },
        constraints={
            "quality": "high",
            "time_limit": 300,
            "output_format": "structured_json"
        }
    )
    
    policy = create_planning_policy(
        budget_limit=50.0,
        latency_limit=30.0,
        priority="quality",
        optimization_target="quality",
        parallel_execution=True
    )
    
    result = await planner.plan(input_data, policy, context)
    
    logger.info(f"Document Analysis Plan:")
    logger.info(f"  Strategy: {result.task_graph.name}")
    logger.info(f"  Tasks: {len(result.task_graph.tasks)}")
    logger.info(f"  Estimated Cost: ${result.estimated_cost:.2f}")
    logger.info(f"  Estimated Latency: {result.estimated_latency:.1f}s")
    logger.info(f"  Confidence: {result.confidence_score:.2f}")
    logger.info(f"  Reasoning: {result.reasoning}")
    
    # Show task details
    for i, task in enumerate(result.task_graph.tasks):
        logger.info(f"    Task {i+1}: {task.name}")
        logger.info(f"      Description: {task.description}")
        logger.info(f"      Tools: {task.required_tools}")
        logger.info(f"      Dependencies: {task.dependencies}")


async def example_multimodal_processing(planner, specifications, features, context):
    """Example: Multimodal processing request."""
    logger = logging.getLogger(__name__)
    
    user_intent = "Process both the uploaded image and text document, extract information from both modalities, and create a unified analysis report"
    
    input_data = create_planning_input(
        specifications=specifications,
        features=features,
        user_intent=user_intent,
        context={
            "modalities": ["image", "text"],
            "image_format": "PNG",
            "text_format": "PDF",
            "user_id": "multimodal_001",
            "session_id": "multimodal_analysis_001"
        },
        constraints={
            "fusion_method": "late_fusion",
            "quality": "high",
            "time_limit": 60
        }
    )
    
    policy = create_planning_policy(
        budget_limit=75.0,
        latency_limit=45.0,
        priority="balanced",
        optimization_target="efficiency",
        parallel_execution=True
    )
    
    result = await planner.plan(input_data, policy, context)
    
    logger.info(f"Multimodal Processing Plan:")
    logger.info(f"  Strategy: {result.task_graph.name}")
    logger.info(f"  Tasks: {len(result.task_graph.tasks)}")
    logger.info(f"  Estimated Cost: ${result.estimated_cost:.2f}")
    logger.info(f"  Estimated Latency: {result.estimated_latency:.1f}s")
    logger.info(f"  Confidence: {result.confidence_score:.2f}")


async def example_research_summarization(planner, specifications, features, context):
    """Example: Research and summarization request."""
    logger = logging.getLogger(__name__)
    
    user_intent = "Search for recent research papers on AI safety, analyze their content, extract key findings, and create a comprehensive summary with citations and recommendations"
    
    input_data = create_planning_input(
        specifications=specifications,
        features=features,
        user_intent=user_intent,
        context={
            "research_topic": "AI safety",
            "time_range": "last_2_years",
            "min_papers": 10,
            "user_id": "researcher_001",
            "session_id": "research_summary_001"
        },
        constraints={
            "citation_format": "APA",
            "quality": "high",
            "completeness": "comprehensive",
            "time_limit": 600
        }
    )
    
    policy = create_planning_policy(
        budget_limit=100.0,
        latency_limit=120.0,
        priority="quality",
        optimization_target="quality",
        parallel_execution=True
    )
    
    result = await planner.plan(input_data, policy, context)
    
    logger.info(f"Research Summarization Plan:")
    logger.info(f"  Strategy: {result.task_graph.name}")
    logger.info(f"  Tasks: {len(result.task_graph.tasks)}")
    logger.info(f"  Estimated Cost: ${result.estimated_cost:.2f}")
    logger.info(f"  Estimated Latency: {result.estimated_latency:.1f}s")
    logger.info(f"  Confidence: {result.confidence_score:.2f}")


async def example_budget_constrained(planner, specifications, features, context):
    """Example: Budget-constrained request."""
    logger = logging.getLogger(__name__)
    
    user_intent = "Generate a quick summary of the provided text document with key points and main themes"
    
    input_data = create_planning_input(
        specifications=specifications,
        features=features,
        user_intent=user_intent,
        context={
            "document_length": "short",
            "user_id": "budget_user_001",
            "session_id": "budget_summary_001"
        },
        constraints={
            "max_cost": 10.0,
            "quality": "acceptable",
            "time_limit": 30
        }
    )
    
    policy = create_planning_policy(
        budget_limit=10.0,  # Very low budget
        latency_limit=30.0,
        priority="speed",
        optimization_target="cost",
        parallel_execution=False  # Sequential to reduce cost
    )
    
    result = await planner.plan(input_data, policy, context)
    
    logger.info(f"Budget-Constrained Plan:")
    logger.info(f"  Strategy: {result.task_graph.name}")
    logger.info(f"  Tasks: {len(result.task_graph.tasks)}")
    logger.info(f"  Estimated Cost: ${result.estimated_cost:.2f}")
    logger.info(f"  Estimated Latency: {result.estimated_latency:.1f}s")
    logger.info(f"  Confidence: {result.confidence_score:.2f}")
    
    # Verify budget constraint
    if result.estimated_cost <= policy.budget_limit:
        logger.info("  ✅ Budget constraint satisfied")
    else:
        logger.warning("  ⚠️ Budget constraint exceeded")


async def example_speed_optimized(planner, specifications, features, context):
    """Example: Speed-optimized request."""
    logger = logging.getLogger(__name__)
    
    user_intent = "Quickly translate the provided text from English to Spanish and provide a confidence score"
    
    input_data = create_planning_input(
        specifications=specifications,
        features=features,
        user_intent=user_intent,
        context={
            "source_language": "English",
            "target_language": "Spanish",
            "text_length": "medium",
            "user_id": "speed_user_001",
            "session_id": "speed_translation_001"
        },
        constraints={
            "max_latency": 5.0,
            "quality": "good",
            "confidence_threshold": 0.8
        }
    )
    
    policy = create_planning_policy(
        budget_limit=25.0,
        latency_limit=5.0,  # Very low latency
        priority="speed",
        optimization_target="speed",
        parallel_execution=True
    )
    
    result = await planner.plan(input_data, policy, context)
    
    logger.info(f"Speed-Optimized Plan:")
    logger.info(f"  Strategy: {result.task_graph.name}")
    logger.info(f"  Tasks: {len(result.task_graph.tasks)}")
    logger.info(f"  Estimated Cost: ${result.estimated_cost:.2f}")
    logger.info(f"  Estimated Latency: {result.estimated_latency:.1f}s")
    logger.info(f"  Confidence: {result.confidence_score:.2f}")
    
    # Verify latency constraint
    if result.estimated_latency <= policy.latency_limit:
        logger.info("  ✅ Latency constraint satisfied")
    else:
        logger.warning("  ⚠️ Latency constraint exceeded")


async def example_alternative_plans(planner, specifications, features, context):
    """Example: Generate alternative plans."""
    logger = logging.getLogger(__name__)
    
    user_intent = "Analyze customer feedback data and generate insights for product improvement"
    
    input_data = create_planning_input(
        specifications=specifications,
        features=features,
        user_intent=user_intent,
        context={
            "data_type": "customer_feedback",
            "data_size": "large",
            "user_id": "product_manager_001",
            "session_id": "feedback_analysis_001"
        },
        constraints={
            "insight_types": ["sentiment", "themes", "recommendations"],
            "quality": "high",
            "time_limit": 180
        }
    )
    
    policy = create_planning_policy(
        budget_limit=60.0,
        latency_limit=90.0,
        priority="balanced",
        optimization_target="efficiency",
        parallel_execution=True
    )
    
    # Generate alternatives
    alternatives = await planner.generate_alternatives(
        input_data, policy, context, num_alternatives=3
    )
    
    logger.info(f"Alternative Plans Generated: {len(alternatives)}")
    
    for i, alt in enumerate(alternatives):
        logger.info(f"  Alternative {i+1}:")
        logger.info(f"    Strategy: {alt.task_graph.name}")
        logger.info(f"    Tasks: {len(alt.task_graph.tasks)}")
        logger.info(f"    Cost: ${alt.estimated_cost:.2f}")
        logger.info(f"    Latency: {alt.estimated_latency:.1f}s")
        logger.info(f"    Confidence: {alt.confidence_score:.2f}")
        logger.info(f"    Reasoning: {alt.reasoning}")


# ============================================================================
# Advanced Examples
# ============================================================================

async def advanced_example():
    """Advanced example with custom strategy."""
    logger = logging.getLogger(__name__)
    
    # Create custom strategy
    from src.core.runtime.planner import PlanningStrategy, PlanningResult, PlanningInput, PlanningPolicy, PlanningContext
    
    class CustomResearchStrategy(PlanningStrategy):
        def get_strategy_name(self) -> str:
            return "custom_research"
        
        async def plan(self, input_data: PlanningInput, policy: PlanningPolicy, context: PlanningContext) -> PlanningResult:
            # Custom logic for research tasks
            from src.core.models.contracts import TaskGraph, Task
            
            tasks = [
                Task(
                    task_id="research_search",
                    name="Research Search",
                    description="Search for relevant research papers",
                    required_tools=["vector_search", "mcp_tool_executor"],
                    input_data={"query": input_data.user_intent}
                ),
                Task(
                    task_id="paper_analysis",
                    name="Paper Analysis", 
                    description="Analyze research papers",
                    required_tools=["document_processor", "qwen3_complete"],
                    input_data={"analysis_type": "comprehensive"},
                    dependencies=["research_search"]
                ),
                Task(
                    task_id="insight_generation",
                    name="Insight Generation",
                    description="Generate insights and recommendations",
                    required_tools=["qwen3_complete"],
                    input_data={"output_format": "structured"},
                    dependencies=["paper_analysis"]
                )
            ]
            
            task_graph = TaskGraph(
                graph_id="custom_research_graph",
                name="Custom Research Strategy",
                description="Custom strategy for research tasks",
                tasks=tasks,
                entry_points=["research_search"],
                exit_points=["insight_generation"]
            )
            
            return PlanningResult(
                task_graph=task_graph,
                estimated_cost=80.0,
                estimated_latency=45.0,
                confidence_score=0.9,
                reasoning="Custom research strategy optimized for academic analysis"
            )
    
    # Register custom strategy
    planner = create_agent_planner()
    planner.register_strategy("custom_research", CustomResearchStrategy())
    
    # Use custom strategy
    input_data = create_planning_input(
        specifications={"test": "spec"},
        features=["research", "analysis", "generation"],
        user_intent="Research AI safety in autonomous systems"
    )
    
    policy = create_planning_policy()
    context = create_planning_context()
    
    result = await planner.plan(input_data, policy, context, strategy="custom_research")
    
    logger.info(f"Custom Strategy Result:")
    logger.info(f"  Strategy: {result.task_graph.name}")
    logger.info(f"  Tasks: {len(result.task_graph.tasks)}")
    logger.info(f"  Cost: ${result.estimated_cost:.2f}")
    logger.info(f"  Latency: {result.estimated_latency:.1f}s")
    logger.info(f"  Confidence: {result.confidence_score:.2f}")


# ============================================================================
# Performance Benchmark
# ============================================================================

async def performance_benchmark():
    """Performance benchmark for the planner."""
    logger = logging.getLogger(__name__)
    
    import time
    
    planner = create_agent_planner()
    
    # Create test scenarios
    scenarios = [
        {
            "name": "Simple Text Generation",
            "intent": "Generate a short story about AI",
            "features": ["text_generation"],
            "budget": 10.0,
            "latency": 5.0
        },
        {
            "name": "Complex Analysis",
            "intent": "Analyze multiple documents and generate comprehensive insights",
            "features": ["document_analysis", "summarization", "insight_generation"],
            "budget": 50.0,
            "latency": 30.0
        },
        {
            "name": "Multimodal Processing",
            "intent": "Process image and text data for unified analysis",
            "features": ["image_processing", "text_analysis", "multimodal_fusion"],
            "budget": 75.0,
            "latency": 45.0
        }
    ]
    
    logger.info("Running Performance Benchmark...")
    
    for scenario in scenarios:
        logger.info(f"Scenario: {scenario['name']}")
        
        input_data = create_planning_input(
            specifications={"test": "benchmark"},
            features=scenario["features"],
            user_intent=scenario["intent"]
        )
        
        policy = create_planning_policy(
            budget_limit=scenario["budget"],
            latency_limit=scenario["latency"]
        )
        
        context = create_planning_context()
        
        # Benchmark each strategy
        strategies = ["sequential", "parallel", "optimized"]
        
        for strategy in strategies:
            start_time = time.time()
            result = await planner.plan(input_data, policy, context, strategy=strategy)
            end_time = time.time()
            
            planning_time = end_time - start_time
            
            logger.info(f"  {strategy}:")
            logger.info(f"    Planning Time: {planning_time:.3f}s")
            logger.info(f"    Tasks: {len(result.task_graph.tasks)}")
            logger.info(f"    Cost: ${result.estimated_cost:.2f}")
            logger.info(f"    Latency: {result.estimated_latency:.1f}s")
            logger.info(f"    Confidence: {result.confidence_score:.2f}")


# ============================================================================
# Main execution
# ============================================================================

if __name__ == "__main__":
    # Run the main example
    asyncio.run(main())
    
    # Uncomment to run advanced examples
    # asyncio.run(advanced_example())
    # asyncio.run(performance_benchmark())
