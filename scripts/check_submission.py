# File: scripts/check_submission.py
from __future__ import annotations

import json
from pathlib import Path


def main() -> None:
    """
    Validate expected project structure for current submission stage.

    This is a lightweight file-presence check to catch missing critical modules.
    """
    root = Path(__file__).resolve().parent.parent
    required_paths = [
        "README.md",
        "docs/03_prd_hld.md",
        "env/environment.py",
        "env/reward_engine.py",
        "tasks/task_registry.py",
        "grader/grader_factory.py",
        "baseline/runner.py",
        "api/app.py",
        "scripts/smoke_test.py",
        "scripts/run_baseline.py",
        "scripts/simulate_episode.py",
    ]

    missing: list[str] = []
    for rel in required_paths:
        if not (root / rel).exists():
            missing.append(rel)

    if missing:
        print(json.dumps({"status": "failed", "missing": missing}, indent=2))
        raise SystemExit(1)

    print(json.dumps({"status": "ok", "checked": required_paths}, indent=2))


if __name__ == "__main__":
    main()

