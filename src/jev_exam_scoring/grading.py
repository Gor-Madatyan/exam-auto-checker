"""Point-based grading wrappers around the jev scoring functions.

jev ``score`` questions return a continuous float (e.g. 0-2). In practice
jev systematically undershoots: even a fully correct answer rarely comes
back as a clean 2.0, typically landing around 1.6-1.8. So by default the
raw score is rounded *up* to the next discrete level of the score range
split into ``num_levels`` evenly spaced steps (default 5)::

    0-2 range, 5 levels -> (0, 0.5, 1, 1.5, 2)
    0-1 range, 5 levels -> (0, 0.25, 0.5, 0.75, 1)

and then scaled to the task's point value::

    points = (discrete - min) / (max - min) * max_points

Example: a 5-point task where jev returns 1.7 snaps up to 2.0,
awarding the full 5 points. Pass ``mode="nearest"`` for unbiased
nearest-level snapping instead, or ``mode="optimist"`` to ceil once
20% of the way through an interval is covered (1.7 snaps to 2.0
while 1.55 stays at 1.5).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Literal

SnapMode = Literal["ceil", "nearest", "optimist"]


@dataclass(frozen=True)
class GradedScore:
    """Result of snapping a raw jev score to discrete levels and point scale."""

    raw_score: float
    discrete_score: float
    max_points: float
    points: float
    levels: tuple[float, ...]
    mode: SnapMode = "ceil"


def discrete_levels(
    score_min: float = 0.0, score_max: float = 2.0, num_levels: int = 5
) -> tuple[float, ...]:
    """Evenly spaced discrete levels spanning [score_min, score_max].

    ``num_levels=5`` over 0-2 gives (0, 0.5, 1, 1.5, 2); over 0-1 it gives
    (0, 0.25, 0.5, 0.75, 1).
    """
    _validate_range(score_min, score_max, num_levels)
    step = (score_max - score_min) / (num_levels - 1)
    return tuple(score_min + i * step for i in range(num_levels))


def snap_to_discrete(
    score: float,
    score_min: float = 0.0,
    score_max: float = 2.0,
    num_levels: int = 5,
    mode: SnapMode = "ceil",
) -> float:
    """Snap a raw jev score to a discrete level.

    Out-of-range inputs are clamped first. ``mode="ceil"`` (default)
    rounds up to the next level, compensating for jev's systematic
    undershoot (1.66 and 1.7 both snap to 2.0); exact levels stay put.
    ``mode="nearest"`` snaps to the closest level, with exact ties
    rounding up toward ``score_max``. ``mode="optimist"`` ceils once
    20% of an interval is covered (upper 80% ceils, lower 20%
    floors), so 1.7 snaps to 2.0 while 1.55 stays at 1.5.
    """
    _validate_range(score_min, score_max, num_levels)
    _validate_mode(mode)
    clamped = min(max(score, score_min), score_max)
    step = (score_max - score_min) / (num_levels - 1)
    quotient = (clamped - score_min) / step
    if mode == "ceil":
        # epsilon keeps exact levels (up to float error) on their level
        # instead of spilling over to the next one.
        index = math.ceil(quotient - 1e-9)
    elif mode == "nearest":
        index = math.floor(quotient + 0.5)
    else:
        # optimist: ceil once 20% of the interval is covered, i.e. the
        # upper 80% ceils and the lower 20% floors; the boundary itself
        # ceils, mirroring nearest's round-ties-up behavior.
        index = math.floor(quotient + 0.80 + 1e-9)
    index = min(max(index, 0), num_levels - 1)
    return score_min + index * step


def score_to_points(
    score: float,
    max_points: float,
    score_min: float = 0.0,
    score_max: float = 2.0,
    num_levels: int = 5,
    mode: SnapMode = "ceil",
) -> float:
    """Snap ``score`` to the discrete grid, then scale to ``max_points``."""
    _validate_points(max_points)
    discrete = snap_to_discrete(score, score_min, score_max, num_levels, mode)
    return (discrete - score_min) / (score_max - score_min) * max_points


def grade_score(
    score: float,
    max_points: float,
    score_min: float = 0.0,
    score_max: float = 2.0,
    num_levels: int = 5,
    mode: SnapMode = "ceil",
) -> GradedScore:
    """Grade an already-obtained jev score against a task's point value."""
    _validate_range(score_min, score_max, num_levels)
    _validate_mode(mode)
    _validate_points(max_points)
    discrete = snap_to_discrete(score, score_min, score_max, num_levels, mode)
    points = (discrete - score_min) / (score_max - score_min) * max_points
    return GradedScore(
        raw_score=score,
        discrete_score=discrete,
        max_points=max_points,
        points=points,
        levels=discrete_levels(score_min, score_max, num_levels),
        mode=mode,
    )


def _validate_mode(mode: str) -> None:
    if mode not in ("ceil", "nearest", "optimist"):
        raise ValueError(f'mode ({mode!r}) must be "ceil", "nearest" or "optimist".')


def _validate_range(score_min: float, score_max: float, num_levels: int) -> None:
    if not score_max > score_min:
        raise ValueError(
            f"score_max ({score_max}) must be greater than score_min ({score_min})."
        )
    if num_levels < 2:
        raise ValueError(f"num_levels ({num_levels}) must be at least 2.")


def _validate_points(max_points: float) -> None:
    if max_points < 0:
        raise ValueError(f"max_points ({max_points}) must be non-negative.")


# ---- End-to-end wrappers: call jev, then grade the returned score. ----


def grade_code_score(
    student_code: str,
    correct_code: str,
    question_description: str,
    max_points: float,
    num_levels: int = 5,
    mode: SnapMode = "ceil",
) -> GradedScore:
    """Grade a code submission on a 0-2 scale, snapped to points."""
    from .code_check import check_code_score

    return grade_score(
        check_code_score(student_code, correct_code, question_description),
        max_points,
        num_levels=num_levels,
        mode=mode,
    )


def grade_fact_score(
    student_answer: str,
    correct_answer: str,
    question_description: str,
    max_points: float,
    num_levels: int = 5,
    mode: SnapMode = "ceil",
) -> GradedScore:
    """Grade a factual answer on a 0-2 scale, snapped to points."""
    from .fact_check import check_fact_score

    return grade_score(
        check_fact_score(student_answer, correct_answer, question_description),
        max_points,
        num_levels=num_levels,
        mode=mode,
    )


def grade_pseudocode_score(
    student_pseudocode: str,
    correct_pseudocode: str,
    question_description: str,
    max_points: float,
    num_levels: int = 5,
    mode: SnapMode = "ceil",
) -> GradedScore:
    """Grade a pseudocode submission on a 0-2 scale, snapped to points."""
    from .pseudocode_check import check_pseudocode_score

    return grade_score(
        check_pseudocode_score(
            student_pseudocode, correct_pseudocode, question_description
        ),
        max_points,
        num_levels=num_levels,
        mode=mode,
    )


def grade_essay_score(
    student_essay: str,
    topic: str,
    max_points: float,
    requirements: str = "",
    num_levels: int = 5,
    mode: SnapMode = "ceil",
) -> GradedScore:
    """Grade an essay on a 0-2 scale, snapped to points."""
    from .essay_check import check_essay_score

    return grade_score(
        check_essay_score(student_essay, topic, requirements),
        max_points,
        num_levels=num_levels,
        mode=mode,
    )


def grade_code_full(
    student_code: str,
    correct_code: str,
    question_description: str,
    max_points: float,
    num_levels: int = 5,
    mode: SnapMode = "ceil",
) -> dict[str, dict[str, float] | GradedScore]:
    """Grade a code submission: noul checks plus the 0-2 score snapped to points.

    Returns {"checks": {compiles_and_runs, correct_algorithm, handles_edge_cases},
    "grading": GradedScore}.
    """
    from .code_check import check_code_full

    result = check_code_full(student_code, correct_code, question_description)
    checks = result["checks"]
    score = result["score"]
    assert isinstance(checks, dict)
    assert isinstance(score, (int, float))
    return {
        "checks": checks,
        "grading": grade_score(
            float(score), max_points, num_levels=num_levels, mode=mode
        ),
    }


def grade_pseudocode_full(
    student_pseudocode: str,
    correct_pseudocode: str,
    question_description: str,
    max_points: float,
    num_levels: int = 5,
    mode: SnapMode = "ceil",
) -> dict[str, dict[str, float] | GradedScore]:
    """Grade a pseudocode submission: noul checks plus score snapped to points.

    Returns {"checks": {clear_and_complete, correct_algorithm, handles_edge_cases},
    "grading": GradedScore}.
    """
    from .pseudocode_check import check_pseudocode_full

    result = check_pseudocode_full(
        student_pseudocode, correct_pseudocode, question_description
    )
    checks = result["checks"]
    score = result["score"]
    assert isinstance(checks, dict)
    assert isinstance(score, (int, float))
    return {
        "checks": checks,
        "grading": grade_score(
            float(score), max_points, num_levels=num_levels, mode=mode
        ),
    }


def grade_essay_full(
    student_essay: str,
    topic: str,
    max_points: float,
    requirements: str = "",
    num_levels: int = 5,
    mode: SnapMode = "ceil",
) -> dict[str, dict[str, float] | GradedScore]:
    """Grade an essay: noul checks plus the 0-2 score snapped to points.

    Returns {"checks": {meets_requirements, grammatically_correct},
    "grading": GradedScore}.
    """
    from .essay_check import check_essay_full

    result = check_essay_full(student_essay, topic, requirements)
    checks = result["checks"]
    score = result["score"]
    assert isinstance(checks, dict)
    assert isinstance(score, (int, float))
    return {
        "checks": checks,
        "grading": grade_score(
            float(score), max_points, num_levels=num_levels, mode=mode
        ),
    }
