
from .util import *

SCORE_CRITERIA = [
    "0: Incorrect — Wrong algorithm (a fundamentally different approach than requested), a code path that produces no result (e.g., missing return), or errors that would crash or give wrong answers.",
    "1: Partially Correct — The right algorithm with minor logic bugs (e.g., off-by-one) or incomplete edge case handling.",
    "2: Correct — The algorithm is correct and complete and produces the right result for all inputs. Style, syntax, and implementation details may differ from the reference.",
]


NOUL_QUESTIONS = {
    "compiles_and_runs": {
        "type": "noul",
        "instructions": "Is the syntax valid and does every code path return a value (no missing or implicit returns)?",
        "criteria": {
            "true": "Valid syntax",
            "false": "Syntax or structure error",
        },
    },
    "correct_algorithm": {
        "type": "noul",
        "instructions": "Does it implement the requested algorithm's logic correctly?",
        "criteria": {
            "true": "Correct algorithm design",
            "false": "Wrong algorithm or logic",
        },
    },
    "handles_edge_cases": {
        "type": "noul",
        "instructions": "Does it correctly handle boundary conditions and edge cases (e.g., empty input, single element, target not present, extreme values)?",
        "criteria": {
            "true": "Handles edge cases",
            "false": "Fails on edge cases",
        },
    },
}


SCORE_QUESTION = {
    "code_score": {
        "type": "score",
        "instructions": """
        Compare the Student Answer against the Correct Answer and rate its functional correctness, including return values on every code path.
        """,
        "criteria": SCORE_CRITERIA,
    }
}


SCORE_KEYS = ("compiles_and_runs", "correct_algorithm", "handles_edge_cases")







def check_code(
    student_code: str, correct_code: str, question_description: str
) -> dict[str, float]:
    """Compare a student's code against a correct solution using the jev model.

    Returns a dict of probabilities (0 to 1) for each check:
    compiles_and_runs, correct_algorithm, handles_edge_cases.
    """
    answers = ask_jev(
        build_state(question_description, correct_code, student_code),
        NOUL_QUESTIONS,
    )
    # noul is a probability from 0 (no) to 1 (yes); choice and score carry the full distribution.
    return {key: answers[key]["noul"] for key in SCORE_KEYS}


def check_code_score(
    student_code: str, correct_code: str, question_description: str
) -> float:
    """Single-score variant: rate the submission on a 0-2 scale.

    Returns one score: 0 (incorrect), 1 (partially correct), 2 (fully correct).
    """
    answers = ask_jev(
        build_state(question_description, correct_code, student_code),
        SCORE_QUESTION,
    )
    # noul is a probability from 0 (no) to 1 (yes); choice and score carry the full distribution.
    return answers["code_score"]["score"]


def check_code_full(
    student_code: str, correct_code: str, question_description: str
) -> dict[str, dict[str, float] | float]:
    """Combined variant: three noul checks and the 0-2 score in a single request.

    Returns {"checks": {compiles_and_runs, correct_algorithm, handles_edge_cases},
    "score": 0 (incorrect) to 2 (fully correct)}.
    """
    answers = ask_jev(
        build_state(question_description, correct_code, student_code),
        {**NOUL_QUESTIONS, **SCORE_QUESTION},
    )
    # noul is a probability from 0 (no) to 1 (yes); choice and score carry the full distribution.
    return {
        "checks": {key: answers[key]["noul"] for key in SCORE_KEYS},
        "score": answers["code_score"]["score"],
    }
