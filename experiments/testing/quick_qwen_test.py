#!/usr/bin/env python3
""'
Quick Qwen3-Omni Model Test Script

Simple script to quickly verify the model is working correctly.
""'

import torch
import time
from transformers import AutoTokenizer, AutoModelForCausalLM
from pathlib import Path

def quick_test():
    """TODO: Add docstring."""
    """Run a quick test of the Qwen model""'
    model_path = "./Qwen3-Omni-30B-A3B-Instruct'

    print("🚀 Quick Qwen3-Omni Test')
    print("=' * 50)

    # Check if model exists
    if not Path(model_path).exists():
        print(f"❌ Model not found at {model_path}')
        return False

    print(f"✅ Model found at {model_path}')

    # Check system info
    print(f"PyTorch version: {torch.__version__}')
    print(f"CUDA available: {torch.cuda.is_available()}')
    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name(0)}')
        print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB')

    try:
        print("\n📥 Loading tokenizer...')
        tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
        print("✅ Tokenizer loaded successfully')

        print("\n📥 Loading model...')
        start_time = time.time()

        # Try to load with minimal memory usage first
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            trust_remote_code=True,
            torch_dtype=torch.float16,
            device_map="auto',
            low_cpu_mem_usage=True
        )

        load_time = time.time() - start_time
        print(f"✅ Model loaded in {load_time:.2f} seconds')

        # Test generation
        print("\n🧪 Testing text generation...')
        test_prompts = [
            "Hello, how are you?',
            "Explain quantum computing in one sentence.',
            "What is the capital of France?'
        ]

        for i, prompt in enumerate(test_prompts, 1):
            print(f"\nTest {i}: {prompt}')

            inputs = tokenizer(prompt, return_tensors="pt')

            start_time = time.time()
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=100,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id
                )

            generation_time = time.time() - start_time
            response = tokenizer.decode(outputs[0], skip_special_tokens=True)
            response_text = response[len(prompt):].strip()

            print(f"Response: {response_text}')
            print(f"Time: {generation_time:.2f}s')

        print("\n🎉 Quick test completed successfully!')
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__':
    success = quick_test()
    exit(0 if success else 1)
