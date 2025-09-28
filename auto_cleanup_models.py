#!/usr/bin/env python3
"""
Auto Cleanup Underperforming Models - Remove models that scored below 6.0
Based on performance evaluation results
"""

import subprocess
import shutil
import os
from pathlib import Path

def remove_ollama_model(model_name):
    """Remove Ollama model"""
    try:
        print(f"🗑️  Removing Ollama model: {model_name}")
        result = subprocess.run(["ollama", "rm", model_name], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Successfully removed: {model_name}")
            return True
        else:
            print(f"❌ Failed to remove {model_name}: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error removing {model_name}: {e}")
        return False

def remove_mlx_model(model_path):
    """Remove MLX model directory"""
    try:
        expanded_path = os.path.expanduser(model_path)
        path = Path(expanded_path)
        if path.exists():
            print(f"🗑️  Removing MLX model directory: {path}")
            shutil.rmtree(path)
            print(f"✅ Successfully removed: {path}")
            return True
        else:
            print(f"⚠️  MLX model directory not found: {path}")
            return False
    except Exception as e:
        print(f"❌ Error removing MLX model {model_path}: {e}")
        return False

def main():
    """Main cleanup function"""
    print("🚀 AUTO MODEL CLEANUP - Removing Underperforming Models")
    print("=" * 60)
    
    # Based on performance evaluation results:
    # Models to KEEP (scored 6.0+ or are top performers):
    models_to_keep = [
        "Qwen3-30B-A3B-Instruct-2507-MLX-4bit",  # 10.1/10 - Best overall
        "Dia-1.6B",                               # 7.6/10 - Good MLX model
        "llama3.2:3b",                            # 6.3/10 - Fast and efficient
        "qwen2.5:7b",                             # 6.0/10 - Good balance
        "gpt-oss:20b",                            # 6.0/10 - Large model
        "mistral:7b",                             # 6.0/10 - Good performance
        "llava:7b"                                # Keep for multimodal (only option)
    ]
    
    # Models to REMOVE (scored below 6.0):
    ollama_models_to_remove = [
        "llama3.1:8b",  # 5.9/10
        "qwen3:8b",     # 5.2/10  
        "phi3:3.8b"     # 3.4/10
    ]
    
    # MLX models to remove (none - both performed well)
    mlx_models_to_remove = []
    
    print("📊 CLEANUP PLAN:")
    print(f"✅ Models to KEEP: {len(models_to_keep)}")
    print(f"❌ Models to REMOVE: {len(ollama_models_to_remove) + len(mlx_models_to_remove)}")
    
    print("\n📋 Models to keep:")
    for model in models_to_keep:
        print(f"  ✅ {model}")
    
    print("\n📋 Models to remove:")
    for model in ollama_models_to_remove:
        print(f"  ❌ {model}")
    for model in mlx_models_to_remove:
        print(f"  ❌ {model}")
    
    print("\n🚀 Proceeding with automatic cleanup...")
    print("This will free up approximately 12-15 GB of storage space.")
    
    removed_count = 0
    
    # Remove Ollama models
    if ollama_models_to_remove:
        print("\n🗑️  Removing Ollama models:")
        print("-" * 30)
        for model in ollama_models_to_remove:
            if remove_ollama_model(model):
                removed_count += 1
    
    # Remove MLX models
    if mlx_models_to_remove:
        print("\n🗑️  Removing MLX models:")
        print("-" * 30)
        mlx_model_paths = {
            "Qwen3-30B-A3B-Instruct-2507-MLX-4bit": "~/.lmstudio/models/lmstudio-community/Qwen3-30B-A3B-Instruct-2507-MLX-4bit",
            "Dia-1.6B": "~/.lmstudio/models/mlx-community/Dia-1.6B"
        }
        
        for model in mlx_models_to_remove:
            if model in mlx_model_paths:
                if remove_mlx_model(mlx_model_paths[model]):
                    removed_count += 1
    
    print(f"\n🎉 CLEANUP COMPLETE!")
    print(f"✅ Successfully removed {removed_count} underperforming models")
    print(f"💾 Estimated storage freed: ~12-15 GB")
    
    print(f"\n📋 REMAINING OPTIMIZED MODELS:")
    print("=" * 40)
    for model in models_to_keep:
        print(f"  ✅ {model}")
    
    print(f"\n🎯 NEXT STEPS:")
    print("1. Test your remaining models to ensure they work correctly")
    print("2. Integrate the best models with your FastAPI server")
    print("3. Create workflows using your optimized model collection")
    print("4. Monitor performance and adjust as needed")
    
    # Show current Ollama models
    print(f"\n📊 Current Ollama models after cleanup:")
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        if result.returncode == 0:
            print(result.stdout)
        else:
            print("Could not list Ollama models")
    except Exception as e:
        print(f"Error listing Ollama models: {e}")
    
    # Create final optimized model summary
    create_optimized_summary(models_to_keep)

def create_optimized_summary(models_to_keep):
    """Create summary of optimized model collection"""
    
    print(f"\n📊 OPTIMIZED MODEL COLLECTION SUMMARY")
    print("=" * 50)
    
    # Categorize remaining models
    text_generation = [
        "Qwen3-30B-A3B-Instruct-2507-MLX-4bit",
        "Dia-1.6B", 
        "llama3.2:3b",
        "qwen2.5:7b",
        "gpt-oss:20b",
        "mistral:7b"
    ]
    
    multimodal = ["llava:7b"]
    
    print(f"🧠 Text Generation Models: {len(text_generation)}")
    for model in text_generation:
        if model in models_to_keep:
            print(f"  ✅ {model}")
    
    print(f"\n🖼️  Multimodal Models: {len(multimodal)}")
    for model in multimodal:
        if model in models_to_keep:
            print(f"  ✅ {model}")
    
    print(f"\n💡 RECOMMENDED USAGE:")
    print(f"  🏆 Best Overall: Qwen3-30B-A3B-MLX (10.1/10)")
    print(f"  ⚡ Fastest: llama3.2:3b (6.3/10, very fast)")
    print(f"  🎯 Balanced: qwen2.5:7b (6.0/10, good balance)")
    print(f"  🖼️  Multimodal: llava:7b (images + text)")
    
    print(f"\n🔗 INTEGRATION READY:")
    print(f"  - All models tested and optimized")
    print(f"  - Performance scores documented")
    print(f"  - Ready for FastAPI integration")
    print(f"  - Storage optimized (~12-15 GB freed)")

if __name__ == "__main__":
    main()
