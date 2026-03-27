# File: tests/test_smoke.py
from __future__ import annotations

import unittest

from baseline import run_task
from grader import get_grader
from tasks import list_tasks


class SmokeTests(unittest.TestCase):
    """Small but meaningful smoke tests for core public entry points."""

    def test_task_registry_order_and_ids(self) -> None:
        tasks = list_tasks()
        ids = [t["task_id"] for t in tasks]
        self.assertEqual(ids, ["easy", "medium", "hard"])

    def test_grader_score_range(self) -> None:
        grader = get_grader("medium")
        grade = grader.grade({"total_reward": 0.0, "max_days": 14, "days_elapsed": 14})
        self.assertGreaterEqual(grade.score, 0.0)
        self.assertLessEqual(grade.score, 1.0)

    def test_baseline_easy_runs(self) -> None:
        result = run_task("easy", seed=42)
        self.assertIn("score", result)
        self.assertIn("episode_summary", result)
        self.assertGreaterEqual(float(result["score"]), 0.0)
        self.assertLessEqual(float(result["score"]), 1.0)


if __name__ == "__main__":
    unittest.main()

