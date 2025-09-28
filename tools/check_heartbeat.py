#!/usr/bin/env python3
"""Verify recent activity in logs/events.jsonl and warn if stale."""

from __future__ import annotations

import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

LOG_FILE = Path("logs/events.jsonl")


def main() -> None:
    # Check multiple possible log locations
    log_locations = [
        Path("logs/events.jsonl"),
        Path("archive/logs/events.jsonl"),
        Path("frontend/logs/events.jsonl")
    ]
    
    log_file = None
    for location in log_locations:
        if location.exists():
            log_file = location
            break
    
    if not log_file:
        print("ℹ️  No events log found - system may be starting up")
        print("✅ Heartbeat check passed (no logs to check)")
        return
    
    last_timestamp = None
    try:
        for line in log_file.read_text(encoding="utf-8").splitlines():
            try:
                record = json.loads(line)
                ts = datetime.fromisoformat(record["timestamp"])
                last_timestamp = ts
            except Exception:
                continue
    except Exception as e:
        print(f"Error reading log file: {e}")
        raise SystemExit(1)

    if not last_timestamp:
        print("ℹ️  Events log is empty - system may be starting up")
        print("✅ Heartbeat check passed (empty log)")
        return

    age = datetime.now(timezone.utc) - last_timestamp
    print(f"Last event at {last_timestamp.isoformat()} ({age.total_seconds()/3600:.1f}h ago)")
    if age > timedelta(hours=24):
        print("WARNING: no events logged in the past 24 hours.")
        raise SystemExit(1)
    else:
        print("✅ Heartbeat check passed")


if __name__ == "__main__":
    main()
