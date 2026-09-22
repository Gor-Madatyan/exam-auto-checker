from .util import *
from .util import build_state


def build_essay_state(topic: str, requirements: str, student_essay: str) -> str:
    """Build the state prompt sent to jev for essay grading."""
    return build_state(topic, requirements, student_essay,)


ESSAY_NOUL_QUESTIONS = {
    "meets_requirements": {
        "type": "noul",
        "instructions": "Does the student essay fulfil the essay requirements?",
        "criteria": {
            "true": "Meets topic and length requirements",
            "false": "Off-topic or wrong length",
        },
    },
    "grammatically_correct": {
        "type": "noul",
        "instructions": "Is the essay grammatically correct?",
        "criteria": {
            "true": "Grammatically correct with correct spelling and basic sentence punctuation",
            "false": "Frequent grammar, spelling, or basic sentence punctuation errors relative to length",
        },
    },
}


ESSAY_SCORE_KEYS = ("meets_requirements", "grammatically_correct")

# Weights for deriving the essay score from the two noul markers.
ESSAY_GRAMMAR_WEIGHT = 0.4
ESSAY_REQUIREMENTS_WEIGHT = 0.6


def essay_score_from_checks(
    meets_requirements: float, grammatically_correct: float
) -> float:
    """Derive the 0-2 essay score from the two noul markers (no extra jev call).

    Weighted average of the markers remapped to the 0-2 range through the
    dense_power curve (dense in the lower part of the range):
    dense_score(grammatically_correct * 0.6 + meets_requirements * 0.4).
    """
    weighted = min((
        grammatically_correct * ESSAY_GRAMMAR_WEIGHT
        + meets_requirements * ESSAY_REQUIREMENTS_WEIGHT
    )+0.1, 1)
    return dense_score(weighted)


def check_essay(
    student_essay: str, topic: str, max_points: float, requirements: str = ""
) -> dict[str, float]:
    """Score a student essay against its topic and requirements using the jev model.

    Args:
        student_essay: The student's essay text.
        topic: The assigned essay topic the essay must match.
        max_points: Maximum points achievable for the essay.
        requirements: Additional essay requirements (e.g. word count,
            structure, style). May be an empty string if only the topic applies.

    Returns a dict with probabilities (0 to 1) for meets_requirements and
    grammatically_correct, plus the derived essay_score on the 0-2 scale
    and points_given (essay_score / 2 * max_points).
    """
    answers = ask_jev(
        build_essay_state(topic, requirements, student_essay),
        ESSAY_NOUL_QUESTIONS,
    )
    # noul is a probability from 0 (no) to 1 (yes).
    checks = {key: answers[key]["noul"] for key in ESSAY_SCORE_KEYS}
    essay_score = essay_score_from_checks(
        checks["meets_requirements"], checks["grammatically_correct"]
    )
    return {
        **checks,
        "essay_score": essay_score,
        "points_given": essay_score * max_points,
    }
