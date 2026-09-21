"""Essay scoring endpoint (1 feature)."""

from __future__ import annotations

from functools import partial

from fastapi import APIRouter, Depends

from .._helpers import call_jev
from ..schemas import EssayCheckRequest, EssayChecks
from ..security import verify_api_key

router = APIRouter(
    prefix="/essay", tags=["essay"], dependencies=[Depends(verify_api_key)]
)


@router.post("/check", response_model=EssayChecks, summary="Essay noul checks")
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
