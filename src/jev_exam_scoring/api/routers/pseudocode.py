"""Pseudocode scoring endpoint (check only)."""

from __future__ import annotations

from functools import partial

from fastapi import APIRouter, Depends

from .._helpers import ERROR_RESPONSES, call_jev
from ..schemas import PseudocodeCheckRequest, PseudocodeChecks
from ..security import verify_api_key

router = APIRouter(
    prefix="/pseudocode",
    tags=["pseudocode"],
    dependencies=[Depends(verify_api_key)],
    responses=ERROR_RESPONSES,
)


@router.post(
    "/check",
    response_model=PseudocodeChecks,
    summary="Pseudocode checks + derived score",
    description="Score student pseudocode against a reference. Returns "
    "per-criterion floats in [0, 1] (clear_and_complete, correct_algorithm, "
    "handles_edge_cases) plus the derived pseudocode_score on the 0-2 scale "
    "(clear_and_complete * 0.2 + correct_algorithm * 0.5 + handles_edge_cases "
    "* 0.3, remapped to 0-2 through the dense_power curve) and points_given. "
    "Fail the submission if "
    "clear_and_complete < 0.5 or correct_algorithm < 0.5.",
)
async def check_pseudocode_endpoint(body: PseudocodeCheckRequest) -> PseudocodeChecks:
    from ... import check_pseudocode as _check_pseudocode

    result = await call_jev(
        partial(
            _check_pseudocode,
            student_pseudocode=body.student_pseudocode,
            correct_pseudocode=body.correct_pseudocode,
            question_description=body.question_description,
            max_points=body.max_points,
        )
    )
    return PseudocodeChecks(**result)
