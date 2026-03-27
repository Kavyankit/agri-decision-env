# File: tasks/medium_task.py
"""
Medium benchmark task definition.

This task has:
- moderate horizon
- more zones and metrics
- tighter but still manageable resources and noise
"""

from __future__ import annotations

from config import get_config
from models import Difficulty, EnvConfig

TASK_ID = "medium"


def build_task_config(seed: int | None = 42) -> EnvConfig:
    """Build the EnvConfig for the medium task."""
    if seed is not None and not isinstance(seed, int):
        raise TypeError("seed must be int or None")
    return get_config(Difficulty.MEDIUM, seed)


def describe_task(config: EnvConfig | None = None) -> dict:
    """Return a small metadata dictionary describing the medium task."""
    # Allow callers to pass a prebuilt config to avoid duplicate construction.
    if config is None:
        config = build_task_config()
    return {
        "task_id": TASK_ID,
        "difficulty": config.task.difficulty.value,
        "max_days": config.task.max_days,
        "zone_count": config.task.zone_count,
        "visible_metrics": config.task.visible_metrics,
        "description": "Balanced constraints and uncertainty for general evaluation.",
    }

