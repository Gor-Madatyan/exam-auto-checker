"""Fact scoring endpoint (1 feature)."""

from __future__ import annotations

from functools import partial

from fastapi import APIRouter, Depends

from .._helpers import ERROR_RESPONSES, call_jev
from ..schemas import FactScoreRequest, GradedScoreResponse
from ..security import verify_api_key

router = APIRouter(
    prefix="/fact",
    tags=["fact"],
    dependencies=[Depends(verify_api_key)],
    responses=ERROR_RESPONSES,
)


@router.post(
    "/score",
    response_model=GradedScoreResponse,
    summary="Fact score in points",
    description="Grade a short factual answer against the correct answer, snapped "
    "to task points. Score-only endpoint (no separate check).",
)
async def check_fact_score_endpoint(body: FactScoreRequest) -> GradedScoreResponse:
    from ... import grade_fact_score as _grade_fact_score

    graded = await call_jev(
        partial(
            _grade_fact_score,
            student_answer=body.student_answer,
            correct_answer=body.correct_answer,
            question_description=body.question_description,
            max_points=body.max_points,
            num_levels=body.num_levels,
            mode=body.mode,
        )
    )
    return GradedScoreResponse.from_graded(graded)
