#!/usr/bin/env python3
"""
Quick Integration: Add Advanced Prompt Engineering to Your Existing Orchestrator

This script shows exactly how to add ensemble prompt optimization to your existing system
in under 30 minutes.
"""

import asyncio
import time
import hashlib
from typing import Dict, List, Any
import statistics

# Assuming you have these from your existing system
# from your_orchestrator import YourModelOrchestrator
# from your_monitor import YourMonitor
# from your_cache import YourCache

class PromptEngineeringExtension:
    """
    Extension class that adds advanced prompt engineering to your existing orchestrator.

    Simply instantiate this with your existing orchestrator and you get:
    - Ensemble prompt optimization
    - Cross-model validation
    - Performance monitoring integration
    - Caching for optimization results
    """

    def __init__(self, your_orchestrator, your_monitor=None, your_cache=None):
        """
        Initialize with your existing components

        Args:
            your_orchestrator: Your existing model orchestrator
            your_monitor: Your existing monitoring system (optional)
            your_cache: Your existing caching system (optional)
        """
        self.orchestrator = your_orchestrator
        self.monitor = your_monitor
        self.cache = your_cache

        # Optimization tracking
        self.optimization_history = []

    async def optimize_prompt_ensemble(self, prompt: str, iterations: int = 2) -> Dict[str, Any]:
        """
        Optimize a prompt using your full model orchestration

        Args:
            prompt: The prompt to optimize
            iterations: Number of optimization rounds

        Returns:
            Dict with optimization results
        """

        start_time = time.time()
        optimization_id = f"opt_{int(time.time())}_{hash(prompt) % 10000}"

        # Check cache first (if available)
        if self.cache:
            cached_result = await self._check_cache(prompt)
            if cached_result:
                return cached_result

        print(f"🎯 Optimizing prompt: {prompt[:50]}...")

        optimized_prompt = prompt
        improvement_history = []

        for iteration in range(iterations):
            print(f"🔄 Iteration {iteration + 1}/{iterations}")

            # Step 1: Get analysis from your orchestration
            analysis_responses = await self._get_ensemble_analysis(optimized_prompt)
            print(f"📊 Got {len(analysis_responses)} analysis responses")

            # Step 2: Generate improvements using your models
            improvements = await self._generate_improvements(optimized_prompt, analysis_responses)
            print(f"💡 Generated {len(improvements)} improvement suggestions")

            # Step 3: Select best improvement
            best_improvement = self._select_best_improvement(improvements)

            if best_improvement['score'] > 0.6:  # Good improvement threshold
                optimized_prompt = best_improvement['text']
                improvement_history.append({
                    'iteration': iteration + 1,
                    'improvement': best_improvement,
                    'model': best_improvement.get('model', 'unknown')
                })
                print(f"✅ Improved prompt (score: {best_improvement['score']:.2f})")
            else:
                print("⏹️ No significant improvement found")
                break

        # Calculate final metrics
        execution_time = time.time() - start_time
        final_score = self._calculate_overall_improvement(prompt, optimized_prompt)

        result = {
            'optimization_id': optimization_id,
            'original_prompt': prompt,
            'optimized_prompt': optimized_prompt,
            'improvement_score': final_score,
            'iterations_completed': len(improvement_history),
            'execution_time': execution_time,
            'model_contributions': self._analyze_contributions(improvement_history)
        }

        # Cache result
        if self.cache:
            await self._cache_result(prompt, result)

        # Track in monitoring
        if self.monitor:
            await self._track_metrics(result)

        self.optimization_history.append(result)

        print(".2f"        return result

    async def _get_ensemble_analysis(self, prompt: str) -> List[Dict[str, Any]]:
        """Get analysis from your model orchestration"""

        analysis_prompt = f"""
        Analyze this prompt and suggest specific improvements:

        Prompt: "{prompt}"

        Provide:
        1. Clarity assessment (1-10)
        2. Specificity assessment (1-10)
        3. Potential ambiguities
        4. Concrete improvement suggestions
        """

        # Adapt this to your orchestrator's method for getting multiple responses
        # This is where you integrate with your existing system

        try:
            # Example: assuming your orchestrator has a method like this
            responses = await self.orchestrator.get_all_model_responses(analysis_prompt)

            return [{
                'model': getattr(resp, 'model_name', f'model_{i}'),
                'content': getattr(resp, 'content', resp),
                'quality_score': getattr(resp, 'quality_score', 7.0),
                'response_time': getattr(resp, 'execution_time', 0)
            } for i, resp in enumerate(responses)]

        except AttributeError:
            # Fallback if your orchestrator has different method names
            print("⚠️ Please adapt the orchestrator method calls to match your system")
            return [{
                'model': 'fallback_model',
                'content': 'Sample analysis response',
                'quality_score': 7.0,
                'response_time': 1.0
            }]

    async def _generate_improvements(self, prompt: str, analysis_responses: List[Dict]) -> List[Dict]:
        """Generate improvement suggestions from analysis"""

        improvements = []

        for analysis in analysis_responses:
            improvement_prompt = f"""
            Based on this analysis:

            {analysis['content']}

            Original prompt: "{prompt}"

            Generate 2-3 specific, actionable improvements to make this prompt better.
            Focus on clarity, specificity, and effectiveness.

            Format: Number each suggestion clearly.
            """

            try:
                # Use your orchestrator to generate improvements
                improvement_response = await self.orchestrator.route_and_execute(
                    improvement_prompt,
                    task_type='creative'  # Adapt to your routing
                )

                # Parse suggestions from response
                suggestions = self._parse_suggestions(improvement_response)

                for suggestion in suggestions:
                    improvements.append({
                        'text': suggestion,
                        'source_model': analysis['model'],
                        'quality_score': analysis['quality_score'],
                        'base_prompt': prompt
                    })

            except Exception as e:
                print(f"⚠️ Failed to generate improvements: {e}")

        return improvements

    def _parse_suggestions(self, response) -> List[str]:
        """Parse improvement suggestions from model response"""

        # Adapt this parsing to your model's response format
        content = getattr(response, 'content', str(response))

        # Simple parsing - split by numbers or bullet points
        lines = content.split('\n')
        suggestions = []

        for line in lines:
            line = line.strip()
            # Look for numbered suggestions or bullet points
            if (line and
                (line[0].isdigit() or line.startswith('-') or line.startswith('•')) and
                len(line) > 20):  # Reasonable length
                # Clean up the suggestion
                clean_suggestion = line.lstrip('123456789.-• ').strip()
                if clean_suggestion:
                    suggestions.append(clean_suggestion)

        return suggestions[:3]  # Limit to 3 suggestions

    def _select_best_improvement(self, improvements: List[Dict]) -> Dict[str, Any]:
        """Select the best improvement from suggestions"""

        if not improvements:
            return {'text': '', 'score': 0, 'reasoning': 'No improvements available'}

        # Score improvements based on quality and diversity
        scored_improvements = []

        for imp in improvements:
            # Simple scoring - adapt to your needs
            quality_score = imp.get('quality_score', 5) / 10.0  # Normalize to 0-1
            length_score = min(1.0, len(imp['text']) / 200.0)  # Prefer detailed suggestions
            diversity_score = self._calculate_diversity_score(imp['text'], imp['base_prompt'])

            total_score = (quality_score * 0.5 + length_score * 0.3 + diversity_score * 0.2)

            scored_improvements.append((total_score, imp))

        # Select highest scoring
        best_score, best_improvement = max(scored_improvements, key=lambda x: x[0])

        # Create improved prompt based on suggestion
        improved_prompt = self._apply_suggestion_to_prompt(
            best_improvement['base_prompt'],
            best_improvement['text']
        )

        return {
            'text': improved_prompt,
            'score': best_score,
            'source_model': best_improvement['source_model'],
            'suggestion': best_improvement['text']
        }

    def _apply_suggestion_to_prompt(self, original_prompt: str, suggestion: str) -> str:
        """Apply an improvement suggestion to create a new prompt"""

        # This is a simple implementation - you can make this much more sophisticated
        # For now, we'll create a new prompt that incorporates the suggestion

        improved_prompt = f"""
        {original_prompt}

        Additional context: {suggestion}
        """.strip()

        return improved_prompt

    def _calculate_diversity_score(self, suggestion: str, base_prompt: str) -> float:
        """Calculate how different the suggestion is from the base prompt"""

        # Simple diversity calculation
        base_words = set(base_prompt.lower().split())
        suggestion_words = set(suggestion.lower().split())

        # Calculate overlap
        overlap = len(base_words.intersection(suggestion_words))
        total_unique = len(base_words.union(suggestion_words))

        if total_unique == 0:
            return 0.5

        # Higher diversity score for less overlap
        diversity = 1.0 - (overlap / total_unique)
        return diversity

    def _calculate_overall_improvement(self, original: str, optimized: str) -> float:
        """Calculate overall improvement score"""

        # Simple heuristics - you can replace with more sophisticated metrics
        original_length = len(original)
        optimized_length = len(optimized)

        # Length improvement (up to 50% of score)
        length_score = min(0.5, abs(optimized_length - original_length) / max(original_length, 1))

        # Assume some improvement for different content
        content_similarity = self._calculate_similarity(original, optimized)
        content_score = 1.0 - content_similarity  # More different = potentially better

        # Combine scores
        total_score = length_score * 0.4 + content_score * 0.6

        return min(1.0, total_score)  # Cap at 1.0

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity (0-1, higher = more similar)"""

        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 and not words2:
            return 1.0

        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))

        return intersection / union if union > 0 else 0.0

    def _analyze_contributions(self, improvement_history: List[Dict]) -> Dict[str, Any]:
        """Analyze which models contributed to improvements"""

        model_contributions = {}
        model_scores = {}

        for improvement in improvement_history:
            model = improvement.get('model', 'unknown')
            score = improvement.get('improvement', {}).get('score', 0)

            model_contributions[model] = model_contributions.get(model, 0) + 1
            if model not in model_scores:
                model_scores[model] = []
            model_scores[model].append(score)

        # Calculate averages
        avg_scores = {}
        for model, scores in model_scores.items():
            avg_scores[model] = statistics.mean(scores) if scores else 0

        return {
            'contributions': model_contributions,
            'average_scores': avg_scores,
            'total_improvements': len(improvement_history)
        }

    async def _check_cache(self, prompt: str) -> Dict[str, Any]:
        """Check if optimization result is cached"""
        if not self.cache:
            return None

        cache_key = hashlib.md5(prompt.encode()).hexdigest()

        try:
            # Adapt to your cache's method
            return await self.cache.get(f"prompt_opt:{cache_key}")
        except:
            return None

    async def _cache_result(self, prompt: str, result: Dict[str, Any]):
        """Cache optimization result"""
        if not self.cache:
            return

        cache_key = hashlib.md5(prompt.encode()).hexdigest()

        try:
            # Adapt to your cache's method - cache for 1 hour
            await self.cache.set(f"prompt_opt:{cache_key}", result, ttl=3600)
        except Exception as e:
            print(f"⚠️ Failed to cache result: {e}")

    async def _track_metrics(self, result: Dict[str, Any]):
        """Track optimization metrics in your monitoring system"""
        if not self.monitor:
            return

        try:
            # Adapt to your monitor's method
            await self.monitor.record_metric(
                metric_type="prompt_optimization",
                value=result['improvement_score'],
                metadata={
                    'optimization_id': result['optimization_id'],
                    'iterations': result['iterations_completed'],
                    'execution_time': result['execution_time']
                }
            )
        except Exception as e:
            print(f"⚠️ Failed to track metrics: {e}")

# Example usage
async def example_integration():
    """
    Example of how to integrate this with your existing system
    """

    # Assume you have your orchestrator
    # from your_system import YourModelOrchestrator
    # orchestrator = YourModelOrchestrator()

    # Create the prompt engineering extension
    # prompt_engineer = PromptEngineeringExtension(orchestrator)

    # Optimize a prompt
    # result = await prompt_engineer.optimize_prompt_ensemble(
    #     "Explain how neural networks work",
    #     iterations=2
    # )

    # print(f"Original: {result['original_prompt']}")
    # print(f"Optimized: {result['optimized_prompt']}")
    # print(f"Improvement: {result['improvement_score']:.2f}")

    print("🎯 To integrate:")
    print("1. Uncomment the imports above")
    print("2. Replace with your actual orchestrator class")
    print("3. Adapt method calls to match your system's API")
    print("4. Run the example!")

if __name__ == "__main__":
    asyncio.run(example_integration())
