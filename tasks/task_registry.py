# File: tasks/task_registry.py
"""
Task registry for the benchmark.

Phase 9 goal:
- expose easy / medium / hard as explicit tasks
- provide a simple way to list tasks and build configs by ID
"""

from __future__ import annotations

from typing import Callable

from models import EnvConfig
from tasks import easy_task, hard_task, medium_task

# Mapping from task_id string to its module.
_TASK_MODULES = {
    easy_task.TASK_ID: easy_task,
    medium_task.TASK_ID: medium_task,
    hard_task.TASK_ID: hard_task,
}


def list_tasks() -> list[dict]:
    """
    Return lightweight metadata for all registered tasks.

    Each entry comes from that task's `describe_task()` helper.
    """

    # Keep ordering explicit for predictable UX in CLI/API outputs.
    ordered_ids = [easy_task.TASK_ID, medium_task.TASK_ID, hard_task.TASK_ID]
    return [_TASK_MODULES[task_id].describe_task() for task_id in ordered_ids]


def get_task_builder(task_id: str) -> Callable[[int | None], EnvConfig]:
    """
    Return the `build_task_config(seed)` function for the requested task.

    This can be used by:
    - baselines
    - graders
    - API routes
    """

    if task_id not in _TASK_MODULES:
        raise KeyError(f"Unknown task_id: {task_id!r}")
    return _TASK_MODULES[task_id].build_task_config


def build_task_config(task_id: str, seed: int | None = 42) -> EnvConfig:
    """Convenience helper: build an EnvConfig directly by task_id."""
    builder = get_task_builder(task_id)
    return builder(seed)

