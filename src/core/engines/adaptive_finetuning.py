#!/usr/bin/env python3
"""
Adaptive Fine-tuning System
Automatically fine-tunes models to MLX when performance degrades
"""

import os
import json
import logging
import asyncio
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PerformanceGrade(Enum):
    """Performance grading levels"""
    EXCELLENT = "excellent"  # > 90% accuracy
    GOOD = "good"           # 80-90% accuracy
    FAIR = "fair"           # 70-80% accuracy
    POOR = "poor"           # 60-70% accuracy
    FAILING = "failing"     # < 60% accuracy

@dataclass
class PerformanceMetrics:
    """Performance metrics for model evaluation"""
    accuracy: float
    response_time: float
    user_satisfaction: float
    error_rate: float
    timestamp: datetime
    
    @property
    def grade(self) -> PerformanceGrade:
        """Calculate performance grade based on metrics"""
        if self.accuracy >= 0.90:
            return PerformanceGrade.EXCELLENT
        elif self.accuracy >= 0.80:
            return PerformanceGrade.GOOD
        elif self.accuracy >= 0.70:
            return PerformanceGrade.FAIR
        elif self.accuracy >= 0.60:
            return PerformanceGrade.POOR
        else:
            return PerformanceGrade.FAILING

@dataclass
class FineTuningTrigger:
    """Configuration for when to trigger fine-tuning"""
    consecutive_poor_grades: int = 3  # Trigger after 3 consecutive poor grades
    accuracy_threshold: float = 0.70  # Trigger if accuracy drops below 70%
    response_time_threshold: float = 5.0  # Trigger if response time exceeds 5 seconds
    error_rate_threshold: float = 0.10  # Trigger if error rate exceeds 10%
    min_samples: int = 10  # Minimum samples before triggering

class AdaptiveFineTuningSystem:
    """
    Adaptive fine-tuning system that monitors model performance
    and automatically fine-tunes to MLX when grading starts to fail
    """
    
    def __init__(self, config_path: str = "adaptive_finetuning_config.json"):
        self.config_path = config_path
        self.metrics_history: List[PerformanceMetrics] = []
        self.trigger_config = FineTuningTrigger()
        self.finetuning_in_progress = False
        self.last_finetuning = None
        
        # Load configuration
        self.load_config()
        
        # Knowledge base for fine-tuning
        self.knowledge_base_path = "knowledge_base"
        self.trained_models_path = "trained_models"
        self.mlx_models_path = "mlx_models"
        
        # Ensure directories exist
        Path(self.trained_models_path).mkdir(exist_ok=True)
        Path(self.mlx_models_path).mkdir(exist_ok=True)
    
    def load_config(self):
        """Load configuration from file"""
        if Path(self.config_path).exists():
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    self.trigger_config = FineTuningTrigger(**config.get('trigger', {}))
                    logger.info(f"Loaded configuration from {self.config_path}")
            except Exception as e:
                logger.warning(f"Failed to load config: {e}, using defaults")
        else:
            self.save_config()
    
    def save_config(self):
        """Save configuration to file"""
        config = {
            'trigger': {
                'consecutive_poor_grades': self.trigger_config.consecutive_poor_grades,
                'accuracy_threshold': self.trigger_config.accuracy_threshold,
                'response_time_threshold': self.trigger_config.response_time_threshold,
                'error_rate_threshold': self.trigger_config.error_rate_threshold,
                'min_samples': self.trigger_config.min_samples
            },
            'last_updated': datetime.now().isoformat()
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
    
    def record_performance(self, 
                          accuracy: float, 
                          response_time: float, 
                          user_satisfaction: float = 0.8,
                          error_rate: float = 0.0) -> PerformanceMetrics:
        """Record performance metrics"""
        metrics = PerformanceMetrics(
            accuracy=accuracy,
            response_time=response_time,
            user_satisfaction=user_satisfaction,
            error_rate=error_rate,
            timestamp=datetime.now()
        )
        
        self.metrics_history.append(metrics)
        
        # Keep only last 100 metrics to prevent memory bloat
        if len(self.metrics_history) > 100:
            self.metrics_history = self.metrics_history[-100:]
        
        logger.info(f"Recorded performance: {metrics.grade.value} (accuracy: {accuracy:.2f}, time: {response_time:.2f}s)")
        
        # Check if fine-tuning should be triggered
        if self.should_trigger_finetuning():
            asyncio.create_task(self.trigger_finetuning())
        
        return metrics
    
    def should_trigger_finetuning(self) -> bool:
        """Check if fine-tuning should be triggered"""
        if self.finetuning_in_progress:
            return False
        
        if len(self.metrics_history) < self.trigger_config.min_samples:
            return False
        
        # Check if we have enough consecutive poor grades
        recent_metrics = self.metrics_history[-self.trigger_config.consecutive_poor_grades:]
        if len(recent_metrics) >= self.trigger_config.consecutive_poor_grades:
            poor_grades = [m for m in recent_metrics if m.grade in [PerformanceGrade.POOR, PerformanceGrade.FAILING]]
            if len(poor_grades) >= self.trigger_config.consecutive_poor_grades:
                logger.warning(f"Triggering fine-tuning: {len(poor_grades)} consecutive poor grades")
                return True
        
        # Check current performance thresholds
        latest_metric = self.metrics_history[-1]
        if (latest_metric.accuracy < self.trigger_config.accuracy_threshold or
            latest_metric.response_time > self.trigger_config.response_time_threshold or
            latest_metric.error_rate > self.trigger_config.error_rate_threshold):
            logger.warning(f"Triggering fine-tuning: performance thresholds exceeded")
            return True
        
        return False
    
    async def trigger_finetuning(self):
        """Trigger fine-tuning process"""
        if self.finetuning_in_progress:
            logger.info("Fine-tuning already in progress, skipping")
            return
        
        self.finetuning_in_progress = True
        logger.info("🚀 Starting adaptive fine-tuning process...")
        
        try:
            # Determine which model to fine-tune
            model_to_finetune = await self.select_model_for_finetuning()
            
            if not model_to_finetune:
                logger.warning("No suitable model found for fine-tuning")
                return
            
            # Run fine-tuning pipeline
            success = await self.run_finetuning_pipeline(model_to_finetune)
            
            if success:
                logger.info("✅ Adaptive fine-tuning completed successfully!")
                self.last_finetuning = datetime.now()
                
                # Clear metrics history to start fresh
                self.metrics_history = []
                
                # Update system to use new MLX model
                await self.update_system_model(model_to_finetune)
            else:
                logger.error("❌ Adaptive fine-tuning failed")
                
        except Exception as e:
            logger.error(f"❌ Fine-tuning process failed: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.finetuning_in_progress = False
    
    async def select_model_for_finetuning(self) -> Optional[str]:
        """Select the best model for fine-tuning based on current performance"""
        # For now, use qwen2.5:7b as the primary model
        # In the future, this could be more sophisticated
        return "qwen2.5:7b"
    
    async def run_finetuning_pipeline(self, model_name: str) -> bool:
        """Run the complete fine-tuning pipeline"""
        logger.info(f"🔄 Running fine-tuning pipeline for {model_name}")
        
        try:
            # Step 1: Prepare training data from knowledge base
            training_data = await self.prepare_training_data()
            if not training_data:
                logger.error("No training data available")
                return False
            
            # Step 2: Create fine-tuning script
            script_path = await self.create_finetuning_script(model_name, training_data)
            
            # Step 3: Run fine-tuning
            logger.info("Starting fine-tuning...")
            result = subprocess.run([sys.executable, script_path], 
                                  capture_output=True, text=True, timeout=3600)
            
            if result.returncode != 0:
                logger.error(f"Fine-tuning failed: {result.stderr}")
                return False
            
            logger.info("✅ Fine-tuning completed")
            
            # Step 4: Convert to MLX
            trained_model_path = f"./trained_{model_name.replace(':', '_')}"
            mlx_success = await self.convert_to_mlx(model_name, trained_model_path)
            
            if not mlx_success:
                logger.error("MLX conversion failed")
                return False
            
            logger.info("✅ MLX conversion completed")
            
            return True
            
        except Exception as e:
            logger.error(f"Fine-tuning pipeline failed: {e}")
            return False
    
    async def prepare_training_data(self) -> List[Dict[str, Any]]:
        """Prepare training data from knowledge base and performance history"""
        training_data = []
        
        # Add knowledge base data
        if Path(self.knowledge_base_path).exists():
            for json_file in Path(self.knowledge_base_path).glob("*.json"):
                try:
                    with open(json_file, 'r') as f:
                        data = json.load(f)
                        
                    if isinstance(data, list):
                        for item in data:
                            if "content" in item:
                                training_data.append({
                                    "instruction": f"Based on the knowledge base, provide accurate information about:",
                                    "input": "",
                                    "output": item["content"]
                                })
                    elif isinstance(data, dict) and "content" in data:
                        training_data.append({
                            "instruction": f"Based on the knowledge base, provide accurate information about:",
                            "input": "",
                            "output": data["content"]
                        })
                except Exception as e:
                    logger.warning(f"Failed to load {json_file}: {e}")
        
        # Add performance-based training data
        if len(self.metrics_history) > 0:
            # Create training examples based on performance patterns
            recent_metrics = self.metrics_history[-10:]  # Last 10 metrics
            
            for metric in recent_metrics:
                if metric.grade in [PerformanceGrade.POOR, PerformanceGrade.FAILING]:
                    training_data.append({
                        "instruction": "Provide accurate and helpful responses with good performance:",
                        "input": "",
                        "output": "I will provide accurate, helpful responses with optimal performance and minimal errors."
                    })
        
        logger.info(f"Prepared {len(training_data)} training examples")
        return training_data
    
    async def create_finetuning_script(self, model_name: str, training_data: List[Dict[str, Any]]) -> str:
        """Create fine-tuning script"""
        script_content = f'''#!/usr/bin/env python3
"""
Adaptive Fine-tuning Script for {model_name}
Generated by Adaptive Fine-tuning System
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
training_examples = {json.dumps(training_data[:50])}  # Limit for efficiency

def format_instruction(example):
    """Format training example"""
    return f"<|im_start|>system\\nYou are a helpful AI assistant optimized for performance.<|im_end|>\\n<|im_start|>user\\n{{example['instruction']}}<|im_end|>\\n<|im_start|>assistant\\n{{example['output']}}<|im_end|>"

# Format data
formatted_data = [format_instruction(ex) for ex in training_examples]
dataset = Dataset.from_list([{{"text": text}} for text in formatted_data])

# Load model and tokenizer
base_model = "Qwen/Qwen2.5-7B-Instruct"
logger.info(f"Loading base model: {{base_model}}")

tokenizer = AutoTokenizer.from_pretrained(base_model)
model = AutoModelForCausalLM.from_pretrained(
    base_model,
    torch_dtype=torch.float16,
    device_map="auto"
)

# Training arguments optimized for adaptive fine-tuning
training_args = TrainingArguments(
    output_dir="./trained_{model_name.replace(':', '_')}",
    num_train_epochs=1,  # Single epoch for quick adaptation
    per_device_train_batch_size=1,
    per_device_eval_batch_size=1,
    warmup_steps=5,
    learning_rate=1e-5,  # Lower learning rate for stability
    logging_steps=5,
    save_steps=25,
    save_total_limit=1,
    prediction_loss_only=True,
    remove_unused_columns=False,
    dataloader_pin_memory=False,
    dataloader_num_workers=0,
    fp16=True,
    gradient_accumulation_steps=2,
    max_grad_norm=1.0,  # Gradient clipping for stability
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
logger.info("Starting adaptive fine-tuning...")
trainer.train()

# Save model
output_dir = "./trained_{model_name.replace(':', '_')}"
trainer.save_model(output_dir)
tokenizer.save_pretrained(output_dir)

logger.info(f"Adaptive fine-tuning completed! Model saved to {{output_dir}}")
'''
        
        script_path = f"adaptive_finetune_{model_name.replace(':', '_')}.py"
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        return script_path
    
    async def convert_to_mlx(self, model_name: str, trained_model_path: str) -> bool:
        """Convert fine-tuned model to MLX format"""
        logger.info(f"🔄 Converting {model_name} to MLX format...")
        
        try:
            # Install MLX-LM if not available
            try:
                import mlx_lm
            except ImportError:
                logger.info("Installing MLX-LM...")
                subprocess.run([sys.executable, "-m", "pip", "install", "mlx-lm"], check=True)
            
            # Create MLX conversion script
            conversion_script = f'''#!/usr/bin/env python3
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
            
            # Write and execute conversion script
            script_path = f"convert_{model_name.replace(':', '_')}_to_mlx.py"
            with open(script_path, 'w') as f:
                f.write(conversion_script)
            
            logger.info(f"Running MLX conversion: {script_path}")
            result = subprocess.run([sys.executable, script_path], 
                                  capture_output=True, text=True, timeout=1800)
            
            if result.returncode == 0:
                logger.info("✅ MLX conversion completed successfully")
                return True
            else:
                logger.error(f"MLX conversion failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"MLX conversion failed: {e}")
            return False
    
    async def update_system_model(self, model_name: str):
        """Update the system to use the new MLX model"""
        logger.info(f"🔄 Updating system to use new MLX model: {model_name}")
        
        # Create integration configuration
        config = {
            "model_name": model_name,
            "mlx_path": f"./mlx_{model_name.replace(':', '_')}",
            "created_at": datetime.now().isoformat(),
            "status": "active",
            "adaptive_finetuning": True,
            "performance_grade": "improved"
        }
        
        config_path = f"adaptive_config_{model_name.replace(':', '_')}.json"
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"✅ System updated with new MLX model configuration: {config_path}")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        if not self.metrics_history:
            return {"status": "no_data"}
        
        recent_metrics = self.metrics_history[-10:]  # Last 10 metrics
        
        return {
            "total_samples": len(self.metrics_history),
            "recent_accuracy": sum(m.accuracy for m in recent_metrics) / len(recent_metrics),
            "recent_response_time": sum(m.response_time for m in recent_metrics) / len(recent_metrics),
            "recent_error_rate": sum(m.error_rate for m in recent_metrics) / len(recent_metrics),
            "current_grade": recent_metrics[-1].grade.value if recent_metrics else "unknown",
            "finetuning_in_progress": self.finetuning_in_progress,
            "last_finetuning": self.last_finetuning.isoformat() if self.last_finetuning else None,
            "should_trigger": self.should_trigger_finetuning()
        }

# Global instance
_adaptive_system: Optional[AdaptiveFineTuningSystem] = None

def get_adaptive_system() -> AdaptiveFineTuningSystem:
    """Get the global adaptive fine-tuning system instance"""
    global _adaptive_system
    if _adaptive_system is None:
        _adaptive_system = AdaptiveFineTuningSystem()
    return _adaptive_system

# Convenience functions
def record_performance(accuracy: float, response_time: float, **kwargs) -> PerformanceMetrics:
    """Record performance metrics"""
    system = get_adaptive_system()
    return system.record_performance(accuracy, response_time, **kwargs)

def get_performance_summary() -> Dict[str, Any]:
    """Get performance summary"""
    system = get_adaptive_system()
    return system.get_performance_summary()

async def trigger_manual_finetuning(model_name: str = "qwen2.5:7b") -> bool:
    """Manually trigger fine-tuning"""
    system = get_adaptive_system()
    return await system.run_finetuning_pipeline(model_name)
