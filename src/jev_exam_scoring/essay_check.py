from .util import *


def build_essay_state(topic: str, requirements: str, student_essay: str) -> str:
    """Build the state prompt sent to jev for essay grading."""
    return f"""
Essay Topic:
{topic}

Essay Requirements:
{requirements}

Student Essay:
{student_essay}
"""


ESSAY_NOUL_QUESTIONS = {
    "meets_requirements": {
        "type": "noul",
        "instructions": "Does the student essay fulfil the essay requirements? It must stay on the given topic (no drifting off-topic), meet the required word count / length stated in the requirements, and follow standard essay structure with an introduction, body paragraphs, and conclusion presenting a coherent argument.",
        "criteria": {
            "true": "Meets topic, length, and essay structure requirements",
            "false": "Off-topic, wrong length, or missing essay structure",
        },
    },
    "grammatically_correct": {
        "type": "noul",
        "instructions": "Is the essay grammatically correct? Check grammar, spelling, punctuation, and sentence structure. A single minor typo is still correct; repeated errors or errors that obscure meaning are not correct.",
        "criteria": {
            "true": "Grammatically correct with correct spelling",
            "false": "Grammar, spelling, or punctuation errors",
        },
    },
}


ESSAY_SCORE_CRITERIA = [
    "0: Incorrect — Off-topic or drifts off-topic, far below the required length, missing essay structure (no introduction, body, or conclusion), or pervasive grammar, spelling, or punctuation errors that obscure meaning.",
    "1: Partially Correct — Stays on topic with a recognizable essay structure but misses part of the requirements (e.g. short length, weak or missing introduction/conclusion, thin argument) or has repeated grammar, spelling, or punctuation errors.",
    "2: Correct — Fulfils the essay requirements (on the given topic, required length, introduction/body/conclusion with a coherent argument) and is grammatically correct with correct spelling (at most one minor typo).",
]


ESSAY_SCORE_QUESTION = {
    "essay_score": {
        "type": "score",
        "instructions": """
        Rate the overall quality of the Student Essay against the Essay Topic, Essay Requirements, and language correctness.
        Judge topic match (no drifting off-topic), required word count / length, essay structure (introduction, body paragraphs, conclusion with a coherent argument), and grammar/spelling/punctuation together.
        A single minor typo is still correct; repeated errors or errors that obscure meaning are not.
        """,
        "criteria": ESSAY_SCORE_CRITERIA,
    }
}


ESSAY_SCORE_KEYS = ("meets_requirements", "grammatically_correct")


def check_essay(
    student_essay: str, topic: str, requirements: str = ""
) -> dict[str, float]:
    """Score a student essay against its topic and requirements using the jev model.

    Args:
        student_essay: The student's essay text.
        topic: The assigned essay topic the essay must match.
        requirements: Additional essay requirements (e.g. word count,
            structure, style). May be an empty string if only the topic applies.

    Returns a dict of probabilities (0 to 1) for each check:
    meets_requirements, grammatically_correct.
    """
    answers = ask_jev(
        build_essay_state(topic, requirements, student_essay),
        ESSAY_NOUL_QUESTIONS,
    )
    # noul is a probability from 0 (no) to 1 (yes); choice and score carry the full distribution.
    return {key: answers[key]["noul"] for key in ESSAY_SCORE_KEYS}


def check_essay_score(
    student_essay: str, topic: str, requirements: str = ""
) -> float:
    """Single-score variant: rate the essay on a 0-2 scale.

    Returns one score: 0 (incorrect), 1 (partially correct), 2 (fully correct).
    """
    answers = ask_jev(
        build_essay_state(topic, requirements, student_essay),
        ESSAY_SCORE_QUESTION,
    )
    # noul is a probability from 0 (no) to 1 (yes); choice and score carry the full distribution.
    return answers["essay_score"]["score"]


def check_essay_full(
    student_essay: str, topic: str, requirements: str = ""
) -> dict[str, dict[str, float] | float]:
    """Combined variant: two noul checks and the 0-2 score in a single request.

    Returns {"checks": {meets_requirements, grammatically_correct},
    "score": 0 (incorrect) to 2 (fully correct)}.
    """
    answers = ask_jev(
        build_essay_state(topic, requirements, student_essay),
        {**ESSAY_NOUL_QUESTIONS, **ESSAY_SCORE_QUESTION},
    )
    # noul is a probability from 0 (no) to 1 (yes); choice and score carry the full distribution.
    return {
        "checks": {key: answers[key]["noul"] for key in ESSAY_SCORE_KEYS},
        "score": answers["essay_score"]["score"],
    }
