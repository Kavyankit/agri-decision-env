# File: tasks/__init__.py
"""
Public entry points for benchmark tasks.

These helpers are intentionally simple so they can be:
- imported by baseline agents
- wired into an API layer
- or used by local CLI utilities
"""

from .easy_task import TASK_ID as EASY_TASK_ID, build_task_config as build_easy_config
from .hard_task import TASK_ID as HARD_TASK_ID, build_task_config as build_hard_config
from .medium_task import TASK_ID as MEDIUM_TASK_ID, build_task_config as build_medium_config
from .task_registry import build_task_config, get_task_builder, list_tasks

__all__ = [
    "EASY_TASK_ID",
    "MEDIUM_TASK_ID",
    "HARD_TASK_ID",
    "build_easy_config",
    "build_medium_config",
    "build_hard_config",
    "list_tasks",
    "get_task_builder",
    "build_task_config",
]

