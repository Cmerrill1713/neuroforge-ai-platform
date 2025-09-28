import asyncio
from pathlib import Path
from typing import Any, Dict, List

import pytest

from src.core.training import (
    GradeRecord,
    ParallelDatasetBuilder,
    ParallelExecutionPolicy,
    ParallelR1Pipeline,
    ParallelRLTrainer,
    ParallelSFTTrainer,
    PromptRecycler,
)
from src.core.training.parallel_r1_pipeline import VectorStore  # type: ignore


class StubDocument:
    def __init__(self, content: str) -> None:
        self.content = content
        self.metadata: Dict[str, Any] = {}


class StubVectorStore(VectorStore):
    def __init__(self, documents: List[StubDocument]) -> None:
        self.documents = documents

    async def index(self, documents, vectors):
        return []

    async def query(self, vector, limit=10, filter_metadata=None):
        return []

    async def get(self, document_ids):
        return []

    async def delete(self, document_ids):
        return True

    async def update(self, document_id, document, vector=None):
        return True

    async def search_by_metadata(self, metadata: Dict[str, Any], limit: int = 10):
        return self.documents[:limit]

    async def get_stats(self):
        return {"documents": len(self.documents)}


@pytest.mark.asyncio
async def test_parallel_dataset_builder_uses_knowledge_base():
    kb_dir = Path("knowledge_base")
    assert kb_dir.exists(), "knowledge_base directory missing"

    stub_store = StubVectorStore([])
    builder = ParallelDatasetBuilder(vector_store=stub_store, knowledge_base_dir=kb_dir)

    record = GradeRecord(
        prompt="Explain the Parallel-R1 curriculum",
        response="Here is a single reasoning path explaining the curriculum.",
        score=0.95,
        metadata={"topic": "parallel"},
    )

    dataset = await builder.build_dataset([record])
    assert len(dataset) == 1
    context = dataset[0]["context"]
    assert any("Parallel-R1" in chunk for chunk in context), "Expected knowledge base snippet in context"
    assert dataset[0]["target"].startswith("<Parallel>"), "Output should be formatted in parallel structure"


@pytest.mark.asyncio
async def test_parallel_pipeline_run(tmp_path):
    documents = [StubDocument("Parallel reasoning overview.")]
    stub_store = StubVectorStore(documents)
    builder = ParallelDatasetBuilder(vector_store=stub_store, knowledge_base_dir=Path("knowledge_base"))
    sft_trainer = ParallelSFTTrainer(tmp_path)
    rl_trainer = ParallelRLTrainer()
    pipeline = ParallelR1Pipeline(
        dataset_builder=builder,
        sft_trainer=sft_trainer,
        rl_trainer=rl_trainer,
        execution_policy=ParallelExecutionPolicy(),
    )

    records = [
        GradeRecord(
            prompt="Solve 2+2 with parallel thinking",
            response="Path A: explain basics.\n\nPath B: alternative view.",
            score=0.93,
            metadata={"difficulty": "easy", "topic": "math"},
        ),
        GradeRecord(
            prompt="Explain reinforcement scaffolding",
            response="Detailed response about scaffolding and verification.",
            score=0.9,
            metadata={"difficulty": "easy", "topic": "parallel"},
        ),
    ]

    result = await pipeline.run(records, difficulty="easy")

    dataset_file = tmp_path / "parallel_sft_dataset.jsonl"
    assert dataset_file.exists(), "SFT trainer should emit dataset file"
    assert result["policy"]["branch_count"] >= 2
    assert result["promotion_ready"] is True
    summary = result["summary"]
    assert "sft" in summary and "rl" in summary
    timings = result["timings"]
    assert timings["dataset"] >= 0


@pytest.mark.asyncio
async def test_prompt_recycler_filters_records(tmp_path):
    documents = [StubDocument("Parallel reuse test")]
    stub_store = StubVectorStore(documents)
    builder = ParallelDatasetBuilder(
        vector_store=stub_store,
        knowledge_base_dir=Path("knowledge_base"),
        enable_vector_store=False,
    )
    sft_trainer = ParallelSFTTrainer(tmp_path)
    rl_trainer = ParallelRLTrainer()
    recycler = PromptRecycler(recycle_threshold=0.95, trash_threshold=0.85)
    recycle_dir = tmp_path / "recycle_logs"
    pipeline = ParallelR1Pipeline(
        dataset_builder=builder,
        sft_trainer=sft_trainer,
        rl_trainer=rl_trainer,
        recycler=recycler,
        recycle_output_dir=recycle_dir,
    )

    records = [
        GradeRecord(
            prompt="High quality reasoning",
            response="Path A.\n\nPath B.",
            score=0.97,
            metadata={"difficulty": "bench", "topic": "parallel"},
        ),
        GradeRecord(
            prompt="Low score reasoning",
            response="Short answer",
            score=0.6,
            metadata={"difficulty": "bench", "topic": "parallel"},
        ),
        GradeRecord(
            prompt="High quality reasoning",
            response="Path A.\n\nPath B.",
            score=0.99,
            metadata={"difficulty": "bench", "topic": "parallel"},
        ),
    ]

    result = await pipeline.run(records, difficulty="bench")
    dataset_metrics = result["summary"]["dataset"]["metrics"]
    assert dataset_metrics["input_records"] == float(len(records))
    # One low score trashed, one duplicate trashed
    assert dataset_metrics["trash"] == 2.0
    assert dataset_metrics["filtered_records"] == float(len(records) - 2)
    recycling_report = result["recycling"]
    assert "low_score" in recycling_report["trash"]
    assert "duplicate" in recycling_report["trash"]
    recycle_file = recycle_dir / "recycle.jsonl"
    trash_file = recycle_dir / "trash.jsonl"
    assert trash_file.exists()
    assert recycle_file.exists()
    assert trash_file.read_text(encoding="utf-8").count("\n") == len(recycling_report["trash"]) == 2
    assert recycle_file.read_text(encoding="utf-8").count("\n") == len(recycling_report["recycle"]) == 1
