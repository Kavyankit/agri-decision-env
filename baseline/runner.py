# File: baseline/runner.py
from __future__ import annotations

from baseline.heuristic_agent import HeuristicAgent
from env import AgriEnv
from grader import get_grader
from tasks import build_task_config


def _build_episode_summary(
    *,
    task_id: str,
    max_days: int,
    initial_budget: float,
    remaining_budget: float,
    days_elapsed: int,
    total_reward: float,
    overuse_penalty_total: float,
    total_actions: int,
    waste_actions: int,
    final_avg_degradation: float,
    final_avg_crop_health: float,
) -> dict:
    """Create the normalized summary dictionary consumed by graders."""
    return {
        "task_id": task_id,
        "max_days": max_days,
        "initial_budget": initial_budget,
        "remaining_budget": remaining_budget,
        "days_elapsed": days_elapsed,
        "total_reward": total_reward,
        "overuse_penalty_total": overuse_penalty_total,
        "total_actions": total_actions,
        "waste_actions": waste_actions,
        "final_avg_degradation": final_avg_degradation,
        "final_avg_crop_health": final_avg_crop_health,
    }


def run_task(task_id: str, seed: int | None = 42) -> dict:
    """
    Run one full baseline episode for a task and return grading output.

    Output keys:
    - task_id
    - episode_summary
    - score
    - subscores
    - explanation
    """
    config = build_task_config(task_id, seed=seed)
    env = AgriEnv(config)
    agent = HeuristicAgent()
    grader = get_grader(task_id)

    obs = env.reset()
    agent.reset()
    done = False

    total_reward = 0.0
    total_actions = 0
    waste_actions = 0
    overuse_penalty_total = 0.0

    while not done:
        action = agent.act(obs, max_actions_per_day=config.task.max_actions_per_day)
        total_actions += len(action.tasks)
        # Waste definition mirrors reward/grader assumptions:
        # intervention actions with non-positive amount contribute no value.
        waste_actions += sum(
            1
            for task in action.tasks
            if task.action_type.value in {"irrigate", "apply_input"} and task.amount <= 0.0
        )

        obs, reward, done, info = env.step(action)
        total_reward += float(reward)
        overuse_penalty_total += float(info.get("overuse_penalty_applied", 0.0))

    # Final hidden-state averages are used by current deterministic graders.
    zone_count = max(1, len(env.zones))
    final_avg_degradation = sum(z.degradation_level for z in env.zones) / zone_count
    final_avg_crop_health = sum(z.crop_health for z in env.zones) / zone_count

    episode_summary = _build_episode_summary(
        task_id=task_id,
        max_days=config.task.max_days,
        initial_budget=config.task.initial_budget,
        remaining_budget=env.remaining_budget,
        days_elapsed=env.day,
        total_reward=total_reward,
        overuse_penalty_total=overuse_penalty_total,
        total_actions=total_actions,
        waste_actions=waste_actions,
        final_avg_degradation=final_avg_degradation,
        final_avg_crop_health=final_avg_crop_health,
    )

    # Deterministic grader converts summary -> normalized score and explanation.
    grade = grader.grade(episode_summary)
    return {
        "task_id": task_id,
        "episode_summary": episode_summary,
        "score": grade.score,
        "subscores": grade.subscores,
        "explanation": grade.explanation,
    }


def run_all_tasks(seed: int | None = 42) -> list[dict]:
    """Run baseline episodes for easy/medium/hard and return result list."""
    results = []
    for task_id in ["easy", "medium", "hard"]:
        results.append(run_task(task_id, seed=seed))
    return results

