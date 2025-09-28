#!/usr/bin/env python3
"""
Hybrid Model Fusion System
Implements HRM-inspired fusion of competing models for robust reasoning
"""

import asyncio
import logging
import random
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class FusionStrategy(Enum):
    """Different strategies for fusing model outputs."""
    WEIGHTED_AVERAGE = "weighted_average"
    CONSENSUS_VOTING = "consensus_voting"
    CONFIDENCE_BASED = "confidence_based"
    CHAOS_SELECTION = "chaos_selection"
    QUANTUM_SUPERPOSITION = "quantum_superposition"

@dataclass
class ModelOutput:
    """Container for model output with metadata."""
    content: str
    confidence: float
    model_name: str
    response_time: float
    tokens_used: int
    metadata: Dict[str, Any]

@dataclass
class FusionResult:
    """Result of model fusion process."""
    final_output: str
    fusion_strategy: FusionStrategy
    participating_models: List[str]
    confidence_score: float
    fusion_time: float
    individual_outputs: List[ModelOutput]
    metadata: Dict[str, Any]

class HybridModelFusion:
    """HRM-inspired hybrid model fusion system."""
    
    def __init__(self, ollama_adapter, config: Optional[Dict] = None):
        self.ollama_adapter = ollama_adapter
        self.config = config or self._default_config()
        self.model_weights = self.config.get("model_weights", {})
        self.fusion_strategies = self.config.get("fusion_strategies", [])
        self.chaos_factor = self.config.get("chaos_factor", 0.1)
        
    def _default_config(self) -> Dict:
        """Default configuration for hybrid fusion."""
        return {
            "model_weights": {
                "llama3.1:8b": 0.3,
                "qwen2.5:7b": 0.25,
                "mistral:7b": 0.2,
                "phi3:3.8b": 0.15,
                "llama3.2:3b": 0.1
            },
            "fusion_strategies": [
                FusionStrategy.WEIGHTED_AVERAGE,
                FusionStrategy.CONSENSUS_VOTING,
                FusionStrategy.CHAOS_SELECTION,
                FusionStrategy.QUANTUM_SUPERPOSITION
            ],
            "chaos_factor": 0.1,
            "min_confidence_threshold": 0.6,
            "max_models_per_fusion": 3
        }
    
    async def fuse_models(
        self, 
        prompt: str, 
        task_type: str = "general",
        strategy: Optional[FusionStrategy] = None
    ) -> FusionResult:
        """Fuse multiple models for robust output generation."""
        
        start_time = time.time()
        
        # Select models based on task type and strategy
        selected_models = await self._select_models_for_fusion(task_type, strategy)
        
        # Generate outputs from all selected models
        model_outputs = await self._generate_parallel_outputs(prompt, selected_models)
        
        # Apply fusion strategy
        if strategy is None:
            strategy = self._select_fusion_strategy(task_type, model_outputs)
        
        fused_result = await self._apply_fusion_strategy(strategy, model_outputs, prompt)
        
        fusion_time = time.time() - start_time
        
        return FusionResult(
            final_output=fused_result["output"],
            fusion_strategy=strategy,
            participating_models=selected_models,
            confidence_score=fused_result["confidence"],
            fusion_time=fusion_time,
            individual_outputs=model_outputs,
            metadata=fused_result.get("metadata", {})
        )
    
    async def _select_models_for_fusion(
        self, 
        task_type: str, 
        strategy: Optional[FusionStrategy]
    ) -> List[str]:
        """Select models for fusion based on task type and strategy."""
        
        available_models = list(self.model_weights.keys())
        
        # HRM-inspired model selection with chaos theory
        if strategy == FusionStrategy.CHAOS_SELECTION:
            # Introduce controlled randomness
            chaos_selection = random.random() < self.chaos_factor
            if chaos_selection:
                # Randomly select models for creative diversity
                num_models = random.randint(2, min(4, len(available_models)))
                return random.sample(available_models, num_models)
        
        # Task-based selection
        if task_type in ["creative_problem_solving", "reasoning_deep"]:
            # Prefer more capable models for complex tasks
            return ["llama3.1:8b", "qwen2.5:7b", "mistral:7b"]
        elif task_type in ["quick", "simple_reasoning"]:
            # Use faster models for simple tasks
            return ["phi3:3.8b", "llama3.2:3b"]
        else:
            # Balanced selection
            return available_models[:self.config["max_models_per_fusion"]]
    
    async def _generate_parallel_outputs(
        self, 
        prompt: str, 
        models: List[str]
    ) -> List[ModelOutput]:
        """Generate outputs from multiple models in parallel."""
        
        tasks = []
        for model in models:
            task = self._generate_single_output(prompt, model)
            tasks.append(task)
        
        outputs = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and create ModelOutput objects
        valid_outputs = []
        for i, output in enumerate(outputs):
            if isinstance(output, Exception):
                logger.warning(f"Model {models[i]} failed: {output}")
                continue
            
            valid_outputs.append(output)
        
        return valid_outputs
    
    async def _generate_single_output(self, prompt: str, model: str) -> ModelOutput:
        """Generate output from a single model."""
        
        start_time = time.time()
        
        try:
            # Use the existing Ollama adapter
            response = await self.ollama_adapter.generate_text(
                prompt=prompt,
                model_key=model,
                max_tokens=1000,
                temperature=0.7
            )
            
            response_time = time.time() - start_time
            
            # Calculate confidence based on response characteristics
            confidence = self._calculate_confidence(response, response_time)
            
            return ModelOutput(
                content=response.get("text", ""),
                confidence=confidence,
                model_name=model,
                response_time=response_time,
                tokens_used=response.get("tokens_used", 0),
                metadata=response.get("metadata", {})
            )
            
        except Exception as e:
            logger.error(f"Error generating output from {model}: {e}")
            raise
    
    def _calculate_confidence(self, response: Dict, response_time: float) -> float:
        """Calculate confidence score for model output."""
        
        # Base confidence from response quality indicators
        base_confidence = 0.7
        
        # Adjust based on response time (faster = more confident)
        time_factor = max(0.1, 1.0 - (response_time / 10.0))
        
        # Adjust based on response length (reasonable length = more confident)
        text_length = len(response.get("text", ""))
        length_factor = min(1.0, text_length / 500.0) if text_length > 0 else 0.1
        
        # Combine factors
        confidence = (base_confidence + time_factor + length_factor) / 3.0
        
        return min(1.0, max(0.0, confidence))
    
    def _select_fusion_strategy(
        self, 
        task_type: str, 
        model_outputs: List[ModelOutput]
    ) -> FusionStrategy:
        """Select appropriate fusion strategy based on context."""
        
        # HRM-inspired strategy selection
        if task_type in ["creative_problem_solving", "reasoning_deep"]:
            # Use quantum superposition for complex reasoning
            return FusionStrategy.QUANTUM_SUPERPOSITION
        elif len(model_outputs) >= 3:
            # Use consensus voting for multiple models
            return FusionStrategy.CONSENSUS_VOTING
        elif random.random() < self.chaos_factor:
            # Introduce chaos for creative diversity
            return FusionStrategy.CHAOS_SELECTION
        else:
            # Default to weighted average
            return FusionStrategy.WEIGHTED_AVERAGE
    
    async def _apply_fusion_strategy(
        self, 
        strategy: FusionStrategy, 
        model_outputs: List[ModelOutput],
        original_prompt: str
    ) -> Dict[str, Any]:
        """Apply the selected fusion strategy."""
        
        if strategy == FusionStrategy.WEIGHTED_AVERAGE:
            return await self._weighted_average_fusion(model_outputs)
        elif strategy == FusionStrategy.CONSENSUS_VOTING:
            return await self._consensus_voting_fusion(model_outputs)
        elif strategy == FusionStrategy.CONFIDENCE_BASED:
            return await self._confidence_based_fusion(model_outputs)
        elif strategy == FusionStrategy.CHAOS_SELECTION:
            return await self._chaos_selection_fusion(model_outputs)
        elif strategy == FusionStrategy.QUANTUM_SUPERPOSITION:
            return await self._quantum_superposition_fusion(model_outputs)
        else:
            # Fallback to weighted average
            return await self._weighted_average_fusion(model_outputs)
    
    async def _weighted_average_fusion(self, model_outputs: List[ModelOutput]) -> Dict[str, Any]:
        """Fuse outputs using weighted average based on model weights."""
        
        if not model_outputs:
            return {"output": "", "confidence": 0.0}
        
        # Calculate weighted scores for each output
        weighted_outputs = []
        total_weight = 0
        
        for output in model_outputs:
            weight = self.model_weights.get(output.model_name, 0.1)
            adjusted_weight = weight * output.confidence
            weighted_outputs.append((output.content, adjusted_weight))
            total_weight += adjusted_weight
        
        # Select output based on weighted probability
        if total_weight > 0:
            random_value = random.random() * total_weight
            current_weight = 0
            
            for content, weight in weighted_outputs:
                current_weight += weight
                if random_value <= current_weight:
                    return {
                        "output": content,
                        "confidence": sum(o.confidence for o in model_outputs) / len(model_outputs),
                        "metadata": {"strategy": "weighted_average", "total_weight": total_weight}
                    }
        
        # Fallback to highest confidence output
        best_output = max(model_outputs, key=lambda x: x.confidence)
        return {
            "output": best_output.content,
            "confidence": best_output.confidence,
            "metadata": {"strategy": "weighted_average_fallback"}
        }
    
    async def _consensus_voting_fusion(self, model_outputs: List[ModelOutput]) -> Dict[str, Any]:
        """Fuse outputs using consensus voting."""
        
        if not model_outputs:
            return {"output": "", "confidence": 0.0}
        
        # Group similar outputs
        output_groups = {}
        for output in model_outputs:
            # Simple similarity check (in practice, use more sophisticated methods)
            content_hash = hash(output.content[:100])  # Use first 100 chars for grouping
            if content_hash not in output_groups:
                output_groups[content_hash] = []
            output_groups[content_hash].append(output)
        
        # Find the group with highest total confidence
        best_group = max(output_groups.values(), key=lambda group: sum(o.confidence for o in group))
        
        # Select the highest confidence output from the best group
        best_output = max(best_group, key=lambda x: x.confidence)
        
        return {
            "output": best_output.content,
            "confidence": sum(o.confidence for o in best_group) / len(best_group),
            "metadata": {
                "strategy": "consensus_voting",
                "groups_found": len(output_groups),
                "group_size": len(best_group)
            }
        }
    
    async def _confidence_based_fusion(self, model_outputs: List[ModelOutput]) -> Dict[str, Any]:
        """Fuse outputs based on confidence scores."""
        
        if not model_outputs:
            return {"output": "", "confidence": 0.0}
        
        # Select output with highest confidence
        best_output = max(model_outputs, key=lambda x: x.confidence)
        
        return {
            "output": best_output.content,
            "confidence": best_output.confidence,
            "metadata": {"strategy": "confidence_based", "selected_model": best_output.model_name}
        }
    
    async def _chaos_selection_fusion(self, model_outputs: List[ModelOutput]) -> Dict[str, Any]:
        """HRM-inspired chaos selection fusion."""
        
        if not model_outputs:
            return {"output": "", "confidence": 0.0}
        
        # Introduce controlled randomness in selection
        chaos_factor = random.random()
        
        if chaos_factor < 0.3:
            # Random selection for creative diversity
            selected_output = random.choice(model_outputs)
            strategy_note = "random_chaos"
        elif chaos_factor < 0.6:
            # Reverse confidence selection (lowest confidence)
            selected_output = min(model_outputs, key=lambda x: x.confidence)
            strategy_note = "reverse_confidence_chaos"
        else:
            # Weighted random selection
            weights = [o.confidence for o in model_outputs]
            total_weight = sum(weights)
            if total_weight > 0:
                random_value = random.random() * total_weight
                current_weight = 0
                for i, weight in enumerate(weights):
                    current_weight += weight
                    if random_value <= current_weight:
                        selected_output = model_outputs[i]
                        break
                else:
                    selected_output = model_outputs[-1]
            else:
                selected_output = random.choice(model_outputs)
            strategy_note = "weighted_random_chaos"
        
        return {
            "output": selected_output.content,
            "confidence": selected_output.confidence * 0.8,  # Slightly reduce confidence for chaos
            "metadata": {
                "strategy": "chaos_selection",
                "chaos_factor": chaos_factor,
                "chaos_type": strategy_note
            }
        }
    
    async def _quantum_superposition_fusion(self, model_outputs: List[ModelOutput]) -> Dict[str, Any]:
        """HRM-inspired quantum superposition fusion."""
        
        if not model_outputs:
            return {"output": "", "confidence": 0.0}
        
        # Quantum-inspired superposition of outputs
        # Create a "superposition" by combining elements from different outputs
        
        # Extract key phrases from each output
        key_phrases = []
        for output in model_outputs:
            # Simple phrase extraction (in practice, use NLP techniques)
            phrases = output.content.split('.')[:3]  # First 3 sentences
            key_phrases.extend([(phrase.strip(), output.confidence) for phrase in phrases if phrase.strip()])
        
        # Create superposition by combining high-confidence phrases
        if key_phrases:
            # Sort by confidence and select top phrases
            key_phrases.sort(key=lambda x: x[1], reverse=True)
            top_phrases = key_phrases[:min(3, len(key_phrases))]
            
            # Combine phrases into coherent output
            combined_content = '. '.join([phrase[0] for phrase in top_phrases])
            if combined_content and not combined_content.endswith('.'):
                combined_content += '.'
            
            avg_confidence = sum(phrase[1] for phrase in top_phrases) / len(top_phrases)
            
            return {
                "output": combined_content,
                "confidence": avg_confidence,
                "metadata": {
                    "strategy": "quantum_superposition",
                    "phrases_combined": len(top_phrases),
                    "total_phrases": len(key_phrases)
                }
            }
        else:
            # Fallback to best output
            best_output = max(model_outputs, key=lambda x: x.confidence)
            return {
                "output": best_output.content,
                "confidence": best_output.confidence,
                "metadata": {"strategy": "quantum_superposition_fallback"}
            }

# Example usage and testing
async def test_hybrid_fusion():
    """Test the hybrid model fusion system."""
    
    # Mock Ollama adapter for testing
    class MockOllamaAdapter:
        async def generate_text(self, prompt, model_key, max_tokens, temperature):
            return {
                "text": f"Mock response from {model_key}: {prompt[:50]}...",
                "tokens_used": 100,
                "metadata": {"model": model_key}
            }
    
    # Create fusion system
    mock_adapter = MockOllamaAdapter()
    fusion_system = HybridModelFusion(mock_adapter)
    
    # Test different fusion strategies
    prompt = "Explain quantum computing in simple terms"
    
    strategies = [
        FusionStrategy.WEIGHTED_AVERAGE,
        FusionStrategy.CONSENSUS_VOTING,
        FusionStrategy.CHAOS_SELECTION,
        FusionStrategy.QUANTUM_SUPERPOSITION
    ]
    
    for strategy in strategies:
        print(f"\nTesting {strategy.value} fusion:")
        result = await fusion_system.fuse_models(prompt, "creative_problem_solving", strategy)
        print(f"Output: {result.final_output[:100]}...")
        print(f"Confidence: {result.confidence_score:.2f}")
        print(f"Models: {result.participating_models}")
        print(f"Strategy: {result.fusion_strategy.value}")

if __name__ == "__main__":
    asyncio.run(test_hybrid_fusion())
