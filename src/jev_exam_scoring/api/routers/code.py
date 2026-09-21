"""Code scoring endpoints (3 features)."""

from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING, cast

from fastapi import APIRouter, Depends

from .._helpers import ERROR_RESPONSES, call_jev
from ..schemas import (
    CodeCheckRequest,
    CodeChecks,
    CodeFullResponse,
    CodeScoreRequest,
    GradedScoreResponse,
)
from ..security import verify_api_key

if TYPE_CHECKING:
    from ...grading import GradedScore

router = APIRouter(
    prefix="/code",
    tags=["code"],
    dependencies=[Depends(verify_api_key)],
    responses=ERROR_RESPONSES,
)


@router.post(
    "/check",
    response_model=CodeChecks,
    summary="Code raw checks",
    description="Score student source code against a reference solution. Returns "
    "per-criterion floats in [0, 1]: compiles_and_runs, correct_algorithm, "
    "handles_edge_cases.",
)
async def check_code_endpoint(body: CodeCheckRequest) -> CodeChecks:
    from ... import check_code as _check_code

    result = await call_jev(
        partial(
            _check_code,
            student_code=body.student_code,
            correct_code=body.correct_code,
            question_description=body.question_description,
        )
    )
    return CodeChecks(**result)


@router.post(
    "/score",
    response_model=GradedScoreResponse,
    summary="Code score in points",
    description="Grade student source code directly to task points. Snaps the raw "
    "jev score to discrete levels (mode=ceil by default) and scales to max_points.",
)
async def check_code_score_endpoint(body: CodeScoreRequest) -> GradedScoreResponse:
    from ... import grade_code_score as _grade_code_score

    graded = await call_jev(
        partial(
            _grade_code_score,
            student_code=body.student_code,
            correct_code=body.correct_code,
            question_description=body.question_description,
            max_points=body.max_points,
            num_levels=body.num_levels,
            mode=body.mode,
        )
    )
    return GradedScoreResponse.from_graded(graded)


@router.post(
    "/full",
    response_model=CodeFullResponse,
    summary="Code checks + points",
    description="Code checks plus point grading in one call. Request combines the "
    "check fields with max_points/num_levels/mode.",
)
async def check_code_full_endpoint(body: CodeScoreRequest) -> CodeFullResponse:
    from ... import grade_code_full as _grade_code_full

    result = await call_jev(
        partial(
            _grade_code_full,
            student_code=body.student_code,
            correct_code=body.correct_code,
            question_description=body.question_description,
            max_points=body.max_points,
            num_levels=body.num_levels,
            mode=body.mode,
        )
    )
    return CodeFullResponse(
        checks=cast("dict[str, float]", result["checks"]),
        grading=GradedScoreResponse.from_graded(
            cast("GradedScore", result["grading"])
        ),
    )
