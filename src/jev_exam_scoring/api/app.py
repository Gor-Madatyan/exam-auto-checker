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
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # One endpoint per scoring feature (8 total).
    app.include_router(code_router, prefix=settings.api_prefix)
    app.include_router(essay_router, prefix=settings.api_prefix)
    app.include_router(fact_router, prefix=settings.api_prefix)
    app.include_router(pseudocode_router, prefix=settings.api_prefix)
    return app


app = create_app()
