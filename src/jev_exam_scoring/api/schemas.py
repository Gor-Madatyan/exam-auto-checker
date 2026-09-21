"""Pydantic request/response schemas — one pair per scoring feature."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from ..grading import GradedScore

SnapModeParam = Literal["ceil", "nearest", "optimist"]


class PointsRequest(BaseModel):
    """Task point value + discretization options for score endpoints."""

    max_points: float = Field(gt=0)
    num_levels: int = Field(default=5, ge=2)
    mode: SnapModeParam = "ceil"


class GradedScoreResponse(BaseModel):
    raw_score: float
    discrete_score: float
    max_points: float
    points: float
    levels: list[float]
    mode: SnapModeParam

    @classmethod
    def from_graded(cls, graded: GradedScore) -> GradedScoreResponse:
        return cls(
            raw_score=graded.raw_score,
            discrete_score=graded.discrete_score,
            max_points=graded.max_points,
            points=graded.points,
            levels=list(graded.levels),
            mode=graded.mode,
        )


# ---- code ----
class CodeCheckRequest(BaseModel):
    student_code: str = Field(min_length=1)
    correct_code: str = Field(min_length=1)
    question_description: str = Field(min_length=1)


class CodeScoreRequest(CodeCheckRequest, PointsRequest):
    pass


class CodeChecks(BaseModel):
    compiles_and_runs: float = Field(ge=0, le=1)
    correct_algorithm: float = Field(ge=0, le=1)
    handles_edge_cases: float = Field(ge=0, le=1)


class CodeFullResponse(BaseModel):
    checks: CodeChecks
    grading: GradedScoreResponse


# ---- essay ----
class EssayCheckRequest(BaseModel):
    student_essay: str = Field(min_length=1)
    topic: str = Field(min_length=1)
    requirements: str = ""


class EssayChecks(BaseModel):
    meets_requirements: float = Field(ge=0, le=1)
    grammatically_correct: float = Field(ge=0, le=1)


class EssayScoreRequest(EssayCheckRequest, PointsRequest):
    pass


class EssayFullResponse(BaseModel):
    checks: EssayChecks
    grading: GradedScoreResponse


# ---- fact ----
class FactScoreRequest(PointsRequest):
    student_answer: str = Field(min_length=1)
    correct_answer: str = Field(min_length=1)
    question_description: str = Field(min_length=1)


# ---- pseudocode ----
class PseudocodeCheckRequest(BaseModel):
    student_pseudocode: str = Field(min_length=1)
    correct_pseudocode: str = Field(min_length=1)
    question_description: str = Field(min_length=1)


class PseudocodeScoreRequest(PseudocodeCheckRequest, PointsRequest):
    pass


class PseudocodeChecks(BaseModel):
    clear_and_complete: float = Field(ge=0, le=1)
    correct_algorithm: float = Field(ge=0, le=1)
    handles_edge_cases: float = Field(ge=0, le=1)


class PseudocodeFullResponse(BaseModel):
    checks: PseudocodeChecks
    grading: GradedScoreResponse
