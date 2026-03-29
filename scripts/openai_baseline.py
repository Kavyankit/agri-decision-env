# File: scripts/openai_baseline.py
"""
Submission helper: uses the official OpenAI Python client (required key) and calls the
running API's `/tasks` and `/baseline` endpoints.

Start the server first (`python main.py` or Docker on port 7860), then:

  set OPENAI_API_KEY=sk-...    # Windows: set OPENAI_API_KEY=sk-...
  python scripts/openai_baseline.py

Optional: `OPENENV_BASE_URL` (defaults to the deployed HF Space; use `http://127.0.0.1:7860` for local `main.py`).
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request
from pathlib import Path

# Allow running from /scripts with project imports if extended later.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from dotenv import load_dotenv

    load_dotenv(PROJECT_ROOT / ".env")
except ImportError:
    pass


def _http_json(method: str, url: str, body: dict | None = None, timeout: int = 300) -> dict:
    data = None if body is None else json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method=method,
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main() -> None:
    """Initialize OpenAI client (submission compliance), then query local/OpenEnv API."""
    if not os.environ.get("OPENAI_API_KEY"):
        print("Error: Set OPENAI_API_KEY (e.g. export OPENAI_API_KEY=sk-...)")
        raise SystemExit(1)

    try:
        # OpenAI client present (hackathon / OpenEnv spec requirement).
        from openai import OpenAI

        _client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

        _default_space = "https://kavyankit-agri-decision-openenv.hf.space"
        base = os.environ.get("OPENENV_BASE_URL", _default_space).rstrip("/")

        tasks = _http_json("GET", f"{base}/tasks")
        baseline = _http_json("POST", f"{base}/baseline", {"seed": 42})

        out = {
            "openai_client": "initialized",
            "tasks_response": tasks,
            "baseline_results": baseline,
        }
        print("Connected to OpenAI client and OpenEnv API")
        print(json.dumps(out, indent=2))
    except Exception as e:
        print("Error:", e)
        raise SystemExit(1) from e


if __name__ == "__main__":
    main()
