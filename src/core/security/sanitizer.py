"""Input sanitization and basic prompt-injection guards."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List

_SUSPICIOUS_PATTERNS = [
    r"rm\s+-rf",
    r"sudo\s+",
    r"curl\s+http",
    r"wget\s+http",
    r";\s*rm",
    r"\bshutdown\b",
    r"exec\s*\(",
]

@dataclass
class SanitizedInput:
    text: str
    flags: List[str]


def sanitize_user_text(text: str) -> SanitizedInput:
    """Return the text unchanged but flag obvious dangerous patterns."""
    lowered = text.lower()
    flags: List[str] = []
    for pattern in _SUSPICIOUS_PATTERNS:
        if re.search(pattern, lowered):
            flags.append(pattern)
    return SanitizedInput(text=text, flags=flags)

__all__ = ["sanitize_user_text", "SanitizedInput"]
