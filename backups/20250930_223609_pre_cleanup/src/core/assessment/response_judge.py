"""Lightweight heuristic judge that scores assistant responses."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass
class JudgeResult:
    """
    """
    score: float
    reasons: Dict[str, float]


def judge_response(*, fallback_used: bool, review_required: bool, security_flags: int, confidence: float, response: str) -> JudgeResult:
    """
    """
    reasons: Dict[str, float] = {}
    score = confidence

    if fallback_used:
        reasons["fallback_penalty"] = -0.3
        score *= 0.6
    if review_required:
        reasons["review_penalty"] = -0.2
        score *= 0.7
    if security_flags:
        reasons["security_penalty"] = -0.5 * security_flags
        score *= 0.4
    if len(response.strip()) < 10:
        reasons["length_penalty"] = -0.1
        score *= 0.8

    score = max(0.0, min(score, 1.0))
    reasons["final_score"] = score
    return JudgeResult(score=score, reasons=reasons)

__all__ = ["judge_response", "JudgeResult"]
