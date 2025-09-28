#!/usr/bin/env python3
"""
Finetuning Grading System Integration
Integrates finetuning with the universal AI tools grading scale
"""

import json
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

class GradingLevel(str, Enum):
    """Grading levels for finetuning assessment"""
    EXCELLENT = "A+"
    VERY_GOOD = "A"
    GOOD = "B+"
    SATISFACTORY = "B"
    NEEDS_IMPROVEMENT = "C"
    POOR = "D"
    FAILED = "F"

@dataclass
class FinetuningMetrics:
    """Metrics for finetuning evaluation"""
    # Training Performance
    training_loss: float = 0.0
    validation_loss: float = 0.0
    training_time: float = 0.0
    convergence_epochs: int = 0
    
    # Model Quality
    perplexity: float = 0.0
    bleu_score: float = 0.0
    rouge_score: float = 0.0
    
    # System Performance
    memory_usage: float = 0.0
    gpu_utilization: float = 0.0
    throughput: float = 0.0
    
    # Knowledge Integration
    knowledge_retention: float = 0.0
    domain_accuracy: float = 0.0
    response_quality: float = 0.0

@dataclass
class GradingCriteria:
    """Grading criteria for finetuning assessment"""
    # Performance thresholds
    excellent_loss_threshold: float = 0.5
    good_loss_threshold: float = 1.0
    acceptable_loss_threshold: float = 2.0
    
    # Quality thresholds
    excellent_perplexity_threshold: float = 10.0
    good_perplexity_threshold: float = 20.0
    acceptable_perplexity_threshold: float = 50.0
    
    # Time thresholds (in minutes)
    excellent_time_threshold: float = 30.0
    good_time_threshold: float = 60.0
    acceptable_time_threshold: float = 120.0
    
    # Knowledge integration thresholds
    excellent_knowledge_threshold: float = 0.9
    good_knowledge_threshold: float = 0.8
    acceptable_knowledge_threshold: float = 0.7

@dataclass
class FinetuningGrade:
    """Complete finetuning grade assessment"""
    overall_grade: GradingLevel
    metrics: FinetuningMetrics
    criteria: GradingCriteria
    detailed_scores: Dict[str, Tuple[float, GradingLevel]] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)

class FinetuningGradingSystem:
    """Grading system for finetuning evaluation"""
    
    def __init__(self, criteria: Optional[GradingCriteria] = None):
        self.criteria = criteria or GradingCriteria()
        self.grading_history: List[FinetuningGrade] = []
    
    def evaluate_training_performance(self, metrics: FinetuningMetrics) -> Tuple[float, GradingLevel]:
        """Evaluate training performance"""
        score = 0.0
        
        # Loss evaluation (40% weight)
        if metrics.training_loss <= self.criteria.excellent_loss_threshold:
            score += 40.0
        elif metrics.training_loss <= self.criteria.good_loss_threshold:
            score += 30.0
        elif metrics.training_loss <= self.criteria.acceptable_loss_threshold:
            score += 20.0
        else:
            score += 10.0
        
        # Time evaluation (30% weight)
        if metrics.training_time <= self.criteria.excellent_time_threshold:
            score += 30.0
        elif metrics.training_time <= self.criteria.good_time_threshold:
            score += 25.0
        elif metrics.training_time <= self.criteria.acceptable_time_threshold:
            score += 20.0
        else:
            score += 10.0
        
        # Convergence evaluation (30% weight)
        if metrics.convergence_epochs <= 3:
            score += 30.0
        elif metrics.convergence_epochs <= 5:
            score += 25.0
        elif metrics.convergence_epochs <= 10:
            score += 20.0
        else:
            score += 10.0
        
        grade = self._score_to_grade(score)
        return score, grade
    
    def evaluate_model_quality(self, metrics: FinetuningMetrics) -> Tuple[float, GradingLevel]:
        """Evaluate model quality"""
        score = 0.0
        
        # Perplexity evaluation (50% weight)
        if metrics.perplexity <= self.criteria.excellent_perplexity_threshold:
            score += 50.0
        elif metrics.perplexity <= self.criteria.good_perplexity_threshold:
            score += 40.0
        elif metrics.perplexity <= self.criteria.acceptable_perplexity_threshold:
            score += 30.0
        else:
            score += 15.0
        
        # BLEU score evaluation (25% weight)
        if metrics.bleu_score >= 0.8:
            score += 25.0
        elif metrics.bleu_score >= 0.6:
            score += 20.0
        elif metrics.bleu_score >= 0.4:
            score += 15.0
        else:
            score += 10.0
        
        # ROUGE score evaluation (25% weight)
        if metrics.rouge_score >= 0.8:
            score += 25.0
        elif metrics.rouge_score >= 0.6:
            score += 20.0
        elif metrics.rouge_score >= 0.4:
            score += 15.0
        else:
            score += 10.0
        
        grade = self._score_to_grade(score)
        return score, grade
    
    def evaluate_system_performance(self, metrics: FinetuningMetrics) -> Tuple[float, GradingLevel]:
        """Evaluate system performance"""
        score = 0.0
        
        # Memory efficiency (40% weight)
        if metrics.memory_usage <= 8.0:  # GB
            score += 40.0
        elif metrics.memory_usage <= 16.0:
            score += 30.0
        elif metrics.memory_usage <= 32.0:
            score += 20.0
        else:
            score += 10.0
        
        # GPU utilization (30% weight)
        if metrics.gpu_utilization >= 80.0:
            score += 30.0
        elif metrics.gpu_utilization >= 60.0:
            score += 25.0
        elif metrics.gpu_utilization >= 40.0:
            score += 20.0
        else:
            score += 10.0
        
        # Throughput (30% weight)
        if metrics.throughput >= 100.0:  # samples/second
            score += 30.0
        elif metrics.throughput >= 50.0:
            score += 25.0
        elif metrics.throughput >= 25.0:
            score += 20.0
        else:
            score += 10.0
        
        grade = self._score_to_grade(score)
        return score, grade
    
    def evaluate_knowledge_integration(self, metrics: FinetuningMetrics) -> Tuple[float, GradingLevel]:
        """Evaluate knowledge integration"""
        score = 0.0
        
        # Knowledge retention (40% weight)
        if metrics.knowledge_retention >= self.criteria.excellent_knowledge_threshold:
            score += 40.0
        elif metrics.knowledge_retention >= self.criteria.good_knowledge_threshold:
            score += 30.0
        elif metrics.knowledge_retention >= self.criteria.acceptable_knowledge_threshold:
            score += 20.0
        else:
            score += 10.0
        
        # Domain accuracy (30% weight)
        if metrics.domain_accuracy >= 0.9:
            score += 30.0
        elif metrics.domain_accuracy >= 0.8:
            score += 25.0
        elif metrics.domain_accuracy >= 0.7:
            score += 20.0
        else:
            score += 10.0
        
        # Response quality (30% weight)
        if metrics.response_quality >= 0.9:
            score += 30.0
        elif metrics.response_quality >= 0.8:
            score += 25.0
        elif metrics.response_quality >= 0.7:
            score += 20.0
        else:
            score += 10.0
        
        grade = self._score_to_grade(score)
        return score, grade
    
    def generate_recommendations(self, metrics: FinetuningMetrics, scores: Dict[str, Tuple[float, GradingLevel]]) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        # Training performance recommendations
        if scores.get("training_performance", (0, GradingLevel.FAILED))[1] in [GradingLevel.NEEDS_IMPROVEMENT, GradingLevel.POOR, GradingLevel.FAILED]:
            if metrics.training_loss > self.criteria.acceptable_loss_threshold:
                recommendations.append("Consider reducing learning rate or increasing training epochs")
            if metrics.training_time > self.criteria.acceptable_time_threshold:
                recommendations.append("Optimize batch size or use gradient accumulation")
            if metrics.convergence_epochs > 10:
                recommendations.append("Adjust learning rate schedule or add warmup steps")
        
        # Model quality recommendations
        if scores.get("model_quality", (0, GradingLevel.FAILED))[1] in [GradingLevel.NEEDS_IMPROVEMENT, GradingLevel.POOR, GradingLevel.FAILED]:
            if metrics.perplexity > self.criteria.acceptable_perplexity_threshold:
                recommendations.append("Increase model capacity or improve data quality")
            if metrics.bleu_score < 0.4:
                recommendations.append("Improve training data diversity and quality")
            if metrics.rouge_score < 0.4:
                recommendations.append("Add more domain-specific training examples")
        
        # System performance recommendations
        if scores.get("system_performance", (0, GradingLevel.FAILED))[1] in [GradingLevel.NEEDS_IMPROVEMENT, GradingLevel.POOR, GradingLevel.FAILED]:
            if metrics.memory_usage > 32.0:
                recommendations.append("Use gradient checkpointing or reduce batch size")
            if metrics.gpu_utilization < 40.0:
                recommendations.append("Increase batch size or optimize data loading")
            if metrics.throughput < 25.0:
                recommendations.append("Optimize model architecture or use mixed precision")
        
        # Knowledge integration recommendations
        if scores.get("knowledge_integration", (0, GradingLevel.FAILED))[1] in [GradingLevel.NEEDS_IMPROVEMENT, GradingLevel.POOR, GradingLevel.FAILED]:
            if metrics.knowledge_retention < self.criteria.acceptable_knowledge_threshold:
                recommendations.append("Increase knowledge base coverage and quality")
            if metrics.domain_accuracy < 0.7:
                recommendations.append("Add more domain-specific examples")
            if metrics.response_quality < 0.7:
                recommendations.append("Improve prompt engineering and fine-tuning strategy")
        
        return recommendations
    
    def grade_finetuning(self, metrics: FinetuningMetrics) -> FinetuningGrade:
        """Generate complete finetuning grade"""
        logger.info("🎯 Evaluating finetuning performance...")
        
        # Evaluate each category
        training_score, training_grade = self.evaluate_training_performance(metrics)
        quality_score, quality_grade = self.evaluate_model_quality(metrics)
        system_score, system_grade = self.evaluate_system_performance(metrics)
        knowledge_score, knowledge_grade = self.evaluate_knowledge_integration(metrics)
        
        # Calculate overall grade
        overall_score = (training_score + quality_score + system_score + knowledge_score) / 4
        overall_grade = self._score_to_grade(overall_score)
        
        # Store detailed scores
        detailed_scores = {
            "training_performance": (training_score, training_grade),
            "model_quality": (quality_score, quality_grade),
            "system_performance": (system_score, system_grade),
            "knowledge_integration": (knowledge_score, knowledge_grade)
        }
        
        # Generate recommendations
        recommendations = self.generate_recommendations(metrics, detailed_scores)
        
        # Create grade object
        grade = FinetuningGrade(
            overall_grade=overall_grade,
            metrics=metrics,
            criteria=self.criteria,
            detailed_scores=detailed_scores,
            recommendations=recommendations
        )
        
        # Store in history
        self.grading_history.append(grade)
        
        logger.info(f"📊 Finetuning Grade: {overall_grade} ({overall_score:.1f}/100)")
        logger.info(f"   Training: {training_grade} ({training_score:.1f})")
        logger.info(f"   Quality: {quality_grade} ({quality_score:.1f})")
        logger.info(f"   System: {system_grade} ({system_score:.1f})")
        logger.info(f"   Knowledge: {knowledge_grade} ({knowledge_score:.1f})")
        
        return grade
    
    def _score_to_grade(self, score: float) -> GradingLevel:
        """Convert numerical score to letter grade"""
        if score >= 95:
            return GradingLevel.EXCELLENT
        elif score >= 90:
            return GradingLevel.VERY_GOOD
        elif score >= 85:
            return GradingLevel.GOOD
        elif score >= 80:
            return GradingLevel.SATISFACTORY
        elif score >= 70:
            return GradingLevel.NEEDS_IMPROVEMENT
        elif score >= 60:
            return GradingLevel.POOR
        else:
            return GradingLevel.FAILED
    
    def export_grading_report(self, grade: FinetuningGrade, output_path: str) -> None:
        """Export grading report to file"""
        report = {
            "timestamp": grade.timestamp,
            "overall_grade": grade.overall_grade.value,
            "overall_score": sum(score for score, _ in grade.detailed_scores.values()) / len(grade.detailed_scores),
            "metrics": {
                "training_loss": grade.metrics.training_loss,
                "validation_loss": grade.metrics.validation_loss,
                "training_time": grade.metrics.training_time,
                "convergence_epochs": grade.metrics.convergence_epochs,
                "perplexity": grade.metrics.perplexity,
                "bleu_score": grade.metrics.bleu_score,
                "rouge_score": grade.metrics.rouge_score,
                "memory_usage": grade.metrics.memory_usage,
                "gpu_utilization": grade.metrics.gpu_utilization,
                "throughput": grade.metrics.throughput,
                "knowledge_retention": grade.metrics.knowledge_retention,
                "domain_accuracy": grade.metrics.domain_accuracy,
                "response_quality": grade.metrics.response_quality
            },
            "detailed_scores": {
                category: {"score": score, "grade": grade.value}
                for category, (score, grade) in grade.detailed_scores.items()
            },
            "recommendations": grade.recommendations,
            "criteria": {
                "excellent_loss_threshold": grade.criteria.excellent_loss_threshold,
                "good_loss_threshold": grade.criteria.good_loss_threshold,
                "acceptable_loss_threshold": grade.criteria.acceptable_loss_threshold,
                "excellent_perplexity_threshold": grade.criteria.excellent_perplexity_threshold,
                "good_perplexity_threshold": grade.criteria.good_perplexity_threshold,
                "acceptable_perplexity_threshold": grade.criteria.acceptable_perplexity_threshold,
                "excellent_time_threshold": grade.criteria.excellent_time_threshold,
                "good_time_threshold": grade.criteria.good_time_threshold,
                "acceptable_time_threshold": grade.criteria.acceptable_time_threshold,
                "excellent_knowledge_threshold": grade.criteria.excellent_knowledge_threshold,
                "good_knowledge_threshold": grade.criteria.good_knowledge_threshold,
                "acceptable_knowledge_threshold": grade.criteria.acceptable_knowledge_threshold
            }
        }
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📄 Grading report exported to {output_path}")
    
    def get_grading_summary(self) -> Dict[str, Any]:
        """Get summary of all grading history"""
        if not self.grading_history:
            return {"message": "No grading history available"}
        
        recent_grade = self.grading_history[-1]
        grade_counts = {}
        
        for grade in self.grading_history:
            grade_value = grade.overall_grade.value
            grade_counts[grade_value] = grade_counts.get(grade_value, 0) + 1
        
        return {
            "total_evaluations": len(self.grading_history),
            "latest_grade": recent_grade.overall_grade.value,
            "latest_score": sum(score for score, _ in recent_grade.detailed_scores.values()) / len(recent_grade.detailed_scores),
            "grade_distribution": grade_counts,
            "average_score": sum(
                sum(score for score, _ in grade.detailed_scores.values()) / len(grade.detailed_scores)
                for grade in self.grading_history
            ) / len(self.grading_history),
            "improvement_trend": self._calculate_improvement_trend()
        }
    
    def _calculate_improvement_trend(self) -> str:
        """Calculate improvement trend over time"""
        if len(self.grading_history) < 2:
            return "Insufficient data"
        
        recent_scores = []
        for grade in self.grading_history[-3:]:  # Last 3 evaluations
            score = sum(s for s, _ in grade.detailed_scores.values()) / len(grade.detailed_scores)
            recent_scores.append(score)
        
        if len(recent_scores) >= 2:
            if recent_scores[-1] > recent_scores[-2]:
                return "Improving"
            elif recent_scores[-1] < recent_scores[-2]:
                return "Declining"
            else:
                return "Stable"
        
        return "Insufficient data"

# Example usage and testing
def main():
    """Example usage of the finetuning grading system"""
    logger.info("🎯 Testing Finetuning Grading System")
    logger.info("=" * 50)
    
    # Create grading system
    grading_system = FinetuningGradingSystem()
    
    # Example metrics (simulated)
    example_metrics = FinetuningMetrics(
        training_loss=0.8,
        validation_loss=1.2,
        training_time=45.0,
        convergence_epochs=4,
        perplexity=15.0,
        bleu_score=0.75,
        rouge_score=0.82,
        memory_usage=12.0,
        gpu_utilization=85.0,
        throughput=75.0,
        knowledge_retention=0.88,
        domain_accuracy=0.92,
        response_quality=0.89
    )
    
    # Grade the finetuning
    grade = grading_system.grade_finetuning(example_metrics)
    
    # Export report
    grading_system.export_grading_report(grade, "finetuning_grade_report.json")
    
    # Get summary
    summary = grading_system.get_grading_summary()
    logger.info(f"📊 Grading Summary: {summary}")
    
    return grade

if __name__ == "__main__":
    main()
