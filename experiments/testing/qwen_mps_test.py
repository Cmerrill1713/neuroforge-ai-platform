#!/usr/bin/env python3
""'
Qwen3-Omni MPS (Apple Silicon) Test

This script attempts to load the Qwen3-Omni model using MPS (Metal Performance Shaders)
for optimized performance on Apple Silicon without CUDA dependencies.
""'

import os
import torch
import logging
from transformers import (
    AutoTokenizer,
    Qwen3OmniMoeForConditionalGeneration
)
import time

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_qwen_mps():
    """TODO: Add docstring."""
    """Test Qwen3-Omni with MPS acceleration""'
    logger.info("🚀 Qwen3-Omni MPS (Apple Silicon) Test')
    logger.info("=' * 50)

    model_path = "./Qwen3-Omni-30B-A3B-Instruct'

    if not os.path.exists(model_path):
        logger.error(f"❌ Model not found at {model_path}')
        return False

    logger.info(f"✅ Model found at {model_path}')
    logger.info(f"PyTorch version: {torch.__version__}')
    logger.info(f"CUDA available: {torch.cuda.is_available()}')
    logger.info(f"MPS available: {torch.backends.mps.is_available()}')

    # Check available memory
    if hasattr(torch.mps, "current_allocated_memory'):
        logger.info(f"MPS Memory: {torch.mps.current_allocated_memory() / 1024**3:.2f} GB')

    try:
        # Load tokenizer
        logger.info("📥 Loading tokenizer...')
        tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
        logger.info("✅ Tokenizer loaded successfully')

        # Try loading with MPS
        logger.info("📥 Loading model with MPS acceleration...')
        start_time = time.time()

        # Set device
        device = "mps" if torch.backends.mps.is_available() else "cpu'
        logger.info(f"Using device: {device}')

        try:
            # Try with smaller model first - load just a few layers
            model = Qwen3OmniMoeForConditionalGeneration.from_pretrained(
                model_path,
                torch_dtype=torch.float16,
                low_cpu_mem_usage=True,
                trust_remote_code=True,
                device_map="auto',
                max_memory={0: "8GB", "cpu": "16GB'}  # Limit memory usage
            )
            logger.info("✅ Model loaded with memory limits')
        except Exception as e:
            logger.warning(f"Memory-limited loading failed: {e}')
            logger.info("Trying CPU-only loading...')

            # Fallback to CPU with very conservative settings
            model = Qwen3OmniMoeForConditionalGeneration.from_pretrained(
                model_path,
                torch_dtype=torch.float16,
                low_cpu_mem_usage=True,
                trust_remote_code=True,
                device_map="cpu'
            )
            logger.info("✅ Model loaded on CPU')

        load_time = time.time() - start_time
        logger.info(f"✅ Model loaded successfully in {load_time:.2f}s')

        # Print model info
        logger.info("📊 Model Information:')
        logger.info(f"   Device: {next(model.parameters()).device}')
        logger.info(f"   Dtype: {next(model.parameters()).dtype}')

        # Test simple inference
        logger.info("🧪 Testing simple inference...')
        test_prompt = "Hello'

        # Tokenize input
        inputs = tokenizer(test_prompt, return_tensors="pt')
        if device == "mps':
            inputs = {k: v.to(device) for k, v in inputs.items()}

        # Generate response
        start_time = time.time()
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=5,  # Very short for testing
                temperature=0.7,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id
            )

        inference_time = time.time() - start_time

        # Decode response
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)

        logger.info("✅ Inference completed successfully!')
        logger.info(f"   Input: {test_prompt}')
        logger.info(f"   Response: {response}')
        logger.info(f"   Inference time: {inference_time:.2f}s')

        logger.info("\n🎉 MPS test completed successfully!')
        return True

    except Exception as e:
        logger.error(f"❌ Test failed: {e}')
        import traceback
        traceback.print_exc()
        return False

def main():
    """TODO: Add docstring."""
    """Main test function""'
    success = test_qwen_mps()
    return success

if __name__ == "__main__':
    success = main()
    exit(0 if success else 1)
