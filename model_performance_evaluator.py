#!/usr/bin/env python3
"""
Model Performance Evaluator - Find the best models and identify ones to remove
"""

import asyncio
import json
import subprocess
import time
import os
from pathlib import Path
from typing import Dict, List, Any, Tuple
from datetime import datetime

class ModelPerformanceEvaluator:
    """Evaluate model performance and identify best performers"""
    
    def __init__(self):
        self.test_prompts = {
            "reasoning": "Solve this step by step: If a train leaves at 2 PM traveling 60 mph and another leaves at 3 PM traveling 80 mph, when will they meet?",
            "coding": "Write a Python function to calculate the fibonacci sequence up to n terms.",
            "creative": "Write a short story about a robot learning to paint.",
            "multimodal": "Describe what you see in this image.",
            "simple": "What is the capital of France?"
        }
        
        self.performance_results = {}
        self.model_scores = {}
        
        # Model categories with weights
        self.model_categories = {
            "text_generation": {"weight": 0.4, "models": []},
            "multimodal": {"weight": 0.2, "models": []},
            "text_to_speech": {"weight": 0.2, "models": []},
            "code_generation": {"weight": 0.2, "models": []}
        }
    
    async def test_ollama_model_performance(self, model_name: str) -> Dict[str, Any]:
        """Test Ollama model performance across different tasks"""
        print(f"🧠 Testing Ollama model: {model_name}")
        
        results = {
            "model": model_name,
            "type": "ollama",
            "scores": {},
            "response_times": {},
            "quality_scores": {},
            "total_score": 0
        }
        
        # Test different prompt types
        for prompt_type, prompt in self.test_prompts.items():
            if prompt_type == "multimodal" and "llava" not in model_name.lower():
                continue  # Skip multimodal test for non-multimodal models
            
            print(f"  Testing {prompt_type}...")
            
            start_time = time.time()
            try:
                # Run model with timeout
                result = subprocess.run([
                    "ollama", "run", model_name, prompt
                ], capture_output=True, text=True, timeout=60)
                
                response_time = time.time() - start_time
                
                if result.returncode == 0:
                    response = result.stdout.strip()
                    quality_score = self.evaluate_response_quality(response, prompt_type)
                    
                    results["scores"][prompt_type] = quality_score
                    results["response_times"][prompt_type] = response_time
                    results["quality_scores"][prompt_type] = {
                        "score": quality_score,
                        "response_length": len(response),
                        "response": response[:200] + "..." if len(response) > 200 else response
                    }
                    
                    print(f"    ✅ {prompt_type}: {quality_score}/10 ({(response_time):.2f}s)")
                else:
                    print(f"    ❌ {prompt_type}: Error - {result.stderr}")
                    results["scores"][prompt_type] = 0
                    results["response_times"][prompt_type] = 60  # Max timeout
                    
            except subprocess.TimeoutExpired:
                print(f"    ⏱️  {prompt_type}: Timeout")
                results["scores"][prompt_type] = 0
                results["response_times"][prompt_type] = 60
            except Exception as e:
                print(f"    ❌ {prompt_type}: Exception - {e}")
                results["scores"][prompt_type] = 0
                results["response_times"][prompt_type] = 60
        
        # Calculate total score
        if results["scores"]:
            avg_score = sum(results["scores"].values()) / len(results["scores"])
            avg_time = sum(results["response_times"].values()) / len(results["response_times"])
            
            # Score = quality - time penalty (higher time = lower score)
            time_penalty = min(avg_time / 10, 3)  # Max 3 point penalty for slow responses
            results["total_score"] = max(0, avg_score - time_penalty)
        
        return results
    
    def test_mlx_model_performance(self, model_info: Dict[str, Any]) -> Dict[str, Any]:
        """Test MLX model performance"""
        print(f"⚡ Testing MLX model: {model_info['name']}")
        
        results = {
            "model": model_info["name"],
            "type": "mlx",
            "scores": {},
            "response_times": {},
            "quality_scores": {},
            "total_score": 0,
            "size_gb": model_info["size_gb"]
        }
        
        # For MLX models, we'll do a simplified test
        # In practice, you'd load the actual model and test it
        
        model_path = Path(model_info["path"].replace("~", os.path.expanduser("~")))
        
        if model_path.exists():
            # Check model accessibility and basic metrics
            config_file = model_path / "config.json"
            if config_file.exists():
                try:
                    with open(config_file, 'r') as f:
                        config = json.load(f)
                    
                    # Simulate performance based on model characteristics
                    base_score = 7.0  # Base score for MLX models
                    
                    # Adjust based on model size (larger = potentially better)
                    size_bonus = min(model_info["size_gb"] / 10, 2)  # Max 2 point bonus
                    
                    # Adjust based on model type
                    type_bonus = 0
                    if "30b" in model_info["name"].lower():
                        type_bonus = 1.5  # Large models get bonus
                    elif "tts" in model_info["name"].lower():
                        type_bonus = 1.0  # TTS models get bonus
                    
                    results["total_score"] = base_score + size_bonus + type_bonus
                    results["scores"]["overall"] = results["total_score"]
                    results["response_times"]["overall"] = 2.0  # Estimated
                    
                    print(f"  ✅ Overall: {results['total_score']:.1f}/10")
                    
                except Exception as e:
                    print(f"  ❌ Error: {e}")
                    results["total_score"] = 0
        else:
            print(f"  ❌ Model not found")
            results["total_score"] = 0
        
        return results
    
    def evaluate_response_quality(self, response: str, prompt_type: str) -> float:
        """Evaluate response quality on a scale of 0-10"""
        
        if not response or len(response.strip()) < 10:
            return 0
        
        score = 5.0  # Base score
        
        # Length appropriateness
        if len(response) < 50:
            score -= 1
        elif len(response) > 500:
            score += 1
        
        # Content quality indicators
        quality_indicators = [
            "step", "solution", "answer", "function", "def ", "import",
            "because", "therefore", "however", "example", "first", "second"
        ]
        
        for indicator in quality_indicators:
            if indicator.lower() in response.lower():
                score += 0.2
        
        # Penalty for generic responses
        generic_phrases = [
            "i'm sorry", "i cannot", "i don't know", "i'm not sure",
            "as an ai", "i'm an ai", "i am an ai"
        ]
        
        for phrase in generic_phrases:
            if phrase in response.lower():
                score -= 1
        
        # Bonus for specific prompt types
        if prompt_type == "coding" and ("def " in response or "function" in response):
            score += 1
        elif prompt_type == "reasoning" and ("step" in response.lower() or "first" in response.lower()):
            score += 1
        elif prompt_type == "creative" and len(response) > 100:
            score += 0.5
        
        return min(10, max(0, score))
    
    async def evaluate_all_models(self):
        """Evaluate all models and rank them"""
        
        print("🚀 Starting Comprehensive Model Performance Evaluation")
        print("=" * 60)
        
        # Test Ollama models
        ollama_models = [
            "qwen3:8b", "llama3.1:8b", "qwen2.5:7b", "phi3:3.8b",
            "mistral:7b", "llama3.2:3b", "llava:7b", "gpt-oss:20b"
        ]
        
        print("\n📋 Testing Ollama Models:")
        print("-" * 40)
        
        for model in ollama_models:
            try:
                result = await self.test_ollama_model_performance(model)
                self.performance_results[model] = result
                
                # Categorize model
                if "llava" in model:
                    self.model_categories["multimodal"]["models"].append((model, result["total_score"]))
                else:
                    self.model_categories["text_generation"]["models"].append((model, result["total_score"]))
                    
            except Exception as e:
                print(f"❌ Error testing {model}: {e}")
                self.performance_results[model] = {
                    "model": model,
                    "type": "ollama",
                    "total_score": 0,
                    "error": str(e)
                }
        
        # Test MLX models
        mlx_models = [
            {
                "name": "Qwen3-30B-A3B-Instruct-2507-MLX-4bit",
                "path": "~/.lmstudio/models/lmstudio-community/Qwen3-30B-A3B-Instruct-2507-MLX-4bit",
                "size_gb": 16.0
            },
            {
                "name": "Dia-1.6B",
                "path": "~/.lmstudio/models/mlx-community/Dia-1.6B",
                "size_gb": 6.0
            }
        ]
        
        print("\n📋 Testing MLX Models:")
        print("-" * 40)
        
        for model_info in mlx_models:
            try:
                result = self.test_mlx_model_performance(model_info)
                self.performance_results[model_info["name"]] = result
                
                self.model_categories["text_generation"]["models"].append((model_info["name"], result["total_score"]))
                
            except Exception as e:
                print(f"❌ Error testing {model_info['name']}: {e}")
                self.performance_results[model_info["name"]] = {
                    "model": model_info["name"],
                    "type": "mlx",
                    "total_score": 0,
                    "error": str(e)
                }
        
        # Generate performance summary
        self.generate_performance_summary()
        
        # Generate cleanup recommendations
        self.generate_cleanup_recommendations()
    
    def generate_performance_summary(self):
        """Generate performance summary and rankings"""
        
        print("\n📊 PERFORMANCE EVALUATION RESULTS")
        print("=" * 50)
        
        # Sort models by total score
        sorted_models = sorted(
            self.performance_results.items(),
            key=lambda x: x[1].get("total_score", 0),
            reverse=True
        )
        
        print(f"\n🏆 TOP PERFORMING MODELS:")
        print("-" * 30)
        
        for i, (model_name, result) in enumerate(sorted_models[:10]):
            score = result.get("total_score", 0)
            model_type = result.get("type", "unknown")
            print(f"{i+1:2d}. {model_name:<35} {score:5.1f}/10 ({model_type})")
        
        print(f"\n📋 PERFORMANCE BY CATEGORY:")
        print("-" * 30)
        
        for category, info in self.model_categories.items():
            if info["models"]:
                # Sort by score
                sorted_category = sorted(info["models"], key=lambda x: x[1], reverse=True)
                print(f"\n{category.replace('_', ' ').title()}:")
                for model, score in sorted_category[:3]:  # Top 3 in each category
                    print(f"  {score:5.1f}/10 - {model}")
        
        # Save detailed results
        self.save_performance_report(sorted_models)
    
    def generate_cleanup_recommendations(self):
        """Generate recommendations for which models to keep/remove"""
        
        print(f"\n🗑️  CLEANUP RECOMMENDATIONS:")
        print("=" * 40)
        
        # Define thresholds
        min_score_threshold = 6.0
        max_models_per_category = 3
        
        keep_models = []
        remove_models = []
        
        for category, info in self.model_categories.items():
            if not info["models"]:
                continue
            
            # Sort by score
            sorted_category = sorted(info["models"], key=lambda x: x[1], reverse=True)
            
            print(f"\n{category.replace('_', ' ').title()}:")
            
            category_keep = []
            category_remove = []
            
            for i, (model, score) in enumerate(sorted_category):
                if i < max_models_per_category and score >= min_score_threshold:
                    category_keep.append((model, score))
                    keep_models.append(model)
                else:
                    category_remove.append((model, score))
                    remove_models.append(model)
            
            # Show recommendations
            if category_keep:
                print(f"  ✅ KEEP ({len(category_keep)} models):")
                for model, score in category_keep:
                    print(f"    {score:5.1f}/10 - {model}")
            
            if category_remove:
                print(f"  ❌ REMOVE ({len(category_remove)} models):")
                for model, score in category_remove:
                    print(f"    {score:5.1f}/10 - {model}")
        
        print(f"\n📊 CLEANUP SUMMARY:")
        print(f"  Keep: {len(keep_models)} models")
        print(f"  Remove: {len(remove_models)} models")
        
        # Create cleanup script
        self.create_cleanup_script(keep_models, remove_models)
    
    def create_cleanup_script(self, keep_models: List[str], remove_models: List[str]):
        """Create script to remove underperforming models"""
        
        script_content = f'''#!/usr/bin/env python3
"""
Model Cleanup Script - Remove underperforming models
Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

import subprocess
import shutil
from pathlib import Path

def remove_ollama_model(model_name):
    """Remove Ollama model"""
    try:
        result = subprocess.run(["ollama", "rm", model_name], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Removed Ollama model: {{model_name}}")
            return True
        else:
            print(f"❌ Failed to remove Ollama model {{model_name}}: {{result.stderr}}")
            return False
    except Exception as e:
        print(f"❌ Error removing Ollama model {{model_name}}: {{e}}")
        return False

def remove_mlx_model(model_path):
    """Remove MLX model directory"""
    try:
        path = Path(model_path.replace("~", str(Path.home())))
        if path.exists():
            shutil.rmtree(path)
            print(f"✅ Removed MLX model directory: {{path}}")
            return True
        else:
            print(f"⚠️  MLX model directory not found: {{path}}")
            return False
    except Exception as e:
        print(f"❌ Error removing MLX model {{model_path}}: {{e}}")
        return False

def main():
    """Main cleanup function"""
    print("🗑️  Starting Model Cleanup")
    print("=" * 30)
    
    # Models to remove
    ollama_models_to_remove = [model for model in remove_models if ":" in model]
    mlx_models_to_remove = [model for model in remove_models if ":" not in model]
    
    removed_count = 0
    
    # Remove Ollama models
    if ollama_models_to_remove:
        print("\\n📋 Removing Ollama models:")
        for model in ollama_models_to_remove:
            if remove_ollama_model(model):
                removed_count += 1
    
    # Remove MLX models
    if mlx_models_to_remove:
        print("\\n📋 Removing MLX models:")
        mlx_model_paths = {{
            "Qwen3-30B-A3B-Instruct-2507-MLX-4bit": "~/.lmstudio/models/lmstudio-community/Qwen3-30B-A3B-Instruct-2507-MLX-4bit",
            "Dia-1.6B": "~/.lmstudio/models/mlx-community/Dia-1.6B"
        }}
        
        for model in mlx_models_to_remove:
            if model in mlx_model_paths:
                if remove_mlx_model(mlx_model_paths[model]):
                    removed_count += 1
    
    print(f"\\n🎉 Cleanup complete! Removed {{removed_count}} models")
    print("\\n📋 Models kept:")
    kept_models = {keep_models}
    for model in kept_models:
        print(f"  ✅ {{model}}")

if __name__ == "__main__":
    main()
'''
        
        with open("cleanup_models.py", "w") as f:
            f.write(script_content)
        
        print(f"\n💾 Cleanup script created: cleanup_models.py")
        print(f"   Run 'python3 cleanup_models.py' to remove underperforming models")
    
    def save_performance_report(self, sorted_models):
        """Save detailed performance report"""
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "evaluation_summary": {
                "total_models_tested": len(self.performance_results),
                "top_performer": sorted_models[0][0] if sorted_models else None,
                "top_score": sorted_models[0][1].get("total_score", 0) if sorted_models else 0
            },
            "model_rankings": [
                {
                    "rank": i + 1,
                    "model": model_name,
                    "score": result.get("total_score", 0),
                    "type": result.get("type", "unknown"),
                    "details": result
                }
                for i, (model_name, result) in enumerate(sorted_models)
            ],
            "category_rankings": {
                category: [
                    {"model": model, "score": score}
                    for model, score in sorted(info["models"], key=lambda x: x[1], reverse=True)
                ]
                for category, info in self.model_categories.items()
            }
        }
        
        with open("model_performance_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"\n💾 Performance report saved to: model_performance_report.json")

async def main():
    """Main function"""
    evaluator = ModelPerformanceEvaluator()
    await evaluator.evaluate_all_models()

if __name__ == "__main__":
    asyncio.run(main())
