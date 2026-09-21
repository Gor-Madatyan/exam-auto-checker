"""Pseudocode scoring endpoints (3 features)."""

from __future__ import annotations

from functools import partial
from typing import cast

from fastapi import APIRouter, Depends

from .._helpers import call_jev
from ..schemas import (
    PseudocodeCheckRequest,
    PseudocodeChecks,
    PseudocodeFullResponse,
    PseudocodeScoreResponse,
)
from ..security import verify_api_key

router = APIRouter(
    prefix="/pseudocode",
    tags=["pseudocode"],
    dependencies=[Depends(verify_api_key)],
)


@router.post(
    "/check", response_model=PseudocodeChecks, summary="Pseudocode noul checks"
)
async def check_pseudocode_endpoint(body: PseudocodeCheckRequest) -> PseudocodeChecks:
    from ... import check_pseudocode as _check_pseudocode

    result = await call_jev(
        partial(
            _check_pseudocode,
            student_pseudocode=body.student_pseudocode,
            correct_pseudocode=body.correct_pseudocode,
            question_description=body.question_description,
        )
    )
    return PseudocodeChecks(**result)


@router.post(
    "/score",
    response_model=PseudocodeScoreResponse,
    summary="Pseudocode 0-2 score",
)
async def check_pseudocode_score_endpoint(
    body: PseudocodeCheckRequest,
) -> PseudocodeScoreResponse:
    from ... import check_pseudocode_score as _check_pseudocode_score

    score = await call_jev(
        partial(
            _check_pseudocode_score,
            student_pseudocode=body.student_pseudocode,
            correct_pseudocode=body.correct_pseudocode,
            question_description=body.question_description,
        )
    )
    return PseudocodeScoreResponse(score=score)


@router.post(
    "/full",
    response_model=PseudocodeFullResponse,
    summary="Pseudocode checks + score",
)
async def check_pseudocode_full_endpoint(
    body: PseudocodeCheckRequest,
) -> PseudocodeFullResponse:
    from ... import check_pseudocode_full as _check_pseudocode_full

    result = await call_jev(
        partial(
            _check_pseudocode_full,
            student_pseudocode=body.student_pseudocode,
            correct_pseudocode=body.correct_pseudocode,
            question_description=body.question_description,
        )
    )
    return PseudocodeFullResponse(
        checks=cast("dict[str, float]", result["checks"]),
        score=cast(float, result["score"]),
    )
