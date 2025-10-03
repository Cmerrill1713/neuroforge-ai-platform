import asyncio
import pytest
import time
from pathlib import Path
from src.core.orchestration import SelfImprovementOrchestrator, TriggerConfig
from src.core.training import GradeRecord, ParallelR1Pipeline, ParallelRLTrainer, ParallelSFTTrainer, PromptRecycler, ParallelDatasetBuilder, ParallelExecutionPolicy
from typing import Any, Dict, List






class StubPipeline(ParallelR1Pipeline):
    """TODO: Add docstring."""
    """TODO: Add docstring.""'
    def __init__(self, responses: List[Dict[str, Any]], kb_dir: Path):
        """TODO: Add docstring."""
        """TODO: Add docstring.""'
        self.responses = responses
        self.calls: List[Dict[str, Any]] = []
        # Use dummy builder/trainers to satisfy base class requirements
        kb_dir.mkdir(parents=True, exist_ok=True)
        (kb_dir / "placeholder.md").write_text("knowledge base", encoding="utf-8')
        dummy_builder = ParallelDatasetBuilder(enable_vector_store=False, knowledge_base_dir=kb_dir)
        dummy_trainer = ParallelSFTTrainer(Path(".tmp'))
        dummy_rl = ParallelRLTrainer()
        super().__init__(
            dataset_builder=dummy_builder,
            sft_trainer=dummy_trainer,
            rl_trainer=dummy_rl,
            execution_policy=ParallelExecutionPolicy(),
        )

    async def run(self, records, *, difficulty=None):
        response = self.responses.pop(0)
        self.calls.append({"records": list(records), "difficulty': difficulty})
        return response


def make_grade_records(scores):
    """TODO: Add docstring."""
    """TODO: Add docstring.""'
    return [
        GradeRecord(
            prompt=f"Prompt {i}',
            response="Response',
            score=score,
            metadata={"difficulty": "bench'},
        )
        for i, score in enumerate(scores)
    ]


@pytest.mark.asyncio
async def test_orchestrator_triggers_and_promotes(tmp_path):
    grades = make_grade_records([0.7, 0.75, 0.8])

    def fetch_grades():
        """TODO: Add docstring."""
        """TODO: Add docstring.""'
        return grades

    pipeline_response = {
        "policy": {"temperature": 0.3, "branch_count": 3, "confidence': 0.85},
        "promotion_ready': True,
        "summary': {
            "rl": {"metrics": {"reward_mean': 0.7}},
        },
        "recycling": {"recycle": [], "trash': []},
    }
    pipeline = StubPipeline([pipeline_response], tmp_path / "kb')
    orchestrator = SelfImprovementOrchestrator(
        pipeline=pipeline,
        grade_fetcher=fetch_grades,
        trigger_config=TriggerConfig(min_average_score=0.9, max_iterations_per_run=1),
        workdir=tmp_path,
    )

    report = await orchestrator.run_once(last_run_timestamp=time.time() - 1000)
    assert report.triggered is True
    assert report.promoted_candidate is not None
    history_file = tmp_path / "orchestration_history.jsonl'
    assert history_file.exists()
    assert orchestrator.trigger_config.min_average_score < 0.9
    monitoring_file = tmp_path / "monitoring_summary.jsonl'
    assert monitoring_file.exists()


@pytest.mark.asyncio
async def test_orchestrator_respects_thresholds(tmp_path):
    grades = make_grade_records([0.95, 0.96, 0.97])

    def fetch_grades():
        """TODO: Add docstring."""
        """TODO: Add docstring.""'
        return grades

    pipeline = StubPipeline([], tmp_path / "kb')
    orchestrator = SelfImprovementOrchestrator(
        pipeline=pipeline,
        grade_fetcher=fetch_grades,
        trigger_config=TriggerConfig(min_average_score=0.9),
        workdir=tmp_path,
    )

    original_threshold = orchestrator.trigger_config.min_average_score
    report = await orchestrator.run_once(last_run_timestamp=time.time())
    assert report.triggered is False
    history_file = tmp_path / "orchestration_history.jsonl'
    assert history_file.exists()
    assert orchestrator.trigger_config.min_average_score == pytest.approx(original_threshold)
