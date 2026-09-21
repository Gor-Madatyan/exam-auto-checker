"""Pseudocode scoring endpoints (3 features)."""

from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING, cast

from fastapi import APIRouter, Depends

from .._helpers import call_jev
from ..schemas import (
    GradedScoreResponse,
    PseudocodeCheckRequest,
    PseudocodeChecks,
    PseudocodeFullResponse,
    PseudocodeScoreRequest,
)
from ..security import verify_api_key

if TYPE_CHECKING:
    from ...grading import GradedScore

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
    response_model=GradedScoreResponse,
    summary="Pseudocode score in points",
)
async def check_pseudocode_score_endpoint(
    body: PseudocodeScoreRequest,
) -> GradedScoreResponse:
    from ... import grade_pseudocode_score as _grade_pseudocode_score

    graded = await call_jev(
        partial(
            _grade_pseudocode_score,
            student_pseudocode=body.student_pseudocode,
            correct_pseudocode=body.correct_pseudocode,
            question_description=body.question_description,
            max_points=body.max_points,
            num_levels=body.num_levels,
            mode=body.mode,
        )
    )
    return GradedScoreResponse.from_graded(graded)


@router.post(
    "/full",
    response_model=PseudocodeFullResponse,
    summary="Pseudocode checks + points",
)
async def check_pseudocode_full_endpoint(
    body: PseudocodeScoreRequest,
) -> PseudocodeFullResponse:
    from ... import grade_pseudocode_full as _grade_pseudocode_full

    result = await call_jev(
        partial(
            _grade_pseudocode_full,
            student_pseudocode=body.student_pseudocode,
            correct_pseudocode=body.correct_pseudocode,
            question_description=body.question_description,
            max_points=body.max_points,
            num_levels=body.num_levels,
            mode=body.mode,
        )
    )
    return PseudocodeFullResponse(
        checks=cast("dict[str, float]", result["checks"]),
        grading=GradedScoreResponse.from_graded(
            cast("GradedScore", result["grading"])
        ),
    )
