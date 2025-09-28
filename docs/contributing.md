# Contributing Guidelines

These guidelines implement the Agentic LLM Core Constitution and codify the end-to-end workflow for changes, automation, and continuous improvement.

---

## 1. Foundations
- **Read the Constitution:** `prompt_engineering/.specify/memory/constitution.md` governs all work. Reference the relevant clauses in plans and PRs.
- **Scope First:** Every task must originate from a plan (`plans/`) or an issue describing the expected outcome, success metrics, and rollback strategy.

---

## 2. Development Workflow
1. **Plan → Implement → Evaluate → Promote**
   - Author or update the relevant plan. Include links to benchmarks, KB sources, and risks.
   - Write or update tests / grading criteria before code changes (Red→Green→Refactor enforced).
   - Implement the change with structured logging and doc updates.
   - Run evaluation suite (pytest, grading harness, smoke tests). Capture outputs.
   - Submit PR referencing the plan, constitution clause(s), and evaluation results.

2. **Testing**
   - `PYTHONPATH=. pytest` including new tests.
   - When relevant, run `PYTHONPATH=. pytest tests/test_parallel_pipeline.py tests/test_self_iterating_orchestrator.py` to ensure continuous-improvement functions remain intact.
   - For orchestrator-sensitive changes, run the smoke script from `README` or `smoke_tests/`.

3. **Documentation**
   - Inline docstrings for new modules.
   - Update `docs/` for user-facing or operational changes.
   - Add knowledge base entries when new concepts or references appear.

4. **Review Process**
   - Two reviewers for high-impact changes (security, orchestration, constitution updates).
   - Reviewers check tests, compliance with principles, KB grounding, and clarity.
   - Approval requires all CI jobs green and reviewers satisfied.

---

## 3. Automation & Orchestration
- **SelfImprovementOrchestrator** is scheduled to run daily or when new grading data arrives.
- Promotion decisions are logged in `.self_improvement/orchestration_history.jsonl` and `.self_improvement/monitoring_summary.jsonl`.
- Promotions must invoke `promote_callback` to snapshot baseline, apply updates, and notify maintainers.
- Failures or repeated no-promote runs trigger review; create issues to investigate root causes.

---

## 4. Knowledge & Data Hygiene
- All prompts and reasoning must ground in curated KB sources (Docker vector stores or markdown).
- Prompt recycling outputs (`recycle_logs/recycle.jsonl`, `trash.jsonl`) should be reviewed regularly and used to generate SFT datasets.
- Flagged / low-score prompts are automatically excluded by the recycler; when they're legit defects, open issues to fix upstream logic.

---

## 5. Monitoring & Alerts
- Monitor aggregate metrics via dashboard reading JSONL histories (avg score, failure rate, promotion frequency).
- Alerting thresholds (e.g., repeated fallback to manual mode) must be documented and handled promptly.
- Keep a changelog of threshold adjustments; calibrator updates are already persisted.

---

## 6. Security & Resource Controls
- All core services run locally/offline. Protect secrets in environment variables.
- Rate-limit orchestration runs and track compute usage before running heavy SFT/RL jobs.
- Log access should respect least privilege; scrub sensitive fields before sharing.

---

## 7. Governance Changes
- Proposals to modify the constitution require a written RFC, approval from at least two maintainers, and migration plan.
- Record amendments in the constitution version history.

---

By following these guidelines you ensure the system stays auditable, grounded, and continuously improving in line with the Constitution.
