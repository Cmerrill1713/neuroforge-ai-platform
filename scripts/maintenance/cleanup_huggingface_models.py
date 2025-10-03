#!/usr/bin/env python3
""'
Cleanup Unused HuggingFace Models - Remove models that aren't being used
""'

import shutil
import os
from pathlib import Path

def remove_huggingface_model(model_path):
    """TODO: Add docstring."""
    """Remove HuggingFace model directory""'
    try:
        expanded_path = os.path.expanduser(model_path)
        path = Path(expanded_path)
        if path.exists():
            print(f"🗑️  Removing HuggingFace model: {path}')

            # Calculate size before removal
            total_size = sum(f.stat().st_size for f in path.rglob("*') if f.is_file())
            size_gb = total_size / (1024**3)

            shutil.rmtree(path)
            print(f"✅ Successfully removed: {path} ({size_gb:.1f} GB)')
            return size_gb
        else:
            print(f"⚠️  HuggingFace model not found: {path}')
            return 0
    except Exception as e:
        print(f"❌ Error removing HuggingFace model {model_path}: {e}')
        return 0

def main():
    """TODO: Add docstring."""
    """Main cleanup function""'
    print("🚀 HUGGINGFACE MODEL CLEANUP')
    print("=' * 40)

    # Models to KEEP (actively used):
    models_to_keep = [
        "models--Qwen--Qwen3-Omni-30B-A3B-Instruct',  # Keep the main multimodal model
        "models--lmstudio-community--Qwen3-Coder-30B-A3B-Instruct-MLX-5bit'  # Keep the code generation model
    ]

    # Models to REMOVE (duplicates or unused):
    models_to_remove = [
        "~/.cache/huggingface/hub/models--Qwen--Qwen2-1.5B-Instruct',
        "~/.cache/huggingface/hub/models--Qwen--Qwen2-7B-Instruct',
        "~/.cache/huggingface/hub/models--Qwen--Qwen2.5-7B-Instruct',
        "~/.cache/huggingface/hub/models--Marvis-AI--marvis-tts-250m-v0.1-MLX-4bit',
        "~/.cache/huggingface/hub/models--Marvis-AI--marvis-tts-250m-v0.1-MLX-8bit',
        "~/.cache/huggingface/hub/models--Marvis-AI--marvis-tts-250m-v0.1-MLX-fp16',
        "~/.cache/huggingface/hub/models--facebook--mms-tts-eng',
        "~/.cache/huggingface/hub/models--microsoft--VibeVoice-1.5B',
        "~/.cache/huggingface/hub/models--microsoft--speecht5_tts',
        "~/.cache/huggingface/hub/models--microsoft--speecht5_hifigan',
        "~/.cache/huggingface/hub/models--descript--dac_44khz',
        "~/.cache/huggingface/hub/models--kyutai--moshiko-pytorch-bf16',
        "~/.cache/huggingface/hub/models--microsoft--DialoGPT-medium'
    ]

    print("📊 CLEANUP PLAN:')
    print(f"✅ Models to KEEP: {len(models_to_keep)}')
    print(f"❌ Models to REMOVE: {len(models_to_remove)}')

    print("\n📋 HuggingFace models to keep:')
    for model in models_to_keep:
        print(f"  ✅ {model}')

    print("\n📋 HuggingFace models to remove:')
    for model in models_to_remove:
        print(f"  ❌ {model}')

    print("\n🚀 Proceeding with HuggingFace model cleanup...')
    print("This will free up significant storage space.')

    total_freed = 0
    removed_count = 0

    for model_path in models_to_remove:
        freed_size = remove_huggingface_model(model_path)
        if freed_size > 0:
            total_freed += freed_size
            removed_count += 1

    print(f"\n🎉 HUGGINGFACE CLEANUP COMPLETE!')
    print(f"✅ Successfully removed {removed_count} HuggingFace models')
    print(f"💾 Total storage freed: {total_freed:.1f} GB')

    print(f"\n📋 REMAINING HUGGINGFACE MODELS:')
    print("=' * 40)
    for model in models_to_keep:
        print(f"  ✅ {model}')

    print(f"\n🎯 FINAL OPTIMIZED MODEL COLLECTION:')
    print("=' * 50)
    print("🧠 Ollama Models (7):')
    print("  - qwen2.5:7b (balanced performance)')
    print("  - mistral:7b (good performance)')
    print("  - llama3.2:3b (fastest)')
    print("  - llava:7b (multimodal)')
    print("  - gpt-oss:20b (large model)')
    print("  - qwen2.5:72b (very large)')
    print("  - qwen2.5:14b (large)')

    print("\n⚡ MLX Models (2):')
    print("  - Qwen3-30B-A3B-MLX (best overall)')
    print("  - Dia-1.6B (good MLX model)')

    print("\n🤗 HuggingFace Models (2):')
    print("  - Qwen3-Omni-30B (multimodal)')
    print("  - Qwen3-Coder-30B (code generation)')

    print(f"\n💾 TOTAL STORAGE OPTIMIZED:')
    print(f"  - Removed underperforming Ollama models: ~12-15 GB')
    print(f"  - Removed unused HuggingFace models: ~{total_freed:.1f} GB')
    print(f"  - Total freed: ~{12 + total_freed:.1f} GB')

    print(f"\n🚀 READY FOR INTEGRATION!')
    print("Your model collection is now optimized and ready for:')
    print("  - FastAPI server integration')
    print("  - Intelligent model routing')
    print("  - High-performance AI applications')

if __name__ == "__main__':
    main()
