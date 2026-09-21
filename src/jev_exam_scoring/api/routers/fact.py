"""Fact scoring endpoint (1 feature)."""

from __future__ import annotations

from functools import partial

from fastapi import APIRouter, Depends

from .._helpers import call_jev
from ..schemas import FactScoreRequest, FactScoreResponse
from ..security import verify_api_key

router = APIRouter(
    prefix="/fact", tags=["fact"], dependencies=[Depends(verify_api_key)]
)


@router.post("/score", response_model=FactScoreResponse, summary="Fact 0-2 score")
async def check_fact_score_endpoint(body: FactScoreRequest) -> FactScoreResponse:
    from ... import check_fact_score as _check_fact_score

    score = await call_jev(
        partial(
            _check_fact_score,
            student_answer=body.student_answer,
            correct_answer=body.correct_answer,
            question_description=body.question_description,
        )
    )
    return FactScoreResponse(score=score)
