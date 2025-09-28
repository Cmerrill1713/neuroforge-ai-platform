#!/usr/bin/env python3
"""
Quick test of the finetuning grading system
"""

import sys
from pathlib import Path

# Add the project root to the path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.core.training.finetuning_grading_system import (
    FinetuningGradingSystem, 
    FinetuningMetrics, 
    GradingLevel
)

def test_grading_system():
    """Test the grading system with example metrics"""
    print("🎯 Testing Finetuning Grading System")
    print("=" * 50)
    
    # Create grading system
    grading_system = FinetuningGradingSystem()
    
    # Example metrics (simulated good performance)
    example_metrics = FinetuningMetrics(
        training_loss=0.8,
        validation_loss=1.2,
        training_time=45.0,  # minutes
        convergence_epochs=4,
        perplexity=15.0,
        bleu_score=0.75,
        rouge_score=0.82,
        memory_usage=12.0,  # GB
        gpu_utilization=85.0,  # percentage
        throughput=75.0,  # samples/second
        knowledge_retention=0.88,
        domain_accuracy=0.92,
        response_quality=0.89
    )
    
    print("📊 Example Metrics:")
    print(f"   Training Loss: {example_metrics.training_loss}")
    print(f"   Training Time: {example_metrics.training_time} minutes")
    print(f"   Perplexity: {example_metrics.perplexity}")
    print(f"   Memory Usage: {example_metrics.memory_usage} GB")
    print(f"   Knowledge Retention: {example_metrics.knowledge_retention}")
    print()
    
    # Grade the finetuning
    grade = grading_system.grade_finetuning(example_metrics)
    
    # Print results
    print("🎯 GRADING RESULTS:")
    print(f"Overall Grade: {grade.overall_grade.value}")
    print(f"Overall Score: {sum(score for score, _ in grade.detailed_scores.values()) / len(grade.detailed_scores):.1f}/100")
    print()
    print("📈 Category Breakdown:")
    for category, (score, grade_level) in grade.detailed_scores.items():
        print(f"   {category.replace('_', ' ').title()}: {grade_level.value} ({score:.1f})")
    
    if grade.recommendations:
        print()
        print("💡 Recommendations:")
        for rec in grade.recommendations:
            print(f"   • {rec}")
    
    # Export report
    grading_system.export_grading_report(grade, "test_finetuning_grade_report.json")
    print()
    print("📄 Grading report exported to test_finetuning_grade_report.json")
    
    # Get summary
    summary = grading_system.get_grading_summary()
    print()
    print("📊 Grading Summary:")
    print(f"   Total Evaluations: {summary['total_evaluations']}")
    print(f"   Latest Grade: {summary['latest_grade']}")
    print(f"   Average Score: {summary['average_score']:.1f}")
    print(f"   Improvement Trend: {summary['improvement_trend']}")
    
    return grade

if __name__ == "__main__":
    test_grading_system()
