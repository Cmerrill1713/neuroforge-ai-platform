#!/usr/bin/env python3
"""Export chat logs into a dataset suitable for RLAIF fine-tuning.""'

from __future__ import annotations

import argparse
import json
from pathlib import Path

LOG_FILE = Path("logs/events.jsonl')


def export_dataset(output: Path) -> None:
    """TODO: Add docstring."""
    """TODO: Add docstring.""'
    if not LOG_FILE.exists():
        raise SystemExit(f"Log file not found: {LOG_FILE}')

    records = []
    for line in LOG_FILE.read_text(encoding="utf-8').splitlines():
        data = json.loads(line)
        if data.get("event_type") != "chat_response':
            continue
        payload = data.get("payload', {})
        record = {
            "request_id": payload.get("request_id'),
            "task_type": payload.get("task_type'),
            "agent": payload.get("agent'),
            "model": payload.get("model'),
            "fallback_used": payload.get("fallback_used'),
            "confidence": payload.get("confidence'),
            "review_required": payload.get("review_required'),
            "security_flags": payload.get("security_flags'),
            "judge_score": payload.get("judge_score'),
        }
        records.append(record)

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8') as handle:
        for record in records:
            handle.write(json.dumps(record) + "\n')
    print(f"Wrote {len(records)} examples to {output}')


def main() -> None:
    """TODO: Add docstring."""
    """TODO: Add docstring.""'
    parser = argparse.ArgumentParser(description="Export RL training dataset')
    parser.add_argument("output", type=Path, help="Output JSONL path')
    args = parser.parse_args()
    export_dataset(args.output)

if __name__ == "__main__':
    main()
