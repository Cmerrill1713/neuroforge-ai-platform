#!/usr/bin/env python3
""'
Debug script to investigate model performance tracking issue
""'

import asyncio
import time
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src'))

from src.core.engines.ollama_adapter import OllamaAdapter

async def test_model_performance():
    """Test actual model performance to debug the issue""'

    adapter = OllamaAdapter()

    if not await adapter.check_ollama_status():
        print("❌ Ollama not running')
        return

    print("🔍 Testing Model Performance - Debugging Issue')
    print("=' * 50)

    # Test each model with the same prompt
    test_prompt = "What is 2+2? Answer briefly.'

    models_to_test = ["primary", "coding", "lightweight']

    for model_key in models_to_test:
        if model_key not in adapter.models:
            print(f"❌ Model {model_key} not found')
            continue

        model = adapter.models[model_key]
        print(f"\n🤖 Testing {model_key} ({model.name})')
        print(f"   Ollama name: {model.ollama_name}')
        print(f"   Expected to be: {"Fast" if model_key == "lightweight" else "Slower"}')

        # Run multiple tests to get average
        times = []
        tokens_list = []

        for i in range(3):
            start_time = time.time()
            try:
                response = await adapter.generate_response(
                    model_key=model_key,
                    prompt=f"{test_prompt} (Test {i+1})',
                    max_tokens=50
                )
                end_time = time.time()

                response_time = end_time - start_time
                times.append(response_time)
                tokens_list.append(response.tokens_generated)

                print(f"   Test {i+1}: {response_time:.3f}s, {response.tokens_generated} tokens')

            except Exception as e:
                print(f"   Test {i+1}: ❌ Error - {e}')

        if times:
            avg_time = sum(times) / len(times)
            avg_tokens = sum(tokens_list) / len(tokens_list)
            tokens_per_sec = avg_tokens / avg_time if avg_time > 0 else 0

            print(f"   📊 Average: {avg_time:.3f}s, {avg_tokens:.1f} tokens, {tokens_per_sec:.1f} tokens/sec')

            # Check if this matches expectations
            if model_key == "lightweight' and avg_time > 2.0:
                print(f"   ⚠️  WARNING: Lightweight model is slower than expected!')
            elif model_key == "primary' and avg_time < 1.0:
                print(f"   ⚠️  WARNING: Primary model is faster than expected!')

if __name__ == "__main__':
    asyncio.run(test_model_performance())
