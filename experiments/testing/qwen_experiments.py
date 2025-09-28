#!/usr/bin/env python3
"""
Comprehensive Qwen3-Omni-30B-A3B-Instruct Experimentation Framework

This script provides extensive testing capabilities for the Qwen3-Omni model including:
- Basic text generation
- Multimodal capabilities (text, image, audio, video)
- Performance benchmarking
- Memory usage monitoring
- Various inference configurations
"""

import os
import sys
import time
import json
import logging
import argparse
import traceback
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import psutil
import torch
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM, 
    AutoProcessor,
    BitsAndBytesConfig,
    GenerationConfig
)
from qwen_omni_utils import (
    QwenOmniProcessor,
    QwenOmniForConditionalGeneration,
    QwenOmniConfig
)
from PIL import Image
import numpy as np

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('qwen_experiments.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class QwenExperimentSuite:
    """Comprehensive experimentation suite for Qwen3-Omni model"""
    
    def __init__(self, model_path: str, device: str = "auto"):
        self.model_path = Path(model_path)
        self.device = device
        self.model = None
        self.tokenizer = None
        self.processor = None
        self.results = {}
        
        # Performance tracking
        self.performance_metrics = {
            "load_time": 0,
            "inference_times": [],
            "memory_usage": [],
            "gpu_memory": []
        }
        
    def log_system_info(self):
        """Log system information and model details"""
        logger.info("=== System Information ===")
        logger.info(f"Python version: {sys.version}")
        logger.info(f"PyTorch version: {torch.__version__}")
        logger.info(f"CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            logger.info(f"CUDA version: {torch.version.cuda}")
            logger.info(f"GPU count: {torch.cuda.device_count()}")
            for i in range(torch.cuda.device_count()):
                logger.info(f"GPU {i}: {torch.cuda.get_device_name(i)}")
        
        logger.info(f"CPU cores: {psutil.cpu_count()}")
        logger.info(f"RAM: {psutil.virtual_memory().total / (1024**3):.2f} GB")
        logger.info(f"Model path: {self.model_path}")
        
    def load_model(self, quantization: str = "none", max_memory: Optional[Dict] = None):
        """Load the model with various configurations"""
        logger.info(f"Loading model from {self.model_path}")
        start_time = time.time()
        
        try:
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_path,
                trust_remote_code=True
            )
            
            # Configure quantization if requested
            quantization_config = None
            if quantization == "4bit":
                quantization_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type="nf4"
                )
            elif quantization == "8bit":
                quantization_config = BitsAndBytesConfig(
                    load_in_8bit=True
                )
            
            # Load model
            model_kwargs = {
                "trust_remote_code": True,
                "torch_dtype": torch.float16 if quantization == "none" else None,
                "device_map": self.device,
            }
            
            if quantization_config:
                model_kwargs["quantization_config"] = quantization_config
            
            if max_memory:
                model_kwargs["max_memory"] = max_memory
                
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                **model_kwargs
            )
            
            # Load processor for multimodal capabilities
            try:
                self.processor = AutoProcessor.from_pretrained(
                    self.model_path,
                    trust_remote_code=True
                )
                logger.info("Multimodal processor loaded successfully")
            except Exception as e:
                logger.warning(f"Could not load multimodal processor: {e}")
                self.processor = None
            
            self.performance_metrics["load_time"] = time.time() - start_time
            logger.info(f"Model loaded successfully in {self.performance_metrics['load_time']:.2f} seconds")
            
            # Log model info
            total_params = sum(p.numel() for p in self.model.parameters())
            trainable_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
            logger.info(f"Total parameters: {total_params:,}")
            logger.info(f"Trainable parameters: {trainable_params:,}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            logger.error(traceback.format_exc())
            return False
    
    def get_memory_usage(self):
        """Get current memory usage"""
        process = psutil.Process()
        memory_info = process.memory_info()
        
        memory_data = {
            "rss_gb": memory_info.rss / (1024**3),
            "vms_gb": memory_info.vms / (1024**3),
            "system_ram_percent": psutil.virtual_memory().percent
        }
        
        if torch.cuda.is_available():
            memory_data.update({
                "gpu_memory_allocated_gb": torch.cuda.memory_allocated() / (1024**3),
                "gpu_memory_reserved_gb": torch.cuda.memory_reserved() / (1024**3),
                "gpu_memory_max_allocated_gb": torch.cuda.max_memory_allocated() / (1024**3)
            })
        
        return memory_data
    
    def generate_text(self, prompt: str, **generation_kwargs) -> Dict[str, Any]:
        """Generate text from a prompt"""
        logger.info(f"Generating text for prompt: {prompt[:100]}...")
        
        # Default generation config
        default_config = {
            "max_new_tokens": 512,
            "temperature": 0.7,
            "top_p": 0.9,
            "do_sample": True,
            "pad_token_id": self.tokenizer.eos_token_id,
            "eos_token_id": self.tokenizer.eos_token_id,
        }
        default_config.update(generation_kwargs)
        
        start_time = time.time()
        memory_before = self.get_memory_usage()
        
        try:
            # Tokenize input
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
            
            # Generate
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    **default_config
                )
            
            # Decode output
            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            response_text = generated_text[len(prompt):].strip()
            
            inference_time = time.time() - start_time
            memory_after = self.get_memory_usage()
            
            result = {
                "prompt": prompt,
                "response": response_text,
                "inference_time": inference_time,
                "memory_before": memory_before,
                "memory_after": memory_after,
                "generation_config": default_config,
                "input_tokens": inputs.input_ids.shape[1],
                "output_tokens": outputs.shape[1] - inputs.input_ids.shape[1],
                "tokens_per_second": (outputs.shape[1] - inputs.input_ids.shape[1]) / inference_time
            }
            
            self.performance_metrics["inference_times"].append(inference_time)
            self.performance_metrics["memory_usage"].append(memory_after)
            
            logger.info(f"Generated {result['output_tokens']} tokens in {inference_time:.2f}s "
                       f"({result['tokens_per_second']:.2f} tok/s)")
            
            return result
            
        except Exception as e:
            logger.error(f"Text generation failed: {e}")
            logger.error(traceback.format_exc())
            return {"error": str(e), "prompt": prompt}
    
    def test_multimodal(self, text_prompt: str, image_path: Optional[str] = None, 
                       audio_path: Optional[str] = None, video_path: Optional[str] = None):
        """Test multimodal capabilities"""
        if not self.processor:
            logger.warning("No processor available for multimodal testing")
            return {"error": "No multimodal processor available"}
        
        logger.info("Testing multimodal capabilities")
        
        try:
            inputs = {}
            
            # Add text
            inputs["text"] = text_prompt
            
            # Add image if provided
            if image_path and os.path.exists(image_path):
                image = Image.open(image_path)
                inputs["images"] = [image]
                logger.info(f"Added image: {image_path}")
            
            # Add audio if provided
            if audio_path and os.path.exists(audio_path):
                # Note: Audio processing would need specific implementation
                logger.info(f"Audio support not yet implemented: {audio_path}")
            
            # Add video if provided
            if video_path and os.path.exists(video_path):
                # Note: Video processing would need specific implementation
                logger.info(f"Video support not yet implemented: {video_path}")
            
            # Process inputs
            processed_inputs = self.processor(**inputs, return_tensors="pt")
            
            # Generate response
            start_time = time.time()
            with torch.no_grad():
                outputs = self.model.generate(
                    **processed_inputs,
                    max_new_tokens=512,
                    temperature=0.7,
                    do_sample=True
                )
            
            inference_time = time.time() - start_time
            
            # Decode response
            response = self.processor.decode(outputs[0], skip_special_tokens=True)
            
            result = {
                "prompt": text_prompt,
                "image_path": image_path,
                "response": response,
                "inference_time": inference_time,
                "inputs_processed": list(inputs.keys())
            }
            
            logger.info(f"Multimodal generation completed in {inference_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Multimodal generation failed: {e}")
            logger.error(traceback.format_exc())
            return {"error": str(e)}
    
    def benchmark_performance(self, test_prompts: List[str], iterations: int = 5):
        """Run performance benchmarks"""
        logger.info(f"Running performance benchmark with {len(test_prompts)} prompts, {iterations} iterations each")
        
        results = {
            "prompts": test_prompts,
            "iterations": iterations,
            "results": []
        }
        
        for i, prompt in enumerate(test_prompts):
            logger.info(f"Benchmarking prompt {i+1}/{len(test_prompts)}")
            prompt_results = []
            
            for j in range(iterations):
                result = self.generate_text(prompt, max_new_tokens=256)
                if "error" not in result:
                    prompt_results.append({
                        "iteration": j,
                        "inference_time": result["inference_time"],
                        "tokens_per_second": result["tokens_per_second"],
                        "memory_usage": result["memory_after"]
                    })
                else:
                    logger.warning(f"Iteration {j} failed: {result['error']}")
            
            if prompt_results:
                avg_time = sum(r["inference_time"] for r in prompt_results) / len(prompt_results)
                avg_tps = sum(r["tokens_per_second"] for r in prompt_results) / len(prompt_results)
                
                results["results"].append({
                    "prompt_index": i,
                    "prompt": prompt,
                    "iterations_completed": len(prompt_results),
                    "average_inference_time": avg_time,
                    "average_tokens_per_second": avg_tps,
                    "individual_results": prompt_results
                })
        
        return results
    
    def run_comprehensive_tests(self):
        """Run a comprehensive test suite"""
        logger.info("Starting comprehensive test suite")
        
        test_results = {
            "timestamp": time.time(),
            "system_info": self.get_memory_usage(),
            "tests": {}
        }
        
        # Test 1: Basic text generation
        logger.info("Test 1: Basic text generation")
        basic_prompts = [
            "Explain quantum computing in simple terms.",
            "Write a short story about a robot learning to paint.",
            "What are the key principles of machine learning?",
            "Describe the process of photosynthesis.",
            "How does blockchain technology work?"
        ]
        
        for i, prompt in enumerate(basic_prompts):
            result = self.generate_text(prompt)
            test_results["tests"][f"basic_text_{i}"] = result
        
        # Test 2: Multimodal (if processor available)
        if self.processor:
            logger.info("Test 2: Multimodal capabilities")
            # Look for sample images in the project
            sample_images = []
            for ext in [".jpg", ".jpeg", ".png", ".bmp"]:
                sample_images.extend(Path(".").glob(f"samples/*{ext}"))
                sample_images.extend(Path(".").glob(f"*{ext}"))
            
            if sample_images:
                image_path = str(sample_images[0])
                result = self.test_multimodal(
                    "Describe what you see in this image in detail.",
                    image_path=image_path
                )
                test_results["tests"]["multimodal_image"] = result
            else:
                logger.info("No sample images found for multimodal testing")
        
        # Test 3: Performance benchmark
        logger.info("Test 3: Performance benchmark")
        benchmark_prompts = [
            "Summarize the main points of artificial intelligence.",
            "Explain the concept of neural networks.",
            "Describe the benefits of renewable energy."
        ]
        
        benchmark_results = self.benchmark_performance(benchmark_prompts, iterations=3)
        test_results["tests"]["performance_benchmark"] = benchmark_results
        
        # Test 4: Different generation configurations
        logger.info("Test 4: Generation configuration testing")
        config_tests = [
            {"temperature": 0.1, "name": "low_temp"},
            {"temperature": 0.9, "name": "high_temp"},
            {"top_p": 0.5, "name": "low_top_p"},
            {"top_p": 0.95, "name": "high_top_p"},
            {"max_new_tokens": 100, "name": "short_response"},
            {"max_new_tokens": 1000, "name": "long_response"}
        ]
        
        test_prompt = "Explain the importance of data privacy in the digital age."
        for config in config_tests:
            name = config.pop("name")
            result = self.generate_text(test_prompt, **config)
            test_results["tests"][f"config_{name}"] = result
        
        # Save results
        results_file = f"qwen_test_results_{int(time.time())}.json"
        with open(results_file, "w") as f:
            json.dump(test_results, f, indent=2, default=str)
        
        logger.info(f"Comprehensive test suite completed. Results saved to {results_file}")
        return test_results
    
    def cleanup(self):
        """Clean up resources"""
        if self.model:
            del self.model
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

def main():
    parser = argparse.ArgumentParser(description="Qwen3-Omni Comprehensive Experimentation Suite")
    parser.add_argument("--model_path", default="./Qwen3-Omni-30B-A3B-Instruct", 
                       help="Path to the model directory")
    parser.add_argument("--device", default="auto", choices=["auto", "cpu", "cuda", "mps"],
                       help="Device to run the model on")
    parser.add_argument("--quantization", default="none", choices=["none", "4bit", "8bit"],
                       help="Quantization method")
    parser.add_argument("--test", choices=["basic", "multimodal", "benchmark", "comprehensive"],
                       default="comprehensive", help="Type of test to run")
    parser.add_argument("--prompt", help="Custom prompt for basic testing")
    parser.add_argument("--image", help="Image path for multimodal testing")
    parser.add_argument("--max_memory", type=float, help="Maximum memory usage in GB")
    
    args = parser.parse_args()
    
    # Setup max memory if specified
    max_memory = None
    if args.max_memory:
        max_memory = {0: f"{args.max_memory}GB"}
    
    # Initialize experiment suite
    suite = QwenExperimentSuite(args.model_path, args.device)
    suite.log_system_info()
    
    try:
        # Load model
        if not suite.load_model(args.quantization, max_memory):
            logger.error("Failed to load model. Exiting.")
            return 1
        
        # Run selected test
        if args.test == "basic":
            prompt = args.prompt or "Hello, how are you today?"
            result = suite.generate_text(prompt)
            print(f"Response: {result.get('response', result.get('error', 'Unknown error'))}")
            
        elif args.test == "multimodal":
            prompt = args.prompt or "Describe what you see in this image."
            result = suite.test_multimodal(prompt, args.image)
            print(f"Response: {result.get('response', result.get('error', 'Unknown error'))}")
            
        elif args.test == "benchmark":
            test_prompts = [
                "Explain machine learning concepts.",
                "Write a creative story.",
                "Analyze the benefits of renewable energy."
            ]
            results = suite.benchmark_performance(test_prompts, iterations=3)
            print(f"Benchmark results: {json.dumps(results, indent=2, default=str)}")
            
        elif args.test == "comprehensive":
            results = suite.run_comprehensive_tests()
            print(f"Comprehensive test completed. Check logs and result files.")
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("Experiment interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Experiment failed: {e}")
        logger.error(traceback.format_exc())
        return 1
    finally:
        suite.cleanup()

if __name__ == "__main__":
    sys.exit(main())
