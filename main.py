# File: main.py
from __future__ import annotations

import os

import uvicorn

from api import app


def main() -> None:
    """
    Run the FastAPI application for local/dev execution.

    Host and port are configurable through environment variables to simplify
    deployment on different platforms.
    """
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", "7860"))
    uvicorn.run("main:app", host=host, port=port, reload=False)


if __name__ == "__main__":
    main()

