"""Self-iterating orchestration loop for continuous model improvement."""

from __future__ import annotations

import json
import logging
import random
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence

from ..training import GradeRecord, ParallelR1Pipeline, PromptRecycler

logger = logging.getLogger(__name__)


@dataclass
class TriggerConfig:
    """Thresholds that decide when the improvement loop should run."""

    min_average_score: float = 0.88
    max_failure_rate: float = 0.1
    max_iterations_per_run: int = 3
    stale_seconds: int = 6 * 60 * 60  # re-run if data older than 6 hours


@dataclass
class CandidatePlan:
    """Represents a proposed change to pipeline parameters."""

    name: str
    overrides: Dict[str, Any]
    notes: str = ""


@dataclass
class OrchestrationReport:
    """Result of a single orchestration run."""

    triggered: bool
    reason: str
    candidates_evaluated: List[Dict[str, Any]] = field(default_factory=list)
    promoted_candidate: Optional[str] = None
    timestamp: float = field(default_factory=lambda: time.time())

    def to_json(self) -> str:
        return json.dumps(
            {
                "triggered": self.triggered,
                "reason": self.reason,
                "candidates_evaluated": self.candidates_evaluated,
                "promoted_candidate": self.promoted_candidate,
                "timestamp": self.timestamp,
            },
            ensure_ascii=False,
        )


class PromotionCalibrator:
    """Adapts trigger thresholds based on observed candidate quality."""

    def __init__(
        self,
        *,
        min_score_floor: float = 0.82,
        min_score_ceiling: float = 0.95,
        smoothing: float = 0.2,
    ) -> None:
        self.min_score_floor = min_score_floor
        self.min_score_ceiling = min_score_ceiling
        self.smoothing = smoothing
        self.min_average_score = min_score_ceiling
        self.history: List[float] = []

    def update(self, metrics: Dict[str, Any]) -> float:
        reward = metrics.get("reward_mean")
        if reward is None:
            return self.min_average_score
        reward = max(self.min_score_floor, min(self.min_score_ceiling, float(reward)))
        self.history.append(reward)
        self.min_average_score = (
            (1 - self.smoothing) * self.min_average_score + self.smoothing * reward
        )
        self.min_average_score = max(self.min_score_floor, min(self.min_score_ceiling, self.min_average_score))
        return self.min_average_score

    def as_dict(self) -> Dict[str, Any]:
        return {
            "min_average_score": self.min_average_score,
            "history": self.history[-5:],
        }


class SelfImprovementOrchestrator:
    """Co-ordinates observation, candidate generation, evaluation, and promotion."""

    def __init__(
        self,
        *,
        pipeline: ParallelR1Pipeline,
        grade_fetcher: Callable[[], Sequence[GradeRecord]],
        promote_callback: Optional[Callable[[CandidatePlan, Dict[str, Any]], None]] = None,
        trigger_config: Optional[TriggerConfig] = None,
        recycler: Optional[PromptRecycler] = None,
        calibrator: Optional[PromotionCalibrator] = None,
        workdir: Optional[Path] = None,
    ) -> None:
        self.pipeline = pipeline
        self.grade_fetcher = grade_fetcher
        self.promote_callback = promote_callback
        self.trigger_config = trigger_config or TriggerConfig()
        self.recycler = recycler or PromptRecycler()
        self.calibrator = calibrator or PromotionCalibrator(
            min_score_floor=self.trigger_config.min_average_score - 0.06,
            min_score_ceiling=self.trigger_config.min_average_score,
        )
        self.workdir = workdir or Path(".self_improvement")
        self.workdir.mkdir(parents=True, exist_ok=True)

    def observe_metrics(self, grades: Sequence[GradeRecord]) -> Dict[str, float]:
        if not grades:
            return {"avg": 0.0, "fail_rate": 1.0, "count": 0.0}
        avg = sum(g.score for g in grades) / len(grades)
        fail_rate = sum(1 for g in grades if g.score < 0.5) / len(grades)
        return {"avg": avg, "fail_rate": fail_rate, "count": float(len(grades))}

    def should_trigger(self, metrics: Dict[str, float], last_run: Optional[float]) -> (bool, str):
        if metrics["count"] == 0:
            return True, "no_data"
        if metrics["avg"] < self.trigger_config.min_average_score:
            return True, f"avg_score_below_{self.trigger_config.min_average_score}"
        if metrics["fail_rate"] > self.trigger_config.max_failure_rate:
            return True, f"fail_rate_above_{self.trigger_config.max_failure_rate}"
        if last_run is None or (time.time() - last_run) > self.trigger_config.stale_seconds:
            return True, "stale_results"
        return False, "within_thresholds"

    def generate_candidate_plans(self, metrics: Dict[str, float]) -> List[CandidatePlan]:
        base_temperature = 0.4 if metrics["avg"] < 0.85 else 0.3
        candidates = [
            CandidatePlan(
                name="increase_parallel_branches",
                overrides={"execution_policy": {"base_branch_count": 3, "base_temperature": base_temperature}},
                notes="More parallel paths to explore broader reasoning space",
            ),
            CandidatePlan(
                name="lower_temperature",
                overrides={"execution_policy": {"base_branch_count": 2, "base_temperature": 0.25}},
                notes="Promote determinism for consistent scoring",
            ),
        ]
        extra_candidate = CandidatePlan(
            name="adaptive_threshold",
            overrides={"promotion_gain": metrics["avg"] * 0.05},
            notes="Adjust promotion gain dynamically based on current average",
        )
        candidates.append(extra_candidate)
        return candidates[: self.trigger_config.max_iterations_per_run]

    async def evaluate_candidate(
        self,
        candidate: CandidatePlan,
        records: Sequence[GradeRecord],
    ) -> Dict[str, Any]:
        original_policy = self.pipeline.execution_policy
        promotion_gain = candidate.overrides.get("promotion_gain")
        config_overrides = candidate.overrides.get("execution_policy", {})
        try:
            if config_overrides:
                self.pipeline.execution_policy = original_policy.__class__(
                    base_temperature=config_overrides.get("base_temperature", original_policy.base_temperature),
                    base_branch_count=config_overrides.get("base_branch_count", original_policy.base_branch_count),
                )
            result = await self.pipeline.run(records)
        finally:
            self.pipeline.execution_policy = original_policy
        result_metrics = result["summary"].get("rl", {}).get("metrics", {})
        result_metrics["promotion_gain_override"] = promotion_gain
        return {
            "candidate": candidate.name,
            "metrics": result_metrics,
            "policy": result["policy"],
            "promotion_ready": result["promotion_ready"],
            "raw": result,
            "notes": candidate.notes,
        }

    def select_best_candidate(self, evaluations: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if not evaluations:
            return None
        sorted_evals = sorted(
            evaluations,
            key=lambda item: item["metrics"].get("reward_mean", 0.0),
            reverse=True,
        )
        best = sorted_evals[0]
        if best["promotion_ready"]:
            return best
        return None

    def persist_report(self, report: OrchestrationReport, *, calibration: Optional[Dict[str, Any]] = None) -> None:
        log_path = self.workdir / "orchestration_history.jsonl"
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(report.to_json() + "\n")
        if calibration is not None:
            monitor_path = self.workdir / "monitoring_summary.jsonl"
            payload = {
                "timestamp": report.timestamp,
                "calibration": calibration,
                "trigger_config": {
                    "min_average_score": self.trigger_config.min_average_score,
                    "max_failure_rate": self.trigger_config.max_failure_rate,
                },
            }
            with monitor_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(payload, ensure_ascii=False) + "\n")

    async def run_once(self, last_run_timestamp: Optional[float] = None) -> OrchestrationReport:
        grades = list(self.grade_fetcher())
        metrics = self.observe_metrics(grades)
        triggered, reason = self.should_trigger(metrics, last_run_timestamp)
        if not triggered:
            report = OrchestrationReport(triggered=False, reason=reason)
            self.persist_report(report, calibration=self.calibrator.as_dict())
            return report

        candidates = self.generate_candidate_plans(metrics)
        evaluations: List[Dict[str, Any]] = []
        for candidate in candidates:
            evaluation = await self.evaluate_candidate(candidate, grades)
            evaluations.append(evaluation)

        best = self.select_best_candidate(evaluations)
        report = OrchestrationReport(
            triggered=True,
            reason=reason,
            candidates_evaluated=evaluations,
            promoted_candidate=best["candidate"] if best else None,
        )
        if best and self.promote_callback:
            self.promote_callback(
                CandidatePlan(name=best["candidate"], overrides={}, notes=best["notes"]),
                best,
            )
        if best:
            new_threshold = self.calibrator.update(best["metrics"])
            self.trigger_config.min_average_score = new_threshold
        self.persist_report(report, calibration=self.calibrator.as_dict())
        return report


__all__ = [
    "CandidatePlan",
    "OrchestrationReport",
    "SelfImprovementOrchestrator",
    "TriggerConfig",
]
