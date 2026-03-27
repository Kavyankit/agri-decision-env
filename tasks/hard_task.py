# File: tasks/hard_task.py
"""
Hard benchmark task definition.

This task emphasizes:
- long horizon
- many zones and metrics
- strong resource pressure and higher noise
- scenarios where strategic sacrifice is often required
"""

from __future__ import annotations

from config import get_config
from models import Difficulty, EnvConfig

TASK_ID = "hard"


def build_task_config(seed: int | None = 42) -> EnvConfig:
    """Build the EnvConfig for the hard task."""
    if seed is not None and not isinstance(seed, int):
        raise TypeError("seed must be int or None")
    return get_config(Difficulty.HARD, seed)


def describe_task(config: EnvConfig | None = None) -> dict:
    """Return a small metadata dictionary describing the hard task."""
    # Allow callers to pass a prebuilt config to avoid duplicate construction.
    if config is None:
        config = build_task_config()
    return {
        "task_id": TASK_ID,
        "difficulty": config.task.difficulty.value,
        "max_days": config.task.max_days,
        "zone_count": config.task.zone_count,
        "visible_metrics": config.task.visible_metrics,
        "description": (
            "High-uncertainty, resource-tight setup that rewards prioritization and sacrifice."
        ),
    }

