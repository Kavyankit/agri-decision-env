# File: scripts/simulate_episode.py
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Allow running this script directly from /scripts while importing project packages.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from baseline import HeuristicAgent
from env import AgriEnv
from models import Action
from models.action_models import TaskAction
from tasks import build_task_config


def _task_line(task: TaskAction) -> str:
    """One-line summary of a single task for text transcripts."""
    parts = [task.action_type.value, f"z{task.zone_id}"]
    if task.amount:
        parts.append(f"amt={task.amount:.3g}")
    if task.input_type:
        parts.append(f"in={task.input_type}")
    return " ".join(parts)


def main() -> None:
    """
    Simulate one episode and print a compact trace summary.

    Modes:
    - heuristic: uses HeuristicAgent decisions each step
    - noop: sends empty actions each step
    """
    parser = argparse.ArgumentParser(description="Simulate one environment episode.")
    parser.add_argument("--task", type=str, default="easy", help="easy | medium | hard")
    parser.add_argument("--seed", type=int, default=42, help="Deterministic task seed.")
    parser.add_argument(
        "--mode",
        type=str,
        choices=["heuristic", "noop"],
        default="heuristic",
        help="Action mode per step.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Include per-step trace (actions, reward, key info) in JSON output.",
    )
    parser.add_argument(
        "--format",
        type=str,
        choices=["json", "text"],
        default="json",
        help="json: one JSON object. text: day-by-day transcript (good for copy-paste).",
    )
    args = parser.parse_args()

    config = build_task_config(args.task, seed=args.seed)
    env = AgriEnv(config)
    obs = env.reset()

    agent = HeuristicAgent()
    agent.reset()

    done = False
    total_reward = 0.0
    steps = 0
    trace: list[dict] = []

    while not done:
        if args.mode == "heuristic":
            action = agent.act(obs, max_actions_per_day=config.task.max_actions_per_day)
        else:
            action = Action(tasks=[])
        obs, reward, done, info = env.step(action)
        total_reward += float(reward)
        steps += 1

        if args.verbose or args.format == "text":
            rb = info.get("reward_breakdown") or {}
            trace.append(
                {
                    "step": steps,
                    "day_after": obs.day,
                    "action": action.model_dump(mode="json"),
                    "reward": float(reward),
                    "spent_budget": info.get("spent_budget"),
                    "spent_time": info.get("spent_time"),
                    "travel_time_spent": info.get("travel_time_spent"),
                    "actions_count": info.get("actions_count"),
                    "reward_breakdown": rb,
                }
            )

    final_state = env.state()
    output = {
        "task_id": args.task,
        "seed": args.seed,
        "mode": args.mode,
        "steps": steps,
        "total_reward": total_reward,
        "final_state": final_state,
        "last_info_phase": env.history[-1]["phase"] if env.history else None,
    }
    if args.verbose:
        output["trace"] = trace

    if args.format == "text":
        lines = [
            f"=== Heuristic episode | task={args.task} seed={args.seed} mode={args.mode} ===",
            f"max_days={config.task.max_days} zones={config.task.zone_count}",
            "",
        ]
        for row in trace:
            day = row["day_after"]
            r = row["reward"]
            tasks = row["action"].get("tasks") or []
            if tasks:
                desc = "; ".join(
                    _task_line(TaskAction.model_validate(t)) for t in tasks
                )
            else:
                desc = "(no tasks)"
            rb = row.get("reward_breakdown") or {}
            total_rb = rb.get("total")
            lines.append(
                f"Day {day:>2} | reward {r:+.6f} | rb_total {total_rb} | "
                f"budget {row.get('spent_budget')} time {row.get('spent_time')} travel {row.get('travel_time_spent')}"
            )
            lines.append(f"         | {desc}")
            lines.append("")
        lines.append(f"--- total_reward={total_reward:.6f} steps={steps} ---")
        print("\n".join(lines))
    else:
        print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()

