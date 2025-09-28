# Parallel-R1 Inspired Fine-Tuning & Evaluation Pipeline

This plan adapts the **Parallel-R1** curriculum to our scoring-driven agent platform so we can trigger the SFT → RL workflow whenever the grading system flags a model for upgrade.

## 1. Entry Criteria (Scoring Integration)

| Signal | Threshold | Action |
|--------|-----------|--------|
| Weighted agent score (from Intelligent Agent Selector) | Drops below target (e.g. <0.82) for N=5 evaluations | Queue SFT fine-tune
| Reliability metric | Std dev > 0.12 or >8% fail rate | Launch RL exploration stage
| Drift detector | Significant change vs. baseline (>7% drop) | Force full curriculum run
| Task-specific rubric | Fails compliance/safety rubric | Trigger targeted SFT with guardrail prompts

Implementation sketch (scheduler):
```python
if monitor.agent_score(agent) < thresholds.sft:
    pipeline.enqueue("parallel_r1:sft", agent)
if monitor.reliability(agent) < thresholds.rl:
    pipeline.enqueue("parallel_r1:rl", agent)
```

## 2. Curriculum Pipeline

### Stage A – Supervised Parallel SFT
1. **Dataset assembly**
   - Pull easy problems from nightly “gradebook” (tasks scored ≥0.9) as seed trajectories
   - Add high-confidence KB snippets for context
   - Format responses in `<Parallel><Path>…` form
2. **Training setup**
   - Initialize `ParallelSFTTrainer`
   - Use LoRA adapters for fast iteration
3. **Validation**
   - Evaluate on lightweight benchmark (internal GSM-lite)
   - Require ≥5% uplift before progressing

### Stage B – Reinforcement Parallel RL
1. **Curriculum scheduler** escalates difficulty (task tiers: easy → medium → hard)
2. **Reward function** combines
   - Final grade (existing scoring)
   - Path diversity (entropy over paths)
   - Verification consistency (agreement with critic agent)
3. **Exploration scaffolding**
   - Allow increased temperature / branch count in “explore” epochs
   - Switch to conservative settings for “verify” epochs
4. **Stop criteria**
   - Performance plateau (no ≥1% improvement over 3 eval windows)
   - Reward stability (variance < 0.02)

## 3. Components to Build

| Component | Scope | Notes |
|-----------|-------|-------|
| `ParallelDatasetBuilder` | Converts graded transcripts to Parallel-R1 format | Uses KB context retrieval via Docker PG/Weaviate vector stores |
| `ParallelSFTTrainer` | Thin wrapper over existing fine-tune script (`finetune_qwen2.5-7b.py`) | Accepts branch count, special tokens |
| `ParallelRLTrainer` | PPO/GRPO loop with parallel thinking rewards | Reuses `backtest_agentic_system.py` scoring as reward signal |
| `ParallelExecutionPolicy` | Controls branch count/temperature at inference | Integrates with agent manager overrides |
| `ParallelScoreboard` | Dashboards new KPIs (path diversity, consensus rate) | Feeds back into Intelligent Agent Selector |

## 4. Knowledge-Base Connectivity (Docker)

1. Use `DockerInfrastructureConfig` to resolve PostgreSQL/Weaviate endpoints.
2. `ParallelDatasetBuilder` fetches references:
   ```python
   discovery = create_service_discovery()
   store = PostgreSQLVectorStore(discovery.get_postgresql_config())
   await store.initialize()
   context = await store.query(vector, limit=5)
   ```
3. Embed retrieved passages into each `<Path>` to ground reasoning.
4. Cache heavy reads via Redis config in the same module.

## 5. Evaluation & Promotion

- **Backtest Harness**: extend `backtest_agentic_system.py` to simulate parallel inference and compare vs. baseline
- **Automated Grading**: reuse weighted scoring; add new rubric columns (parallel format adherence, consensus confidence)
- **Promotion Gate**: deploy only if
  - Overall score ≥ previous + 4%
  - Compliance checks green
  - Path diversity metric within bounds (avoid degenerate single-path)

## 6. Recommended Additions (Actionable)

1. Implement `ParallelDatasetBuilder` + KB hooks
2. Extend fine-tune script with `--parallel-format` flag (adds special tokens, branch count)
3. Build `parallel_rl.py` module (PPO loop w/ reward adapters)
4. Update agent config with `parallel_reasoner` profile using HRM model (or upgraded model)
5. Add CI task `pytest tests/parallel` covering dataset builder + reward shaping
6. Update monitoring dashboard with parallel KPIs and escalation triggers

## 7. Timeline Suggestion

- **Sprint 1**: Dataset builder, SFT adaptation, baseline evaluation
- **Sprint 2**: RL trainer, reward shaping, backtest integration
- **Sprint 3**: Deployment automation, monitoring, documentation

## 8. Documentation & Runbooks

- Create `docs/parallel_r1_playbook.md` describing run commands, hyperparameters, and rollback process
- Add runbook entries for “Parallel Fine-Tune” & “Parallel RL” in ops wiki

This plan keeps the Parallel-R1 structure aligned with our scoring-based automation so we can auto-trigger curriculum-based fine-tuning whenever the system’s metrics indicate it’s due.
