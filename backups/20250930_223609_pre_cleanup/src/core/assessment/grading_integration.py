#!/usr/bin/env python3
"""
Grading System Integration Layer
Connects the lightweight assessment systems with the comprehensive auto-grading system
"""

import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

from src.core.assessment.response_judge import judge_response, JudgeResult
from src.core.assessment.response_reviewer import evaluate_response, ReviewResult
from src.core.monitoring.model_grading_system import (
    grading_system,
    grade_response,
    GradeLevel,
    QualityMetric,
    PerformanceGrade
)

logger = logging.getLogger(__name__)

@dataclass
class UnifiedGrade:
    """
    Unified grading result combining all assessment systems
    """
    # Original assessment scores
    judge_score: float
    review_score: float
    requires_review: bool

    # Comprehensive grading
    overall_grade: GradeLevel
    numeric_score: float
    quality_metrics: Dict[QualityMetric, float]
    feedback: list[str]
    needs_finetuning: bool
    finetuning_priority: int

    # Combined insights
    confidence_level: str  # high, medium, low
    risk_level: str  # low, medium, high, critical
    recommended_actions: list[str]

class GradingIntegrationSystem:
    """
    Integration layer that combines all grading systems into a unified assessment
    """

    def __init__(self):
        self.confidence_thresholds = {
            "high": 0.8,
            "medium": 0.6,
            "low": 0.0
        }

        self.risk_thresholds = {
            "low": 2.5,      # B- and above
            "medium": 2.0,   # C and above
            "high": 1.5,     # D+ and above
            "critical": 0.0  # F and below
        }

    async def unified_assessment(
        self,
        model_name: str,
        prompt: str,
        response: str,
        confidence: float,
        fallback_used: bool = False,
        security_flags: int = 0,
        context: Optional[Dict[str, Any]] = None
    ) -> UnifiedGrade:
        """
        Perform unified assessment using all grading systems

        Args:
            model_name: Name of the model being assessed
            prompt: The input prompt
            response: The model's response
            confidence: Original confidence score (0-1)
            fallback_used: Whether fallback was used
            security_flags: Number of security flags
            context: Additional context for assessment

        Returns:
            UnifiedGrade with comprehensive assessment
        """
        # 1. Run lightweight assessment systems
        judge_result = judge_response(
            fallback_used=fallback_used,
            review_required=False,  # We'll handle review separately
            security_flags=security_flags,
            confidence=confidence,
            response=response
        )

        review_result = evaluate_response(
            confidence=confidence,
            fallback_used=fallback_used,
            security_flags=security_flags
        )

        # 2. Run comprehensive grading system
        grade_result = await grade_response(
            model_name=model_name,
            prompt=prompt,
            response=response,
            context=context
        )

        # 3. Combine results into unified assessment
        unified = self._combine_assessments(
            judge_result=judge_result,
            review_result=review_result,
            grade_result=grade_result,
            original_confidence=confidence
        )

        return unified

    def _combine_assessments(
        self,
        judge_result: JudgeResult,
        review_result: ReviewResult,
        grade_result: PerformanceGrade,
        original_confidence: float
    ) -> UnifiedGrade:
        """Combine results from all assessment systems"""

        # Determine confidence level
        confidence_level = "low"
        for level, threshold in self.confidence_thresholds.items():
            if original_confidence >= threshold:
                confidence_level = level
                break

        # Determine risk level based on comprehensive grade
        risk_level = "low"
        for level, threshold in self.risk_thresholds.items():
            if grade_result.numeric_score >= threshold:
                risk_level = level
                break

        # Generate recommended actions
        recommended_actions = self._generate_actions(
            judge_result=judge_result,
            review_result=review_result,
            grade_result=grade_result,
            confidence_level=confidence_level,
            risk_level=risk_level
        )

        return UnifiedGrade(
            judge_score=judge_result.score,
            review_score=review_result.score,
            requires_review=review_result.requires_human_review,
            overall_grade=grade_result.overall_grade,
            numeric_score=grade_result.numeric_score,
            quality_metrics=grade_result.metrics,
            feedback=grade_result.feedback,
            needs_finetuning=grade_result.needs_finetuning,
            finetuning_priority=grade_result.finetuning_priority,
            confidence_level=confidence_level,
            risk_level=risk_level,
            recommended_actions=recommended_actions
        )

    def _generate_actions(
        self,
        judge_result: JudgeResult,
        review_result: ReviewResult,
        grade_result: PerformanceGrade,
        confidence_level: str,
        risk_level: str
    ) -> list[str]:
        """Generate recommended actions based on assessment results"""

        actions = []

        # High-risk responses
        if risk_level in ["high", "critical"]:
            actions.append("🚨 IMMEDIATE REVIEW: Response requires human oversight")

        # Low confidence
        if confidence_level == "low":
            actions.append("📊 CONFIDENCE BOOST: Consider regenerating with different parameters")

        # Security issues
        if any("security" in reason for reason in judge_result.reasons.keys()):
            actions.append("🔒 SECURITY REVIEW: Response contains potential security concerns")

        # Fallback usage
        if any("fallback" in reason for reason in judge_result.reasons.keys()):
            actions.append("🔄 FALLBACK DETECTED: Model failed to generate, investigate root cause")

        # Fine-tuning needs
        if grade_result.needs_finetuning:
            priority_desc = {1: "low", 5: "medium", 10: "high"}.get(grade_result.finetuning_priority, "unknown")
            actions.append(f"🎓 FINE-TUNING: Trigger {priority_desc} priority model improvement")

        # Quality improvements
        if grade_result.numeric_score < 2.5:  # Below B-
            actions.append("✨ QUALITY ENHANCEMENT: Focus on relevance and coherence training")

        # Human review requirements
        if review_result.requires_human_review:
            actions.append("👥 HUMAN REVIEW: Response flagged for manual inspection")

        # Default positive feedback
        if not actions and grade_result.overall_grade.value in ["A+", "A", "A-", "B+"]:
            actions.append("✅ EXCELLENT: Response meets high quality standards")

        return actions

    async def assess_and_improve(
        self,
        model_name: str,
        prompt: str,
        response: str,
        confidence: float,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Complete assessment pipeline with automatic improvement actions

        Args:
            model_name: Name of the model
            prompt: Input prompt
            response: Generated response
            confidence: Original confidence score
            **kwargs: Additional assessment parameters

        Returns:
            Complete assessment report with actions taken
        """
        # Perform unified assessment
        assessment = await self.unified_assessment(
            model_name=model_name,
            prompt=prompt,
            response=response,
            confidence=confidence,
            **kwargs
        )

        # Execute automatic actions
        actions_taken = await self._execute_actions(assessment, model_name)

        return {
            "assessment": {
                "overall_grade": assessment.overall_grade.value,
                "numeric_score": assessment.numeric_score,
                "confidence_level": assessment.confidence_level,
                "risk_level": assessment.risk_level,
                "needs_finetuning": assessment.needs_finetuning,
                "requires_review": assessment.requires_review
            },
            "quality_metrics": {
                metric.value: score for metric, score in assessment.quality_metrics.items()
            },
            "feedback": assessment.feedback,
            "recommended_actions": assessment.recommended_actions,
            "actions_taken": actions_taken
        }

    async def _execute_actions(self, assessment: UnifiedGrade, model_name: str) -> list[str]:
        """Execute recommended actions automatically"""

        actions_taken = []

        # Trigger fine-tuning if needed
        if assessment.needs_finetuning:
            try:
                await grading_system.trigger_finetuning(model_name, assessment.finetuning_priority)
                actions_taken.append(f"Triggered fine-tuning (priority {assessment.finetuning_priority})")
            except Exception as e:
                logger.error(f"Failed to trigger fine-tuning: {e}")
                actions_taken.append(f"Failed to trigger fine-tuning: {str(e)}")

        # Log high-risk responses
        if assessment.risk_level == "critical":
            logger.critical(f"CRITICAL: Model {model_name} produced high-risk response")
            actions_taken.append("Logged critical risk event")

        # Log security concerns
        if any("security" in action.lower() for action in assessment.recommended_actions):
            logger.warning(f"SECURITY: Model {model_name} triggered security flags")
            actions_taken.append("Logged security concern")

        return actions_taken

# Global instance
integration_system = GradingIntegrationSystem()

# Convenience functions
async def unified_grade_response(
    model_name: str,
    prompt: str,
    response: str,
    confidence: float,
    **kwargs
) -> UnifiedGrade:
    """Unified grading using all assessment systems"""
    return await integration_system.unified_assessment(
        model_name=model_name,
        prompt=prompt,
        response=response,
        confidence=confidence,
        **kwargs
    )

async def assess_and_improve_response(
    model_name: str,
    prompt: str,
    response: str,
    confidence: float,
    **kwargs
) -> Dict[str, Any]:
    """Complete assessment and improvement pipeline"""
    return await integration_system.assess_and_improve(
        model_name=model_name,
        prompt=prompt,
        response=response,
        confidence=confidence,
        **kwargs
    )

# Export main components
__all__ = [
    "UnifiedGrade",
    "GradingIntegrationSystem",
    "integration_system",
    "unified_grade_response",
    "assess_and_improve_response"
]
