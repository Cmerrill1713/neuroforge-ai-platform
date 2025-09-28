"""
Model Adaptation System
Provides adaptive context, hallucination detection, and reasoning assistance for different model capabilities
"""

from .adaptive_model_context import (
    AdaptiveModelContextSystem,
    ModelCapability,
    ReasoningLevel,
    ModelProfile,
    ContextualInformation,
    ResponseEnhancement
)

from .hallucination_detection import (
    HallucinationDetectionSystem,
    HallucinationType,
    ConfidenceLevel,
    HallucinationPattern,
    HallucinationDetection,
    ResponseValidation
)

from .reasoning_assistance import (
    ReasoningAssistanceSystem,
    ReasoningDomain,
    ReasoningStep,
    ReasoningFramework,
    ReasoningAssistance,
    ReasoningResult
)

from .integrated_adaptation import (
    IntegratedModelAdaptationSystem,
    AdaptationStrategy,
    ModelAdaptationResult,
    ResponseAnalysis
)

__all__ = [
    # Adaptive Model Context
    "AdaptiveModelContextSystem",
    "ModelCapability",
    "ReasoningLevel",
    "ModelProfile",
    "ContextualInformation",
    "ResponseEnhancement",
    
    # Hallucination Detection
    "HallucinationDetectionSystem",
    "HallucinationType",
    "ConfidenceLevel",
    "HallucinationPattern",
    "HallucinationDetection",
    "ResponseValidation",
    
    # Reasoning Assistance
    "ReasoningAssistanceSystem",
    "ReasoningDomain",
    "ReasoningStep",
    "ReasoningFramework",
    "ReasoningAssistance",
    "ReasoningResult",
    
    # Integrated System
    "IntegratedModelAdaptationSystem",
    "AdaptationStrategy",
    "ModelAdaptationResult",
    "ResponseAnalysis"
]
