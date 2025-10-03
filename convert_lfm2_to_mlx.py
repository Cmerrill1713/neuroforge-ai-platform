#!/usr/bin/env python3
"""
Convert LFM2-2.6B to MLX Format
"""

import os
import sys
from pathlib import Path

def convert_lfm2_to_mlx():
    """Convert LFM2-2.6B model to MLX format for fast Apple Silicon inference"""
    model_name = "LiquidAI/LFM2-2.6B"
    mlx_output_path = "./mlx_models/lfm2-2.6b-mlx"

    print("🚀 Converting LFM2-2.6B to MLX Format")
    print("=" * 50)

    try:
        # Import MLX conversion tools
        from mlx_lm import convert
        import mlx.core as mx

        print(f"✅ MLX-LM tools available")
        print(f"MLX version: {mx.__version__}")

        print(f"\n📥 Converting model to MLX format...")
        print(f"Source: {model_name} (from Hugging Face)")
        print(f"Destination: {mlx_output_path}")

        # Convert the model with 4-bit quantization for speed
        convert(
            hf_path=model_name,
            mlx_path=mlx_output_path,
            quantize=True,
            q_group_size=64,
            q_bits=4,  # 4-bit quantization for fast inference
        )

        print(f"✅ Model converted successfully to {mlx_output_path}")

        # Test the converted model
        print(f"\n🧪 Testing converted MLX model...")

        from mlx_lm import load, generate

        model, tokenizer = load(mlx_output_path)

        # Test generation
        test_prompt = "Hello, how are you?"
        print(f"Test prompt: {test_prompt}")

        response = generate(
            model=model,
            tokenizer=tokenizer,
            prompt=test_prompt,
            max_tokens=20,
            temp=0.7,
            verbose=True
        )

        print(f"Response: {response}")
        print(f"\n🎉 MLX conversion and testing completed successfully!")

        return True

    except Exception as e:
        print(f"❌ Conversion failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = convert_lfm2_to_mlx()
    sys.exit(0 if success else 1)

