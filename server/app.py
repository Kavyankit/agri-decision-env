# File: server/app.py
from __future__ import annotations

import os

from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field

from baseline import run_all_tasks, run_task
from env import AgriEnv
from grader import get_grader
from models import Action
from tasks import build_task_config, list_tasks

app = FastAPI(
    title="Agri Decision Environment API",
    description="Thin API wrappers around tasks, graders, and baseline runner.",
    version="0.1.0",
)

# Interactive OpenEnv-style loop: call `/reset` before `/step` (single global episode).
_interactive_env: AgriEnv | None = None


class GraderRequest(BaseModel):
    """Input payload for `/grader` endpoint."""
    task_id: str = Field(description="easy | medium | hard")
    episode_summary: dict = Field(default_factory=dict)


class BaselineRequest(BaseModel):
    """Input payload for `/baseline` endpoint."""
    task_id: str | None = Field(default=None, description="If omitted, run all tasks.")
    seed: int | None = 42


@app.get("/health")
def health() -> dict:
    """Health check for OpenEnv / deployment probes."""
    return {"status": "healthy"}


@app.post("/reset")
def reset(task_id: str = "easy", seed: int = 42) -> dict:
    """
    Start or restart one interactive episode (OpenEnv-style loop).

    Builds `AgriEnv` from `task_id` + `seed`, then returns the initial observation.
    """
    global _interactive_env
    try:
        config = build_task_config(task_id, seed=seed)
    except KeyError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    _interactive_env = AgriEnv(config)
    obs = _interactive_env.reset()
    return {"observation": obs.model_dump()}


@app.post("/step")
def step(action: Action) -> dict:
    """Advance the environment one day. Call `/reset` first."""
    if _interactive_env is None:
        raise HTTPException(status_code=400, detail="Call POST /reset before /step.")
    obs, reward, done, info = _interactive_env.step(action)
    return {
        "observation": obs.model_dump(),
        "reward": float(reward),
        "done": bool(done),
        "info": jsonable_encoder(info),
    }


@app.get("/state")
def interactive_state() -> dict:
    """Return internal debug state from the running interactive env (call `/reset` first)."""
    if _interactive_env is None:
        raise HTTPException(status_code=400, detail="Call POST /reset before /state.")
    return {"state": jsonable_encoder(_interactive_env.state())}


@app.get("/tasks")
def get_tasks() -> dict:
    """
    Return benchmark task metadata.

    Thin wrapper over `tasks.list_tasks()`.
    """
    return {"tasks": list_tasks()}


@app.post("/grader")
def grade_episode(payload: GraderRequest) -> dict:
    """
    Grade one episode summary for the requested task.

    Thin wrapper over `grader.get_grader(...).grade(...)`.
    """
    try:
        grader = get_grader(payload.task_id)
    except KeyError as exc:
        # Convert domain lookup errors into clear API-level client errors.
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    grade = grader.grade(payload.episode_summary)
    return {
        "task_id": payload.task_id,
        "score": grade.score,
        "subscores": grade.subscores,
        "explanation": grade.explanation,
    }


@app.post("/baseline")
def run_baseline(payload: BaselineRequest) -> dict:
    """
    Run deterministic baseline and return episode + grading output.

    - If `task_id` is provided: run a single task.
    - Otherwise run easy/medium/hard.
    """
    try:
        if payload.task_id:
            return {"results": [run_task(payload.task_id, seed=payload.seed)]}
        return {"results": run_all_tasks(seed=payload.seed)}
    except KeyError as exc:
        # Keep API contract consistent: invalid task IDs return HTTP 400.
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/")
def root():
    return {"message": "Agri Decision OpenEnv running 🚀"}


def main() -> None:
    """Run uvicorn for local / `python -m server` (OpenEnv-compatible entry)."""
    import uvicorn

    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", os.getenv("PORT", "7860")))
    uvicorn.run("server.app:app", host=host, port=port, reload=False)


if __name__ == "__main__":
    main()
