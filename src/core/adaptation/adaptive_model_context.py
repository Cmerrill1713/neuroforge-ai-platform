#!/usr/bin/env python3
"""
Adaptive Model Context System
Provides appropriate context and assistance based on model capabilities
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

class ModelCapability(str, Enum):
    """Model capability levels"""
    TINY = "tiny"        # < 3B parameters - Limited reasoning, high hallucination risk
    SMALL = "small"      # 3-7B parameters - Basic reasoning, moderate hallucination risk
    MEDIUM = "medium"    # 7-13B parameters - Good reasoning, low hallucination risk
    LARGE = "large"      # 13-70B parameters - Excellent reasoning, minimal hallucination risk
    XLARGE = "xlarge"    # > 70B parameters - Superior reasoning, very low hallucination risk

class ReasoningLevel(str, Enum):
    """Reasoning assistance levels"""
    BASIC = "basic"           # Simple step-by-step
    INTERMEDIATE = "intermediate"  # Structured reasoning
    ADVANCED = "advanced"     # Complex multi-step reasoning
    EXPERT = "expert"         # Sophisticated logical analysis

@dataclass
class ModelProfile:
    """Profile defining model capabilities and requirements"""
    model_id: str
    capability: ModelCapability
    parameter_count: int
    reasoning_level: ReasoningLevel
    hallucination_risk: float  # 0-1 scale
    context_window: int
    strengths: List[str]
    weaknesses: List[str]
    optimal_prompt_length: int
    needs_reasoning_assistance: bool
    needs_knowledge_injection: bool
    needs_hallucination_prevention: bool

@dataclass
class ContextualInformation:
    """Information provided to assist model responses"""
    facts: List[str]
    examples: List[str]
    reasoning_steps: List[str]
    constraints: List[str]
    verification_points: List[str]
    confidence_indicators: List[str]

@dataclass
class ResponseEnhancement:
    """Enhancement applied to improve model responses"""
    enhanced_prompt: str
    context_injection: ContextualInformation
    reasoning_framework: Optional[str]
    verification_checks: List[str]
    confidence_threshold: float
    fallback_strategy: str

class AdaptiveModelContextSystem:
    """
    System that adapts context and assistance based on model capabilities
    """
    
    def __init__(self):
        self.model_profiles = self._initialize_model_profiles()
        self.knowledge_base = self._initialize_knowledge_base()
        self.reasoning_templates = self._initialize_reasoning_templates()
        self.hallucination_patterns = self._initialize_hallucination_patterns()
        
        logger.info("🧠 Adaptive Model Context System initialized")
    
    def _initialize_model_profiles(self) -> Dict[str, ModelProfile]:
        """Initialize profiles for different model sizes"""
        return {
            # Tiny models (< 3B)
            "llama3.2:3b": ModelProfile(
                model_id="llama3.2:3b",
                capability=ModelCapability.TINY,
                parameter_count=3_000_000_000,
                reasoning_level=ReasoningLevel.BASIC,
                hallucination_risk=0.8,
                context_window=8192,
                strengths=["fast", "efficient", "lightweight"],
                weaknesses=["reasoning", "factual_accuracy", "complex_tasks"],
                optimal_prompt_length=500,
                needs_reasoning_assistance=True,
                needs_knowledge_injection=True,
                needs_hallucination_prevention=True
            ),
            "phi3:3.8b": ModelProfile(
                model_id="phi3:3.8b",
                capability=ModelCapability.TINY,
                parameter_count=3_800_000_000,
                reasoning_level=ReasoningLevel.BASIC,
                hallucination_risk=0.75,
                context_window=128000,
                strengths=["code", "math", "reasoning"],
                weaknesses=["general_knowledge", "creative_tasks"],
                optimal_prompt_length=800,
                needs_reasoning_assistance=True,
                needs_knowledge_injection=True,
                needs_hallucination_prevention=True
            ),
            
            # Small models (3-7B)
            "mistral:7b": ModelProfile(
                model_id="mistral:7b",
                capability=ModelCapability.SMALL,
                parameter_count=7_000_000_000,
                reasoning_level=ReasoningLevel.INTERMEDIATE,
                hallucination_risk=0.6,
                context_window=32768,
                strengths=["coding", "reasoning", "instruction_following"],
                weaknesses=["creative_writing", "complex_reasoning"],
                optimal_prompt_length=1000,
                needs_reasoning_assistance=True,
                needs_knowledge_injection=True,
                needs_hallucination_prevention=True
            ),
            "qwen2.5:7b": ModelProfile(
                model_id="qwen2.5:7b",
                capability=ModelCapability.SMALL,
                parameter_count=7_000_000_000,
                reasoning_level=ReasoningLevel.INTERMEDIATE,
                hallucination_risk=0.55,
                context_window=32768,
                strengths=["multilingual", "reasoning", "math"],
                weaknesses=["creative_tasks", "domain_specific"],
                optimal_prompt_length=1200,
                needs_reasoning_assistance=True,
                needs_knowledge_injection=True,
                needs_hallucination_prevention=True
            ),
            
            # Medium models (7-13B)
            "llama3.1:8b": ModelProfile(
                model_id="llama3.1:8b",
                capability=ModelCapability.MEDIUM,
                parameter_count=8_000_000_000,
                reasoning_level=ReasoningLevel.ADVANCED,
                hallucination_risk=0.4,
                context_window=128000,
                strengths=["reasoning", "coding", "math", "general_knowledge"],
                weaknesses=["creative_writing", "specialized_domains"],
                optimal_prompt_length=2000,
                needs_reasoning_assistance=False,
                needs_knowledge_injection=True,
                needs_hallucination_prevention=True
            ),
            "llama-13b": ModelProfile(
                model_id="llama-13b",
                capability=ModelCapability.MEDIUM,
                parameter_count=13_000_000_000,
                reasoning_level=ReasoningLevel.ADVANCED,
                hallucination_risk=0.35,
                context_window=4096,
                strengths=["general_knowledge", "reasoning", "conversation"],
                weaknesses=["coding", "math", "specialized_tasks"],
                optimal_prompt_length=2500,
                needs_reasoning_assistance=False,
                needs_knowledge_injection=True,
                needs_hallucination_prevention=True
            ),
            
            # Large models (13-70B)
            "gpt-4-turbo": ModelProfile(
                model_id="gpt-4-turbo",
                capability=ModelCapability.LARGE,
                parameter_count=70_000_000_000,
                reasoning_level=ReasoningLevel.EXPERT,
                hallucination_risk=0.2,
                context_window=128000,
                strengths=["reasoning", "coding", "math", "creative", "general"],
                weaknesses=["real_time_info", "specialized_domains"],
                optimal_prompt_length=4000,
                needs_reasoning_assistance=False,
                needs_knowledge_injection=False,
                needs_hallucination_prevention=False
            ),
            "claude-3-opus": ModelProfile(
                model_id="claude-3-opus",
                capability=ModelCapability.LARGE,
                parameter_count=70_000_000_000,
                reasoning_level=ReasoningLevel.EXPERT,
                hallucination_risk=0.15,
                context_window=200000,
                strengths=["reasoning", "analysis", "writing", "coding"],
                weaknesses=["real_time_info", "math"],
                optimal_prompt_length=5000,
                needs_reasoning_assistance=False,
                needs_knowledge_injection=False,
                needs_hallucination_prevention=False
            ),
        }
    
    def _initialize_knowledge_base(self) -> Dict[str, List[str]]:
        """Initialize knowledge base for injection into smaller models"""
        return {
            "general_facts": [
                "The Earth is approximately 4.5 billion years old",
                "Water boils at 100°C (212°F) at sea level",
                "The human body has 206 bones",
                "Light travels at approximately 299,792,458 meters per second",
                "The periodic table has 118 known elements"
            ],
            "programming_concepts": [
                "Variables store data in memory",
                "Functions are reusable blocks of code",
                "Loops repeat code execution",
                "Conditionals execute code based on conditions",
                "Arrays store multiple values in sequence"
            ],
            "math_concepts": [
                "Addition combines numbers",
                "Subtraction finds the difference",
                "Multiplication repeats addition",
                "Division splits into equal parts",
                "Exponents multiply a number by itself"
            ],
            "reasoning_patterns": [
                "Break complex problems into smaller parts",
                "Consider multiple perspectives",
                "Verify assumptions with evidence",
                "Look for patterns and relationships",
                "Test solutions systematically"
            ]
        }
    
    def _initialize_reasoning_templates(self) -> Dict[str, str]:
        """Initialize reasoning templates for different complexity levels"""
        return {
            "basic": """
Let's think through this step by step:

1. What is the problem asking?
2. What information do we have?
3. What do we need to find?
4. How can we solve this?
5. Let's check our answer.
""",
            "intermediate": """
Let me analyze this systematically:

**Problem Analysis:**
- Core question: {question}
- Given information: {given}
- Required output: {required}

**Approach:**
1. Identify the key concepts
2. Break down into manageable steps
3. Apply relevant principles
4. Verify the solution

**Solution:**
{step_by_step_solution}

**Verification:**
- Does this make logical sense?
- Are all requirements met?
- Can we double-check the answer?
""",
            "advanced": """
**Comprehensive Analysis Framework:**

**1. Problem Decomposition:**
- Primary objective: {objective}
- Constraints: {constraints}
- Assumptions: {assumptions}
- Success criteria: {criteria}

**2. Multi-Perspective Analysis:**
- Technical perspective: {technical_view}
- Logical perspective: {logical_view}
- Practical perspective: {practical_view}

**3. Solution Architecture:**
- Core approach: {approach}
- Supporting methods: {methods}
- Risk mitigation: {risks}

**4. Implementation Strategy:**
- Phase 1: {phase1}
- Phase 2: {phase2}
- Phase 3: {phase3}

**5. Validation & Testing:**
- Unit tests: {unit_tests}
- Integration tests: {integration_tests}
- Edge cases: {edge_cases}
"""
        }
    
    def _initialize_hallucination_patterns(self) -> List[str]:
        """Initialize patterns that indicate potential hallucinations"""
        return [
            "I'm not sure, but I think...",
            "I believe this might be...",
            "From what I remember...",
            "I think I heard that...",
            "It's possible that...",
            "I'm not certain, but...",
            "This might be wrong, but...",
            "I could be mistaken, but...",
            "I'm not an expert, but...",
            "I don't have the exact details, but..."
        ]
    
    def get_model_profile(self, model_id: str) -> Optional[ModelProfile]:
        """Get profile for a specific model"""
        return self.model_profiles.get(model_id)
    
    def enhance_prompt_for_model(self, 
                               model_id: str, 
                               original_prompt: str, 
                               task_type: str = "general") -> ResponseEnhancement:
        """Enhance prompt based on model capabilities"""
        
        profile = self.get_model_profile(model_id)
        if not profile:
            logger.warning(f"Unknown model: {model_id}, using default enhancement")
            profile = self.model_profiles["llama3.2:3b"]  # Default to tiny model
        
        logger.info(f"🎯 Enhancing prompt for {model_id} ({profile.capability.value})")
        
        # Build contextual information
        context_info = self._build_contextual_information(profile, task_type)
        
        # Build enhanced prompt
        enhanced_prompt = self._build_enhanced_prompt(original_prompt, profile, context_info, task_type)
        
        # Build verification checks
        verification_checks = self._build_verification_checks(profile, task_type)
        
        # Determine confidence threshold
        confidence_threshold = self._calculate_confidence_threshold(profile)
        
        # Determine fallback strategy
        fallback_strategy = self._determine_fallback_strategy(profile)
        
        return ResponseEnhancement(
            enhanced_prompt=enhanced_prompt,
            context_injection=context_info,
            reasoning_framework=self.reasoning_templates.get(profile.reasoning_level.value),
            verification_checks=verification_checks,
            confidence_threshold=confidence_threshold,
            fallback_strategy=fallback_strategy
        )
    
    def _build_contextual_information(self, 
                                    profile: ModelProfile, 
                                    task_type: str) -> ContextualInformation:
        """Build contextual information based on model needs"""
        
        facts = []
        examples = []
        reasoning_steps = []
        constraints = []
        verification_points = []
        confidence_indicators = []
        
        # Add knowledge injection for smaller models
        if profile.needs_knowledge_injection:
            if task_type in ["programming", "coding"]:
                facts.extend(self.knowledge_base["programming_concepts"])
            elif task_type in ["math", "mathematics"]:
                facts.extend(self.knowledge_base["math_concepts"])
            else:
                facts.extend(self.knowledge_base["general_facts"])
        
        # Add reasoning assistance for smaller models
        if profile.needs_reasoning_assistance:
            reasoning_steps.extend(self.knowledge_base["reasoning_patterns"])
            
            # Add specific examples based on task type
            if task_type == "programming":
                examples.extend([
                    "Example: To sort a list, compare elements and swap if needed",
                    "Example: To find maximum, keep track of largest value seen",
                    "Example: To validate input, check format and range"
                ])
            elif task_type == "math":
                examples.extend([
                    "Example: To solve 2x + 5 = 13, subtract 5 then divide by 2",
                    "Example: To find area of rectangle, multiply length by width",
                    "Example: To convert units, multiply by conversion factor"
                ])
        
        # Add constraints for hallucination prevention
        if profile.needs_hallucination_prevention:
            constraints.extend([
                "Only provide information you are confident about",
                "If uncertain, clearly state your uncertainty",
                "Avoid speculation beyond the given information",
                "Cite specific sources when possible"
            ])
        
        # Add verification points
        verification_points.extend([
            "Does this answer make logical sense?",
            "Are all steps clearly explained?",
            "Is the solution complete and correct?",
            "Can this be verified independently?"
        ])
        
        # Add confidence indicators
        confidence_indicators.extend([
            "High confidence: I'm certain this is correct",
            "Medium confidence: This is likely correct",
            "Low confidence: I'm not sure about this",
            "No confidence: I don't know the answer"
        ])
        
        return ContextualInformation(
            facts=facts,
            examples=examples,
            reasoning_steps=reasoning_steps,
            constraints=constraints,
            verification_points=verification_points,
            confidence_indicators=confidence_indicators
        )
    
    def _build_enhanced_prompt(self, 
                             original_prompt: str, 
                             profile: ModelProfile, 
                             context: ContextualInformation,
                             task_type: str) -> str:
        """Build enhanced prompt with appropriate context"""
        
        enhanced_parts = []
        
        # Add reasoning framework for smaller models
        if profile.needs_reasoning_assistance and profile.reasoning_level != ReasoningLevel.EXPERT:
            reasoning_template = self.reasoning_templates.get(profile.reasoning_level.value, "")
            if reasoning_template:
                enhanced_parts.append("REASONING FRAMEWORK:")
                enhanced_parts.append(reasoning_template)
                enhanced_parts.append("")
        
        # Add contextual facts
        if context.facts:
            enhanced_parts.append("RELEVANT FACTS:")
            for fact in context.facts[:5]:  # Limit to 5 facts
                enhanced_parts.append(f"• {fact}")
            enhanced_parts.append("")
        
        # Add examples
        if context.examples:
            enhanced_parts.append("EXAMPLES:")
            for example in context.examples[:3]:  # Limit to 3 examples
                enhanced_parts.append(f"• {example}")
            enhanced_parts.append("")
        
        # Add constraints for hallucination prevention
        if context.constraints:
            enhanced_parts.append("IMPORTANT CONSTRAINTS:")
            for constraint in context.constraints:
                enhanced_parts.append(f"• {constraint}")
            enhanced_parts.append("")
        
        # Add the original prompt
        enhanced_parts.append("TASK:")
        enhanced_parts.append(original_prompt)
        enhanced_parts.append("")
        
        # Add verification instructions
        if profile.needs_hallucination_prevention:
            enhanced_parts.append("VERIFICATION:")
            enhanced_parts.append("Before providing your final answer, please:")
            for point in context.verification_points[:3]:
                enhanced_parts.append(f"• {point}")
            enhanced_parts.append("")
        
        # Add confidence requirement
        if profile.capability in [ModelCapability.TINY, ModelCapability.SMALL]:
            enhanced_parts.append("CONFIDENCE LEVEL:")
            enhanced_parts.append("Please indicate your confidence level:")
            for indicator in context.confidence_indicators:
                enhanced_parts.append(f"• {indicator}")
        
        return "\n".join(enhanced_parts)
    
    def _build_verification_checks(self, profile: ModelProfile, task_type: str) -> List[str]:
        """Build verification checks based on model capabilities"""
        
        checks = []
        
        if profile.needs_hallucination_prevention:
            checks.extend([
                "Check for hallucination patterns",
                "Verify factual accuracy",
                "Ensure logical consistency",
                "Validate completeness"
            ])
        
        if profile.needs_reasoning_assistance:
            checks.extend([
                "Verify reasoning steps",
                "Check for logical gaps",
                "Ensure step-by-step clarity",
                "Validate conclusion"
            ])
        
        if task_type in ["programming", "coding"]:
            checks.extend([
                "Check syntax correctness",
                "Verify algorithm logic",
                "Test edge cases",
                "Validate input/output"
            ])
        
        return checks
    
    def _calculate_confidence_threshold(self, profile: ModelProfile) -> float:
        """Calculate confidence threshold based on model capabilities"""
        
        # Smaller models need higher confidence thresholds
        base_thresholds = {
            ModelCapability.TINY: 0.8,
            ModelCapability.SMALL: 0.7,
            ModelCapability.MEDIUM: 0.6,
            ModelCapability.LARGE: 0.5,
            ModelCapability.XLARGE: 0.4
        }
        
        return base_thresholds.get(profile.capability, 0.6)
    
    def _determine_fallback_strategy(self, profile: ModelProfile) -> str:
        """Determine fallback strategy for when model confidence is low"""
        
        if profile.capability in [ModelCapability.TINY, ModelCapability.SMALL]:
            return "request_human_assistance"
        elif profile.capability == ModelCapability.MEDIUM:
            return "provide_partial_answer_with_disclaimer"
        else:
            return "provide_best_effort_answer"
    
    def detect_hallucination_patterns(self, response: str) -> Dict[str, Any]:
        """Detect potential hallucination patterns in response"""
        
        detected_patterns = []
        confidence_score = 1.0
        
        for pattern in self.hallucination_patterns:
            if pattern.lower() in response.lower():
                detected_patterns.append(pattern)
                confidence_score -= 0.1
        
        # Additional checks
        uncertainty_indicators = [
            "might", "could", "possibly", "perhaps", "maybe",
            "I think", "I believe", "I'm not sure", "I don't know"
        ]
        
        uncertainty_count = sum(1 for indicator in uncertainty_indicators 
                               if indicator.lower() in response.lower())
        
        if uncertainty_count > 3:
            detected_patterns.append("high_uncertainty")
            confidence_score -= 0.2
        
        return {
            "has_hallucination_patterns": len(detected_patterns) > 0,
            "detected_patterns": detected_patterns,
            "confidence_score": max(0.0, confidence_score),
            "recommendation": "verify_response" if len(detected_patterns) > 0 else "response_appears_reliable"
        }
    
    def provide_reasoning_assistance(self, 
                                   model_id: str, 
                                   problem: str, 
                                   current_response: str) -> str:
        """Provide reasoning assistance for smaller models"""
        
        profile = self.get_model_profile(model_id)
        if not profile or not profile.needs_reasoning_assistance:
            return current_response
        
        # Analyze the problem and provide structured reasoning
        reasoning_assistance = f"""
REASONING ASSISTANCE FOR {model_id.upper()}:

Problem: {problem}

Current Response: {current_response}

STRUCTURED REASONING APPROACH:

1. PROBLEM BREAKDOWN:
   - What is the main question?
   - What information is given?
   - What needs to be found?

2. STEP-BY-STEP SOLUTION:
   - Identify the approach
   - Break into smaller steps
   - Apply relevant principles
   - Check each step

3. VERIFICATION:
   - Does the answer make sense?
   - Are all steps logical?
   - Can you verify the result?

Please revise your response using this structured approach.
"""
        
        return reasoning_assistance
    
    def get_model_recommendations(self, task_type: str) -> Dict[str, List[str]]:
        """Get model recommendations based on task type"""
        
        recommendations = {
            "best_models": [],
            "good_models": [],
            "avoid_models": []
        }
        
        for model_id, profile in self.model_profiles.items():
            if task_type in profile.strengths:
                if profile.capability in [ModelCapability.LARGE, ModelCapability.XLARGE]:
                    recommendations["best_models"].append(model_id)
                else:
                    recommendations["good_models"].append(model_id)
            elif task_type in profile.weaknesses:
                recommendations["avoid_models"].append(model_id)
        
        return recommendations

# Example usage and testing
def test_adaptive_system():
    """Test the adaptive model context system"""
    logger.info("🧪 Testing Adaptive Model Context System")
    
    system = AdaptiveModelContextSystem()
    
    # Test with different model sizes
    test_models = ["llama3.2:3b", "mistral:7b", "llama3.1:8b", "gpt-4-turbo"]
    test_prompt = "Write a Python function to sort a list of numbers"
    
    for model_id in test_models:
        logger.info(f"\n🎯 Testing with {model_id}")
        
        # Get enhancement
        enhancement = system.enhance_prompt_for_model(model_id, test_prompt, "programming")
        
        logger.info(f"   Capability: {system.get_model_profile(model_id).capability.value}")
        logger.info(f"   Reasoning Level: {system.get_model_profile(model_id).reasoning_level.value}")
        logger.info(f"   Hallucination Risk: {system.get_model_profile(model_id).hallucination_risk}")
        logger.info(f"   Needs Reasoning Assistance: {system.get_model_profile(model_id).needs_reasoning_assistance}")
        logger.info(f"   Needs Knowledge Injection: {system.get_model_profile(model_id).needs_knowledge_injection}")
        logger.info(f"   Confidence Threshold: {enhancement.confidence_threshold}")
        logger.info(f"   Fallback Strategy: {enhancement.fallback_strategy}")
        
        # Test hallucination detection
        test_response = "I think this function might work, but I'm not sure about the syntax..."
        hallucination_result = system.detect_hallucination_patterns(test_response)
        logger.info(f"   Hallucination Detection: {hallucination_result['has_hallucination_patterns']}")
        logger.info(f"   Confidence Score: {hallucination_result['confidence_score']}")
    
    # Test model recommendations
    recommendations = system.get_model_recommendations("programming")
    logger.info("\n📊 Programming Task Recommendations:")
    logger.info(f"   Best Models: {recommendations['best_models']}")
    logger.info(f"   Good Models: {recommendations['good_models']}")
    logger.info(f"   Avoid Models: {recommendations['avoid_models']}")
    
    return system

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    system = test_adaptive_system()
