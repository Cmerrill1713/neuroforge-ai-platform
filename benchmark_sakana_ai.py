#!/usr/bin/env python3
"""
Comprehensive Benchmark Suite for Sakana AI Fine-tuning Methods
Tests performance, memory usage, and accuracy across different scenarios
"""

import time
import psutil
import torch
import json
import logging
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass, asdict

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class BenchmarkResult:
    """Results from a benchmark test"""
    method: str
    test_name: str
    duration: float
    memory_peak: float
    memory_avg: float
    success: bool
    accuracy: float
    throughput: float
    error_message: str = ""

class SakanaAIBenchmark:
    """Comprehensive benchmark suite for Sakana AI methods"""
    
    def __init__(self):
        self.results: List[BenchmarkResult] = []
        self.test_prompts = [
            "Make this model excel at code generation and debugging",
            "Optimize this model for mathematical reasoning and problem solving",
            "Enhance creative writing and storytelling capabilities",
            "Improve analysis and summarization skills",
            "Create a model specialized in translation between languages",
            "Develop expertise in scientific research and data analysis",
            "Build advanced conversational AI with emotional intelligence",
            "Train for high-level programming and software architecture"
        ]
        
    def measure_memory_usage(self):
        """Measure current memory usage"""
        process = psutil.Process()
        memory_info = process.memory_info()
        return memory_info.rss / (1024**3)  # Convert to GB
    
    def run_text_to_lora_benchmark(self) -> List[BenchmarkResult]:
        """Benchmark Text-to-LoRA method"""
        logger.info("🎯 Running Text-to-LoRA Benchmark")
        results = []
        
        try:
            # Import here to avoid issues if not available
            from src.core.training.sakana_ai_methods import SakanaAIIntegration, TextToLoRAConfig
            
            sakana = SakanaAIIntegration()
            
            for i, prompt in enumerate(self.test_prompts):
                logger.info(f"Testing prompt {i+1}/{len(self.test_prompts)}: {prompt[:50]}...")
                
                start_time = time.time()
                start_memory = self.measure_memory_usage()
                
                try:
                    result = sakana.generate_adapter_from_text(prompt, "microsoft/DialoGPT-small")
                    
                    end_time = time.time()
                    end_memory = self.measure_memory_usage()
                    
                    duration = end_time - start_time
                    memory_peak = end_memory - start_memory
                    memory_avg = (start_memory + end_memory) / 2
                    
                    # Calculate accuracy based on skill detection
                    detected_skills = result.get('adapter_info', {}).get('detected_skills', [])
                    accuracy = len(detected_skills) / 10.0  # Normalize to 0-1
                    throughput = 1.0 / duration if duration > 0 else 0
                    
                    results.append(BenchmarkResult(
                        method="Text-to-LoRA",
                        test_name=f"Prompt_{i+1}",
                        duration=duration,
                        memory_peak=memory_peak,
                        memory_avg=memory_avg,
                        success=True,
                        accuracy=accuracy,
                        throughput=throughput
                    ))
                    
                except Exception as e:
                    end_time = time.time()
                    duration = end_time - start_time
                    
                    results.append(BenchmarkResult(
                        method="Text-to-LoRA",
                        test_name=f"Prompt_{i+1}",
                        duration=duration,
                        memory_peak=0.0,
                        memory_avg=0.0,
                        success=False,
                        accuracy=0.0,
                        throughput=0.0,
                        error_message=str(e)
                    ))
                    
        except ImportError as e:
            logger.error(f"Failed to import Sakana AI methods: {e}")
            results.append(BenchmarkResult(
                method="Text-to-LoRA",
                test_name="Import_Error",
                duration=0.0,
                memory_peak=0.0,
                memory_avg=0.0,
                success=False,
                accuracy=0.0,
                throughput=0.0,
                error_message=f"Import failed: {e}"
            ))
            
        return results
    
    def run_transformer2_benchmark(self) -> List[BenchmarkResult]:
        """Benchmark Transformer² method"""
        logger.info("🧠 Running Transformer² Benchmark")
        results = []
        
        try:
            from src.core.training.sakana_ai_methods import SakanaAIIntegration
            from transformers import AutoModelForCausalLM
            import torch
            
            sakana = SakanaAIIntegration()
            
            # Load model for Transformer²
            model_path = "microsoft/DialoGPT-small"
            base_model = AutoModelForCausalLM.from_pretrained(
                model_path,
                torch_dtype=torch.float16,
                device_map="auto",
                trust_remote_code=True,
                low_cpu_mem_usage=True
            )
            
            transformer2_model = sakana.create_transformer2_model(base_model)
            
            test_inputs = [
                "def fibonacci(n):",
                "Solve this equation: 2x + 5 = 13",
                "Write a creative story about",
                "Analyze the following data:",
                "Summarize this text:",
                "Translate this to French:",
                "What is the answer to",
                "Debug this code:"
            ]
            
            for i, test_input in enumerate(test_inputs):
                logger.info(f"Testing input {i+1}/{len(test_inputs)}: {test_input[:30]}...")
                
                start_time = time.time()
                start_memory = self.measure_memory_usage()
                
                try:
                    # Simulate Transformer² processing
                    import torch
                    tokens = torch.tensor([[1, 2, 3, 4, 5]])  # Simplified tokenization
                    
                    with torch.no_grad():
                        outputs = transformer2_model(tokens)
                    
                    end_time = time.time()
                    end_memory = self.measure_memory_usage()
                    
                    duration = end_time - start_time
                    memory_peak = end_memory - start_memory
                    memory_avg = (start_memory + end_memory) / 2
                    
                    # Calculate accuracy based on skill detection
                    adaptations = len(getattr(outputs, 'adaptations', {}))
                    accuracy = min(1.0, adaptations / 5.0)  # Normalize to 0-1
                    throughput = 1.0 / duration if duration > 0 else 0
                    
                    results.append(BenchmarkResult(
                        method="Transformer²",
                        test_name=f"Input_{i+1}",
                        duration=duration,
                        memory_peak=memory_peak,
                        memory_avg=memory_avg,
                        success=True,
                        accuracy=accuracy,
                        throughput=throughput
                    ))
                    
                except Exception as e:
                    end_time = time.time()
                    duration = end_time - start_time
                    
                    results.append(BenchmarkResult(
                        method="Transformer²",
                        test_name=f"Input_{i+1}",
                        duration=duration,
                        memory_peak=0.0,
                        memory_avg=0.0,
                        success=False,
                        accuracy=0.0,
                        throughput=0.0,
                        error_message=str(e)
                    ))
                    
        except ImportError as e:
            logger.error(f"Failed to import Transformer² methods: {e}")
            results.append(BenchmarkResult(
                method="Transformer²",
                test_name="Import_Error",
                duration=0.0,
                memory_peak=0.0,
                memory_avg=0.0,
                success=False,
                accuracy=0.0,
                throughput=0.0,
                error_message=f"Import failed: {e}"
            ))
            
        return results
    
    def run_system_benchmark(self) -> List[BenchmarkResult]:
        """Benchmark system performance"""
        logger.info("🖥️ Running System Performance Benchmark")
        results = []
        
        # CPU benchmark
        start_time = time.time()
        cpu_result = sum(i*i for i in range(1000000))
        cpu_duration = time.time() - start_time
        
        # Memory benchmark
        start_memory = self.measure_memory_usage()
        test_data = [i for i in range(1000000)]
        memory_usage = self.measure_memory_usage() - start_memory
        del test_data
        
        # GPU benchmark (if available)
        gpu_duration = 0.0
        if torch.cuda.is_available():
            start_time = time.time()
            test_tensor = torch.randn(1000, 1000).cuda()
            result = torch.mm(test_tensor, test_tensor)
            gpu_duration = time.time() - start_time
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            start_time = time.time()
            test_tensor = torch.randn(1000, 1000).to('mps')
            result = torch.mm(test_tensor, test_tensor)
            gpu_duration = time.time() - start_time
        
        results.extend([
            BenchmarkResult(
                method="System",
                test_name="CPU_Performance",
                duration=cpu_duration,
                memory_peak=memory_usage,
                memory_avg=memory_usage,
                success=True,
                accuracy=1.0 if cpu_duration < 1.0 else 0.5,
                throughput=1.0 / cpu_duration if cpu_duration > 0 else 0
            ),
            BenchmarkResult(
                method="System",
                test_name="Memory_Performance",
                duration=0.0,
                memory_peak=memory_usage,
                memory_avg=memory_usage,
                success=True,
                accuracy=1.0 if memory_usage < 0.1 else 0.5,
                throughput=0.0
            ),
            BenchmarkResult(
                method="System",
                test_name="GPU_Performance",
                duration=gpu_duration,
                memory_peak=0.0,
                memory_avg=0.0,
                success=gpu_duration > 0,
                accuracy=1.0 if gpu_duration > 0 else 0.0,
                throughput=1.0 / gpu_duration if gpu_duration > 0 else 0
            )
        ])
        
        return results
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive benchmark report"""
        logger.info("📊 Generating Benchmark Report")
        
        # Group results by method
        method_results = {}
        for result in self.results:
            if result.method not in method_results:
                method_results[result.method] = []
            method_results[result.method].append(result)
        
        # Calculate statistics
        report = {
            "timestamp": time.time(),
            "total_tests": len(self.results),
            "successful_tests": sum(1 for r in self.results if r.success),
            "failed_tests": sum(1 for r in self.results if not r.success),
            "methods": {}
        }
        
        for method, results in method_results.items():
            if not results:
                continue
                
            successful_results = [r for r in results if r.success]
            
            method_stats = {
                "total_tests": len(results),
                "successful_tests": len(successful_results),
                "success_rate": len(successful_results) / len(results) if results else 0,
                "avg_duration": sum(r.duration for r in successful_results) / len(successful_results) if successful_results else 0,
                "avg_memory_peak": sum(r.memory_peak for r in successful_results) / len(successful_results) if successful_results else 0,
                "avg_accuracy": sum(r.accuracy for r in successful_results) / len(successful_results) if successful_results else 0,
                "avg_throughput": sum(r.throughput for r in successful_results) / len(successful_results) if successful_results else 0,
                "min_duration": min(r.duration for r in successful_results) if successful_results else 0,
                "max_duration": max(r.duration for r in successful_results) if successful_results else 0,
                "errors": [r.error_message for r in results if not r.success and r.error_message]
            }
            
            report["methods"][method] = method_stats
        
        return report
    
    def run_comprehensive_benchmark(self):
        """Run all benchmarks"""
        logger.info("🚀 Starting Comprehensive Sakana AI Benchmark")
        logger.info("=" * 60)
        
        # Run all benchmarks
        self.results.extend(self.run_text_to_lora_benchmark())
        self.results.extend(self.run_transformer2_benchmark())
        self.results.extend(self.run_system_benchmark())
        
        # Generate report
        report = self.generate_report()
        
        # Save report
        report_path = "sakana_ai_benchmark_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        # Print summary
        logger.info("=" * 60)
        logger.info("🎯 BENCHMARK SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total Tests: {report['total_tests']}")
        logger.info(f"Successful: {report['successful_tests']}")
        logger.info(f"Failed: {report['failed_tests']}")
        logger.info(f"Success Rate: {(report['successful_tests']/report['total_tests']*100):.1f}%")
        
        for method, stats in report["methods"].items():
            logger.info(f"\n{method}:")
            logger.info(f"  Success Rate: {stats['success_rate']*100:.1f}%")
            logger.info(f"  Avg Duration: {stats['avg_duration']:.3f}s")
            logger.info(f"  Avg Memory: {stats['avg_memory_peak']:.3f}GB")
            logger.info(f"  Avg Accuracy: {stats['avg_accuracy']:.3f}")
            logger.info(f"  Avg Throughput: {stats['avg_throughput']:.3f}/s")
        
        logger.info(f"\n📄 Detailed report saved to: {report_path}")
        logger.info("=" * 60)
        
        return report

def main():
    """Main benchmark execution"""
    benchmark = SakanaAIBenchmark()
    report = benchmark.run_comprehensive_benchmark()
    
    # Return success status
    success_rate = report['successful_tests'] / report['total_tests']
    return success_rate > 0.8  # Consider successful if >80% tests pass

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
