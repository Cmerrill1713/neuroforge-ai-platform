#!/usr/bin/env python3
"""
Test Sakana AI methods with larger models to validate scalability
"""

import time
import logging
import json
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_larger_model():
    """Test Sakana AI methods with a larger model"""
    logger.info("🚀 Testing Sakana AI with Larger Model")
    logger.info("=" * 50)
    
    try:
        from src.core.training.sakana_ai_methods import SakanaAIIntegration
        
        sakana = SakanaAIIntegration()
        
        # Test with Qwen2.5-7B model
        model_path = "Qwen/Qwen2.5-7B-Instruct"
        test_prompt = "Make this model excel at code generation and debugging with advanced algorithms"
        
        logger.info(f"📥 Testing with model: {model_path}")
        logger.info(f"📝 Prompt: {test_prompt}")
        
        start_time = time.time()
        
        # Test Text-to-LoRA with larger model
        logger.info("🎯 Testing Text-to-LoRA with 7B model...")
        try:
            result = sakana.generate_adapter_from_text(test_prompt, model_path)
            
            end_time = time.time()
            duration = end_time - start_time
            
            logger.info(f"✅ Text-to-LoRA Success!")
            logger.info(f"   Duration: {duration:.2f}s")
            logger.info(f"   Skills: {result['adapter_info']['detected_skills']}")
            logger.info(f"   Skill Weights: {len(result['adapter_info']['skill_weights'])} detected")
            
            return {
                "success": True,
                "method": "Text-to-LoRA",
                "model": model_path,
                "duration": duration,
                "skills": result['adapter_info']['detected_skills'],
                "skill_count": len(result['adapter_info']['detected_skills'])
            }
            
        except Exception as e:
            logger.error(f"❌ Text-to-LoRA failed: {e}")
            return {
                "success": False,
                "method": "Text-to-LoRA",
                "model": model_path,
                "error": str(e)
            }
            
    except ImportError as e:
        logger.error(f"❌ Failed to import Sakana AI: {e}")
        return {
            "success": False,
            "error": f"Import failed: {e}"
        }

def test_model_comparison():
    """Compare performance across different model sizes"""
    logger.info("📊 Running Model Size Comparison")
    logger.info("=" * 50)
    
    models = [
        ("microsoft/DialoGPT-small", "Small (117M)"),
        ("microsoft/DialoGPT-medium", "Medium (345M)"),
        # ("Qwen/Qwen2.5-7B-Instruct", "Large (7B)")  # Commented out due to size
    ]
    
    test_prompt = "Optimize this model for mathematical reasoning and problem solving"
    results = []
    
    try:
        from src.core.training.sakana_ai_methods import SakanaAIIntegration
        sakana = SakanaAIIntegration()
        
        for model_path, model_name in models:
            logger.info(f"🧪 Testing {model_name} ({model_path})")
            
            start_time = time.time()
            try:
                result = sakana.generate_adapter_from_text(test_prompt, model_path)
                duration = time.time() - start_time
                
                logger.info(f"✅ {model_name} Success!")
                logger.info(f"   Duration: {duration:.2f}s")
                logger.info(f"   Skills: {result['adapter_info']['detected_skills']}")
                
                results.append({
                    "model": model_name,
                    "path": model_path,
                    "duration": duration,
                    "skills": result['adapter_info']['detected_skills'],
                    "success": True
                })
                
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"❌ {model_name} failed: {e}")
                results.append({
                    "model": model_name,
                    "path": model_path,
                    "duration": duration,
                    "error": str(e),
                    "success": False
                })
    
    except ImportError as e:
        logger.error(f"❌ Failed to import Sakana AI: {e}")
        return []
    
    return results

def main():
    """Main test execution"""
    logger.info("🎯 Starting Larger Model Testing")
    logger.info("=" * 60)
    
    # Test single larger model
    large_model_result = test_larger_model()
    
    # Test model comparison
    comparison_results = test_model_comparison()
    
    # Generate summary report
    report = {
        "timestamp": time.time(),
        "large_model_test": large_model_result,
        "model_comparison": comparison_results,
        "summary": {
            "total_models_tested": len(comparison_results) + (1 if large_model_result.get("success") else 0),
            "successful_tests": len([r for r in comparison_results if r.get("success")]) + (1 if large_model_result.get("success") else 0),
            "failed_tests": len([r for r in comparison_results if not r.get("success")]) + (0 if large_model_result.get("success") else 1)
        }
    }
    
    # Save report
    report_path = "larger_model_test_report.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    # Print summary
    logger.info("=" * 60)
    logger.info("🎯 LARGER MODEL TEST SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total Models Tested: {report['summary']['total_models_tested']}")
    logger.info(f"Successful Tests: {report['summary']['successful_tests']}")
    logger.info(f"Failed Tests: {report['summary']['failed_tests']}")
    
    if comparison_results:
        logger.info("\n📊 Model Comparison Results:")
        for result in comparison_results:
            status = "✅" if result.get("success") else "❌"
            duration = f"{result.get('duration', 0):.2f}s" if result.get("success") else "N/A"
            skills = len(result.get('skills', [])) if result.get("success") else 0
            logger.info(f"  {status} {result['model']}: {duration}, {skills} skills")
    
    logger.info(f"\n📄 Detailed report saved to: {report_path}")
    logger.info("=" * 60)
    
    return report['summary']['successful_tests'] > 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
