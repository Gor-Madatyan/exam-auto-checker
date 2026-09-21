"""Essay scoring endpoints (3 features)."""

from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING, cast

from fastapi import APIRouter, Depends

from .._helpers import ERROR_RESPONSES, call_jev
from ..schemas import (
    EssayCheckRequest,
    EssayChecks,
    EssayFullResponse,
    EssayScoreRequest,
    GradedScoreResponse,
)
from ..security import verify_api_key

if TYPE_CHECKING:
    from ...grading import GradedScore

router = APIRouter(
    prefix="/essay",
    tags=["essay"],
    dependencies=[Depends(verify_api_key)],
    responses=ERROR_RESPONSES,
)


@router.post(
    "/check",
    response_model=EssayChecks,
    summary="Essay raw checks",
    description="Score a student essay against the topic and requirements. Returns "
    "meets_requirements and grammatically_correct floats in [0, 1].",
)
async def check_essay_endpoint(body: EssayCheckRequest) -> EssayChecks:
    from ... import check_essay as _check_essay

    result = await call_jev(
        partial(
            _check_essay,
            student_essay=body.student_essay,
            topic=body.topic,
            requirements=body.requirements,
        )
    )
    return EssayChecks(**result)


@router.post(
    "/score",
    response_model=GradedScoreResponse,
    summary="Essay score in points",
    description="Grade a student essay directly to task points "
    "(discrete snap scaled to max_points).",
)
async def check_essay_score_endpoint(
    body: EssayScoreRequest,
) -> GradedScoreResponse:
    from ... import grade_essay_score as _grade_essay_score

    graded = await call_jev(
        partial(
            _grade_essay_score,
            student_essay=body.student_essay,
            topic=body.topic,
            requirements=body.requirements,
            max_points=body.max_points,
            num_levels=body.num_levels,
            mode=body.mode,
        )
    )
    return GradedScoreResponse.from_graded(graded)


@router.post(
    "/full",
    response_model=EssayFullResponse,
    summary="Essay checks + points",
    description="Essay checks plus point grading in one call.",
)
async def check_essay_full_endpoint(body: EssayScoreRequest) -> EssayFullResponse:
    from ... import grade_essay_full as _grade_essay_full

    result = await call_jev(
        partial(
            _grade_essay_full,
            student_essay=body.student_essay,
            topic=body.topic,
            requirements=body.requirements,
            max_points=body.max_points,
            num_levels=body.num_levels,
            mode=body.mode,
        )
    )
    return EssayFullResponse(
        checks=cast("dict[str, float]", result["checks"]),
        grading=GradedScoreResponse.from_graded(
            cast("GradedScore", result["grading"])
        ),
    )
