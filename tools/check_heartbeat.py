#!/usr/bin/env python3
"""Verify recent activity in logs/events.jsonl and warn if stale."""

from __future__ import annotations

import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

LOG_FILE = Path("logs/events.jsonl")


def main() -> None:
    if not LOG_FILE.exists():
        print("No events log found.")
        raise SystemExit(1)

    last_timestamp = None
    for line in LOG_FILE.read_text(encoding="utf-8").splitlines():
        try:
            record = json.loads(line)
            ts = datetime.fromisoformat(record["timestamp"])
            last_timestamp = ts
        except Exception:
            continue

    if not last_timestamp:
        print("Events log is empty.")
        raise SystemExit(1)

    age = datetime.now(timezone.utc) - last_timestamp
    print(f"Last event at {last_timestamp.isoformat()} ({age.total_seconds()/3600:.1f}h ago)")
    if age > timedelta(hours=24):
        print("WARNING: no events logged in the past 24 hours.")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
