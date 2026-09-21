"""Backend server entry point — start with ``uv run serve``.

Host/port/reload are configurable via CLI flags or env vars::

    uv run serve                       # 127.0.0.1:8000
    uv run serve --port 8080 --reload  # dev mode
    HOST=0.0.0.0 PORT=8000 uv run serve
"""

from __future__ import annotations

import argparse
import os

import uvicorn


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Start the jev-exam-scoring backend server.")
    parser.add_argument(
        "--host",
        default=os.getenv("HOST", "127.0.0.1"),
        help="Bind address (env: HOST, default: 127.0.0.1).",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("PORT", "8000")),
        help="Bind port (env: PORT, default: 8000).",
    )
    parser.add_argument(
        "--reload",
        action=argparse.BooleanOptionalAction,
        default=os.getenv("RELOAD", "").lower() in {"1", "true", "yes"},
        help="Enable auto-reload (env: RELOAD).",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    uvicorn.run(
        "jev_exam_scoring.api.app:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
    )


if __name__ == "__main__":
    main()
