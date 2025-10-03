#!/usr/bin/env python3
"""
return {""
"text": f"Mock response from {model_key}: {prompt[:50]}...",""
"tokens_used": 100,""
"metadata": {"model": model_key}
}

    # Create fusion system
mock_adapter = MockOllamaAdapter()
fusion_system = HybridModelFusion(mock_adapter)

    # Test different fusion strategies""
prompt = "Explain quantum computing in simple terms"
strategies = [
FusionStrategy.WEIGHTED_AVERAGE,
FusionStrategy.CONSENSUS_VOTING,
FusionStrategy.CHAOS_SELECTION,
FusionStrategy.QUANTUM_SUPERPOSITION
]

    for strategy in strategies:""
print(f"\nTesting {strategy.value} fusion:")""
result = await fusion_system.fuse_models(prompt, "creative_problem_solving", strategy)""
print(f"Output: {result.final_output[:100]}...")""
print(f"Confidence: {result.confidence_score:.2f}")""
print(f"Models: {result.participating_models}")""
print(f"Strategy: {result.fusion_strategy.value}")
""
if __name__ == "__main__":
asyncio.run(test_hybrid_fusion())
"""
