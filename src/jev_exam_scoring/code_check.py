from .util import *

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


SCORE_KEYS = ("compiles_and_runs", "correct_algorithm", "handles_edge_cases")

# Weights for deriving the 0-2 code score from the three noul markers.
# The algorithm itself dominates; syntax/returns and edge cases share the rest.
CODE_COMPILES_WEIGHT = 0.2
CODE_ALGORITHM_WEIGHT = 0.5
CODE_EDGE_WEIGHT = 0.3


def code_score_from_checks(
    compiles_and_runs: float,
    correct_algorithm: float,
    handles_edge_cases: float,
) -> float:
    """Derive the 0-2 code score from the three noul markers (no extra jev call).

    Weighted average of the markers remapped to the 0-2 range through the
    dense_power curve (dense in the lower part of the range):
    dense_score(compiles_and_runs * 0.2 + correct_algorithm * 0.5
    + handles_edge_cases * 0.3).

    Note the score is a quality signal, not a sole gate: a single failing
    criterion should fail the submission even when the weighted score looks
    middling (e.g. broken syntax with sound logic, or a wrong algorithm that
    still handles edges). A reasonable rule: fail if ``compiles_and_runs < 0.5``
    or ``correct_algorithm < 0.5``.
    """
    weighted = min((
        compiles_and_runs * CODE_COMPILES_WEIGHT
        + correct_algorithm * CODE_ALGORITHM_WEIGHT
        + handles_edge_cases * CODE_EDGE_WEIGHT
    ) + 0.1, 1)
    return dense_score(weighted)


def check_code(
    student_code: str,
    correct_code: str,
    question_description: str,
    max_points: float,
) -> dict[str, float]:
    """Compare a student's code against a correct solution using the jev model.

    Args:
        student_code: The student's source code.
        correct_code: The reference solution.
        question_description: The task / problem statement.
        max_points: Maximum points achievable for the task.

    Returns a dict with probabilities (0 to 1) for compiles_and_runs,
    correct_algorithm and handles_edge_cases, plus the derived code_score
    on the 0-2 scale and points_given (code_score / 2 * max_points).
    """
    answers = ask_jev(
        build_state(question_description, correct_code, student_code),
        NOUL_QUESTIONS,
    )
    # noul is a probability from 0 (no) to 1 (yes).
    checks = {key: answers[key]["noul"] for key in SCORE_KEYS}
    code_score = code_score_from_checks(
        checks["compiles_and_runs"],
        checks["correct_algorithm"],
        checks["handles_edge_cases"],
    )
    return {
        **checks,
        "code_score": code_score,
        "points_given": code_score * max_points,
    }
