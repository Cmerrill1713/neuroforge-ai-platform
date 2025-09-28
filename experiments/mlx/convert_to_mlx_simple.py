#!/usr/bin/env python3
"""
Simple MLX Conversion Script for Qwen3-Omni

This script converts the Qwen3-Omni model to MLX format with a unique output path.
"""

import os
import sys
from pathlib import Path

def convert_qwen_to_mlx():
    """Convert Qwen3-Omni model to MLX format"""
    model_path = "./Qwen3-Omni-30B-A3B-Instruct"
    mlx_output_path = "./Qwen3-Omni-MLX-v1"
    
    print("🚀 Converting Qwen3-Omni to MLX Format")
    print("=" * 50)
    
    # Check if source model exists
    if not Path(model_path).exists():
        print(f"❌ Source model not found at {model_path}")
        return False
    
    print(f"✅ Source model found at {model_path}")
    
    try:
        # Import MLX conversion tools
        from mlx_lm import convert
        import mlx.core as mx
        
        print(f"✅ MLX-LM tools available")
        print(f"MLX version: {mx.__version__}")
        
        print(f"\n📥 Converting model to MLX format...")
        print(f"Source: {model_path}")
        print(f"Destination: {mlx_output_path}")
        
        # Convert the model with 4-bit quantization
        convert(
            hf_path=model_path,
            mlx_path=mlx_output_path,
            quantize=True,
            q_group_size=64,
            q_bits=4,
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
            max_tokens=50,
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
    success = convert_qwen_to_mlx()
    sys.exit(0 if success else 1)
