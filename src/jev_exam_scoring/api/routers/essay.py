"""Essay scoring endpoint (check only)."""

from __future__ import annotations

from functools import partial

from fastapi import APIRouter, Depends

from .._helpers import ERROR_RESPONSES, call_jev
from ..schemas import EssayCheckRequest, EssayChecks
from ..security import verify_api_key

router = APIRouter(
    prefix="/essay",
    tags=["essay"],
    dependencies=[Depends(verify_api_key)],
    responses=ERROR_RESPONSES,
)


@router.post(
    "/check",
    response_model=EssayChecks,
    summary="Essay checks + derived score",
    description="Score a student essay against the topic and requirements. Returns "
    "meets_requirements and grammatically_correct floats in [0, 1] plus the "
    "derived essay_score on the 0-2 scale "
    "(grammatically_correct * 0.6 + meets_requirements * 0.4, remapped to 0-2 "
    "through the dense_power curve) and points_given.",
)
async def check_essay_endpoint(body: EssayCheckRequest) -> EssayChecks:
    from ... import check_essay as _check_essay

    result = await call_jev(
        partial(
            _check_essay,
            student_essay=body.student_essay,
            topic=body.topic,
            requirements=body.requirements,
            max_points=body.max_points,
        )
    )
    return EssayChecks(**result)
