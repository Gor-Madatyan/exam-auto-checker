"""Code scoring endpoints (3 features)."""

from __future__ import annotations

from functools import partial
from typing import cast

from fastapi import APIRouter, Depends

from .._helpers import call_jev
from ..schemas import (
    CodeCheckRequest,
    CodeChecks,
    CodeFullResponse,
    CodeScoreResponse,
)
from ..security import verify_api_key

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


@router.post("/score", response_model=CodeScoreResponse, summary="Code 0-2 score")
async def check_code_score_endpoint(body: CodeCheckRequest) -> CodeScoreResponse:
    from ... import check_code_score as _check_code_score

    score = await call_jev(
        partial(
            _check_code_score,
            student_code=body.student_code,
            correct_code=body.correct_code,
            question_description=body.question_description,
        )
    )
    return CodeScoreResponse(score=score)


@router.post("/full", response_model=CodeFullResponse, summary="Code checks + score")
async def check_code_full_endpoint(body: CodeCheckRequest) -> CodeFullResponse:
    from ... import check_code_full as _check_code_full

    result = await call_jev(
        partial(
            _check_code_full,
            student_code=body.student_code,
            correct_code=body.correct_code,
            question_description=body.question_description,
        )
    )
    return CodeFullResponse(
        checks=cast("dict[str, float]", result["checks"]),
        score=cast(float, result["score"]),
    )
