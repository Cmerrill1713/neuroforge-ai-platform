#!/usr/bin/env python3
"""
Ollama-MLX Integration Pipeline
Leverages existing Ollama models for training and MLX conversion
"""

import os
import sys
import json
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OllamaMLXIntegration:
    """
    Integration pipeline for Ollama models → Training → MLX conversion
    """
    
    def __init__(self):
        self.ollama_models = {
            "qwen2.5:7b": {
                "size": "4.7 GB",
                "description": "Primary model for chat and reasoning",
                "best_for": ["chat", "reasoning", "code_generation"],
                "priority": 1
            },
            "qwen2.5:14b": {
                "size": "9.0 GB", 
                "description": "Larger model for complex tasks",
                "best_for": ["complex_reasoning", "analysis", "research"],
                "priority": 2
            },
            "qwen2.5:72b": {
                "size": "47 GB",
                "description": "Largest model for advanced reasoning",
                "best_for": ["advanced_reasoning", "research", "analysis"],
                "priority": 3
            },
            "llama3.2:3b": {
                "size": "2.0 GB",
                "description": "Lightweight model for fast responses",
                "best_for": ["fast_chat", "devops", "quick_tasks"],
                "priority": 4
            },
            "mistral:7b": {
                "size": "4.4 GB",
                "description": "Balanced model for general tasks",
                "best_for": ["general_chat", "backend_tasks"],
                "priority": 5
            },
            "llava:7b": {
                "size": "4.7 GB",
                "description": "Multimodal model for vision tasks",
                "best_for": ["vision", "multimodal", "image_analysis"],
                "priority": 6
            },
            "nomic-embed-text:latest": {
                "size": "274 MB",
                "description": "Embedding model for semantic search",
                "best_for": ["embeddings", "semantic_search"],
                "priority": 7
            },
            "gpt-oss:20b": {
                "size": "13 GB",
                "description": "Large model for complex reasoning",
                "best_for": ["complex_reasoning", "analysis"],
                "priority": 8
            }
        }
        
        self.knowledge_base_path = "knowledge_base"
        self.training_output_dir = "trained_models"
        self.mlx_output_dir = "mlx_models"
        
    def check_ollama_status(self) -> bool:
        """Check if Ollama is running and models are available"""
        try:
            result = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                logger.info("✅ Ollama is running")
                logger.info(f"Available models:\n{result.stdout}")
                return True
            else:
                logger.error("❌ Ollama is not running")
                return False
        except Exception as e:
            logger.error(f"❌ Error checking Ollama status: {e}")
            return False
    
    def test_ollama_model(self, model_name: str) -> Dict[str, Any]:
        """Test an Ollama model"""
        logger.info(f"🧠 Testing Ollama model: {model_name}")
        
        try:
            test_prompt = f"Hello! You are {model_name}. Please respond with a brief introduction of your capabilities."
            
            result = subprocess.run([
                "ollama", "run", model_name, test_prompt
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                response = result.stdout.strip()
                logger.info(f"✅ {model_name}: Working")
                return {
                    "status": "working",
                    "response": response[:100] + "..." if len(response) > 100 else response,
                    "error": None
                }
            else:
                logger.error(f"❌ {model_name}: Error - {result.stderr}")
                return {
                    "status": "error",
                    "response": None,
                    "error": result.stderr
                }
                
        except subprocess.TimeoutExpired:
            logger.warning(f"⏱️ {model_name}: Timeout")
            return {
                "status": "timeout",
                "response": None,
                "error": "Request timed out"
            }
        except Exception as e:
            logger.error(f"❌ {model_name}: Exception - {e}")
            return {
                "status": "error",
                "response": None,
                "error": str(e)
            }
    
    def prepare_knowledge_base_for_training(self) -> List[Dict[str, Any]]:
        """Prepare knowledge base data for training"""
        logger.info("📚 Preparing knowledge base for training...")
        
        training_data = []
        
        if not Path(self.knowledge_base_path).exists():
            logger.warning(f"Knowledge base directory not found: {self.knowledge_base_path}")
            return training_data
        
        # Load all JSON files from knowledge base
        for json_file in Path(self.knowledge_base_path).glob("*.json"):
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    
                if isinstance(data, list):
                    for item in data:
                        if "content" in item:
                            training_data.append({
                                "instruction": f"Based on the knowledge base, answer this question about {item.get('metadata', {}).get('category', 'general')}:",
                                "input": "",
                                "output": item["content"]
                            })
                elif isinstance(data, dict) and "content" in data:
                    training_data.append({
                        "instruction": f"Based on the knowledge base, provide information about:",
                        "input": "",
                        "output": data["content"]
                    })
                    
            except Exception as e:
                logger.warning(f"Failed to load {json_file}: {e}")
        
        logger.info(f"✅ Prepared {len(training_data)} training examples")
        return training_data
    
    def create_training_script(self, model_name: str, training_data: List[Dict[str, Any]]) -> str:
        """Create a training script for fine-tuning"""
        script_content = f'''#!/usr/bin/env python3
"""
Fine-tuning script for {model_name}
"""

import json
import torch
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM, 
    TrainingArguments, 
    Trainer,
    DataCollatorForLanguageModeling
)
from datasets import Dataset
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Training data
training_examples = {json.dumps(training_data[:100])}  # Limit for testing

def format_instruction(example):
    """Format training example"""
    return f"<|im_start|>system\\nYou are a helpful AI assistant.<|im_end|>\\n<|im_start|>user\\n{{example['instruction']}}<|im_end|>\\n<|im_start|>assistant\\n{{example['output']}}<|im_end|>"

# Format data
formatted_data = [format_instruction(ex) for ex in training_examples]
dataset = Dataset.from_list([{{"text": text}} for text in formatted_data])

# Load model and tokenizer
model_name = "{model_name}"
logger.info(f"Loading model: {{model_name}}")

# Use a base model for fine-tuning
base_model = "Qwen/Qwen2.5-7B-Instruct"  # Use Qwen as base
tokenizer = AutoTokenizer.from_pretrained(base_model)
model = AutoModelForCausalLM.from_pretrained(
    base_model,
    torch_dtype=torch.float16,
    device_map="auto"
)

# Training arguments
training_args = TrainingArguments(
    output_dir="./trained_{model_name.replace(':', '_')}",
    num_train_epochs=1,  # Single epoch for testing
    per_device_train_batch_size=1,
    per_device_eval_batch_size=1,
    warmup_steps=10,
    learning_rate=5e-5,
    logging_steps=5,
    save_steps=50,
    save_total_limit=2,
    prediction_loss_only=True,
    remove_unused_columns=False,
    dataloader_pin_memory=False,
    dataloader_num_workers=0,
    fp16=True,
    gradient_accumulation_steps=2,
)

# Create trainer
data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset,
    data_collator=data_collator,
)

# Train
logger.info("Starting training...")
trainer.train()

# Save model
output_dir = "./trained_{model_name.replace(':', '_')}"
trainer.save_model(output_dir)
tokenizer.save_pretrained(output_dir)

logger.info(f"Fine-tuning completed! Model saved to {{output_dir}}")
'''
        return script_content
    
    def create_mlx_conversion_script(self, model_name: str, trained_model_path: str) -> str:
        """Create MLX conversion script"""
        script_content = f'''#!/usr/bin/env python3
"""
MLX conversion script for {model_name}
"""

import os
from mlx_lm import convert

# Convert to MLX
mlx_output_path = "./mlx_{model_name.replace(':', '_')}"

convert(
    hf_path="{trained_model_path}",
    mlx_path=mlx_output_path,
    quantize=True,
    q_group_size=64,
    q_bits=4,
)

print(f"✅ Model converted to MLX format: {{mlx_output_path}}")

# Test the converted model
from mlx_lm import load, generate

model, tokenizer = load(mlx_output_path)

# Test generation
test_prompt = "Hello, how are you?"
print(f"Test prompt: {{test_prompt}}")

response = generate(
    model=model,
    tokenizer=tokenizer,
    prompt=test_prompt,
    max_tokens=50,
    temp=0.7,
    verbose=True
)

print(f"Response: {{response}}")
print(f"\\n🎉 MLX conversion and testing completed successfully!")
'''
        return script_content
    
    def run_training_pipeline(self, model_name: str) -> bool:
        """Run the complete training pipeline"""
        logger.info(f"🚀 Starting training pipeline for {model_name}")
        
        try:
            # Step 1: Test Ollama model
            test_result = self.test_ollama_model(model_name)
            if test_result["status"] != "working":
                logger.error(f"Ollama model {model_name} is not working")
                return False
            
            # Step 2: Prepare training data
            training_data = self.prepare_knowledge_base_for_training()
            if not training_data:
                logger.error("No training data available")
                return False
            
            # Step 3: Create and run training script
            training_script = self.create_training_script(model_name, training_data)
            script_path = f"train_{model_name.replace(':', '_')}.py"
            
            with open(script_path, 'w') as f:
                f.write(training_script)
            
            logger.info(f"Running training script: {script_path}")
            result = subprocess.run([sys.executable, script_path], 
                                  capture_output=True, text=True, timeout=3600)
            
            if result.returncode != 0:
                logger.error(f"Training failed: {result.stderr}")
                return False
            
            logger.info("✅ Training completed successfully")
            
            # Step 4: Convert to MLX
            trained_model_path = f"./trained_{model_name.replace(':', '_')}"
            mlx_script = self.create_mlx_conversion_script(model_name, trained_model_path)
            mlx_script_path = f"convert_{model_name.replace(':', '_')}_to_mlx.py"
            
            with open(mlx_script_path, 'w') as f:
                f.write(mlx_script)
            
            logger.info(f"Running MLX conversion: {mlx_script_path}")
            result = subprocess.run([sys.executable, mlx_script_path], 
                                  capture_output=True, text=True, timeout=1800)
            
            if result.returncode != 0:
                logger.error(f"MLX conversion failed: {result.stderr}")
                return False
            
            logger.info("✅ MLX conversion completed successfully")
            
            # Step 5: Create integration config
            self.create_integration_config(model_name)
            
            logger.info(f"🎉 Complete pipeline finished for {model_name}!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Pipeline failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def create_integration_config(self, model_name: str):
        """Create integration configuration for the trained model"""
        config = {
            "model_name": model_name,
            "trained_path": f"./trained_{model_name.replace(':', '_')}",
            "mlx_path": f"./mlx_{model_name.replace(':', '_')}",
            "created_at": datetime.now().isoformat(),
            "status": "ready",
            "capabilities": self.ollama_models.get(model_name, {}).get("best_for", []),
            "integration": {
                "api_endpoint": f"/api/chat/mlx/{model_name.replace(':', '_')}",
                "model_type": "mlx",
                "quantization": "4bit",
                "optimization": "apple_silicon"
            }
        }
        
        config_path = f"config_{model_name.replace(':', '_')}.json"
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"✅ Integration config created: {config_path}")
    
    def run_complete_integration(self):
        """Run complete integration for all Ollama models"""
        logger.info("🚀 Starting Ollama-MLX Integration Pipeline")
        logger.info("=" * 60)
        
        # Check Ollama status
        if not self.check_ollama_status():
            logger.error("Ollama is not available. Please start Ollama first.")
            return False
        
        # Start with the primary model
        primary_model = "qwen2.5:7b"
        logger.info(f"Starting with primary model: {primary_model}")
        
        success = self.run_training_pipeline(primary_model)
        
        if success:
            logger.info("🎉 Primary model integration completed successfully!")
            logger.info("You can now:")
            logger.info("1. Use the trained MLX model in your API")
            logger.info("2. Run additional models through the pipeline")
            logger.info("3. Integrate with your existing system")
        else:
            logger.error("❌ Primary model integration failed")
        
        return success

def main():
    """Main function"""
    integration = OllamaMLXIntegration()
    success = integration.run_complete_integration()
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
