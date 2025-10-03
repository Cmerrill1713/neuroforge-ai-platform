#!/usr/bin/env python3
""'
Simple Model Comparison Test
Direct comparison of gpt-oss:20b vs smaller models using OllamaAdapter
""'

import asyncio
import json
import time
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src'))

from src.core.engines.ollama_adapter import OllamaAdapter

class SimpleModelTester:
    """TODO: Add docstring."""
    """Simple direct model comparison.""'

    def __init__(self):
        """TODO: Add docstring."""
        """TODO: Add docstring.""'
        self.ollama_adapter = OllamaAdapter()
        self.test_models = ["llama3.1:8b", "qwen2.5:7b", "mistral:7b", "gpt-oss:20b']
        self.results = {}

    async def test_model_performance(self, model: str, prompt: str, test_name: str):
        """Test a specific model with a given prompt.""'

        print(f"🧠 Testing {model} - {test_name}...')
        start_time = time.time()

        try:
            # Create a simple request
            from src.core.models.requests import ModelRequest

            request = ModelRequest(
                prompt=prompt,
                model=model,
                max_tokens=500,
                temperature=0.7,
                input_tokens=len(prompt.split())
            )

            response = await self.ollama_adapter.generate_response(request)
            end_time = time.time()
            response_time = end_time - start_time

            result = {
                "model': model,
                "test_name': test_name,
                "response_time': response_time,
                "response_length": len(response.content) if hasattr(response, "content') else 0,
                "tokens_generated": getattr(response, "tokens_used', 0),
                "tokens_per_second": (getattr(response, "tokens_used', 0) / response_time) if response_time > 0 else 0,
                "status": "success',
                "response_preview": (response.content[:100] + "...") if hasattr(response, "content") and len(response.content) > 100 else getattr(response, "content", "No content')
            }

            size_category = "LARGE (20B)" if "gpt-oss" in model else "SMALL (7-8B)'
            print(f"✅ {model} ({size_category}): {response_time:.2f}s, {result["tokens_per_second"]:.1f} tok/s')
            print(f"   📝 Preview: {result["response_preview"]}')

        except Exception as e:
            result = {
                "model': model,
                "test_name': test_name,
                "status": "error',
                "error': str(e),
                "response_time': time.time() - start_time
            }
            print(f"❌ {model}: Error - {str(e)}')

        return result

    async def run_comprehensive_test(self):
        """Run comprehensive tests on all models.""'

        print("🚀 **COMPREHENSIVE MODEL COMPARISON**')
        print("=' * 60)

        # Test prompts of varying complexity
        test_prompts = {
            "simple": "What are the benefits of using larger language models? Answer in 2-3 sentences.',

            "medium": ""'Analyze this system architecture and identify potential performance bottlenecks:
- Frontend: Next.js (1.7s load time)
- API: FastAPI (1.6s average response)
- Cache: Redis (70% hit rate)
- Database: PostgreSQL (6 connections)
Provide 3 specific optimization recommendations.""',

            "complex": ""'You are a senior system architect. A distributed microservices system is experiencing performance issues:

CURRENT STATE:
- 8 microservices with varying response times (200ms-2s)
- Redis cache with 70% hit rate, 5.9MB memory usage
- PostgreSQL with 6 active connections, 7485 kB size
- Next.js frontend loading in 1.7s
- Overall system health score: 82/100

REQUIREMENTS:
1. Identify the top 3 performance bottlenecks
2. Propose specific technical solutions with implementation steps
3. Estimate performance improvements with metrics
4. Assess risks and provide mitigation strategies
5. Create a 2-week implementation timeline

Provide a comprehensive analysis with actionable recommendations.""'
        }

        all_results = []

        for test_name, prompt in test_prompts.items():
            print(f"\n📊 **{test_name.upper()} COMPLEXITY TEST**')
            print("-' * 40)

            for model in self.test_models:
                result = await self.test_model_performance(model, prompt, test_name)
                all_results.append(result)
                await asyncio.sleep(1)  # Brief pause between tests

        self.results = {
            "test_results': all_results,
            "timestamp': datetime.now().isoformat()
        }

        return self.results

    def analyze_results(self):
        """TODO: Add docstring."""
        """Analyze and report on the test results.""'

        print("\n📋 **PERFORMANCE ANALYSIS**')
        print("=' * 60)

        if not self.results or not self.results.get("test_results'):
            print("❌ No results to analyze')
            return

        # Group results by test complexity
        by_complexity = {}
        for result in self.results["test_results']:
            if result.get("status") == "success':
                test_name = result["test_name']
                if test_name not in by_complexity:
                    by_complexity[test_name] = []
                by_complexity[test_name].append(result)

        # Analyze each complexity level
        for complexity, results in by_complexity.items():
            print(f"\n🧠 **{complexity.upper()} COMPLEXITY RESULTS:**')
            print("-' * 40)

            small_models = [r for r in results if "gpt-oss" not in r["model']]
            large_models = [r for r in results if "gpt-oss" in r["model']]

            if small_models:
                avg_small_time = sum(r["response_time'] for r in small_models) / len(small_models)
                avg_small_tokens = sum(r["tokens_per_second'] for r in small_models) / len(small_models)
                print(f"📊 Small Models (7-8B) Average:')
                print(f"   ⏱️  Response Time: {avg_small_time:.2f}s')
                print(f"   🚀 Tokens/sec: {avg_small_tokens:.1f}')

            if large_models:
                avg_large_time = sum(r["response_time'] for r in large_models) / len(large_models)
                avg_large_tokens = sum(r["tokens_per_second'] for r in large_models) / len(large_models)
                print(f"📊 Large Model (20B) Average:')
                print(f"   ⏱️  Response Time: {avg_large_time:.2f}s')
                print(f"   🚀 Tokens/sec: {avg_large_tokens:.1f}')

                if small_models:
                    speed_improvement = ((avg_small_time - avg_large_time) / avg_small_time) * 100
                    throughput_improvement = ((avg_large_tokens - avg_small_tokens) / avg_small_tokens) * 100
                    print(f"📈 Improvements:')
                    print(f"   ⚡ Speed: {speed_improvement:+.1f}%')
                    print(f"   🚀 Throughput: {throughput_improvement:+.1f}%')

        # Overall recommendation
        self._generate_recommendation()

    def _generate_recommendation(self):
        """TODO: Add docstring."""
        """Generate overall recommendation based on results.""'

        print(f"\n💡 **RECOMMENDATION**')
        print("=' * 40)

        successful_results = [r for r in self.results["test_results"] if r.get("status") == "success']

        if not successful_results:
            print("❌ Insufficient data for recommendation')
            return

        small_model_results = [r for r in successful_results if "gpt-oss" not in r["model']]
        large_model_results = [r for r in successful_results if "gpt-oss" in r["model']]

        if not small_model_results or not large_model_results:
            print("❌ Need both small and large model results for comparison')
            return

        # Calculate overall averages
        avg_small_time = sum(r["response_time'] for r in small_model_results) / len(small_model_results)
        avg_large_time = sum(r["response_time'] for r in large_model_results) / len(large_model_results)

        avg_small_throughput = sum(r["tokens_per_second'] for r in small_model_results) / len(small_model_results)
        avg_large_throughput = sum(r["tokens_per_second'] for r in large_model_results) / len(large_model_results)

        speed_improvement = ((avg_small_time - avg_large_time) / avg_small_time) * 100
        throughput_improvement = ((avg_large_throughput - avg_small_throughput) / avg_small_throughput) * 100

        print(f"📊 Overall Performance Comparison:')
        print(f"   Small Models: {avg_small_time:.2f}s avg, {avg_small_throughput:.1f} tok/s')
        print(f"   Large Model:  {avg_large_time:.2f}s avg, {avg_large_throughput:.1f} tok/s')
        print(f"   Improvements: {speed_improvement:+.1f}% speed, {throughput_improvement:+.1f}% throughput')

        if speed_improvement > 15 or throughput_improvement > 20:
            print(f"\n✅ **STRONG RECOMMENDATION: UPGRADE TO LARGER MODEL**')
            print(f"   The gpt-oss:20b model shows significant performance improvements.')
            print(f"   Consider making it the primary model for complex tasks.')
        elif speed_improvement > 5 or throughput_improvement > 10:
            print(f"\n⚡ **MODERATE RECOMMENDATION: CONSIDER UPGRADE**')
            print(f"   The larger model shows improvements but may not justify the resource cost.')
            print(f"   Use for specific high-complexity tasks.')
        else:
            print(f"\n🤔 **MIXED RESULTS: CURRENT MODELS SUFFICIENT**')
            print(f"   The performance difference may not justify upgrading.')
            print(f"   Consider other optimization strategies first.')

async def main():
    """Run the simple model comparison test.""'

    print("🔬 **SIMPLE MODEL COMPARISON TEST**')
    print("=' * 70)
    print("Testing gpt-oss:20b vs smaller models with direct OllamaAdapter calls')
    print("=' * 70)

    tester = SimpleModelTester()

    # Run tests
    results = await tester.run_comprehensive_test()

    # Analyze results
    tester.analyze_results()

    # Save results
    with open("simple_model_comparison_results.json", "w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n✅ **COMPARISON COMPLETE!**')
    print(f"📊 Results saved to: simple_model_comparison_results.json')

if __name__ == "__main__':
    asyncio.run(main())
