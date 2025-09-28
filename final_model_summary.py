#!/usr/bin/env python3
"""
Final Model Summary - Complete integration of all models
"""

import json
import subprocess
from pathlib import Path
from datetime import datetime

class FinalModelSummary:
    """Complete summary of all available models"""
    
    def __init__(self):
        self.ollama_models = [
            {"name": "qwen3:8b", "size": "5.2 GB", "type": "text-generation", "status": "working"},
            {"name": "llama3.1:8b", "size": "4.9 GB", "type": "text-generation", "status": "working"},
            {"name": "qwen2.5:7b", "size": "4.7 GB", "type": "text-generation", "status": "working"},
            {"name": "phi3:3.8b", "size": "2.2 GB", "type": "text-generation", "status": "working"},
            {"name": "mistral:7b", "size": "4.4 GB", "type": "text-generation", "status": "working"},
            {"name": "llama3.2:3b", "size": "2.0 GB", "type": "text-generation", "status": "working"},
            {"name": "llava:7b", "size": "4.7 GB", "type": "multimodal", "status": "working"},
            {"name": "nomic-embed-text:latest", "size": "274 MB", "type": "embeddings", "status": "error"},
            {"name": "gpt-oss:20b", "size": "13 GB", "type": "text-generation", "status": "working"},
        ]
        
        self.mlx_models = [
            {"name": "Qwen3-30B-A3B-Instruct-2507-MLX-4bit", "size": "16.0 GB", "type": "text-generation", "status": "working"},
            {"name": "Dia-1.6B", "size": "6.0 GB", "type": "text-generation", "status": "working"},
            {"name": "Marvis-TTS-250m-v0.1-MLX-4bit", "size": "0.8 GB", "type": "text-to-speech", "status": "working"},
            {"name": "Marvis-TTS-250m-v0.1-MLX-8bit", "size": "1.2 GB", "type": "text-to-speech", "status": "working"},
            {"name": "Marvis-TTS-250m-v0.1-MLX-fp16", "size": "4.2 GB", "type": "text-to-speech", "status": "working"},
        ]
        
        self.huggingface_models = [
            {"name": "Qwen2-1.5B-Instruct", "size": "5.8 GB", "type": "text-generation", "status": "found"},
            {"name": "Qwen2-7B-Instruct", "size": "28.4 GB", "type": "text-generation", "status": "found"},
            {"name": "Qwen2.5-7B-Instruct", "size": "28.4 GB", "type": "text-generation", "status": "found"},
            {"name": "Qwen3-Omni-30B-A3B-Instruct", "size": "0.0 GB", "type": "multimodal", "status": "found"},
            {"name": "Facebook-MMS-TTS-eng", "size": "0.3 GB", "type": "text-to-speech", "status": "found"},
            {"name": "Microsoft-VibeVoice-1.5B", "size": "0.0 GB", "type": "text-to-speech", "status": "found"},
            {"name": "Microsoft-SpeechT5-TTS", "size": "2.2 GB", "type": "text-to-speech", "status": "found"},
            {"name": "Microsoft-SpeechT5-HiFiGAN", "size": "0.2 GB", "type": "text-to-speech", "status": "found"},
            {"name": "Descript-DAC-44khz", "size": "0.6 GB", "type": "audio-processing", "status": "found"},
            {"name": "Kyutai-Moshiko-PyTorch-bf16", "size": "0.7 GB", "type": "text-to-speech", "status": "found"},
            {"name": "LMStudio-Qwen3-Coder-30B-A3B-Instruct-MLX-5bit", "size": "39.1 GB", "type": "code-generation", "status": "found"},
            {"name": "Microsoft-DialoGPT-medium", "size": "0.0 GB", "type": "chat", "status": "found"},
        ]
        
        self.new_models = [
            {"name": "WAN-2.5", "type": "video-generation", "status": "online"},
            {"name": "Qwen-Image-Edit-2509", "type": "image-editing", "status": "online"},
        ]
    
    def calculate_total_storage(self) -> float:
        """Calculate total storage used by all models"""
        total = 0
        
        for model_list in [self.ollama_models, self.mlx_models, self.huggingface_models]:
            for model in model_list:
                try:
                    size_str = model["size"].replace(" GB", "").replace(" MB", "")
                    size_value = float(size_str)
                    if "MB" in model["size"]:
                        size_value = size_value / 1024  # Convert MB to GB
                    total += size_value
                except:
                    pass
        
        return total
    
    def count_models_by_type(self) -> dict:
        """Count models by type"""
        type_counts = {}
        
        for model_list in [self.ollama_models, self.mlx_models, self.huggingface_models, self.new_models]:
            for model in model_list:
                model_type = model["type"]
                if model_type not in type_counts:
                    type_counts[model_type] = {"total": 0, "working": 0}
                
                type_counts[model_type]["total"] += 1
                if model["status"] in ["working", "found"]:
                    type_counts[model_type]["working"] += 1
        
        return type_counts
    
    def generate_comprehensive_summary(self):
        """Generate comprehensive model summary"""
        
        print("🚀 COMPLETE AI MODEL COLLECTION SUMMARY")
        print("=" * 60)
        
        # Total counts
        total_ollama = len(self.ollama_models)
        working_ollama = sum(1 for m in self.ollama_models if m["status"] == "working")
        
        total_mlx = len(self.mlx_models)
        working_mlx = sum(1 for m in self.mlx_models if m["status"] == "working")
        
        total_hf = len(self.huggingface_models)
        found_hf = sum(1 for m in self.huggingface_models if m["status"] == "found")
        
        total_new = len(self.new_models)
        
        total_models = total_ollama + total_mlx + total_hf + total_new
        total_working = working_ollama + working_mlx + found_hf + total_new
        
        print(f"📊 TOTAL MODELS: {total_models}")
        print(f"✅ WORKING/FOUND: {total_working}")
        print(f"💾 TOTAL STORAGE: {self.calculate_total_storage():.1f} GB")
        
        # Model breakdown
        print(f"\n📋 MODEL BREAKDOWN:")
        print(f"  🧠 Ollama Models: {working_ollama}/{total_ollama} working")
        print(f"  ⚡ MLX Models: {working_mlx}/{total_mlx} working")
        print(f"  🤗 HuggingFace Models: {found_hf}/{total_hf} found")
        print(f"  🆕 New Models: {total_new} available online")
        
        # Type breakdown
        type_counts = self.count_models_by_type()
        print(f"\n🎯 MODELS BY TYPE:")
        for model_type, counts in type_counts.items():
            working = counts["working"]
            total = counts["total"]
            print(f"  {model_type}: {working}/{total} available")
        
        # Detailed model lists
        self.print_detailed_lists()
        
        # Usage recommendations
        self.print_usage_recommendations()
        
        # Save summary
        self.save_summary()
    
    def print_detailed_lists(self):
        """Print detailed model lists"""
        
        print(f"\n📋 DETAILED MODEL LISTS:")
        print("=" * 40)
        
        print(f"\n🧠 OLLAMA MODELS (Ready to use):")
        for model in self.ollama_models:
            status_icon = "✅" if model["status"] == "working" else "❌"
            print(f"  {status_icon} {model['name']} ({model['size']}) - {model['type']}")
        
        print(f"\n⚡ MLX MODELS (High performance):")
        for model in self.mlx_models:
            status_icon = "✅" if model["status"] == "working" else "❌"
            print(f"  {status_icon} {model['name']} ({model['size']}) - {model['type']}")
        
        print(f"\n🤗 HUGGINGFACE MODELS (Specialized):")
        for model in self.huggingface_models:
            status_icon = "✅" if model["status"] == "found" else "❌"
            print(f"  {status_icon} {model['name']} ({model['size']}) - {model['type']}")
        
        print(f"\n🆕 NEW MODELS (Online access):")
        for model in self.new_models:
            status_icon = "🌐" if model["status"] == "online" else "❌"
            print(f"  {status_icon} {model['name']} - {model['type']}")
    
    def print_usage_recommendations(self):
        """Print usage recommendations"""
        
        print(f"\n💡 USAGE RECOMMENDATIONS:")
        print("=" * 40)
        
        print(f"\n🎯 BEST MODELS FOR DIFFERENT TASKS:")
        
        print(f"\n  🧠 Text Generation:")
        print(f"    - llama3.1:8b (best reasoning)")
        print(f"    - qwen3:8b (latest capabilities)")
        print(f"    - Qwen3-30B-A3B-MLX (most powerful)")
        
        print(f"\n  🖼️  Multimodal (Image + Text):")
        print(f"    - llava:7b (basic image understanding)")
        print(f"    - Qwen3-Omni-30B (advanced multimodal)")
        
        print(f"\n  🎤 Text-to-Speech:")
        print(f"    - Marvis-TTS-MLX models (high quality)")
        print(f"    - Microsoft VibeVoice (professional)")
        print(f"    - Facebook MMS-TTS (multilingual)")
        
        print(f"\n  💻 Code Generation:")
        print(f"    - Qwen3-Coder-30B-MLX (specialized)")
        print(f"    - llama3.1:8b (general coding)")
        
        print(f"\n  ⚡ Fast Inference:")
        print(f"    - phi3:3.8b (lightweight)")
        print(f"    - llama3.2:3b (fastest)")
        
        print(f"\n🔗 INTEGRATION OPPORTUNITIES:")
        print(f"  1. Connect all models to your FastAPI server")
        print(f"  2. Create intelligent model routing")
        print(f"  3. Build multimodal workflows")
        print(f"  4. Develop voice AI applications")
        print(f"  5. Enhance your existing knowledge base")
    
    def save_summary(self):
        """Save comprehensive summary to file"""
        
        summary_data = {
            "timestamp": datetime.now().isoformat(),
            "total_models": len(self.ollama_models) + len(self.mlx_models) + len(self.huggingface_models) + len(self.new_models),
            "total_storage_gb": self.calculate_total_storage(),
            "model_breakdown": {
                "ollama": {"total": len(self.ollama_models), "working": sum(1 for m in self.ollama_models if m["status"] == "working")},
                "mlx": {"total": len(self.mlx_models), "working": sum(1 for m in self.mlx_models if m["status"] == "working")},
                "huggingface": {"total": len(self.huggingface_models), "found": sum(1 for m in self.huggingface_models if m["status"] == "found")},
                "new": {"total": len(self.new_models)}
            },
            "models_by_type": self.count_models_by_type(),
            "all_models": {
                "ollama": self.ollama_models,
                "mlx": self.mlx_models,
                "huggingface": self.huggingface_models,
                "new": self.new_models
            }
        }
        
        with open("final_model_summary.json", "w") as f:
            json.dump(summary_data, f, indent=2)
        
        print(f"\n💾 Complete summary saved to: final_model_summary.json")
        print(f"\n🎉 You now have access to {summary_data['total_models']} AI models!")
        print(f"   Total storage: {summary_data['total_storage_gb']:.1f} GB")
        print(f"   Ready for integration with your existing system!")

def main():
    """Main function"""
    summary = FinalModelSummary()
    summary.generate_comprehensive_summary()

if __name__ == "__main__":
    main()
