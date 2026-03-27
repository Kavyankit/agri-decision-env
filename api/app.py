# File: api/app.py
from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from baseline import run_all_tasks, run_task
from grader import get_grader
from tasks import list_tasks

app = FastAPI(
    title="Agri Decision Environment API",
    description="Thin API wrappers around tasks, graders, and baseline runner.",
    version="0.1.0",
)


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
    """Simple health endpoint for local checks."""
    return {"status": "ok"}


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