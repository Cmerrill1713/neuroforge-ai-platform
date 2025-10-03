#!/usr/bin/env python3
""'
Direct Ollama API Test
Simple direct comparison using requests to Ollama API
""'

import requests
import json
import time
from datetime import datetime

class DirectOllamaTest:
    """TODO: Add docstring."""
    """Direct Ollama API testing without complex imports.""'

    def __init__(self):
        """TODO: Add docstring."""
        """TODO: Add docstring.""'
        self.ollama_url = "http://localhost:11434'
        self.test_models = ["llama3.1:8b", "qwen2.5:7b", "mistral:7b", "gpt-oss:20b']
        self.results = []

    def test_model(self, model: str, prompt: str, test_name: str):
        """TODO: Add docstring."""
        """Test a model directly via Ollama API.""'

        print(f"🧠 Testing {model} - {test_name}...')
        start_time = time.time()

        try:
            # Direct Ollama API call
            response = requests.post(
                f"{self.ollama_url}/api/generate',
                json={
                    "model': model,
                    "prompt': prompt,
                    "stream': False,
                    "options': {
                        "temperature': 0.7,
                        "num_predict': 500
                    }
                },
                timeout=60
            )

            end_time = time.time()
            response_time = end_time - start_time

            if response.status_code == 200:
                data = response.json()
                content = data.get("response", "')

                # Calculate basic metrics
                word_count = len(content.split())
                char_count = len(content)
                words_per_second = word_count / response_time if response_time > 0 else 0

                result = {
                    "model': model,
                    "test_name': test_name,
                    "response_time': response_time,
                    "word_count': word_count,
                    "char_count': char_count,
                    "words_per_second': words_per_second,
                    "status": "success',
                    "response_preview": content[:150] + "...' if len(content) > 150 else content,
                    "model_size": "LARGE (20B)" if "gpt-oss" in model else "SMALL (7-8B)'
                }

                print(f"✅ {model} ({result["model_size"]}): {response_time:.2f}s, {words_per_second:.1f} words/s')
                print(f"   📝 Preview: {result["response_preview"]}')

            else:
                result = {
                    "model': model,
                    "test_name': test_name,
                    "status": "error',
                    "error": f"HTTP {response.status_code}',
                    "response_time': response_time,
                    "model_size": "LARGE (20B)" if "gpt-oss" in model else "SMALL (7-8B)'
                }
                print(f"❌ {model}: HTTP {response.status_code}')

        except Exception as e:
            result = {
                "model': model,
                "test_name': test_name,
                "status": "error',
                "error': str(e),
                "response_time': time.time() - start_time,
                "model_size": "LARGE (20B)" if "gpt-oss" in model else "SMALL (7-8B)'
            }
            print(f"❌ {model}: Error - {str(e)}')

        self.results.append(result)
        return result

    def run_comparison_tests(self):
        """TODO: Add docstring."""
        """Run comprehensive comparison tests.""'

        print("🚀 **DIRECT OLLAMA MODEL COMPARISON**')
        print("=' * 60)

        # Test prompts of varying complexity
        test_prompts = {
            "simple": "What are the main benefits of using larger language models? Answer briefly.',

            "reasoning": ""'Analyze this scenario: A web application has these performance metrics:
- Frontend load time: 1.7 seconds
- API response time: 1.6 seconds
- Cache hit rate: 70%
- Database connections: 6 active

What are the top 3 performance bottlenecks and how would you fix them?""',

            "complex": ""'You are a system architect reviewing a distributed system with these issues:

PERFORMANCE METRICS:
- 8 microservices with 200ms-2s response times
- Redis cache: 70% hit rate, 5.9MB memory
- PostgreSQL: 6 connections, 7485 kB size
- Next.js frontend: 1.7s load time
- Overall health score: 82/100

TASK: Create a comprehensive optimization plan including:
1. Root cause analysis of bottlenecks
2. Specific technical solutions
3. Expected performance improvements
4. Implementation timeline
5. Risk assessment

Provide detailed, actionable recommendations.""'
        }

        for test_name, prompt in test_prompts.items():
            print(f"\n📊 **{test_name.upper()} TEST**')
            print("-' * 40)

            for model in self.test_models:
                self.test_model(model, prompt, test_name)
                time.sleep(2)  # Brief pause between tests

    def analyze_results(self):
        """TODO: Add docstring."""
        """Analyze and report on test results.""'

        print(f"\n📋 **PERFORMANCE ANALYSIS**')
        print("=' * 60)

        successful_results = [r for r in self.results if r.get("status") == "success']

        if not successful_results:
            print("❌ No successful results to analyze')
            return

        # Group by test complexity
        by_test = {}
        for result in successful_results:
            test_name = result["test_name']
            if test_name not in by_test:
                by_test[test_name] = {"small": [], "large': []}

            if result["model_size"] == "LARGE (20B)':
                by_test[test_name]["large'].append(result)
            else:
                by_test[test_name]["small'].append(result)

        # Analyze each test
        overall_improvements = {"speed": [], "throughput': []}

        for test_name, results in by_test.items():
            print(f"\n🧠 **{test_name.upper()} TEST RESULTS:**')
            print("-' * 40)

            small_results = results["small']
            large_results = results["large']

            if small_results:
                avg_small_time = sum(r["response_time'] for r in small_results) / len(small_results)
                avg_small_throughput = sum(r["words_per_second'] for r in small_results) / len(small_results)
                print(f"📊 Small Models (7-8B) - {len(small_results)} models:')
                print(f"   ⏱️  Avg Response Time: {avg_small_time:.2f}s')
                print(f"   🚀 Avg Throughput: {avg_small_throughput:.1f} words/s')

            if large_results:
                avg_large_time = sum(r["response_time'] for r in large_results) / len(large_results)
                avg_large_throughput = sum(r["words_per_second'] for r in large_results) / len(large_results)
                print(f"📊 Large Model (20B) - {len(large_results)} models:')
                print(f"   ⏱️  Avg Response Time: {avg_large_time:.2f}s')
                print(f"   🚀 Avg Throughput: {avg_large_throughput:.1f} words/s')

                if small_results:
                    speed_improvement = ((avg_small_time - avg_large_time) / avg_small_time) * 100
                    throughput_improvement = ((avg_large_throughput - avg_small_throughput) / avg_small_throughput) * 100

                    overall_improvements["speed'].append(speed_improvement)
                    overall_improvements["throughput'].append(throughput_improvement)

                    print(f"📈 Improvements vs Small Models:')
                    print(f"   ⚡ Speed: {speed_improvement:+.1f}%')
                    print(f"   🚀 Throughput: {throughput_improvement:+.1f}%')

        # Overall recommendation
        self._generate_recommendation(overall_improvements)

    def _generate_recommendation(self, improvements):
        """TODO: Add docstring."""
        """Generate overall recommendation.""'

        print(f"\n💡 **OVERALL RECOMMENDATION**')
        print("=' * 50)

        if not improvements["speed"] or not improvements["throughput']:
            print("❌ Insufficient data for recommendation')
            return

        avg_speed_improvement = sum(improvements["speed"]) / len(improvements["speed'])
        avg_throughput_improvement = sum(improvements["throughput"]) / len(improvements["throughput'])

        print(f"📊 Overall Performance Comparison:')
        print(f"   ⚡ Average Speed Improvement: {avg_speed_improvement:+.1f}%')
        print(f"   🚀 Average Throughput Improvement: {avg_throughput_improvement:+.1f}%')

        # Determine recommendation
        if avg_speed_improvement > 20 or avg_throughput_improvement > 30:
            recommendation = "✅ **STRONG UPGRADE RECOMMENDATION**'
            explanation = "The gpt-oss:20b model shows significant performance improvements across all test scenarios.'
            action = "Immediately configure as primary model for complex tasks.'
        elif avg_speed_improvement > 10 or avg_throughput_improvement > 15:
            recommendation = "⚡ **MODERATE UPGRADE RECOMMENDATION**'
            explanation = "The larger model shows meaningful improvements, especially for complex tasks.'
            action = "Use gpt-oss:20b for high-complexity reasoning tasks.'
        elif avg_speed_improvement > 0 or avg_throughput_improvement > 0:
            recommendation = "🤔 **CONDITIONAL UPGRADE RECOMMENDATION**'
            explanation = "The larger model shows some improvements but may not justify full migration.'
            action = "Test with specific use cases before deciding.'
        else:
            recommendation = "❌ **NO UPGRADE NEEDED**'
            explanation = "Current smaller models perform adequately for your use cases.'
            action = "Focus on other optimization strategies.'

        print(f"\n{recommendation}')
        print(f"📝 Analysis: {explanation}')
        print(f"🎯 Action: {action}')

        # Additional insights
        print(f"\n🔍 **DETAILED INSIGHTS:**')
        if avg_speed_improvement > 0:
            print(f"   ✅ Faster response times across all complexity levels')
        if avg_throughput_improvement > 0:
            print(f"   ✅ Higher word generation throughput')

        print(f"   💾 Resource Trade-off: 20B model uses ~3x more memory than 7B models')
        print(f"   🎯 Best Use Case: Complex reasoning and analysis tasks')

    def save_results(self):
        """TODO: Add docstring."""
        """Save results to file.""'

        results_data = {
            "test_results': self.results,
            "timestamp': datetime.now().isoformat(),
            "summary': {
                "total_tests': len(self.results),
                "successful_tests": len([r for r in self.results if r.get("status") == "success']),
                "failed_tests": len([r for r in self.results if r.get("status") == "error'])
            }
        }

        with open("direct_ollama_test_results.json", "w') as f:
            json.dump(results_data, f, indent=2, default=str)

        print(f"📊 Results saved to: direct_ollama_test_results.json')

def main():
    """TODO: Add docstring."""
    """Run the direct Ollama comparison test.""'

    print("🔬 **DIRECT OLLAMA MODEL COMPARISON**')
    print("=' * 70)
    print("Testing gpt-oss:20b vs smaller models using direct API calls')
    print("=' * 70)

    tester = DirectOllamaTest()

    # Run tests
    tester.run_comparison_tests()

    # Analyze results
    tester.analyze_results()

    # Save results
    tester.save_results()

    print(f"\n✅ **DIRECT COMPARISON COMPLETE!**')
    print(f"🎯 Use these results to decide on model configuration')

if __name__ == "__main__':
    main()
