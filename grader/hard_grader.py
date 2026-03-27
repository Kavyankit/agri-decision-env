# File: grader/hard_grader.py
from __future__ import annotations

from grader.base_grader import BaseGrader


class HardGrader(BaseGrader):
    """
    Hard-task grader.

    Hard mode emphasizes sustainability and disciplined behavior under
    high uncertainty and tight resources, not only raw outcome.
    """

    COMPONENT_WEIGHTS = {
        "outcome": 0.25,
        "efficiency": 0.20,
        "sustainability": 0.35,
        "discipline": 0.20,
    }

