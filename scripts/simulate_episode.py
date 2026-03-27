# File: scripts/simulate_episode.py
from __future__ import annotations

import argparse
import json

from baseline import HeuristicAgent
from env import AgriEnv
from models import Action
from tasks import build_task_config


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
    args = parser.parse_args()

    config = build_task_config(args.task, seed=args.seed)
    env = AgriEnv(config)
    obs = env.reset()

    agent = HeuristicAgent()
    agent.reset()

    done = False
    total_reward = 0.0
    steps = 0

    while not done:
        if args.mode == "heuristic":
            action = agent.act(obs, max_actions_per_day=config.task.max_actions_per_day)
        else:
            action = Action(tasks=[])
        obs, reward, done, info = env.step(action)
        total_reward += float(reward)
        steps += 1

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
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()

