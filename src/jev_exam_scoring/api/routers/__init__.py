"""Routers package — one router per scoring domain."""

from .code import router as code_router
from .essay import router as essay_router
from .fact import router as fact_router
from .pseudocode import router as pseudocode_router

__all__ = ["code_router", "essay_router", "fact_router", "pseudocode_router"]
