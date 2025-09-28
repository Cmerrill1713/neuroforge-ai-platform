#!/usr/bin/env python3
"""
Controlled Qwen3-Omni Test

This script performs a controlled test of the Qwen3-Omni model with proper
memory management and inference demonstration.
"""

import os
import torch
import logging
import time
import psutil
from transformers import (
    AutoTokenizer, 
    Qwen3OmniMoeForConditionalGeneration
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_memory_usage():
    """Get current memory usage"""
    memory = psutil.virtual_memory()
    return {
        'total_gb': memory.total / 1024**3,
        'used_gb': memory.used / 1024**3,
        'available_gb': memory.available / 1024**3,
        'percent': memory.percent
    }

def test_qwen_controlled():
    """Controlled test of Qwen3-Omni model"""
    logger.info("🧪 Controlled Qwen3-Omni Model Test")
    logger.info("=" * 50)
    
    model_path = "./Qwen3-Omni-30B-A3B-Instruct"
    
    if not os.path.exists(model_path):
        logger.error(f"❌ Model not found at {model_path}")
        return False
    
    # Initial memory check
    initial_memory = get_memory_usage()
    logger.info(f"📊 Initial Memory: {initial_memory['used_gb']:.1f}GB used / {initial_memory['total_gb']:.1f}GB total")
    
    try:
        # Load tokenizer
        logger.info("📥 Loading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
        logger.info("✅ Tokenizer loaded successfully")
        
        # Memory check after tokenizer
        tokenizer_memory = get_memory_usage()
        logger.info(f"📊 After Tokenizer: {tokenizer_memory['used_gb']:.1f}GB used")
        
        # Load model with controlled settings
        logger.info("📥 Loading model with controlled memory usage...")
        start_time = time.time()
        
        model = Qwen3OmniMoeForConditionalGeneration.from_pretrained(
            model_path,
            torch_dtype=torch.float16,
            low_cpu_mem_usage=True,
            trust_remote_code=True,
            device_map="auto"
        )
        
        load_time = time.time() - start_time
        
        # Memory check after model loading
        model_memory = get_memory_usage()
        memory_increase = model_memory['used_gb'] - tokenizer_memory['used_gb']
        
        logger.info(f"✅ Model loaded successfully in {load_time:.2f}s")
        logger.info(f"📊 After Model: {model_memory['used_gb']:.1f}GB used")
        logger.info(f"📊 Model Memory Usage: {memory_increase:.1f}GB")
        
        # Print model info
        logger.info("📊 Model Information:")
        logger.info(f"   Device: {next(model.parameters()).device}")
        logger.info(f"   Dtype: {next(model.parameters()).dtype}")
        
        # Test inference with multiple prompts
        test_prompts = [
            "Hello",
            "What is AI?",
            "Explain quantum computing briefly."
        ]
        
        for i, prompt in enumerate(test_prompts, 1):
            logger.info(f"\n🧪 Test {i}: {prompt}")
            
            # Tokenize input
            inputs = tokenizer(prompt, return_tensors="pt")
            
            # Generate response
            start_time = time.time()
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=50,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id,
                    eos_token_id=tokenizer.eos_token_id
                )
            
            inference_time = time.time() - start_time
            
            # Decode response
            response = tokenizer.decode(outputs[0], skip_special_tokens=True)
            response_text = response[len(prompt):].strip()
            
            logger.info(f"   Response: {response_text}")
            logger.info(f"   Time: {inference_time:.2f}s")
        
        # Final memory check
        final_memory = get_memory_usage()
        logger.info(f"\n📊 Final Memory: {final_memory['used_gb']:.1f}GB used")
        
        logger.info("\n🎉 Controlled test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        logger.info("🧹 Cleaning up...")
        if 'model' in locals():
            del model
        if 'tokenizer' in locals():
            del tokenizer
        
        # Force garbage collection
        import gc
        gc.collect()
        
        # Final memory check
        cleanup_memory = get_memory_usage()
        logger.info(f"📊 After Cleanup: {cleanup_memory['used_gb']:.1f}GB used")

def main():
    """Main test function"""
    success = test_qwen_controlled()
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
