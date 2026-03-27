# File: tasks/easy_task.py
"""
Easy benchmark task definition.

This module describes the easiest version of the environment:
- short horizon
- few zones and metrics
- generous resources and low noise
"""

from __future__ import annotations

from config import get_config
from models import Difficulty, EnvConfig

# Public identifier for this task.
TASK_ID = "easy"


def build_task_config(seed: int | None = 42) -> EnvConfig:
    """
    Build the EnvConfig for the easy task.

    Callers can override `seed` to get different but reproducible instances.
    """

    if seed is not None and not isinstance(seed, int):
        raise TypeError("seed must be int or None")
    return get_config(Difficulty.EASY, seed)


def describe_task(config: EnvConfig | None = None) -> dict:
    """
    Return a small, beginner-friendly metadata dictionary for this task.

    This is intentionally simple so it can be used by:
    - a CLI script
    - a baseline agent
    - or a future API layer
    """

    # Allow callers to pass a prebuilt config to avoid duplicate construction.
    if config is None:
        config = build_task_config()
    return {
        "task_id": TASK_ID,
        "difficulty": config.task.difficulty.value,
        "max_days": config.task.max_days,
        "zone_count": config.task.zone_count,
        "visible_metrics": config.task.visible_metrics,
        "description": "Low-noise, high-resource configuration for baseline learning.",
    }

