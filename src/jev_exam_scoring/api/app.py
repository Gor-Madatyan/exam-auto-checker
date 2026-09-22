"""FastAPI application factory — one endpoint per scoring feature."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .routers import code_router, essay_router, fact_router, pseudocode_router


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    # Startup / shutdown hooks will go here (clients, pools, etc.).
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "Automated exam scoring backed by the jev scoring backend "
            "(via OpenRouter). One endpoint group per scoring domain: code, "
            "essay, fact, pseudocode. Each domain exposes a single /check "
            "endpoint returning per-criterion noul floats in [0, 1], the "
            "derived 0-2 score (criteria joined with coefficients), and "
            "points_given. Every endpoint requires an X-API-Key header."
        ),
        openapi_tags=[
            {
                "name": "code",
                "description": "Source-code answer scoring (compiles/runs, algorithm, edge cases).",
            },
            {
                "name": "essay",
                "description": "Free-text essay scoring (requirements, grammar).",
            },
            {
                "name": "fact",
                "description": "Short factual-answer scoring, graded directly to points.",
            },
            {
                "name": "pseudocode",
                "description": "Pseudocode answer scoring (clarity, algorithm, edge cases).",
            },
        ],
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # One check endpoint per scoring domain (4 total: code, essay, fact, pseudocode).
    app.include_router(code_router, prefix=settings.api_prefix)
    app.include_router(essay_router, prefix=settings.api_prefix)
    app.include_router(fact_router, prefix=settings.api_prefix)
    app.include_router(pseudocode_router, prefix=settings.api_prefix)
    return app


app = create_app()
