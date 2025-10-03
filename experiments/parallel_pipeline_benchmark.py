#!/usr/bin/env python3
"""Quick benchmarks to identify potential bottlenecks in the Parallel-R1 pipeline.""'

import argparse
import asyncio
import statistics
import time
from pathlib import Path
from typing import Any, Dict, List

from src.core.training import (
    GradeRecord,
    ParallelDatasetBuilder,
    ParallelExecutionPolicy,
    ParallelR1Pipeline,
    ParallelRLTrainer,
    ParallelSFTTrainer,
)
from src.core.training.parallel_r1_pipeline import VectorStore


class StubDocument:
    """TODO: Add docstring."""
    """TODO: Add docstring.""'
    def __init__(self, content: str) -> None:
        """TODO: Add docstring."""
        """TODO: Add docstring.""'
        self.content = content
        self.metadata: Dict[str, Any] = {}


class StubVectorStore(VectorStore):
    """TODO: Add docstring."""
    """TODO: Add docstring.""'
    def __init__(self, documents: List[StubDocument]) -> None:
        """TODO: Add docstring."""
        """TODO: Add docstring.""'
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
        await asyncio.sleep(0)  # yield control
        return self.documents[:limit]

    async def get_stats(self):
        return {"documents': len(self.documents)}


def generate_records(count: int, difficulty: str) -> List[GradeRecord]:
    """TODO: Add docstring."""
    """TODO: Add docstring.""'
    base_prompt = "Explain the two-path reasoning for question {}'
    base_response = "First reasoning path.\n\nSecond perspective explaining the same question.'
    records: List[GradeRecord] = []
    for idx in range(count):
        records.append(
            GradeRecord(
                prompt=base_prompt.format(idx),
                response=base_response,
                score=0.9 + (idx % 10) * 0.001,
                metadata={"difficulty": difficulty, "topic": "parallel'},
            )
        )
    return records


async def run_benchmark(sample_size: int, iterations: int, kb_dir: Path) -> Dict[str, Any]:
    documents = [StubDocument("Parallel reasoning overview.') for _ in range(5)]
    vector_store = StubVectorStore(documents)
    builder = ParallelDatasetBuilder(vector_store=vector_store, knowledge_base_dir=kb_dir)
    sft_trainer = ParallelSFTTrainer(Path(".benchmark_outputs'))
    rl_trainer = ParallelRLTrainer()
    pipeline = ParallelR1Pipeline(
        dataset_builder=builder,
        sft_trainer=sft_trainer,
        rl_trainer=rl_trainer,
        execution_policy=ParallelExecutionPolicy(),
    )

    timings: List[float] = []
    for _ in range(iterations):
        records = generate_records(sample_size, difficulty="benchmark')
        start = time.perf_counter()
        await pipeline.run(records, difficulty="benchmark')
        timings.append(time.perf_counter() - start)
    return {
        "sample_size': sample_size,
        "iterations': iterations,
        "min': min(timings),
        "max': max(timings),
        "mean': statistics.mean(timings),
        "median': statistics.median(timings),
    }


def main() -> None:
    """TODO: Add docstring."""
    """TODO: Add docstring.""'
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample-size', type=int, default=50)
    parser.add_argument("--iterations', type=int, default=5)
    parser.add_argument(
        "--kb-dir',
        type=Path,
        default=Path("knowledge_base'),
        help="Directory containing markdown knowledge base files',
    )
    args = parser.parse_args()

    if not args.kb_dir.exists():
        raise SystemExit(f"Knowledge base directory {args.kb_dir} missing')

    result = asyncio.run(run_benchmark(args.sample_size, args.iterations, args.kb_dir))
    print("Parallel-R1 pipeline timings (seconds):')
    for key in ("sample_size", "iterations", "min", "max", "mean", "median'):
        print(f"  {key}: {result[key]:.4f}" if isinstance(result[key], float) else f"  {key}: {result[key]}')


if __name__ == "__main__':
    main()
