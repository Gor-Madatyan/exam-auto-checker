"""Code scoring endpoint (check only)."""

from __future__ import annotations

from functools import partial

from fastapi import APIRouter, Depends

from .._helpers import ERROR_RESPONSES, call_jev
from ..schemas import CodeCheckRequest, CodeChecks
from ..security import verify_api_key

router = APIRouter(
    prefix="/code",
    tags=["code"],
    dependencies=[Depends(verify_api_key)],
    responses=ERROR_RESPONSES,
)


@router.post(
    "/check",
    response_model=CodeChecks,
    summary="Code checks + derived score",
    description="Score student source code against a reference solution. Returns "
    "per-criterion floats in [0, 1] (compiles_and_runs, correct_algorithm, "
    "handles_edge_cases) plus the derived code_score on the 0-2 scale "
    "(compiles_and_runs * 0.2 + correct_algorithm * 0.5 + handles_edge_cases "
    "* 0.3, remapped to 0-2 through the dense_power curve) and points_given. "
    "Fail the submission if "
    "compiles_and_runs < 0.5 or correct_algorithm < 0.5.",
)
async def check_code_endpoint(body: CodeCheckRequest) -> CodeChecks:
    from ... import check_code as _check_code

    result = await call_jev(
        partial(
            _check_code,
            student_code=body.student_code,
            correct_code=body.correct_code,
            question_description=body.question_description,
            max_points=body.max_points,
        )
    )
    return CodeChecks(**result)
