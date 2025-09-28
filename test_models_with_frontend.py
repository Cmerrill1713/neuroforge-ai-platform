#!/usr/bin/env python3
"""
Test Optimized Models with Frontend - See how they perform and iterate
"""

import asyncio
import json
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

class FrontendModelTester:
    """Test optimized models with the existing frontend"""
    
    def __init__(self):
        self.optimized_models = {
            "ollama": [
                "qwen2.5:7b",      # Balanced performance
                "mistral:7b",       # Good performance  
                "llama3.2:3b",      # Fastest
                "llava:7b",         # Multimodal
                "gpt-oss:20b",      # Large model
                "qwen2.5:72b",      # Very large
                "qwen2.5:14b"       # Large
            ],
            "mlx": [
                "Qwen3-30B-A3B-MLX",  # Best overall (10.1/10)
                "Dia-1.6B"           # Good MLX model
            ],
            "huggingface": [
                "Qwen3-Omni-30B",    # Multimodal
                "Qwen3-Coder-30B"    # Code generation
            ]
        }
        
        self.frontend_tasks = [
            "Improve the chat interface design",
            "Add new features to the code editor", 
            "Enhance the multimodal analysis panel",
            "Optimize the learning dashboard",
            "Add performance monitoring",
            "Improve user experience",
            "Add new AI model integrations",
            "Enhance the overall architecture"
        ]
        
        self.test_results = {}
    
    async def test_model_with_frontend_task(self, model_name: str, task: str) -> Dict[str, Any]:
        """Test a model with a specific frontend task"""
        print(f"🧪 Testing {model_name} with task: {task}")
        
        prompt = f"""You are an expert frontend developer working on a Next.js + TypeScript + Tailwind CSS application. 

TASK: {task}

CONTEXT: We have a comprehensive frontend with:
- Chat interface with 8 AI models
- Monaco code editor with syntax highlighting
- Multimodal analysis panel (LLaVA integration)
- Learning dashboard with progress tracking
- Real-time WebSocket communication
- HRM-enhanced features

Please provide specific, actionable recommendations for improving this frontend. Focus on:
1. Technical implementation details
2. Code examples where applicable
3. Performance optimizations
4. User experience improvements
5. Integration possibilities

Be specific and provide concrete next steps."""
        
        start_time = time.time()
        
        try:
            result = subprocess.run([
                "ollama", "run", model_name, prompt
            ], capture_output=True, text=True, timeout=120)
            
            response_time = time.time() - start_time
            
            if result.returncode == 0:
                response = result.stdout.strip()
                quality_score = self.evaluate_frontend_response(response, task)
                
                return {
                    "model": model_name,
                    "task": task,
                    "response": response,
                    "response_time": response_time,
                    "quality_score": quality_score,
                    "status": "success"
                }
            else:
                return {
                    "model": model_name,
                    "task": task,
                    "response": None,
                    "response_time": response_time,
                    "quality_score": 0,
                    "status": "error",
                    "error": result.stderr
                }
                
        except subprocess.TimeoutExpired:
            return {
                "model": model_name,
                "task": task,
                "response": None,
                "response_time": 120,
                "quality_score": 0,
                "status": "timeout"
            }
        except Exception as e:
            return {
                "model": model_name,
                "task": task,
                "response": None,
                "response_time": 0,
                "quality_score": 0,
                "status": "error",
                "error": str(e)
            }
    
    def evaluate_frontend_response(self, response: str, task: str) -> float:
        """Evaluate frontend development response quality"""
        
        if not response or len(response.strip()) < 50:
            return 0
        
        score = 5.0  # Base score
        
        # Technical depth indicators
        tech_indicators = [
            "typescript", "react", "next.js", "tailwind", "monaco", "websocket",
            "component", "hook", "state", "props", "api", "endpoint",
            "performance", "optimization", "bundle", "lazy", "memo",
            "accessibility", "responsive", "mobile", "desktop"
        ]
        
        tech_score = 0
        for indicator in tech_indicators:
            if indicator.lower() in response.lower():
                tech_score += 0.3
        
        score += min(tech_score, 3)  # Max 3 points for technical depth
        
        # Code example bonus
        if "```" in response or "const " in response or "function " in response:
            score += 1.5
        
        # Specific implementation bonus
        if "implementation" in response.lower() or "specific" in response.lower():
            score += 1
        
        # Architecture thinking bonus
        if "architecture" in response.lower() or "structure" in response.lower():
            score += 1
        
        # Task relevance bonus
        task_keywords = task.lower().split()
        relevance_score = 0
        for keyword in task_keywords:
            if keyword in response.lower():
                relevance_score += 0.2
        
        score += min(relevance_score, 1)  # Max 1 point for relevance
        
        return min(10, max(0, score))
    
    async def run_comprehensive_frontend_test(self):
        """Run comprehensive frontend testing with all optimized models"""
        
        print("🚀 TESTING OPTIMIZED MODELS WITH FRONTEND")
        print("=" * 60)
        
        # Test each model with each frontend task
        for model_name in self.optimized_models["ollama"]:
            print(f"\n📋 Testing Ollama Model: {model_name}")
            print("-" * 40)
            
            model_results = []
            
            for task in self.frontend_tasks[:3]:  # Test with first 3 tasks
                result = await self.test_model_with_frontend_task(model_name, task)
                model_results.append(result)
                
                if result["status"] == "success":
                    print(f"  ✅ {task[:30]}... - {result['quality_score']:.1f}/10 ({result['response_time']:.1f}s)")
                else:
                    print(f"  ❌ {task[:30]}... - {result['status']}")
            
            # Calculate average performance
            successful_results = [r for r in model_results if r["status"] == "success"]
            if successful_results:
                avg_score = sum(r["quality_score"] for r in successful_results) / len(successful_results)
                avg_time = sum(r["response_time"] for r in successful_results) / len(successful_results)
                
                self.test_results[model_name] = {
                    "avg_score": avg_score,
                    "avg_time": avg_time,
                    "success_rate": len(successful_results) / len(model_results),
                    "results": model_results
                }
                
                print(f"  📊 Average: {avg_score:.1f}/10 ({avg_time:.1f}s) - {len(successful_results)}/{len(model_results)} tasks")
            else:
                print(f"  ❌ No successful tasks")
                self.test_results[model_name] = {
                    "avg_score": 0,
                    "avg_time": 0,
                    "success_rate": 0,
                    "results": model_results
                }
        
        # Generate frontend improvement recommendations
        self.generate_frontend_recommendations()
        
        # Save test results
        self.save_test_results()
    
    def generate_frontend_recommendations(self):
        """Generate recommendations based on test results"""
        
        print(f"\n📊 FRONTEND IMPROVEMENT RECOMMENDATIONS")
        print("=" * 50)
        
        # Sort models by performance
        sorted_models = sorted(
            self.test_results.items(),
            key=lambda x: x[1]["avg_score"],
            reverse=True
        )
        
        print(f"\n🏆 TOP PERFORMING MODELS FOR FRONTEND DEVELOPMENT:")
        print("-" * 50)
        
        for i, (model_name, result) in enumerate(sorted_models[:5]):
            print(f"{i+1}. {model_name:<20} {result['avg_score']:5.1f}/10 ({result['avg_time']:5.1f}s)")
        
        # Generate specific recommendations
        print(f"\n💡 SPECIFIC FRONTEND IMPROVEMENTS:")
        print("-" * 40)
        
        best_model = sorted_models[0][0] if sorted_models else None
        if best_model:
            print(f"🎯 Best Model for Frontend: {best_model}")
            print(f"   Use this model for complex frontend architecture decisions")
        
        # Analyze common themes from responses
        all_responses = []
        for model_results in self.test_results.values():
            for result in model_results["results"]:
                if result["response"]:
                    all_responses.append(result["response"])
        
        # Extract common improvement themes
        themes = self.extract_improvement_themes(all_responses)
        
        print(f"\n🔍 COMMON IMPROVEMENT THEMES:")
        for theme, count in themes.items():
            print(f"  {theme}: {count} mentions")
        
        # Generate next steps
        self.generate_next_steps(sorted_models)
    
    def extract_improvement_themes(self, responses: List[str]) -> Dict[str, int]:
        """Extract common improvement themes from responses"""
        
        themes = {
            "Performance Optimization": 0,
            "User Experience": 0,
            "Code Quality": 0,
            "Accessibility": 0,
            "Mobile Responsiveness": 0,
            "Real-time Features": 0,
            "AI Integration": 0,
            "Architecture": 0
        }
        
        for response in responses:
            response_lower = response.lower()
            
            if "performance" in response_lower or "optimization" in response_lower:
                themes["Performance Optimization"] += 1
            if "user experience" in response_lower or "ux" in response_lower:
                themes["User Experience"] += 1
            if "code quality" in response_lower or "typescript" in response_lower:
                themes["Code Quality"] += 1
            if "accessibility" in response_lower or "a11y" in response_lower:
                themes["Accessibility"] += 1
            if "mobile" in response_lower or "responsive" in response_lower:
                themes["Mobile Responsiveness"] += 1
            if "real-time" in response_lower or "websocket" in response_lower:
                themes["Real-time Features"] += 1
            if "ai" in response_lower or "model" in response_lower:
                themes["AI Integration"] += 1
            if "architecture" in response_lower or "structure" in response_lower:
                themes["Architecture"] += 1
        
        return {k: v for k, v in themes.items() if v > 0}
    
    def generate_next_steps(self, sorted_models: List[tuple]):
        """Generate next steps for frontend improvement"""
        
        print(f"\n🚀 NEXT STEPS FOR FRONTEND ITERATION:")
        print("=" * 45)
        
        if sorted_models:
            best_model = sorted_models[0][0]
            print(f"1. 🎯 Use {best_model} for frontend architecture decisions")
            print(f"   - This model scored highest for frontend development tasks")
            print(f"   - Use it for complex technical decisions")
        
        print(f"\n2. 🔧 Implement Performance Optimizations:")
        print(f"   - Add lazy loading for components")
        print(f"   - Implement code splitting")
        print(f"   - Optimize bundle size")
        print(f"   - Add performance monitoring")
        
        print(f"\n3. 🎨 Enhance User Experience:")
        print(f"   - Improve mobile responsiveness")
        print(f"   - Add accessibility features")
        print(f"   - Implement dark mode")
        print(f"   - Add keyboard shortcuts")
        
        print(f"\n4. 🤖 Integrate More AI Models:")
        print(f"   - Add MLX models for specialized tasks")
        print(f"   - Implement model switching")
        print(f"   - Add model performance monitoring")
        print(f"   - Create model-specific interfaces")
        
        print(f"\n5. 📊 Add Advanced Features:")
        print(f"   - Real-time collaboration")
        print(f"   - Advanced analytics")
        print(f"   - Custom model training")
        print(f"   - Plugin system")
        
        print(f"\n6. 🔗 Backend Integration:")
        print(f"   - Connect to your FastAPI server")
        print(f"   - Implement WebSocket communication")
        print(f"   - Add real-time model switching")
        print(f"   - Integrate knowledge base")
    
    def save_test_results(self):
        """Save comprehensive test results"""
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "test_summary": {
                "models_tested": len(self.test_results),
                "tasks_per_model": 3,
                "total_tests": len(self.test_results) * 3
            },
            "model_performance": {
                model: {
                    "avg_score": result["avg_score"],
                    "avg_time": result["avg_time"],
                    "success_rate": result["success_rate"]
                }
                for model, result in self.test_results.items()
            },
            "detailed_results": self.test_results,
            "recommendations": {
                "best_model": max(self.test_results.items(), key=lambda x: x[1]["avg_score"])[0] if self.test_results else None,
                "improvement_areas": self.extract_improvement_themes([
                    r["response"] for model_results in self.test_results.values() 
                    for r in model_results["results"] if r["response"]
                ])
            }
        }
        
        with open("frontend_model_test_results.json", "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"\n💾 Test results saved to: frontend_model_test_results.json")

async def main():
    """Main function"""
    tester = FrontendModelTester()
    await tester.run_comprehensive_frontend_test()

if __name__ == "__main__":
    asyncio.run(main())
