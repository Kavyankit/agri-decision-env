# File: scripts/check_submission.py
from __future__ import annotations

import json
import sys
from pathlib import Path

# Allow running this script directly from /scripts while importing project packages.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def _check_files(root: Path) -> list[str]:
    """Check presence of critical project files."""
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
        "requirements.txt",
        "Dockerfile",
        "openenv.yaml",
        "main.py",
    ]
    missing: list[str] = []
    for rel in required_paths:
        if not (root / rel).exists():
            missing.append(rel)
    return missing


def _check_runtime() -> list[str]:
    """
    Run small runtime checks expected before submission.

    Checks:
    - imports work
    - tasks load
    - env reset/step works
    - grader returns valid score
    - baseline runner works
    - api app import works
    """
    errors: list[str] = []
    try:
        from baseline import run_task
        from env import AgriEnv
        from grader import get_grader
        from models import Action
        from tasks import build_task_config, list_tasks
        from api import app as api_app
    except Exception as exc:  # noqa: BLE001
        return [f"import_failure: {exc}"]

    try:
        tasks = list_tasks()
        if [t["task_id"] for t in tasks] != ["easy", "medium", "hard"]:
            errors.append("task_registry_invalid")
    except Exception as exc:  # noqa: BLE001
        errors.append(f"tasks_load_failure: {exc}")

    try:
        config = build_task_config("easy", seed=42)
        env = AgriEnv(config)
        obs = env.reset()
        # one no-op step should run without errors
        _, _, _, _ = env.step(Action(tasks=[]))
        if obs.day != 0:
            errors.append("env_reset_observation_invalid")
    except Exception as exc:  # noqa: BLE001
        errors.append(f"env_runtime_failure: {exc}")

    try:
        grade = get_grader("easy").grade({"total_reward": 0.0, "max_days": 10, "days_elapsed": 10})
        if not (0.0 <= grade.score <= 1.0):
            errors.append("grader_score_out_of_range")
    except Exception as exc:  # noqa: BLE001
        errors.append(f"grader_failure: {exc}")

    try:
        baseline_result = run_task("easy", seed=42)
        if "score" not in baseline_result:
            errors.append("baseline_output_missing_score")
    except Exception as exc:  # noqa: BLE001
        errors.append(f"baseline_failure: {exc}")

    try:
        # Touch app object to ensure import produced a FastAPI instance-like object.
        _ = api_app.title
    except Exception as exc:  # noqa: BLE001
        errors.append(f"api_import_failure: {exc}")

    return errors


def main() -> None:
    """
    Validate expected project structure for current submission stage.

    This check combines:
    - file presence checks
    - lightweight runtime sanity checks
    """
    root = Path(__file__).resolve().parent.parent

    missing = _check_files(root)
    runtime_errors = _check_runtime()

    if missing or runtime_errors:
        print(
            json.dumps(
                {"status": "failed", "missing": missing, "runtime_errors": runtime_errors},
                indent=2,
            )
        )
        raise SystemExit(1)

    print(json.dumps({"status": "ok", "checked": "files+runtime"}, indent=2))


if __name__ == "__main__":
    main()

