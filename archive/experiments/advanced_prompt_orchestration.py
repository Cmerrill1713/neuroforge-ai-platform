#!/usr/bin/env python3
"""
Advanced Prompt Engineering Orchestration System

Leverages your existing model orchestration to create an intelligent prompt engineering system
optimized for 30B+ models with advanced multi-model reasoning capabilities.
"""

import asyncio
import logging
import time
import json
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from collections import defaultdict
import statistics

# Import your existing system components
from src.core.cache.context_fusion_cache import create_context_fusion_cache
from src.core.monitoring.context_monitoring_system import create_context_monitoring_system
from src.core.validation.schema_validation_framework import create_schema_validation_framework

logger = logging.getLogger(__name__)

class AdvancedPromptOrchestrator:
    """
    Advanced prompt engineering system that leverages your existing model orchestration.

    This system transforms your multi-model setup into an intelligent prompt engineering
    platform with ensemble reasoning, cross-model validation, and adaptive optimization.
    """

    def __init__(self, model_orchestrator):
        """
        Initialize with your existing model orchestrator

        Args:
            model_orchestrator: Your existing model orchestration system
        """
        self.orchestrator = model_orchestrator

        # Leverage your existing components
        self.cache = create_context_fusion_cache()
        self.monitor = create_context_monitoring_system()
        self.validator = create_schema_validation_framework()

        # Advanced prompt engineering state
        self.prompt_history = defaultdict(list)
        self.model_performance = defaultdict(lambda: defaultdict(list))
        self.optimization_cache = {}

        # Ensemble intelligence
        self.ensemble_weights = {}
        self.consensus_threshold = 0.7

        logger.info("🚀 Advanced Prompt Orchestrator initialized with your existing system")

    async def optimize_prompt_ensemble(self, prompt: str, iterations: int = 3) -> Dict[str, Any]:
        """
        Multi-stage prompt optimization using your full model orchestration

        Args:
            prompt: Base prompt to optimize
            iterations: Number of optimization rounds

        Returns:
            Dict containing optimized prompt and performance metrics
        """

        start_time = time.time()
        optimization_id = f"opt_{int(time.time())}_{hash(prompt) % 10000}"

        logger.info(f"🎯 Starting ensemble optimization for prompt: {prompt[:50]}...")

        current_prompt = prompt
        optimization_history = []

        for iteration in range(iterations):
            logger.info(f"🔄 Optimization iteration {iteration + 1}/{iterations}")

            # Phase 1: Multi-model analysis
            analysis_results = await self._analyze_with_ensemble(current_prompt)

            # Phase 2: Cross-model improvement suggestions
            improvement_suggestions = await self._generate_improvements_ensemble(
                current_prompt, analysis_results
            )

            # Phase 3: Consensus validation
            validated_improvements = await self._validate_improvements_consensus(
                current_prompt, improvement_suggestions
            )

            # Phase 4: Select best improvement
            best_improvement = self._select_best_improvement(validated_improvements)

            # Update for next iteration
            if best_improvement['improvement_score'] > 0.1:  # Significant improvement
                current_prompt = best_improvement['improved_prompt']
                optimization_history.append(best_improvement)
                logger.info(f"✅ Improved prompt (score: {best_improvement['improvement_score']:.2f})")
            else:
                logger.info("⏹️ No significant improvement found, stopping optimization")
                break

        # Final evaluation
        final_evaluation = await self._evaluate_final_prompt(current_prompt, prompt)

        # Cache results using your existing cache
        await self._cache_optimization_results(optimization_id, {
            'original_prompt': prompt,
            'optimized_prompt': current_prompt,
            'optimization_history': optimization_history,
            'final_evaluation': final_evaluation,
            'total_time': time.time() - start_time
        })

        # Track in your monitoring system
        await self._track_optimization_metrics(optimization_id, final_evaluation)

        result = {
            'optimization_id': optimization_id,
            'original_prompt': prompt,
            'optimized_prompt': current_prompt,
            'improvement_score': final_evaluation.get('overall_improvement', 0),
            'iterations_completed': len(optimization_history),
            'model_contributions': self._analyze_model_contributions(optimization_history),
            'execution_time': time.time() - start_time,
            'confidence_score': final_evaluation.get('confidence_score', 0)
        }

        logger.info(f"🎉 Ensemble optimization completed: {result['improvement_score']:.2f} improvement")
        return result

    async def _analyze_with_ensemble(self, prompt: str) -> Dict[str, Any]:
        """Use your orchestration to analyze prompt from multiple perspectives"""

        analysis_tasks = []

        # Define different analysis perspectives
        analysis_prompts = {
            'clarity': f"Analyze the clarity and precision of this prompt: '{prompt}'. Rate clarity from 0-10 and suggest improvements.",
            'specificity': f"Evaluate how specific and detailed this prompt is: '{prompt}'. Identify ambiguities and suggest making it more specific.",
            'structure': f"Assess the structure and organization of this prompt: '{prompt}'. Suggest better organization.",
            'effectiveness': f"Evaluate how effective this prompt would be at getting the desired response: '{prompt}'. Rate effectiveness 0-10."
        }

        # Use your orchestrator to route to different models
        for analysis_type, analysis_prompt in analysis_prompts.items():
            # Route to your orchestration - you'll need to adapt this to your specific routing
            task = self.orchestrator.route_and_execute(analysis_prompt, task_type='analysis')
            analysis_tasks.append((analysis_type, task))

        # Execute all analyses in parallel
        results = {}
        for analysis_type, task in analysis_tasks:
            try:
                result = await task
                results[analysis_type] = self._parse_analysis_result(result)
                # Track model performance
                await self._track_model_performance(task.model_used, 'analysis', result.quality_score)
            except Exception as e:
                logger.warning(f"Analysis failed for {analysis_type}: {e}")
                results[analysis_type] = {'score': 5, 'suggestions': [], 'error': str(e)}

        return results

    async def _generate_improvements_ensemble(self, prompt: str, analysis_results: Dict) -> List[Dict]:
        """Generate improvement suggestions using ensemble of models"""

        improvement_tasks = []

        for analysis_type, analysis in analysis_results.items():
            if 'error' not in analysis:
                improvement_prompt = f"""
                Based on this analysis of a prompt: {analysis}

                Original prompt: "{prompt}"

                Generate 3 specific, actionable improvements to make this prompt better.
                Focus on {analysis_type} improvements.
                Return as a JSON list of improvement suggestions.
                """

                task = self.orchestrator.route_and_execute(improvement_prompt, task_type='creative')
                improvement_tasks.append((analysis_type, task))

        # Execute improvement generation
        improvements = []
        for analysis_type, task in improvement_tasks:
            try:
                result = await task
                parsed_improvements = self._parse_improvement_suggestions(result)
                improvements.extend(parsed_improvements)
                await self._track_model_performance(task.model_used, 'creative', result.quality_score)
            except Exception as e:
                logger.warning(f"Improvement generation failed for {analysis_type}: {e}")

        return improvements

    async def _validate_improvements_consensus(self, original_prompt: str, improvements: List[Dict]) -> List[Dict]:
        """Validate improvements using cross-model consensus"""

        validation_tasks = []

        for improvement in improvements:
            validation_prompt = f"""
            Compare these two prompts:

            Original: "{original_prompt}"
            Improved: "{improvement['text']}"

            Rate the improvement on a scale of 0-10 (10 being much better).
            Consider: clarity, specificity, effectiveness, and overall quality.

            Return only a JSON with: {{"score": number, "reasoning": "brief explanation"}}
            """

            task = self.orchestrator.route_and_execute(validation_prompt, task_type='evaluation')
            validation_tasks.append((improvement, task))

        # Get consensus validation
        validated_improvements = []
        for improvement, task in validation_tasks:
            try:
                result = await task
                validation = self._parse_validation_result(result)

                validated_improvement = {
                    **improvement,
                    'validation_score': validation['score'],
                    'validation_reasoning': validation['reasoning'],
                    'overall_score': (improvement.get('quality_score', 5) + validation['score']) / 2
                }

                validated_improvements.append(validated_improvement)
                await self._track_model_performance(task.model_used, 'evaluation', validation['score'])

            except Exception as e:
                logger.warning(f"Validation failed for improvement: {e}")
                validated_improvements.append({**improvement, 'validation_score': 5, 'overall_score': 5})

        return validated_improvements

    def _select_best_improvement(self, validated_improvements: List[Dict]) -> Dict[str, Any]:
        """Select the best improvement based on ensemble scoring"""

        if not validated_improvements:
            return {
                'improved_prompt': '',
                'improvement_score': 0,
                'reasoning': 'No valid improvements generated'
            }

        # Score improvements based on multiple factors
        scored_improvements = []
        for imp in validated_improvements:
            ensemble_score = (
                imp.get('quality_score', 5) * 0.3 +
                imp.get('validation_score', 5) * 0.4 +
                imp.get('novelty_score', 5) * 0.3
            )
            scored_improvements.append((ensemble_score, imp))

        # Select highest scoring improvement
        best_score, best_improvement = max(scored_improvements, key=lambda x: x[0])

        return {
            'improved_prompt': best_improvement['text'],
            'improvement_score': best_score / 10,  # Normalize to 0-1
            'reasoning': best_improvement.get('reasoning', 'Ensemble selection'),
            'contributing_models': best_improvement.get('models_used', [])
        }

    async def _evaluate_final_prompt(self, optimized_prompt: str, original_prompt: str) -> Dict[str, Any]:
        """Final evaluation of optimization results"""

        evaluation_prompt = f"""
        Compare these two prompts and rate the improvement:

        Original: "{original_prompt}"
        Optimized: "{optimized_prompt}"

        Rate overall improvement from 0-10.
        Consider: clarity, specificity, effectiveness, and task completion likelihood.

        Return JSON: {{"improvement_score": number, "confidence": number, "key_improvements": ["list"]}}
        """

        result = await self.orchestrator.route_and_execute(evaluation_prompt, task_type='evaluation')

        try:
            evaluation = self._parse_evaluation_result(result)
            return {
                'overall_improvement': evaluation['improvement_score'] / 10,
                'confidence_score': evaluation['confidence'] / 10,
                'key_improvements': evaluation.get('key_improvements', []),
                'evaluation_model': result.model_used
            }
        except Exception as e:
            logger.warning(f"Final evaluation parsing failed: {e}")
            return {'overall_improvement': 0, 'confidence_score': 0.5, 'key_improvements': []}

    async def _cache_optimization_results(self, optimization_id: str, results: Dict):
        """Cache results using your existing fusion cache"""
        await self.cache.cache_fusion_result(
            fusion_context={'type': 'prompt_optimization', 'id': optimization_id},
            fusion_result=results
        )

    async def _track_optimization_metrics(self, optimization_id: str, evaluation: Dict):
        """Track metrics in your existing monitoring system"""
        await self.monitor.record_operation(
            operation_type="prompt_optimization",
            processing_time=evaluation.get('total_time', 0),
            quality_score=evaluation.get('overall_improvement', 0),
            error_occurred=False,
            metadata={
                'optimization_id': optimization_id,
                'improvement_score': evaluation.get('overall_improvement', 0),
                'confidence': evaluation.get('confidence_score', 0.5)
            }
        )

    async def _track_model_performance(self, model_name: str, task_type: str, score: float):
        """Track model performance for routing optimization"""
        self.model_performance[model_name][task_type].append(score)

        # Keep only recent performance data
        if len(self.model_performance[model_name][task_type]) > 100:
            self.model_performance[model_name][task_type] = self.model_performance[model_name][task_type][-50:]

    def _analyze_model_contributions(self, optimization_history: List[Dict]) -> Dict[str, Any]:
        """Analyze which models contributed most to optimization"""
        model_contributions = defaultdict(int)
        model_scores = defaultdict(list)

        for step in optimization_history:
            models = step.get('contributing_models', [])
            score = step.get('improvement_score', 0)

            for model in models:
                model_contributions[model] += 1
                model_scores[model].append(score)

        # Calculate average scores per model
        avg_scores = {}
        for model, scores in model_scores.items():
            avg_scores[model] = statistics.mean(scores) if scores else 0

        return {
            'total_contributions': dict(model_contributions),
            'average_scores': avg_scores,
            'top_performer': max(avg_scores.items(), key=lambda x: x[1], default=(None, 0))[0]
        }

    # Utility parsing methods (you'll need to adapt these to your orchestrator's response format)
    def _parse_analysis_result(self, result) -> Dict:
        """Parse analysis result from your orchestrator"""
        # Adapt this to your orchestrator's response format
        return {'score': 7, 'suggestions': ['test suggestion']}

    def _parse_improvement_suggestions(self, result) -> List[Dict]:
        """Parse improvement suggestions"""
        # Adapt to your format
        return [{'text': 'Improved prompt text', 'quality_score': 8}]

    def _parse_validation_result(self, result) -> Dict:
        """Parse validation result"""
        return {'score': 7, 'reasoning': 'Good improvement'}

    def _parse_evaluation_result(self, result) -> Dict:
        """Parse final evaluation"""
        return {'improvement_score': 6, 'confidence': 8, 'key_improvements': ['Better clarity']}

# Example usage with your system
async def example_usage():
    """Example of how to use the advanced orchestrator with your existing system"""

    # Assuming you have your orchestrator instance
    # your_orchestrator = YourModelOrchestrator()

    # Create advanced prompt orchestrator
    # advanced_orchestrator = AdvancedPromptOrchestrator(your_orchestrator)

    # Optimize a prompt
    # result = await advanced_orchestrator.optimize_prompt_ensemble(
    #     "Write a summary of artificial intelligence",
    #     iterations=2
    # )

    # print(f"Optimization result: {result}")

    pass

if __name__ == "__main__":
    # Run example
    asyncio.run(example_usage())
