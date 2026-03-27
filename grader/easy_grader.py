# File: grader/easy_grader.py
from __future__ import annotations

from grader.base_grader import BaseGrader


class EasyGrader(BaseGrader):
    """
    Easy-task grader.

    Easy mode rewards successful outcomes most, while still encouraging
    basic efficiency and clean action discipline.
    """

    COMPONENT_WEIGHTS = {
        "outcome": 0.45,
        "efficiency": 0.25,
        "sustainability": 0.20,
        "discipline": 0.10,
    }

