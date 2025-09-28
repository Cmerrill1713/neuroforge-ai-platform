#!/usr/bin/env python3
"""
Qwen3-Omni LoRA + 4-bit Quantization Test

This script attempts to load the Qwen3-Omni model with LoRA and 4-bit quantization
to reduce memory usage while maintaining performance.
"""

import os
import torch
import logging
from transformers import (
    AutoTokenizer, 
    Qwen3OmniMoeForConditionalGeneration,
    BitsAndBytesConfig
)
from peft import LoraConfig, get_peft_model, TaskType
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_qwen_lora_4bit():
    """Test Qwen3-Omni with LoRA and 4-bit quantization"""
    logger.info("🚀 Qwen3-Omni LoRA + 4-bit Quantization Test")
    logger.info("=" * 60)
    
    model_path = "./Qwen3-Omni-30B-A3B-Instruct"
    
    if not os.path.exists(model_path):
        logger.error(f"❌ Model not found at {model_path}")
        return False
    
    logger.info(f"✅ Model found at {model_path}")
    logger.info(f"PyTorch version: {torch.__version__}")
    logger.info(f"CUDA available: {torch.cuda.is_available()}")
    
    try:
        # Load tokenizer
        logger.info("📥 Loading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
        logger.info("✅ Tokenizer loaded successfully")
        
        # Configure 4-bit quantization
        logger.info("📥 Configuring 4-bit quantization...")
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
            bnb_4bit_compute_dtype=torch.bfloat16
        )
        logger.info("✅ 4-bit quantization config created")
        
        # Configure LoRA
        logger.info("📥 Configuring LoRA...")
        lora_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            inference_mode=False,
            r=16,  # Rank
            lora_alpha=32,  # Scaling parameter
            lora_dropout=0.1,
            target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
        )
        logger.info("✅ LoRA config created")
        
        # Load model with quantization
        logger.info("📥 Loading model with 4-bit quantization...")
        start_time = time.time()
        
        model = Qwen3OmniMoeForConditionalGeneration.from_pretrained(
            model_path,
            quantization_config=bnb_config,
            low_cpu_mem_usage=True,
            trust_remote_code=True,
            device_map="auto",
            torch_dtype=torch.bfloat16
        )
        
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
        
        # Get memory usage
        if torch.cuda.is_available():
            memory_allocated = torch.cuda.memory_allocated() / 1024**3
            memory_reserved = torch.cuda.memory_reserved() / 1024**3
            logger.info(f"   GPU Memory Allocated: {memory_allocated:.2f} GB")
            logger.info(f"   GPU Memory Reserved: {memory_reserved:.2f} GB")
        else:
            logger.info("   Running on CPU")
        
        # Test inference
        logger.info("🧪 Testing inference...")
        test_prompt = "Hello, how are you today?"
        
        # Tokenize input
        inputs = tokenizer(test_prompt, return_tensors="pt").to(model.device)
        
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
        
        logger.info("✅ Inference completed successfully!")
        logger.info(f"   Input: {test_prompt}")
        logger.info(f"   Response: {response}")
        logger.info(f"   Inference time: {inference_time:.2f}s")
        
        # Test multiple prompts
        test_prompts = [
            "What is artificial intelligence?",
            "Explain quantum computing briefly.",
            "Write a short poem about technology."
        ]
        
        logger.info("🧪 Testing multiple prompts...")
        for i, prompt in enumerate(test_prompts, 1):
            logger.info(f"\nTest {i}: {prompt}")
            
            inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
            
            start_time = time.time()
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=100,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id,
                    eos_token_id=tokenizer.eos_token_id
                )
            
            inference_time = time.time() - start_time
            response = tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            logger.info(f"   Response: {response[len(prompt):].strip()}")
            logger.info(f"   Time: {inference_time:.2f}s")
        
        logger.info("\n🎉 LoRA + 4-bit quantization test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    success = test_qwen_lora_4bit()
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
