#!/usr/bin/env python3
""'
Qwen3-Omni Quantized Model Test Script

This script loads the Qwen3-Omni model with quantization to reduce memory usage.
""'

import torch
import time
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_qwen_quantized():
    """TODO: Add docstring."""
    """Test Qwen3-Omni with quantization""'
    model_path = "./Qwen3-Omni-30B-A3B-Instruct'

    print("🚀 Qwen3-Omni Quantized Model Test')
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
        from transformers import AutoTokenizer
        tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
        print("✅ Tokenizer loaded successfully')

        print("\n📥 Loading model with 4-bit quantization...')
        start_time = time.time()

        # Try with 4-bit quantization
        try:
            from transformers import BitsAndBytesConfig
            from transformers import Qwen3OmniMoeForConditionalGeneration

            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4'
            )

            model = Qwen3OmniMoeForConditionalGeneration.from_pretrained(
                model_path,
                trust_remote_code=True,
                quantization_config=quantization_config,
                device_map="auto',
                low_cpu_mem_usage=True
            )

        except Exception as e:
            print(f"⚠️ 4-bit quantization failed: {e}')
            print("Trying 8-bit quantization...')

            try:
                quantization_config = BitsAndBytesConfig(
                    load_in_8bit=True
                )

                model = Qwen3OmniMoeForConditionalGeneration.from_pretrained(
                    model_path,
                    trust_remote_code=True,
                    quantization_config=quantization_config,
                    device_map="auto',
                    low_cpu_mem_usage=True
                )

            except Exception as e2:
                print(f"⚠️ 8-bit quantization failed: {e2}')
                print("Trying CPU loading with float16...')

                model = Qwen3OmniMoeForConditionalGeneration.from_pretrained(
                    model_path,
                    trust_remote_code=True,
                    torch_dtype=torch.float16,
                    device_map="cpu',
                    low_cpu_mem_usage=True
                )

        load_time = time.time() - start_time
        print(f"✅ Model loaded in {load_time:.2f} seconds')

        # Test generation
        print("\n🧪 Testing text generation...')
        test_prompts = [
            "Hello, how are you?',
            "What is AI?'
        ]

        for i, prompt in enumerate(test_prompts, 1):
            print(f"\nTest {i}: {prompt}')

            inputs = tokenizer(prompt, return_tensors="pt')

            start_time = time.time()
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=50,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id
                )

            generation_time = time.time() - start_time
            response = tokenizer.decode(outputs[0], skip_special_tokens=True)
            response_text = response[len(prompt):].strip()

            print(f"Response: {response_text}')
            print(f"Time: {generation_time:.2f}s')

        print("\n🎉 Quantized model test completed successfully!')
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__':
    success = test_qwen_quantized()
    exit(0 if success else 1)
