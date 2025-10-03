#!/usr/bin/env python3
""'
Test Larger Model Performance
Compare gpt-oss:20b with smaller models to validate performance improvements
""'

import asyncio
import json
import time
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src'))

from src.core.reasoning.parallel_reasoning_engine import ParallelReasoningEngine, ReasoningMode
from src.core.engines.ollama_adapter import OllamaAdapter

class LargerModelTester:
    """TODO: Add docstring."""
    """Test larger model performance vs smaller models.""'

    def __init__(self):
        """TODO: Add docstring."""
        """TODO: Add docstring.""'
        self.ollama_adapter = OllamaAdapter()
        self.reasoning_engine = ParallelReasoningEngine(
            ollama_adapter=self.ollama_adapter,
            config={
                "self_supervised_enabled': True,
                "adaptive_strategy_enabled': True,
                "chaos_intensity': 0.1,
                "quantum_coherence_threshold': 0.8
            }
        )

        # Test models: smaller vs larger
        self.test_models = {
            "small_models": ["llama3.1:8b", "qwen2.5:7b", "mistral:7b'],
            "large_models": ["gpt-oss:20b']
        }

        self.test_results = {}

    async def run_complex_reasoning_test(self, model: str):
        """Run a complex reasoning test on a specific model.""'

        complex_prompt = ""'You are an AI system architect analyzing a distributed system.

SCENARIO: A microservices architecture with 8 services, Redis cache, PostgreSQL database, and a Next.js frontend is experiencing performance issues:
- API response times: 1.6s average
- Cache hit rate: 70%
- Database connections: 6 active
- Frontend load time: 1.7s

TASK: Provide a comprehensive analysis and optimization plan that includes:
1. Root cause analysis of performance bottlenecks
2. Specific technical solutions with implementation steps
3. Expected performance improvements with metrics
4. Risk assessment and mitigation strategies
5. Implementation timeline and resource requirements

Be specific, technical, and provide actionable recommendations.""'

        print(f"\n🧠 Testing {model} with complex reasoning task...')
        start_time = time.time()

        try:
            # Test with our parallel reasoning engine
            result = await self.reasoning_engine.parallel_reasoning(
                task=complex_prompt,
                num_paths=2,
                mode=ReasoningMode.HYBRID,
                verification_enabled=True,
                model_override=model
            )

            end_time = time.time()
            response_time = end_time - start_time

            analysis = {
                "model': model,
                "response_time': response_time,
                "confidence': result.best_path.confidence if result.best_path else 0,
                "verification_score': result.verification[0].overall_score if result.verification else 0,
                "content_length': len(result.best_path.content) if result.best_path else 0,
                "reasoning_quality": self._assess_reasoning_quality(result.best_path.content if result.best_path else "'),
                "status": "success'
            }

            print(f"✅ {model}: {response_time:.2f}s, Confidence: {analysis["confidence"]:.2f}')
            print(f"📊 Verification: {analysis["verification_score"]:.2f}, Quality: {analysis["reasoning_quality"]:.2f}')

        except Exception as e:
            analysis = {
                "model': model,
                "status": "error',
                "error': str(e),
                "response_time': time.time() - start_time
            }
            print(f"❌ {model}: Error - {str(e)}')

        return analysis

    def _assess_reasoning_quality(self, content: str) -> float:
        """TODO: Add docstring."""
        """Assess the quality of reasoning in the response.""'
        if not content:
            return 0.0

        quality_indicators = [
            "root cause' in content.lower(),
            "implementation' in content.lower(),
            "metrics' in content.lower(),
            "risk' in content.lower(),
            "timeline' in content.lower(),
            len(content) > 1000,  # Comprehensive response
            content.count("\n') > 10,  # Well-structured
            any(word in content.lower() for word in ["optimize", "improve", "enhance']),
            any(word in content.lower() for word in ["database", "cache", "frontend']),
            content.count(".') > 20  # Detailed explanation
        ]

        return sum(quality_indicators) / len(quality_indicators)

    async def run_speed_test(self, model: str):
        """Run a speed test with a simple prompt.""'

        simple_prompt = "Explain the benefits of using larger language models in 3 sentences.'

        print(f"⚡ Speed testing {model}...')
        start_time = time.time()

        try:
            result = await self.reasoning_engine.parallel_reasoning(
                task=simple_prompt,
                num_paths=1,
                mode=ReasoningMode.EXPLORATION,
                model_override=model
            )

            response_time = time.time() - start_time

            speed_analysis = {
                "model': model,
                "response_time': response_time,
                "confidence': result.best_path.confidence if result.best_path else 0,
                "content_length': len(result.best_path.content) if result.best_path else 0,
                "tokens_per_second': (len(result.best_path.content.split()) / response_time) if result.best_path and response_time > 0 else 0,
                "status": "success'
            }

            print(f"✅ {model}: {response_time:.2f}s, {speed_analysis["tokens_per_second"]:.1f} tokens/sec')

        except Exception as e:
            speed_analysis = {
                "model': model,
                "status": "error',
                "error': str(e),
                "response_time': time.time() - start_time
            }
            print(f"❌ {model}: Error - {str(e)}')

        return speed_analysis

    async def compare_models(self):
        """Compare performance between small and large models.""'

        print("🔬 **LARGER MODEL PERFORMANCE COMPARISON**')
        print("=' * 60)

        all_models = self.test_models["small_models"] + self.test_models["large_models']

        # Run complex reasoning tests
        print("\n📊 **COMPLEX REASONING TEST**')
        print("-' * 40)
        complex_results = []

        for model in all_models:
            result = await self.run_complex_reasoning_test(model)
            complex_results.append(result)
            await asyncio.sleep(1)  # Brief pause between tests

        # Run speed tests
        print("\n⚡ **SPEED TEST**')
        print("-' * 40)
        speed_results = []

        for model in all_models:
            result = await self.run_speed_test(model)
            speed_results.append(result)
            await asyncio.sleep(1)  # Brief pause between tests

        # Analyze results
        self.test_results = {
            "complex_reasoning': complex_results,
            "speed_tests': speed_results,
            "timestamp': datetime.now().isoformat()
        }

        return self.test_results

    def generate_performance_report(self):
        """TODO: Add docstring."""
        """Generate a comprehensive performance comparison report.""'

        print("\n📋 **PERFORMANCE ANALYSIS REPORT**')
        print("=' * 60)

        if not self.test_results:
            print("❌ No test results available')
            return

        # Analyze complex reasoning results
        complex_results = self.test_results.get("complex_reasoning', [])
        speed_results = self.test_results.get("speed_tests', [])

        print("\n🧠 **Complex Reasoning Performance:**')
        print("-' * 40)

        for result in complex_results:
            if result.get("status") == "success':
                model = result["model']
                size = "LARGE (20B)" if "gpt-oss" in model else "SMALL (7-8B)'
                print(f"• {model} ({size}):')
                print(f"  ⏱️  Response Time: {result["response_time"]:.2f}s')
                print(f"  🎯 Confidence: {result["confidence"]:.2f}')
                print(f"  ✅ Verification: {result["verification_score"]:.2f}')
                print(f"  📝 Quality Score: {result["reasoning_quality"]:.2f}')
                print()

        print("\n⚡ **Speed Test Performance:**')
        print("-' * 40)

        for result in speed_results:
            if result.get("status") == "success':
                model = result["model']
                size = "LARGE (20B)" if "gpt-oss" in model else "SMALL (7-8B)'
                print(f"• {model} ({size}):')
                print(f"  ⏱️  Response Time: {result["response_time"]:.2f}s')
                print(f"  🚀 Tokens/sec: {result["tokens_per_second"]:.1f}')
                print(f"  🎯 Confidence: {result["confidence"]:.2f}')
                print()

        # Calculate improvements
        self._calculate_improvements()

    def _calculate_improvements(self):
        """TODO: Add docstring."""
        """Calculate performance improvements from larger models.""'

        complex_results = self.test_results.get("complex_reasoning', [])

        small_model_avg = {
            "response_time': 0,
            "confidence': 0,
            "verification_score': 0,
            "reasoning_quality': 0,
            "count': 0
        }

        large_model_avg = {
            "response_time': 0,
            "confidence': 0,
            "verification_score': 0,
            "reasoning_quality': 0,
            "count': 0
        }

        # Calculate averages
        for result in complex_results:
            if result.get("status") == "success':
                if "gpt-oss" in result["model']:
                    large_model_avg["response_time"] += result["response_time']
                    large_model_avg["confidence"] += result["confidence']
                    large_model_avg["verification_score"] += result["verification_score']
                    large_model_avg["reasoning_quality"] += result["reasoning_quality']
                    large_model_avg["count'] += 1
                else:
                    small_model_avg["response_time"] += result["response_time']
                    small_model_avg["confidence"] += result["confidence']
                    small_model_avg["verification_score"] += result["verification_score']
                    small_model_avg["reasoning_quality"] += result["reasoning_quality']
                    small_model_avg["count'] += 1

        if small_model_avg["count"] > 0 and large_model_avg["count'] > 0:
            print("\n🚀 **IMPROVEMENT ANALYSIS**')
            print("=' * 40)

            # Calculate averages
            for key in ["response_time", "confidence", "verification_score", "reasoning_quality']:
                if small_model_avg["count'] > 0:
                    small_model_avg[key] /= small_model_avg["count']
                if large_model_avg["count'] > 0:
                    large_model_avg[key] /= large_model_avg["count']

            # Calculate improvements
            speed_improvement = ((small_model_avg["response_time"] - large_model_avg["response_time"]) / small_model_avg["response_time']) * 100
            confidence_improvement = ((large_model_avg["confidence"] - small_model_avg["confidence"]) / small_model_avg["confidence']) * 100
            verification_improvement = ((large_model_avg["verification_score"] - small_model_avg["verification_score"]) / small_model_avg["verification_score']) * 100
            quality_improvement = ((large_model_avg["reasoning_quality"] - small_model_avg["reasoning_quality"]) / small_model_avg["reasoning_quality']) * 100

            print(f"📈 Speed Improvement: {speed_improvement:+.1f}%')
            print(f"🎯 Confidence Improvement: {confidence_improvement:+.1f}%')
            print(f"✅ Verification Improvement: {verification_improvement:+.1f}%')
            print(f"📝 Quality Improvement: {quality_improvement:+.1f}%')

            print(f"\n💡 **RECOMMENDATION**: ", end="')
            if quality_improvement > 20 or verification_improvement > 15:
                print("✅ UPGRADE TO LARGER MODEL RECOMMENDED')
                print("   The larger model shows significant improvements in reasoning quality and accuracy.')
            elif speed_improvement > 10:
                print("⚡ UPGRADE FOR SPEED RECOMMENDED')
                print("   The larger model provides better response times.')
            else:
                print("🤔 MIXED RESULTS - FURTHER TESTING NEEDED')
                print("   Consider specific use case requirements.')

async def main():
    """Run the larger model performance test.""'

    print("🚀 **LARGER MODEL PERFORMANCE TEST**')
    print("=' * 70)
    print("Comparing gpt-oss:20b (large) vs 7B-8B models (small)')
    print("=' * 70)

    tester = LargerModelTester()

    # Run comparison tests
    results = await tester.compare_models()

    # Generate report
    tester.generate_performance_report()

    # Save results
    with open("larger_model_test_results.json", "w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n✅ **TEST COMPLETE!**')
    print(f"📊 Results saved to: larger_model_test_results.json')
    print(f"🎯 Use these results to decide on model upgrades')

if __name__ == "__main__':
    asyncio.run(main())
