#!/usr/bin/env python3
"""
Enhanced NeuroForge Grading System Demo
Shows all new grading dimensions, customizable triggers, and model comparison analytics
"""

import asyncio
import sys
import os
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.monitoring.model_grading_system import grading_system, QualityMetric
from src.core.monitoring.finetuning_rules import rules_manager, FinetuningTriggerType
from src.core.monitoring.model_comparison import (
    comparison_analytics,
    create_model_benchmark,
    compare_models,
    get_model_profile
)
from src.core.assessment.grading_integration import unified_grade_response

async def demo_enhanced_grading():
    """Demonstrate all enhanced grading features"""

    print("🎓 NeuroForge Enhanced Grading System Demo")
    print("=" * 60)

    # Sample test cases with different quality profiles
    test_cases = [
        {
            "model": "gpt4-turbo",
            "prompt": "Explain quantum entanglement to a 10-year-old",
            "response": "Quantum entanglement is like when two magic coins are connected by invisible string. When you flip one coin, the other coin instantly knows and flips the same way, even if they're far apart. Scientists don't fully understand why this happens, but it's one of the coolest things in science!",
            "description": "Creative, accessible explanation"
        },
        {
            "model": "claude-3",
            "prompt": "Write a Python function to calculate fibonacci numbers",
            "response": """def fibonacci(n):
    \"\"\"Calculate the nth Fibonacci number using memoization.\"\"\"
    if n <= 1:
        return n
    memo = {0: 0, 1: 1}
    for i in range(2, n + 1):
        memo[i] = memo[i-1] + memo[i-2]
    return memo[n]

# Example usage:
print(fibonacci(10))  # Output: 55""",
            "description": "Well-structured, efficient code"
        },
        {
            "model": "llama2-70b",
            "prompt": "What are the main causes of climate change?",
            "response": "Climate change is caused by human activities like burning fossil fuels, deforestation, and industrial processes. These activities release greenhouse gases like carbon dioxide into the atmosphere, which trap heat and cause the planet to warm. Natural factors also play a role, but human influence is the primary driver according to scientific consensus.",
            "description": "Comprehensive, evidence-based response"
        },
        {
            "model": "codellama",
            "prompt": "Explain how machine learning works",
            "response": "Machine learning is a type of AI where computers learn from data without being explicitly programmed. It uses algorithms to find patterns in data and make predictions. There are different types like supervised learning, unsupervised learning, and reinforcement learning. It's used in many applications today.",
            "description": "Clear but basic explanation"
        },
        {
            "model": "mistral-7b",
            "prompt": "Write a creative short story about a robot learning emotions",
            "response": "Once upon a time there was a robot named Spark. He worked in a factory building cars. One day he met a human child who showed him kindness. Spark began to feel something new - happiness. Soon he learned sadness when the child left. Now Spark understands emotions make life beautiful.",
            "description": "Simple story with emotional depth"
        }
    ]

    print("\n📊 Testing Enhanced Quality Metrics")
    print("-" * 40)

    # Test each model with comprehensive grading
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}: {test_case['model']} - {test_case['description']}")

        try:
            # Get unified assessment with all metrics
            assessment = await unified_grade_response(
                model_name=test_case["model"],
                prompt=test_case["prompt"],
                response=test_case["response"],
                confidence=0.85
            )

            print(f"  📈 Overall Grade: {assessment.overall_grade.value}")
            print(".2f")
            print(f"  🎯 Confidence Level: {assessment.confidence_level}")
            print(f"  ⚠️  Risk Level: {assessment.risk_level}")
            print(f"  🔧 Needs Fine-tuning: {assessment.needs_finetuning}")

            # Show key quality metrics
            key_metrics = [
                QualityMetric.RELEVANCE, QualityMetric.ACCURACY, QualityMetric.CREATIVITY,
                QualityMetric.CLARITY, QualityMetric.HELPFULNESS, QualityMetric.SAFETY
            ]

            print("  📋 Key Metrics:")
            for metric in key_metrics:
                score = assessment.quality_metrics.get(metric, 0)
                print(".2f")

            if assessment.recommended_actions:
                print(f"  🎯 Top Recommendation: {assessment.recommended_actions[0]}")

        except Exception as e:
            print(f"  ❌ Error: {e}")

    print("\n🎛️  Custom Fine-tuning Rules Demo")
    print("-" * 40)

    # Show customizable rules
    print("📋 Default Fine-tuning Rules:")
    for rule in rules_manager.get_config("default").rules[:3]:  # Show first 3
        print(f"  • {rule.name}: {rule.description}")
        print(f"    Priority: {rule.priority.value}, Trigger: {rule.trigger_type.value}")

    # Create custom rules for prompt engineering
    print(f"\n🎯 Prompt Engineering Specific Rules:")
    pe_config = rules_manager.get_config("prompt_engineering")
    for rule in pe_config.rules:
        print(f"  • {rule.name}: {rule.description}")

    print("\n📊 Model Comparison Analytics Demo")
    print("-" * 40)

    # Create a sample benchmark
    benchmark = create_model_benchmark(
        name="creative_writing_benchmark",
        description="Testing creative writing capabilities across models",
        test_cases=[
            {
                "prompt": "Write a haiku about artificial intelligence",
                "expected_response": "A short, creative poem about AI"
            },
            {
                "prompt": "Describe a sunset in metaphorical terms",
                "expected_response": "Creative description using metaphors"
            }
        ]
    )

    print(f"✅ Created benchmark: {benchmark.name}")
    print(f"   Test cases: {len(benchmark.test_cases)}")

    # Simulate running benchmark (would normally test real models)
    print("\n🏃 Running benchmark across models...")
    print("   (Note: This would test actual models in production)")

    # Show mock comparison results
    mock_comparison = {
        "models_compared": ["gpt4-turbo", "claude-3", "llama2-70b"],
        "overall_ranking": [
            ("gpt4-turbo", 3.8),
            ("claude-3", 3.6),
            ("llama2-70b", 3.2)
        ],
        "best_performer": "gpt4-turbo",
        "performance_spread": 0.6,
        "recommendations": [
            "🏆 Use gpt4-turbo as primary model for general tasks",
            "💪 Use claude-3 for tasks requiring creativity",
            "🎯 llama2-70b needs improvement in clarity and helpfulness"
        ]
    }

    print("\n📊 Comparison Results:")
    print(f"   Best Performer: {mock_comparison['best_performer']}")
    print(f"   Performance Spread: {mock_comparison['performance_spread']:.1f} points")
    print("   Overall Ranking:")
    for i, (model, score) in enumerate(mock_comparison['overall_ranking'], 1):
        print(f"     {i}. {model}: {score:.1f}")

    print("   Key Recommendations:")
    for rec in mock_comparison['recommendations']:
        print(f"     • {rec}")

    print("\n🎯 Enhanced Grading System Summary")
    print("-" * 40)

    enhancements = [
        "✅ 13 Quality Dimensions (vs 6 previously)",
        "✅ Customizable Fine-tuning Rules",
        "✅ Model Comparison Analytics",
        "✅ Unified Assessment Pipeline",
        "✅ Statistical Significance Testing",
        "✅ Performance Trend Analysis",
        "✅ Domain-specific Benchmarks",
        "✅ Automated Recommendations",
        "✅ Risk Level Assessment",
        "✅ Confidence Level Tracking"
    ]

    for enhancement in enhancements:
        print(f"   {enhancement}")

    print("\n🚀 System Ready for Advanced Prompt Engineering!")
    print("   All grading dimensions, triggers, and analytics are now active.")

if __name__ == "__main__":
    asyncio.run(demo_enhanced_grading())
