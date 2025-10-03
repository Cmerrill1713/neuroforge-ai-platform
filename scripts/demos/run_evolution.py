#!/usr/bin/env python3
"""
Run Evolutionary Prompt Optimization
Complete end-to-end evolution with RAG integration
"""

import asyncio
import json
import logging
from pathlib import Path
import sys
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


async def main():
    print("="*80)
    print("EVOLUTIONARY PROMPT OPTIMIZATION")
    print("Full Evolution with RAG Integration + Dual Backend")
    print("="*80)
    print()
    
    # Load golden dataset
    print("📚 Loading golden dataset...")
    dataset_path = Path("data/golden_dataset.json")
    with open(dataset_path) as f:
        data = json.load(f)
    
    golden_examples = data if isinstance(data, list) else data.get("examples", [])
    print(f"✅ Loaded {len(golden_examples)} examples")
    print()
    
    # Initialize integration
    print("🔧 Initializing integration...")
    try:
        from src.core.prompting.dual_backend_integration import DualBackendEvolutionaryIntegration
    except ImportError:
        print("⚠️  DualBackendEvolutionaryIntegration not found, using mock implementation")
        class DualBackendEvolutionaryIntegration:
            def __init__(self, *args, **kwargs):
                pass
            async def initialize(self):
                pass
            async def run_evolution(self, *args, **kwargs):
                return {"status": "mock", "generations": 1, "best_score": 0.8}
    
    integration = DualBackendEvolutionaryIntegration()
    await integration.initialize()
    
    print(f"✅ Integration initialized")
    print(f"   RAG Service: {'✅' if integration.rag_service else '❌'}")
    print(f"   Ollama Adapter: {'✅' if integration.ollama_adapter else '❌'}")
    print(f"   Orchestrator: {'✅' if integration.orchestrator else '❌'}")
    print()
    
    # Run evolution
    print("🧬 Starting evolutionary optimization...")
    print(f"   Generations: 3 (quick run)")
    print(f"   Population: 12 genomes")
    print(f"   Examples: {len(golden_examples)}")
    print(f"   MIPROv2: Disabled (for speed)")
    print()
    print("⏳ This will take 5-10 minutes...")
    print()
    
    try:
        best_genome = await integration.optimize_comprehensive(
            base_prompt="You are a helpful AI assistant. Be clear, specific, and actionable.",
            golden_dataset=golden_examples,
            num_generations=3,  # Quick run
            use_mipro=False  # Skip MIPROv2 for speed
        )
        
        print()
        print("="*80)
        print("✅ EVOLUTION COMPLETE!")
        print("="*80)
        print()
        print(f"🏆 Best Genome:")
        print(f"   ID: {best_genome.genome_id}")
        print(f"   Temperature: {best_genome.temp}")
        print(f"   Max Tokens: {best_genome.max_tokens}")
        print(f"   Model: {best_genome.model_key}")
        print(f"   Generation: {best_genome.generation}")
        print(f"   Uses CoT: {best_genome.cot}")
        print(f"   Uses Consensus: {best_genome.use_consensus}")
        print()
        
        # Get fitness history
        if integration.evolutionary.fitness_history:
            print("📊 Fitness Progress:")
            for gen in integration.evolutionary.fitness_history:
                print(f"   Gen {gen['generation']}: Best={gen['best_score']:.4f}, Mean={gen['mean_score']:.4f}")
            
            # Calculate improvement
            first_gen = integration.evolutionary.fitness_history[0]
            last_gen = integration.evolutionary.fitness_history[-1]
            improvement = ((last_gen['best_score'] - first_gen['best_score']) / first_gen['best_score']) * 100
            
            print()
            print(f"📈 Improvement: +{improvement:.1f}%")
        
        print()
        print("💾 Results saved to:")
        results_files = list(Path("results").glob("dual_backend_optimization_*.json"))
        for f in sorted(results_files, reverse=True)[:1]:
            print(f"   {f}")
        
        print()
        print("🎯 Ready for Production Deployment!")
        print()
        print("Next steps:")
        print("   1. Review results in results/ directory")
        print("   2. Deploy with bandit: integration.deploy_to_production([best_genome])")
        print("   3. Monitor metrics in Grafana")
        print()
        
    except Exception as e:
        print()
        print(f"❌ Evolution failed: {e}")
        import traceback
        traceback.print_exc()
        print()
        print("💡 This is likely due to missing dependencies or backend issues.")
        print("   Check logs above for specific errors.")


if __name__ == "__main__":
    asyncio.run(main())

