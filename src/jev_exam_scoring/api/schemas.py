"""Pydantic request/response schemas — one pair per scoring feature."""

from __future__ import annotations

from pydantic import BaseModel, Field


# ---- code ----
class CodeCheckRequest(BaseModel):
    student_code: str = Field(min_length=1)
    correct_code: str = Field(min_length=1)
    question_description: str = Field(min_length=1)


class CodeChecks(BaseModel):
    compiles_and_runs: float = Field(ge=0, le=1)
    correct_algorithm: float = Field(ge=0, le=1)
    handles_edge_cases: float = Field(ge=0, le=1)


class CodeScoreResponse(BaseModel):
    score: float = Field(ge=0, le=2)


class CodeFullResponse(BaseModel):
    checks: CodeChecks
    score: float = Field(ge=0, le=2)


# ---- essay ----
class EssayCheckRequest(BaseModel):
    student_essay: str = Field(min_length=1)
    topic: str = Field(min_length=1)
    requirements: str = ""


class EssayChecks(BaseModel):
    meets_requirements: float = Field(ge=0, le=1)
    grammatically_correct: float = Field(ge=0, le=1)


# ---- fact ----
class FactScoreRequest(BaseModel):
    student_answer: str = Field(min_length=1)
    correct_answer: str = Field(min_length=1)
    question_description: str = Field(min_length=1)


class FactScoreResponse(BaseModel):
    score: float = Field(ge=0, le=2)


# ---- pseudocode ----
class PseudocodeCheckRequest(BaseModel):
    student_pseudocode: str = Field(min_length=1)
    correct_pseudocode: str = Field(min_length=1)
    question_description: str = Field(min_length=1)


class PseudocodeChecks(BaseModel):
    clear_and_complete: float = Field(ge=0, le=1)
    correct_algorithm: float = Field(ge=0, le=1)
    handles_edge_cases: float = Field(ge=0, le=1)


class PseudocodeScoreResponse(BaseModel):
    score: float = Field(ge=0, le=2)


class PseudocodeFullResponse(BaseModel):
    checks: PseudocodeChecks
    score: float = Field(ge=0, le=2)
