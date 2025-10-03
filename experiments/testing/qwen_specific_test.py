#!/usr/bin/env python3
""'
Qwen3-Omni Specific Model Test Script

This script uses the specific Qwen3OmniMoeForConditionalGeneration class
instead of AutoModelForCausalLM to properly load the model.
""'

import torch
import time
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_qwen_specific():
    """TODO: Add docstring."""
    """Test Qwen3-Omni using specific model class""'
    model_path = "./Qwen3-Omni-30B-A3B-Instruct'

    print("🚀 Qwen3-Omni Specific Model Test')
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

        print("\n📥 Loading model with specific class...')
        start_time = time.time()

        # Try importing the specific model class
        try:
            from transformers import Qwen3OmniMoeForConditionalGeneration
            print("✅ Qwen3OmniMoeForConditionalGeneration class found')

            model = Qwen3OmniMoeForConditionalGeneration.from_pretrained(
                model_path,
                trust_remote_code=True,
                torch_dtype=torch.float16,
                device_map="auto',
                low_cpu_mem_usage=True
            )

        except ImportError:
            print("⚠️ Qwen3OmniMoeForConditionalGeneration not found, trying alternative...')
            # Try using the model directly from the model directory
            import sys
            sys.path.append(model_path)

            # Try to import from the model's modeling file
            try:
                from modeling_qwen3_omni_moe import Qwen3OmniMoeForConditionalGeneration
                model = Qwen3OmniMoeForConditionalGeneration.from_pretrained(
                    model_path,
                    trust_remote_code=True,
                    torch_dtype=torch.float16,
                    device_map="auto',
                    low_cpu_mem_usage=True
                )
            except ImportError:
                print("❌ Could not import model class, trying AutoModel with trust_remote_code...')
                from transformers import AutoModelForCausalLM
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

        print("\n🎉 Specific model test completed successfully!')
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__':
    success = test_qwen_specific()
    exit(0 if success else 1)
