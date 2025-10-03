#!/usr/bin/env python3
""'
Test script for the Integrated Model Adaptation System
""'

import sys
import os
import logging

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src'))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_adaptive_model_context():
    """TODO: Add docstring."""
    """Test the adaptive model context system""'
    logger.info("🧪 Testing Adaptive Model Context System')

    try:
        from core.adaptation.adaptive_model_context import AdaptiveModelContextSystem

        system = AdaptiveModelContextSystem()

        # Test with different model sizes
        test_models = ["llama3.2:3b", "mistral:7b", "llama3.1:8b", "gpt-4-turbo']
        test_prompt = "Write a Python function to sort a list of numbers'

        for model_id in test_models:
            logger.info(f"\n🎯 Testing with {model_id}')

            # Get enhancement
            enhancement = system.enhance_prompt_for_model(model_id, test_prompt, "programming')

            profile = system.get_model_profile(model_id)
            if profile:
                logger.info(f"   Capability: {profile.capability.value}')
                logger.info(f"   Reasoning Level: {profile.reasoning_level.value}')
                logger.info(f"   Hallucination Risk: {profile.hallucination_risk}')
                logger.info(f"   Needs Reasoning Assistance: {profile.needs_reasoning_assistance}')
                logger.info(f"   Needs Knowledge Injection: {profile.needs_knowledge_injection}')
                logger.info(f"   Confidence Threshold: {enhancement.confidence_threshold}')
                logger.info(f"   Fallback Strategy: {enhancement.fallback_strategy}')

        return True

    except Exception as e:
        logger.error(f"Error testing adaptive model context: {e}')
        return False

def test_hallucination_detection():
    """TODO: Add docstring."""
    """Test the hallucination detection system""'
    logger.info("🧪 Testing Hallucination Detection System')

    try:
        from core.adaptation.hallucination_detection import HallucinationDetectionSystem

        system = HallucinationDetectionSystem()

        # Test responses with different hallucination patterns
        test_responses = [
            "I"m certain that the Earth is flat and this is scientifically proven.',
            "I think this might work, but I"m not sure about the details.',
            "From what I remember, Python was created in 1991 by Guido van Rossum.',
            "This function will definitely work because I heard it from someone.',
            "The sky is blue because of atmospheric scattering, but it"s also red sometimes.'
        ]

        for i, response in enumerate(test_responses, 1):
            logger.info(f"\n📝 Test Response {i}: {response}')

            validation = system.validate_response(response)

            logger.info(f"   Hallucination Detected: {validation.hallucination_detection.has_hallucination}')
            logger.info(f"   Risk Level: {validation.hallucination_detection.risk_level}')
            logger.info(f"   Confidence Score: {validation.hallucination_detection.confidence_score:.2f}')
            logger.info(f"   Factual Accuracy: {validation.factual_accuracy:.2f}')
            logger.info(f"   Logical Consistency: {validation.logical_consistency:.2f}')
            logger.info(f"   Confidence Assessment: {validation.confidence_assessment.value}')
            logger.info(f"   Verification Needed: {validation.verification_needed}')

        return True

    except Exception as e:
        logger.error(f"Error testing hallucination detection: {e}')
        return False

def test_reasoning_assistance():
    """TODO: Add docstring."""
    """Test the reasoning assistance system""'
    logger.info("🧪 Testing Reasoning Assistance System')

    try:
        from core.adaptation.reasoning_assistance import ReasoningAssistanceSystem, ReasoningDomain

        system = ReasoningAssistanceSystem()

        # Test different domains
        test_problems = [
            ("Write a function to sort a list of numbers', ReasoningDomain.PROGRAMMING),
            ("Solve the equation 2x + 5 = 13', ReasoningDomain.MATHEMATICS),
            ("Prove that if A implies B and B implies C, then A implies C', ReasoningDomain.LOGIC),
            ("How would you organize a team project?', ReasoningDomain.PROBLEM_SOLVING)
        ]

        for problem, domain in test_problems:
            logger.info(f"\n🎯 Testing {domain.value}: {problem}')

            # Get reasoning assistance
            assistance = system.provide_reasoning_assistance(problem, domain)

            logger.info(f"   Framework Steps: {len(assistance.framework.steps)}')
            logger.info(f"   Examples Provided: {len(assistance.examples)}')
            logger.info(f"   Validation Questions: {len(assistance.validation_questions)}')
            logger.info(f"   Common Pitfalls: {len(assistance.common_pitfalls)}')

            # Structure the reasoning process
            result = system.structure_reasoning_process(problem, domain)

            logger.info(f"   Validation Passed: {result.validation_passed}')
            logger.info(f"   Confidence Score: {result.confidence_score:.2f}')
            logger.info(f"   Improvement Suggestions: {len(result.improvement_suggestions)}')

        return True

    except Exception as e:
        logger.error(f"Error testing reasoning assistance: {e}')
        return False

def test_integrated_system():
    """TODO: Add docstring."""
    """Test the integrated adaptation system""'
    logger.info("🧪 Testing Integrated Model Adaptation System')

    try:
        from core.adaptation.integrated_adaptation import IntegratedModelAdaptationSystem

        system = IntegratedModelAdaptationSystem()

        # Test different models and tasks
        test_cases = [
            ("llama3.2:3b", "Write a Python function to sort a list", "programming'),
            ("mistral:7b", "Solve the equation 2x + 5 = 13", "mathematics'),
            ("llama3.1:8b", "Explain the concept of recursion", "general'),
            ("gpt-4-turbo", "Analyze the pros and cons of renewable energy", "analysis')
        ]

        for model_id, prompt, task_type in test_cases:
            logger.info(f"\n🎯 Testing {model_id} with {task_type}: {prompt}')

            # Adapt for model
            adaptation_result = system.adapt_for_model(model_id, prompt, task_type)

            logger.info(f"   Adaptation Strategy: {adaptation_result.adaptation_strategy.value}')
            logger.info(f"   Confidence Threshold: {adaptation_result.confidence_threshold}')
            logger.info(f"   Verification Required: {adaptation_result.verification_required}')
            logger.info(f"   Has Reasoning Assistance: {adaptation_result.reasoning_assistance is not None}')
            logger.info(f"   Has Hallucination Prevention: {adaptation_result.hallucination_prevention is not None}')

            # Simulate a response and analyze it
            mock_response = "I think this might work, but I"m not sure about the details...'
            analysis = system.analyze_response(model_id, mock_response, task_type)

            logger.info(f"   Response Analysis:')
            logger.info(f"     Hallucination Detected: {analysis.hallucination_detected}')
            logger.info(f"     Confidence Score: {analysis.confidence_score:.2f}')
            logger.info(f"     Reasoning Quality: {analysis.reasoning_quality:.2f}')
            logger.info(f"     Factual Accuracy: {analysis.factual_accuracy:.2f}')
            logger.info(f"     Verification Needed: {analysis.verification_needed}')

        # Test model recommendations
        recommendations = system.recommend_best_model("programming', {
            "max_hallucination_risk': 0.5,
            "min_reasoning_level': 2
        })
        logger.info(f"\n📊 Best models for programming: {recommendations}')

        return True

    except Exception as e:
        logger.error(f"Error testing integrated system: {e}')
        return False

def main():
    """TODO: Add docstring."""
    """Run all tests""'
    logger.info("🚀 Starting Model Adaptation System Tests')

    tests = [
        ("Adaptive Model Context', test_adaptive_model_context),
        ("Hallucination Detection', test_hallucination_detection),
        ("Reasoning Assistance', test_reasoning_assistance),
        ("Integrated System', test_integrated_system),
    ]

    results = []
    for test_name, test_func in tests:
        logger.info(f"\n{"="*50}')
        logger.info(f"Running {test_name} Test')
        logger.info(f"{"="*50}')

        try:
            result = test_func()
            results.append((test_name, result))
            logger.info(f"✅ {test_name} Test: {"PASSED" if result else "FAILED"}')
        except Exception as e:
            logger.error(f"❌ {test_name} Test: FAILED - {e}')
            results.append((test_name, False))

    # Summary
    logger.info(f"\n{"="*50}')
    logger.info("TEST SUMMARY')
    logger.info(f"{"="*50}')

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED'
        logger.info(f"{test_name}: {status}')

    logger.info(f"\nOverall: {passed}/{total} tests passed')

    if passed == total:
        logger.info("🎉 All tests passed! The Model Adaptation System is working correctly.')
    else:
        logger.warning("⚠️ Some tests failed. Please check the errors above.')

    return passed == total

if __name__ == "__main__':
    success = main()
    sys.exit(0 if success else 1)
