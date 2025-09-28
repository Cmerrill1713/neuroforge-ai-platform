#!/usr/bin/env python3
"""
Integrated Model Adaptation System
Combines adaptive context, hallucination detection, and reasoning assistance
"""

import json
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum

from .adaptive_model_context import AdaptiveModelContextSystem, ModelCapability, ReasoningLevel
from .hallucination_detection import HallucinationDetectionSystem, ConfidenceLevel
from .reasoning_assistance import ReasoningAssistanceSystem, ReasoningDomain

logger = logging.getLogger(__name__)

class AdaptationStrategy(str, Enum):
    """Strategies for adapting to different model capabilities"""
    MINIMAL = "minimal"           # For large models - minimal intervention
    MODERATE = "moderate"         # For medium models - some assistance
    COMPREHENSIVE = "comprehensive"  # For small models - full assistance
    MAXIMAL = "maximal"          # For tiny models - maximum assistance

@dataclass
class ModelAdaptationResult:
    """Result of model adaptation"""
    original_prompt: str
    enhanced_prompt: str
    adaptation_strategy: AdaptationStrategy
    reasoning_assistance: Optional[str]
    hallucination_prevention: Optional[str]
    confidence_threshold: float
    verification_required: bool
    model_recommendations: List[str]
    success_indicators: List[str]

@dataclass
class ResponseAnalysis:
    """Analysis of model response"""
    original_response: str
    enhanced_response: str
    hallucination_detected: bool
    confidence_score: float
    reasoning_quality: float
    factual_accuracy: float
    improvement_suggestions: List[str]
    verification_needed: bool

class IntegratedModelAdaptationSystem:
    """
    Integrated system that provides comprehensive adaptation for different model capabilities
    """
    
    def __init__(self):
        self.context_system = AdaptiveModelContextSystem()
        self.hallucination_system = HallucinationDetectionSystem()
        self.reasoning_system = ReasoningAssistanceSystem()
        
        logger.info("🚀 Integrated Model Adaptation System initialized")
    
    def adapt_for_model(self, 
                       model_id: str, 
                       prompt: str, 
                       task_type: str = "general",
                       domain: str = "general") -> ModelAdaptationResult:
        """Adapt prompt and provide assistance based on model capabilities"""
        
        logger.info(f"🎯 Adapting for model: {model_id}")
        
        # Get model profile
        profile = self.context_system.get_model_profile(model_id)
        if not profile:
            logger.warning(f"Unknown model: {model_id}, using default")
            profile = self.context_system.model_profiles["llama3.2:3b"]
        
        # Determine adaptation strategy
        strategy = self._determine_adaptation_strategy(profile)
        
        # Enhance prompt with context
        enhancement = self.context_system.enhance_prompt_for_model(model_id, prompt, task_type)
        
        # Add reasoning assistance if needed
        reasoning_assistance = None
        if profile.needs_reasoning_assistance:
            reasoning_domain = self._map_task_to_reasoning_domain(task_type)
            assistance = self.reasoning_system.provide_reasoning_assistance(prompt, reasoning_domain)
            reasoning_assistance = self._format_reasoning_assistance(assistance)
        
        # Add hallucination prevention if needed
        hallucination_prevention = None
        if profile.needs_hallucination_prevention:
            hallucination_prevention = self._format_hallucination_prevention(profile)
        
        # Get model recommendations
        model_recommendations = self.context_system.get_model_recommendations(task_type)
        
        # Generate success indicators
        success_indicators = self._generate_success_indicators(profile, task_type)
        
        # Build final enhanced prompt
        enhanced_prompt = self._build_final_prompt(
            enhancement.enhanced_prompt,
            reasoning_assistance,
            hallucination_prevention,
            strategy
        )
        
        return ModelAdaptationResult(
            original_prompt=prompt,
            enhanced_prompt=enhanced_prompt,
            adaptation_strategy=strategy,
            reasoning_assistance=reasoning_assistance,
            hallucination_prevention=hallucination_prevention,
            confidence_threshold=enhancement.confidence_threshold,
            verification_required=profile.needs_hallucination_prevention,
            model_recommendations=model_recommendations.get("best_models", []),
            success_indicators=success_indicators
        )
    
    def _determine_adaptation_strategy(self, profile) -> AdaptationStrategy:
        """Determine adaptation strategy based on model profile"""
        
        if profile.capability in [ModelCapability.XLARGE, ModelCapability.LARGE]:
            return AdaptationStrategy.MINIMAL
        elif profile.capability == ModelCapability.MEDIUM:
            return AdaptationStrategy.MODERATE
        elif profile.capability == ModelCapability.SMALL:
            return AdaptationStrategy.COMPREHENSIVE
        else:  # TINY
            return AdaptationStrategy.MAXIMAL
    
    def _map_task_to_reasoning_domain(self, task_type: str) -> ReasoningDomain:
        """Map task type to reasoning domain"""
        
        mapping = {
            "programming": ReasoningDomain.PROGRAMMING,
            "coding": ReasoningDomain.PROGRAMMING,
            "mathematics": ReasoningDomain.MATHEMATICS,
            "math": ReasoningDomain.MATHEMATICS,
            "logic": ReasoningDomain.LOGIC,
            "problem_solving": ReasoningDomain.PROBLEM_SOLVING,
            "analysis": ReasoningDomain.PROBLEM_SOLVING,  # Map analysis to problem solving
            "decision_making": ReasoningDomain.DECISION_MAKING
        }
        
        return mapping.get(task_type, ReasoningDomain.PROBLEM_SOLVING)
    
    def _format_reasoning_assistance(self, assistance) -> str:
        """Format reasoning assistance for inclusion in prompt"""
        
        parts = []
        parts.append("🧠 REASONING ASSISTANCE:")
        parts.append("")
        
        for i, step in enumerate(assistance.step_by_step_guide, 1):
            parts.append(f"{i}. {step}")
        
        if assistance.examples:
            parts.append("")
            parts.append("📚 EXAMPLES:")
            for example in assistance.examples[:3]:
                parts.append(f"• {example}")
        
        if assistance.common_pitfalls:
            parts.append("")
            parts.append("⚠️ COMMON PITFALLS TO AVOID:")
            for pitfall in assistance.common_pitfalls[:3]:
                parts.append(f"• {pitfall}")
        
        return "\n".join(parts)
    
    def _format_hallucination_prevention(self, profile) -> str:
        """Format hallucination prevention instructions"""
        
        parts = []
        parts.append("🛡️ HALLUCINATION PREVENTION:")
        parts.append("")
        parts.append("IMPORTANT: This model has a high hallucination risk. Please:")
        parts.append("• Only provide information you are confident about")
        parts.append("• If uncertain, clearly state your uncertainty")
        parts.append("• Avoid speculation beyond the given information")
        parts.append("• Use phrases like 'I'm not certain' when appropriate")
        parts.append("")
        parts.append("CONFIDENCE LEVELS:")
        parts.append("• High confidence: I'm certain this is correct")
        parts.append("• Medium confidence: This is likely correct")
        parts.append("• Low confidence: I'm not sure about this")
        parts.append("• No confidence: I don't know the answer")
        
        return "\n".join(parts)
    
    def _generate_success_indicators(self, profile, task_type: str) -> List[str]:
        """Generate success indicators for the model and task"""
        
        indicators = []
        
        # General indicators
        indicators.extend([
            "Response addresses all parts of the question",
            "Answer is clear and well-structured",
            "Reasoning is logical and coherent"
        ])
        
        # Task-specific indicators
        if task_type in ["programming", "coding"]:
            indicators.extend([
                "Code is syntactically correct",
                "Solution handles edge cases",
                "Algorithm is efficient"
            ])
        elif task_type in ["mathematics", "math"]:
            indicators.extend([
                "Calculations are accurate",
                "Answer includes correct units",
                "Work is shown clearly"
            ])
        elif task_type == "logic":
            indicators.extend([
                "Premises are clearly stated",
                "Logical steps are valid",
                "Conclusion follows from premises"
            ])
        
        # Model-specific indicators
        if profile.needs_hallucination_prevention:
            indicators.append("No hallucination patterns detected")
        
        if profile.needs_reasoning_assistance:
            indicators.append("Reasoning follows structured approach")
        
        return indicators
    
    def _build_final_prompt(self, 
                          enhanced_prompt: str,
                          reasoning_assistance: Optional[str],
                          hallucination_prevention: Optional[str],
                          strategy: AdaptationStrategy) -> str:
        """Build the final enhanced prompt"""
        
        parts = []
        
        # Add hallucination prevention first (most important)
        if hallucination_prevention:
            parts.append(hallucination_prevention)
            parts.append("")
        
        # Add reasoning assistance
        if reasoning_assistance:
            parts.append(reasoning_assistance)
            parts.append("")
        
        # Add the enhanced prompt
        parts.append(enhanced_prompt)
        
        # Add strategy-specific instructions
        if strategy == AdaptationStrategy.MAXIMAL:
            parts.append("")
            parts.append("🔍 MAXIMUM ASSISTANCE MODE:")
            parts.append("Take your time and think through each step carefully.")
            parts.append("If you're unsure about anything, please say so.")
            parts.append("It's better to be honest about uncertainty than to guess.")
        
        return "\n".join(parts)
    
    def analyze_response(self, 
                        model_id: str, 
                        original_response: str,
                        task_type: str = "general",
                        domain: str = "general") -> ResponseAnalysis:
        """Analyze model response for quality and issues"""
        
        logger.info(f"🔍 Analyzing response from {model_id}")
        
        # Get model profile
        profile = self.context_system.get_model_profile(model_id)
        if not profile:
            profile = self.context_system.model_profiles["llama3.2:3b"]
        
        # Detect hallucinations
        hallucination_result = self.hallucination_system.detect_hallucinations(original_response)
        
        # Assess reasoning quality
        reasoning_quality = self._assess_reasoning_quality(original_response, task_type)
        
        # Assess factual accuracy
        factual_accuracy = self.hallucination_system.validate_factual_accuracy(original_response, domain)
        
        # Calculate overall confidence score
        confidence_score = (
            hallucination_result.confidence_score * 0.4 +
            reasoning_quality * 0.3 +
            factual_accuracy * 0.3
        )
        
        # Generate improvement suggestions
        improvement_suggestions = self._generate_improvement_suggestions(
            original_response, profile, hallucination_result, reasoning_quality, factual_accuracy
        )
        
        # Enhance response if needed
        enhanced_response = original_response
        if profile.needs_hallucination_prevention and hallucination_result.has_hallucination:
            enhanced_response = self.hallucination_system.enhance_response_for_smaller_models(
                original_response, profile.capability.value
            )
        
        # Determine if verification is needed
        verification_needed = (
            hallucination_result.has_hallucination or
            confidence_score < 0.7 or
            reasoning_quality < 0.6 or
            factual_accuracy < 0.7
        )
        
        return ResponseAnalysis(
            original_response=original_response,
            enhanced_response=enhanced_response,
            hallucination_detected=hallucination_result.has_hallucination,
            confidence_score=confidence_score,
            reasoning_quality=reasoning_quality,
            factual_accuracy=factual_accuracy,
            improvement_suggestions=improvement_suggestions,
            verification_needed=verification_needed
        )
    
    def _assess_reasoning_quality(self, response: str, task_type: str) -> float:
        """Assess the quality of reasoning in a response"""
        
        # Map task type to reasoning domain
        reasoning_domain = self._map_task_to_reasoning_domain(task_type)
        
        # Use reasoning system to assess quality
        result = self.reasoning_system.structure_reasoning_process(response, reasoning_domain)
        
        return result.confidence_score
    
    def _generate_improvement_suggestions(self, 
                                        response: str,
                                        profile,
                                        hallucination_result,
                                        reasoning_quality: float,
                                        factual_accuracy: float) -> List[str]:
        """Generate improvement suggestions for a response"""
        
        suggestions = []
        
        # Hallucination-related suggestions
        if hallucination_result.has_hallucination:
            suggestions.extend(hallucination_result.mitigation_suggestions[:2])
        
        # Reasoning quality suggestions
        if reasoning_quality < 0.6:
            suggestions.append("Add more structured reasoning steps")
            suggestions.append("Break down complex problems into smaller parts")
        
        # Factual accuracy suggestions
        if factual_accuracy < 0.7:
            suggestions.append("Verify factual claims with reliable sources")
            suggestions.append("Add confidence qualifiers to uncertain statements")
        
        # Model-specific suggestions
        if profile.needs_reasoning_assistance and reasoning_quality < 0.7:
            suggestions.append("Use the provided reasoning framework")
            suggestions.append("Follow the step-by-step approach")
        
        if profile.needs_hallucination_prevention and hallucination_result.has_hallucination:
            suggestions.append("Be more cautious about uncertain information")
            suggestions.append("Clearly state when you're not sure about something")
        
        return suggestions[:5]  # Limit to 5 suggestions
    
    def get_model_performance_summary(self, model_id: str) -> Dict[str, Any]:
        """Get performance summary for a specific model"""
        
        profile = self.context_system.get_model_profile(model_id)
        if not profile:
            return {"error": "Model not found"}
        
        return {
            "model_id": model_id,
            "capability": profile.capability.value,
            "parameter_count": profile.parameter_count,
            "reasoning_level": profile.reasoning_level.value,
            "hallucination_risk": profile.hallucination_risk,
            "context_window": profile.context_window,
            "strengths": profile.strengths,
            "weaknesses": profile.weaknesses,
            "needs_assistance": {
                "reasoning": profile.needs_reasoning_assistance,
                "knowledge_injection": profile.needs_knowledge_injection,
                "hallucination_prevention": profile.needs_hallucination_prevention
            },
            "recommended_tasks": profile.strengths,
            "avoid_tasks": profile.weaknesses,
            "optimal_prompt_length": profile.optimal_prompt_length
        }
    
    def recommend_best_model(self, task_type: str, requirements: Dict[str, Any]) -> List[str]:
        """Recommend the best model for a specific task"""
        
        # Get model recommendations from context system
        recommendations = self.context_system.get_model_recommendations(task_type)
        
        # Filter based on requirements
        filtered_models = []
        
        for model_id in recommendations["best_models"] + recommendations["good_models"]:
            profile = self.context_system.get_model_profile(model_id)
            if not profile:
                continue
            
            # Check if model meets requirements
            meets_requirements = True
            
            if "max_hallucination_risk" in requirements:
                if profile.hallucination_risk > requirements["max_hallucination_risk"]:
                    meets_requirements = False
            
            if "min_reasoning_level" in requirements:
                reasoning_levels = {
                    ReasoningLevel.BASIC: 1,
                    ReasoningLevel.INTERMEDIATE: 2,
                    ReasoningLevel.ADVANCED: 3,
                    ReasoningLevel.EXPERT: 4
                }
                if reasoning_levels.get(profile.reasoning_level, 0) < requirements["min_reasoning_level"]:
                    meets_requirements = False
            
            if meets_requirements:
                filtered_models.append(model_id)
        
        return filtered_models

# Example usage and testing
def test_integrated_system():
    """Test the integrated model adaptation system"""
    logger.info("🧪 Testing Integrated Model Adaptation System")
    
    system = IntegratedModelAdaptationSystem()
    
    # Test different models and tasks
    test_cases = [
        ("llama3.2:3b", "Write a Python function to sort a list", "programming"),
        ("mistral:7b", "Solve the equation 2x + 5 = 13", "mathematics"),
        ("llama3.1:8b", "Explain the concept of recursion", "general"),
        ("gpt-4-turbo", "Analyze the pros and cons of renewable energy", "analysis")
    ]
    
    for model_id, prompt, task_type in test_cases:
        logger.info(f"\n🎯 Testing {model_id} with {task_type}: {prompt}")
        
        # Adapt for model
        adaptation_result = system.adapt_for_model(model_id, prompt, task_type)
        
        logger.info(f"   Adaptation Strategy: {adaptation_result.adaptation_strategy.value}")
        logger.info(f"   Confidence Threshold: {adaptation_result.confidence_threshold}")
        logger.info(f"   Verification Required: {adaptation_result.verification_required}")
        logger.info(f"   Has Reasoning Assistance: {adaptation_result.reasoning_assistance is not None}")
        logger.info(f"   Has Hallucination Prevention: {adaptation_result.hallucination_prevention is not None}")
        
        # Simulate a response and analyze it
        mock_response = "I think this might work, but I'm not sure about the details..."
        analysis = system.analyze_response(model_id, mock_response, task_type)
        
        logger.info(f"   Response Analysis:")
        logger.info(f"     Hallucination Detected: {analysis.hallucination_detected}")
        logger.info(f"     Confidence Score: {analysis.confidence_score:.2f}")
        logger.info(f"     Reasoning Quality: {analysis.reasoning_quality:.2f}")
        logger.info(f"     Factual Accuracy: {analysis.factual_accuracy:.2f}")
        logger.info(f"     Verification Needed: {analysis.verification_needed}")
    
    # Test model recommendations
    recommendations = system.recommend_best_model("programming", {
        "max_hallucination_risk": 0.5,
        "min_reasoning_level": 2
    })
    logger.info(f"\n📊 Best models for programming: {recommendations}")
    
    return system

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    system = test_integrated_system()
