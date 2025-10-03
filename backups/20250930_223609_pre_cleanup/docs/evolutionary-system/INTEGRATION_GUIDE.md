# 🚀 Evolutionary Prompt Optimization - Integration Guide

## Overview

This guide walks you through integrating the evolutionary prompt optimization system with **BOTH** your backend systems:
- **Primary API (Port 8000)** - `api_server.py`
- **Consolidated API (Port 8004)** - `consolidated_api_architecture.py`

---

## Prerequisites

✅ Python 3.11+
✅ FastAPI backends running
✅ Ollama with models loaded
✅ PostgreSQL vector store (optional)
✅ DSPy installed: `pip install dspy-ai numpy`

---

## Step 1: Build Golden Dataset (30 minutes)

### 1.1 Run the Dataset Builder

```bash
cd "/Users/christianmerrill/Prompt Engineering"

# Build golden dataset
python scripts/build_golden_dataset.py
```

This creates `data/golden_dataset.json` with:
- ✅ 50+ high-quality examples
- ✅ Balanced across task types
- ✅ PRD-aligned examples (ST-101 to ST-111)
- ✅ Manual curated examples

### 1.2 Verify the Dataset

```bash
# Check the output
cat data/golden_dataset.json | jq '.metadata'

# Expected output:
# {
#   "created_at": "2025-10-01T...",
#   "total_examples": 50+,
#   "version": "1.0"
# }
```

### 1.3 Add Your Own Examples (Optional)

Edit `scripts/build_golden_dataset.py` and add domain-specific examples:

```python
builder.add_example(
    query="Your specific use case query",
    expected_output="Expected high-quality output",
    context="domain context",
    intent="task_type",
    quality_score=1.0,
    metadata={"custom": "metadata"}
)
```

---

## Step 2: Test Dual Backend Integration (15 minutes)

### 2.1 Verify Backends Are Running

```bash
# Check Primary API (8000)
curl http://localhost:8000/health

# Check Consolidated API (8004) - if separate
curl http://localhost:8004/api/system/health
```

### 2.2 Run Quick Test

```python
# test_integration.py
import asyncio
from src.core.prompting.dual_backend_integration import DualBackendEvolutionaryIntegration

async def quick_test():
    integration = DualBackendEvolutionaryIntegration()
    await integration.initialize()
    
    # Test Primary API
    print("Testing Primary API...")
    integration.set_backend(use_primary=True)
    
    from src.core.prompting.evolutionary_optimizer import PromptSpec, Genome
    
    spec = PromptSpec(
        intent="test",
        prompt="Write a function to add two numbers",
        tools=[]
    )
    
    genome = Genome(
        rubric="You are a coding assistant",
        cot=True,
        temp=0.7,
        max_tokens=512
    )
    
    metrics = await integration.executor(spec, genome)
    print(f"✅ Primary API: latency={metrics.latency_ms:.0f}ms, score={metrics.validator_score:.2f}")
    
    # Test Consolidated API  
    print("Testing Consolidated API...")
    integration.set_backend(use_primary=False)
    
    metrics = await integration.executor(spec, genome)
    print(f"✅ Consolidated API: latency={metrics.latency_ms:.0f}ms, score={metrics.validator_score:.2f}")

asyncio.run(quick_test())
```

```bash
python test_integration.py
```

**Expected Output:**
```
✅ Primary API: latency=324ms, score=0.85
✅ Consolidated API: latency=412ms, score=0.82
```

---

## Step 3: Run First Evolution (1 hour)

### 3.1 Start Small (3 Generations)

```python
# run_first_evolution.py
import asyncio
import json
from pathlib import Path
from src.core.prompting.dual_backend_integration import DualBackendEvolutionaryIntegration

async def main():
    # Load golden dataset
    dataset_path = Path("data/golden_dataset.json")
    with open(dataset_path) as f:
        data = json.load(f)
    
    golden_dataset = data["examples"][:20]  # Start with 20 examples
    
    # Initialize
    integration = DualBackendEvolutionaryIntegration()
    await integration.initialize()
    
    # Run evolution (3 generations for quick test)
    best_genome = await integration.optimize_comprehensive(
        base_prompt="You are a helpful AI assistant. Be clear, specific, and actionable.",
        golden_dataset=golden_dataset,
        num_generations=3,
        use_mipro=False  # Skip MIPROv2 for first test
    )
    
    print(f"\n✅ OPTIMIZATION COMPLETE")
    print(f"Best Genome ID: {best_genome.genome_id}")
    print(f"Temperature: {best_genome.temp}")
    print(f"Max Tokens: {best_genome.max_tokens}")
    print(f"Model: {best_genome.model_key}")
    print(f"Generation: {best_genome.generation}")

if __name__ == "__main__":
    asyncio.run(main())
```

```bash
python run_first_evolution.py
```

**Expected Output:**
```
🚀 Starting comprehensive dual-backend optimization
📝 Skipping MIPROv2 (disabled)
🧬 Phase 2a: Evolutionary optimization (Primary API)
   Gen 0: Best=0.7234, Mean=0.6543
   Gen 1: Best=0.7856, Mean=0.7123
   Gen 2: Best=0.8234, Mean=0.7678
✅ Primary API optimization: score=0.8234
🧬 Phase 2b: Testing on Consolidated API
✅ Consolidated API test: score=0.8012
🎉 Primary API performed better!
💾 Results saved to results/dual_backend_optimization_20251001_143022.json

✅ OPTIMIZATION COMPLETE
Best Genome ID: genome_1727795422_4567
Temperature: 0.65
Max Tokens: 1024
Model: primary
Generation: 2
```

### 3.2 Analyze Results

```bash
# View evolution history
cat results/dual_backend_optimization_*.json | jq '.fitness_history'

# View backend comparison
cat results/backend_comparison_*.json | jq '.'
```

**Key Metrics to Look For:**
- ✅ **Best score improving** across generations
- ✅ **Mean score converging** (less variance)
- ✅ **Backend comparison** showing which API is better

---

## Step 4: Scale Up (2 hours)

### 4.1 Full Evolution Run

Once satisfied with small test, run full optimization:

```python
# run_full_evolution.py
best_genome = await integration.optimize_comprehensive(
    base_prompt="You are a helpful AI assistant...",
    golden_dataset=golden_dataset,  # ALL examples
    num_generations=10,  # Full run
    use_mipro=True  # Enable MIPROv2
)
```

**This will:**
1. Run MIPROv2 to optimize prompt text (~15 min)
2. Run 10 generations of evolution (~45 min)
3. Test on both backends (~10 min)
4. Save comprehensive results

### 4.2 Monitor Progress

```bash
# Watch logs in real-time
tail -f logs/backend_main.log | grep -E "Gen|score"

# Expected:
# Gen 0: Best=0.7234, Mean=0.6543
# Gen 1: Best=0.7856, Mean=0.7123
# ...
# Gen 10: Best=0.9234, Mean=0.8876
```

---

## Step 5: Deploy to Production (30 minutes)

### 5.1 Extract Top Genomes

```python
# deploy_to_production.py
from pathlib import Path
import json

# Load results
results = json.loads(Path("results/dual_backend_optimization_latest.json").read_text())

# Get top 5 genomes
top_5_ids = [
    genome["genome_id"] 
    for genome in results["best_genomes"][:5]
]

print(f"Top 5 Genomes: {top_5_ids}")
```

### 5.2 Deploy with Bandit

```python
# Add to your main API server
from src.core.prompting.dual_backend_integration import DualBackendEvolutionaryIntegration

# Global integration instance
evolutionary_integration = None

@app.on_event("startup")
async def startup():
    global evolutionary_integration
    
    # Initialize
    evolutionary_integration = DualBackendEvolutionaryIntegration()
    await evolutionary_integration.initialize()
    
    # Load top genomes from evolution results
    results = json.loads(Path("results/dual_backend_optimization_latest.json").read_text())
    
    top_genomes = []
    for genome_data in results["best_genomes"][:5]:
        genome = Genome(
            rubric=genome_data["genome"]["rubric"],
            cot=genome_data["genome"]["cot"],
            temp=genome_data["genome"]["temp"],
            max_tokens=genome_data["genome"]["max_tokens"],
            model_key=genome_data["genome"]["model_key"]
        )
        top_genomes.append(genome)
    
    # Deploy with bandit routing
    evolutionary_integration.deploy_to_production(top_genomes, backend="auto")
    
    print("✅ Evolutionary optimization deployed!")

@app.post("/chat")
async def chat(request: ChatRequest):
    # Use bandit routing
    result = await evolutionary_integration.production_route(
        user_query=request.message,
        context=request.context or "",
        intent=request.intent or "text_generation"
    )
    
    # Return response
    return {
        "response": result["response"],
        "genome_id": result["genome_id"],
        "backend": result["backend"],
        "metrics": result["metrics"]
    }
```

### 5.3 Gradual Rollout

Start with 10% traffic:

```python
import random

@app.post("/chat")
async def chat(request: ChatRequest):
    # 10% evolutionary, 90% traditional
    if random.random() < 0.10:
        # Use evolutionary bandit
        result = await evolutionary_integration.production_route(...)
    else:
        # Use traditional routing
        result = await traditional_chat(...)
    
    return result
```

Monitor for 24 hours, then increase to 50%, then 100%.

---

## Step 6: Monitor & Improve (Ongoing)

### 6.1 Track Bandit Stats

```python
# GET /api/evolutionary/stats
@app.get("/api/evolutionary/stats")
async def get_stats():
    stats = evolutionary_integration.get_bandit_stats()
    return stats
```

**Example Response:**
```json
{
  "genome_1234": {
    "pulls": 847,
    "mean_reward": 0.856,
    "expected_value": 0.862
  },
  "genome_5678": {
    "pulls": 623,
    "mean_reward": 0.834,
    "expected_value": 0.841
  },
  "current_backend": "primary",
  "execution_history_count": 1470
}
```

### 6.2 Nightly Improvement Daemon

Set up cron job:

```bash
# crontab -e
# Run every night at 2 AM
0 2 * * * cd /path/to/project && python -m src.core.prompting.improvement_daemon_runner
```

```python
# src/core/prompting/improvement_daemon_runner.py
import asyncio
from pathlib import Path
from src.core.prompting.dual_backend_integration import DualBackendEvolutionaryIntegration
from src.core.prompting.evolutionary_optimizer import improvement_daemon

async def nightly_run():
    integration = DualBackendEvolutionaryIntegration()
    await integration.initialize()
    
    # Run overnight optimization
    best_genome, history = await improvement_daemon(
        trainset_path=Path("data/golden_dataset.json"),
        output_dir=Path("results/nightly"),
        executor=integration.executor,
        num_generations=20  # More generations overnight
    )
    
    # Auto-deploy if significantly better
    current_best_score = 0.85  # Load from production metrics
    new_best_score = history[-1]["best_score"]
    
    if new_best_score > current_best_score + 0.05:  # 5% improvement
        print(f"🎉 New best genome! Deploying: {best_genome.genome_id}")
        # Deploy logic here
    else:
        print(f"📊 No significant improvement: {new_best_score:.4f} vs {current_best_score:.4f}")

if __name__ == "__main__":
    asyncio.run(nightly_run())
```

### 6.3 Add Sentry Monitoring

```python
import * as Sentry from "@sentry/nextjs"

# In your executor
Sentry.startSpan({
    op: "evolutionary.execution",
    name: f"Genome {genome.genome_id}"
}, (span) => {
    span.setAttribute("genome_id", genome.genome_id)
    span.setAttribute("backend", "primary" if self.use_primary else "consolidated")
    span.setAttribute("temperature", genome.temp)
    span.setAttribute("generation", genome.generation)
    
    # Execute and measure
    metrics = await self.executor(spec, genome)
    
    span.setAttribute("latency_ms", metrics.latency_ms)
    span.setAttribute("quality_score", metrics.validator_score)
    span.setAttribute("cost_usd", metrics.cost_usd)
})
```

---

## Troubleshooting

### Issue: Low Evolution Scores

**Symptoms:** Best score stuck at < 0.7

**Solutions:**
1. ✅ Check golden dataset quality
2. ✅ Increase population size (12 → 20)
3. ✅ Run more generations (10 → 20)
4. ✅ Adjust fitness weights

```python
# Adjust weights in executor
def composite_evaluate(example, spec, meta):
    weights = {
        "latency": 0.0005,  # Lower penalty if latency less important
        "tokens": 0.0002,
        "repairs": 0.3,     # Higher penalty for errors
        "cost": 0.1
    }
```

### Issue: Backend Timeouts

**Symptoms:** Execution takes > 5 seconds

**Solutions:**
1. ✅ Reduce `max_tokens` in genome
2. ✅ Use faster models ("lightweight" vs "primary")
3. ✅ Add timeout to executor

```python
async def executor(self, spec, genome):
    try:
        # Add timeout
        return await asyncio.wait_for(
            self._execute_internal(spec, genome),
            timeout=5.0
        )
    except asyncio.TimeoutError:
        return ExecutionMetrics(schema_ok=False, ...)
```

### Issue: Bandit Not Learning

**Symptoms:** All genomes have similar pull counts after 1000 requests

**Solutions:**
1. ✅ Check reward calculation - ensure diversity
2. ✅ Increase exploration in Thompson sampling
3. ✅ Verify genomes are sufficiently different

```python
# More exploration
class ThompsonBandit:
    def __init__(self, genomes, exploration_bonus=2.0):
        self.exploration_bonus = exploration_bonus  # Higher = more exploration
```

---

## Success Metrics

After 1 week of production:

| Metric | Target | How to Measure |
|--------|--------|----------------|
| **Quality Improvement** | +15% | Compare validator scores |
| **Latency Reduction** | -30% | p95 response times |
| **Cost Reduction** | -40% | Tokens used per query |
| **Bandit Convergence** | 70%+ traffic to top genome | Pull count distribution |

---

## Next Steps

✅ **Week 1:** Build dataset, run first evolution (Steps 1-3)
✅ **Week 2:** Deploy with bandit, monitor carefully (Steps 4-5)
✅ **Week 3:** Scale to 100% traffic, set up nightly daemon (Step 6)
✅ **Week 4+:** Iterate on dataset quality, tune hyperparameters

---

## Files Summary

| File | Purpose |
|------|---------|
| `src/core/prompting/evolutionary_optimizer.py` | Core evolutionary algorithm |
| `src/core/prompting/dual_backend_integration.py` | Integration with both backends |
| `scripts/build_golden_dataset.py` | Dataset builder |
| `data/golden_dataset.json` | Training data |
| `results/dual_backend_optimization_*.json` | Evolution results |
| `results/backend_comparison_*.json` | Backend performance comparison |

---

## Support

If you encounter issues:

1. Check logs: `tail -f logs/backend_main.log`
2. Verify backends: `curl http://localhost:8000/health`
3. Test dataset: `python -c "import json; print(json.load(open('data/golden_dataset.json'))['metadata'])"`
4. Run integration test: `python test_integration.py`

**Your system is now ready for production-grade evolutionary prompt optimization!** 🚀
