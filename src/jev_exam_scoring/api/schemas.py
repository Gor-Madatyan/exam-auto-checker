"""Pydantic request/response schemas — one check endpoint per scoring domain.

Every domain follows the same pattern: the check endpoint takes the
submission plus ``max_points`` and returns per-criterion noul floats in
[0, 1], the derived ``*_score`` on the 0-2 scale (weighted average of the
criteria, joined with coefficients), and ``points_given``
(score / 2 * max_points).
"""

from __future__ import annotations

from pydantic import BaseModel, Field


# ---- code ----
class CodeCheckRequest(BaseModel):
    student_code: str = Field(min_length=1)
    correct_code: str = Field(min_length=1)
    question_description: str = Field(min_length=1)
    max_points: float = Field(gt=0)


class CodeChecks(BaseModel):
    compiles_and_runs: float = Field(ge=0, le=1)
    correct_algorithm: float = Field(ge=0, le=1)
    handles_edge_cases: float = Field(ge=0, le=1)
    code_score: float = Field(ge=0, le=2)
    points_given: float = Field(ge=0)


# ---- essay ----
class EssayCheckRequest(BaseModel):
    student_essay: str = Field(min_length=1)
    topic: str = Field(min_length=1)
    requirements: str = ""
    max_points: float = Field(gt=0)


class EssayChecks(BaseModel):
    meets_requirements: float = Field(ge=0, le=1)
    grammatically_correct: float = Field(ge=0, le=1)
    essay_score: float = Field(ge=0, le=2)
    points_given: float = Field(ge=0)


# ---- fact ----
class FactCheckRequest(BaseModel):
    student_answer: str = Field(min_length=1)
    correct_answer: str = Field(min_length=1)
    question_description: str = Field(min_length=1)
    max_points: float = Field(gt=0)


class FactChecks(BaseModel):
    factually_correct: float = Field(ge=0, le=1)
    complete: float = Field(ge=0, le=1)
    answers_question: float = Field(ge=0, le=1)
    fact_score: float = Field(ge=0, le=2)
    points_given: float = Field(ge=0)


# ---- pseudocode ----
class PseudocodeCheckRequest(BaseModel):
    student_pseudocode: str = Field(min_length=1)
    correct_pseudocode: str = Field(min_length=1)
    question_description: str = Field(min_length=1)
    max_points: float = Field(gt=0)


class PseudocodeChecks(BaseModel):
    clear_and_complete: float = Field(ge=0, le=1)
    correct_algorithm: float = Field(ge=0, le=1)
    handles_edge_cases: float = Field(ge=0, le=1)
    pseudocode_score: float = Field(ge=0, le=2)
    points_given: float = Field(ge=0)
