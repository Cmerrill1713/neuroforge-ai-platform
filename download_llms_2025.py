#!/usr/bin/env python3
"""
LLM Download Manager for Agentic LLM Core 2025
Downloads and configures the best LLMs for our system
"""

import asyncio
import logging
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LLMDownloadManager:
    """Manages downloading and configuring LLMs for our system."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.download_stats = {
            "total_downloads": 0,
            "successful_downloads": 0,
            "failed_downloads": 0,
            "total_size": 0,
            "download_time": 0
        }
        
        # Model definitions based on research
        self.models = {
            "tier1": {
                "qwen3-omni-14b": {
                    "ollama_name": "qwen3-omni:14b",
                    "size_gb": 8.0,
                    "description": "Primary multimodal model with enhanced reasoning",
                    "capabilities": ["multimodal", "reasoning", "coding"],
                    "priority": 1
                },
                "llama3.2-11b": {
                    "ollama_name": "llama3.2:11b", 
                    "size_gb": 6.0,
                    "description": "Advanced reasoning model for complex tasks",
                    "capabilities": ["reasoning", "planning", "analysis"],
                    "priority": 2
                },
                "deepseek-coder-v2": {
                    "ollama_name": "deepseek-coder:7b",
                    "size_gb": 7.0,
                    "description": "State-of-the-art coding model",
                    "capabilities": ["coding", "debugging", "analysis"],
                    "priority": 3
                },
                "llava-next-vl-7b": {
                    "ollama_name": "llava-next:7b",
                    "size_gb": 4.0,
                    "description": "Advanced vision and multimodal model",
                    "capabilities": ["vision", "multimodal", "image_analysis"],
                    "priority": 4
                }
            },
            "tier2": {
                "phi3.5-mini": {
                    "ollama_name": "phi3.5:mini",
                    "size_gb": 2.5,
                    "description": "Fast, efficient model for quick responses",
                    "capabilities": ["fast", "lightweight", "general"],
                    "priority": 5
                },
                "gemma2-9b": {
                    "ollama_name": "gemma2:9b",
                    "size_gb": 5.0,
                    "description": "Google's latest open model",
                    "capabilities": ["general", "reasoning", "instruction"],
                    "priority": 6
                },
                "qwen2.5-coder-7b": {
                    "ollama_name": "qwen2.5-coder:7b",
                    "size_gb": 4.0,
                    "description": "Qwen's specialized coding model",
                    "capabilities": ["coding", "specialized", "efficient"],
                    "priority": 7
                }
            },
            "tier3": {
                "deepseek-r1-7b": {
                    "ollama_name": "deepseek-r1:7b",
                    "size_gb": 4.0,
                    "description": "Novel reasoning approach (experimental)",
                    "capabilities": ["experimental", "reasoning", "research"],
                    "priority": 8
                },
                "llama3.2-3b": {
                    "ollama_name": "llama3.2:3b",
                    "size_gb": 2.0,
                    "description": "Ultra-fast responses",
                    "capabilities": ["ultra_fast", "lightweight", "simple"],
                    "priority": 9
                }
            }
        }
    
    async def check_ollama_status(self) -> bool:
        """Check if Ollama is running and accessible."""
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                self.logger.info("✅ Ollama is running and accessible")
                return True
            else:
                self.logger.error(f"❌ Ollama not accessible: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error("❌ Ollama command timed out")
            return False
        except FileNotFoundError:
            self.logger.error("❌ Ollama not found. Please install Ollama first.")
            return False
    
    async def get_current_models(self) -> List[str]:
        """Get list of currently installed models."""
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                models = []
                for line in result.stdout.strip().split('\n')[1:]:  # Skip header
                    if line.strip():
                        model_name = line.split()[0]
                        models.append(model_name)
                
                self.logger.info(f"📋 Found {len(models)} currently installed models")
                return models
            else:
                self.logger.error(f"Failed to list models: {result.stderr}")
                return []
                
        except Exception as e:
            self.logger.error(f"Error getting current models: {e}")
            return []
    
    async def download_model(self, model_name: str, ollama_name: str) -> Tuple[bool, str]:
        """Download a specific model."""
        
        self.logger.info(f"📥 Downloading {model_name} ({ollama_name})...")
        start_time = time.time()
        
        try:
            # Run ollama pull command
            process = subprocess.Popen(
                ["ollama", "pull", ollama_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Monitor progress
            stdout, stderr = process.communicate()
            
            download_time = time.time() - start_time
            
            if process.returncode == 0:
                self.logger.info(f"✅ Successfully downloaded {model_name} in {download_time:.1f}s")
                self.download_stats["successful_downloads"] += 1
                self.download_stats["download_time"] += download_time
                return True, stdout
            else:
                self.logger.error(f"❌ Failed to download {model_name}: {stderr}")
                self.download_stats["failed_downloads"] += 1
                return False, stderr
                
        except Exception as e:
            self.logger.error(f"❌ Error downloading {model_name}: {e}")
            self.download_stats["failed_downloads"] += 1
            return False, str(e)
    
    async def download_tier(self, tier: str, models: Dict[str, Dict]) -> Dict[str, bool]:
        """Download all models in a tier."""
        
        self.logger.info(f"🚀 Starting {tier.upper()} model downloads...")
        
        results = {}
        current_models = await self.get_current_models()
        
        for model_name, model_info in models.items():
            ollama_name = model_info["ollama_name"]
            
            # Check if model already exists
            if ollama_name in current_models:
                self.logger.info(f"⏭️  {model_name} already installed, skipping")
                results[model_name] = True
                continue
            
            # Download model
            success, message = await self.download_model(model_name, ollama_name)
            results[model_name] = success
            
            if success:
                self.download_stats["total_downloads"] += 1
                self.download_stats["total_size"] += model_info["size_gb"]
            
            # Add delay between downloads to avoid overwhelming system
            await asyncio.sleep(2)
        
        return results
    
    async def download_all_tier1(self) -> Dict[str, bool]:
        """Download all Tier 1 (essential) models."""
        return await self.download_tier("tier1", self.models["tier1"])
    
    async def download_all_tier2(self) -> Dict[str, bool]:
        """Download all Tier 2 (specialized) models."""
        return await self.download_tier("tier2", self.models["tier2"])
    
    async def download_all_tier3(self) -> Dict[str, bool]:
        """Download all Tier 3 (experimental) models."""
        return await self.download_tier("tier3", self.models["tier3"])
    
    async def download_specific_models(self, model_names: List[str]) -> Dict[str, bool]:
        """Download specific models by name."""
        
        self.logger.info(f"🎯 Downloading specific models: {', '.join(model_names)}")
        
        results = {}
        current_models = await self.get_current_models()
        
        for tier_name, tier_models in self.models.items():
            for model_name, model_info in tier_models.items():
                if model_name in model_names:
                    ollama_name = model_info["ollama_name"]
                    
                    if ollama_name in current_models:
                        self.logger.info(f"⏭️  {model_name} already installed, skipping")
                        results[model_name] = True
                        continue
                    
                    success, message = await self.download_model(model_name, ollama_name)
                    results[model_name] = success
                    
                    if success:
                        self.download_stats["total_downloads"] += 1
                        self.download_stats["total_size"] += model_info["size_gb"]
                    
                    await asyncio.sleep(2)
        
        return results
    
    def print_download_stats(self):
        """Print download statistics."""
        
        print("\n" + "="*60)
        print("📊 DOWNLOAD STATISTICS")
        print("="*60)
        print(f"Total Downloads: {self.download_stats['total_downloads']}")
        print(f"Successful: {self.download_stats['successful_downloads']}")
        print(f"Failed: {self.download_stats['failed_downloads']}")
        print(f"Total Size: {self.download_stats['total_size']:.1f} GB")
        print(f"Total Time: {self.download_stats['download_time']:.1f} seconds")
        
        if self.download_stats['total_downloads'] > 0:
            avg_time = self.download_stats['download_time'] / self.download_stats['total_downloads']
            print(f"Average Time per Model: {avg_time:.1f} seconds")
    
    def print_model_info(self):
        """Print information about available models."""
        
        print("\n" + "="*60)
        print("🧠 AVAILABLE MODELS FOR DOWNLOAD")
        print("="*60)
        
        for tier_name, tier_models in self.models.items():
            print(f"\n{tier_name.upper()} MODELS:")
            print("-" * 40)
            
            for model_name, model_info in tier_models.items():
                print(f"📦 {model_name}")
                print(f"   Ollama: {model_info['ollama_name']}")
                print(f"   Size: {model_info['size_gb']} GB")
                print(f"   Description: {model_info['description']}")
                print(f"   Capabilities: {', '.join(model_info['capabilities'])}")
                print()

async def main():
    """Main function for LLM download manager."""
    
    print("🧠 LLM Download Manager for Agentic LLM Core 2025")
    print("=" * 60)
    
    # Initialize download manager
    manager = LLMDownloadManager()
    
    # Check Ollama status
    if not await manager.check_ollama_status():
        print("❌ Please install and start Ollama first:")
        print("   brew install ollama")
        print("   ollama serve")
        return
    
    # Print model information
    manager.print_model_info()
    
    # Get user choice
    print("🎯 DOWNLOAD OPTIONS:")
    print("1. Download Tier 1 (Essential) models only")
    print("2. Download Tier 1 + Tier 2 (Essential + Specialized)")
    print("3. Download all models (Tier 1 + 2 + 3)")
    print("4. Download specific models")
    print("5. Show current models only")
    
    try:
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            print("\n🚀 Downloading Tier 1 models...")
            results = await manager.download_all_tier1()
            
        elif choice == "2":
            print("\n🚀 Downloading Tier 1 + Tier 2 models...")
            tier1_results = await manager.download_all_tier1()
            tier2_results = await manager.download_all_tier2()
            results = {**tier1_results, **tier2_results}
            
        elif choice == "3":
            print("\n🚀 Downloading all models...")
            tier1_results = await manager.download_all_tier1()
            tier2_results = await manager.download_all_tier2()
            tier3_results = await manager.download_all_tier3()
            results = {**tier1_results, **tier2_results, **tier3_results}
            
        elif choice == "4":
            print("\nAvailable models:")
            all_models = []
            for tier_models in manager.models.values():
                all_models.extend(tier_models.keys())
            
            for i, model in enumerate(all_models, 1):
                print(f"{i}. {model}")
            
            model_input = input("\nEnter model names (comma-separated): ").strip()
            model_names = [name.strip() for name in model_input.split(",")]
            
            results = await manager.download_specific_models(model_names)
            
        elif choice == "5":
            print("\n📋 Current models:")
            current_models = await manager.get_current_models()
            for model in current_models:
                print(f"   ✅ {model}")
            return
            
        else:
            print("❌ Invalid choice")
            return
        
        # Print results
        print("\n📊 DOWNLOAD RESULTS:")
        print("-" * 40)
        for model_name, success in results.items():
            status = "✅ Success" if success else "❌ Failed"
            print(f"{model_name}: {status}")
        
        # Print statistics
        manager.print_download_stats()
        
        print("\n🎉 Download process completed!")
        print("\n💡 Next steps:")
        print("   1. Update configs/policies.yaml with new models")
        print("   2. Test model integration")
        print("   3. Update agent profiles")
        print("   4. Run performance tests")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Download interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
