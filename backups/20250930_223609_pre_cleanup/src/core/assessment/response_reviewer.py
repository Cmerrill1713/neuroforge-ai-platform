"""Lightweight post-response assessment to flag low confidence outputs."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class ReviewResult:
    """
    """
    score: float
    requires_human_review: bool
    reasons: Dict[str, Any]


def evaluate_response(*, confidence: float, fallback_used: bool, security_flags: int) -> ReviewResult:
    """
    """
    score = confidence
    reasons: Dict[str, Any] = {
        "confidence": confidence,
        "fallback_used": fallback_used,
        "security_flags": security_flags,
    }
    requires_review = fallback_used or confidence < 0.6 or security_flags > 0
    return ReviewResult(score=score, requires_human_review=requires_review, reasons=reasons)

__all__ = ["evaluate_response", "ReviewResult"]
