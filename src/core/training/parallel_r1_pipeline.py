"""Parallel-R1 inspired fine-tuning pipeline integrated with the grading system."""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

try:  # Optional docker integration (may fail in minimal environments)
    from ..memory.docker_config import create_service_discovery
except ModuleNotFoundError:  # pragma: no cover
    create_service_discovery = None  # type: ignore

try:  # Optional dependency: asyncpg may not be installed during unit tests
    from ..memory.vector_pg import PostgreSQLVectorStore, VectorStore
except ModuleNotFoundError:  # pragma: no cover - fallback for minimal environments
    PostgreSQLVectorStore = None  # type: ignore

    class VectorStore:  # type: ignore[no-redef]
        async def index(self, documents, vectors):
            raise NotImplementedError

        async def query(self, vector, limit: int = 10, filter_metadata: Optional[Dict[str, Any]] = None):
            raise NotImplementedError

        async def get(self, document_ids):
            raise NotImplementedError

        async def delete(self, document_ids):
            raise NotImplementedError

        async def update(self, document_id, document, vector=None):
            raise NotImplementedError

        async def search_by_metadata(self, metadata: Dict[str, Any], limit: int = 10):
            return []

        async def get_stats(self):
            return {}

logger = logging.getLogger(__name__)

if PostgreSQLVectorStore is not None:
    _VECTOR_STORE_CACHE: Dict[Tuple[str, int, str, str], PostgreSQLVectorStore] = {}
else:  # pragma: no cover - fallback typing when asyncpg unavailable
    _VECTOR_STORE_CACHE = {}


@dataclass
class GradeRecord:
    """Single graded interaction used for curriculum decisions."""

    prompt: str
    response: str
    score: float
    metadata: Dict[str, Any] = field(default_factory=dict)

    def difficulty(self) -> str:
        return self.metadata.get("difficulty", "unknown")


class ParallelStage(str, Enum):
    DATASET = "dataset"
    SFT = "sft"
    RL = "rl"


@dataclass
class ParallelTrainingResult:
    stage: ParallelStage
    metrics: Dict[str, float]
    artifacts: Dict[str, Path]
    duration: float = 0.0


class PromptRecycleAction(str, Enum):
    KEEP = "keep"
    RECYCLE = "recycle"
    TRASH = "trash"


@dataclass
class PromptRecycleDecision:
    record: GradeRecord
    action: PromptRecycleAction
    reason: str


class PromptRecycler:
    """Classifies graded records for reuse, recycling, or removal."""

    def __init__(
        self,
        *,
        recycle_threshold: float = 0.95,
        trash_threshold: float = 0.8,
    ) -> None:
        self.recycle_threshold = recycle_threshold
        self.trash_threshold = trash_threshold

    def process(self, records: Sequence[GradeRecord]) -> Tuple[List[GradeRecord], Dict[str, List[PromptRecycleDecision]]]:
        cleaned: List[GradeRecord] = []
        report: Dict[str, List[PromptRecycleDecision]] = {"recycle": [], "trash": []}
        seen_pairs: set[tuple[str, str]] = set()

        for record in records:
            pair = (record.prompt.strip(), record.response.strip())
            if pair in seen_pairs:
                decision = PromptRecycleDecision(record, PromptRecycleAction.TRASH, "duplicate")
                report["trash"].append(decision)
                continue
            seen_pairs.add(pair)

            decision = self.evaluate(record)
            if decision.action == PromptRecycleAction.TRASH:
                report["trash"].append(decision)
                continue
            cleaned.append(record)
            if decision.action == PromptRecycleAction.RECYCLE:
                report["recycle"].append(decision)

        return cleaned, report

    def evaluate(self, record: GradeRecord) -> PromptRecycleDecision:
        metadata = record.metadata or {}
        if metadata.get("flagged") or metadata.get("invalid"):
            return PromptRecycleDecision(record, PromptRecycleAction.TRASH, "flagged")
        if record.score < self.trash_threshold:
            return PromptRecycleDecision(record, PromptRecycleAction.TRASH, "low_score")
        if record.score >= self.recycle_threshold or metadata.get("reuse"):
            return PromptRecycleDecision(record, PromptRecycleAction.RECYCLE, "high_score")
        return PromptRecycleDecision(record, PromptRecycleAction.KEEP, "normal")


class ParallelDatasetBuilder:
    """Builds Parallel-R1 formatted examples using grade records and KB context."""

    def __init__(
        self,
        *,
        vector_store: Optional[VectorStore] = None,
        knowledge_base_dir: Optional[Path] = None,
        min_score: float = 0.85,
        enable_vector_store: bool = True,
    ) -> None:
        self.vector_store = vector_store
        self.knowledge_base_dir = knowledge_base_dir or Path("knowledge_base")
        self.min_score = min_score
        self.enable_vector_store = enable_vector_store
        self._kb_cache: Optional[Dict[str, str]] = None

    async def ensure_vector_store(self) -> Optional[VectorStore]:
        if self.vector_store is not None:
            return self.vector_store
        if not self.enable_vector_store:
            return None
        if create_service_discovery is None or PostgreSQLVectorStore is None:
            return None
        try:
            discovery = create_service_discovery()
            config = discovery.get_postgresql_config()
            cache_key = (config.host, config.port, config.database, config.username)
            vector_store = _VECTOR_STORE_CACHE.get(cache_key)
            if vector_store is None:
                vector_store = PostgreSQLVectorStore(config)
                await vector_store.initialize()
                _VECTOR_STORE_CACHE[cache_key] = vector_store
            self.vector_store = vector_store
            return vector_store
        except Exception as exc:  # pragma: no cover
            logger.debug("Falling back to knowledge base files only: %s", exc)
            return None

    async def build_dataset(
        self,
        records: Sequence[GradeRecord],
        *,
        difficulty: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        dataset: List[Dict[str, Any]] = []
        store = await self.ensure_vector_store()
        for record in records:
            if record.score < self.min_score:
                continue
            if difficulty and record.difficulty() != difficulty:
                continue

            context_chunks = await self._gather_context(store, record)
            parallel_paths = self._derive_parallel_paths(record.response)
            formatted_target = self._format_parallel_response(parallel_paths)

            dataset.append(
                {
                    "input": record.prompt,
                    "context": context_chunks,
                    "target": formatted_target,
                    "score": record.score,
                    "metadata": record.metadata,
                }
            )
        return dataset

    async def _gather_context(
        self, store: Optional[VectorStore], record: GradeRecord
    ) -> List[str]:
        snippets: List[str] = []
        metadata = record.metadata.get("context", {})
        if store is not None:
            try:
                results = await store.search_by_metadata(metadata, limit=3)
                for doc in results:
                    snippets.append(doc.content)
            except Exception as exc:  # pragma: no cover
                logger.debug("Vector store lookup failed: %s", exc)
        snippets.extend(self._load_knowledge_base_snippets(record))
        return snippets[:5]

    def _load_knowledge_base_snippets(self, record: GradeRecord) -> List[str]:
        snippets: List[str] = []
        kb_data = self._load_kb_cache()
        topic = (record.metadata.get("topic") or "").lower()
        for text in kb_data.values():
            if not topic:
                snippets.append(text)
                continue
            lowered = text.lower()
            if topic in lowered or "parallel" in lowered:
                snippets.append(text)
        return snippets

    def _load_kb_cache(self) -> Dict[str, str]:
        if self._kb_cache is not None:
            return self._kb_cache
        cache: Dict[str, str] = {}
        if self.knowledge_base_dir.exists():
            for path in self.knowledge_base_dir.glob("*.md"):
                try:
                    cache[path.name] = path.read_text(encoding="utf-8")[:1200]
                except OSError as exc:  # pragma: no cover
                    logger.debug("Failed to read %s: %s", path, exc)
        self._kb_cache = cache
        return cache

    def _derive_parallel_paths(self, response: str) -> List[str]:
        if "<Path>" in response:
            paths = []
            buffer = []
            inside = False
            for line in response.splitlines():
                if "<Path>" in line:
                    inside = True
                    buffer = [line.replace("<Path>", "").strip()]
                elif "</Path>" in line and inside:
                    buffer.append(line.replace("</Path>", "").strip())
                    paths.append(" ".join(part for part in buffer if part))
                    inside = False
                elif inside:
                    buffer.append(line.strip())
            if paths:
                return paths
        chunks = [segment.strip() for segment in response.split("\n\n") if segment.strip()]
        if len(chunks) >= 2:
            return chunks[:2]
        midpoint = len(response) // 2
        return [response[:midpoint].strip(), response[midpoint:].strip()]

    def _format_parallel_response(self, paths: Iterable[str]) -> str:
        path_str = "".join(f"<Path>{path}</Path>\n" for path in paths if path)
        summary = "Summaries: " + " | ".join(path[:120] for path in paths if path)
        return f"<Parallel>\n{path_str}</Parallel>\n<Summary>{summary}</Summary>"


class ParallelSFTTrainer:
    """Write Parallel-R1 datasets and prepare metadata for fine-tuning."""

    def __init__(self, output_dir: Path) -> None:
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def train(self, dataset: Sequence[Dict[str, Any]]) -> ParallelTrainingResult:
        dataset_path = self.output_dir / "parallel_sft_dataset.jsonl"
        with dataset_path.open("w", encoding="utf-8") as handle:
            for row in dataset:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
        metrics = {
            "examples": float(len(dataset)),
            "avg_score": float(sum(item.get("score", 0.0) for item in dataset) / max(len(dataset), 1)),
        }
        logger.info("Parallel SFT dataset prepared at %s", dataset_path)
        return ParallelTrainingResult(ParallelStage.SFT, metrics, {"dataset": dataset_path})


class ParallelRLTrainer:
    """Placeholder RL trainer that computes heuristic rewards for validation."""

    def __init__(self, *, explore_temperature: float = 0.9, verify_temperature: float = 0.3) -> None:
        self.explore_temperature = explore_temperature
        self.verify_temperature = verify_temperature

    def train(self, dataset: Sequence[Dict[str, Any]]) -> ParallelTrainingResult:
        diversity = self._estimate_diversity(dataset)
        stability = max(0.0, 1.0 - abs(self.explore_temperature - self.verify_temperature))
        metrics = {
            "reward_mean": float(0.6 * diversity + 0.4 * stability),
            "path_diversity": diversity,
            "stability": stability,
        }
        return ParallelTrainingResult(ParallelStage.RL, metrics, {})

    def _estimate_diversity(self, dataset: Sequence[Dict[str, Any]]) -> float:
        if not dataset:
            return 0.0
        unique_summaries = {entry.get("target", "") for entry in dataset}
        return min(1.0, len(unique_summaries) / max(len(dataset), 1))


class ParallelExecutionPolicy:
    """Adjusts inference parameters based on curriculum stage results."""

    def __init__(self, base_temperature: float = 0.4, base_branch_count: int = 2) -> None:
        self.base_temperature = base_temperature
        self.base_branch_count = base_branch_count

    def derive_parameters(self, rl_metrics: Dict[str, float]) -> Dict[str, Any]:
        diversity = rl_metrics.get("path_diversity", 0.5)
        reward = rl_metrics.get("reward_mean", 0.5)
        temperature = min(1.2, self.base_temperature + 0.3 * diversity)
        branches = max(self.base_branch_count, int(round(self.base_branch_count + diversity * 2)))
        confidence = min(1.0, (reward + diversity) / 2)
        return {
            "temperature": round(temperature, 3),
            "branch_count": branches,
            "confidence": round(confidence, 3),
        }


class ParallelScoreboard:
    """Tracks metrics across stages for promotion decisions."""

    def __init__(self) -> None:
        self.results: Dict[ParallelStage, ParallelTrainingResult] = {}

    def add_result(self, result: ParallelTrainingResult) -> None:
        self.results[result.stage] = result

    def qualifies_for_promotion(self, *, minimum_gain: float = 0.04) -> bool:
        sft_metrics = self.results.get(ParallelStage.SFT)
        rl_metrics = self.results.get(ParallelStage.RL)
        if not sft_metrics or not rl_metrics:
            return False
        avg_score = sft_metrics.metrics.get("avg_score", 0.0)
        reward = rl_metrics.metrics.get("reward_mean", 0.0)
        return avg_score >= 0.85 and reward >= minimum_gain

    def summary(self) -> Dict[str, Any]:
        return {
            stage.value: {
                "metrics": result.metrics,
                "artifacts": {name: str(path) for name, path in result.artifacts.items()},
                "duration": result.duration,
            }
            for stage, result in self.results.items()
        }


class ParallelR1Pipeline:
    """High-level orchestration aligning grading triggers with the Parallel-R1 curriculum."""

    def __init__(
        self,
        *,
        dataset_builder: ParallelDatasetBuilder,
        sft_trainer: ParallelSFTTrainer,
        rl_trainer: ParallelRLTrainer,
        execution_policy: Optional[ParallelExecutionPolicy] = None,
        recycler: Optional[PromptRecycler] = None,
        recycle_output_dir: Optional[Path] = None,
    ) -> None:
        self.dataset_builder = dataset_builder
        self.sft_trainer = sft_trainer
        self.rl_trainer = rl_trainer
        self.execution_policy = execution_policy or ParallelExecutionPolicy()
        self.scoreboard = ParallelScoreboard()
        self.recycler = recycler
        self.recycle_output_dir = recycle_output_dir
        if self.recycle_output_dir:
            self.recycle_output_dir.mkdir(parents=True, exist_ok=True)

    async def run(
        self,
        records: Sequence[GradeRecord],
        *,
        difficulty: Optional[str] = None,
    ) -> Dict[str, Any]:
        recycle_report: Dict[str, List[PromptRecycleDecision]] = {"recycle": [], "trash": []}
        filtered_records = list(records)
        if self.recycler:
            filtered_records, recycle_report = self.recycler.process(records)
            self._persist_recycle_report(recycle_report)

        start = time.perf_counter()
        dataset = await self.dataset_builder.build_dataset(filtered_records, difficulty=difficulty)
        dataset_duration = time.perf_counter() - start
        dataset_result = ParallelTrainingResult(
            ParallelStage.DATASET,
            {
                "examples": float(len(dataset)),
                "input_records": float(len(records)),
                "filtered_records": float(len(filtered_records)),
                "recycle": float(len(recycle_report["recycle"])),
                "trash": float(len(recycle_report["trash"])),
            },
            {},
            duration=dataset_duration,
        )
        self.scoreboard.add_result(dataset_result)

        start = time.perf_counter()
        sft_result = self.sft_trainer.train(dataset)
        sft_result.duration = time.perf_counter() - start
        self.scoreboard.add_result(sft_result)

        start = time.perf_counter()
        rl_result = self.rl_trainer.train(dataset)
        rl_result.duration = time.perf_counter() - start
        self.scoreboard.add_result(rl_result)

        policy = self.execution_policy.derive_parameters(rl_result.metrics)
        promoted = self.scoreboard.qualifies_for_promotion()

        return {
            "policy": policy,
            "promotion_ready": promoted,
            "summary": self.scoreboard.summary(),
            "timings": {
                ParallelStage.DATASET.value: dataset_duration,
                ParallelStage.SFT.value: sft_result.duration,
                ParallelStage.RL.value: rl_result.duration,
            },
            "recycling": {
                "recycle": [decision.reason for decision in recycle_report["recycle"]],
                "trash": [decision.reason for decision in recycle_report["trash"]],
            },
        }

    def _persist_recycle_report(self, report: Dict[str, List[PromptRecycleDecision]]) -> None:
        if not self.recycle_output_dir:
            return
        def _write(category: str, decisions: List[PromptRecycleDecision]) -> None:
            if not decisions:
                return
            path = self.recycle_output_dir / f"{category}.jsonl"
            with path.open("a", encoding="utf-8") as handle:
                for decision in decisions:
                    payload = {
                        "prompt": decision.record.prompt,
                        "response": decision.record.response,
                        "score": decision.record.score,
                        "metadata": decision.record.metadata,
                        "reason": decision.reason,
                    }
                    handle.write(json.dumps(payload, ensure_ascii=False) + "\n")

        _write("recycle", report.get("recycle", []))
        _write("trash", report.get("trash", []))


__all__ = [
    "GradeRecord",
    "ParallelDatasetBuilder",
    "ParallelExecutionPolicy",
    "ParallelR1Pipeline",
    "ParallelRLTrainer",
    "ParallelSFTTrainer",
    "ParallelScoreboard",
    "ParallelStage",
    "ParallelTrainingResult",
    "PromptRecycleAction",
    "PromptRecycleDecision",
    "PromptRecycler",
]
