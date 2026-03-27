# File: scripts/smoke_test.py
from __future__ import annotations

import json
import traceback

from baseline import run_task
from grader import get_grader
from tasks import list_tasks


def _assert(condition: bool, message: str) -> None:
    """Tiny assert helper with readable errors."""
    if not condition:
        raise AssertionError(message)


def main() -> None:
    """
    Run a quick end-to-end sanity suite.

    Checks:
    1) task registry returns easy/medium/hard
    2) grader can score a minimal summary
    3) baseline run for easy task returns score in [0,1]
    """
    results: dict[str, str] = {}

    # 1) Task registry smoke check.
    tasks = list_tasks()
    task_ids = [t["task_id"] for t in tasks]
    _assert(task_ids == ["easy", "medium", "hard"], "Task registry order/content mismatch")
    results["tasks"] = "ok"

    # 2) Grader smoke check.
    grader = get_grader("easy")
    grade = grader.grade({"total_reward": 0.0, "max_days": 10, "days_elapsed": 10})
    _assert(0.0 <= grade.score <= 1.0, "Grader score out of [0,1]")
    results["grader"] = "ok"

    # 3) Baseline smoke check (single task for speed).
    baseline_output = run_task("easy", seed=42)
    score = float(baseline_output["score"])
    _assert(0.0 <= score <= 1.0, "Baseline score out of [0,1]")
    results["baseline_easy"] = "ok"

    print(json.dumps({"status": "ok", "checks": results}, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"status": "failed", "error": str(exc)}, indent=2))
        traceback.print_exc()
        raise

