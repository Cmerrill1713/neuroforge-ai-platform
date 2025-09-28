"""Structured event logging for agent orchestration."""

from __future__ import annotations

import json
import os
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

_LOG_DIR = Path(os.getenv("AGENT_LOG_DIR", "logs"))
_LOG_DIR.mkdir(parents=True, exist_ok=True)
_LOG_FILE = _LOG_DIR / "events.jsonl"
_lock = threading.Lock()


def log_event(event_type: str, payload: Dict[str, Any]) -> None:
    """Append a structured event to the JSONL log."""
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,
        "payload": payload,
    }
    line = json.dumps(record, ensure_ascii=False)
    with _lock:
        with _LOG_FILE.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")

__all__ = ["log_event"]
