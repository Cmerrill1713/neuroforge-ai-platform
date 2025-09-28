#!/usr/bin/env python3
"""
Qwen3-Omni CPU + LoRA Test

This script attempts to load the Qwen3-Omni model on CPU with LoRA
for Apple Silicon without CUDA dependencies.
"""

import os
import torch
import logging
from transformers import (
    AutoTokenizer, 
    Qwen3OmniMoeForConditionalGeneration
)
from peft import LoraConfig, get_peft_model, TaskType
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_qwen_cpu_lora():
    """Test Qwen3-Omni on CPU with LoRA"""
    logger.info("🚀 Qwen3-Omni CPU + LoRA Test")
    logger.info("=" * 50)
    
    model_path = "./Qwen3-Omni-30B-A3B-Instruct"
    
    if not os.path.exists(model_path):
        logger.error(f"❌ Model not found at {model_path}")
        return False
    
    logger.info(f"✅ Model found at {model_path}")
    logger.info(f"PyTorch version: {torch.__version__}")
    logger.info(f"CUDA available: {torch.cuda.is_available()}")
    logger.info(f"MPS available: {torch.backends.mps.is_available()}")
    
    try:
        # Load tokenizer
        logger.info("📥 Loading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
        logger.info("✅ Tokenizer loaded successfully")
        
        # Configure LoRA
        logger.info("📥 Configuring LoRA...")
        lora_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            inference_mode=False,
            r=8,  # Lower rank for CPU
            lora_alpha=16,  # Lower alpha for CPU
            lora_dropout=0.1,
            target_modules=["q_proj", "k_proj", "v_proj", "o_proj"]
        )
        logger.info("✅ LoRA config created")
        
        # Try loading with minimal memory usage
        logger.info("📥 Loading model on CPU with minimal memory...")
        start_time = time.time()
        
        # First try with float16 and CPU
        try:
            model = Qwen3OmniMoeForConditionalGeneration.from_pretrained(
                model_path,
                torch_dtype=torch.float16,
                low_cpu_mem_usage=True,
                trust_remote_code=True,
                device_map="cpu",
                max_memory={0: "8GB"}  # Limit memory usage
            )
            logger.info("✅ Model loaded with float16")
        except Exception as e:
            logger.warning(f"Float16 failed: {e}")
            logger.info("Trying with float32...")
            
            # Fallback to float32
            model = Qwen3OmniMoeForConditionalGeneration.from_pretrained(
                model_path,
                torch_dtype=torch.float32,
                low_cpu_mem_usage=True,
                trust_remote_code=True,
                device_map="cpu"
            )
            logger.info("✅ Model loaded with float32")
        
        load_time = time.time() - start_time
        logger.info(f"✅ Model loaded successfully in {load_time:.2f}s")
        
        # Apply LoRA
        logger.info("📥 Applying LoRA to model...")
        model = get_peft_model(model, lora_config)
        logger.info("✅ LoRA applied successfully")
        
        # Print model info
        logger.info("📊 Model Information:")
        logger.info(f"   Device: {next(model.parameters()).device}")
        logger.info(f"   Dtype: {next(model.parameters()).dtype}")
        
        # Test simple inference
        logger.info("🧪 Testing simple inference...")
        test_prompt = "Hello"
        
        # Tokenize input
        inputs = tokenizer(test_prompt, return_tensors="pt")
        
        # Generate response
        start_time = time.time()
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=10,  # Very short for testing
                temperature=0.7,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id
            )
        
        inference_time = time.time() - start_time
        
        # Decode response
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        logger.info("✅ Inference completed successfully!")
        logger.info(f"   Input: {test_prompt}")
        logger.info(f"   Response: {response}")
        logger.info(f"   Inference time: {inference_time:.2f}s")
        
        logger.info("\n🎉 CPU + LoRA test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    success = test_qwen_cpu_lora()
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
