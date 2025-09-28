#!/usr/bin/env python3
"""
Advanced Qwen3-Omni Quantization & Memory Optimization

This script uses advanced quantization techniques and memory optimization
to fit the Qwen3-Omni model in available RAM and VRAM.
"""

import os
import torch
import logging
import psutil
from transformers import (
    AutoTokenizer,
    Qwen3OmniMoeForConditionalGeneration,
    BitsAndBytesConfig
)
from peft import LoraConfig, get_peft_model, TaskType
import gc
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AdvancedQuantizationEngine:
    """Advanced quantization and memory optimization for Qwen3-Omni"""
    
    def __init__(self):
        self.model_path = "./Qwen3-Omni-30B-A3B-Instruct"
        self.available_memory = self._get_available_memory()
        
    def _get_available_memory(self):
        """Get available system memory"""
        memory = psutil.virtual_memory()
        return {
            'total_gb': memory.total / 1024**3,
            'available_gb': memory.available / 1024**3,
            'used_gb': memory.used / 1024**3
        }
    
    def _get_mps_memory(self):
        """Get MPS memory info if available"""
        if torch.backends.mps.is_available():
            try:
                # Force MPS to initialize
                dummy = torch.randn(1, device='mps')
                return {
                    'available': True,
                    'device': 'mps'
                }
            except:
                return {'available': False}
        return {'available': False}
    
    def create_quantization_configs(self):
        """Create multiple quantization configurations"""
        configs = {}
        
        # 4-bit quantization with different settings
        configs['4bit_nf4'] = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
            bnb_4bit_compute_dtype=torch.bfloat16
        )
        
        configs['4bit_fp4'] = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="fp4",
            bnb_4bit_use_double_quant=True,
            bnb_4bit_compute_dtype=torch.bfloat16
        )
        
        # 8-bit quantization
        configs['8bit'] = BitsAndBytesConfig(
            load_in_8bit=True,
            bnb_8bit_compute_dtype=torch.bfloat16
        )
        
        # Mixed precision
        configs['mixed_precision'] = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
            bnb_4bit_compute_dtype=torch.float16
        )
        
        return configs
    
    def create_lora_config(self):
        """Create LoRA configuration for additional memory savings"""
        return LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            inference_mode=False,
            r=8,  # Lower rank for memory efficiency
            lora_alpha=16,
            lora_dropout=0.1,
            target_modules=["q_proj", "k_proj", "v_proj", "o_proj"]
        )
    
    def optimize_memory_settings(self):
        """Optimize PyTorch memory settings"""
        logger.info("🔧 Optimizing memory settings...")
        
        # Enable memory efficient attention if available
        if hasattr(torch.backends.cuda, 'enable_flash_sdp'):
            torch.backends.cuda.enable_flash_sdp(True)
        
        # Set memory fraction for MPS if available
        if torch.backends.mps.is_available():
            # MPS doesn't have memory fraction, but we can optimize
            torch.mps.empty_cache()
        
        # Enable memory efficient loading
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.allow_tf32 = True
        
        logger.info("✅ Memory settings optimized")
    
    def try_quantized_loading(self, config_name, config):
        """Try loading model with specific quantization config"""
        logger.info(f"🧪 Trying {config_name} quantization...")
        
        try:
            # Clear memory first
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            if torch.backends.mps.is_available():
                torch.mps.empty_cache()
            
            # Load tokenizer
            tokenizer = AutoTokenizer.from_pretrained(
                self.model_path, 
                trust_remote_code=True
            )
            
            # Load model with quantization
            start_time = time.time()
            
            model = Qwen3OmniMoeForConditionalGeneration.from_pretrained(
                self.model_path,
                quantization_config=config,
                torch_dtype=torch.float16,
                device_map="auto",
                trust_remote_code=True,
                low_cpu_mem_usage=True,
                max_memory={0: "20GB", "cpu": "40GB"}  # Memory limits
            )
            
            load_time = time.time() - start_time
            memory_after = self._get_available_memory()
            memory_used = self.available_memory['available_gb'] - memory_after['available_gb']
            
            logger.info(f"✅ {config_name} successful!")
            logger.info(f"   Load time: {load_time:.2f}s")
            logger.info(f"   Memory used: {memory_used:.2f}GB")
            
            # Test inference
            test_prompt = "Hello, how are you?"
            inputs = tokenizer(test_prompt, return_tensors="pt")
            
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=20,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id
                )
            
            response = tokenizer.decode(outputs[0], skip_special_tokens=True)
            logger.info(f"   Test response: {response[len(test_prompt):].strip()}")
            
            return model, tokenizer, True
            
        except Exception as e:
            logger.warning(f"❌ {config_name} failed: {e}")
            return None, None, False
    
    def try_lora_quantization(self):
        """Try LoRA + quantization combination"""
        logger.info("🧪 Trying LoRA + 4-bit quantization...")
        
        try:
            # Clear memory
            gc.collect()
            
            # Load tokenizer
            tokenizer = AutoTokenizer.from_pretrained(
                self.model_path, 
                trust_remote_code=True
            )
            
            # Create quantization config
            quant_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=True,
                bnb_4bit_compute_dtype=torch.bfloat16
            )
            
            # Load base model
            model = Qwen3OmniMoeForConditionalGeneration.from_pretrained(
                self.model_path,
                quantization_config=quant_config,
                torch_dtype=torch.float16,
                device_map="auto",
                trust_remote_code=True,
                low_cpu_mem_usage=True
            )
            
            # Apply LoRA
            lora_config = self.create_lora_config()
            model = get_peft_model(model, lora_config)
            
            logger.info("✅ LoRA + 4-bit quantization successful!")
            
            # Test inference
            test_prompt = "What is AI?"
            inputs = tokenizer(test_prompt, return_tensors="pt")
            
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=30,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id
                )
            
            response = tokenizer.decode(outputs[0], skip_special_tokens=True)
            logger.info(f"   Test response: {response[len(test_prompt):].strip()}")
            
            return model, tokenizer, True
            
        except Exception as e:
            logger.warning(f"❌ LoRA + quantization failed: {e}")
            return None, None, False
    
    def try_mps_optimization(self):
        """Try MPS-specific optimizations"""
        logger.info("🧪 Trying MPS optimization...")
        
        if not torch.backends.mps.is_available():
            logger.info("❌ MPS not available")
            return None, None, False
        
        try:
            # Set MPS as default device
            torch.set_default_device('mps')
            
            # Load tokenizer
            tokenizer = AutoTokenizer.from_pretrained(
                self.model_path, 
                trust_remote_code=True
            )
            
            # Load model with MPS optimization
            model = Qwen3OmniMoeForConditionalGeneration.from_pretrained(
                self.model_path,
                torch_dtype=torch.float16,
                device_map="mps",
                trust_remote_code=True,
                low_cpu_mem_usage=True,
                max_memory={"mps": "20GB", "cpu": "40GB"}
            )
            
            logger.info("✅ MPS optimization successful!")
            
            # Test inference
            test_prompt = "Hello"
            inputs = tokenizer(test_prompt, return_tensors="pt").to('mps')
            
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=10,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id
                )
            
            response = tokenizer.decode(outputs[0], skip_special_tokens=True)
            logger.info(f"   Test response: {response[len(test_prompt):].strip()}")
            
            return model, tokenizer, True
            
        except Exception as e:
            logger.warning(f"❌ MPS optimization failed: {e}")
            # Reset default device
            torch.set_default_device('cpu')
            return None, None, False
    
    def run_advanced_quantization(self):
        """Run all advanced quantization attempts"""
        logger.info("🚀 Advanced Qwen3-Omni Quantization & Memory Optimization")
        logger.info("=" * 70)
        
        # System info
        logger.info(f"📊 System Memory: {self.available_memory['available_gb']:.1f}GB available")
        mps_info = self._get_mps_memory()
        logger.info(f"📊 MPS Available: {mps_info['available']}")
        
        # Optimize memory settings
        self.optimize_memory_settings()
        
        # Try different quantization approaches
        quantization_configs = self.create_quantization_configs()
        successful_configs = []
        
        # Test quantization configs
        for config_name, config in quantization_configs.items():
            model, tokenizer, success = self.try_quantized_loading(config_name, config)
            if success:
                successful_configs.append(config_name)
                # Clean up for next test
                del model, tokenizer
                gc.collect()
        
        # Test LoRA + quantization
        model, tokenizer, lora_success = self.try_lora_quantization()
        if lora_success:
            successful_configs.append("lora_4bit")
            del model, tokenizer
            gc.collect()
        
        # Test MPS optimization
        model, tokenizer, mps_success = self.try_mps_optimization()
        if mps_success:
            successful_configs.append("mps_optimized")
            del model, tokenizer
            gc.collect()
        
        # Results
        logger.info(f"\n🎯 RESULTS:")
        logger.info(f"Successful configurations: {len(successful_configs)}")
        
        if successful_configs:
            logger.info("✅ Working configurations:")
            for config in successful_configs:
                logger.info(f"   - {config}")
            
            logger.info(f"\n🎉 SUCCESS! Found {len(successful_configs)} working configurations")
            logger.info("The Qwen3-Omni model can be loaded with advanced quantization!")
            
            return successful_configs
        else:
            logger.info("❌ No configurations worked")
            logger.info("The model is still too large for available memory")
            
            return []

def main():
    """Main function"""
    engine = AdvancedQuantizationEngine()
    successful_configs = engine.run_advanced_quantization()
    
    if successful_configs:
        print(f"\n🎉 SUCCESS! Working configurations: {successful_configs}")
        return True
    else:
        print("\n❌ No working configurations found")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
