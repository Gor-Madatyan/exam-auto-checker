"""Fact scoring endpoint (check only)."""

from __future__ import annotations

from functools import partial

from fastapi import APIRouter, Depends

from .._helpers import ERROR_RESPONSES, call_jev
from ..schemas import FactCheckRequest, FactChecks
from ..security import verify_api_key

router = APIRouter(
    prefix="/fact",
    tags=["fact"],
    dependencies=[Depends(verify_api_key)],
    responses=ERROR_RESPONSES,
)


@router.post(
    "/check",
    response_model=FactChecks,
    summary="Fact checks + derived score",
    description="Grade a factual answer against the correct answer. Returns "
    "per-criterion floats in [0, 1] (factually_correct, complete, "
    "answers_question) plus the derived fact_score on the 0-2 scale "
    "(factually_correct * 0.5 + complete * 0.3 + answers_question * 0.2, "
    "remapped to 0-2 through the dense_power curve) and points_given.",
)
async def check_fact_endpoint(body: FactCheckRequest) -> FactChecks:
    from ... import check_fact as _check_fact

    result = await call_jev(
        partial(
            _check_fact,
            student_answer=body.student_answer,
            correct_answer=body.correct_answer,
            question_description=body.question_description,
            max_points=body.max_points,
        )
    )
    return FactChecks(**result)
