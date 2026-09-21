"""Shared helpers for routers (blocking jev calls -> threadpool, unified errors)."""

from __future__ import annotations

from collections.abc import Callable

import requests
from fastapi import HTTPException
from fastapi.concurrency import run_in_threadpool


async def call_jev[T](fn: Callable[[], T]) -> T:
    """Run a blocking scoring function without blocking the event loop."""
    try:
        return await run_in_threadpool(fn)
    except requests.RequestException as exc:
        raise HTTPException(
            status_code=502, detail=f"Scoring backend unavailable: {exc}"
        ) from exc
    except RuntimeError as exc:
        # e.g. OPENROUTER_API_KEY missing at import/call time
        raise HTTPException(status_code=500, detail=str(exc)) from exc
