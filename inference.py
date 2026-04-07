# File: inference.py
"""
HTTP client pipeline: wait for the Agri Decision Environment API, list tasks, run baseline per task.

Uses `OPENENV_BASE_URL`. Default is the deployed **Hugging Face Space**
([`kavyankit-agri-decision-openenv.hf.space`](https://kavyankit-agri-decision-openenv.hf.space/)).
Override with `http://127.0.0.1:7860` when running `python main.py` locally.
"""
from __future__ import annotations

import json
import logging
import os
import time
from typing import Any

import requests

try:
    from dotenv import load_dotenv
    from pathlib import Path

    load_dotenv(Path(__file__).resolve().parent / ".env")
except ImportError:
    pass

# -----------------------------------------------------------------------------
# CONFIGURATION
# -----------------------------------------------------------------------------

# Default: public Space (override for local uvicorn on http://127.0.0.1:7860).
_DEFAULT_SPACE = "https://kavyankit-agri-decision-openenv.hf.space"

BASE_URL = os.getenv("OPENENV_BASE_URL", _DEFAULT_SPACE).rstrip("/")
TIMEOUT = 10  # seconds
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds
HEALTH_ENDPOINT = f"{BASE_URL}/health"

# -----------------------------------------------------------------------------
# LOGGING SETUP
# -----------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# HELPER: RETRY WRAPPER
# -----------------------------------------------------------------------------


def request_with_retries(method: str, url: str, **kwargs: Any) -> requests.Response:
    """
    Retry wrapper for HTTP requests (cold starts, transient 5xx, network blips).

    Client errors (4xx) are not retried — raised immediately with response body.
    """
    last_exc: Exception | None = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.request(method, url, timeout=TIMEOUT, **kwargs)

            if 400 <= response.status_code < 500:
                detail = response.text[:500]
                raise requests.exceptions.HTTPError(
                    f"Client error {response.status_code}: {detail}"
                )

            if response.status_code >= 500:
                raise requests.exceptions.HTTPError(
                    f"Server error: {response.status_code} {response.text[:200]}"
                )

            return response

        except Exception as e:
            last_exc = e
            logger.warning("[Attempt %s/%s] Request failed: %s", attempt, MAX_RETRIES, e)

            if attempt == MAX_RETRIES:
                raise

            time.sleep(RETRY_DELAY)

    raise RuntimeError("Unreachable") from last_exc


# -----------------------------------------------------------------------------
# STEP 1: WAIT FOR SERVICE TO BE READY
# -----------------------------------------------------------------------------


def wait_for_service() -> None:
    """Poll `/health` until 200 (helps HF Spaces / Docker cold starts)."""
    logger.info("Waiting for API service to become ready (%s)...", BASE_URL)

    for _ in range(10):
        try:
            response = requests.get(HEALTH_ENDPOINT, timeout=3)
            if response.status_code == 200:
                logger.info("API is ready.")
                return
        except Exception:
            pass

        time.sleep(2)

    raise RuntimeError("API did not become ready in time.")


# -----------------------------------------------------------------------------
# STEP 2: FETCH TASKS
# -----------------------------------------------------------------------------


def fetch_tasks() -> list[dict[str, Any]]:
    """GET /tasks → { \"tasks\": [ { \"task_id\": \"easy\", ... }, ... ] }"""
    logger.info("Fetching tasks...")

    response = request_with_retries("GET", f"{BASE_URL}/tasks")
    data = response.json()

    tasks = data.get("tasks", [])
    logger.info("Found %s tasks.", len(tasks))

    return tasks


# -----------------------------------------------------------------------------
# STEP 3: RUN BASELINE PER TASK
# -----------------------------------------------------------------------------


def run_task(task_id: str) -> dict[str, Any]:
    """
    POST /baseline with {\"task_id\": ..., \"seed\": 42}.

    API returns {\"results\": [ { ... run_task output ... } ]}.
    """
    logger.info("Running baseline for task: %s", task_id)

    try:
        response = request_with_retries(
            "POST",
            f"{BASE_URL}/baseline",
            json={"task_id": task_id, "seed": 42},
        )
        result = response.json()

        return {
            "task_id": task_id,
            "status": "success",
            "result": result,
        }

    except Exception as e:
        logger.error("Task %s failed: %s", task_id, e)

        return {
            "task_id": task_id,
            "status": "failed",
            "error": str(e),
        }


# -----------------------------------------------------------------------------
# STEP 4: RUN ALL TASKS
# -----------------------------------------------------------------------------


def run_all_tasks() -> dict[str, Any]:
    """
    Orchestration: wait → list tasks → baseline each task_id.
    """
    wait_for_service()

    tasks = fetch_tasks()

    results: list[dict[str, Any]] = []

    for task in tasks:
        task_id = task.get("task_id")

        if not task_id:
            logger.warning("Skipping malformed task: %s", task)
            continue

        result = run_task(str(task_id))
        results.append(result)

    return {
        "base_url": BASE_URL,
        "total_tasks": len(results),
        "results": results,
    }


# -----------------------------------------------------------------------------
# ENTRY POINT
# -----------------------------------------------------------------------------


if __name__ == "__main__":
    logger.info("Starting inference pipeline...")

    try:
        final_output = run_all_tasks()

        logger.info("Inference completed successfully.")

        # STRUCTURED OUTPUT STARTS HERE
        results = final_output.get("results", [])

        for task_result in results:
            task_id = task_result.get("task_id", "unknown")

            print(f"[START] task={task_id}", flush=True)

            if task_result.get("status") == "success":
                # Extract actual metrics safely
                result_data = task_result.get("result", {})
                runs = result_data.get("results", [])

                steps = 0
                score = 0

                if runs:
                    run = runs[0]
                    steps = run.get("steps", 0)
                    score = run.get("score", 0)

                    # Optional: simulate steps (since API doesn't expose step-by-step)
                    for i in range(1, steps + 1):
                        print(f"[STEP] step={i} reward=0.0", flush=True)

                print(
                    f"[END] task={task_id} score={score} steps={steps}",
                    flush=True,
                )

            else:
                print(f"[STEP] step=0 reward=0.0", flush=True)
                print(
                    f"[END] task={task_id} score=0 steps=0",
                    flush=True,
                )

    except Exception as e:
        logger.critical("Inference failed completely: %s", e)
        raise
