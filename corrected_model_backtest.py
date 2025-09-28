#!/usr/bin/env python3
"""
Corrected Model Performance Backtest
Tests each model with identical prompts for accurate comparison
"""

import asyncio
import logging
import time
import statistics
import sys
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.engines.ollama_adapter import OllamaAdapter

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ModelPerformanceResult:
    """Accurate model performance result"""
    model_name: str
    model_key: str
    ollama_name: str
    total_tests: int
    success_rate: float
    average_response_time: float
    median_response_time: float
    min_response_time: float
    max_response_time: float
    average_tokens: float
    tokens_per_second: float
    error_count: int

class CorrectedModelBacktester:
    """Corrected backtesting for accurate model performance comparison"""
    
    def __init__(self, config_path: str = "configs/policies.yaml"):
        self.config_path = config_path
        self.ollama_adapter = OllamaAdapter(config_path)
        self.logger = logging.getLogger(__name__)
        
        # Test prompts of different complexities
        self.test_prompts = {
            "simple": "What is 2+2?",
            "medium": "Explain the concept of machine learning in 2 sentences.",
            "complex": "Write a Python function to implement a binary search algorithm with proper error handling and documentation."
        }
    
    async def initialize(self) -> bool:
        """Initialize the backtesting system."""
        try:
            if await self.ollama_adapter.check_ollama_status():
                logger.info("Corrected backtesting system initialized successfully")
                return True
            else:
                logger.error("Ollama is not running - required for backtesting")
                return False
        except Exception as e:
            logger.error(f"Failed to initialize backtesting system: {e}")
            return False
    
    async def test_model_performance(self, model_key: str, prompt_complexity: str, num_tests: int = 5) -> ModelPerformanceResult:
        """Test a specific model with controlled prompts"""
        
        if model_key not in self.ollama_adapter.models:
            raise ValueError(f"Model {model_key} not found")
        
        model = self.ollama_adapter.models[model_key]
        prompt = self.test_prompts[prompt_complexity]
        
        logger.info(f"Testing {model_key} ({model.name}) with {prompt_complexity} prompts")
        
        response_times = []
        tokens_list = []
        errors = 0
        
        for i in range(num_tests):
            try:
                start_time = time.time()
                response = await self.ollama_adapter.generate_response(
                    model_key=model_key,
                    prompt=f"{prompt} (Test {i+1})",
                    max_tokens=200 if prompt_complexity == "complex" else 50
                )
                end_time = time.time()
                
                response_time = end_time - start_time
                response_times.append(response_time)
                tokens_list.append(response.tokens_generated)
                
                logger.info(f"   Test {i+1}: {response_time:.3f}s, {response.tokens_generated} tokens")
                
            except Exception as e:
                logger.error(f"   Test {i+1}: ❌ Error - {e}")
                errors += 1
        
        if not response_times:
            raise Exception(f"All tests failed for {model_key}")
        
        # Calculate accurate statistics
        success_rate = (num_tests - errors) / num_tests
        avg_response_time = statistics.mean(response_times)
        median_response_time = statistics.median(response_times)
        min_response_time = min(response_times)
        max_response_time = max(response_times)
        avg_tokens = statistics.mean(tokens_list)
        
        # Calculate tokens per second properly
        total_tokens = sum(tokens_list)
        total_time = sum(response_times)
        tokens_per_second = total_tokens / total_time if total_time > 0 else 0.0
        
        return ModelPerformanceResult(
            model_name=model.name,
            model_key=model_key,
            ollama_name=model.ollama_name,
            total_tests=num_tests,
            success_rate=success_rate,
            average_response_time=avg_response_time,
            median_response_time=median_response_time,
            min_response_time=min_response_time,
            max_response_time=max_response_time,
            average_tokens=avg_tokens,
            tokens_per_second=tokens_per_second,
            error_count=errors
        )
    
    async def run_comprehensive_backtest(self) -> Dict[str, List[ModelPerformanceResult]]:
        """Run comprehensive backtest with corrected methodology"""
        
        logger.info("🚀 Starting Corrected Model Performance Backtest")
        logger.info("=" * 70)
        
        if not await self.initialize():
            return {}
        
        results = {}
        
        # Test each model with each prompt complexity
        for prompt_complexity in self.test_prompts.keys():
            logger.info(f"\n📝 Testing with {prompt_complexity} prompts")
            logger.info("-" * 40)
            
            complexity_results = []
            
            for model_key in ["primary", "coding", "lightweight"]:
                if model_key in self.ollama_adapter.models:
                    try:
                        result = await self.test_model_performance(model_key, prompt_complexity)
                        complexity_results.append(result)
                        
                        logger.info(f"✅ {model_key}: {result.average_response_time:.3f}s avg, {result.tokens_per_second:.1f} tokens/sec")
                        
                    except Exception as e:
                        logger.error(f"❌ {model_key}: Failed - {e}")
            
            # Sort by response time (fastest first)
            complexity_results.sort(key=lambda x: x.average_response_time)
            results[prompt_complexity] = complexity_results
        
        return results
    
    def print_summary(self, results: Dict[str, List[ModelPerformanceResult]]):
        """Print comprehensive summary of results"""
        
        logger.info("\n" + "="*70)
        logger.info("🎯 CORRECTED MODEL PERFORMANCE SUMMARY")
        logger.info("="*70)
        
        for prompt_complexity, complexity_results in results.items():
            logger.info(f"\n📊 {prompt_complexity.upper()} PROMPTS:")
            logger.info("-" * 30)
            
            for i, result in enumerate(complexity_results, 1):
                logger.info(f"{i}. {result.model_key} ({result.model_name})")
                logger.info(f"   Response Time: {result.average_response_time:.3f}s avg, {result.median_response_time:.3f}s median")
                logger.info(f"   Range: {result.min_response_time:.3f}s - {result.max_response_time:.3f}s")
                logger.info(f"   Tokens/sec: {result.tokens_per_second:.1f}")
                logger.info(f"   Success Rate: {result.success_rate:.1%}")
                logger.info(f"   Ollama Model: {result.ollama_name}")
        
        # Overall ranking
        logger.info(f"\n🏆 OVERALL RANKING (by average response time):")
        logger.info("-" * 50)
        
        all_results = []
        for complexity_results in results.values():
            all_results.extend(complexity_results)
        
        # Calculate overall average for each model
        model_averages = {}
        for result in all_results:
            if result.model_key not in model_averages:
                model_averages[result.model_key] = []
            model_averages[result.model_key].append(result.average_response_time)
        
        # Sort by overall average
        overall_ranking = []
        for model_key, times in model_averages.items():
            avg_time = statistics.mean(times)
            overall_ranking.append((model_key, avg_time))
        
        overall_ranking.sort(key=lambda x: x[1])
        
        for i, (model_key, avg_time) in enumerate(overall_ranking, 1):
            logger.info(f"{i}. {model_key}: {avg_time:.3f}s average")

async def main():
    """Run corrected model performance backtest"""
    
    backtester = CorrectedModelBacktester()
    results = await backtester.run_comprehensive_backtest()
    backtester.print_summary(results)
    
    logger.info("\n🎉 Corrected backtesting complete!")
    logger.info("This shows the TRUE performance characteristics of each model.")

if __name__ == "__main__":
    asyncio.run(main())
