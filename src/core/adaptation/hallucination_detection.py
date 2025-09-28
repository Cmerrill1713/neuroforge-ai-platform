#!/usr/bin/env python3
"""
Hallucination Detection and Prevention System
Detects and prevents hallucinations in smaller model responses
"""

import re
import json
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

logger = logging.getLogger(__name__)

class HallucinationType(str, Enum):
    """Types of hallucinations"""
    FACTUAL_ERROR = "factual_error"
    LOGICAL_INCONSISTENCY = "logical_inconsistency"
    SPECULATION = "speculation"
    CONFIDENCE_OVERSTATEMENT = "confidence_overstatement"
    KNOWLEDGE_GAP_FILLING = "knowledge_gap_filling"
    TEMPORAL_ERROR = "temporal_error"
    CAUSAL_ERROR = "causal_error"

class ConfidenceLevel(str, Enum):
    """Confidence levels for responses"""
    VERY_HIGH = "very_high"    # 0.9-1.0
    HIGH = "high"              # 0.7-0.9
    MEDIUM = "medium"          # 0.5-0.7
    LOW = "low"                # 0.3-0.5
    VERY_LOW = "very_low"      # 0.0-0.3

@dataclass
class HallucinationPattern:
    """Pattern that indicates potential hallucination"""
    pattern_type: HallucinationType
    regex_pattern: str
    severity: float  # 0-1 scale
    description: str
    mitigation_strategy: str

@dataclass
class HallucinationDetection:
    """Result of hallucination detection"""
    has_hallucination: bool
    detected_patterns: List[HallucinationPattern]
    confidence_score: float
    risk_level: str
    recommendations: List[str]
    mitigation_suggestions: List[str]

@dataclass
class ResponseValidation:
    """Complete response validation result"""
    original_response: str
    hallucination_detection: HallucinationDetection
    factual_accuracy: float
    logical_consistency: float
    confidence_assessment: ConfidenceLevel
    verification_needed: bool
    suggested_corrections: List[str]

class HallucinationDetectionSystem:
    """
    System for detecting and preventing hallucinations in model responses
    """
    
    def __init__(self):
        self.hallucination_patterns = self._initialize_hallucination_patterns()
        self.factual_databases = self._initialize_factual_databases()
        self.logical_validators = self._initialize_logical_validators()
        self.confidence_indicators = self._initialize_confidence_indicators()
        
        logger.info("🔍 Hallucination Detection System initialized")
    
    def _initialize_hallucination_patterns(self) -> List[HallucinationPattern]:
        """Initialize patterns that indicate potential hallucinations"""
        return [
            # Uncertainty patterns
            HallucinationPattern(
                pattern_type=HallucinationType.SPECULATION,
                regex_pattern=r"(?:I think|I believe|I'm not sure|I don't know|I could be wrong)",
                severity=0.3,
                description="Uncertainty indicators",
                mitigation_strategy="Request clarification or admit uncertainty"
            ),
            
            # Overconfidence patterns
            HallucinationPattern(
                pattern_type=HallucinationType.CONFIDENCE_OVERSTATEMENT,
                regex_pattern=r"(?:I'm certain|definitely|absolutely|without a doubt|I know for sure)",
                severity=0.4,
                description="Overconfidence indicators",
                mitigation_strategy="Add appropriate confidence qualifiers"
            ),
            
            # Knowledge gap filling
            HallucinationPattern(
                pattern_type=HallucinationType.KNOWLEDGE_GAP_FILLING,
                regex_pattern=r"(?:from what I remember|I heard that|someone told me|I read somewhere)",
                severity=0.6,
                description="Filling knowledge gaps with uncertain information",
                mitigation_strategy="Verify information or admit lack of knowledge"
            ),
            
            # Temporal errors
            HallucinationPattern(
                pattern_type=HallucinationType.TEMPORAL_ERROR,
                regex_pattern=r"(?:recently|last year|next month|in the future|yesterday)",
                severity=0.5,
                description="Temporal references that may be incorrect",
                mitigation_strategy="Verify temporal accuracy"
            ),
            
            # Causal errors
            HallucinationPattern(
                pattern_type=HallucinationType.CAUSAL_ERROR,
                regex_pattern=r"(?:because of|due to|caused by|leads to|results in)",
                severity=0.7,
                description="Causal relationships that may be incorrect",
                mitigation_strategy="Verify causal relationships"
            ),
            
            # Factual claims without evidence
            HallucinationPattern(
                pattern_type=HallucinationType.FACTUAL_ERROR,
                regex_pattern=r"(?:the fact is|it's a fact that|scientifically proven|research shows)",
                severity=0.8,
                description="Strong factual claims without evidence",
                mitigation_strategy="Provide evidence or qualify the claim"
            ),
            
            # Logical inconsistencies
            HallucinationPattern(
                pattern_type=HallucinationType.LOGICAL_INCONSISTENCY,
                regex_pattern=r"(?:but also|however|on the other hand|contradicts|opposite)",
                severity=0.6,
                description="Potential logical inconsistencies",
                mitigation_strategy="Resolve contradictions or clarify reasoning"
            )
        ]
    
    def _initialize_factual_databases(self) -> Dict[str, List[str]]:
        """Initialize databases for factual verification"""
        return {
            "common_facts": [
                "The Earth orbits the Sun",
                "Water boils at 100°C at sea level",
                "The human body has 206 bones",
                "Light travels at approximately 299,792,458 m/s",
                "The periodic table has 118 known elements"
            ],
            "programming_facts": [
                "Python uses indentation for code blocks",
                "JavaScript is case-sensitive",
                "SQL uses SELECT to query data",
                "HTTP status 200 means success",
                "Git tracks changes in files"
            ],
            "math_facts": [
                "The sum of angles in a triangle is 180°",
                "The area of a circle is π × r²",
                "The derivative of x² is 2x",
                "The square root of 4 is 2",
                "Prime numbers have exactly two divisors"
            ]
        }
    
    def _initialize_logical_validators(self) -> List[str]:
        """Initialize logical validation rules"""
        return [
            "If A implies B, and B implies C, then A implies C",
            "If all X are Y, and some Z are X, then some Z are Y",
            "A statement and its negation cannot both be true",
            "If P is true, then not(not P) is true",
            "If P implies Q, and P is true, then Q is true"
        ]
    
    def _initialize_confidence_indicators(self) -> Dict[str, List[str]]:
        """Initialize confidence level indicators"""
        return {
            "very_high": ["I'm certain", "definitely", "absolutely", "without a doubt"],
            "high": ["I'm confident", "I believe", "likely", "probably"],
            "medium": ["I think", "possibly", "might", "could be"],
            "low": ["I'm not sure", "uncertain", "maybe", "perhaps"],
            "very_low": ["I don't know", "I have no idea", "I'm clueless", "no clue"]
        }
    
    def detect_hallucinations(self, response: str, context: str = "") -> HallucinationDetection:
        """Detect potential hallucinations in a response"""
        
        logger.info(f"🔍 Analyzing response for hallucinations")
        
        detected_patterns = []
        total_severity = 0.0
        
        # Check against hallucination patterns
        for pattern in self.hallucination_patterns:
            if re.search(pattern.regex_pattern, response, re.IGNORECASE):
                detected_patterns.append(pattern)
                total_severity += pattern.severity
                logger.debug(f"   Detected pattern: {pattern.description}")
        
        # Calculate confidence score
        confidence_score = max(0.0, 1.0 - (total_severity / len(self.hallucination_patterns)))
        
        # Determine risk level
        if total_severity > 0.7:
            risk_level = "high"
        elif total_severity > 0.4:
            risk_level = "medium"
        elif total_severity > 0.1:
            risk_level = "low"
        else:
            risk_level = "minimal"
        
        # Generate recommendations
        recommendations = self._generate_recommendations(detected_patterns, risk_level)
        
        # Generate mitigation suggestions
        mitigation_suggestions = self._generate_mitigation_suggestions(detected_patterns)
        
        return HallucinationDetection(
            has_hallucination=len(detected_patterns) > 0,
            detected_patterns=detected_patterns,
            confidence_score=confidence_score,
            risk_level=risk_level,
            recommendations=recommendations,
            mitigation_suggestions=mitigation_suggestions
        )
    
    def _generate_recommendations(self, 
                                detected_patterns: List[HallucinationPattern], 
                                risk_level: str) -> List[str]:
        """Generate recommendations based on detected patterns"""
        
        recommendations = []
        
        if risk_level == "high":
            recommendations.extend([
                "High hallucination risk detected - verify all factual claims",
                "Consider using a larger, more reliable model",
                "Request human verification before using this response",
                "Break down the response into smaller, verifiable parts"
            ])
        elif risk_level == "medium":
            recommendations.extend([
                "Medium hallucination risk - verify key claims",
                "Add confidence qualifiers to uncertain statements",
                "Consider providing sources for factual claims",
                "Review logical consistency of the response"
            ])
        elif risk_level == "low":
            recommendations.extend([
                "Low hallucination risk - minor verification recommended",
                "Add appropriate uncertainty qualifiers",
                "Consider providing additional context"
            ])
        
        # Add specific recommendations based on detected patterns
        pattern_types = [p.pattern_type for p in detected_patterns]
        
        if HallucinationType.SPECULATION in pattern_types:
            recommendations.append("Replace speculation with verified information")
        
        if HallucinationType.CONFIDENCE_OVERSTATEMENT in pattern_types:
            recommendations.append("Reduce confidence claims to appropriate levels")
        
        if HallucinationType.FACTUAL_ERROR in pattern_types:
            recommendations.append("Verify all factual claims with reliable sources")
        
        if HallucinationType.LOGICAL_INCONSISTENCY in pattern_types:
            recommendations.append("Resolve logical contradictions in the response")
        
        return recommendations
    
    def _generate_mitigation_suggestions(self, 
                                       detected_patterns: List[HallucinationPattern]) -> List[str]:
        """Generate mitigation suggestions for detected patterns"""
        
        suggestions = []
        
        for pattern in detected_patterns:
            suggestions.append(pattern.mitigation_strategy)
        
        # Add general mitigation strategies
        if len(detected_patterns) > 0:
            suggestions.extend([
                "Add 'I'm not certain about this' to uncertain statements",
                "Provide sources for factual claims",
                "Use 'to the best of my knowledge' for uncertain information",
                "Break complex claims into smaller, verifiable parts"
            ])
        
        return suggestions
    
    def assess_confidence_level(self, response: str) -> ConfidenceLevel:
        """Assess the confidence level expressed in a response"""
        
        confidence_scores = {}
        
        for level, indicators in self.confidence_indicators.items():
            score = 0
            for indicator in indicators:
                score += response.lower().count(indicator.lower())
            confidence_scores[level] = score
        
        # Find the level with highest score
        max_level = max(confidence_scores, key=confidence_scores.get)
        max_score = confidence_scores[max_level]
        
        # If no indicators found, assess based on language patterns
        if max_score == 0:
            if any(word in response.lower() for word in ["definitely", "certainly", "absolutely"]):
                return ConfidenceLevel.VERY_HIGH
            elif any(word in response.lower() for word in ["probably", "likely", "confident"]):
                return ConfidenceLevel.HIGH
            elif any(word in response.lower() for word in ["think", "believe", "might"]):
                return ConfidenceLevel.MEDIUM
            elif any(word in response.lower() for word in ["not sure", "uncertain", "maybe"]):
                return ConfidenceLevel.LOW
            else:
                return ConfidenceLevel.MEDIUM  # Default
        
        return ConfidenceLevel(max_level)
    
    def validate_factual_accuracy(self, response: str, domain: str = "general") -> float:
        """Validate factual accuracy of response"""
        
        if domain not in self.factual_databases:
            domain = "common_facts"
        
        facts = self.factual_databases[domain]
        response_lower = response.lower()
        
        # Check for factual claims
        factual_claims = []
        for fact in facts:
            if any(word in response_lower for word in fact.lower().split()):
                factual_claims.append(fact)
        
        # Simple accuracy score based on known facts
        if len(factual_claims) == 0:
            return 0.5  # Neutral if no verifiable facts found
        
        # This is a simplified version - in production, you'd use more sophisticated fact-checking
        accuracy_score = min(1.0, len(factual_claims) / 5.0)
        
        return accuracy_score
    
    def validate_logical_consistency(self, response: str) -> float:
        """Validate logical consistency of response"""
        
        # Check for contradictory statements
        contradictions = [
            ("always", "never"),
            ("all", "none"),
            ("every", "no"),
            ("true", "false"),
            ("yes", "no")
        ]
        
        response_lower = response.lower()
        contradiction_count = 0
        
        for pos, neg in contradictions:
            if pos in response_lower and neg in response_lower:
                contradiction_count += 1
        
        # Calculate consistency score
        consistency_score = max(0.0, 1.0 - (contradiction_count * 0.2))
        
        return consistency_score
    
    def validate_response(self, 
                         response: str, 
                         context: str = "", 
                         domain: str = "general") -> ResponseValidation:
        """Comprehensive response validation"""
        
        logger.info(f"🔍 Validating response for hallucinations and accuracy")
        
        # Detect hallucinations
        hallucination_detection = self.detect_hallucinations(response, context)
        
        # Assess factual accuracy
        factual_accuracy = self.validate_factual_accuracy(response, domain)
        
        # Assess logical consistency
        logical_consistency = self.validate_logical_consistency(response)
        
        # Assess confidence level
        confidence_assessment = self.assess_confidence_level(response)
        
        # Determine if verification is needed
        verification_needed = (
            hallucination_detection.has_hallucination or
            factual_accuracy < 0.7 or
            logical_consistency < 0.7 or
            confidence_assessment in [ConfidenceLevel.LOW, ConfidenceLevel.VERY_LOW]
        )
        
        # Generate suggested corrections
        suggested_corrections = []
        
        if hallucination_detection.has_hallucination:
            suggested_corrections.extend(hallucination_detection.mitigation_suggestions)
        
        if factual_accuracy < 0.7:
            suggested_corrections.append("Verify factual claims with reliable sources")
        
        if logical_consistency < 0.7:
            suggested_corrections.append("Resolve logical contradictions")
        
        if confidence_assessment in [ConfidenceLevel.LOW, ConfidenceLevel.VERY_LOW]:
            suggested_corrections.append("Add appropriate confidence qualifiers")
        
        return ResponseValidation(
            original_response=response,
            hallucination_detection=hallucination_detection,
            factual_accuracy=factual_accuracy,
            logical_consistency=logical_consistency,
            confidence_assessment=confidence_assessment,
            verification_needed=verification_needed,
            suggested_corrections=suggested_corrections
        )
    
    def enhance_response_for_smaller_models(self, 
                                         response: str, 
                                         model_capability: str) -> str:
        """Enhance response to reduce hallucination risk for smaller models"""
        
        validation = self.validate_response(response)
        
        if not validation.verification_needed:
            return response
        
        enhanced_parts = []
        
        # Add confidence qualifiers
        if validation.confidence_assessment in [ConfidenceLevel.LOW, ConfidenceLevel.VERY_LOW]:
            enhanced_parts.append("⚠️ CONFIDENCE WARNING: This response has low confidence indicators.")
        
        # Add hallucination warnings
        if validation.hallucination_detection.has_hallucination:
            enhanced_parts.append("🚨 HALLUCINATION RISK: Potential hallucinations detected.")
            enhanced_parts.append("RECOMMENDATIONS:")
            for suggestion in validation.hallucination_detection.mitigation_suggestions[:3]:
                enhanced_parts.append(f"• {suggestion}")
        
        # Add factual accuracy warnings
        if validation.factual_accuracy < 0.7:
            enhanced_parts.append("📚 FACTUAL ACCURACY: Some claims may need verification.")
        
        # Add logical consistency warnings
        if validation.logical_consistency < 0.7:
            enhanced_parts.append("🧠 LOGICAL CONSISTENCY: Some contradictions detected.")
        
        # Add the original response
        enhanced_parts.append("\nORIGINAL RESPONSE:")
        enhanced_parts.append(response)
        
        # Add verification request
        enhanced_parts.append("\n🔍 VERIFICATION RECOMMENDED:")
        enhanced_parts.append("Please verify the accuracy of this response before using it.")
        
        return "\n".join(enhanced_parts)

# Example usage and testing
def test_hallucination_detection():
    """Test the hallucination detection system"""
    logger.info("🧪 Testing Hallucination Detection System")
    
    system = HallucinationDetectionSystem()
    
    # Test responses with different hallucination patterns
    test_responses = [
        "I'm certain that the Earth is flat and this is scientifically proven.",
        "I think this might work, but I'm not sure about the details.",
        "From what I remember, Python was created in 1991 by Guido van Rossum.",
        "This function will definitely work because I heard it from someone.",
        "The sky is blue because of atmospheric scattering, but it's also red sometimes."
    ]
    
    for i, response in enumerate(test_responses, 1):
        logger.info(f"\n📝 Test Response {i}: {response}")
        
        validation = system.validate_response(response)
        
        logger.info(f"   Hallucination Detected: {validation.hallucination_detection.has_hallucination}")
        logger.info(f"   Risk Level: {validation.hallucination_detection.risk_level}")
        logger.info(f"   Confidence Score: {validation.hallucination_detection.confidence_score:.2f}")
        logger.info(f"   Factual Accuracy: {validation.factual_accuracy:.2f}")
        logger.info(f"   Logical Consistency: {validation.logical_consistency:.2f}")
        logger.info(f"   Confidence Assessment: {validation.confidence_assessment.value}")
        logger.info(f"   Verification Needed: {validation.verification_needed}")
        
        if validation.suggested_corrections:
            logger.info(f"   Suggested Corrections:")
            for correction in validation.suggested_corrections[:2]:
                logger.info(f"     • {correction}")
    
    return system

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    system = test_hallucination_detection()
