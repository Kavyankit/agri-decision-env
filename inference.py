"""LLM agent runner for Agri Decision OpenEnv."""

from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path
from typing import Any

import requests
from openai import OpenAI

try:
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).resolve().parent / ".env")
except ImportError:
    pass

API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1").rstrip("/")
MODEL_NAME = os.getenv("MODEL_NAME", "openai/gpt-oss-120b:novita")
HF_TOKEN = os.getenv("HF_TOKEN")
LOCAL_IMAGE_NAME = os.getenv("LOCAL_IMAGE_NAME")
OPENENV_BASE_URL = os.getenv(
    "OPENENV_BASE_URL",
    "https://kavyankit-agri-decision-openenv.hf.space",
).rstrip("/")

SEED = int(os.getenv("SEED", "42"))
MAX_STEPS = int(os.getenv("MAX_STEPS", "40"))
MAX_COMPLETION_TOKENS = int(os.getenv("MAX_COMPLETION_TOKENS", "512"))
TIMEOUT = int(os.getenv("HTTP_TIMEOUT", "20"))
MAX_RETRIES = 3
RETRY_DELAY = 2
HEALTH_ENDPOINT = f"{OPENENV_BASE_URL}/health"
OPENAI_CLIENT: OpenAI | None = None

SYSTEM_PROMPT = """You are an autonomous farm operations agent.
Choose one-day actions from the observation.
Return only tool arguments for `submit_action`.
Allowed action_type: take_reading, apply_input, irrigate, wait.
Prefer safe actions and use take_reading on stale/uncertain zones.
Keep 1-3 tasks per step. If unsure, return a single wait action.
"""

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def request_with_retries(method: str, url: str, **kwargs: Any) -> requests.Response:
    last_exc: Exception | None = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.request(method, url, timeout=TIMEOUT, **kwargs)
            if 400 <= response.status_code < 500:
                raise requests.exceptions.HTTPError(
                    f"Client error {response.status_code}: {response.text[:400]}"
                )
            if response.status_code >= 500:
                raise requests.exceptions.HTTPError(
                    f"Server error {response.status_code}: {response.text[:400]}"
                )
            return response
        except Exception as exc:
            last_exc = exc
            logger.warning("[Attempt %s/%s] %s %s failed: %s", attempt, MAX_RETRIES, method, url, exc)
            if attempt == MAX_RETRIES:
                raise
            time.sleep(RETRY_DELAY)
    raise RuntimeError("Unreachable") from last_exc


def wait_for_service() -> None:
    logger.info("Waiting for API service at %s", OPENENV_BASE_URL)
    for _ in range(15):
        try:
            response = requests.get(HEALTH_ENDPOINT, timeout=3)
            if response.status_code == 200:
                logger.info("API is ready.")
                return
        except Exception:
            pass
        time.sleep(2)
    raise RuntimeError("API did not become ready in time.")


def fetch_tasks() -> list[dict[str, Any]]:
    response = request_with_retries("GET", f"{OPENENV_BASE_URL}/tasks")
    data = response.json()
    tasks = data.get("tasks", [])
    logger.info("Found %s tasks.", len(tasks))
    return tasks


def _fallback_action() -> dict[str, Any]:
    return {
        "tasks": [
            {
                "zone_id": 0,
                "action_type": "wait",
                "input_type": None,
                "amount": 0.0,
                "duration_hours": 0.0,
                "cost": 0.0,
            }
        ]
    }


def _extract_action_from_llm(message: Any) -> dict[str, Any]:
    if not getattr(message, "tool_calls", None):
        return _fallback_action()
    try:
        raw = message.tool_calls[0].function.arguments or "{}"
        parsed = json.loads(raw)
        if isinstance(parsed, dict) and isinstance(parsed.get("tasks"), list):
            return parsed
    except Exception:
        pass
    return _fallback_action()


def choose_action(task_id: str, observation: dict[str, Any], step_num: int, last_reward: float) -> dict[str, Any]:
    assert OPENAI_CLIENT is not None
    tools = [
        {
            "type": "function",
            "function": {
                "name": "submit_action",
                "description": "Return next /step action payload.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "tasks": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "zone_id": {"type": "integer"},
                                    "action_type": {
                                        "type": "string",
                                        "enum": ["take_reading", "apply_input", "irrigate", "wait"],
                                    },
                                    "input_type": {"type": ["string", "null"]},
                                    "amount": {"type": "number"},
                                    "duration_hours": {"type": "number"},
                                    "cost": {"type": "number"},
                                },
                                "required": [
                                    "zone_id",
                                    "action_type",
                                    "input_type",
                                    "amount",
                                    "duration_hours",
                                    "cost",
                                ],
                            },
                        }
                    },
                    "required": ["tasks"],
                },
            },
        }
    ]
    payload = {
        "task_id": task_id,
        "step": step_num,
        "last_reward": last_reward,
        "observation": observation,
    }
    response = OPENAI_CLIENT.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(payload)},
        ],
        tools=tools,
        tool_choice="required",
        max_completion_tokens=MAX_COMPLETION_TOKENS,
    )
    return _extract_action_from_llm(response.choices[0].message)


def _safe_average(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.5


def build_episode_summary(
    task: dict[str, Any],
    final_observation: dict[str, Any],
    days_elapsed: int,
    total_reward: float,
    overuse_penalty_total: float,
    total_actions: int,
    waste_actions: int,
) -> dict[str, Any]:
    zones = final_observation.get("zones", [])
    health_values = [z.get("crop_health") for z in zones if isinstance(z.get("crop_health"), (int, float))]

    degradation_values: list[float] = []
    for zone in zones:
        metrics = zone.get("observed_metrics", {})
        if not isinstance(metrics, dict):
            continue
        for key, value in metrics.items():
            if "degrad" in str(key).lower() and isinstance(value, (int, float)):
                degradation_values.append(float(value))

    remaining_budget = float(final_observation.get("remaining_budget", 0.0))
    initial_budget = float(task.get("initial_budget", max(remaining_budget, 1.0)))
    max_days = int(task.get("max_days", max(days_elapsed, 1)))

    return {
        "task_id": str(task.get("task_id", "unknown")),
        "max_days": max_days,
        "initial_budget": initial_budget,
        "remaining_budget": remaining_budget,
        "days_elapsed": max(days_elapsed, 1),
        "total_reward": float(total_reward),
        "overuse_penalty_total": float(overuse_penalty_total),
        "total_actions": int(max(total_actions, 1)),
        "waste_actions": int(max(waste_actions, 0)),
        "final_avg_degradation": float(min(max(_safe_average(degradation_values), 0.0), 1.0)),
        "final_avg_crop_health": float(min(max(_safe_average(health_values), 0.0), 1.0)),
    }


def grade_episode(task_id: str, episode_summary: dict[str, Any]) -> dict[str, Any]:
    response = request_with_retries(
        "POST",
        f"{OPENENV_BASE_URL}/grader",
        json={"task_id": task_id, "episode_summary": episode_summary},
    )
    return response.json()


def run_task(task: dict[str, Any]) -> dict[str, Any]:
    task_id = str(task.get("task_id", "unknown"))
    print(f"[START] task={task_id}", flush=True)

    reset_resp = request_with_retries(
        "POST",
        f"{OPENENV_BASE_URL}/reset",
        params={"task_id": task_id, "seed": SEED},
    ).json()

    observation = reset_resp.get("observation", {})
    done = False
    step_count = 0
    total_reward = 0.0
    last_reward = 0.0
    overuse_penalty_total = 0.0
    total_actions = 0
    waste_actions = 0

    while not done and step_count < MAX_STEPS:
        step_count += 1
        action = choose_action(task_id, observation, step_count, last_reward)
        task_actions = action.get("tasks", [])

        total_actions += len(task_actions)
        waste_actions += sum(
            1
            for t in task_actions
            if str(t.get("action_type", "")).lower() in {"irrigate", "apply_input"}
            and float(t.get("amount", 0.0)) <= 0.0
        )

        step_resp = request_with_retries(
            "POST",
            f"{OPENENV_BASE_URL}/step",
            json={"tasks": task_actions},
        ).json()

        observation = step_resp.get("observation", {})
        reward = float(step_resp.get("reward", 0.0))
        done = bool(step_resp.get("done", False))
        info = step_resp.get("info", {})

        if isinstance(info, dict):
            overuse_penalty_total += float(info.get("overuse_penalty_applied", 0.0))

        total_reward += reward
        last_reward = reward
        print(f"[STEP] step={step_count} reward={reward}", flush=True)

    episode_summary = build_episode_summary(
        task=task,
        final_observation=observation,
        days_elapsed=step_count,
        total_reward=total_reward,
        overuse_penalty_total=overuse_penalty_total,
        total_actions=total_actions,
        waste_actions=waste_actions,
    )
    grade = grade_episode(task_id, episode_summary)
    score = float(grade.get("score", 0.0))
    print(f"[END] task={task_id} score={score} steps={step_count}", flush=True)

    return {
        "task_id": task_id,
        "steps": step_count,
        "score": score,
        "grade": grade,
        "episode_summary": episode_summary,
    }


def run_all_tasks() -> dict[str, Any]:
    wait_for_service()
    tasks = fetch_tasks()
    results: list[dict[str, Any]] = []
    for task in tasks:
        task_id = task.get("task_id")
        if not task_id:
            logger.warning("Skipping malformed task: %s", task)
            continue
        results.append(run_task(task))

    return {
        "base_url": OPENENV_BASE_URL,
        "total_tasks": len(results),
        "results": results,
    }


if __name__ == "__main__":
    logger.info("Starting LLM agent inference...")
    logger.info("API_BASE_URL=%s", API_BASE_URL)
    logger.info("MODEL_NAME=%s", MODEL_NAME)
    logger.info("HF_TOKEN set=%s", bool(HF_TOKEN))
    logger.info("LOCAL_IMAGE_NAME=%s", LOCAL_IMAGE_NAME or "")
    if not HF_TOKEN:
        raise SystemExit("HF_TOKEN is required for LLM agent mode.")

    OPENAI_CLIENT = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)
    logger.info("OpenAI client initialized=%s", OPENAI_CLIENT is not None)

    try:
        final_output = run_all_tasks()
        logger.info("Completed %s tasks.", final_output.get("total_tasks", 0))
    except Exception as exc:
        logger.critical("Inference failed completely: %s", exc)
        raise
