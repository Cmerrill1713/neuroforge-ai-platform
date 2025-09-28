#!/usr/bin/env python3
"""
Test Smaller Qwen Models

This script tests downloading and loading smaller Qwen models that can actually
run on your system for fine-tuning.
"""

import os
import torch
import logging
from transformers import AutoTokenizer, AutoModelForCausalLM
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_smaller_qwen_model(model_name: str):
    """Test loading a smaller Qwen model"""
    logger.info(f"🧪 Testing {model_name}")
    logger.info("=" * 50)
    
    try:
        # Load tokenizer
        logger.info("📥 Loading tokenizer...")
        start_time = time.time()
        
        tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        tokenizer_time = time.time() - start_time
        logger.info(f"✅ Tokenizer loaded in {tokenizer_time:.2f}s")
        
        # Load model
        logger.info("📥 Loading model...")
        start_time = time.time()
        
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            device_map="auto",
            trust_remote_code=True,
            low_cpu_mem_usage=True
        )
        
        model_time = time.time() - start_time
        logger.info(f"✅ Model loaded in {model_time:.2f}s")
        
        # Test inference
        logger.info("🧪 Testing inference...")
        test_prompt = "What is artificial intelligence?"
        
        inputs = tokenizer(test_prompt, return_tensors="pt")
        
        start_time = time.time()
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=50,
                temperature=0.7,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )
        
        inference_time = time.time() - start_time
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        logger.info(f"✅ Inference completed in {inference_time:.2f}s")
        logger.info(f"   Prompt: {test_prompt}")
        logger.info(f"   Response: {response[len(test_prompt):].strip()}")
        
        # Memory usage
        if torch.cuda.is_available():
            memory_used = torch.cuda.memory_allocated() / 1024**3
            logger.info(f"   GPU Memory: {memory_used:.2f} GB")
        
        logger.info(f"🎉 {model_name} test successful!")
        return True
        
    except Exception as e:
        logger.error(f"❌ {model_name} test failed: {e}")
        return False

def main():
    """Test different smaller Qwen models"""
    logger.info("🚀 Testing Smaller Qwen Models for Fine-tuning")
    logger.info("=" * 60)
    
    # Test models in order of size (smallest first)
    test_models = [
        "Qwen/Qwen2-1.5B-Instruct",      # Smallest
        "Qwen/Qwen2-7B-Instruct",        # Small
        "Qwen/Qwen2.5-7B-Instruct",      # Medium-small
    ]
    
    successful_models = []
    
    for model_name in test_models:
        logger.info(f"\n{'='*60}")
        success = test_smaller_qwen_model(model_name)
        
        if success:
            successful_models.append(model_name)
            logger.info(f"✅ {model_name} - READY FOR FINE-TUNING")
        else:
            logger.info(f"❌ {model_name} - FAILED")
    
    # Summary
    logger.info(f"\n{'='*60}")
    logger.info("📊 TEST SUMMARY")
    logger.info(f"Successful models: {len(successful_models)}/{len(test_models)}")
    
    if successful_models:
        logger.info("✅ Models ready for fine-tuning:")
        for model in successful_models:
            logger.info(f"  - {model}")
        
        logger.info(f"\n🎯 RECOMMENDATION:")
        logger.info(f"Use {successful_models[0]} for fine-tuning with your knowledge base")
        logger.info("This model is small enough to run and can be fine-tuned efficiently")
    else:
        logger.info("❌ No models could be loaded successfully")
    
    return len(successful_models) > 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
