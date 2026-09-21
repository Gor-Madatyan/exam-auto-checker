"""API-key guard — every scoring endpoint requires a valid X-API-Key header."""

from __future__ import annotations

import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader

from .config import get_settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(
    provided: str | None = Depends(api_key_header),
) -> str:
    """Reject requests without the configured backend API key.

    Fail-closed: if the server itself has no API_KEY configured, every
    request is denied with 500 instead of silently running unprotected.
    """
    expected = get_settings().api_key
    if not expected:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server misconfigured: API_KEY is not set.",
        )
    if not provided or not secrets.compare_digest(provided, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key.",
        )
    return provided
