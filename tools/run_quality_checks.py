#!/usr/bin/env python3
"""Run basic quality checks: diff summary, lint, and tests."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run(cmd: list[str], cwd: Path | None = None) -> int:
    print("\n$", " ".join(cmd))
    try:
        result = subprocess.run(cmd, cwd=cwd or ROOT, check=False)
        return result.returncode
    except FileNotFoundError:
        print(f"Command not found: {cmd[0]}")
        return 127


def main() -> None:
    failures = 0

    # Show current diff stats
    run(["git", "diff", "--stat"], cwd=ROOT)

    # Backend lint (ruff if available)
    failures += run(["ruff", "check", "src"], cwd=ROOT) not in (0, 127)

    # Backend tests
    failures += run(["pytest"], cwd=ROOT) not in (0, 127)

    # Frontend lint
    frontend = ROOT / "frontend"
    if frontend.exists():
        failures += run(["npm", "run", "lint"], cwd=frontend) not in (0, 127)

    if failures:
        sys.exit("One or more checks failed. See output above.")


if __name__ == "__main__":
    main()
