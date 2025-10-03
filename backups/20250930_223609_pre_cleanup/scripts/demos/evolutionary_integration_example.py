#!/usr/bin/env python3
"""
Example: Integrate Evolutionary Optimizer with Existing System

Shows how to connect the new evolutionary prompt optimization
with your current orchestration and continuous improvement loop.
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

# Your existing system
from src.core.prompting.mipro_optimizer import MIPROPromptOptimizer
from src.core.orchestration.intelligent_orchestrator import IntelligentOrchestrator

# New evolutionary system
from src.core.prompting.evolutionary_optimizer import (
    EvolutionaryPromptOptimizer,
    Genome,
    ExecutionMetrics,
    PromptSpec,
    ThompsonBandit,
    improvement_daemon
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HybridPromptOptimizer:
    """
    Combines your existing MIPROv2 optimizer with new evolutionary approach
    
    Strategy:
    1. Use MIPROv2 for initial prompt engineering
    2. Use Evolutionary for hyperparameter tuning
    3. Use Bandit for online production routing
    """
    
    def __init__(self):
        # Your existing systems
        self.mipro = MIPROPromptOptimizer()
        self.orchestrator = IntelligentOrchestrator()
        
        # New evolutionary system
        self.evolutionary = EvolutionaryPromptOptimizer(
            population_size=12,
            survivors=6,
            eval_samples=64
        )
        
        # Production routing
        self.bandit: ThompsonBandit = None
        
    async def executor(self, spec: PromptSpec, genome: Genome) -> ExecutionMetrics:
        """
        Execute a prompt spec with genome config and measure performance
        
        This is the bridge between evolutionary optimizer and your system
        """
        import time
        
        start = time.time()
        
        try:
            # Execute using your orchestrator
            result = await self.orchestrator.execute_task(
                task={
                    "prompt": spec.prompt,
                    "model_key": genome.model_key,
                    "temperature": genome.temp,
                    "max_tokens": genome.max_tokens,
                    "use_cot": genome.cot,
                    "use_consensus": genome.use_consensus
                }
            )
            
            # Measure metrics
            latency_ms = (time.time() - start) * 1000
            
            # Validate output
            schema_ok = self._validate_schema(result, spec)
            safety_flags = self._check_safety(result)
            validator_score = self._calculate_quality(result)
            
            return ExecutionMetrics(
                schema_ok=schema_ok,
                safety_flags=safety_flags,
                validator_score=validator_score,
                latency_ms=latency_ms,
                tokens_total=result.get("tokens_used", 0),
                repairs=result.get("repairs_needed", 0),
                accuracy=result.get("accuracy", 1.0),
                cost_usd=self._calculate_cost(result)
            )
            
        except Exception as e:
            logger.error(f"Executor error: {e}")
            
            # Return failed metrics
            return ExecutionMetrics(
                schema_ok=False,
                safety_flags=["execution_error"],
                validator_score=0.0,
                latency_ms=(time.time() - start) * 1000,
                tokens_total=0,
                repairs=1,
                accuracy=0.0,
                cost_usd=0.0
            )
    
    def _validate_schema(self, result: Dict, spec: PromptSpec) -> bool:
        """Check if result matches expected schema"""
        try:
            # Add your validation logic
            if not result:
                return False
            
            # Check required fields based on spec
            required_fields = spec.metadata.get("required_fields", [])
            return all(field in result for field in required_fields)
            
        except Exception:
            return False
    
    def _check_safety(self, result: Dict) -> List[str]:
        """Check for safety issues"""
        flags = []
        
        content = result.get("content", "")
        
        # Basic safety checks (expand with your safety system)
        if any(word in content.lower() for word in ["error", "exception", "failed"]):
            flags.append("error_in_output")
        
        if len(content) < 10:
            flags.append("output_too_short")
        
        return flags
    
    def _calculate_quality(self, result: Dict) -> float:
        """Calculate output quality score"""
        # Use your existing quality metrics
        quality_metrics = result.get("quality_metrics", {})
        
        score = quality_metrics.get("overall_score", 0.5)
        
        # Adjust based on confidence
        confidence = result.get("confidence", 1.0)
        score *= confidence
        
        return min(1.0, max(0.0, score))
    
    def _calculate_cost(self, result: Dict) -> float:
        """Calculate execution cost in USD"""
        tokens = result.get("tokens_used", 0)
        
        # Rough cost estimate (adjust to your pricing)
        # Assuming $0.01 per 1K tokens
        cost_per_1k = 0.01
        return (tokens / 1000) * cost_per_1k
    
    async def optimize_prompt_comprehensive(
        self,
        base_prompt: str,
        golden_dataset: List[Dict[str, Any]],
        num_generations: int = 10
    ) -> Genome:
        """
        Full optimization pipeline:
        1. MIPROv2 optimizes the prompt text
        2. Evolutionary optimizes hyperparameters
        3. Returns best genome for production
        """
        
        logger.info("🚀 Starting comprehensive prompt optimization")
        
        # Phase 1: Use MIPROv2 to optimize prompt text
        logger.info("📝 Phase 1: MIPROv2 prompt optimization")
        
        # Convert to MIPROv2 format
        mipro_dataset = self._convert_to_mipro_format(golden_dataset)
        
        # This uses your existing system
        mipro_result = await self.mipro.optimize_prompt(
            prompt=base_prompt,
            dataset=mipro_dataset
        )
        
        optimized_prompt_text = mipro_result.get("optimized_prompt", base_prompt)
        logger.info(f"✅ MIPROv2 complete. Improved prompt.")
        
        # Phase 2: Use Evolution to optimize hyperparameters
        logger.info("🧬 Phase 2: Evolutionary hyperparameter optimization")
        
        # Create base genome with MIPROv2-optimized prompt
        base_genome = Genome(
            rubric=optimized_prompt_text,
            cot=True,
            temp=0.7,
            max_tokens=2048,
            retriever_topk=5,
            use_consensus=False,
            model_key="primary"
        )
        
        # Run evolutionary optimization
        best_genome = await self.evolutionary.optimize(
            trainset=golden_dataset,
            executor=self.executor,
            num_generations=num_generations,
            base_config=base_genome,
            early_stop_threshold=0.95
        )
        
        logger.info(f"✅ Evolution complete. Best score: {self.evolutionary.best_genomes[-1][0]:.4f}")
        
        # Save results
        results_path = Path(f"results/optimization_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        results_path.parent.mkdir(exist_ok=True)
        self.evolutionary.save_results(results_path)
        
        return best_genome
    
    def _convert_to_mipro_format(self, golden_dataset: List[Dict]) -> List[Dict]:
        """Convert golden dataset to MIPROv2 format"""
        # Adapt to your MIPROv2 format
        return [
            {
                "input": ex.get("query", ""),
                "output": ex.get("expected_output", ""),
                "context": ex.get("context", "")
            }
            for ex in golden_dataset
        ]
    
    def deploy_to_production(self, top_genomes: List[Genome]):
        """
        Deploy optimized genomes to production with bandit routing
        
        Args:
            top_genomes: Top N genomes from evolution (e.g., top 5)
        """
        logger.info(f"🚀 Deploying {len(top_genomes)} genomes to production")
        
        # Initialize bandit with top candidates
        self.bandit = ThompsonBandit(top_genomes)
        
        logger.info("✅ Production deployment complete. Bandit routing active.")
    
    async def production_route(self, user_query: str, context: str = "") -> Dict[str, Any]:
        """
        Production routing with bandit learning
        
        This is what you'd call from your API
        """
        if self.bandit is None:
            raise ValueError("Bandit not initialized. Call deploy_to_production() first.")
        
        # Bandit chooses genome via Thompson sampling
        genome = self.bandit.choose()
        
        logger.info(f"🎯 Bandit chose genome: {genome.genome_id} (gen {genome.generation})")
        
        # Create spec (simplified - you'd use NL2Prompt here)
        spec = PromptSpec(
            intent="user_query",
            prompt=f"{genome.rubric}\n\nQuery: {user_query}",
            tools=[],
            constraints={"max_tokens": genome.max_tokens},
            metadata={"genome_id": genome.genome_id}
        )
        
        # Execute
        metrics = await self.executor(spec, genome)
        
        # Calculate reward (0 to 1)
        reward = self._calculate_reward(metrics)
        
        # Update bandit
        self.bandit.update(genome.genome_id, reward)
        
        # Return result
        return {
            "response": "...",  # Your actual response
            "genome_id": genome.genome_id,
            "metrics": metrics.dict(),
            "reward": reward
        }
    
    def _calculate_reward(self, metrics: ExecutionMetrics) -> float:
        """Calculate reward for bandit (0 to 1)"""
        if not metrics.schema_ok or metrics.safety_flags:
            return 0.0
        
        # Composite reward
        reward = metrics.validator_score * 0.5  # Quality
        reward += (1.0 - min(1.0, metrics.latency_ms / 2000)) * 0.3  # Speed (< 2s is good)
        reward += (1.0 - min(1.0, metrics.cost_usd / 0.05)) * 0.2  # Cost (< $0.05 is good)
        
        return max(0.0, min(1.0, reward))


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

async def example_full_pipeline():
    """
    Example: Complete optimization pipeline
    From base prompt → optimized genome → production deployment
    """
    
    optimizer = HybridPromptOptimizer()
    
    # 1. Load golden dataset
    golden_dataset = [
        {
            "query": "Write a Python function to sort a list",
            "expected_output": "def sort_list(lst): return sorted(lst)",
            "context": "coding task",
        },
        {
            "query": "Explain quantum computing in simple terms",
            "expected_output": "Quantum computing uses quantum mechanics...",
            "context": "explanation task",
        },
        # ... more examples
    ] * 20  # 40 examples
    
    # 2. Optimize comprehensively
    logger.info("🚀 Starting full optimization pipeline")
    
    best_genome = await optimizer.optimize_prompt_comprehensive(
        base_prompt="You are a helpful AI assistant. Be clear and concise.",
        golden_dataset=golden_dataset,
        num_generations=5
    )
    
    logger.info(f"\n✅ Optimization complete!")
    logger.info(f"📊 Best genome: {best_genome.genome_id}")
    logger.info(f"   Temperature: {best_genome.temp}")
    logger.info(f"   Max tokens: {best_genome.max_tokens}")
    logger.info(f"   Model: {best_genome.model_key}")
    logger.info(f"   Generation: {best_genome.generation}")
    
    # 3. Get top 5 genomes for production
    top_5 = [
        genome for _, genome in 
        sorted(optimizer.evolutionary.best_genomes, reverse=True)[:5]
    ]
    
    # 4. Deploy to production
    optimizer.deploy_to_production(top_5)
    
    # 5. Simulate production requests
    logger.info("\n🔄 Simulating production requests...")
    
    for i in range(10):
        result = await optimizer.production_route(
            user_query=f"Test query {i}",
            context="test context"
        )
        logger.info(f"   Request {i+1}: genome={result['genome_id'][:8]}... reward={result['reward']:.3f}")
    
    # 6. Check bandit stats
    logger.info("\n📊 Bandit Statistics:")
    stats = optimizer.bandit.get_stats()
    for genome_id, stat in list(stats.items())[:3]:  # Top 3
        logger.info(f"   {genome_id[:12]}... pulls={stat['pulls']}, mean_reward={stat['mean_reward']:.3f}")


async def example_nightly_daemon():
    """
    Example: Automated nightly improvement
    Run this in CI/cron every night
    """
    
    optimizer = HybridPromptOptimizer()
    
    await improvement_daemon(
        trainset_path=Path("data/golden_dataset.json"),
        output_dir=Path("results/evolution"),
        executor=optimizer.executor,
        num_generations=10
    )
    
    logger.info("🌙 Nightly optimization complete")


if __name__ == "__main__":
    # Run full pipeline
    asyncio.run(example_full_pipeline())
    
    # Or run nightly daemon
    # asyncio.run(example_nightly_daemon())

