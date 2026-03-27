# File: scripts/run_baseline.py
from __future__ import annotations

import argparse
import json

from baseline import run_all_tasks, run_task


def main() -> None:
    """Run baseline episodes and print compact JSON output."""
    parser = argparse.ArgumentParser(description="Run heuristic baseline.")
    parser.add_argument(
        "--task",
        type=str,
        default=None,
        help="Optional task id: easy | medium | hard (default: run all).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Deterministic seed used for task config generation.",
    )
    args = parser.parse_args()

    if args.task:
        result = {"results": [run_task(args.task, seed=args.seed)]}
    else:
        result = {"results": run_all_tasks(seed=args.seed)}

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

