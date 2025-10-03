#!/usr/bin/env python3
"""
Evolutionary Prompt Optimization System
Combines genetic algorithms, multi-objective optimization, and bandit learning
Based on production-grade approaches from Anthropic/OpenAI
"""

import dspy
import random
import logging
from dataclasses import dataclass, replace, field
from typing import List, Dict, Any, Optional, Callable
from pydantic import BaseModel, Field
from datetime import datetime
import json
import numpy as np
from pathlib import Path

logger = logging.getLogger(__name__)

# Configure DSPy with Ollama LLM
try:
    # Use DSPy LM with Ollama endpoint - disable structured output completely
    lm = dspy.LM(
        model="ollama/qwen2.5:7b",  # Use a model that actually exists
        api_base="http://localhost:11434/v1",
        api_key="ollama",
        max_tokens=1000
    )
    # Disable structured outputs globally
    dspy.settings.configure(lm=lm, structured_outputs=False)
    logger.info("✅ DSPy configured with Ollama LLM (ollama/qwen2.5:7b) - structured outputs disabled")
except Exception as e:
    logger.warning(f"⚠️ Could not configure DSPy LLM: {e}")
    logger.warning("Evolution will use fallback mode")

# ============================================================================
# 1. STRICT OUTPUT SCHEMA
# ============================================================================

class PromptSpec(BaseModel):
    """Validated output schema for prompt engineering"""
    intent: str = Field(..., description="User intent label")
    prompt: str = Field(..., description="Final engineered prompt")
    tools: List[str] = Field(default_factory=list, description="Required tools")
    constraints: Dict[str, Any] = Field(default_factory=dict, description="Execution constraints")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Optimization metadata")


class NL2Prompt(dspy.Module):
    """Natural language to structured prompt with schema validation"""
    
    def __init__(self, schema=PromptSpec):
        super().__init__()
        # Create signature string (DSPy 2.x syntax) - simple text output
        self.predict = dspy.Predict(
            "user_query, context, rubric -> prompt_text",
            instructions="Generate a helpful prompt for the user query. Be concise and actionable."
        )
        self.schema = schema
    
    def forward(self, user_query: str, context: str, rubric: str) -> PromptSpec:
        """Generate and validate prompt spec"""
        try:
            # Get simple text response
            response = self.predict(user_query=user_query, context=context, rubric=rubric).prompt_text
            
            # Create a simple PromptSpec from the response
            spec = PromptSpec(
                intent="assist",
                prompt=response,
                tools=[],
                constraints={"max_tokens": 1000},
                metadata={"generated_by": "nl2prompt"}
            )
            return spec
        except Exception as e:
            logger.warning(f"NL2Prompt failed, using fallback: {e}")
            # Fallback to simple prompt
            return PromptSpec(
                intent="assist",
                prompt=f"You are a helpful AI assistant. Answer this query: {user_query}",
                tools=[],
                constraints={"max_tokens": 1000},
                metadata={"fallback": True}
            )


# ============================================================================
# 2. GENOME & EVOLUTION
# ============================================================================

@dataclass(frozen=True)
class Genome:
    """Prompt optimization 'genome' - all tunable parameters"""
    rubric: str
    cot: bool = True
    temp: float = 0.7
    max_tokens: int = 2048
    retriever_topk: int = 5
    use_consensus: bool = False
    model_key: str = "primary"
    generation: int = 0
    parent_id: Optional[str] = None
    genome_id: str = field(default_factory=lambda: f"genome_{datetime.now().timestamp()}")


def mutate(g: Genome) -> Genome:
    """Mutate a genome - single random change"""
    ops = [
        lambda x: replace(x, cot=not x.cot),
        lambda x: replace(x, temp=max(0.0, min(1.0, x.temp + random.choice([-0.2, -0.1, 0.1, 0.2])))),
        lambda x: replace(x, max_tokens=max(256, min(8192, x.max_tokens + random.choice([-512, -256, 256, 512])))),
        lambda x: replace(x, retriever_topk=max(2, min(20, x.retriever_topk + random.choice([-2, -1, 1, 2])))),
        lambda x: replace(x, use_consensus=not x.use_consensus),
        lambda x: replace(x, model_key=random.choice(["primary", "coding", "lightweight", "reasoning"])),
        # Note: rubric mutation would call LLM to rewrite
    ]
    
    mutated = random.choice(ops)(g)
    return replace(
        mutated, 
        generation=g.generation + 1,
        parent_id=g.genome_id,
        genome_id=f"genome_{datetime.now().timestamp()}_{random.randint(0, 9999)}"
    )


def crossover(g1: Genome, g2: Genome) -> Genome:
    """Crossover between two genomes"""
    return Genome(
        rubric=random.choice([g1.rubric, g2.rubric]),
        cot=random.choice([g1.cot, g2.cot]),
        temp=(g1.temp + g2.temp) / 2 + random.uniform(-0.1, 0.1),
        max_tokens=random.choice([g1.max_tokens, g2.max_tokens]),
        retriever_topk=random.choice([g1.retriever_topk, g2.retriever_topk]),
        use_consensus=random.choice([g1.use_consensus, g2.use_consensus]),
        model_key=random.choice([g1.model_key, g2.model_key]),
        generation=max(g1.generation, g2.generation) + 1,
        parent_id=f"{g1.genome_id}+{g2.genome_id}",
    )


# ============================================================================
# 3. MULTI-OBJECTIVE EVALUATION
# ============================================================================

class ExecutionMetrics(BaseModel):
    """Metrics from prompt execution"""
    schema_ok: bool = True
    safety_flags: List[str] = Field(default_factory=list)
    validator_score: float = 1.0
    latency_ms: float = 0.0
    tokens_total: int = 0
    repairs: int = 0
    accuracy: float = 1.0
    cost_usd: float = 0.0


def composite_evaluate(
    example: Dict[str, Any], 
    spec: PromptSpec, 
    meta: ExecutionMetrics,
    weights: Dict[str, float] = None
) -> float:
    """
    Multi-objective evaluation: success - α·latency - β·cost - γ·repairs
    """
    if weights is None:
        weights = {
            "latency": 0.001,      # 1ms = -0.001 points
            "tokens": 0.0005,      # 1 token = -0.0005 points  
            "repairs": 0.2,        # 1 repair = -0.2 points
            "cost": 1.0,           # $1 = -1 point
        }
    
    # Base success check
    ok = all([
        meta.schema_ok,
        not meta.safety_flags,
        meta.validator_score >= 0.9,
        meta.accuracy >= 0.85
    ])
    score = 1.0 if ok else 0.0
    
    # Penalties
    score -= weights["latency"] * meta.latency_ms
    score -= weights["tokens"] * meta.tokens_total
    score -= weights["repairs"] * meta.repairs
    score -= weights["cost"] * meta.cost_usd
    
    return max(0.0, score)  # Never go negative


# ============================================================================
# 4. EVOLUTIONARY OPTIMIZER
# ============================================================================

class EvolutionaryPromptOptimizer:
    """Genetic algorithm for prompt optimization"""
    
    def __init__(
        self,
        population_size: int = 12,
        survivors: int = 6,
        eval_samples: int = 64,
        evaluator: Callable = composite_evaluate
    ):
        self.population_size = population_size
        self.survivors = survivors
        self.eval_samples = eval_samples
        self.evaluator = evaluator
        self.nl2prompt = NL2Prompt()
        self.generation = 0
        
        # Track history
        self.best_genomes: List[tuple[float, Genome]] = []
        self.fitness_history: List[Dict[str, Any]] = []
    
    def seed_population(self, base_config: Optional[Genome] = None) -> List[Genome]:
        """Create initial population with diversity"""
        if base_config is None:
            base_config = Genome(
                rubric="Be clear, specific, and actionable. Provide structured outputs.",
                cot=True,
                temp=0.7,
                max_tokens=2048,
                retriever_topk=5
            )
        
        population = [base_config]
        
        # Generate diverse initial population
        for _ in range(self.population_size - 1):
            mutated = base_config
            for _ in range(random.randint(1, 3)):  # Multiple mutations for diversity
                mutated = mutate(mutated)
            population.append(mutated)
        
        return population
    
    async def evaluate_genome(
        self, 
        genome: Genome, 
        trainset: List[Dict[str, Any]],
        executor: Callable
    ) -> float:
        """Evaluate a genome on training examples"""
        scores = []
        
        # Sample from trainset
        sample_size = min(self.eval_samples, len(trainset))
        samples = random.sample(trainset, k=sample_size)
        
        for example in samples:
            try:
                # Generate spec
                spec = self.nl2prompt.forward(
                    user_query=example["query"],
                    context=example.get("context", ""),
                    rubric=genome.rubric
                )
                
                # Execute and measure
                meta = await executor(spec, genome)
                
                # Evaluate
                score = self.evaluator(example, spec, meta)
                scores.append(score)
                
            except Exception as e:
                logger.error(f"Evaluation error: {e}")
                scores.append(0.0)
        
        avg_score = sum(scores) / len(scores) if scores else 0.0
        return avg_score
    
    async def evolve_generation(
        self,
        population: List[Genome],
        trainset: List[Dict[str, Any]],
        executor: Callable
    ) -> tuple[List[Genome], float, Genome]:
        """Run one generation of evolution"""
        
        logger.info(f"🧬 Generation {self.generation}: Evaluating {len(population)} genomes")
        
        # Evaluate all genomes
        fitness = []
        for genome in population:
            score = await self.evaluate_genome(genome, trainset, executor)
            fitness.append((score, genome))
        
        # Sort by fitness (descending)
        fitness.sort(reverse=True, key=lambda x: x[0])
        
        # Track best
        best_score, best_genome = fitness[0]
        self.best_genomes.append((best_score, best_genome))
        
        # Log generation stats
        scores = [s for s, _ in fitness]
        self.fitness_history.append({
            "generation": self.generation,
            "best_score": best_score,
            "mean_score": np.mean(scores),
            "std_score": np.std(scores),
            "best_genome_id": best_genome.genome_id,
            "timestamp": datetime.now().isoformat()
        })
        
        logger.info(f"✅ Gen {self.generation}: Best={best_score:.4f}, Mean={np.mean(scores):.4f}")
        
        # Selection: Keep top survivors
        survivors_list = [g for _, g in fitness[:self.survivors]]
        
        # Reproduction: Create offspring
        children = []
        while len(children) < self.population_size - len(survivors_list):
            if random.random() < 0.3:  # 30% crossover
                p1, p2 = random.sample(survivors_list, 2)
                child = crossover(p1, p2)
            else:  # 70% mutation
                parent = random.choice(survivors_list)
                child = mutate(parent)
            children.append(child)
        
        # New population
        new_population = survivors_list + children
        self.generation += 1
        
        return new_population, best_score, best_genome
    
    async def optimize(
        self,
        trainset: List[Dict[str, Any]],
        executor: Callable,
        num_generations: int = 10,
        base_config: Optional[Genome] = None,
        early_stop_threshold: float = 0.95
    ) -> Genome:
        """Run full evolutionary optimization"""
        
        logger.info(f"🚀 Starting evolutionary optimization: {num_generations} generations")
        
        # Initialize population
        population = self.seed_population(base_config)
        
        best_overall = None
        best_score = 0.0
        
        for gen in range(num_generations):
            population, gen_best_score, gen_best_genome = await self.evolve_generation(
                population, trainset, executor
            )
            
            # Track overall best
            if gen_best_score > best_score:
                best_score = gen_best_score
                best_overall = gen_best_genome
                logger.info(f"🎉 New best genome! Score: {best_score:.4f}")
            
            # Early stopping
            if best_score >= early_stop_threshold:
                logger.info(f"🎯 Early stop: threshold {early_stop_threshold} reached")
                break
        
        logger.info(f"✅ Optimization complete. Best score: {best_score:.4f}")
        
        return best_overall
    
    def save_results(self, output_path: Path):
        """Save optimization results"""
        results = {
            "generations": self.generation,
            "best_genomes": [
                {
                    "score": score,
                    "genome": {
                        "genome_id": g.genome_id,
                        "rubric": g.rubric,
                        "cot": g.cot,
                        "temp": g.temp,
                        "max_tokens": g.max_tokens,
                        "retriever_topk": g.retriever_topk,
                        "use_consensus": g.use_consensus,
                        "model_key": g.model_key,
                        "generation": g.generation,
                        "parent_id": g.parent_id
                    }
                }
                for score, g in self.best_genomes[-10:]  # Last 10 best
            ],
            "fitness_history": self.fitness_history,
            "timestamp": datetime.now().isoformat()
        }
        
        output_path.write_text(json.dumps(results, indent=2))
        logger.info(f"💾 Results saved to {output_path}")


# ============================================================================
# 5. BANDIT FOR ONLINE ROUTING
# ============================================================================

class ThompsonBandit:
    """Thompson sampling bandit for online prompt routing"""
    
    def __init__(self, genomes: List[Genome]):
        self.genomes = {g.genome_id: g for g in genomes}
        
        # Beta distribution params (successes, failures)
        self.alpha = {g_id: 1.0 for g_id in self.genomes}
        self.beta = {g_id: 1.0 for g_id in self.genomes}
        
        self.pulls = {g_id: 0 for g_id in self.genomes}
        self.rewards = {g_id: [] for g_id in self.genomes}
    
    def choose(self) -> Genome:
        """Choose genome via Thompson sampling"""
        samples = {
            g_id: np.random.beta(self.alpha[g_id], self.beta[g_id])
            for g_id in self.genomes
        }
        
        best_id = max(samples, key=samples.get)
        self.pulls[best_id] += 1
        
        return self.genomes[best_id]
    
    def update(self, genome_id: str, reward: float):
        """Update bandit with reward [0, 1]"""
        self.rewards[genome_id].append(reward)
        
        # Update Beta params
        self.alpha[genome_id] += reward
        self.beta[genome_id] += (1.0 - reward)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get bandit statistics"""
        return {
            g_id: {
                "pulls": self.pulls[g_id],
                "mean_reward": np.mean(self.rewards[g_id]) if self.rewards[g_id] else 0.0,
                "alpha": self.alpha[g_id],
                "beta": self.beta[g_id],
                "expected_value": self.alpha[g_id] / (self.alpha[g_id] + self.beta[g_id])
            }
            for g_id in self.genomes
        }


# ============================================================================
# 6. PRODUCTION ROUTER (with Bandit)
# ============================================================================

class ProductionRouter:
    """
    Production router that uses Thompson Bandit for intelligent prompt routing
    """

    def __init__(self, bandit: ThompsonBandit):
        self.bandit = bandit
        self.request_count = 0
        self.genome_usage = {}

    async def route_request(self, user_query: str, context: str = "") -> Dict[str, Any]:
        """
        Route a production request using bandit selection
        """
        self.request_count += 1

        # Select genome using Thompson sampling
        genome = self.bandit.choose()
        genome_id = genome.genome_id

        # Track usage
        if genome_id not in self.genome_usage:
            self.genome_usage[genome_id] = 0
        self.genome_usage[genome_id] += 1

        logger.info(f"🎯 Request {self.request_count}: Routed to genome {genome_id[:8]}... (gen {genome.generation})")

        # Simulate execution (replace with your actual execution logic)
        # This would call your orchestrator or API
        result = await self._execute_with_genome(genome, user_query, context)

        # Calculate reward (0-1 scale)
        reward = self._calculate_reward(result)

        # Update bandit
        self.bandit.update(genome_id, reward)

        return {
            "genome_id": genome_id,
            "generation": genome.generation,
            "result": result,
            "reward": reward,
            "bandit_stats": self.bandit.get_stats()
        }

    async def _execute_with_genome(self, genome: Genome, query: str, context: str) -> Dict[str, Any]:
        """
        Execute request with selected genome (placeholder - integrate with your system)
        """
        # Placeholder - replace with your actual execution logic
        import time
        time.sleep(0.1)  # Simulate processing

        return {
            "response": f"Processed '{query}' with genome {genome.genome_id[:8]}...",
            "confidence": 0.85,
            "tokens_used": 150,
            "latency_ms": 120
        }

    def _calculate_reward(self, result: Dict[str, Any]) -> float:
        """
        Calculate reward for bandit learning (0-1 scale)
        """
        # Simple reward function - customize based on your metrics
        confidence = result.get("confidence", 0.5)
        latency_ms = result.get("latency_ms", 1000)

        # Reward = 40% confidence + 30% speed + 30% quality
        confidence_score = confidence
        speed_score = max(0, 1.0 - (latency_ms / 2000))  # Good if < 2s
        quality_score = 1.0  # Placeholder - add your quality metrics

        reward = (confidence_score * 0.4) + (speed_score * 0.3) + (quality_score * 0.3)
        return max(0.0, min(1.0, reward))

    def get_usage_stats(self) -> Dict[str, Any]:
        """Get router usage statistics"""
        total_requests = sum(self.genome_usage.values())
        return {
            "total_requests": self.request_count,
            "genome_usage": self.genome_usage,
            "usage_percentages": {
                gid: (count / total_requests * 100) if total_requests > 0 else 0
                for gid, count in self.genome_usage.items()
            },
            "bandit_stats": self.bandit.get_stats()
        }

# ============================================================================
# 7. IMPROVEMENT DAEMON (for scheduler/cron)
# ============================================================================

async def improvement_daemon(
    trainset_path: Path,
    output_dir: Path,
    executor: Callable,
    num_generations: int = 10
):
    """
    Nightly improvement daemon - runs evolutionary optimization
    Deploy this in your CI/scheduler
    """
    logger.info("🌙 Improvement Daemon: Starting nightly optimization")
    
    # Load training data
    trainset = json.loads(trainset_path.read_text())
    
    # Initialize optimizer
    optimizer = EvolutionaryPromptOptimizer(
        population_size=12,
        survivors=6,
        eval_samples=64
    )
    
    # Run evolution
    best_genome = await optimizer.optimize(
        trainset=trainset,
        executor=executor,
        num_generations=num_generations
    )
    
    # Save results
    results_path = output_dir / f"evolution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    optimizer.save_results(results_path)
    
    # Stage to bandit (would integrate with your system)
    logger.info(f"🎯 Best genome ready for deployment: {best_genome.genome_id}")
    
    return best_genome, optimizer.fitness_history


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

async def example_executor(spec: PromptSpec, genome: Genome) -> ExecutionMetrics:
    """Example executor - replace with your actual system"""
    import time
    
    start = time.time()
    
    # Simulate execution
    await asyncio.sleep(random.uniform(0.05, 0.2))
    
    latency_ms = (time.time() - start) * 1000
    
    return ExecutionMetrics(
        schema_ok=True,
        safety_flags=[],
        validator_score=random.uniform(0.8, 1.0),
        latency_ms=latency_ms,
        tokens_total=random.randint(100, 500),
        repairs=0,
        accuracy=random.uniform(0.85, 1.0),
        cost_usd=0.001
    )


async def demo():
    """Demo the evolutionary optimizer"""
    
    # Mock training data
    trainset = [
        {"query": "Write a Python function to sort a list", "context": "coding task"},
        {"query": "Explain quantum computing", "context": "explanation task"},
        {"query": "Analyze this dataset", "context": "analysis task"},
    ] * 20
    
    # Initialize optimizer
    optimizer = EvolutionaryPromptOptimizer()
    
    # Run optimization
    best_genome = await optimizer.optimize(
        trainset=trainset,
        executor=example_executor,
        num_generations=5
    )
    
    print(f"\n🎉 Best Genome:")
    print(f"  ID: {best_genome.genome_id}")
    print(f"  Rubric: {best_genome.rubric}")
    print(f"  Temp: {best_genome.temp}")
    print(f"  Max Tokens: {best_genome.max_tokens}")
    print(f"  Generation: {best_genome.generation}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(demo())

