"""Code scoring endpoints (3 features)."""

from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING, cast

from fastapi import APIRouter, Depends

from .._helpers import call_jev
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
    prefix="/code", tags=["code"], dependencies=[Depends(verify_api_key)]
)


@router.post("/check", response_model=CodeChecks, summary="Code noul checks")
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
    "/score", response_model=GradedScoreResponse, summary="Code score in points"
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
    "/full", response_model=CodeFullResponse, summary="Code checks + points"
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
