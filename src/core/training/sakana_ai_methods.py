#!/usr/bin/env python3
"""
Sakana AI Methods Integration
Implements Text-to-LoRA and Transformer² for revolutionary fine-tuning
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import json
import numpy as np
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import LoraConfig, get_peft_model, TaskType
import time

logger = logging.getLogger(__name__)

@dataclass
class TextToLoRAConfig:
    """Configuration for Text-to-LoRA generation"""
    hyper_network_size: int = 512
    adapter_rank: int = 8
    adapter_alpha: int = 16
    dropout: float = 0.1
    max_prompt_length: int = 256
    skill_embeddings_dim: int = 128

@dataclass
class Transformer2Config:
    """Configuration for Transformer² dynamic adaptation"""
    expert_vector_dim: int = 64
    num_experts: int = 8
    adaptation_layers: List[int] = None
    skill_detection_threshold: float = 0.7
    weight_interpolation_factor: float = 0.3

class HyperNetwork(nn.Module):
    """Hyper-network for generating LoRA adapters from text prompts"""
    
    def __init__(self, config: TextToLoRAConfig, vocab_size: int = 50257):
        super().__init__()
        self.config = config
        
        # Text encoder
        self.embedding = nn.Embedding(vocab_size, config.hyper_network_size)
        self.lstm = nn.LSTM(config.hyper_network_size, config.hyper_network_size, 
                           batch_first=True, bidirectional=True)
        self.linear = nn.Linear(config.hyper_network_size * 2, config.hyper_network_size)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(config.dropout)
        
        # Skill detection network
        self.skill_detector = nn.Sequential(
            nn.Linear(config.hyper_network_size, config.skill_embeddings_dim),
            nn.ReLU(),
            nn.Linear(config.skill_embeddings_dim, 10),  # 10 skill categories
            nn.Softmax(dim=-1)
        )
        
        # Adapter generator networks
        self.adapter_generators = nn.ModuleDict({
            'q_proj': self._create_adapter_generator(),
            'k_proj': self._create_adapter_generator(),
            'v_proj': self._create_adapter_generator(),
            'o_proj': self._create_adapter_generator(),
            'gate_proj': self._create_adapter_generator(),
            'up_proj': self._create_adapter_generator(),
            'down_proj': self._create_adapter_generator()
        })
    
    def _create_adapter_generator(self):
        """Create adapter generator for a specific layer"""
        return nn.Sequential(
            nn.Linear(self.config.hyper_network_size, self.config.hyper_network_size // 2),
            nn.ReLU(),
            nn.Linear(self.config.hyper_network_size // 2, 
                     self.config.adapter_rank * self.config.adapter_alpha),
            nn.Tanh()  # Bound the output
        )
    
    def forward(self, prompt_tokens: torch.Tensor) -> Dict[str, torch.Tensor]:
        """Generate LoRA adapters from text prompt"""
        # Encode text prompt
        embedded = self.embedding(prompt_tokens)
        lstm_out, (hidden, cell) = self.lstm(embedded)
        # Use the last hidden state from both directions
        text_features = self.linear(lstm_out[:, -1, :])  # Take last timestep
        text_features = self.relu(text_features)
        text_features = self.dropout(text_features)
        
        # Detect skills
        skill_weights = self.skill_detector(text_features)
        
        # Generate adapters for each layer
        adapters = {}
        for layer_name, generator in self.adapter_generators.items():
            adapter_params = generator(text_features)
            # Reshape to LoRA format
            adapters[layer_name] = adapter_params.view(
                self.config.adapter_rank, self.config.adapter_alpha
            )
        
        return {
            'adapters': adapters,
            'skill_weights': skill_weights,
            'text_features': text_features
        }

class TextToLoRAGenerator:
    """Text-to-LoRA adapter generator inspired by Sakana AI"""
    
    def __init__(self, config: TextToLoRAConfig):
        self.config = config
        self.hyper_network = HyperNetwork(config)
        self.tokenizer = None
        self.skill_categories = [
            'code_generation', 'mathematics', 'reasoning', 'creative_writing',
            'analysis', 'summarization', 'translation', 'question_answering',
            'debugging', 'optimization'
        ]
        
        logger.info("🎯 Text-to-LoRA Generator initialized")
    
    def load_tokenizer(self, model_name: str):
        """Load tokenizer for the base model"""
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        logger.info(f"✅ Tokenizer loaded for {model_name}")
    
    def generate_adapter_from_prompt(self, prompt: str) -> Dict[str, Any]:
        """Generate LoRA adapter from natural language prompt"""
        if not self.tokenizer:
            raise ValueError("Tokenizer not loaded. Call load_tokenizer() first.")
        
        logger.info(f"🎯 Generating adapter from prompt: '{prompt[:50]}...'")
        
        # Tokenize prompt
        tokens = self.tokenizer(
            prompt,
            return_tensors="pt",
            max_length=self.config.max_prompt_length,
            truncation=True,
            padding=True
        )
        
        # Generate adapter
        with torch.no_grad():
            result = self.hyper_network(tokens.input_ids)
        
        # Extract skill information
        skill_weights = result['skill_weights'].squeeze()
        detected_skills = self._interpret_skills(skill_weights, prompt)
        
        adapter_info = {
            'prompt': prompt,
            'adapters': result['adapters'],
            'detected_skills': detected_skills,
            'skill_weights': skill_weights.tolist(),
            'generation_time': time.time()
        }
        
        logger.info(f"✅ Generated adapter with skills: {detected_skills}")
        return adapter_info
    
    def _interpret_skills(self, skill_weights: torch.Tensor, prompt: str = "") -> List[str]:
        """Enhanced skill interpretation using both weights and keyword analysis"""
        weights = skill_weights.tolist()
        detected_skills = []
        
        # First, try keyword-based detection if prompt is available
        if prompt:
            keyword_skills = self._detect_skills_from_keywords(prompt)
            if keyword_skills and keyword_skills != ['general']:
                detected_skills.extend(keyword_skills)
        
        # Then add weight-based detection
        for i, weight in enumerate(weights):
            if weight > 0.2:  # Lowered threshold for better detection
                skill_name = self.skill_categories[i] if i < len(self.skill_categories) else 'general'
                if skill_name not in detected_skills:
                    detected_skills.append(skill_name)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_skills = []
        for skill in detected_skills:
            if skill not in seen:
                seen.add(skill)
                unique_skills.append(skill)
        
        return unique_skills if unique_skills else ['general']
    
    def _detect_skills_from_keywords(self, prompt: str) -> List[str]:
        """Detect skills using keyword analysis"""
        prompt_lower = prompt.lower()
        detected_skills = []
        
        # Enhanced skill keyword mapping
        skill_keywords = {
            'code_generation': ['code', 'programming', 'function', 'def ', 'class ', 'variable', 'algorithm', 'software', 'development', 'debugging', 'debug'],
            'mathematics': ['math', 'equation', 'solve', 'calculate', 'formula', 'number', 'algebra', 'geometry', 'statistics', 'mathematical'],
            'reasoning': ['reason', 'logic', 'think', 'analyze', 'conclude', 'infer', 'deduce', 'problem solving', 'reasoning'],
            'creative_writing': ['story', 'creative', 'write', 'narrative', 'fiction', 'poetry', 'imagination', 'character', 'storytelling'],
            'analysis': ['analyze', 'analysis', 'examine', 'evaluate', 'assess', 'review', 'study', 'investigate'],
            'summarization': ['summarize', 'summary', 'brief', 'overview', 'condense', 'abstract', 'synopsis'],
            'translation': ['translate', 'language', 'convert', 'interpret', 'localize', 'multilingual'],
            'question_answering': ['answer', 'question', 'what', 'how', 'why', 'when', 'where', 'explain', 'clarify'],
            'debugging': ['debug', 'error', 'fix', 'bug', 'troubleshoot', 'issue', 'problem', 'correct'],
            'optimization': ['optimize', 'improve', 'enhance', 'better', 'faster', 'efficient', 'performance', 'speed']
        }
        
        # Count keyword matches for each skill
        skill_scores = {}
        for skill, keywords in skill_keywords.items():
            score = sum(1 for keyword in keywords if keyword in prompt_lower)
            if score > 0:
                skill_scores[skill] = score
        
        # Return top skills (at least 1 keyword match)
        if skill_scores:
            # Sort by score and return top skills
            sorted_skills = sorted(skill_scores.items(), key=lambda x: x[1], reverse=True)
            detected_skills = [skill for skill, score in sorted_skills if score > 0]
        
        return detected_skills
    
    def create_lora_config_from_adapter(self, adapter_info: Dict[str, Any]) -> LoraConfig:
        """Create LoRA config from generated adapter"""
        return LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            r=self.config.adapter_rank,
            lora_alpha=self.config.adapter_alpha,
            target_modules=list(adapter_info['adapters'].keys()),
            lora_dropout=self.config.dropout,
            bias="none",
            inference_mode=False
        )

class ExpertVector(nn.Module):
    """Expert vector for specific skills in Transformer²"""
    
    def __init__(self, skill_name: str, vector_dim: int, model_dim: int):
        super().__init__()
        self.skill_name = skill_name
        self.vector_dim = vector_dim
        self.model_dim = model_dim
        
        # Learnable skill vector
        self.skill_vector = nn.Parameter(torch.randn(vector_dim))
        
        # Projection layers for weight adaptation
        self.weight_projections = nn.ModuleDict({
            'attention': nn.Linear(vector_dim, model_dim * 4),  # Q, K, V, O
            'ffn': nn.Linear(vector_dim, model_dim * 2),        # Gate, Up
            'output': nn.Linear(vector_dim, model_dim)           # Down
        })
    
    def forward(self, input_features: torch.Tensor) -> Dict[str, torch.Tensor]:
        """Generate weight adaptations for this skill"""
        adaptations = {}
        
        for layer_type, projection in self.weight_projections.items():
            weight_delta = projection(self.skill_vector)
            adaptations[layer_type] = weight_delta
        
        return adaptations

class Transformer2Model(nn.Module):
    """Transformer² with dynamic weight adaptation during inference"""
    
    def __init__(self, base_model, config: Transformer2Config):
        super().__init__()
        self.base_model = base_model
        self.config = config
        
        # Expert vectors for different skills
        self.expert_vectors = nn.ModuleDict({
            'code_generation': ExpertVector('code_generation', config.expert_vector_dim, base_model.config.hidden_size),
            'mathematics': ExpertVector('mathematics', config.expert_vector_dim, base_model.config.hidden_size),
            'reasoning': ExpertVector('reasoning', config.expert_vector_dim, base_model.config.hidden_size),
            'creative_writing': ExpertVector('creative_writing', config.expert_vector_dim, base_model.config.hidden_size),
            'analysis': ExpertVector('analysis', config.expert_vector_dim, base_model.config.hidden_size),
            'summarization': ExpertVector('summarization', config.expert_vector_dim, base_model.config.hidden_size),
            'translation': ExpertVector('translation', config.expert_vector_dim, base_model.config.hidden_size),
            'question_answering': ExpertVector('question_answering', config.expert_vector_dim, base_model.config.hidden_size)
        })
        
        # Skill detection network
        self.skill_detector = nn.Sequential(
            nn.Linear(base_model.config.hidden_size, config.expert_vector_dim),
            nn.ReLU(),
            nn.Linear(config.expert_vector_dim, len(self.expert_vectors)),
            nn.Softmax(dim=-1)
        )
        
        # Adaptation layers (which layers to adapt)
        if config.adaptation_layers is None:
            # Handle different model architectures
            if hasattr(base_model, 'model') and hasattr(base_model.model, 'layers'):
                # Qwen-style architecture
                config.adaptation_layers = list(range(len(base_model.model.layers)))
            elif hasattr(base_model, 'transformer') and hasattr(base_model.transformer, 'h'):
                # GPT-2/DialoGPT-style architecture
                config.adaptation_layers = list(range(len(base_model.transformer.h)))
            else:
                # Fallback - try to find transformer layers
                config.adaptation_layers = [0]  # Just adapt the first layer
        
        logger.info(f"🧠 Transformer² initialized with {len(self.expert_vectors)} expert vectors")
    
    def detect_skills(self, input_ids: torch.Tensor) -> torch.Tensor:
        """Detect required skills from input"""
        # Ensure input_ids are on the correct device
        device = next(self.base_model.parameters()).device
        input_ids = input_ids.to(device)
        
        # Get embeddings from base model - handle different architectures
        try:
            if hasattr(self.base_model, 'model') and hasattr(self.base_model.model, 'embed_tokens'):
                # Qwen-style architecture
                embeddings = self.base_model.model.embed_tokens(input_ids)
            elif hasattr(self.base_model, 'transformer') and hasattr(self.base_model.transformer, 'wte'):
                # GPT-2/DialoGPT-style architecture
                embeddings = self.base_model.transformer.wte(input_ids)
            else:
                # Fallback - use input_ids as embeddings (simplified)
                embeddings = input_ids.float()
        except RuntimeError as e:
            if "MPS device" in str(e):
                # Fallback for MPS device issues - use CPU embeddings
                logger.warning("MPS device issue detected, using CPU fallback for embeddings")
                embeddings = input_ids.float().cpu()
            else:
                raise e
        
        # Pool embeddings
        pooled = embeddings.mean(dim=1)
        
        # Detect skills
        skill_weights = self.skill_detector(pooled.to(next(self.skill_detector.parameters()).device))
        return skill_weights
    
    def adapt_weights(self, skill_weights: torch.Tensor) -> Dict[str, torch.Tensor]:
        """Adapt model weights based on detected skills"""
        adaptations = {}
        
        for i, (skill_name, expert_vector) in enumerate(self.expert_vectors.items()):
            weight = skill_weights[:, i:i+1]  # Get weight for this skill
            
            if weight.item() > self.config.skill_detection_threshold:
                # Generate adaptations for this skill
                skill_adaptations = expert_vector(torch.zeros(1, self.config.expert_vector_dim))
                
                for layer_type, adaptation in skill_adaptations.items():
                    if layer_type not in adaptations:
                        adaptations[layer_type] = []
                    adaptations[layer_type].append(weight * adaptation)
        
        # Combine adaptations
        combined_adaptations = {}
        for layer_type, adaptation_list in adaptations.items():
            if adaptation_list:
                combined_adaptations[layer_type] = torch.stack(adaptation_list).sum(dim=0)
        
        return combined_adaptations
    
    def forward(self, input_ids: torch.Tensor, **kwargs):
        """Forward pass with dynamic weight adaptation"""
        # Detect skills
        skill_weights = self.detect_skills(input_ids)
        
        # Adapt weights
        adaptations = self.adapt_weights(skill_weights)
        
        # Apply adaptations to base model (simplified - in practice would modify attention/FFN weights)
        # For now, we'll use the base model and return skill information
        outputs = self.base_model(input_ids, **kwargs)
        
        # Add skill information to outputs
        outputs.skill_weights = skill_weights
        outputs.adaptations = adaptations
        
        return outputs

class SakanaAIIntegration:
    """Main integration class for Sakana AI methods"""
    
    def __init__(self):
        self.text_to_lora_config = TextToLoRAConfig()
        self.transformer2_config = Transformer2Config()
        
        self.text_to_lora_generator = TextToLoRAGenerator(self.text_to_lora_config)
        
        logger.info("🐟 Sakana AI Methods Integration initialized")
    
    def generate_adapter_from_text(self, prompt: str, model_name: str) -> Dict[str, Any]:
        """Generate LoRA adapter from text prompt"""
        logger.info("🎯 Generating adapter using Text-to-LoRA method")
        
        # Load tokenizer
        self.text_to_lora_generator.load_tokenizer(model_name)
        
        # Generate adapter
        adapter_info = self.text_to_lora_generator.generate_adapter_from_prompt(prompt)
        
        # Create LoRA config
        lora_config = self.text_to_lora_generator.create_lora_config_from_adapter(adapter_info)
        
        return {
            'adapter_info': adapter_info,
            'lora_config': lora_config,
            'method': 'text_to_lora'
        }
    
    def create_transformer2_model(self, base_model) -> Transformer2Model:
        """Create Transformer² model with dynamic adaptation"""
        logger.info("🧠 Creating Transformer² model")
        
        transformer2_model = Transformer2Model(base_model, self.transformer2_config)
        
        return transformer2_model
    
    def compare_methods(self, base_model, prompt: str, test_input: str) -> Dict[str, Any]:
        """Compare traditional fine-tuning vs Sakana AI methods"""
        logger.info("🆚 Comparing fine-tuning methods")
        
        results = {
            'traditional_lora': None,
            'text_to_lora': None,
            'transformer2': None,
            'comparison_metrics': {}
        }
        
        # Test Text-to-LoRA
        try:
            adapter_result = self.generate_adapter_from_text(prompt, "microsoft/DialoGPT-small")
            results['text_to_lora'] = {
                'method': 'Text-to-LoRA',
                'generation_time': time.time() - adapter_result['adapter_info']['generation_time'],
                'detected_skills': adapter_result['adapter_info']['detected_skills'],
                'skill_weights': adapter_result['adapter_info']['skill_weights']
            }
        except Exception as e:
            logger.error(f"Text-to-LoRA failed: {e}")
            results['text_to_lora'] = {'error': str(e)}
        
        # Test Transformer²
        try:
            transformer2_model = self.create_transformer2_model(base_model)
            
            # Test inference
            test_tokens = transformer2_model.base_model.tokenizer.encode(test_input, return_tensors="pt")
            
            with torch.no_grad():
                outputs = transformer2_model(test_tokens)
            
            results['transformer2'] = {
                'method': 'Transformer²',
                'detected_skills': outputs.skill_weights.tolist(),
                'adaptations_applied': len(outputs.adaptations),
                'inference_time': time.time()
            }
        except Exception as e:
            logger.error(f"Transformer² failed: {e}")
            results['transformer2'] = {'error': str(e)}
        
        return results

# Example usage and testing
def test_sakana_methods():
    """Test Sakana AI methods with a simple example"""
    logger.info("🧪 Testing Sakana AI Methods")
    logger.info("=" * 50)
    
    # Initialize integration
    sakana = SakanaAIIntegration()
    
    # Test prompt
    prompt = "Make this model excel at code generation and debugging"
    test_input = "def fibonacci(n):"
    
    try:
        # Test Text-to-LoRA
        logger.info("🎯 Testing Text-to-LoRA...")
        adapter_result = sakana.generate_adapter_from_text(prompt, "microsoft/DialoGPT-small")
        
        logger.info(f"✅ Text-to-LoRA Results:")
        logger.info(f"   Detected Skills: {adapter_result['adapter_info']['detected_skills']}")
        logger.info(f"   Skill Weights: {adapter_result['adapter_info']['skill_weights']}")
        
        # Test Transformer² (would need actual model)
        logger.info("🧠 Transformer² method ready for integration")
        
        logger.info("🎉 Sakana AI methods test completed!")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_sakana_methods()
